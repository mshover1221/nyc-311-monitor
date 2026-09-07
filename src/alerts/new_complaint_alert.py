import logging
from datetime import datetime
from src.email.email_sender import send_email

"""
This module evaluates whether a newly inserted complaint
should trigger an alert, builds the email content, and sends it.
"""

def build_alert_email(complaint):
    return f"""
    <h2>New 311 Complaint Alert</h2>

    <p><strong>Complaint ID:</strong> {complaint.unique_key}</p>
    <p><strong>Created:</strong> {complaint.created_date}</p>
    <p><strong>Agency:</strong> {complaint.agency} — {complaint.agency_name}</p>
    <p><strong>Type:</strong> {complaint.complaint_type}</p>
    <p><strong>Descriptor:</strong> {complaint.descriptor}</p>
    <p><strong>Borough:</strong> {complaint.borough}</p>

    <p><strong>Location:</strong> {complaint.latitude}, {complaint.longitude}</p>

    <hr>
    <p>This is an automated alert from NYC 311 Monitor.</p>
    """


def should_trigger_alert(complaint):
    """
    Basic logic for new complaint alerts.
    Right now: ALWAYS alert on new complaints.
    Later: add filters, keywords, borough logic, etc.
    """
    return True


def run_new_complaint_alert(complaint, db_session):
    """
    Main entry point.
    Called immediately after inserting a new complaint into the DB.

    Steps:
    1. Check if alert should trigger
    2. Build email content
    3. Send email
    4. Record alert in DB to prevent duplicates
    """

    # Prevent duplicates: check if alert already sent
    if complaint.alert_sent:
        logging.info(f"Alert already sent for complaint {complaint.unique_key}")
        return False

    if not should_trigger_alert(complaint):
        logging.info(f"No alert triggered for complaint {complaint.unique_key}")
        return False

    subject = f"New 311 Complaint: {complaint.complaint_type}"
    html_content = build_alert_email(complaint)

    success = send_email(
        subject=subject,
        html_content=html_content,
        to_email="mshover985@gmail.com"  # change later for subscribers
    )

    if success:
        complaint.alert_sent = True
        complaint.alert_sent_at = datetime.utcnow()
        db_session.commit()
        logging.info(f"Alert sent and recorded for complaint {complaint.unique_key}")
        return True
    else:
        logging.error(f"Failed to send alert for complaint {complaint.unique_key}")
        return False


