from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserType, OTP

class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)
    readonly_fields = ('uuid', 'created_at', 'updated_at')

admin.site.register(UserType, UserTypeAdmin)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'email', 'name', 'org', 'user_type', 'is_verified', 'is_active', 'is_staff', 'is_hospital_admin')
    list_filter = ('is_active', 'is_staff', 'is_verified', 'user_type', 'org')
    search_fields = ('email', 'name', 'org__name')
    ordering = ('email',)
    readonly_fields = ('uuid',)

    fieldsets = (
        ('Personal Info', {'fields': ('uuid', 'email', 'name', 'password')}),
        ('Organization Info', {'fields': ('org', 'user_type')}),
        ('Permissions', {'fields': ('is_verified', 'is_active', 'is_staff', 'is_hospital_admin', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        ('Create User', {
            'classes': ('wide',),
            'fields': ('email', 'name', 'org', 'user_type', 'password1', 'password2', 'is_staff', 'is_hospital_admin', 'is_active', 'is_verified')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'expires_at', 'created_at')
    list_filter = ('is_verified', 'expires_at', 'created_at')
    search_fields = ('user__email',)
    ordering = ('-created_at',)
    readonly_fields = ('user', 'otp_hash', 'expires_at', 'is_verified', 'created_at', 'updated_at')

admin.site.register(OTP, OTPAdmin)
