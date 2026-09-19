from datetime import timedelta

from sqlalchemy import func
import pandas as pd
from src.app.db import Complaint


def get_current_count(session, borough, category, start_time, end_time):
    count = (
        session.query(Complaint)
        .filter(
            Complaint.borough == borough,
            Complaint.category == category,
            Complaint.created_date >= start_time,
            Complaint.created_date < end_time,
        )
        .count()
    )

    return count


def get_season(date):
    month = date.month

    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8):
        return "Summer"

    return "Fall"


def get_historical_counts(
    session,
    borough,
    category,
    start_time,
):
    historical_start = start_time - timedelta(days=365)

    rows = (
        session.query(Complaint.created_date)
        .filter(
            Complaint.borough == borough,
            Complaint.category == category,
            Complaint.created_date >= historical_start,
            Complaint.created_date < start_time,
        )
        .all()
    )

    current_season = get_season(start_time)
    current_hour = start_time.hour
    current_weekday = start_time.weekday()

    counts_by_date = {}

    for row in rows:
        created = row.created_date

        if (
            created.hour == current_hour
            and created.weekday() == current_weekday
            and get_season(created) == current_season
        ):
            date_key = created.date()
            counts_by_date[date_key] = counts_by_date.get(date_key, 0) + 1

    historical_dates = []

    current_date = historical_start.date()

    while current_date < start_time.date():
        if (
            current_date.weekday() == current_weekday
            and get_season(current_date) == current_season
        ):
            historical_dates.append(current_date)

        current_date += timedelta(days=1)

    return [
        counts_by_date.get(date, 0)
        for date in historical_dates
    ]


def calculate_threshold(counts):
    if not counts:
        return None

    return pd.Series(counts).quantile(0.95).item()


def is_unusual(
    session,
    borough,
    category,
    start_time,
    end_time,
):
    current_count = get_current_count(
        session,
        borough,
        category,
        start_time,
        end_time,
)

    historical_counts = get_historical_counts(
        session,
        borough,
        category,
        start_time,
)

    threshold = calculate_threshold(historical_counts)

    if threshold is None:
        return {
            "current_count": current_count,
            "threshold": None,
            "historical_count": len(historical_counts),
            "unusual": False
        }

    return {
        "current_count": current_count,
        "threshold": threshold,
        "historical_count": len(historical_counts),
        "unusual": current_count > threshold
    }


def evaluate_conditions(session, start_time, end_time, conditions):
    results = []

    for borough, category in conditions:
        result = is_unusual(
            session,
            borough,
            category,
            start_time,
            end_time
        )

        result.update({
            "borough": borough,
            "category": category,
            "start_time": start_time,
            "end_time": end_time
        })

        results.append(result)

    return results


def get_triggered_conditions(results):
    return [result for result in results if result.get("unusual") == True]

