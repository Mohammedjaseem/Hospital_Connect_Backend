from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
import uuid
from .models import HostelStaffGatePass
from utils.handle_exception import handle_exception
from utils.whatsapp_sender import send_whatsapp_message


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_staff_hostel_gate_pass(request):
    try:
        staff_profile = request.user.staff_profile

        # Ensure user is hostel staff
        if not staff_profile.is_hosteler:
            return Response(
                {"message": "You are not a hostel staff"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for a gate pass requested within the last 5 hours
        five_hours_ago = timezone.now() - timedelta(hours=5)
        latest_gate_pass = HostelStaffGatePass.objects.filter(
            student=staff_profile, requested_on__gte=five_hours_ago
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
    


