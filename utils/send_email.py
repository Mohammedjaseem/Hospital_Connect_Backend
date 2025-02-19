
from connect_bills.models import EmailLog
from django.core.mail import EmailMessage


def send_email(subject, message, recipient, cc_emails=None):
    try:
        try:
            # Create the email message
            send_email = EmailMessage(subject, message, to=[recipient])

            # Add CC emails if provided
            if cc_emails:
                send_email.cc = cc_emails

            # Set content subtype for HTML email
            send_email.content_subtype = "html"

            # Send the email
            send_email.send()
            EmailLog.objects.create(
                sent_by="Main Thread",
                subject=subject,
                recipient=recipient,
                cc_emails=cc_emails,
                status='Sent'
            )
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            EmailLog.objects.create(
                subject=subject,
                recipient=recipient,
                cc_emails=cc_emails,
                message=message,
                status='Failed',
                error_message=str(e)
            )
            return False
    except Exception as e:
        print("Mailer Error: ", e)
        return False
   