from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Departments, Designations
from staff.models import StaffProfile
from .serializers import (
    DepartmentSerializer,
    DesignationSerializer,
)
# from staff.serializers import StaffProfileSerializer
from utils.validate_required_fields import validate_required_fields
from rest_framework.permissions import IsAuthenticated
from utils.decorators import verify_tenant_user
from django.utils.timezone import now
# from students.models import StudentProfile
from utils.custom_permissions import IsTenantUser, IsHospitalAdmin


class DepartmentApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        departments = Departments.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        departments_data = serializer.data
        return Response({'data': departments_data, 'status': True}, status=status.HTTP_200_OK)

    @verify_tenant_user(is_hospital_admin=True)
    def post(self, request):
        try:
            required_fields = ['name']
            validate_response = validate_required_fields(request.data, required_fields)
            if validate_response:
                return validate_response

            serializer = DepartmentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Department added successfully.', 'data': serializer.data, 'status': True}, status=status.HTTP_201_CREATED)

            error_messages = " | ".join([f"{field.replace('_', ' ').capitalize()}: {', '.join(errors)}" for field, errors in serializer.errors.items()])
            return Response({'error': f"Validation failed: {error_messages}", 'status': False}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Error creating department: {str(e)}", 'status': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @verify_tenant_user(is_hospital_admin=True)
    def patch(self, request, pk):
        try:
            department = get_object_or_404(Departments, pk=pk)
            serializer = DepartmentSerializer(department, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Department updated successfully.', 'data': serializer.data, 'status': True}, status=status.HTTP_200_OK)

            error_messages = " | ".join([f"{field.replace('_', ' ').capitalize()}: {', '.join(errors)}" for field, errors in serializer.errors.items()])
            return Response({'error': f"Validation failed: {error_messages}", 'status': False}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Error updating department: {str(e)}", 'status': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @verify_tenant_user(is_hospital_admin=True)
    def delete(self, request, pk):
        try:
            department = get_object_or_404(Departments, pk=pk)
            department.delete()
            return Response({'message': 'Department deleted successfully.', 'status': True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f"Error deleting department: {str(e)}", 'status': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DesignationApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, department_id=None):
        try:
            if department_id:
                department = get_object_or_404(Departments, pk=department_id)
                designations = Designations.objects.filter(department=department)
                data = DesignationSerializer(designations, many=True).data
                for designation in data:
                    designation["department_name"] = department.name
            else:
                designations = Designations.objects.select_related('department').all()
                data = [
                    {
                        "id": designation.id,
                        "name": designation.name,
                        "description": designation.description,
                        "department_id": designation.department.id if designation.department else None,
                        'department_name': designation.department.name if designation.department else None
                    }
                    for designation in designations
                ]
            return Response({'data': data, 'status': True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f"Error retrieving designations: {str(e)}", 'status': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @verify_tenant_user(is_hospital_admin=True)
    def post(self, request):
        try:
            required_fields = ['department', 'name']
            validate_response = validate_required_fields(request.data, required_fields)
            if validate_response:
                return validate_response

            department_id = request.data.get('department')
            department = get_object_or_404(Departments, pk=department_id)

            serializer = DesignationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(department=department)
                designation_data = serializer.data
                designation_data['department_name'] = department.name
                return Response(
                    {'message': 'Designation added successfully.', 'data': designation_data, 'status': True},
                    status=status.HTTP_201_CREATED
                )

            error_messages = " | ".join(
                [f"{field.replace('_', ' ').capitalize()}: {', '.join(errors)}" for field, errors in serializer.errors.items()]
            )
            return Response({'error': f"Validation failed: {error_messages}", 'status': False}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Error creating designation: {str(e)}", 'status': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @verify_tenant_user(is_hospital_admin=True)
    def patch(self, request, pk):
        try:
            designation = get_object_or_404(Designations, pk=pk)
            serializer = DesignationSerializer(designation, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Designation updated successfully.', 'data': serializer.data, 'status': True}, status=status.HTTP_200_OK)

            error_messages = " | ".join([f"{field.replace('_', ' ').capitalize()}: {', '.join(errors)}" for field, errors in serializer.errors.items()])
            return Response({'error': f"Validation failed: {error_messages}", 'status': False}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Error updating designation: {str(e)}", 'status': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @verify_tenant_user(is_hospital_admin=True)
    def delete(self, request, pk):
        try:
            designation = get_object_or_404(Designations, pk=pk)
            designation.delete()
            return Response({'message': 'Designation  deleted successfully.', 'status': True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f"Error deleting designation: {str(e)}", 'status': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class VerifyStaffApiView(APIView):
    permission_classes = [IsAuthenticated]

    @verify_tenant_user(is_hospital_admin=True)
    def get(self, request):
        try:
            staff = StaffProfile.objects.filter(is_verified=False)
            return Response({'message': StaffProfileSerializer(staff, many=True).data, 'status': True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f"Error retrieving verified staff: {str(e)}", 'status': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @verify_tenant_user(is_hospital_admin=True)
    def post(self, request, pk):
        try:
            staff = get_object_or_404(StaffProfile, pk=pk)
            staff.is_verified = True
            staff.save()
            return Response({'message': 'Staff verified successfully.', 'status': True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f"Error verifying staff: {str(e)}", 'status': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @verify_tenant_user(is_hospital_admin=True)
    def delete(self, request, pk):
        try:
            staff = get_object_or_404(StaffProfile, pk=pk)
            staff.is_verified = False
            staff.save()
            return Response({'message': 'Staff unverified successfully.', 'status': True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f"Error unverifying staff: {str(e)}", 'status': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

import logging

logger = logging.getLogger(__name__)

class AdminDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsTenantUser, IsHospitalAdmin]

    def get(self, request):
        for header, value in request.headers.items():
            logger.info(f"{header}: {value}")
        try:
            # Total staff count
            total_staff = StaffProfile.objects.count()
    

            # Total departments
            total_departments = Departments.objects.count()

            # Total Students

            # Response Data
            dashboard_data = {
                "total_staff": total_staff,
              
                "total_departments": total_departments,
                
            }

            return Response(
                {"data": dashboard_data, "status": True},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Error retrieving dashboard data: {str(e)}", "status": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
