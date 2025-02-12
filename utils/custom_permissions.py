from rest_framework.permissions import BasePermission

class IsTenantUser(BasePermission):
    """
    Permission to check if the user belongs to the current tenant.
    """

    def has_permission(self, request, view):
        if request.user.org.client != request.tenant:
            return False
        return True


class IsSchoolAdmin(BasePermission):
    """
    Permission to check if the user is a school admin.
    """

    def has_permission(self, request, view):
        return request.user.is_school_admin
