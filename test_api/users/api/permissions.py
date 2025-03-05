from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsOwnerOrManager(BasePermission):
    """
    Permission class that allows access to:
    - Superusers (for all operations)
    - Store owners (for all operations)
    - Store managers (for viewing and editing only, not deletion)
    """

    def has_permission(self, request, view):
        # Authentication check is handled by IsAuthenticated
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Superusers have full access
        if user.is_superuser:
            return True

        # Store owners have full access to their stores
        if obj.owner == user:
            return True

        # Store managers can view and edit but not delete
        if request.method != "DELETE" and user in obj.manager_ids.all():
            return True

        return False


class IsOwnerOnly(BasePermission):
    """
    Permission class that allows access only to:
    - Superusers (for all operations)
    - Store owners (for all operations)
    """

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_superuser or obj.owner == user
