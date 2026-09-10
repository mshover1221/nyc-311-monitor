"""Send NYC 311 alert emails through SendGrid."""

import logging
import os

from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

logger = logging.getLogger(__name__)

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")

if not SENDGRID_API_KEY:
    raise RuntimeError("SENDGRID_API_KEY is not set in environment variables")

if not FROM_EMAIL:
    raise RuntimeError("SENDGRID_FROM_EMAIL is not set in environment variables")


def send_email(subject: str, html_content: str, to_email: str) -> bool:
    """
    Send an email using SendGrid.

    Returns True when SendGrid accepts the message (HTTP 202).
    Returns False if the request fails.
    """

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )

    try:
        sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
        response = sg.send(message)

        if response.status_code == 202:
            logger.info("Email accepted by SendGrid for %s", to_email)
            return True

        logger.error(
            "SendGrid returned status %s: %s",
            response.status_code,
            response.body,
        )
        return False

    except Exception:
        logger.exception("Error sending email to %s", to_email)
        return False

