from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django_tenants.utils import schema_context
from staff.models import StaffProfile



#to get staff profile
def get_staff_profile(request: HttpRequest):
    try:
        with schema_context(request.tenant.schema_name):
            return StaffProfile.objects.get(user=request.user)
    except StaffProfile.DoesNotExist:
        return None
