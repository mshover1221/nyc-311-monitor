import logging
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy.orm import Session

from app.db import Complaint, SessionLocal
from app.process_data import process_dataframe

logger = logging.getLogger(__name__)


# -----------------------------
# Convert SQLAlchemy row → dict
# -----------------------------
def row_to_dict(row):
    """Convert a Complaint ORM object into a plain dictionary."""
    return {
        "unique_key": row.unique_key,
        "created_date": row.created_date,
        "agency": row.agency,
        "agency_name": row.agency_name,
        "complaint_type": row.complaint_type,
        "descriptor": row.descriptor,
        "borough": row.borough,
        "latitude": row.latitude,
        "longitude": row.longitude,
    }


# -----------------------------
# DB fetch helpers
# -----------------------------
def get_complaints_since(minutes: int):
    """Return complaints created within the last N minutes."""
    logger.info(f"Fetching complaints from the last {minutes} minutes...")
    session: Session = SessionLocal()
    cutoff = datetime.now() - timedelta(minutes=minutes)

    results = (
        session.query(Complaint)
        .filter(Complaint.created_date >= cutoff)
        .all()
    )
    session.close()

    logger.info(f"Retrieved {len(results)} complaints from last {minutes} minutes.")
    return pd.DataFrame([row_to_dict(r) for r in results])


def get_complaints_between(start_minutes: int, end_minutes: int):
    """Return complaints created between two time windows."""
    logger.info(f"Fetching complaints from {end_minutes}–{start_minutes} minutes ago...")
    session: Session = SessionLocal()
    now = datetime.now()

    start = now - timedelta(minutes=start_minutes)
    end = now - timedelta(minutes=end_minutes)

    results = (
        session.query(Complaint)
        .filter(Complaint.created_date >= end)
        .filter(Complaint.created_date < start)
        .all()
    )
    session.close()

    logger.info(f"Retrieved {len(results)} complaints from {end_minutes}–{start_minutes} minutes ago.")
    return pd.DataFrame([row_to_dict(r) for r in results])


# -----------------------------
# Spike detection
# -----------------------------
def detect_spike(current_count: int, previous_count: int, multiplier: float = 1.5):
    """Return True if current_count is significantly higher than previous_count."""
    logger.debug(
        f"Detecting spike: current={current_count}, previous={previous_count}, multiplier={multiplier}"
    )

    if previous_count == 0:
        # Avoid false positives when previous window is empty
        return current_count > 5

    return current_count > previous_count * multiplier


# -----------------------------
# Main alert generation
# -----------------------------
def generate_alerts():
    """Generate alerts based on complaint spikes in total, category, and borough."""
    logger.info("Generating alerts...")
    alerts = []

    # Time windows (3 days = 4320 minutes)
    df_current = get_complaints_since(4320)
    df_previous = get_complaints_between(4320, 8640)

    if df_current.empty or df_previous.empty:
        logger.info("No alerts generated — insufficient data in one or both time windows.")
        return []

    # Process both windows (adds category, hour_of_day, etc.)
    logger.info("Processing current and previous complaint data...")
    df_current = process_dataframe(df_current)
    df_previous = process_dataframe(df_previous)

    # Total spike
    current_total = len(df_current)
    previous_total = len(df_previous)
    logger.info(f"Total complaints — current: {current_total}, previous: {previous_total}")

    if detect_spike(current_total, previous_total):
        msg = f"Total complaints spiked! Last window: {current_total}, Previous window: {previous_total}"
        logger.info(f"ALERT: {msg}")
        alerts.append(msg)

    # Category spikes
    logger.info("Checking category spikes...")
    for category in df_current["category"].unique():
        curr = len(df_current[df_current["category"] == category])
        prev = len(df_previous[df_previous["category"] == category])

        if detect_spike(curr, prev):
            msg = f"{category} complaints surged! Last window: {curr}, Previous window: {prev}"
            logger.info(f"ALERT: {msg}")
            alerts.append(msg)

    # Borough spikes
    logger.info("Checking borough spikes...")
    for borough in df_current["borough"].unique():
        curr = len(df_current[df_current["borough"] == borough])
        prev = len(df_previous[df_previous["borough"] == borough])

        if detect_spike(curr, prev):
            msg = f"{borough} complaints increased significantly! Last window: {curr}, Previous window: {prev}"
            logger.info(f"ALERT: {msg}")
            alerts.append(msg)

    logger.info(f"Alert generation complete. Total alerts: {len(alerts)}")
    return alerts
