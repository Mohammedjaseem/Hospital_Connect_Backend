from django.urls import path
from .views import create_hostel, list_hostels, get_hostel, update_hostel, delete_hostel

urlpatterns = [
    path('api/hostels/create/', create_hostel, name='create-hostel'),
    path('api/hostels/', list_hostels, name='list-hostels'),
    path('api/hostels/<int:hostel_id>/', get_hostel, name='get-hostel'),
    path('api/hostels/<int:hostel_id>/update/', update_hostel, name='update-hostel'),
    path('api/hostels/<int:hostel_id>/delete/', delete_hostel, name='delete-hostel'),
]
