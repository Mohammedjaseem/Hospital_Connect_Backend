from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def send_otp_to_email(self, to_email, otp, name, org_name):
    mail_subject = f"OTP Code from {org_name} Connect"
    current_date = datetime.now().strftime("%B %d, %Y")

    html_content = f"""
    <!DOCTYPE html>
    <html lang=\"en\">
      <head>
        <meta charset=\"UTF-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
        <meta http-equiv=\"X-UA-Compatible\" content=\"ie=edge\" />
        <title>Static Template</title>

        <link
          href=\"https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap\"
          rel=\"stylesheet\"
        />
      </head>
      <body
        style=\"margin: 0; font-family: 'Poppins', sans-serif; background: #ffffff; font-size: 14px;\"
      >
        <div
          style=\"max-width: 680px; margin: 0 auto; padding: 45px 30px 60px; background: #f4f7ff;
            background-image: url(https://archisketch-resources.s3.ap-northeast-2.amazonaws.com/vrstyler/1661497957196_595865/email-template-background-banner);
            background-repeat: no-repeat; background-size: 800px 452px; background-position: top center;
            font-size: 14px; color: #434343;\"
        >
          <header>
            <table style=\"width: 100%;\">
              <tbody>
                <tr style=\"height: 0;\">
                  <td>
                    <img
                      alt=\"\"
                      src=\"https://connectv2s3.s3.ap-south-1.amazonaws.com/Logo/ConnectLogo1024-removebg+(1).png\"
                      height=\"80px\"
                    />
                  </td>
                  <td style=\"text-align: right;\">
                    <span style=\"font-size: 16px; line-height: 30px; color: #ffffff;\">{current_date}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </header>

          <main>
            <div
              style=\"margin: 0; margin-top: 70px; padding: 50px 30px 90px;
              background: #ffffff; border-radius: 30px; text-align: center;\"
            >
              <div style=\"width: 100%; max-width: 489px; margin: 0 auto;\">
                <h1 style=\"margin: 0; font-size: 24px; font-weight: 500; color: #1f1f1f;\">
                  Connect Register OTP
                </h1>

                <p style=\"margin: 0; margin-top: 5px; font-weight: 500; letter-spacing: 0.56px;\">
                  Hello, <b>{name}</b><br><br>
                  Thank you for choosing <b>{org_name}</b>.<br><br>
                  Use the following OTP to verify your email address.<br>
                  OTP is valid for <span style=\"font-weight: 600; color: #1f1f1f;\">10 minutes</span>.<br><br>
                </p>

                <p
                  style=\"margin: 0; margin-top: 60px; font-size: 40px; font-weight: 600;
                  letter-spacing: 25px; color: #ba3d4f;\"
                >
                  {otp}
                </p>

                <p style=\"margin: 0; margin-top: 15px; font-weight: 500; letter-spacing: 0.56px;\">
                  Do not share this code with others, including Connect employees.
                </p>
              </div>
            </div>

            <p
              style=\"max-width: 400px; margin: 0 auto; margin-top: 50px; text-align: center;
              font-weight: 500; color: #8c8c8c;\"
            >
              Need help? Ask at
              <a
                href=\"mailto:itmanager@edentu.com\"
                style=\"color: #499fb6; text-decoration: none;\"
              >itmanager@edentu.com</a>
            </p>
          </main>

          <footer
            style=\"width: 100%; max-width: 490px; margin: 20px auto 0; text-align: center;
              border-top: 1px solid #e6ebf1;\"
          >
            <p style=\"margin: 0; margin-top: 40px; font-size: 16px; font-weight: 600; color: #434343;\">
              Connect V2 by {org_name}.
            </p>
            <p style=\"margin: 0; margin-top: 8px; color: #434343;\">Edappal Kerala.</p>
            <div style=\"margin: 0; margin-top: 16px;\">
              <a href=\"\" target=\"_blank\" style=\"display: inline-block;\">
                <img width=\"36px\" alt=\"Facebook\"
                  src=\"https://archisketch-resources.s3.ap-northeast-2.amazonaws.com/vrstyler/1661502815169_682499/email-template-icon-facebook\" />
              </a>
              <a href=\"\" target=\"_blank\" style=\"display: inline-block; margin-left: 8px;\">
                <img width=\"36px\" alt=\"Instagram\"
                  src=\"https://archisketch-resources.s3.ap-northeast-2.amazonaws.com/vrstyler/1661504218208_684135/email-template-icon-instagram\" />
              </a>
              <a href=\"\" target=\"_blank\" style=\"display: inline-block; margin-left: 8px;\">
                <img width=\"36px\" alt=\"Twitter\"
                  src=\"https://archisketch-resources.s3.ap-northeast-2.amazonaws.com/vrstyler/1661503043040_372004/email-template-icon-twitter\" />
              </a>
              <a href=\"\" target=\"_blank\" style=\"display: inline-block; margin-left: 8px;\">
                <img width=\"36px\" alt=\"Youtube\"
                  src=\"https://archisketch-resources.s3.ap-northeast-2.amazonaws.com/vrstyler/1661503195931_210869/email-template-icon-youtube\" />
              </a>
            </div>
            <p style=\"margin: 0; margin-top: 16px; color: #434343;\">
              Copyright © 2025. All rights reserved.
            </p>
          </footer>
        </div>
      </body>
    </html>
    """

    try:
        email = EmailMultiAlternatives(
            subject=mail_subject,
            body=strip_tags(html_content),
            from_email=settings.EMAIL_HOST_USER,
            to=[to_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        logger.info(f"OTP email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send OTP email to {to_email}: {str(e)}")

    return "Email Sent"
