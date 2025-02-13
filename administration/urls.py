from django.urls import path
from . import views


urlpatterns = [
    # Departments endpoints
    path('departments/', views.DepartmentApiView.as_view(), name='departments'),
    path('departments/<int:pk>/', views.DepartmentApiView.as_view(), name='department_detail'),

    # Staff Designations endpoints
    path('designations/', views.DesignationApiView.as_view(), name='designations'),
    path('designations/<int:pk>/', views.DesignationApiView.as_view(), name='designation_detail'),
    path('designations/departments/<int:department_id>/', views.DesignationApiView.as_view(), name='designation_by_department'),

    # Department Incharge and HOD endpoints
    # path('department-incharge-hod/', views.DepartmentInchargeAndHodApiView.as_view(), name='department_incharge_hod'),
    # path('department-incharge-hod/<int:pk>/', views.DepartmentInchargeAndHodApiView.as_view(), name='department_incharge_hod_detail'),

    # Verify Staff endpoint
    path('verify-staff/', views.VerifyStaffApiView.as_view(), name='verify_staff'),
    path('verify-staff/<int:pk>/', views.VerifyStaffApiView.as_view(), name='verify_staff_detail'),

    # # Classrooms endpoints
    # path('classrooms/', views.ClassRoomListCreateAPIView.as_view(), name='classroom-list-create'),
    # path('classrooms/<int:pk>/', views.ClassRoomDetailAPIView.as_view(), name='classroom-detail'),

    # Academic Years endpoints
    # path('academic-years/', views.AcademicYearApiView.as_view(), name='academic-year-api'),
    # path('academic-years/<int:pk>/', views.AcademicYearApiView.as_view(), name='academic-year-detail'),

    # Sections endpoints
    # path('sections/', views.SectionApiView.as_view(), name='section-api'),
    # path('sections/<int:pk>/', views.SectionApiView.as_view(), name='section-detail'),

    # Divisions endpoints
    # path('divisions/', views.DivisionApiView.as_view(), name='division-api'),
    # path('divisions/<int:pk>/', views.DivisionApiView.as_view(), name='division-detail'),

    # Dashboard
    path('dashboard/', views.AdminDashboardAPIView.as_view(), name='dashboard'),
    
    

]
