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

from .models import HostelStaffGatePass
from utils.handle_exception import handle_exception
from utils.whatsapp_sender import send_whatsapp_message
from utils.fetch_staff import get_staff_profile


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

        if latest_gate_pass:
            time_left = latest_gate_pass.requested_on + timedelta(hours=5) - timezone.now()
            hours, minutes = divmod(time_left.total_seconds(), 3600)
            return Response(
                {
                    "message": f"You have already requested a gate pass within the last 5 hours. Please try after {int(hours):02}:{int(minutes // 60):02}.",
                    "status": False,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

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
        mentor_number = mentor.staff_profile.mobile

        # Create gate pass
        gate_pass = HostelStaffGatePass.objects.create(
            student=staff_profile,
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
                "name": "staff_gatepass",
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
                            {"type": "text", "text": str(total_out_duration)},
                            {"type": "text", "text": purpose},
                            {"type": "button", "index": "0", "sub_type": "url", "parameters": [{"type": "text", "text": str(gate_pass.pass_token)}]},
                            {"type": "button", "index": "1", "sub_type": "url", "parameters": [{"type": "text", "text": str(gate_pass.pass_token)}]}
                        ]
                    }
                ]
            }
        }

        # Send WhatsApp notification
        notification_status = send_whatsapp_message(request, passing_data=whatsapp_data, type="Gatepass request", sent_to=mentor_number)

        if notification_status:
            return Response(
                {"message": "Gate pass request sent successfully", "status": True},
                status=status.HTTP_200_OK
            )
        else:
            gate_pass.delete()  # Rollback if message fails
            return Response(
                {"message": "Gate pass request failed to send WhatsApp message", "status": False},
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




