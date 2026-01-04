'''
def continue_chat(request, session_uuid):
    user_prompt = request.POST.get('text')
    history_obj = UserChatDB.objects.get(chat_session__id=session_uuid, owner=request.user)
    
    # 1. Get current history
    current_messages = history_obj.full_history 
    
    # 2. Append user message
    current_messages.append({"role": "user", "content": user_prompt})
    
    # 3. Get AI Response (placeholder logic)
    ai_response = "This is the AI response" 
    current_messages.append({"role": "assistant", "content": ai_response})
    
    # 4. Save back to DB
    history_obj.full_history = current_messages
    history_obj.save()

'''


'''class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer 
    permission_classes = [permissions.IsAuthenticated] 
    

    def get_queryset(self,request): # when user will click on any old chat and frontend needs to show the chat
        Chat_ID = request.data.get('ChatID')
        return UserChatDB.objects.filter(owner=self.request.user,id = Chat_ID)
        
    
    def perform_create(self, request): # POST-> staring a new chat so no prior data to give to ai or frontend
        try:
            user_prompt = request.data.get('prompt')
            ai_mode = request.data.get('mode')
            Chat_ID = request.data.get('ChatID')
        
        except :
            return JsonResponse({'error': 'provide all details'}, status=400)
        
        history_obj = get_object_or_404(UserChatDB, chat__id=Chat_ID, owner=request.user)
        history_obj = history_obj.content
        history_obj.append({"role": "user", "content": user_prompt})

        if ai_mode == "therpy":
            ai_result = therpy_ai_response(user_prompt)
            ai_text = ai_result['message']# filtering out from json format 
            # saving data
            history_obj.append(ai_text)
            responce = ai_text['response']
            history_obj.save()
            return JsonResponse({'response': responce})
    
        else:
            ai_result = consiler_ai_responce(user_prompt)
            ai_text = ai_result['response']
            history_obj.append(ai_text)
            responce = ai_text['response']
            history_obj.save()
            return JsonResponse({'response': ai_text})
       

    def perform_update(self, request): # PUSH -> when user will continue chating with ai from some old chat
        try:
            user_prompt = request.data.get('prompt')
            ai_mode = request.data.get('mode')
            Chat_ID = request.data.get('ChatID')
        
        except :
            return JsonResponse({'error': 'prompt required'}, status=400)
        context = UserChatDB.objects.get(id = Chat_ID, owner=self.request.user)
        
        context = context.content
               
        if ai_mode == "therpy":
            ai_result = therpy_ai_response(user_prompt, context)
            ai_text = ai_result['message']# filtering out from json format 
            # saving data
            context.append({"role": "user", "content": user_prompt})
            context.append(ai_text)
            responce = ai_text['response']
            context.save()
            return JsonResponse({'response': responce})
    
        else:
            ai_result = consiler_ai_responce(user_prompt, context)
            ai_text = ai_result['message']
            context.append({"role": "user", "content": user_prompt})
            context.append(ai_text)
            responce = ai_text['response']
            context.save()
            return JsonResponse({'response': responce})
'''



'''from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import UserChatDB
# Import your AI functions here

class SendMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_id):
        # 1. Manual Fetching (No get_queryset magic here)
        # We explicitly look for the chat linked to the UUID and the User
        history_obj = get_object_or_404(UserChatDB, chat__id=chat_id, owner=request.user)

        # 2. Extract Data
        user_prompt = request.data.get('prompt')
        if not user_prompt:
            return Response({"error": "Prompt missing"}, status=400)

        # 3. Update History Logic (Same as before)
        current_history = history_obj.content
        current_history.append({"role": "user", "content": user_prompt})

        # --- AI CALL GOES HERE ---
        ai_response = "Simulated AI Response" # Replace with your function
        
        current_history.append({"role": "assistant", "content": ai_response})
        
        # 4. Save
        history_obj.content = current_history
        history_obj.save()

        return Response({"response": ai_response})'''
###########################################################################################
'''from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message_func(request, chat_id):
    # 1. Fetch
    history_obj = get_object_or_404(UserChatDB, chat__id=chat_id, owner=request.user)
    
    # 2. Logic
    user_prompt = request.data.get('prompt')
    
    # ... (Insert your AI and Append logic here) ...
    
    history_obj.save()
    
    return Response({"status": "success"})'''

