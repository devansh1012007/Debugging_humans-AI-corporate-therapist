# views.py

# Import necessary tools to build API views and check permissions (like if a user is logged in)
from rest_framework import viewsets, permissions
# Import the database models (the filing cabinet definitions)
from .models import UserHomepageDB, UserChatDB, TeamMembers, TeamData, UserProblems
# Import the translators (serializers) to convert data to JSON
from .serializers import HomePageSerializer, ChatSerializer, UserProblemSerializer, TeamMembersSerializer, TeamDataSerializer
# Import generic views for standard tasks and the User model for authentication
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
# Import decorators to create custom actions (like "continue_chat")
from rest_framework.decorators import action
# Import the standard tool to send answers back to the user
from rest_framework.response import Response
# Import a shortcut to get data or show a 404 error if missing
from django.shortcuts import get_object_or_404
# Import permission to allow anyone (even guests) to access a view
from rest_framework.permissions import AllowAny
# Import Python's built-in tool for handling JSON text
import json
# Import a Django specific JSON response tool
from django.http import JsonResponse
# Import the custom AI function that generates the therapy responses
from .Ai import ai_response

# Class 1: Manages the "Menu" of chats (The list of past conversations)
class OldChatsViewSet(viewsets.ModelViewSet):
    # Use the HomePageSerializer to translate the data
    serializer_class = HomePageSerializer 
    # Only allow logged-in users to access this
    permission_classes = [permissions.IsAuthenticated] 

    # This function decides which chats to show the user
    def get_queryset(self):
        # Return only the chats that belong to the current logged-in user
        return UserHomepageDB.objects.filter(owner=self.request.user)

    # This function runs automatically when a user creates a NEW chat session
    def perform_create(self, serializer):
        # Save the new chat session and mark the current user as the owner
        session = serializer.save(owner=self.request.user) 
        # Simultaneously create an empty entry in the UserChatDB (where the actual messages will go)
        # This links the "Book Cover" (UserHomepageDB) to the "Pages" (UserChatDB)
        UserChatDB.objects.create( 
            owner=self.request.user, 
            chat=session, 
            content=[] # Start with an empty list of messages
        )

# Class 2: Manages the actual messages inside a chat
class ChatViewSet(viewsets.ModelViewSet):
    # Use the ChatSerializer to translate the message history
    serializer_class = ChatSerializer
    # Only allow logged-in users
    permission_classes = [permissions.IsAuthenticated]
    
    # This function gets the chat history for the current user
    def get_queryset(self):
        return UserChatDB.objects.filter(owner=self.request.user)

    # Custom Action: This is the core feature. It handles "talking" to the AI.
    # It listens for a POST request (sending data)
    @action(detail=False, methods=['post'])
    def continue_chat(self, request):
        
        # Extract the user's message from the incoming data
        user_prompt = request.data.get('prompt')
        # Extract the AI personality mode (e.g., therapy)
        ai_mode = request.data.get('mode')
        # Extract the ID of the chat session
        chat_id = request.data.get('ChatID')
    
        try:
            # Try to find the specific chat session belonging to this user
            chat_session = UserHomepageDB.objects.get(id=chat_id, owner=request.user)
        except UserHomepageDB.DoesNotExist:
            # If not found, return a 404 error
            return Response({'error': f'Chat Session {chat_id} not found for this user.'}, status=404)
        
        # Get the history object (the messages), or create it if it doesn't exist (safety check)
        history_obj, created = UserChatDB.objects.get_or_create(
            chat=chat_session,
            owner=request.user,
            defaults={'content': []} 
        )
        
        # Get the username to personalize the AI response
        user_username = request.user.username
        
        # Validation: Ensure the user actually sent a message and a chat ID
        if not user_prompt or not chat_id:
            return Response({'error': 'Prompt and ChatID are required'}, status=400)

        # Set the specific AI model based on the mode selected
        if ai_mode == "therapy":
            model_override = "therapy-ai"
        else:
            model_override = ""

        # Retrieve the chat history object again to be safe
        history_obj = get_object_or_404(UserChatDB, chat__id=chat_id, owner=request.user)
        
        # Ensure the content is a list (array), if it's null, make it an empty list
        current_history = history_obj.content if isinstance(history_obj.content, list) else []

        # Prepare the packet of data (payload) to send to the AI brain
        payload = {
            "message": user_prompt, # The new message
            "conversation" : current_history, # The past context
            "user_profile": "name:" + user_username, # Who is talking
            "workspace_context": "employee in an Indian startup or hight intencity work enviroment", # The setting
            "model_override": model_override # The personality
        }
             
        try:
            # Send the payload to the AI function and wait for a response
            ai_result = ai_response(payload) 
            
            # Check if the AI function reported an error
            if "error" in ai_result:
                raise ValueError(ai_result["error"])

            # Extract the actual text response from the AI's result
            ai_message_text = ai_result.get('response', '')
            
            # If the AI sent nothing back, raise an error
            if not ai_message_text:
                raise ValueError("AI returned an empty response")
        except Exception as e:
            # If anything crashed during the AI part, tell the frontend
            return Response({'error': f'AI Error: {str(e)}'}, status=500)

        # Add the User's message to the history list
        current_history.append({
            "role": "user", 
            "message": user_prompt
        })
        
        # Add the AI's response to the history list
        current_history.append({
            "role": "assistant", 
            "message": ai_message_text
        })

        # Save the updated history list back to the database
        history_obj.content = current_history
        history_obj.save()
        
        # (Optional) Remove the last 4 characters if they are garbage formatting
        ai_message_text = ai_message_text[:-4]
        
        # Print to the server console for debugging
        print("response sent: "+ ai_message_text)
        
        # Send the final answer back to the frontend website
        return Response({'response': ai_message_text})

# Class 3: Manages user problems/assessments
class problemsViewSet(viewsets.ModelViewSet):
    # Use the UserProblemSerializer
    serializer_class = UserProblemSerializer 
    permission_classes = [permissions.IsAuthenticated]
    # Get problems for the current user
    def get_queryset(self):
        return UserProblems.objects.filter(owner=self.request.user)
    # Note: Logic to update this automatically via scheduler is planned for later

# Class 4: Manages Team Members (List of people in a team)
class TeamMembersViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated] 
    serializer_class = TeamMembersSerializer
    # This gets ALL team members (Note: This might be a privacy issue later if not restricted)
    queryset = TeamMembers.objects.all()

# Class 5: Manages Team Data (Reports and Summaries)
class TeamDataViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated] 
    serializer_class = TeamDataSerializer
    # Gets all team data
    queryset = TeamData.objects.all()

# Class 6: Manages User Registration (Sign up)
class RegisterView(generics.CreateAPIView): 
    # Allow creating new users in the main User database
    queryset = User.objects.all() 
    # Allow ANYONE to access this (you don't need to be logged in to sign up)
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer