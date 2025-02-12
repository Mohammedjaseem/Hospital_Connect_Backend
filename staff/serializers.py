from rest_framework import serializers
from .models import StaffProfile
from datetime import date

# class StaffProfileSerializer(serializers.ModelSerializer):
#     department_name = serializers.CharField(source='department.name', read_only=True)
#     designation_name = serializers.CharField(source='designation.name', read_only=True)

#     class Meta:
#         model = StaffProfile
#         fields = [
#             'uuid', 'is_active', 'user', 'name', 'gender', 'dob', 'mobile',
#             'department', 'department_name', 'designation', 'designation_name',
#             'is_verified', 'is_teaching_staff', 'address','picture',
#             'blood_group','emergency_contact'
#         ]
#         read_only_fields = ('uuid',)
#     def validate(self, data):
#         if data.get('dob') and data['dob'] > date.today():
#             raise serializers.ValidationError({"dob": "Date of birth cannot be in the future."})
#         return data

class StaffProfileSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    designation_name = serializers.SerializerMethodField()

    class Meta:
        model = StaffProfile
        fields = [
            'id', 'is_active', 'user', 'name', 'gender', 'dob', 'mobile',
            'department', 'designation', 'department_name','designation_name','is_verified', 'is_teaching_staff', 'address', 'picture',
            'blood_group', 'emergency_contact'
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