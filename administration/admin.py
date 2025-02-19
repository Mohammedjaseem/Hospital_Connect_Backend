from django.contrib import admin
from administration.models import Departments, Designations

@admin.register(Departments)
class DepartmentsAdmin(admin.ModelAdmin):
    list_display = ("short_code", "name", "phone_number", "email", "hod", "incharge", "created_at", "updated_at")
    search_fields = ("name", "short_code", "phone_number", "email")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)
    
@admin.register(Designations)
class DesignationsAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "created_at", "updated_at")
    search_fields = ("name", "department__name")
    list_filter = ("created_at", "updated_at", "department")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)