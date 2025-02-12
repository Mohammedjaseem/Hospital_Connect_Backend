from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def verify_tenant_user(is_hospital_admin=False):
    """
    Decorator to verify the user belongs to the current tenant and optionally if they are an admin.
    
    :param is_admin: Whether the user must be a tenant admin to access the view.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            # Check if the user belongs to the current tenant
            if request.user.org.client != request.tenant:
                return Response(
                    {'error': 'You do not belong to this school', 'status': False},
                    status=status.HTTP_403_FORBIDDEN
                )
            # Check if admin access is required
            if not request.user.is_school_admin:
                return Response(
                    {'error': 'You do not have permission to do this', 'status': False},
                    status=status.HTTP_403_FORBIDDEN
                )
            return view_func(self, request, *args, **kwargs)
        return _wrapped_view
    return decorator