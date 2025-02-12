from django.urls import path
from . import views

urlpatterns = [
    path('staff/', views.StaffProfileView.as_view(), name='add_staff'),  # POST for adding staff
    path('staff/<int:pk>/', views.StaffProfileView.as_view(), name='edit_delete_staff'),  # PUT for editing and DELETE for deleting staff
    path('search/', views.SearchStaffView.as_view(), name='search_staff'),
    path('home/', views.HomeView, name='home'),
    path('get-teaching-staffs/', views.GetTeachingStaffApiView.as_view(), name="get_teaching_staff"),
    # path('download-staff-details-as-excel/', views.DownloadStaffDetailsAsExcelView.as_view(), name="download_staff_details"),
    path('cache/', views.CacheManagementApiView.as_view(), name='cache_management'),
]