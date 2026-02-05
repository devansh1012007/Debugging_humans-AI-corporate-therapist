#views.py
from httpx import request
from rest_framework import viewsets, permissions
from .models import OrgNode, PrivacyPolicyAcceptance, UserFeedback, UserHomepageDB, UserChatDB,TeamData,UserConsent,UserDrillDown,UserDashboard, UserPersonalityData,TeamDataHistory,UserChatSummary
from .serializers import UserConsentSerializer, HomePageSerializer, ChatSerializer, OrgNodeSerializer, PrivacyPolicyAcceptanceSerializer, UserFeedbackSerializer, TeamDataSerializer, UserPsycoDataSerializer, UserDrillDownSerializer, UserDashboardSerializer, UserPersonalityDataSerializer, UserChatSummerySerializer, UserDashbioardHistorySerializer, TeamDataHistorySerializer
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
import json
from django.http import JsonResponse
from .Ai import ai_response, therpy_ai_response, consiler_ai_responce
from .permissions import IsHierarchicalSuperior
from django.http import StreamingHttpResponse
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.db import transaction
from .tasks import generate_drill_down_lists

class OldChatsViewSet(viewsets.ModelViewSet):
    serializer_class = HomePageSerializer 
    permission_classes = [permissions.IsAuthenticated] 
    # this will give list of all the titel along with there titels 
    def get_queryset(self):
        return UserHomepageDB.objects.filter(owner=self.request.user)
    # if user wants to star a new chat v take title and ai mode and add it to our UserHomepageDB
    def perform_create(self, serializer):
        session = serializer.save(owner=self.request.user) # id will generted by itself 
        UserChatDB.objects.create( # creating space in other db
            owner=self.request.user, 
            chat=session, 
            content=[],
            to_be_summarized=False,
        )

class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):# used for filtering the chat history based on chat session id #It is the "Django way" to handle ownership.
        chat_id = self.request.query_params.get('chat_id')
        if chat_id is None:
            # Return nothing if no ID provided, or use UserChatDB.objects.none()
            error_response = Response({'error': 'Chat ID is required'}, status=400)
            return error_response 
        chat_session = get_object_or_404(UserHomepageDB, id=chat_id, owner=self.request.user)
        return UserChatDB.objects.filter(chat=chat_session, owner=self.request.user)# another way of filtering that chat willl be --> UserChatDB.objects.filter(chat__id=chat_id, owner=self.request.user) # this is also correct and works fine, but the above one is more readable and easier to understand for most developers, especially those new to Django. It clearly shows the relationship between the models and the filtering logic. The double underscore syntax can be less intuitive for those who are not familiar with Django's ORM.
    
    # need to looka at this from other project whewre streaming works
    @action(detail=False, methods=['post'])# action decorator to create custom endpoint
    def continue_chat(self, request):
        user_prompt = request.data.get('prompt')
        ai_mode = request.data.get('mode')
        chat_id = request.data.get('ChatID')
    
        if not user_prompt or not chat_id:
            return Response({'error': 'Prompt and ChatID are required'}, status=400)
    
        # 1. Get the session and history objects
        chat_session = get_object_or_404(UserHomepageDB, id=chat_id, owner=request.user)
        history_obj = get_object_or_404(UserChatDB, chat=chat_session, owner=request.user)
        current_history = history_obj.content if isinstance(history_obj.content, list) else []
        #context_window = current_history[:10] if len(current_history) > 10 else current_history
        if len(current_history) > 10:#call summery function
            #chat_to_be_summarized = current_history[9:]
            summary = UserChatSummary.objects.filter(owner=request.user, chat=chat_session,).first()# idt first should be needed here coz there will be only one summary per chat session due to OneToOne relationship, so we can directly use .get() instead of .filter().first()
            context_window = current_history[:9] + [{"role": "assistant", "content": summary}]
            # Save the summary to the UserChatSummary model
            '''UserChatSummary.objects.create(
                owner=request.user,
                chat=chat_session,
                summary=summary
            )'''
        else:
            context_window = current_history

        
        def stream_wrapper():
            full_reply = "" # Keep track of the full string to save to DB later
            try:    
                # Determine which generator to use
                if ai_mode == "specialist":
                    gen = therpy_ai_response(user_prompt, context_window, request.user.name)
                else:
                    gen = consiler_ai_responce(user_prompt, context_window, request.user.name)

                for token in gen:
                    full_reply += token
                    yield token # Send token to frontend
            except Exception as e:
                yield f"\n[Error generating response: {str(e)}]"
                return# In case of error, we yield an error message and exit the generator
            # 3. SAVE TO DB
            current_history.append({"role": "user", "content": user_prompt})
            current_history.append({"role": "assistant", "content": full_reply})
            history_obj.to_be_summarized = True
            history_obj.content = current_history
            history_obj.save()
    
        # 4. Return the Stream

        return StreamingHttpResponse(stream_wrapper(), headers={'Content-Type': 'text/plain'})    
        
    # add delete method to delete chat history if needed
    # no need coz ModelViewSet already has a .destroy() method mapped to the DELETE HTTP verb
    @action(detail=False, methods=['delete'])
    def delete_chat(self, request):
        chat_id = request.data.get('ChatID')
        try:
            chat_session = UserHomepageDB.objects.get(id=chat_id, owner=request.user)
        except UserHomepageDB.DoesNotExist:
            return Response({'error': f'Chat Session {chat_id} not found for this user.'}, status=404)
        
        history_obj = get_object_or_404(UserChatDB, chat=chat_session, owner=request.user)
        history_obj.content = []  # Clear the chat history
        history_obj.save()
        return Response({'status': 'Chat history deleted successfully'})

