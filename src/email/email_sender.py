import ssl
import certifi
import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = "alerts@nyc311alerts.com"

if not SENDGRID_API_KEY:
    raise RuntimeError("SENDGRID_API_KEY is not set in environment variables")

ssl_context = ssl.create_default_context(cafile=certifi.where())
sg = SendGridAPIClient(api_key=SENDGRID_API_KEY, ssl_context=ssl_context)

def send_email(subject: str, html_content: str, to_email: str) -> bool:
    """
    Sends an email using SendGrid.
    Returns True on success, False on failure.
    """

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )

    try:
        response = sg.send(message)

        if response.status_code == 202:
            logging.info(f"Email sent successfully to {to_email}")
            return True
        else:
            logging.error(
                f"SendGrid returned non-202 status: {response.status_code}, body: {response.body}"
            )
            return False

    except Exception as e:
        logging.exception(f"Error sending email to {to_email}: {e}")
        return False