############################################################################################
'''from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import UserHomepageDB, UserChatDB
from .serializers import HomePageSerializer, ChatSerializer
from Ai import therpy_ai_response, consiler_ai_responce 

# Class 1: Managing Chat Sessions (The Sidebar)
class OldChatsViewSet(viewsets.ModelViewSet):
    serializer_class = HomePageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 1. Return only chats owned by the user
        return UserHomepageDB.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # 2. When User clicks "New Chat", we create the session AND the empty history
        session = serializer.save(owner=self.request.user)
        
        # Auto-create the linked history row so it exists immediately
        UserChatDB.objects.create(
            owner=self.request.user, 
            chat=session, 
            content=[]
        )

# Class 2: Managing the Chat Messages
class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # This tells DRF to look for the 'chat_id' in the URL
    lookup_field = 'chat__id'

    def get_queryset(self):
        return UserChatDB.objects.filter(owner=self.request.user)

    # ACTION: Handling the AI Logic separately
    # Endpoint: POST /api/chat_interface/{uuid}/send_message/
    @action(detail=True, methods=['post'])
    def send_message(self, request, chat__id=None):
        # 1. Fetch the history object for this chat session
        # We look up by the related field 'chat__id'
        history_obj = get_object_or_404(UserChatDB, chat__id=chat__id, owner=request.user)
        
        # 2. Extract Data (No need for json.loads)
        user_prompt = request.data.get('prompt')
        ai_mode = request.data.get('mode', 'therpy')
        
        if not user_prompt:
            return Response({'error': 'Prompt is required'}, status=400)

        # 3. APPEND User Message (Don't overwrite!)
        current_history = history_obj.content # Get existing list
        current_history.append({"role": "user", "content": user_prompt})

        # 4. Call AI (Pass the full history for context)
        try:
            if ai_mode == "therpy":
                # Assuming your AI function takes (prompt, history)
                ai_result = therpy_ai_response(user_prompt, current_history)
                # Adjust these keys based on your actual AI return
                response_text = ai_result.get('message', {}).get('response', '')
            else:
                ai_result = consiler_ai_responce(user_prompt, current_history)
                response_text = ai_result.get('response', '')
        except Exception as e:
            return Response({'error': f"AI Error: {str(e)}"}, status=500)

        # 5. APPEND AI Response
        current_history.append({"role": "assistant", "content": response_text})

        # 6. Save back to DB
        history_obj.content = current_history
        history_obj.save()

        # Optional: Update 'last_updated' on the parent session so it moves to top of sidebar
        history_obj.chat.save()

        return Response({'response': response_text, 'history': current_history})'''




######### final 
'''from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    lookup_field = 'chat__id'
    def get_queryset(self,request): # 
        return UserChatDB.objects.filter(owner=self.request.user)
    #we don't need to filter the chat by id because we are not using any url parameter here; but chat_id method still works(need to experiment)


    @action(detail=False, methods=['post'])# @action decorator to create a custom action and v want use perform_create or perform_update here bcoz we are not creating or updating any model instance directly
    def continue_chat(self, request):
        
        user_prompt = request.data.get('prompt')
        ai_mode = request.data.get('mode')
        chat_id = request.data.get('ChatID')

        if not user_prompt or not chat_id:
            return Response({'error': 'Prompt and ChatID are required'}, status=400)

        history_obj = get_object_or_404(UserChatDB, chat__id=chat_id, owner=request.user)

        
        messages_list = history_obj.content 

    
        messages_list.append({"role": "user", "content": user_prompt})

        try:
            if ai_mode == "therpy":
                ai_result = therpy_ai_response(user_prompt, messages_list)
                ai_message_data = ai_result.get('message', {})
            else:
                ai_result = consiler_ai_responce(user_prompt, messages_list)
                ai_message_data = ai_result.get('message', {})
            
            # Extract just the text response to send back to frontend
            response_text = ai_message_data.get('response', '')

        except Exception as e:
            return Response({'error': f'AI Error: {str(e)}'}, status=500)

        messages_list.append(ai_message_data)

        
        history_obj.content = messages_list
        
        history_obj.save() 

        return Response({'response': response_text})'''