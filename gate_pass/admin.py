from django.contrib import admin
from django.utils.html import format_html
from .models import HostelStaffGatePass

@admin.register(HostelStaffGatePass)
class HostelStaffGatePassAdmin(admin.ModelAdmin):
    list_display = (
        "gatepass_no",
        "staff",
        "mentor",
        "requested_check_out",
        "proposed_check_in",
        "status_update_display",
        "checked_out",
        "checked_in",
    )
    list_filter = ("request_status", "checked_out", "checked_in", "informed_warden")
    search_fields = ("staff__name", "mentor__name", "gatepass_no", "request_status")
    ordering = ("-requested_on",)
    readonly_fields = (
        "requested_on", "updated_on", "status_update_display", "requested_check_out",
        "proposed_check_in", "date_time_exit", "date_time_entry", "profile_pic"
    )
    fieldsets = (
        ("Staff Information", {
            "fields": ("staff", "mentor", "profile_pic")
        }),
        ("Gate Pass Details", {
            "fields": ("gatepass_no", "pass_token", "purpose", "request_status", "status_update_display")
        }),
        ("Request Timing", {
            "fields": ("requested_check_out", "proposed_check_in")
        }),
        ("Approval Details", {
            "fields": ("mentor_updated", "updated_on", "remarks", "informed_warden")
        }),
        ("Check In/Out Details", {
            "fields": ("checked_out", "date_time_exit", "checked_in", "date_time_entry", "duration")
        }),
        ("QR Code", {
            "fields": ("qr_code_url",)
        }),
    )

    def status_update_display(self, obj):
        return obj.status_update
    
    status_update_display.short_description = "Status"
    status_update_display.allow_tags = True