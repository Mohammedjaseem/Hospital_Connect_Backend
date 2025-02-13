from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .models import StaffProfile
from .serializers import StaffProfileSerializer, TeachingStaffSerializer
from utils.validate_required_fields import validate_required_fields
from rest_framework.pagination import PageNumberPagination
from utils.decorators import verify_tenant_user
from django.http import HttpResponse
# from openpyxl import Workbook
# from openpyxl.utils import get_column_letter
# from ..utils import validate_required_fields
from utils.custom_permissions import IsTenantUser, IsHospitalAdmin

class StaffProfilePagination(PageNumberPagination):
    page_size = 20  # Number of results per page
    page_size_query_param = 'page_size'  # Allow the client to override this via a query parameter
    max_page_size = 100  # Maximum results allowed per page


class StaffProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @verify_tenant_user(is_hospital_admin=True)
    def get(self, request, pk=None):
        try:
            if pk:
                # Retrieve a single staff profile by UUID
                staff = get_object_or_404(StaffProfile, pk=pk)
                serializer = StaffProfileSerializer(staff)
                return Response({"data": serializer.data, "status": True}, status=status.HTTP_200_OK)
            else:
                # Check query parameter for pagination toggle
                use_pagination = request.query_params.get('use_pagination', 'true').lower() == 'true'

                # Retrieve and process query parameters
                search_query = request.query_params.get('search', None)
                gender = request.query_params.get('gender', None)
                department_id = request.query_params.get('department_id', None)
                designation_id = request.query_params.get('designation_id', None)
                is_teaching_staff = request.query_params.get('is_teaching_staff', None)

                # Base queryset
                staff = StaffProfile.objects.all().order_by('-created_at')

                # Apply filters
                if search_query:
                    staff = staff.filter(name__icontains=search_query)
                if gender:
                    staff = staff.filter(gender=gender)
                if department_id:
                    try:
                        department_id = int(department_id)
                        staff = staff.filter(department=department_id)
                    except ValueError:
                        return Response({"error": "Invalid department_id", "status": False}, status=status.HTTP_400_BAD_REQUEST)
                if designation_id:
                    try:
                        designation_id = int(designation_id)
                        staff = staff.filter(designation=designation_id)
                    except ValueError:
                        return Response({"error": "Invalid designation_id", "status": False}, status=status.HTTP_400_BAD_REQUEST)
                if is_teaching_staff is not None:
                    is_teaching_staff = is_teaching_staff.lower() == 'true'
                    staff = staff.filter(is_teaching_staff=is_teaching_staff)

                # Handle pagination
                if use_pagination:
                    paginator = StaffProfilePagination()
                    result_page = paginator.paginate_queryset(staff, request)
                    serializer = StaffProfileSerializer(result_page, many=True)

                    paginated_response = {
                        "count": paginator.page.paginator.count,
                        "next": paginator.get_next_link(),
                        "previous": paginator.get_previous_link(),
                        "page_size": paginator.page_size,
                        "results": serializer.data,
                    }

                    return Response({"data": paginated_response, "status": True}, status=status.HTTP_200_OK)
                else:
                    # Return all results without pagination
                    serializer = StaffProfileSerializer(staff, many=True)
                    return Response({"data": serializer.data, "status": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Error retrieving staff profile(s): {str(e)}", "status": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @verify_tenant_user(is_hospital_admin=False)
    def post(self, request):
        try:
            data = request.data.copy()
            validate_required_fields(data,['name', 'dob', 'mobile', 'department', 'designation', 'picture'])

            data['user'] = request.user.id
            serializer = StaffProfileSerializer(data=data)
            try:
                serializer.is_valid(raise_exception=True)
                staff = serializer.save(is_verified=True)
            except serializers.ValidationError as e:
                if 'mobile' in e.detail:
                    return Response({
                        "error": "Phone number already exists, please provide another number",
                        "status": False
                    }, status=status.HTTP_400_BAD_REQUEST)
                raise e

            return Response({
                "message": "Staff added successfully",
                "staff_profile": StaffProfileSerializer(staff).data,
                "status": True
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Error creating staff profile: {str(e)}", "status": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @verify_tenant_user(is_hospital_admin=False)
    def patch(self, request,pk):
        try:
            staff = get_object_or_404(StaffProfile, pk=pk)
            # data = request.data.copy()

            serializer = StaffProfileSerializer(staff, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({
                "message": "Staff updated successfully",
                "status": True,
                'staff_profile': serializer.data
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error updating staff profile: {str(e)}", "status": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @verify_tenant_user(is_hospital_admin=False)
    def delete(self, request, uuid):
        try:
            staff = get_object_or_404(StaffProfile, uuid=uuid)
            staff.delete()
            return Response({
                "message": "Staff deleted successfully",
                "status": True
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error deleting staff profile: {str(e)}", "status": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SearchStaffView(APIView):
    permission_classes = [IsAuthenticated]
    @verify_tenant_user(is_hospital_admin=True)
    def get(self, request):
        try:
            query = request.query_params.get('query')
            staff = StaffProfile.objects.filter(name__icontains=query)
            serializer = StaffProfileSerializer(staff, many=True)
            return Response({"data": serializer.data, "status": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error searching staff: {str(e)}", "status": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetTeachingStaffApiView(APIView):
    permission_classes = [IsAuthenticated,IsTenantUser]

    # @verify_tenant_user(is_hospital_admin=False)
    def get(self, request):
        try:
            teaching_staff = StaffProfile.objects.filter(is_teaching_staff=True,is_active=True)
            serializer = TeachingStaffSerializer(teaching_staff, many=True)
            return Response({"data": serializer.data, "status": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error retrieving teaching staff: {str(e)}", "status": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# class DownloadStaffDetailsAsExcelView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         # Create a workbook and sheet
#         wb = Workbook()
#         ws = wb.active
#         ws.title = "Staff Details"

#         # Define the header row
#         headers = [
#             "Sl. No", "Name", "Mobile", "Department Name", "Designation Name",
#             "Is Teaching Staff", "Date of Birth", "Gender", "Blood Group",
#             "Emergency Contact Number", "Address"
#         ]
#         ws.append(headers)

#         # Fetch all staff details
#         staff_profiles = StaffProfile.objects.select_related('department', 'designation').order_by('name')

#         # Add data rows
#         for index, staff in enumerate(staff_profiles, start=1):
#             ws.append([
#                 index,
#                 staff.name,
#                 staff.mobile,
#                 staff.department.name if staff.department else "",
#                 staff.designation.name if staff.designation else "",
#                 "Yes" if staff.is_teaching_staff else "No",
#                 staff.dob.strftime('%d/%m/%Y') if staff.dob else "",
#                 staff.gender,
#                 staff.blood_group,
#                 staff.emergency_contact,
#                 staff.address
#             ])

#         # Adjust column widths
#         for col_num, column_cells in enumerate(ws.columns, start=1):
#             max_length = 0
#             for cell in column_cells:
#                 try:
#                     max_length = max(max_length, len(str(cell.value)))
#                 except TypeError:
#                     pass
#             adjusted_width = max_length + 2
#             ws.column_dimensions[get_column_letter(col_num)].width = adjusted_width

#         # Create a response with the Excel file
#         response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#         response['Content-Disposition'] = 'attachment; filename="staff_details.xlsx"'

#         # Save the workbook to the response
#         wb.save(response)
#         return response



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def HomeView(request):
    return Response({"message": "Welcome to Connect API", "user": str(request.user), "tenant": str(getattr(request, 'tenant', 'No Tenant Found')), "status": True}, status=status.HTTP_200_OK)







from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_redis import get_redis_connection

class CacheManagementApiView(APIView):
    def get(self, request):
        # List all cached keys for tenant objects
        redis_conn = get_redis_connection(alias='default')
        keys = redis_conn.keys(":1:tenant_*")  # Adjust prefix if necessary
        return Response({'keys': [key.decode() for key in keys]}, status=status.HTTP_200_OK)

    def delete(self, request):
        # Delete a specific key and its data
        key = request.data.get("key")  # Full key, including prefix (e.g., ":1:tenant_123_departments")
        if key:
            redis_conn = get_redis_connection(alias='default')
            result = redis_conn.delete(key)  # Delete the entire key from Redis
            if result == 1:  # Redis returns 1 if the key existed and was deleted
                return Response({'message': f'Key {key} deleted successfully.'}, status=status.HTTP_200_OK)
            return Response({'error': f'Key {key} not found or already deleted.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Key is required for deletion.'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        # Flush all cached keys for tenant objects
        action = request.data.get("action")
        if action == "flush":
            redis_conn = get_redis_connection(alias='default')
            keys = redis_conn.keys(":1:tenant_*")  # Adjust prefix if necessary
            for key in keys:
                redis_conn.delete(key)
            return Response({'message': 'All cached keys for tenant objects flushed.'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid action specified.'}, status=status.HTTP_400_BAD_REQUEST)

