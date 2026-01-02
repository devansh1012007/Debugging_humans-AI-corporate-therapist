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


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer 
    permission_classes = [permissions.IsAuthenticated] 
    

    def get_queryset(self): # when user will click on any old chat and frontend needs to show the chat
        data = json.loads(self.request.body)
        Chat_ID = data.get('ChatID')
        return UserChatDB.objects.filter(owner=self.request.user,id = Chat_ID)
        
    
    def perform_create(self, serializer): # POST-> staring a new chat so no prior data to give to ai or frontend
        try:
            data = json.loads(self.request.body)
            user_prompt = data.get('prompt')
            ai_mode = data.get('mode')
            Chat_ID = data.get('ChatID')
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'prompt required'}, status=400)
        
        if ai_mode == "therpy":
            ai_result = therpy_ai_response(user_prompt)
            ai_text = ai_result['message']# filtering out from json format 
            # saving data
            responce = ai_text['response']
            serializer.save(owner=self.request.user, content = ai_text, id = Chat_ID)# hopefully it doesnt save anything else
            return JsonResponse({'response': responce})
    
        else:
            ai_result = consiler_ai_responce(user_prompt)
            ai_text = ai_result['response']
            # saving data
            serializer.save(owner=self.request.user, content = ai_text, id = Chat_ID) ## important
            return JsonResponse({'response': ai_text})
       

    def perform_update(self, serializer): # PUSH -> when user will continue chating with ai from some old chat
        try:
            data = json.loads(self.request.body)
            user_prompt = data.get('prompt')
            ai_mode = data.get('mode')
            Chat_ID = data.get('ChatID')
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'prompt required'}, status=400)
        context = UserChatDB.objects.get(id = Chat_ID, owner=self.request.user)
        if ai_mode == "therpy":
            ai_result = therpy_ai_response(user_prompt, context)
            ai_text = ai_result['message']# filtering out from json format 
            # saving data
            responce = ai_text['response']
            serializer.save(owner=self.request.user, content = ai_text, id = Chat_ID)# hopefully it doesnt save anything else
            return JsonResponse({'response': responce})
    
        else:
            ai_result = consiler_ai_responce(user_prompt, context)
            ai_text = ai_result['response']
            # saving data
            serializer.save(owner=self.request.user, content = ai_text, id = Chat_ID) ## important
            return JsonResponse({'response': ai_text})

