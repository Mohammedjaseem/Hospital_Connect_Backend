from rest_framework import serializers
from .models import HostelStaffGatePass

class HostelStaffGatePassSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.name", read_only=True)
    mentor_name = serializers.CharField(source="mentor.name", read_only=True)

    class Meta:
        model = HostelStaffGatePass
        fields = [
            "id",
            "staff",
            "staff_name",
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
