from django.db import connection
from django.db.models import Avg
from .models import OrgNode, MentalHealthMetric, ReportSnapshot

def get_direct_reports_ids(root_id, include_self=True):
    """
    Returns only the node itself and its immediate children.
    """
    # Get IDs of people who report directly to this ID
    children_ids = list(OrgNode.objects.filter(parent_id=root_id).values_list('id', flat=True))
    
    if include_self:
        children_ids.append(root_id)
        
    return children_ids

'''
# You install django-mptt and change your model to MPTTModel
def get_subtree_ids_mptt(node):
    # This becomes an incredibly fast single query:
    # SELECT id FROM table WHERE lft BETWEEN node.lft AND node.rght
    return node.get_descendants(include_self=True).values_list('id', flat=True)
'''
'''
def get_subtree_ids_path(node_path): # If you were to implement a Materialized Path (like storing path = "1/5/12") carelessly, it could indeed create security vulnerabilities—specifically Information Disclosure and ID Enumeration.
    # Find everyone whose path starts with my path
    return OrgNode.objects.filter(path__startswith=node_path).values_list('id', flat=True)
'''
'''
def has_object_permission(self, request, view, obj):
    me = request.user.org_node
    # If my path is '1/5' and target is '1/5/12', I am their boss.
    return obj.path.startswith(me.path)
'''

def run_weekly_distribution():
    # 1. Get all nodes that have a User assigned
    # (We don't want to generate reports for vacant positions)
    all_positions = OrgNode.objects.filter(user__isnull=False)

    for position in all_positions:
        # For a weekly automated run, the 'requester' is effectively 'system' 
        # or we treat it as if the person is viewing their own team/self.
        
        generate_mental_health_report(
            target_node_id=position.id,
            requester_node_id=position.id, # Seeing their own data/team
            save=True,                     # Permanently save to ReportSnapshot
            report_type='WEEKLY'
        )

def generate_mental_health_report(target_node_id, requester_node_id, save=False, report_type='WEEKLY'):
    """
    target_node_id: The person/team being viewed.
    requester_node_id: The person LOGGED IN.
    """
    try:
        target_node = OrgNode.objects.select_related('structure_level').get(id=target_node_id)# knowing if this is manager or not is important for the report and also we need to know the role of the person for the report
    except OrgNode.DoesNotExist:
        return None

    # CONTEXT CHECK: Who is looking?
    # this need to be removed 
    is_self = (target_node_id == requester_node_id)
    
    # 1. RAW LOGS (Personal Access Only)
    # If I am looking at myself, I get my diary/logs.
    # If I am looking at my subordinate, I get EMPTY list (Privacy).
    raw_logs = [] 
    # this will be chat extraction 
    if is_self:
        raw_logs = list(MentalHealthMetric.objects.filter(node_id=target_node_id).values(
            'id', 'wellness_index', 'stress_level', 'note', 'date_recorded'
        ))
    '''
    raw_logs = list(MentalHealthMetric.objects.filter(node_id=target_node_id).values(
    'id', 'wellness_index', 'stress_level', 'note', 'date_recorded'
    ))
    '''
    # 2. AGGREGATE DATA (Manager Access)
    # If the target is a Manager (has subordinates), calculate the team average.
    target_group_ids = get_direct_reports_ids(target_node_id)
    # Important: Exclude the target node itself from the team average if strict separation is needed, 
    # but usually "Team Average" includes the lead. 
    
    # Check if target manages people
    has_subordinates = target_node.children.exists()
    
    team_stats = None
    drill_down = []

    if has_subordinates:
        # Calculate Team Average
        #in mane v need to find avg using ai here 
        # this need to chage to code where v r sending chhts to ai and getting avg back
        #it will be done like this :
        '''
        # roughly pseudocode
        # get chats 
        chats = []
        for id in target_group_ids:
            chats.extend(list(MentalHealthMetric.objects.filter(node_id=id)))
        # pass chats to ai model and get avg back
        team_stats = ai_model.calculate_team_averages(chats)
        # v need to extract data from json format but that will be done later
        team_stats_data = {
            "avg_wellness": team_stats['avg_wellness'],
            "avg_stress": team_stats['avg_stress']}
        
        # saving time and data v got from ai
        master_doc, created = UserIdeas.objects.get_or_create(
            owner=user,
            defaults={'content': []}
        )
        master_list = master_doc.content if isinstance(master_doc.content, list) else []
        master_list.extend(team_stats_data)
        master_doc.content = master_list
        master_doc.save()
        
        '''

        agg = MentalHealthMetric.objects.filter(node_id__in=target_group_ids).aggregate(avg_wellness=Avg('wellness_index'), avg_stress=Avg('stress_level'))
        team_stats = {
            "avg_wellness": round(agg['avg_wellness'], 1) if agg['avg_wellness'] else None,
            "avg_stress": round(agg['avg_stress'], 1) if agg['avg_stress'] else None
        }

        # Create Drill-Down (Anonymous Averages for direct reports)
        # We recursively get averages for children, NEVER raw logs.
        drill_down_list = []
        for child in children:
            # We include the ID so the frontend can call this function again for the child
            drill_down_list.append({
                "node_id": child.id,
                "name": child.name, # Position Name (e.g. "Backend Lead")
                "rank": child.structure_level.level_rank, # The Numerical System
                "has_team": child.children.exists() # UI Hint: Should this be clickable?
            })

            drill_down.append({
                "name": child.name,
                "role": child.structure_level.name,
                "team_wellness_avg": visible_score
            })

    '''# 3. CONSTRUCT FINAL JSON
    report_data = {
        "meta": {
            "name": target_node.name,
            "role": target_node.structure_level.name,
            "view_type": "PERSONAL" if is_self else "MANAGEMENT"
        },
        "my_data": {
            "logs": raw_logs, # Only populated if is_self is True
        },
        "team_data": {
            "stats": team_stats, # Only populated if target has subordinates
            "breakdown": drill_down
        }
    }'''

    # 4. SAVE SNAPSHOT
    if save:
        ReportSnapshot.objects.create(
            node=target_node,
            report_type=report_type,
            data=report_data
        )

    return report_data



