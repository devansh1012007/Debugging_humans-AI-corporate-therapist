from rest_framework import permissions

class IsManager(permissions.BasePermission):
    """
    Allows access only to users who are in the 'Team' group.
    """
    def has_permission(self, request, view):
        # 1. Ensure they are logged in
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Check if they are in a group named 'Manager'
        return request.user.groups.filter(name='Manager').exists()