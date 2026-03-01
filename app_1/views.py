# views.py
from django.utils import timezone
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
from rest_framework.decorators import authentication_classes

from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView


from .models import (
    OrgNode, Tharipistneeded, UserHomepageDB, 
    UserChatDB, TeamData, UserConsent, UserDrillDown, UserDashboard, 
    #UserChatSummary,UserPsycoData,UserPsycoDataHistory,UserPersonalityDataHistoric,UserPersonalityData
    UserPsycoProcessedData,UserPsycoProcessedDataHistory
)

from .serializers import (
    RegisterSerializer, TherapistNeededSerializer, UserConsentSerializer, HomePageSerializer, ChatSerializer, 
    OrgNodeSerializer, UserFeedbackSerializer, 
    TeamDataSerializer, UserDrillDownSerializer, UserDashboardSerializer,UserPsycoDataSerializer,
    #UserPsycoDataHistorySerializer,UserPersonalityDataSerializer,UserPersonalityDataHistoricSerializer,
    UserPsycoProcessedDataSerializer,UserPsycoProcessedDataHistorySerializer
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
        
        # Context Window Logic 
        a = []
        context_window = []
        total_words = 0
        
        for chat in current_history:
            msg_content = chat.get("content") or chat.get("message") or ""
            
            normalized_chat = chat.copy()
            normalized_chat["content"] = msg_content
            
            words = msg_content.split()
            total_words += len(words)
            estimated_tokens = math.ceil(total_words * 1.5)
            
            a.append(normalized_chat)
            
            if estimated_tokens > 4000:
                get_chat_summary = summarize_chat_history(current_history[:-len(a)])
                context_window.append(get_chat_summary)
                break
        
        if not context_window:
            context_window = a
        def stream_wrapper():
            full_reply = ""
            try:    
                if ai_mode == "therapy":
                    gen = therpy_ai_response(user_prompt, context_window, request.user.username)
                else:
                    gen = consiler_ai_responce(user_prompt, context_window, request.user.username)

                for token in gen:
                    full_reply += token
                    yield token
                
                current_history.append({
                    "role": "user", 
                    "content": user_prompt,
                    "message": user_prompt 
                })
                current_history.append({
                    "role": "assistant", 
                    "content": full_reply,
                    "message": full_reply
                })
                
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
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        response.set_cookie(
            key='consent_version_held',
            value=serializer.data.get('consent_version', 'v1.0-2026'),
            max_age=31536000, 
            httponly=False,   
            samesite='None',  
            secure=True       
        )

        return response

    def perform_create(self, serializer):
        serializer.save(
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            user=self.request.user if self.request.user.is_authenticated else None
        )

    @action(detail=False, methods=['get']) 
    @authentication_classes([]) 
    def needs_new_consent(self, request):
        CURRENT_VERSION = "v1.0-2026" 

        user_held_version = request.COOKIES.get('consent_version_held')

        #print(f"DEBUG: Cookie received from frontend: {user_held_version}")
        needs_consent = user_held_version != CURRENT_VERSION

        return Response({'needs_consent': needs_consent})


class OrgNodeViewSet(viewsets.ModelViewSet):
    queryset = OrgNode.objects.all()
    serializer_class = OrgNodeSerializer
    permission_classes = [IsAuthenticated, IsHierarchicalSuperior]

    @action(detail=True, methods=['get'])
    def health_dashboard(self, request, pk=None):
        target_node = self.get_object() 
        #requester_node = request.user.org_node

        try:
            dashboard = TeamData.objects.get(node=target_node)# this is to see his own team's performance data, not the subordinates data. The subordinate data is in the TeamData model and is accessed in the 'else' block below.
            
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
        new_node_id = request.data.get('replacement') 

        if not new_node_id:
            return Response({"error": "replacement ID is required"}, status=400)

        try:
            with transaction.atomic():
                
                old_node = OrgNode.objects.get(pk=old_node_id)
                new_node = OrgNode.objects.get(pk=new_node_id)

                if old_node.company != new_node.company:
                    return Response({"error": "Cannot cross-promote between companies"}, status=400)

                new_node.structure_level = old_node.structure_level
                
                new_node.parent = old_node.parent 
                
                new_node.save()

                old_node.children.exclude(id=new_node.id).update(parent=new_node)

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



class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        if request.data.get('id_token') and not request.data.get('access_token'):
            if isinstance(request.data, dict):
                request.data['access_token'] = request.data['id_token']
            else:
                data = request.data.copy()
                data['access_token'] = data['id_token']
                request._full_data = data
                
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            user = self.user 
            
            refresh = RefreshToken.for_user(user)
            response.data['access'] = str(refresh.access_token)
            response.data['refresh'] = str(refresh)
            
        return response
    
class TherapistNeededView(viewsets.ModelViewSet):
    queryset = Tharipistneeded.objects.all()
    serializer_class = TherapistNeededSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user, 
            submitted_at=timezone.now(), 
            in_need=True
        )

class UserPsycoProcessedDataViewSet(viewsets.ModelViewSet):
    serializer_class = UserPsycoProcessedDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserPsycoProcessedData.objects.filter(owner=self.request.user)

class UserPsycoProcessedDataHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = UserPsycoProcessedDataHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserPsycoProcessedDataHistory.objects.filter(owner=self.request.user)

'''
class UserPersonalityDataViewSet(viewsets.ModelViewSet):
    serializer_class = UserPersonalityDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserPersonalityData.objects.filter(owner=self.request.user)

class UserPersonalityDataHistoricViewSet(viewsets.ModelViewSet):
    serializer_class = UserPersonalityDataHistoricSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserPersonalityDataHistoric.objects.filter(owner=self.request.user)
'''