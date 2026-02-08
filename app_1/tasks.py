# app_1/tasks.py
from datetime import date
from .models import OrgNode, UserChatSummary, UserDashboard, UserDashboard,User, UserChatDB, UserDrillDown, TeamData, TeamDataHistory, UserDashboardHistory
from django.shortcuts import get_object_or_404
def ai_model(chats):
    pass

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
    """
    Returns only the node itself and its immediate children.
    """
    # Get IDs of people who report directly to this ID
    children_ids = list(OrgNode.objects.filter(parent_id=root_id).values_list('id', flat=True))
    
    if include_self:
        children_ids.append(root_id)
        
    return children_ids

def ai_model():
    pass

def mid_night():# this is for chat summry
    users = User.objects.all()
    for user in users:
        # Get all chat sessions for this user   
        user_chats = UserChatDB.objects.filter(owner=user)
        for chat_session in user_chats:
                history_obj = get_object_or_404(UserChatDB, chat=chat_session, owner=user, to_be_summarized=True)
                # summarize the chat history
                summary = ai_model(history_obj.content)
                UserChatSummary.objects.clear(owner=user, chat=chat_session)
                UserChatSummary.objects.create(
                    owner=user,
                    chat=chat_session,
                    summary=summary
                )
                history_obj.to_be_summarized = False
                history_obj.save()

def process_midnight_snapshots():
    users = User.objects.all()
    for employee in users:
        if employee.OrgNode.children.exists():
            direct_reports = employee.OrgNode.children.all()
            target_group_ids = get_direct_reports_ids(employee.OrgNode.id)
            # get chats 
            chats = []
            for id in target_group_ids:
                user_ = id.user
                user_chats = UserChatDB.objects.filter(owner=user_)
                for chat in user_chats:
                    chats.append(chat.content)
            # pass chats to ai model and get avg back
            TeamData = ai_model(chats)
            processed_data = {# cut this bs and the format of setup_dev_data
                "employee_name": employee.name,
                "employee_title": employee.OrgNode.structure_level.name,
                "team_size": direct_reports.count(),
                "team_data": TeamData,
                "status": "Calculated & Verified",
                "date": date.today()
            }
            
            master_doc, created = TeamDataHistory.objects.get_or_create(
                node=employee,
                defaults={'content': []}
            )
            history_doc, created = TeamDataHistory.objects.get_or_create(
                node=employee,
                #team_data=master_doc,
                defaults={'data': []})
            
            history_list = history_doc.content if isinstance(history_doc.content, list) else []
            master_list = master_doc.content if isinstance(master_doc.content, list) else []
            history_list.append(processed_data)
            master_list.clear()
            master_list.append(processed_data)
            master_doc.content = master_list
            master_doc.save()
            history_doc.content = history_list
            history_doc.save()

    for user in users:
        chats = []
        # Get all chat sessions for this user
        user_chats = UserChatDB.objects.filter(owner=user)
        for chat in user_chats:
            chats.append(chat.content)
        
        DashBoardData= ai_model(chats)
        
        personal_doc, created = UserDashboard.objects.get_or_create(
            owner=user,
            #node = employee.OrgNode.id
            defaults={'content': []}
        )
        
        processed_data = {
                "employee_name": user.name,
                "employee_title": user.OrgNode.structure_level.name if user.OrgNode else "No Title",
                "_personal_dashboard_data": DashBoardData,
                "date": date.today(),
                "status": "Calculated & Verified"
            }
        
        history_doc, created = UserDashboardHistory.objects.get_or_create(
                owner=user,
                #dashboard=personal_doc,
                defaults={'content': []})
        history_list = history_doc.content if isinstance(history_doc.content, list) else []
        history_list.append(processed_data)
        history_doc.content = history_list
        history_doc.save()
        personal_doc.content.clear()
        Personal_list = personal_doc.content if isinstance(personal_doc.content, list) else []
        Personal_list.append(processed_data)
        personal_doc.content = Personal_list
        personal_doc.save()