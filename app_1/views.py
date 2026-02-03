#views.py
from rest_framework import viewsets, permissions
from .models import PrivacyPolicyAcceptance, UserFeedback, UserHomepageDB, UserChatDB,TeamMembers,TeamData,UserProblems,ConsentFormAcceptance,UserPsycoData
from .serializers import ConsentFormAcceptanceSerializer, HomePageSerializer, ChatSerializer, PrivacyPolicyAcceptanceSerializer, UserFeedbackSerializer, UserProblemSerializer, TeamMembersSerializer, TeamDataSerializer, UserPsycoDataSerializer
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
from .permissions import IsManager
from django.http import StreamingHttpResponse



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
    def get_queryset(self):# used for filtering the chat history based on chat session id #It is the "Django way" to handle ownership.
        chat_id = self.request.query_params.get('chat_id')
        if chat_id is None:
            # Return nothing if no ID provided, or use UserChatDB.objects.none()
            return UserChatDB.objects.filter(owner=self.request.user) 
        chat_session = get_object_or_404(UserHomepageDB, id=chat_id, owner=self.request.user)
        return UserChatDB.objects.filter(chat=chat_session, owner=self.request.user)
    
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
    
        # 2. Define the Stream Generator
        def stream_wrapper():
            full_reply = "" # Keep track of the full string to save to DB later
            
            # Determine which generator to use
            if ai_mode == "specialist":
                gen = therpy_ai_response(user_prompt, current_history)
            else:
                gen = consiler_ai_responce(user_prompt, current_history)
    
            for token in gen:
                full_reply += token
                yield token # Send token to frontend
    
            # 3. SAVE TO DB: This only runs after the 'for' loop finishes (stream ends)
            current_history.append({"role": "user", "content": user_prompt})
            current_history.append({"role": "assistant", "content": full_reply})
            
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

class UserPsycoDataViewSet(viewsets.ModelViewSet):# this will need to be changed later 
    serializer_class = UserPsycoDataSerializer 
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return UserPsycoData.objects.filter(owner=self.request.user)
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class problemsViewSet(viewsets.ModelViewSet):# this will need to be changed later and made someting read only and v need to addewd ai 
    serializer_class = UserProblemSerializer 
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return UserProblems.objects.filter(owner=self.request.user)
    def partial_update(self, serializer):
        serializer.save(owner=self.request.user)
    # data in this will be updated automaticly from some time set function using django-apscheduler

class TeamMembersViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser] 
    serializer_class = TeamMembersSerializer
    queryset = TeamMembers.objects.all()

class TeamDataViewSet(viewsets.ModelViewSet):
    permission_classes = [IsManager]
    serializer_class = TeamDataSerializer
    queryset = TeamData.objects.all()
    # there will be alot of custom logic later 

class RegisterView(generics.CreateAPIView): # generic view for user registration built-in create behavior
    queryset = User.objects.all() # queryset set to all users so that we can create new ones
    # Everyone must be able to hit this endpoint to sign up!
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class UserFeedbackViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserFeedbackSerializer
    #queryset = UserFeedback.objects.filter(owner=self.request.user)
    def get_queryset(self):
        return UserFeedback.objects.filter(owner=self.request.user)
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class PrivacyPolicyAcceptanceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PrivacyPolicyAcceptanceSerializer
    #queryset = PrivacyPolicyAcceptance.objects.all()
    def get_queryset(self):
        return PrivacyPolicyAcceptance.objects.filter(owner=self.request.user)
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ConsentFormAcceptanceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConsentFormAcceptanceSerializer
    #queryset = ConsentFormAcceptance.objects.all()
    def get_queryset(self):
        return ConsentFormAcceptance.objects.filter(owner=self.request.user)
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


from django.http import JsonResponse

def TeamData2(request):
    data = {
        'summary': 'This is a summary of the team data.',
        'recommendation': [{'recommendation': 'Recommendation 1'}, {'recommendation': 'Recommendation 2'}],
        'common_problems': [{'problem': 'Problem 1'}, {'problem': 'Problem 2'}]
    }
    # Use JsonResponse to return the dictionary as a JSON object
    return JsonResponse(data)

def PrivacyPolicy(request):
    policy_text = """
    Privacy Policy

    Effective Date: January 1, 2024

    1. Introduction
    We value your privacy and are committed to protecting your personal information. This Privacy Policy outlines how we collect, use, and safeguard your data.

    2. Information We Collect
    - Personal Information: Name, email address, contact details.
    - Usage Data: IP address, browser type, pages visited.

    3. How We Use Your Information
    - To provide and maintain our services.
    - To communicate with you about updates and promotions.
    - To improve our website and services.

    4. Data Sharing
    We do not sell or rent your personal information to third parties. We may share data with service providers who assist us in operating our business.

    5. Data Security
    We implement security measures to protect your data from unauthorized access, alteration, disclosure, or destruction.

    6. Your Rights
    You have the right to access, correct, or delete your personal information. Contact us to exercise these rights.

    7. Changes to This Policy
    We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated effective date.

    8. Contact Us
    If you have any questions about this Privacy Policy, please contact us at"""
    return JsonResponse({'privacy_policy': policy_text})

def TermsOfService(request):
    terms_text = """
    Terms of Service

    Effective Date: January 1, 2024

    1. Acceptance of Terms
    By accessing or using our services, you agree to be bound by these Terms of Service.

    2. User Responsibilities
    You agree to use our services in compliance with all applicable laws and regulations.

    3. Intellectual Property
    All content and materials provided through our services are the property of the company and protected by intellectual property laws.

    4. Limitation of Liability
    We are not liable for any damages arising from your use of our services.

    5. Termination
    We reserve the right to terminate or suspend your access to our services at our discretion.

    6. Changes to Terms
    We may modify these Terms of Service at any time. Continued use of our services constitutes acceptance of the updated terms.

    7. Contact Us
    If you have any questions about these Terms of Service, please contact us at"""
    return JsonResponse({'terms_of_service': terms_text})

def UserPsycoData(request):
    data = {
        'summary': 'This is a summary of the team data.',
        'recommendation': [{'recommendation': 'Recommendation 1'}, {'recommendation': 'Recommendation 2'}],
        'common_problems': [{'problem': 'Problem 1'}, {'problem': 'Problem 2'}]
    }
    return JsonResponse(data)

