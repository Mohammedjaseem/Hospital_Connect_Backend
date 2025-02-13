from rest_framework import serializers
from datetime import date
from .models import StaffProfile

class StaffProfileSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    designation_name = serializers.SerializerMethodField()
    # blood_group_display = serializers.CharField(source="get_blood_group_display", read_only=True)
    # gender_display = serializers.CharField(source="get_gender_display", read_only=True)

    class Meta:
        model = StaffProfile
        fields = [
            'id', 'is_active', 'user', 'name', 'gender','dob', 'mobile', 'emp_id', 'hostel', 'room_no',
            'department', 'designation', 'department_name', 'designation_name', 'is_verified',
            'is_hosteller', 'address', 'picture', 'blood_group',  'emergency_contact'
        ]
        read_only_fields = ('uuid',)

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_designation_name(self, obj):
        return obj.designation.name if obj.designation else None

    def validate(self, data):
        if data.get('dob') and data['dob'] > date.today():
            raise serializers.ValidationError({"dob": "Date of birth cannot be in the future."})
        return data
class TeachingStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = [
            'id','name','picture'
        ]