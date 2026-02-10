# app_1/tasks.py
from datetime import date
from .models import OrgNode, UserChatSummary, UserDashboard, UserDashboard,User, UserChatDB, UserDrillDown, TeamData, TeamDataHistory, UserDashboardHistory,UserPersonalityData
from django.shortcuts import get_object_or_404
from .problems_AI import TeamDashboard_data, UserDashboard_data
from .Ai import summarize_chat_history
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
        User_data, created = UserDashboard.objects.get_or_create(
            owner=user,
            defaults={'content': []}
        )
        Personal_list = User_data.content if isinstance(User_data.content, list) else []




###############################################################33


def process_midnight_snapshots():
    users = User.objects.all()
    # Process User Dashboard
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
        total_words = 0
        for chat in user_chats:
            words = chat["content"].split()
            total_words += len(words)
            estimated_tokens = math.ceil(total_words * 1.5)
            chats.append[chat]
            if estimated_tokens > 30000:
                DashBoardDataAI = UserDashboard_data(chats, processed_data)
                processed_data = {
            "content": DashBoardDataAI}
                total_words = 0
                chats = []
        
        
        processed_data = {
            "content": DashBoardDataAI
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
                "content": AI_Output
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

    