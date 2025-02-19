from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
import uuid
from django.db.models import Count, Sum, Avg, Min, Max, DurationField, ExpressionWrapper, F
from django.db.models.functions import ExtractWeekDay
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from .models import HostelStaffGatePass
from .serializers import HostelStaffGatePassSerializer
from utils.handle_exception import handle_exception
from utils.whatsapp_sender import send_whatsapp_message
from utils.fetch_staff import get_staff_profile
from django.utils.timezone import now
import os
import boto3
import pyqrcode
from botocore.exceptions import NoCredentialsError, ClientError
from utils.paginator import paginate_and_serialize
import pyqrcode
from PIL import Image
import io
from collections import Counter
import requests
# from utils.send_email import send_email
from .tasks import send_email
from django.template.loader import render_to_string
from django.db import connection
            

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_staff_hostel_gate_pass(request):
    try:
        staff_profile = get_staff_profile(request)

        if not staff_profile.is_hosteller:
            return Response({"message": "You are not a hostel staff", "status": False}, status=status.HTTP_400_BAD_REQUEST)

        five_hours_ago = timezone.now() - timedelta(hours=5)
        latest_gate_pass = HostelStaffGatePass.objects.filter(
            staff=staff_profile, requested_on__gte=five_hours_ago
        ).only('requested_on').first()

        if latest_gate_pass:
            time_left = latest_gate_pass.requested_on + timedelta(hours=5) - timezone.now()
            return Response(
                {"message": f"You have already requested a gate pass. Try again after {int(time_left.total_seconds() // 3600):02}:{int((time_left.total_seconds() % 3600) // 60):02}.", "status": False},
                status=status.HTTP_400_BAD_REQUEST
            )

        required_fields = ['purpose', 'requesting_date', 'requesting_time', 'return_date', 'return_time']
        missing_fields = [field for field in required_fields if not request.data.get(field)]
        if missing_fields:
            return Response({"message": f"Missing required fields: {', '.join(missing_fields)}", "status": False}, status=status.HTTP_400_BAD_REQUEST)

        purpose = request.data['purpose']
        requesting_date = request.data['requesting_date']
        requesting_time = datetime.strptime(request.data['requesting_time'], '%I:%M %p').strftime('%H:%M:%S')
        return_date = request.data['return_date']
        return_time = datetime.strptime(request.data['return_time'], '%I:%M %p').strftime('%H:%M:%S')
        
        mentor = staff_profile.hostel.incharge
        if not mentor:
            return Response({"message": "Hostel Incharge not found!", "status": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        mentor_number = mentor.mobile.strip().replace(" ", "").lstrip('+')
        
        gate_pass = HostelStaffGatePass.objects.create(
            staff=staff_profile, mentor=mentor, purpose=purpose,
            requesting_date=requesting_date, requesting_time=requesting_time,
            return_date=return_date, return_time=return_time,
            pass_token=f"GatePass-HostelStaff-{uuid.uuid4()}"
        )
        
        total_seconds = (
            datetime.strptime(f"{return_date} {return_time}", "%Y-%m-%d %H:%M:%S") - 
            datetime.strptime(f"{requesting_date} {requesting_time}", "%Y-%m-%d %H:%M:%S")
        ).total_seconds()
        
        days, remainder = divmod(total_seconds, 86400)
        hours, minutes = divmod(remainder, 3600)
        minutes //= 60
        total_out_duration = f"{int(days)} day{'s' if days > 1 else ''} {int(hours)} hr{'s' if hours != 1 else ''} {int(minutes)} min{'s' if minutes != 1 else ''}" if days else f"{int(hours)} hr{'s' if hours != 1 else ''} {int(minutes)} min{'s' if minutes != 1 else ''}"
        
        check_out_time = datetime.strptime(requesting_time, "%H:%M:%S").strftime("%I:%M %p")
        check_in_time = datetime.strptime(return_time, "%H:%M:%S").strftime("%I:%M %p")
        
        whatsapp_data = {
            "messaging_product": "whatsapp", "to": mentor_number, "type": "template",
            "template": {
                "name": "staff_hostel_pass_request", "language": {"code": "en"}, "components": [
                    {"type": "header", "parameters": [{"type": "text", "text": "Mims"}]},
                    {"type": "body", "parameters": [
                        {"type": "text", "text": staff_profile.name},
                        {"type": "text", "text": staff_profile.department.name},
                        {"type": "text", "text": staff_profile.designation.name},
                        {"type": "text", "text": staff_profile.emp_id},
                        {"type": "text", "text": requesting_date},
                        {"type": "text", "text": check_out_time},
                        {"type": "text", "text": return_date},
                        {"type": "text", "text": check_in_time},
                        {"type": "text", "text": total_out_duration},
                        {"type": "text", "text": purpose},
                    ]},
                    {"type": "button", "index": "0", "sub_type": "url", "parameters": [{"type": "text", "text": str(gate_pass.pass_token)}]},
                    {"type": "button", "index": "1", "sub_type": "url", "parameters": [{"type": "text", "text": str(gate_pass.pass_token)}]},
                ]
            }
        }
        
        notification_status = send_whatsapp_message(request, passing_data=whatsapp_data, type="Gatepass request", sent_to=mentor_number)
        
        org_banner_url = request.user.org.email_banner.url
        subject = f"{staff_profile.name} Has requested for Gate Pass | ID: #{gate_pass.id}"
        message = render_to_string('hostel_pass/MailToMentor.html', {
            'staff_name': staff_profile.name,
            'staff_photo': request.build_absolute_uri(staff_profile.picture.url),
            'department': staff_profile.department.name,
            'designation': staff_profile.designation.name,
            'hostel': staff_profile.hostel.name,
            'staff_req_date': requesting_date,
            'staff_req_time': check_out_time,
            'retrun_date': return_date,
            'retrun_time': check_in_time,
            'total_out_duration': total_out_duration,
            'purpose': purpose,
            'org_banner_url': org_banner_url,
            'pass_token': gate_pass.pass_token,
        })
        
        mailed_to_mentor = send_email.delay(subject, message, mentor.user.email)
        
        if notification_status:
            return Response({
                "message": "Gate pass request sent successfully", "status": True,
                "notification_status": notification_status, "wa_number": mentor_number
            }, status=status.HTTP_200_OK)
        
        gate_pass.delete()
        return Response({"message": "Gate pass request failed to send notification", "status": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return handle_exception(e)



@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Secure API access
def gate_pass_report(request):
    try:
        # Get all approved gate passes
        gatepasses = HostelStaffGatePass.objects.filter(request_status="Approved")

        # Most frequently going staff
        most_going_staff = gatepasses.values('staff__name').annotate(
            total_passes=Count('id')
        ).order_by('-total_passes')[:10]  # Top 10 staff

        # Staff with the longest total duration
        most_duration_staff = gatepasses.values('staff__name').annotate(
            total_duration=Sum('duration', output_field=DurationField())
        ).order_by('-total_duration')[:10]  # Top 10 staff with the longest duration

        # Extract weekdays of gate passes
        weekday_counts = gatepasses.annotate(
            weekday=ExtractWeekDay('requesting_date')
        ).values('weekday').annotate(
            total_passes=Count('id')
        ).order_by('-total_passes')

        # Determine most and least active weekdays
        most_active_weekday = max(weekday_counts, key=lambda x: x['total_passes']) if weekday_counts else None
        least_active_weekday = min(weekday_counts, key=lambda x: x['total_passes']) if weekday_counts else None

        # Overall statistics
        total_requests = HostelStaffGatePass.objects.count()
        total_approved = HostelStaffGatePass.objects.filter(request_status="Approved").count()
        total_rejected = HostelStaffGatePass.objects.filter(request_status="Rejected").count()
        total_requested = HostelStaffGatePass.objects.filter(request_status="Requested").count()

        avg_duration = gatepasses.aggregate(avg_duration=Avg('duration'))['avg_duration']

        # Mentor Approval Time Analysis (EXCLUDING mentor_updated=NULL)
        mentor_approval_qs = HostelStaffGatePass.objects.filter(
            updated_on__isnull=False, mentor_updated__isnull=False
        ).annotate(
            approval_time=ExpressionWrapper(
                F('updated_on') - F('requested_on'),
                output_field=DurationField()
            )
        )

        # Mentor approval statistics
        mentor_avg_approval_time = mentor_approval_qs.aggregate(
            avg_approval_time=Avg('approval_time')
        )['avg_approval_time']

        mentor_max_approval_time = mentor_approval_qs.aggregate(
            max_approval_time=Max('approval_time')
        )['max_approval_time']

        mentor_min_approval_time = mentor_approval_qs.aggregate(
            min_approval_time=Min('approval_time')
        )['min_approval_time']

        report_data = {
            "most_going_staff": list(most_going_staff),
            "most_duration_staff": list(most_duration_staff),
            "most_active_weekday": most_active_weekday,
            "least_active_weekday": least_active_weekday,
            "total_requests": total_requests,
            "total_approved": total_approved,
            "total_rejected": total_rejected,
            "total_requested": total_requested,
            "average_duration": str(avg_duration) if avg_duration else "0:00:00",

            # Mentor Approval Time Data (EXCLUDING mentor_updated=NULL)
            "mentor_avg_approval_time": str(mentor_avg_approval_time) if mentor_avg_approval_time else "N/A",
            "mentor_max_approval_time": str(mentor_max_approval_time) if mentor_max_approval_time else "N/A",
            "mentor_min_approval_time": str(mentor_min_approval_time) if mentor_min_approval_time else "N/A",
        }

        return JsonResponse(report_data, safe=False)
    except Exception as e:
        return handle_exception(e)


@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_my_pass_list(request):
    try:
        # Get staff profile
        staff_profile = get_staff_profile(request)

        # Get gate passes for the staff
        gatepasses = HostelStaffGatePass.objects.filter(staff=staff_profile)

        # Serialize gate passes with pagination
        paginated_response = paginate_and_serialize(gatepasses, request, HostelStaffGatePassSerializer, 50)

        # Extract the paginated data
        paginated_data = paginated_response.data  # Extracting data from the Response object

        return Response({
            "status": True,
            "message": "Gate passes retrieved successfully",
            "data": paginated_data
        }, status=paginated_response.status_code)  # Maintain the original status code

    except Exception as e:
        return handle_exception(e)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def single_pass_data(request):
    try:
        pass_token = request.GET.get("pass_token", None)
        
        if pass_token is None:
            return Response({
                "status": False,
                "message": "Pass token is required",
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get gate passes for the staff
        gatepasses = HostelStaffGatePass.objects.get(pass_token=pass_token)

        # Serialize single gate pass
        serializer = HostelStaffGatePassSerializer(gatepasses)

        return Response({
            "status": True,
            "message": "Gate pass retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)  # Assuming a successful response

    except Exception as e:
        return handle_exception(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def mentor_approval_pendings(request):
    try:
        
        # Get staff profile
        staff_profile = get_staff_profile(request)

        # Get gate passes for the staff
        gatepasses = HostelStaffGatePass.objects.filter(mentor=staff_profile, mentor_updated=None)

        # Serialize gate passes with pagination
        paginated_response = paginate_and_serialize(gatepasses, request, HostelStaffGatePassSerializer, 2)

        # Extract the paginated data
        paginated_data = paginated_response.data  # Extracting data from the Response object

        return Response({
            "status": True,
            "message": "Gate passes retrieved successfully",
            "data": paginated_data
        }, status=paginated_response.status_code)  # Maintain the original status code

    except Exception as e:
        return handle_exception(e)
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mentor_rejected_gate_passes(request):
    try:
        # Get staff profile
        staff_profile = get_staff_profile(request)

        # Get gate passes for the staff
        gatepasses = HostelStaffGatePass.objects.filter(mentor=staff_profile, request_status="Rejected")

        # Serialize gate passes with pagination
        paginated_response = paginate_and_serialize(gatepasses, request, HostelStaffGatePassSerializer, 2)

        # Extract the paginated data
        paginated_data = paginated_response.data  # Extracting data from the Response object

        return Response({
            "status": True,
            "message": "Gate passes retrieved successfully",
            "data": paginated_data
        }, status=paginated_response.status_code)  # Maintain the original status code

    except Exception as e:
        return handle_exception(e)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mentor_approved_gate_passes(request):
    try:
        # Get staff profile
        staff_profile = get_staff_profile(request)

        # Get gate passes for the staff
        gatepasses = HostelStaffGatePass.objects.filter(mentor=staff_profile, request_status="Approved")

        # Serialize gate passes with pagination
        paginated_response = paginate_and_serialize(gatepasses, request, HostelStaffGatePassSerializer, 2)

        # Extract the paginated data
        paginated_data = paginated_response.data  # Extracting data from the Response object

        return Response({
            "status": True,
            "message": "Gate passes retrieved successfully",
            "data": paginated_data
        }, status=paginated_response.status_code)  # Maintain the original status code

    except Exception as e:
        return handle_exception(e)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def HostelStaffGatePassApprove(request, token, decision):

    try:
        gate_pass = HostelStaffGatePass.objects.get(pass_token=token)
        if gate_pass.mentor_updated is not None:
            mentor_updated = "approved" if gate_pass.mentor_updated else "rejected"
            return Response({
                "message": f"Request is already {mentor_updated} !",
                "status": False,
            }, status=status.HTTP_200_OK)

        if decision == "Approve":
            gate_pass.updated_on = datetime.now()
            gate_pass.mentor_updated = True
            gate_pass.gatepass_no = get_random_string(length=6) + str(gate_pass.id)
            gate_pass.request_status = "Approved"

            
            # Assuming you have AWS credentials configured as environment variables or in some other way
            aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            aws_region = os.getenv("AWS_REGION")
            bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME")
            

            # Create an S3 client
            s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)

            # Ensure the directory exists in S3 before saving the file
            directory = 'GatePass/HostelStaff/qrCodes/'
            s3_directory = f'{directory}{gate_pass.gatepass_no}.png'

            # Generate QR code
            try:
                # Generate QR code
                qr_code = pyqrcode.create(f"{gate_pass.pass_token}")

                # Create an in-memory file to save QR
                img_byte_arr = io.BytesIO()
                qr_code.png(img_byte_arr, scale=10)  # Increased scale for better resolution

                # Convert to RGB format using PIL
                img_byte_arr.seek(0)
                qr_image = Image.open(img_byte_arr).convert("RGB")

                # Resize to meet WhatsApp's recommended dimensions
                qr_image = qr_image.resize((1125, 1125), Image.Resampling.BICUBIC)

                # Save QR to a temporary file
                local_qr_code_path = f'{gate_pass.gatepass_no}.png'
                qr_image.save(local_qr_code_path, format="PNG")

            except Exception as e:
                return Response({
                    "message": str(f"Error generating QR code: {e}"),
                    "status": False,
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


            try:
                # Upload the local file to S3
                message = ""
                s3.upload_file(local_qr_code_path, bucket_name, s3_directory)

                # ✅ Verify upload success
                try:
                    s3.head_object(Bucket=bucket_name, Key=s3_directory)
                    print("✅ File successfully uploaded to S3")
                    
                    # ✅ Generate and save public URL
                    gate_pass.qr_code_url = f'https://{bucket_name}.s3.ap-south-1.amazonaws.com/{s3_directory}'
                    gate_pass.save()
                
                except ClientError as e:
                    message += f" | Failed to verify file: {e}"

            except NoCredentialsError:
                message += " | No S3 credentials found"
            except Exception as e:
                message += f" | Error uploading file to S3: {e}"

            finally:
                # ✅ Ensure cleanup of local files
                if os.path.exists(local_qr_code_path):
                    os.remove(local_qr_code_path)

            
            qr_code_url = gate_pass.qr_code_url
            tenant_name = "Mims"
            mentor_name = str(gate_pass.mentor.name).strip()
            mentor_department = str(gate_pass.mentor.department.name).strip()
            mentor_designation = str(gate_pass.mentor.designation.name).strip()
            check_out_date = gate_pass.requesting_date.strftime('%d-%m-%Y')
            check_out_time = gate_pass.requesting_time.strftime('%I:%M %p')
            check_in_date = gate_pass.return_date.strftime('%d-%m-%Y')
            check_in_time = gate_pass.return_time.strftime('%I:%M %p')
            purpose = gate_pass.purpose
            
            staff_number = gate_pass.staff.mobile.strip().replace(" ", "")
            if staff_number.startswith('+'):
                staff_number = staff_number[1:]
                
                

            
            # # # WhatsApp message to Student parent
            data = {
                "messaging_product": "whatsapp",
                "to": str(staff_number),  
                "type": "template",
                "template": {
                    "name": "hostel_approved_pass_staff",
                    "language": {"code": "en"},
                    "components": [
                        {
                            "type": "header",
                            "parameters": [
                                {
                                    "type": "image",
                                    "image": {
                                        "link": qr_code_url  
                                    }
                                }
                            ]
                        },
                        {
                            "type": "body",
                            "parameters": [
                                {"type": "text", "text": tenant_name},  
                                {"type": "text", "text": mentor_name},
                                {"type": "text", "text": mentor_department},
                                {"type": "text", "text": mentor_designation},
                                {"type": "text", "text": check_out_date},
                                {"type": "text", "text": check_out_time},
                                {"type": "text", "text": check_in_date},
                                {"type": "text", "text": check_in_time},
                                {"type": "text", "text": purpose}
                            ]
                        }
                    ]
                }
            }
            
            # # # WhatsApp message to Student parent
            # data = {
            #     "messaging_product": "whatsapp",
            #     "to": staff_number,  
            #     "type": "template",
            #     "template": {
            #         "name": "no_qr_template",
            #         "language": {"code": "en"},
            #         "components": [
            #             {
            #                 "type": "body",
            #                 "parameters": [
            #                     {"type": "text", "text": tenant_name},  
            #                     {"type": "text", "text": mentor_name},
            #                     {"type": "text", "text": mentor_department},
            #                     {"type": "text", "text": mentor_designation},
            #                     {"type": "text", "text": check_out_date},
            #                     {"type": "text", "text": check_out_time},
            #                     {"type": "text", "text": check_in_date},
            #                     {"type": "text", "text": check_in_time},
            #                     {"type": "text", "text": purpose}
            #                 ]
            #             }
            #         ]
            #     }
            # }
            
            
            type = f"Gatepass Approved message to '{gate_pass.staff.name}', Approved by Mentor '{mentor_name}'"
            whatsapp_alert_to_staff = send_whatsapp_message(request, passing_data=data, type=type, sent_to=staff_number)
            
            if whatsapp_alert_to_staff == True:
                return Response(
                        {"message": "Gate pass approved successfully", 
                        "notification_status": whatsapp_alert_to_staff, 
                        "status": True},
                        status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": "Gate pass approval failed to send WhatsApp message",
                     "url": f"{gate_pass.qr_code_url}",
                     "message" : message,
                     "notification_status": whatsapp_alert_to_staff, 
                     "status": False},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


        elif decision == "Reject":
            #reject reason
            reason = request.POST.get('reason')
            if not reason:
                return Response({
                    "message": "Reason is required to reject the pass.",
                    "status": False,
                }, status=status.HTTP_400_BAD_REQUEST)
                           
            tentant_name = "Mims"
            mentor_name = str(gate_pass.mentor.name).strip()
            mentor_department = str(gate_pass.mentor.department.name).strip()
            mentor_designation = str(gate_pass.mentor.designation.name).strip()
            check_out_date = gate_pass.requesting_date.strftime('%d-%m-%Y')
            check_out_time = gate_pass.requesting_time.strftime('%I:%M %p')
            check_in_date = gate_pass.return_date.strftime('%d-%m-%Y')
            check_in_time = gate_pass.return_time.strftime('%I:%M %p')
            purpose = gate_pass.purpose
            rejection_reason = reason
            
            
            staff_number = gate_pass.staff.mobile.strip().replace(" ", "")
            if staff_number.startswith('+'):
                staff_number = staff_number[1:]

            
            # # WhatsApp message to Student parent
            data = {
                "messaging_product": "whatsapp",
                "to": f"{staff_number}",
                "type": "template",
                "template": {
                    "name": "rejected_hostel_staff_gatepass",
                    "language": {"code": "en"},
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": tentant_name
                                },
                                {
                                    "type": "text",
                                    "text": mentor_name
                                },
                                {
                                    "type": "text",
                                    "text": mentor_department
                                },
                                {
                                    "type": "text",
                                    "text": mentor_designation
                                },
                                {
                                    "type": "text",
                                    "text": check_out_date
                                },
                                {
                                    "type": "text",
                                    "text": check_out_time
                                },
                                {
                                    "type": "text",
                                    "text": check_in_date
                                },
                                {
                                    "type": "text",
                                    "text": check_in_time
                                },
                                {
                                    "type": "text",
                                    "text": purpose
                                },
                                {
                                    "type": "text",
                                    "text": rejection_reason
                                },
                            ]
                        }
                    ]
                }
            }
            
            type = f"Gatepass Rejcted message to '{gate_pass.staff.name}', Rejected by Mentor {mentor_name}'"
            sent_to = staff_number
            whatsapp_alert_to_staff = send_whatsapp_message(request, passing_data=data, type=type, sent_to=sent_to)
            
            if whatsapp_alert_to_staff == True:
                #gatepass to save 
                gate_pass.request_status = "Rejected"
                gate_pass.remarks = reason
                gate_pass.mentor_updated = True
                gate_pass.updated_on = datetime.now()
                gate_pass.save()
                
                return Response(
                        {"message": "Gate pass Rejcted successfully", 
                        "notification_status": whatsapp_alert_to_staff, 
                        "wa_number": sent_to,
                        "status": True},
                        status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": "Gate pass rejcetion failed to send WhatsApp message", "notification_status": whatsapp_alert_to_staff, "status": False},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
    except Exception as e:
        return handle_exception(e)
    
    


@api_view(['GET'])
def check_in_check_out_marker(request):
    gatepass_code = request.GET.get('unique_id', None)
    if not gatepass_code:
        return JsonResponse({'status': False, 'message': 'Gatepass Uniquecode is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Determine the type based on gatepass_code and set model and serializer accordingly
    model, serializer = (HostelStaffGatePass, HostelStaffGatePassSerializer)
    
    try:
        gatepass = model.objects.get(pass_token=gatepass_code)
        if not gatepass.mentor_updated:
            return JsonResponse({'status': False, 'message': 'Mentor not updated'}, status=status.HTTP_400_BAD_REQUEST)
        
    except model.DoesNotExist:
        return JsonResponse({'status': False, 'message': 'Invalid gatepass code'}, status=status.HTTP_404_NOT_FOUND)

    current_time = timezone.now()
    today = current_time.date()

    # Check for valid date
    if not gatepass.checked_out:
        if gatepass.requesting_date != today:
            return JsonResponse({
                'status': False, 
                'message': f'This Gatepass is only valid to checkout on {gatepass.requesting_date}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return handle_check_in_out(gatepass, current_time, gatepass_code,serializer)

def  handle_check_in_out(gatepass, current_time, gatepass_code,serializer):
    # Handle check-out
    if not gatepass.checked_out:
        gatepass.checked_out = True
        gatepass.date_time_exit = current_time
        gatepass.save(update_fields=['checked_out', 'date_time_exit'])
        # Corrected function call with all required arguments in the correct order
        return build_response(gatepass, current_time, "Check Out time marked successfully", "check-out", gatepass_code, serializer)
    
    # Gatepass already used
    if gatepass.checked_in:
        return JsonResponse({
            'status': False, 
            'message': "Gatepass already used for check out & check in",
            'type': "Expired",
        }, status=status.HTTP_400_BAD_REQUEST)

    # Wait if checked out recently
    if gatepass.date_time_exit and (current_time - gatepass.date_time_exit) < timedelta(minutes=3):
        wait_time = (gatepass.date_time_exit + timedelta(minutes=3) - current_time).seconds // 60
        return JsonResponse({'status': False, 'message': f"Checked out recently, please wait {wait_time} minutes before checking in"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle check-in
    gatepass.checked_in = True
    gatepass.date_time_entry = current_time
    gatepass.duration = current_time - gatepass.date_time_exit
    gatepass.save(update_fields=['checked_in', 'date_time_entry','duration' ])
    return build_response(gatepass, current_time, "Check In time marked successfully", "check-in", gatepass_code,serializer)

def build_response(gatepass, current_time, message, action_type, gatepass_code,serializer):
    return JsonResponse({
        'status': True, 
        'message': message,
        f'{action_type}_time': current_time,
        'type': action_type
    }, status=status.HTTP_200_OK)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pass_counts_for_mentor(request):
    try:
        staff_profile = get_staff_profile(request)
        status_counts = Counter(
            HostelStaffGatePass.objects.filter(mentor=staff_profile)
            .values_list("request_status", flat=True)
        )

        return Response({
            "total_gatepasses": sum(status_counts.values()),
            "approval_pending": status_counts.get("Requested", 0),
            "approved_pass": status_counts.get("Approved", 0),
            "rejected_pass": status_counts.get("Rejected", 0),
            "status": True
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return handle_exception(e)
