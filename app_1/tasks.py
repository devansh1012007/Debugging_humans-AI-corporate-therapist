# app_1/tasks.py
from datetime import date
from .models import OrgNode, UserChatSummary, UserDashboard, UserDashboard,User, UserChatDB, UserDrillDown, TeamData, TeamDataHistory, UserDashboardHistory,UserPersonalityData,UserPsycoData,UserPsycoDataHistory,UserPersonalityDataHistoric
from django.shortcuts import get_object_or_404
from .problems_AI import TeamDashboard_data, UserDashboard_data,personality_extractor
from .Ai import summarize_chat_history,assesment
import math
def generate_drill_down_lists(target):
    # 1. Fetch direct subordinates
    subordinates = target.children.all()
    
    # 2. Get or create the container for this specific user
    # Note: Using 'owner' to match your UserDrillDown model
    drill_down_list, created = UserDrillDown.objects.get_or_create(
        owner=target.user,
        defaults={'content': []}
    )

    # 3. Build the new list
    new_drill_down = []
    
    # Add the current user (The "Root" of this view)
    new_drill_down.append({
        "node_id": target.id,
        "name": target.name,
        "title": target.structure_level.name if target.structure_level else "No Title",
        "has_team": subordinates.exists() 
    })

    # Add all direct reports
    for child in subordinates:
        new_drill_down.append({
            "node_id": child.id,
            "name": child.name,
            "title": child.structure_level.name if child.structure_level else "No Title",
            "has_team": child.children.exists() 
        })

    # 4. Save the new list directly (Overwriting the old one)
    drill_down_list.content = new_drill_down
    drill_down_list.save()
    
    return new_drill_down


def get_direct_reports_ids(root_id, include_self=True):
    children_ids = list(OrgNode.objects.filter(parent_id=root_id).values_list('id', flat=True))
    
    if include_self:
        children_ids.append(root_id)
        
    return children_ids



def mid_night():# this is for chat summry--> but rn i am not to use it ,also i need to improve it for updated format of archit's ai 
    users = User.objects.all()
    for user in users:
        # Get all chat sessions for this user   
        user_chats = UserChatDB.objects.filter(owner=user)
        for chat_session in user_chats:
                history_obj = get_object_or_404(UserChatDB, chat=chat_session, owner=user, to_be_summarized=True)
                # summarize the chat history
                summary = summarize_chat_history(history_obj.content)
                UserChatSummary.objects.clear(owner=user, chat=chat_session)
                UserChatSummary.objects.create(
                    owner=user,
                    chat=chat_session,
                    summary=summary
                )
                history_obj.to_be_summarized = False
                history_obj.save()

