from rest_framework import serializers
from .models import Departments, Designations, DepartmentInchargeAndHod

class DepartmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Departments
        fields = [
            'id','name', 'short_code',
        ]

class DesignationSerializer(serializers.ModelSerializer):
    department_id = serializers.IntegerField(source='department.id', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Designations
        fields = [
            'id', 'name', 'description',
            'department_id', 'department_name'
        ]


# class ClassRoomSerializer(serializers.ModelSerializer):
#     class_teacher_name = serializers.SerializerMethodField()

#     class Meta:
#         model = ClassRoom
#         fields = ['uuid', 'id','academic_year', 'section', 'division', 'department','class_teacher', 'classs', 'class_teacher_name', 'description']
    
#     def get_class_teacher_name(self, obj):
#         return obj.class_teacher.name if obj.class_teacher else None


# class DepartmentInchargeAndHodSerializer(serializers.ModelSerializer):
#     department_id = serializers.IntegerField(source='department.id', read_only=True)
#     department_name = serializers.CharField(source='department.name', read_only=True)
#     hod_name = serializers.CharField(source='hod.name', read_only=True, default=None)
#     incharge_name = serializers.CharField(source='incharge.name', read_only=True, default=None)

#     class Meta:
#         model = DepartmentInchargeAndHod
#         fields = [
#             'id', 'department_id', 'department_name', 
#             'hod', 'hod_name', 'incharge', 'incharge_name', 
#             'description'
#         ]

# class AcademicYearCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AcademicYear
#         fields = ['start_year', 'end_year','description']  # Exclude `name` as it is auto-generated

#     def validate(self, data):
#         start_year = data.get('start_year')
#         end_year = data.get('end_year')
#         # start_date = data.get('start_date')
#         # end_date = data.get('end_date')

#         # Validate that end_year is exactly one year after start_year
#         if end_year != start_year + 1:
#             raise serializers.ValidationError("End year must be exactly one year after the start year.")

#         # Validate that start_date is within start_year
#         # if start_date.year != start_year:
#         #     raise serializers.ValidationError("Start date must be within the start year.")

#         # Validate that end_date is within end_year
#         # if end_date.year != end_year:
#         #     raise serializers.ValidationError("End date must be within the end year.")

#         # # Validate that start_date is before end_date
#         # if start_date >= end_date:
#         #     raise serializers.ValidationError("Start date must be earlier than the end date.")

#         return data

# class AcademicYearRetrieveSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AcademicYear
#         fields = ['id', 'name', 'start_year', 'end_year','description']


# class SectionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Section
#         fields = '__all__'

# class DivisionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Division
#         fields = '__all__'