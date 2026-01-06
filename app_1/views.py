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
from .Ai import ai_response



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
    # v should add a filter by chat_id
    # chat_session = UserHomepageDB.objects.get(id=chat_id, owner=request.user)
    # return chat_session
    def get_queryset(self):
        return UserChatDB.objects.filter(owner=self.request.user)
    #we don't need to filter the chat by id because we are not using any url parameter here; but chat_id method still works(need to experiment)

    
    @action(detail=False, methods=['post'])# maybe v should also add patch but udt its needed)# @action decorator to create a custom action and v want use perform_create or perform_update here bcoz we are not creating or updating any model instance directly
    def continue_chat(self, request):
        
        user_prompt = request.data.get('prompt')
        ai_mode = request.data.get('mode')
        chat_id = request.data.get('ChatID')
    
        

        try:
            chat_session = UserHomepageDB.objects.get(id=chat_id, owner=request.user)
            # chat_session = chat_session[20:] # for returning last 10 chats 
        except UserHomepageDB.DoesNotExist:
            return Response({'error': f'Chat Session {chat_id} not found for this user.'}, status=404)

        
        history_obj, created = UserChatDB.objects.get_or_create(
            chat=chat_session,
            owner=request.user,
            defaults={'content': []} 
        )
        user_username = request.user.username
        if not user_prompt or not chat_id:
            return Response({'error': 'Prompt and ChatID are required'}, status=400)

        if ai_mode == "therapy":
            model_override = "therapy-ai"
            delet = True
        else:
            model_override = "problem-solver"
        # 1. Get History
        history_obj = get_object_or_404(UserChatDB, chat__id=chat_id, owner=request.user)
        # Ensure it is a list, defaulting to empty
        current_history = history_obj.content if isinstance(history_obj.content, list) else []
        #print("Current History:", current_history)
        #print("User Prompt:", user_prompt)
        #print("AI Mode:", model_override)
        payload = {
            "message": user_prompt,
            "conversation" : current_history,# can cause issues
            "user_profile": "name:" + user_username,
            "workspace_context": "employee in an Indian startup or hight intencity work enviroment",
            "model_override": model_override
        }
             
        try:
            
            ai_result = ai_response(payload) 
            #print("AI Result:", ai_result)
            # Check for error key from our safe Ai.py
            if "error" in ai_result:
                raise ValueError(ai_result["error"])

            ai_message_text = ai_result.get('response', '')
            
            if not ai_message_text:
                raise ValueError("AI returned an empty response")
        except Exception as e:
            return Response({'error': f'AI Error: {str(e)}'}, status=500)

            
        current_history.append({
            "role": "user", 
            "message": user_prompt
        })
        
        # Append AI Message Object
        current_history.append({
            "role": "assistant", 
            "message": ai_message_text
        })


        history_obj.content = current_history
        history_obj.save()
        if delet:
            ai_message_text = ai_message_text[:-4]
        print("response sent: "+ ai_message_text)
        return Response({'response': ai_message_text})
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

