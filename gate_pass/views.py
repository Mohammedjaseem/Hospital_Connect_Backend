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
from botocore.exceptions import NoCredentialsError 


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_staff_hostel_gate_pass(request):
    try:
        staff_profile = get_staff_profile(request)

        # Ensure user is hostel staff
        if not staff_profile.is_hosteller:
            return Response(
                {"message": "You are not a hostel staff"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for a gate pass requested within the last 5 hours
        five_hours_ago = timezone.now() - timedelta(hours=5)
        latest_gate_pass = HostelStaffGatePass.objects.filter(
            staff=staff_profile, requested_on__gte=five_hours_ago
        ).only('requested_on').first()

        # if latest_gate_pass:
        #     time_left = latest_gate_pass.requested_on + timedelta(hours=5) - timezone.now()
        #     hours, minutes = divmod(time_left.total_seconds(), 3600)
        #     return Response(
        #         {
        #             "message": f"You have already requested a gate pass within the last 5 hours. Please try after {int(hours):02}:{int(minutes // 60):02}.",
        #             "status": False,
        #         },
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        # Required fields validation
        required_fields = ['purpose', 'requesting_date', 'requesting_time', 'return_date', 'return_time']
        missing_fields = [field for field in required_fields if not request.data.get(field)]
        if missing_fields:
            return Response(
                {"message": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extract data
        purpose = request.data['purpose']
        requesting_date = request.data['requesting_date']
        requesting_time = request.data['requesting_time']
        return_date = request.data['return_date']
        return_time = request.data['return_time']

        # Convert times from 12-hour format to 24-hour format
        requesting_time = datetime.strptime(requesting_time, '%I:%M %p').strftime('%H:%M:%S')
        return_time = datetime.strptime(return_time, '%I:%M %p').strftime('%H:%M:%S')

        # Get mentor details
        mentor = staff_profile.hostel.incharge
        mentor_number = mentor.mobile.strip().replace(" ", "")

        # Remove leading '+' if present
        if mentor_number.startswith('+'):
            mentor_number = mentor_number[1:]
            

        # Create gate pass
        gate_pass = HostelStaffGatePass.objects.create(
            staff=staff_profile,
            mentor=mentor,
            purpose=purpose,
            requesting_date=requesting_date,
            requesting_time=requesting_time,
            return_date=return_date,
            return_time=return_time,
            pass_token=f"GatePass-{uuid.uuid4()}"
        )

        # Calculate total out duration
        total_seconds = (datetime.strptime(f"{return_date} {return_time}", "%Y-%m-%d %H:%M:%S") - 
                         datetime.strptime(f"{requesting_date} {requesting_time}", "%Y-%m-%d %H:%M:%S")).total_seconds()

        days, remainder = divmod(total_seconds, 86400)  # 86400 seconds in a day
        hours, remainder = divmod(remainder, 3600)  # 3600 seconds in an hour
        minutes, _ = divmod(remainder, 60)  # 60 seconds in a minute

        if days > 0:
            total_out_duration = f"{int(days)} day{'s' if days > 1 else ''} {int(hours)} hr{'s' if hours != 1 else ''} {int(minutes)} min{'s' if minutes != 1 else ''}"
        else:
            total_out_duration = f"{int(hours)} hr{'s' if hours != 1 else ''} {int(minutes)} min{'s' if minutes != 1 else ''}"

        # Convert times to 12-hour format with AM/PM
        check_out_time = datetime.strptime(requesting_time, "%H:%M:%S").strftime("%I:%M %p")
        check_in_time = datetime.strptime(return_time, "%H:%M:%S").strftime("%I:%M %p")

        # WhatsApp notification data
        tenant_name = "Mims"
        whatsapp_data = {
            "messaging_product": "whatsapp",
            "to": f"{mentor_number}",
            "type": "template",
            "template": {
                "name": "staff_hostel_pass_request",
                "language": {"code": "en"},
                "components": [
                    {"type": "header", "parameters": [{"type": "text", "text": tenant_name}]},
                    {
                        "type": "body",
                        "parameters": [
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
                        ]
                    },
                    
                        {
                            "type": "button",
                            "index": "0",
                            "sub_type": "url",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": str(gate_pass.pass_token)
                                },
                            ]
                        },
                        {
                            "type": "button",
                            "index": "1",
                            "sub_type": "url",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": str(gate_pass.pass_token)
                                },
                            ]
                        },
                ]
            }
        }
        
        # mentor_number = 918086500023

        # Send WhatsApp notification
        notification_status = send_whatsapp_message(request, passing_data=whatsapp_data, type="Gatepass request", sent_to=mentor_number)
        print("notification_status", notification_status)
        if notification_status == True:
            return Response(
                {"message": "Gate pass request sent successfully", 
                 "notification_status": notification_status, 
                 "wa_number": mentor_number,
                 "status": True},
                status=status.HTTP_200_OK
            )
        else:
            gate_pass.delete()  # Rollback if message fails
            return Response(
                {"message": "Gate pass request failed to send WhatsApp message", "notification_status": notification_status, "status": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
        # gatepasses = HostelStaffGatePass.objects.filter(staff=staff_profile)
        gatepasses = HostelStaffGatePass.objects.all()

        # Serialize gate passes
        serialized_gatepasses = HostelStaffGatePassSerializer(gatepasses, many=True).data

        return Response({
                "data": serialized_gatepasses,
                "status": True,
            }, status=status.HTTP_200_OK)
    except Exception as e:
        return handle_exception(e)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def HostelStaffGatePassApprove(request, token, decision):
    try:
        gate_pass = HostelStaffGatePass.objects.get(pass_token=token)
        
        if gate_pass.mentor_updated is not None:
            status_msg = "approved" if gate_pass.mentor_updated else "rejected"
            return Response(
                {"message": f"Request is already {status_msg}!", "status": False},
                status=status.HTTP_200_OK
            )

        if decision not in ["Approve", "Reject"]:
            return Response(
                {"message": "Invalid decision provided!", "status": False},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch and format required data
        formatted_data = {
            "tenant_name": "Mims",
            "mentor_name": gate_pass.mentor.name.strip(),
            "mentor_department": gate_pass.mentor.department.name.strip(),
            "mentor_designation": gate_pass.mentor.designation.name.strip(),
            "check_out_date": gate_pass.requesting_date.strftime('%d-%m-%Y'),
            "check_out_time": gate_pass.requesting_time.strftime('%I:%M %p'),
            "check_in_date": gate_pass.return_date.strftime('%d-%m-%Y'),
            "check_in_time": gate_pass.return_time.strftime('%I:%M %p'),
            "purpose": gate_pass.purpose
        }
        
        # Format Staff Number
        staff_number = gate_pass.staff.mobile.strip().replace(" ", "")
        staff_number = staff_number.lstrip("+")  # Remove '+' prefix

        if decision == "Approve":
            return handle_gatepass_approval(gate_pass, formatted_data, staff_number)

        elif decision == "Reject":
            reason = request.POST.get('reason')
            if not reason:
                return Response({"message": "Reason is required to reject the pass.", "status": False},
                                status=status.HTTP_400_BAD_REQUEST)

            return handle_gatepass_rejection(gate_pass, formatted_data, staff_number, reason)

    except HostelStaffGatePass.DoesNotExist:
        return Response({"message": "Invalid gate pass token!", "status": False}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"message": str(e), "status": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def handle_gatepass_approval(gate_pass, formatted_data, staff_number):
    try:
        # Generate gate pass number
        gate_pass.updated_on = now()
        gate_pass.mentor_updated = True
        gate_pass.gatepass_no = get_random_string(length=6) + str(gate_pass.id)
        gate_pass.request_status = "Approved"

        # Upload QR Code to S3
        qr_code_url = generate_and_upload_qr(gate_pass)
        if not qr_code_url:
            return Response(
                {"message": "QR code generation failed.", "status": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        gate_pass.qr_code_url = qr_code_url
        gate_pass.save()

        # Send WhatsApp Notification
        whatsapp_status = send_whatsapp_notification("hostel_staff_approved_pass", staff_number, formatted_data)
        if whatsapp_status == True:
            return Response(
                {
                    "message": "Gate pass approved successfully",
                    "notification_status": whatsapp_status,
                    "wa_number": staff_number,
                    "status": True
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Gate pass approval failed to send WhatsApp message", 
                 "notification_status": whatsapp_status,"
                 "status": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        return Response(
            {"message": f"Error approving gate pass: {e}", "status": False},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def handle_gatepass_rejection(gate_pass, formatted_data, staff_number, reason):
    try:
        formatted_data["rejection_reason"] = reason

        whatsapp_status = send_whatsapp_notification("hostel_staff_rejected_pass", staff_number, formatted_data)

        if whatsapp_status:
            gate_pass.request_status = "Rejected"
            gate_pass.remarks = reason
            gate_pass.mentor_updated = True
            gate_pass.updated_on = now()
            gate_pass.save()

            return Response(
                {
                    "message": "Gate pass rejected successfully",
                    "notification_status": whatsapp_status,
                    "wa_number": staff_number,
                    "status": True
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Gate pass rejection failed to send WhatsApp message", "status": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        return Response(
            {"message": f"Error rejecting gate pass: {e}", "status": False},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def generate_and_upload_qr(gate_pass):
    try:
        # AWS Credentials
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region = os.getenv("AWS_REGION")
        bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME")
        directory = "GatePass/HostelStaff/qrCodes/"
        s3_filename = f"{directory}{gate_pass.gatepass_no}.png"

        # Generate QR Code
        qr = pyqrcode.create(gate_pass.pass_token)
        local_file = f"{gate_pass.gatepass_no}.png"
        qr.png(local_file, scale=6)

        # Upload to S3
        s3 = boto3.client("s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)
        s3.upload_file(local_file, bucket_name, s3_filename)
        s3.put_object_acl(Bucket=bucket_name, Key=s3_filename, ACL="public-read")

        os.remove(local_file)  # Clean up local file

        return f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{s3_filename}"
    
    except NoCredentialsError:
        return "cred issues"
    except Exception as e:
        return handle_exception(e)


def send_whatsapp_notification(template_name, staff_number, data):
    try:
        message_payload = {
            "messaging_product": "whatsapp",
            "to": staff_number,
            "type": "template",
            "template": {"name": template_name, "language": {"code": "en"}, "components": [{"type": "body", "parameters": [{"type": "text", "text": value} for value in data.values()]}]},
        }
        return send_whatsapp_message(message_payload)
    except Exception as e:
        return handle_exception(e)