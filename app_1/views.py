# views.py
from datetime import timezone
import json
import math
import os
#from ollama import chat
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.http import StreamingHttpResponse
from django.contrib.auth.models import User

# Social Auth
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

# Local Imports
from .models import (
    OrgNode, Tharipistneeded, UserHomepageDB, 
    UserChatDB, TeamData, UserConsent, UserDrillDown, UserDashboard, 
    UserChatSummary
)

from .serializers import (
    RegisterSerializer, TherapistNeededSerializer, UserConsentSerializer, HomePageSerializer, ChatSerializer, 
    OrgNodeSerializer, UserFeedbackSerializer, 
    TeamDataSerializer, UserDrillDownSerializer, UserDashboardSerializer
)
from .Ai import therpy_ai_response, consiler_ai_responce, summarize_chat_history
from .permissions import IsHierarchicalSuperior
from .tasks import generate_drill_down_lists
class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.request.query_params.get('chat_id')
        if chat_id is None:
             return UserChatDB.objects.none()
        
        # Security: Ensure user owns the chat
        chat_session = get_object_or_404(UserHomepageDB, id=chat_id, owner=self.request.user)
        return UserChatDB.objects.filter(chat=chat_session, owner=self.request.user)

    @action(detail=False, methods=['post'])
    def continue_chat(self, request):
        user_prompt = request.data.get('prompt')
        ai_mode = request.data.get('mode')
        chat_id = request.data.get('ChatID')
    
        if not user_prompt or not chat_id:
            return Response({'error': 'Prompt and ChatID are required'}, status=400)
    
        chat_session = get_object_or_404(UserHomepageDB, id=chat_id, owner=request.user)
        history_obj = get_object_or_404(UserChatDB, chat=chat_session, owner=request.user)
        current_history = history_obj.content if isinstance(history_obj.content, list) else []
        #current_history = current_history[:-1]
        # Context Window Logic
        a = []
        context_window = []
        total_words = 0
        for chat in current_history[::-1]:# current histroy is chat data/convo
            words = chat["content"].split()
            total_words += len(words)
            estimated_tokens = math.ceil(total_words * 1.5)
            a.append(chat)
            if estimated_tokens > 8000:
                get_chat_summary = summarize_chat_history(current_history[:-len(a)])
                context_window.append(get_chat_summary)
                break

        ### here v can later add depalyed summary bringing it from d

        context_window.append(a)
        # Generator wrapper
        def stream_wrapper():
            full_reply = ""
            try:    
                if ai_mode == "specialist":
                    gen = therpy_ai_response(user_prompt, context_window, request.user.username)
                else:
                    gen = consiler_ai_responce(user_prompt, context_window, request.user.username)

                for token in gen:
                    full_reply += token
                    yield token
                
                # Database update MUST happen after stream finishes or be handled asynchronously
                # Doing it here is risky if connection breaks, but acceptable for MVP
                current_history.append({"role": "user", "content": user_prompt})
                current_history.append({"role": "assistant", "content": full_reply})
                history_obj.content = current_history
                history_obj.to_be_summarized = True
                history_obj.save()

            except Exception as e:
                yield f"\n[Error: {str(e)}]"

        return StreamingHttpResponse(stream_wrapper(), headers={'Content-Type': 'text/plain'})

    @action(detail=False, methods=['delete'])
    def delete_chat(self, request):
        chat_id = request.data.get('ChatID')
        chat_session = get_object_or_404(UserHomepageDB, id=chat_id, owner=request.user)
        history_obj = get_object_or_404(UserChatDB, chat=chat_session, owner=request.user)
        
        history_obj.content = []
        history_obj.save()
        return Response({'status': 'Chat history cleared'})

class OldChatsViewSet(viewsets.ModelViewSet):
    serializer_class = HomePageSerializer 
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        return UserHomepageDB.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        session = serializer.save(owner=self.request.user)
        UserChatDB.objects.create(
            owner=self.request.user, 
            chat=session, 
            content=[],
            to_be_summarized=False,
        )

class UserDrillDownViewSet(viewsets.ModelViewSet):
    serializer_class = UserDrillDownSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return UserDrillDown.objects.filter(owner=self.request.user)

class UserDashboardViewSet(viewsets.ModelViewSet):
    serializer_class = UserDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return UserDashboard.objects.filter(owner=self.request.user)

class UserFeedbackViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserFeedbackSerializer
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class UserConsentViewSet(viewsets.ModelViewSet):
    queryset = UserConsent.objects.all()
    serializer_class = UserConsentSerializer
    permission_classes = [AllowAny] # Unauthenticated users must also be able to consent

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def create(self, request, *args, **kwargs):
        """
        Overriding create to handle IP capture and Cookie setting
        """
        # 1. Standard DRF validation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. Save the instance with the extra system data
        # We pass these into save() so they override the read_only constraints for the save action
        self.perform_create(serializer)

        # 3. Create the standard DRF JSON response
        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        # 4. Attach the Cookie to the response
        response.set_cookie(
            key='consent_version_held',
            value=serializer.data['consent_version'],
            max_age=31536000, # 1 Year
            httponly=False,   # False so frontend JS can read it to hide the banner
            samesite='Lax'
        )

        return response

    def perform_create(self, serializer):
        # This is where we inject the data not provided by the user
        serializer.save(
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            user=self.request.user if self.request.user.is_authenticated else None
        )

    def needs_new_consent(request):
    # 1. Define your current required version (usually in settings.py)
        CURRENT_VERSION = "v2.0" 

        # 2. Get the version from the user's cookie
        user_held_version = request.COOKIES.get('consent_version_held')

        # 3. Compare
        if not user_held_version or user_held_version != CURRENT_VERSION:
            return True # Trigger the pop-up/form again

        return False


class OrgNodeViewSet(viewsets.ModelViewSet):
    queryset = OrgNode.objects.all()
    serializer_class = OrgNodeSerializer
    permission_classes = [IsAuthenticated, IsHierarchicalSuperior]

    @action(detail=True, methods=['get'])
    def health_dashboard(self, request, pk=None):
        # 1. Permission Check (IsHierarchicalSuperior runs here automatically)
        target_node = self.get_object() 
        #requester_node = request.user.org_node

        try:
            # FIX: Use lowercase 'node' (field name), not 'OrgNode' (class name)
            dashboard = TeamData.objects.get(node=target_node)# this is to see his own team's performance data, not the subordinates data. The subordinate data is in the TeamData model and is accessed in the 'else' block below.
            
            # FIX: Must serialize the data before returning
            serializer = TeamDataSerializer(dashboard)##
            return Response(serializer.data)
            
        except TeamData.DoesNotExist:
            return Response({"data": ["error", "No dashboard data available yet. Wait for midnight processing."]}, status=404)
       
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def replace_employee(self, request, pk=None):
        """
        Logic:
        - 'pk' is the OLD person (leaving).
        - 'replacement_id' is the NEW person (taking the seat).
        """
        old_node_id = pk
        new_node_id = request.data.get('replacement') # Expecting ID (e.g., 5), not User object

        if not new_node_id:
            return Response({"error": "replacement ID is required"}, status=400)

        try:
            with transaction.atomic():
                # FIX: Query by ID (pk), not by User, to ensure we get the node specifically
                old_node = OrgNode.objects.get(pk=old_node_id)
                new_node = OrgNode.objects.get(pk=new_node_id)

                # Step 1: Validate Company Match
                if old_node.company != new_node.company:
                    return Response({"error": "Cannot cross-promote between companies"}, status=400)

                # Step 2: "Inheritance" - New Node moves up to Old Node's spot
                # We give the New Person the Old Person's Rank & Boss
                new_node.structure_level = old_node.structure_level
                
                # Handling the Parent logic
                # If New Node was reporting to Old Node, New Node's parent becomes Old Node's parent.
                new_node.parent = old_node.parent 
                
                new_node.save()

                # Step 3: "Adoption" - Move Old Node's children to New Node
                # All people who used to report to Old Node now report to New Node.
                # FIX: Use 'id' to exclude, it's safer.
                old_node.children.exclude(id=new_node.id).update(parent=new_node)

                # Step 4: Fire the Old Node
                # This deletes the Old Node row. 
                # Note: Because 'UserDashboard' is OneToOne with CASCADE, the old user's dashboard is deleted.
                old_node.delete()
                generate_drill_down_lists(new_node.OrgNode)
                return Response({
                    "message": f"Success. {new_node.user.username} has replaced {old_node.user.username}."
                })

        except OrgNode.DoesNotExist:
            return Response({"error": "Node not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

# for jwt token auth and registration
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken # <--- Add this import

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        # 1. Trick the serializer (as we discussed before)
        if request.data.get('access_token') and not request.data.get('id_token'):
            if isinstance(request.data, dict):
                request.data['id_token'] = request.data['access_token']
            else:
                data = request.data.copy()
                data['id_token'] = data['access_token']
                request._full_data = data
                
        # 2. Get the default response
        response = super().post(request, *args, **kwargs)

        # 3. FORCE JWT: If the response is just a 'key' (token), swap it for access/refresh
        if response.status_code == 200 and 'key' in response.data:
            # The 'user' object is available on the view after login
            user = self.user 
            
            # Generate the tokens manually
            refresh = RefreshToken.for_user(user)
            
            # Update the response data
            response.data['access'] = str(refresh.access_token)
            response.data['refresh'] = str(refresh)
            
            # Optional: Remove the 'key' if you don't want it
            # del response.data['key']

        return response
    
class TherapistNeededView(viewsets.ModelViewSet):
    serializer_class = TherapistNeededSerializer
    permission_classes = [IsAuthenticated]
    @action(detail=False, methods=['post'])
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, submitted_at=timezone.now(), in_need=True)