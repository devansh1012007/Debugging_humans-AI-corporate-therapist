# here all the repeating task will come
# summar + probelsm + team problems
# not working yet
from .models import UserIdeas,User, UserChatDB
from .Ai import idea_lister
from django.shortcuts import get_object_or_404
def Idea_listed():
    users = User.objects.all()
    for user in users:
        '''idea_obj = get_object_or_404(UserIdeas, owner=user)
        existing_ideas = idea_obj.content if isinstance(idea_obj.content, list) else []
        #existing_probs = []
        chats = UserChatDB.objects.filter(owner=user)
        for chat in chats:
            if chat.ideas_listed is True:
                full_chat = chat.content       
                prob_list = idea_lister(full_chat, existing_ideas) 
                existing_ideas.extend(prob_list)
                idea_obj.content = existing_ideas
                idea_obj.save()
                chat.ideas_listed = False
                chat.save()

        chats_to_process = UserChatDB.objects.filter(owner=user, IdeaListed=True)
        updates_made = False'''

        master_doc, created = UserIdeas.objects.get_or_create(
            owner=user,
            defaults={'content': []}
        )

        master_list = master_doc.content if isinstance(master_doc.content, list) else []
        
        # 2. PROCESS CHATS
        # Only fetch chats flagged with IdeaListed=True
        chats_to_process = UserChatDB.objects.filter(owner=user, IdeaListed=True)
        updates_made = False

        for chat in chats_to_process:
            # chat.content is the chat history transcript
            new_ideas_objs = idea_lister(chat.content, master_list) 
            
            if new_ideas_objs:
                # Map AI output keys to our standard schema
                clean_ideas = [
                    {
                        "Idea": item.get('Ideas', item.get('Idea', 'Untitled Idea')), 
                        "Description": item.get('suggestion', item.get('Description', '')),
                        "source": "AI Analysis"
                    } for item in new_ideas_objs
                ]
                master_list.extend(clean_ideas)
                updates_made = True
            
            # Reset flag so we don't process this chat again
            chat.IdeaListed = False 
            chat.save()

        # 3. SAVE & RESPOND
        if updates_made:
            master_doc.content = master_list
            master_doc.save()