from django.db.models import Avg
from .models import OrgNode, MentalHealthMetric

def generate_team_level_report(target_node_id):
    """
    Calculates stats ONLY for the immediate children of the target.
    This provides the 'Team Averages' without exposing individual 'Leaf' data.
    """
    target = OrgNode.objects.select_related('structure_level').get(id=target_node_id)
    
    # 1. Get Direct Reports (1 Layer Down)
    children = target.children.all()
    
    # 2. Guard: If this is an Individual (Leaf Node) with no team, return nothing.
    # The manager can view the "Team Lead" to see the team's avg, 
    # but cannot view the "Individual" directly to see their specific score.
    if not children.exists():
        return {
            "status": "RESTRICTED",
            "message": "This is an individual contributor. Individual data is private."
        }

    # 3. Calculate Average of the Children (The Team Score)
    # We aggregate the wellness of the people reporting to this target.
    team_stats = MentalHealthMetric.objects.filter(node__in=children).aggregate(
        avg_wellness=Avg('wellness_index'),
        avg_stress=Avg('stress_level')
    )

    # 4. Prepare the "Next Step" Drill Down List
    # We show the children so the frontend knows which IDs are available to click next.
    drill_down_list = []
    for child in children:
        # We include the ID so the frontend can call this function again for the child
        drill_down_list.append({
            "node_id": child.id,
            "name": child.name, # Position Name (e.g. "Backend Lead")
            "rank": child.structure_level.level_rank, # The Numerical System
            "has_team": child.children.exists() # UI Hint: Should this be clickable?
        })

    return {
        "viewing_target": target.name,
        "level_rank": target.structure_level.level_rank,
        "team_summary": {
            "wellness_avg": round(team_stats['avg_wellness'], 1) if team_stats['avg_wellness'] else None,
            "stress_avg": round(team_stats['avg_stress'], 1) if team_stats['avg_stress'] else None
        },
        "drill_down": drill_down_list
    }



from django.db.models import Avg
from .models import OrgNode, MentalHealthMetric

def generate_team_level_report(target_node_id, requester_node_id):
    target = OrgNode.objects.select_related('structure_level').get(id=target_node_id)
    
    # CHECK: Is this a "Self View"?
    is_self_view = (target_node_id == requester_node_id)
    
    # 1. Get Direct Reports (The Team)
    children = target.children.all()
    has_team = children.exists()

    # --- SCENARIO A: INDIVIDUAL CONTRIBUTOR (No Team) ---
    if not has_team:
        if is_self_view:
            # CORRECT: I can see my own data
            my_logs = MentalHealthMetric.objects.filter(node=target).values(
                'wellness_index', 'stress_level', 'date_recorded'
            )
            data = {
                "view_type": "PERSONAL_DASHBOARD",
                "person": target.name,
                "data": list(my_logs)
            }
        

    # --- SCENARIO B: MANAGER (Has Team) ---
    # Both the Manager and the CEO can see this (Team Averages)
    
    team_stats = MentalHealthMetric.objects.filter(node__in=children).aggregate(
        avg_wellness=Avg('wellness_index'),
        avg_stress=Avg('stress_level')
    )

    drill_down = []
    for child in children:
        drill_down.append({
            "node_id": child.id,
            "name": child.name,
            "has_team": child.children.exists() 
        })

    return {
        "view_type": "TEAM_SUMMARY",
        "manager_position": target.name,
        "team_stats": {
            "wellness": round(team_stats['avg_wellness'] or 0, 1),
            "stress": round(team_stats['avg_stress'] or 0, 1)
        },
        "drill_down": drill_down
    }