from django.urls import path
from . import views

urlpatterns = [
    path('apply-hostel-staff-gate-pass/', views.apply_staff_hostel_gate_pass, name='apply_staff_gate_pass'),
    path('get_my_pass_list/', views.get_my_pass_list, name="get_my_pass_list"),
    path('mentor_approval_pendings/', views.mentor_approval_pendings, name="mentor_approval_pendings"),
    path('mentor_rejected_gate_passes/', views.mentor_rejected_gate_passes, name="mentor_rejected_gate_passes"),
    path('mentor_approved_gate_passes/', views.mentor_approved_gate_passes, name="mentor_approved_gate_passes"),
    path('pass_counts_for_mentor/', views.pass_counts_for_mentor, name="pass_counts_for_mentor"),
    path('search_staff_pass/', views.search_staff_pass, name="serach_staff_pass"),
    path('Hostel_gatepass/<str:token>/<str:decision>/', views.HostelStaffGatePassApprove, name="Hostel_gatepass_approve"),
    path('check_in_check_out_marker/', views.check_in_check_out_marker, name="check_in_check_out_marker"),
    path('gate_pass_report/', views.gate_pass_report, name="gate_pass_report"),
    path("single_pass_data/", views.single_pass_data, name="single_pass_data"),

]