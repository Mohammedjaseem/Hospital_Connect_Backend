from django.urls import path
from . import views

urlpatterns = [
    path('apply-hostel-staff-gate-pass/', views.apply_staff_hostel_gate_pass, name='apply_staff_gate_pass'),
    path('get_my_pass_list', views.get_my_pass_list, name="get_my_pass_list"),
    path('Hostel_gatepass/<str: token>/<str: decision>/', views.HostelStaffGatePassApprove, name="get_my_pass_list"),
]
