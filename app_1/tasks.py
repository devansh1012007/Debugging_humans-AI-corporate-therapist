# here all the repeating task will come
# summar + probelsm + team problems
# not working yet
from datetime import date
from .models import OrgNode, UserDashboard, UserDashboard,User, UserChatDB, UserDrillDown
from .Ai import idea_lister
from django.shortcuts import get_object_or_404


def generate_drill_down_lists():
    for User in User.objects.all():
        target = User.org_node
        subordinates = target.children.all()
        drill_down_list, created = UserDrillDown.objects.get_or_create(
            owner=User,
            defaults={'content': []}
        )
        #OneToOneField in models
        drill_down = []
        # the 1st ideaa is of the target itselfs
        drill_down.append({
            "node_id": target.id,##### from here frontent can get the id of the node and make api calls to get data for that node
            "name": target.name,
            "has_team": target.children.exists() 
        })
        for child in subordinates:
            drill_down.append({
                "node_id": child.id,
                "name": child.name,
                "has_team": child.children.exists() 
            })
        drill_down_list.content = drill_down
        drill_down_list.save()


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

def process_midnight_snapshots():
    """
    CRON JOB: Runs at 00:00.
    Iterates through every Manager in the company.
    Calculates their TEAM's average for the day/week.
    Saves it as a static snapshot.
    """
    #print(f"--- Starting Batch Processing for {.today()} ---")
    print(f"--- Starting Batch Processing for {date.today()} ---")
    
    # 1. Get all nodes that have subordinates (Managers only)
    # We use distinct() to avoid duplicates
    #managers = OrgNode.objects.filter(children__isnull=False).distinct()
    users = User.objects.all()
    for manager in users:
        # 2. Identify the Team (1 Layer Deep)
        # We only aggregate the Direct Reports.
        if manager.OrgNode.children.exists():
            direct_reports = manager.OrgNode.children.all()

            # 3. Calculate the Stats (The "AI" Processing)
            # We aggregate the metrics from the collected raw logs
            # this needs to be changed 
            target_group_ids = get_direct_reports_ids(manager.OrgNode.id)
            # roughly pseudocode
            # get chats 
            chats = []
            for id in target_group_ids:
                chats.extend(list(UserChatDB.objects.filter(node_id=id)))
            # pass chats to ai model and get avg back
            team_stats = ai_model.calculate_team_averages(chats)
            
            
            
            '''
            stats = MentalHealthMetric.objects.filter(node__in=direct_reports).aggregate(
                avg_wellness=Avg('wellness_index'),
                avg_stress=Avg('stress_level')
            )

            # 4. Filter: Only save if there is data
            if stats['avg_wellness'] is None:
                continue'''

            processed_data = {
                "manager_title": manager.name,
                "team_size": direct_reports.count(),
                "metrics": {
                    "wellness_avg": team_stats['avg_wellness'],
                    "stress_avg": team_stats['avg_stress']
                },
                "status": "Calculated & Verified"
            }

            # 5. Save to Database (The Record)----> need to be chaged heavily + needs to be chges made in models.py also
            master_doc, created = OrgNode.objects.get_or_create(
                node=manager,
                defaults={'data': []}
            )
            master_list = master_doc.data if isinstance(master_doc.data, list) else []
            master_list.extend([processed_data])
            master_doc.data = master_list### THIS NEED TO be set all saved in one json field, SO v just extend the list and save it and also in models v need to change ForeignKey to oneToOneField and also change the related name to content coz 
            master_doc.save()

    for user in users:
        chats = list(OrgNode.objects.filter(node__user=user)) #we need to link chat to nodes
            # pass chats to ai model and get avg back
        team_stats = ai_model.calculate_team_averages(chats)
        personal_doc, created = UserDashboard.objects.get_or_create(
            owner=user,
            defaults={'content': []}
        )
        
        processed_data = {
                "type": "TEAM_SUMMARY",
                    "manager_title": user.name,
                "metrics": {
                    "wellness_avg": team_stats['avg_wellness'],
                    "stress_avg": team_stats['avg_stress']
                },
                "status": "Calculated & Verified"
            }
        personal_doc.content.append(processed_data)
        personal_doc.save()