#views.py
from rest_framework import viewsets, permissions
from .models import UserHomepageDB, UserChatDB,TeamMembers,TeamData,UserProblems
from .serializers import HomePageSerializer, ChatSerializer, UserProblemSerializer, TeamMembersSerializer, TeamDataSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
import json
from django.http import JsonResponse
from .Ai import therpy_ai_response, counselor_ai_responce



# Class 1 -> gives data from model 1 (mostly get but dosen't matter)
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
            content=[]
        )
# Class 2 -> gives and take data to ai and front end chat interface


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    #lookup_field = 'chat__id'
    def get_queryset(self):
        return UserChatDB.objects.filter(owner=self.request.user)
    #we don't need to filter the chat by id because we are not using any url parameter here; but chat_id method still works(need to experiment)


    @action(detail=False, methods=['post'])# maybe v should also add patch but udt its needed)# @action decorator to create a custom action and v want use perform_create or perform_update here bcoz we are not creating or updating any model instance directly
    def continue_chat(self, request):
        
        user_prompt = request.data.get('prompt')
        ai_mode = request.data.get('mode')
        chat_id = request.data.get('ChatID')

        if not user_prompt or not chat_id:
            return Response({'error': 'Prompt and ChatID are required'}, status=400)

        history_obj = get_object_or_404(UserChatDB, chat__id=chat_id, owner=request.user)
        # v r checking if chat has any history or not, if not v will create empty list
        raw_history= history_obj.content if isinstance(history_obj.content, list) else []
        messages_list = [
            msg for msg in raw_history 
            if isinstance(msg, dict) and 'role' in msg and 'content' in msg
        ]
             
        messages_list.append({"role": "user", "content": user_prompt})

        try:
            if ai_mode == "therapy":
                ai_result = therpy_ai_response(user_prompt, messages_list)
                
            else:
                ai_result = counselor_ai_responce(user_prompt, messages_list)
                
            ai_message_data = ai_result.get('message', {})
            # Extract just the text response to send back to frontend
            response_text = ai_message_data.get('content', '')

        except Exception as e:
            return Response({'error': f'AI Error: {str(e)}'}, status=500)

        messages_list.append(ai_message_data)

        
        history_obj.content = messages_list
        
        history_obj.save() 

        return Response({'response': response_text})
    
class problemsViewSet(viewsets.ModelViewSet):# this will need to be changed later and made someting read only and v need to addewd ai 
    serializer_class = UserProblemSerializer 
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return UserProblems.objects.filter(owner=self.request.user)
    # data in this will be updated automaticly from some time set function using django-apscheduler

class TeamMembersViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated] 
    serializer_class = TeamMembersSerializer
    queryset = TeamMembers.objects.all()

class TeamDataViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated] 
    serializer_class = TeamDataSerializer
    queryset = TeamData.objects.all()
    # there will be alot of custom logic later 

class RegisterView(generics.CreateAPIView): # generic view for user registration built-in create behavior
    queryset = User.objects.all() # queryset set to all users so that we can create new ones
    # Everyone must be able to hit this endpoint to sign up!
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

