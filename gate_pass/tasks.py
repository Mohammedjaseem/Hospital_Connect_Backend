from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import logging
from connect_bills.models import EmailLog
from smtplib import SMTPException

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(SMTPException,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def send_email(self, subject, message, recipient, cc_emails=None):
    """
    Celery task to send emails asynchronously.
    Automatically retries up to 3 times if an error occurs.
    """
    try:
        print(f"📩 Preparing email for {recipient}")  
        logger.info(f"📩 Preparing email for {recipient}")

        # Use EmailMultiAlternatives to support HTML and plaintext emails
        email = EmailMultiAlternatives(
            subject=subject,
            body="Your email client does not support HTML content.",  # Fallback text
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient]
        )

        if cc_emails:
            email.cc = cc_emails

        email.attach_alternative(message, "text/html")  # Attach HTML message

        print(f"📤 Sending email to {recipient}...")  
        logger.info(f"📤 Sending email to {recipient}...")

        email.send()

        print(f"✅ Email successfully sent to {recipient}")  
        logger.info(f"✅ Email successfully sent to {recipient}")

        # # ✅ Log successful email sending
        # EmailLog.objects.create(
        #     sent_by="Celery Worker",
        #     subject=subject,
        #     recipient=recipient,
        #     cc_emails=cc_emails or "",
        #     status="Sent"
        # )

        return True

    except SMTPException as e:
        print(f"🚨 SMTP error while sending email: {e}")  
        logger.error(f"🚨 SMTP error while sending email: {e}")

        # Log failure
        EmailLog.objects.create(
            subject=subject,
            recipient=recipient,
            cc_emails=cc_emails or "",
            message=message,
            status="Failed",
            error_message=str(e)
        )

        raise self.retry(exc=e)  

    except Exception as e:
        print(f"❌ Unexpected error sending email: {e}")  
        logger.exception(f"❌ Unexpected error sending email: {e}")

        EmailLog.objects.create(
            subject=subject,
            recipient=recipient,
            cc_emails=cc_emails or "",
            message=message,
            status="Failed",
            error_message=str(e)
        )

        return False  