def get_report():
    users = User.objects.all()
    for user in users:
        User_data, created = UserPsycoData.objects.get_or_create(
            owner=user,
            defaults={'content': {
        "Personality": {
          "Does the user tend not to worry excessively?": "Neutral",
          "Does the user generally like most people they meet?": "Neutral",
          "Does the user have a very active imagination?": "Neutral",
          "Is the user known for prudence and common sense?": "Neutral",
          "Does the user often get angry about how people treat them?": "Neutral",
          "Does the user shy away from crowds of people?": "Neutral",
          "Are aesthetic and artistic concerns relatively unimportant to the user?": "Neutral",
          "Is the user not crafty or sly by nature?": "Neutral",
          "Does the user prefer keeping options open rather than planning everything in advance?": "Neutral",
          "Does the user rarely feel lonely or sad?": "Neutral",
          "Is the user dominant, forceful, and assertive?": "Neutral",
          "Does the user feel life would be uninteresting without strong emotions?": "Neutral",
          "Do some people perceive the user as selfish or egotistical?": "Neutral",
          "Does the user try to perform all assigned tasks conscientiously?": "Neutral",
          "Does the user dread making social blunders when interacting with others?": "Neutral",
          "Does the user have a leisurely style in work and play?": "Neutral",
          "Is the user fairly set in their ways?": "Neutral",
          "Does the user prefer cooperating with others rather than competing?": "Neutral",
          "Is the user easy-going and somewhat lackadaisical?": "Neutral",
          "Does the user rarely overindulge in anything?": "Neutral",
          "Does the user often crave excitement?": "Neutral",
          "Does the user enjoy playing with theories or abstract ideas?": "Neutral",
          "Does the user not mind bragging about talents and accomplishments?": "Neutral",
          "Is the user good at pacing themselves to complete tasks on time?": "Neutral",
          "Does the user often feel helpless and want others to solve their problems?": "Neutral",
          "Has the user never literally jumped for joy?": "Neutral",
          "Is the user often the life of the party?": "Neutral",
          "Does the user feel little concern for others?": "Neutral",
          "Is the user always prepared?": "Neutral",
          "Does the user get stressed out easily?": "Neutral",
          "Does the user have a rich vocabulary?": "Neutral",
          "Does the user tend not to talk much?": "Neutral",
          "Is the user interested in people?": "Neutral",
          "Does the user leave their belongings around?": "Neutral",
          "Is the user relaxed most of the time?": "Neutral",
          "Does the user have difficulty understanding abstract ideas?": "Neutral",
          "Does the user feel comfortable around people?": "Neutral",
          "Does the user insult people?": "Neutral",
          "Does the user pay attention to details?": "Neutral",
          "Does the user worry about things?": "Neutral",
          "Does the user have a vivid imagination?": "Neutral",
          "Does the user prefer to keep in the background?": "Neutral",
          "Is the user generally uninterested in others?": "Neutral",
          "Does the user like order?": "Neutral",
          "Is the user quiet around strangers?": "Neutral",
          "Does the user make people feel at ease?": "Neutral",
          "Is the user exacting or precise in their work?": "Neutral",
          "Does the user often feel sad or blue?": "Neutral",
          "Is the user full of ideas?": "Neutral"
        },
        "Burnout": {
          "Does the user feel emotionally exhausted because of their work?": "Neutral",
          "Does the user feel worn out at the end of a working day?": "Neutral",
          "Does the user feel tired upon waking and facing a new workday?": "Neutral",
          "Can the user easily understand the actions of colleagues or supervisors?": "Neutral",
          "Does the user feel they treat some colleagues impersonally, like objects?": "Neutral",
          "Does the user find working with people all day stressful?": "Neutral",
          "Is the user afraid their work is making them emotionally harder?": "Neutral",
          "Does the user feel full of energy?": "Neutral",
          "Does the user feel frustrated by their work?": "Neutral",
          "Does the user feel they work too hard?": "Neutral",
          "Is the user uninterested in what is going on with many colleagues?": "Neutral",
          "Does the user find direct contact with people at work too stressful?": "Neutral",
          "Does the user find it easy to create a relaxed work atmosphere?": "Neutral",
          "Does the user feel stimulated after working closely with colleagues?": "Neutral",
          "Has the user achieved many rewarding work objectives?": "Neutral",
          "Is the user relaxed when dealing with emotional problems at work?": "Neutral",
          "Does the user feel colleagues blame them for their problems?": "Neutral"
        },
        "Depression": {
          "Does the user experience a depressed mood such as sadness or hopelessness?": "Neutral",
          "Does the user experience feelings of guilt?": "Neutral",
          "Does the user experience suicidal thoughts or behaviors?": "Neutral",
          "Does the user have difficulty falling asleep?": "Neutral",
          "Does the user experience disturbed sleep during the night?": "Neutral",
          "Does the user wake up early due to sleep disturbance?": "Neutral",
          "Has the user's interest in work or activities decreased?": "Neutral",
          "Does the user show psychomotor slowing?": "Neutral",
          "Does the user experience agitation or restlessness?": "Neutral",
          "Does the user experience psychological anxiety?": "Neutral",
          "Does the user experience physical anxiety symptoms?": "Neutral",
          "Does the user experience gastrointestinal symptoms?": "Neutral",
          "Does the user experience general physical symptoms?": "Neutral",
          "Does the user experience sexual or genital symptoms?": "Neutral",
          "Does the user show excessive concern about health?": "Neutral"
        },
        "Anxiety": {
          "Does the user experience an anxious mood?": "Neutral",
          "Does the user experience tension or nervousness?": "Neutral",
          "Does the user experience fears?": "Neutral",
          "Does the user experience insomnia related to anxiety?": "Neutral",
          "Does the user have difficulty concentrating due to anxiety?": "Neutral",
          "Does the user experience depressed mood related to anxiety?": "Neutral",
          "Does the user experience muscular symptoms?": "Neutral",
          "Does the user experience sensory symptoms?": "Neutral",
          "Does the user experience cardiovascular symptoms?": "Neutral",
          "Does the user experience respiratory symptoms?": "Neutral",
          "Does the user experience gastrointestinal symptoms related to anxiety?": "Neutral",
          "Does the user experience genitourinary symptoms related to anxiety?": "Neutral",
          "Does the user experience autonomic symptoms?": "Neutral"
        }}}  
              )
        
        old_data_list = User_data.content if isinstance(User_data.content, dict) else {}
        b = []
        chats = []
        user_chats = UserChatDB.objects.filter(owner=user)
        total_words = 0
        for chat in user_chats:
            for item in chat.content:
                c = item.get("message","")
                words = c.split()
                total_words += len(words)
                estimated_tokens = math.ceil(total_words * 1.5)
                chats.append(chat)
                if estimated_tokens > 5000:
                    a = summarize_chat_history(chats)
                    chats = []
                    total_words = 0
                    b.append(a)

        b.append(chats)
        AI_data = assesment(old_data_list,b)
        AI_data = AI_data
        processed_data = {"content":AI_data,
                          "date": str(date.today())}
        history_doc, created = UserPsycoDataHistory.objects.get_or_create(
            owner=user,
            defaults={'content': []}
        )
        old_data_list = AI_data
        User_data.content = old_data_list
        User_data.save()
        history_list = history_doc.content if isinstance(history_doc.content, list) else {}
        history_list.append(processed_data)
        history_doc.content = history_list
        history_doc.save()
    # personality 
    for user in users:
        User_data, created = UserPersonalityData.objects.get_or_create(
            owner=user,
            defaults={'content': {}})
        old_data_list = User_data.content if isinstance(User_data.content, dict) else None
        b = []
        chats = []
        user_chats = UserChatDB.objects.filter(owner=user)
        total_words = 0
        for chat in user_chats:
            for item in chat.content:
                c = item.get("message","")
                words = c.split()
                total_words += len(words)
                estimated_tokens = math.ceil(total_words * 1.5)
                chats.append(chat)
                if estimated_tokens > 5000:
                    a = summarize_chat_history(chats)
                    chats = []
                    total_words = 0
                    b.append(a)
        
        b.append(chats)
        AI_data = assesment(b,old_data_list) 
        processed_data = {"content":[AI_data]}
        history_doc, created = UserPersonalityDataHistoric.objects.get_or_create(
            owner=user,
            defaults={'content': []}
        )
        old_data_list = processed_data["content"]
        User_data.content = old_data_list
        User_data.save()
        history_list = history_doc.content if isinstance(history_doc.content, list) else []
        history_list.append(processed_data)
        history_doc.content = history_list
        history_doc.save()
        



