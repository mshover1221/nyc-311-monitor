"""Run the NYC 311 alert evaluation pipeline."""

import os
from datetime import datetime, timedelta

from src.app.db import SessionLocal
from src.email.email_sender import send_email
from src.alerts.detector import evaluate_conditions, get_triggered_conditions
from src.alerts.formatter import format_alert_text


CONDITIONS = [
    ("BROOKLYN", "Noise"),
    ("BROOKLYN", "Water System"),
    ("QUEENS", "Noise"),
]

ALERT_RECIPIENT = os.getenv("ALERT_RECIPIENT")
ALERT_SUBJECT = "NYC 311 Alert"

def run_alert_evaluation(start_time, end_time):
    """Evaluate configured alert conditions and return formatted alert text."""
    session = SessionLocal()

    try:
        results = evaluate_conditions(
            session,
            start_time,
            end_time,
            CONDITIONS,
        )

        triggered_conditions = get_triggered_conditions(results)

        if not triggered_conditions:
            return None

        alert_text = format_alert_text(triggered_conditions)

        if not ALERT_RECIPIENT:
            raise RuntimeError("ALERT_RECIPIENT is not set in environment variables")

        send_email(
            ALERT_SUBJECT,
            alert_text,
            ALERT_RECIPIENT,
        )

        return alert_text

    finally:
        session.close()