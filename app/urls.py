from django.urls import path,include
from . import views
from django.contrib import admin


urlpatterns = [
 path('admin/', admin.site.urls), 
 path('', views.index, name='index'),
 path('api/custom_users/', include('custom_users.urls')), 
]