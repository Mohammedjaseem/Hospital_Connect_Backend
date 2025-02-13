from django.urls import path
from .views import apply_staff_hostel_gate_pass

urlpatterns = [
    path('apply-hostel-staff-gate-pass/', apply_staff_hostel_gate_pass, name='apply_staff_gate_pass'),
]
