import pandas as pd
from app.process_data import process_dataframe
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db import Complaint, SessionLocal
import logging
logger = logging.getLogger(__name__)


# -----------------------------
# Convert SQLAlchemy row → dict
# -----------------------------
def row_to_dict(row):
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
# Helper: fetch complaints from DB
# -----------------------------

def get_complaints_since(minutes: int):
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
# Spike detection logic
# -----------------------------

def detect_spike(current_count: int, previous_count: int, multiplier: float = 1.5):
    logger.debug(f"Detecting spike: current={current_count}, previous={previous_count}, multiplier={multiplier}")
    if previous_count == 0:
        return current_count > 5  # avoid false positives
    return current_count > previous_count * multiplier


# -----------------------------
# Main alert function
# -----------------------------

def generate_alerts():
    logger.info("Generating alerts...")

    alerts = []

    # Last 60 minutes
    df_current = get_complaints_since(60)
    df_previous = get_complaints_between(60, 120)

    if df_current.empty or df_previous.empty:
        logger.info("No alerts generated — insufficient data in one or both time windows.")
        return []

    # RE-PROCESS DB DATA (adds category, hour_of_day, etc.)
    logger.info("Processing current and previous complaint data...")
    df_current = process_dataframe(df_current)
    df_previous = process_dataframe(df_previous)

    current_total = len(df_current)
    previous_total = len(df_previous)

    logger.info(f"Total complaints — current: {current_total}, previous: {previous_total}")

    # Spike in total complaints
    if detect_spike(current_total, previous_total):
        alert_msg = (
            f"Total complaints spiked! Last hour: {current_total}, Previous hour: {previous_total}"
        )
        logger.info(f"ALERT: {alert_msg}")
        alerts.append(alert_msg)

    # Category spikes
    logger.info("Checking category spikes...")
    for category in df_current["category"].unique():
        curr_cat_count = len(df_current[df_current["category"] == category])
        prev_cat_count = len(df_previous[df_previous["category"] == category])

        if detect_spike(curr_cat_count, prev_cat_count):
            alert_msg = (
                f"{category} complaints surged! Last hour: {curr_cat_count}, Previous hour: {prev_cat_count}"
            )
            logger.info(f"ALERT: {alert_msg}")
            alerts.append(alert_msg)

    # Borough spikes
    logger.info("Checking borough spikes...")
    for borough in df_current["borough"].unique():
        curr_boro_count = len(df_current[df_current["borough"] == borough])
        prev_boro_count = len(df_previous[df_previous["borough"] == borough])

        if detect_spike(curr_boro_count, prev_boro_count):
            alert_msg = (
                f"{borough} complaints increased significantly! Last hour: {curr_boro_count}, Previous hour: {prev_boro_count}"
            )
            logger.info(f"ALERT: {alert_msg}")
            alerts.append(alert_msg)

    logger.info(f"Alert generation complete. Total alerts: {len(alerts)}")
    return alerts


