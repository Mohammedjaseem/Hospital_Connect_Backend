from django.urls import path
from . import views

urlpatterns = [
    path('apply-hostel-staff-gate-pass/', views.apply_staff_hostel_gate_pass, name='apply_staff_gate_pass'),
    path('get_my_pass_list/', views.get_my_pass_list, name="get_my_pass_list"),
    path('mentor_approval_pendings/', views.mentor_approval_pendings, name="mentor_approval_pendings"),
    path('Hostel_gatepass/<str:token>/<str:decision>/', views.HostelStaffGatePassApprove, name="Hostel_gatepass_approve"),
    path('check_in_check_out_marker/', views.check_in_check_out_marker, name="check_in_check_out_marker"),
]
