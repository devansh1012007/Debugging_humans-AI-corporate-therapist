# app_1/permissions.py
from rest_framework import permissions
from django.db import connection
from .models import OrgNode
class IsHierarchicalSuperior(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow Self
        if request.user.org_node.id == obj.id:
            return True

        # Allow Downline (Recursive check)
        requester_id = request.user.org_node.id
        query = """
            WITH RECURSIVE subordinates AS (
                SELECT id FROM app_1_orgnode WHERE parent_id = %s
                UNION ALL
                SELECT child.id FROM app_1_orgnode child
                JOIN subordinates parent ON child.parent_id = parent.id
            )
            SELECT 1 FROM subordinates WHERE id = %s LIMIT 1;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [requester_id, obj.id])
            return bool(cursor.fetchone())
        
    '''
 

    def has_object_permission(self, request, view, obj):
        requester = request.user.org_node # Assuming the user has a link to OrgNode
        
        if not requester:
            return False
    
        # The logic: Is the 'obj' (target) a descendant of 'requester'?
        # We can check this by looking at the target's ancestry.
        
        def is_descendant(parent, target):
            current = target.parent
            while current is not None:
                if current == parent:
                    return True
                current = current.parent
            return False
    
        return is_descendant(requester, obj)
    
    '''