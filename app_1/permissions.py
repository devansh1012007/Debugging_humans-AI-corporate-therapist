from rest_framework import permissions
from django.db import connection

class IsHierarchicalSuperior(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow Self
        if request.user.org_node.id == obj.id:
            return True

        # Allow Downline (Recursive check)
        requester_id = request.user.org_node.id
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
            return bool(cursor.fetchone())