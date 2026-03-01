from rest_framework import permissions
from .tasks import get_subtree_ids

class IsHierarchicalSuperior(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or not hasattr(request.user, 'org_node'):
            return False

        requester = request.user.org_node

        # Company Isolation
        if requester.company_id != obj.company_id:
            return False

        # Allow if Self
        if requester.id == obj.id:
            return True

        # Allow if Descendant (Manager viewing Subordinate)
        allowed_ids = get_subtree_ids(requester.id)
        return obj.id in allowed_ids
    

from rest_framework import permissions
from django.db import connection

class IsHierarchicalSuperior(permissions.BasePermission):
    """
    Allows access if the Requester is an ANCESTOR of the Target.
    (e.g., CEO (Lvl 1) can view Team Lead (Lvl 5)).
    """
    def has_object_permission(self, request, view, obj):
        # 1. Self Access is always allowed
        if request.user.org_node.id == obj.id:
            return True

        # 2. Hierarchy Access
        # We perform a quick recursive check to see if 'obj' is inside 'user's' tree.
        requester_id = request.user.org_node.id
        
        # Optimized Recursive Query to check lineage
        query = """
        WITH RECURSIVE subordinates AS (
            SELECT id FROM app_orgnode WHERE parent_id = %s
            UNION ALL
            SELECT child.id FROM app_orgnode child
            JOIN subordinates parent ON child.parent_id = parent.id
        )
        SELECT 1 FROM subordinates WHERE id = %s LIMIT 1;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [requester_id, obj.id])
            is_descendant = cursor.fetchone()
        
        return bool(is_descendant)