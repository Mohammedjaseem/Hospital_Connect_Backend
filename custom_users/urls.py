from django.urls import path
from . import views
urlpatterns = [
    path('register/',views.register_user,name='user_register'),
    path('verify-otp/',views.verify_otp,name='verify_otp'),
    path('resend-otp/',views.resend_otp,name='resend_otp'),
    path('login/',views.login,name='login_user'),
    # path('forgot-password/',views.forgot_password,name='forgot_password'),
    # path('reset-password/',views.reset_password,name='reset_password_from_forgot_password'),
    # path('logout/',views.logout,name='logout_user'),
    path('refresh-token/', views.refresh_token, name='refresh_token'),
    path('homes/',views.home,name='homes'),
    # path('create-user-from-school/',views.create_user_from_school,name='create_user_from_school'),
    # path('user-retrival/', views.user_retrival, name='user_retrival')
]