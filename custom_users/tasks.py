from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def send_otp_to_email(self, to_email, otp, name,org_name):
    mail_subject = f"OTP Code from {org_name} Connect "

    # HTML content for the email
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OTP Verification</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                text-align: center;
            }}
            .container {{
                max-width: 600px;
                margin: 30px auto;
                background: #ffffff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }}
            .logo {{
                width: 150px;
                margin-top: 20px;
            }}
            .otp {{
                font-size: 28px;
                font-weight: bold;
                background: #28a745;
                color: #ffffff;
                display: inline-block;
                padding: 12px 30px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .message {{
                font-size: 18px;
                color: #333;
            }}
            .footer {{
                margin-top: 20px;
                font-size: 14px;
                color: #777;
                background: #f1f1f1;
                padding: 20px;
                border-radius: 10px;
            }}
            .social-icons {{
                margin-top: 15px;
            }}
            .social-icons a {{
                margin: 0 10px;
                display: inline-block;
            }}
            .social-icons img {{
                width: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Hello, {name}!</h2>
            <h3>Welcome to {org_name}</h3>
            <h2>Email Verification</h2>
            <p class="message">Your One-Time Password (OTP) for verification is:</p>
            <div class="otp">{otp}</div>
            <p class="message">This OTP is valid for only 10 minutes. Do not share it with anyone.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <div class="footer">
                <p>Follow us on:</p>
                <div class="social-icons">
                    <a href="https://www.linkedin.com/company/connect-v2/posts/?feedView=all"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn"></a>
                    <a href="https://www.instagram.com/connect.v2/"><img src="https://cdn-icons-png.flaticon.com/512/2111/2111463.png" alt="Instagram"></a>
                </div>
                <p>&copy; 2025 Edentu Learning Solutions Private Limited. All rights reserved.</p>
                <p>Need help? Contact us at <a href="mailto:itmanager@edentu.com">itmanager@edentu.com</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        email = EmailMultiAlternatives(
            subject=mail_subject,
            body=strip_tags(html_content),  # Fallback text version
            from_email=settings.EMAIL_HOST_USER,
            to=[to_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        logger.info(f"OTP email sent successfully to {to_email}")

    except Exception as e:
        logger.error(f"Failed to send OTP email to {to_email}: {str(e)}")

    return "Email Sent"