class UserDrillDownViewSet(viewsets.ModelViewSet):
    serializer_class = UserDrillDownSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return UserDrillDown.objects.filter(owner=self.request.user)


class RegisterView(generics.CreateAPIView): # generic view for user registration built-in create behavior
    queryset = User.objects.all() # queryset set to all users so that we can create new ones
    # Everyone must be able to hit this endpoint to sign up!
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class UserFeedbackViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserFeedbackSerializer
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class PrivacyPolicyAcceptanceViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = PrivacyPolicyAcceptanceSerializer
    queryset = PrivacyPolicyAcceptance.objects.all()
    
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
            key='privacy_policy_version_held',
            value=serializer.data['privacy_policy_version'],
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
        user_held_version = request.COOKIES.get('privacy_policy_version_held')

        # 3. Compare
        if not user_held_version or user_held_version != CURRENT_VERSION:
            return True # Trigger the pop-up/form again

        return False
    

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
        requester_node = request.user.org_node
        
        # --- SCENARIO 1: I AM LOOKING AT MYSELF (Raw Data) ---
        if target_node.id == requester_node.id:
            try:
                # FIX: Use lowercase 'node' (field name), not 'OrgNode' (class name)
                dashboard = UserDashboard.objects.get(node=target_node)
                
                # FIX: Must serialize the data before returning
                serializer = UserDashboardSerializer(dashboard)
                return Response(serializer.data)
                
            except UserDashboard.DoesNotExist:
                return Response({"view_mode": "PERSONAL", "data": []})
        
        # --- SCENARIO 2: I AM LOOKING AT A SUBORDINATE (Team Snapshot) ---
        else:
            try:
                # FIX: We want the TeamData attached to the TARGET (subordinate), not the requester
                team_data = TeamData.objects.get(node=target_node)
                
                serializer = TeamDataSerializer(team_data)
                return Response(serializer.data)
                
            except TeamData.DoesNotExist:
                return Response({
                    "view_mode": "TEAM_OVERSIGHT",
                    "error": "No processed data available yet. Wait for midnight processing."
                }, status=404)

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