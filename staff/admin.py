from django.contrib import admin
from django.utils.html import mark_safe
from .models import StaffProfile

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = (
        "emp_id",
        "name",
        "department",
        "designation",
        "mobile",
        "is_verified",
        "is_active",
        "profile_picture_display",
    )
    list_filter = ("is_verified", "is_active", "department", "designation")
    search_fields = ("name", "emp_id", "mobile", "user__email", "department__name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "profile_picture_display")
    fieldsets = (
        ("Personal Information", {
            "fields": ("user", "emp_id", "name", "gender", "dob", "mobile", "address", "blood_group", "emergency_contact")
        }),
        ("Work Details", {
            "fields": ("department", "designation", "is_verified", "is_active")
        }),
        ("Hostel Details", {
            "fields": ("is_hosteller", "hostel", "room_no")
        }),
        ("Profile Picture", {
            "fields": ("picture", "profile_picture_display")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def profile_picture_display(self, obj):
        return obj.profile_pic()
    
    profile_picture_display.short_description = "Profile Picture"
    profile_picture_display.allow_tags = True