###############################################################33


def process_midnight_snapshots():
    users = User.objects.all()
    
    for user in users:
        chats = []
        personal_doc, created = UserDashboard.objects.get_or_create(
            owner=user,
            defaults={'content': []}
        )
        user_chats = UserChatDB.objects.filter(owner=user)
        Personal_list = personal_doc.content if isinstance(personal_doc.content, list) else []
        
        processed_data = {
            "content": Personal_list
        }
        
        DashBoardDataAI = None
        total_words = 0
        
        for chat in user_chats:
            for item in chat.content: 
                c = item.get("message", "")   
                words = c.split()
                total_words += len(words)
                estimated_tokens = math.ceil(total_words * 1.5)
                chats.append(chat)
                
                if estimated_tokens > 30000:
                    DashBoardDataAI = UserDashboard_data(chats, processed_data)
                    processed_data = {
                        "content": DashBoardDataAI.model_dump() #
                    }
                    total_words = 0
                    chats = []

        if chats:
            DashBoardDataAI = UserDashboard_data(chats, processed_data)
            processed_data = {
                "content": DashBoardDataAI.model_dump()
            }

        history_doc, created = UserDashboardHistory.objects.get_or_create(
            owner=user,
            defaults={'content': []}
        )
        
        history_list = history_doc.content if isinstance(history_doc.content, list) else []
        history_list.append(processed_data)
        history_doc.content = history_list
        history_doc.save()
        
        
        personal_doc.content = [processed_data] 
        personal_doc.save()


    
    # team dashboard
    for employee in users:
        if employee.org_node.children.exists():
            target_group_ids = get_direct_reports_ids(employee.org_node.id)
            Dahboards = []
            master_doc, created = TeamData.objects.get_or_create(
                node=employee.org_node,
                defaults={'content': []}
            )
            
            master_list = master_doc.content if isinstance(master_doc.content, list) else []            
            '''processed_data={
                "centent":master_list
                }'''
            for node_id in target_group_ids:
                node = OrgNode.objects.get(id=node_id)
                user_DashBoard = UserDashboard.objects.filter(owner=node.user)
                Dahboards.append(user_DashBoard)
            
            AI_Output = TeamDashboard_data(Dahboards, master_list)
            processed_data = {
                "content": AI_Output.model_dump()
            }         
            

            history_doc, created = TeamDataHistory.objects.get_or_create(
                node=employee.org_node,
                defaults={'content': []}
            )
            
            history_list = history_doc.content if isinstance(history_doc.content, list) else []
            history_list.append(processed_data)
            history_doc.content = history_list
            history_doc.save()
            master_doc.content = [processed_data]
            master_doc.save()


 