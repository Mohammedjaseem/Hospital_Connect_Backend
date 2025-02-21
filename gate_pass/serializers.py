from rest_framework import serializers
from .models import HostelStaffGatePass

class HostelStaffGatePassSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.name", read_only=True)
    mentor_name = serializers.CharField(source="mentor.name", read_only=True)
    hostel_name = serializers.CharField(source="staff.hostel.name", read_only=True)
    staff_department = serializers.CharField(source="staff.department.name", read_only=True)
    staff_designation = serializers.CharField(source="staff.designation.name", read_only=True)
    staff_picture = serializers.SerializerMethodField()

    class Meta:
        model = HostelStaffGatePass
        fields = [
            "id",
            "staff",
            "staff_name",
            "staff_department",
            "staff_designation",
            "staff_picture",
            "requested_on",
            "purpose",
            "requesting_date",
            "requesting_time",
            "return_date",
            "return_time",
            "pass_token",
            "request_status",
            "mentor",
            "mentor_name",
            "mentor_updated",
            "updated_on",
            "qr_code_url",
            "remarks",
            "informed_warden",
            "gatepass_no",
            "checked_out",
            "date_time_exit",
            "checked_in",
            "date_time_entry",
            "duration",
        ]
        
    def get_staff_picture(self, obj):
        return obj.staff.picture.url if obj.staff.picture else None
