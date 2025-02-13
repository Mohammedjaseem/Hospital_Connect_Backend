from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.urls import re_path as url
from django.views.static import serve



urlpatterns = [
    path('api/staff/', include('staff.urls')),
    path('api/administration/', include('administration.urls')),
    path('hostel/', include('hostel.urls')),
    
    # path('api/students/', include('students.urls')),
    # path('api/attendance/', include('attendance.urls')),
    # path('api/fees/', include('fees.urls')),
    # path('api/news/', include('news.urls'))


    # url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    # url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)