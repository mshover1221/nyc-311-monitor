from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import func

from src.app.db import SessionLocal, Complaint
from src.alerts.detector import get_season


session = SessionLocal()

rows = (
    session.query(
        func.date(Complaint.created_date).label("date"),
        func.count(Complaint.unique_key).label("count"),
    )
    .filter(
        Complaint.borough == "BROOKLYN",
        Complaint.category == "Noise",
        func.strftime("%H", Complaint.created_date) == "22",
    )
    .group_by(func.date(Complaint.created_date))
    .all()
)

counts_by_date = {
    datetime.fromisoformat(row.date).date(): row.count
    for row in rows
}


def get_historical_counts(
    counts_by_date,
    start_time,
    historical_start,
):
    current_season = get_season(start_time)
    current_weekday = start_time.weekday()
    historical_counts = []

    current_date = historical_start.date()

    while current_date < start_time.date():
        if (
            current_date.weekday() == current_weekday
            and get_season(current_date) == current_season
        ):
            historical_counts.append(
                counts_by_date.get(current_date, 0)
            )

        current_date += timedelta(days=1)

    return historical_counts


def evaluate_model(
    counts_by_date,
    start_time,
    historical_start,
    min_nonzero_history,
):
    current_count = counts_by_date.get(start_time.date(), 0)

    historical_counts = get_historical_counts(
        counts_by_date,
        start_time,
        historical_start,
    )

    nonzero_historical_count = sum(
        count > 0 for count in historical_counts
    )

    if nonzero_historical_count < min_nonzero_history:
        return {
            "current_count": current_count,
            "threshold": None,
            "unusual": False,
            "historical_count": len(historical_counts),
            "nonzero_historical_count": nonzero_historical_count,
        }

    threshold = (
        pd.Series(historical_counts)
        .quantile(0.95)
        .item()
    )

    return {
        "current_count": current_count,
        "threshold": threshold,
        "unusual": current_count > threshold,
        "historical_count": len(historical_counts),
        "nonzero_historical_count": nonzero_historical_count,
    }


# ---------------------------------------------------------
# Minimum-history comparison
# ---------------------------------------------------------

start_date = datetime(2026, 6, 1)
end_date = datetime(2026, 8, 30)

min_history_values = [3, 5, 8, 10, 12]

alert_totals = {
    min_history: 0
    for min_history in min_history_values
}

eligible_totals = {
    min_history: 0
    for min_history in min_history_values
}

different_dates = set()

current_date = start_date

while current_date < end_date:
    start_time = current_date.replace(hour=22)

    results = {}

    for min_history in min_history_values:
        results[min_history] = evaluate_model(
            counts_by_date,
            start_time,
            start_time - timedelta(days=365),
            min_history,
        )

        result = results[min_history]

        if result["threshold"] is not None:
            eligible_totals[min_history] += 1

        if result["unusual"]:
            alert_totals[min_history] += 1

    decisions = {
        min_history: results[min_history]["unusual"]
        for min_history in min_history_values
    }

    if len(set(decisions.values())) > 1:
        different_dates.add(current_date.date())

    current_date += timedelta(days=1)


print()
print("=" * 70)
print("MINIMUM HISTORY EXPERIMENT")
print("=" * 70)

print()
print("Evaluation period: 2026-06-01 through 2026-08-29")
print("Lookback: 365 days")
print("Baseline: same weekday + hour + season")
print("Threshold: 95th percentile")
print()

for min_history in min_history_values:
    print(
        "Minimum nonzero history:",
        min_history,
        "| Eligible:",
        eligible_totals[min_history],
        "| Alerts:",
        alert_totals[min_history],
    )

print()
print(
    "Dates where minimum-history settings disagree:",
    len(different_dates),
)

print()
print("Different dates:")

for date in sorted(different_dates):
    print(date)

print()
print("=" * 70)
print("DECISION DETAILS")
print("=" * 70)

# Print the dates where at least one setting alerts
# and another setting does not.
current_date = start_date

while current_date < end_date:
    start_time = current_date.replace(hour=22)

    results = {
        min_history: evaluate_model(
            counts_by_date,
            start_time,
            start_time - timedelta(days=365),
            min_history,
        )
        for min_history in min_history_values
    }

    decisions = {
        min_history: results[min_history]["unusual"]
        for min_history in min_history_values
    }

    if len(set(decisions.values())) > 1:
        print()
        print("Date:", current_date.date())
        print(
            "Current count:",
            results[3]["current_count"],
        )

        for min_history in min_history_values:
            result = results[min_history]

            print(
                "Min",
                min_history,
                "| historical:",
                result["historical_count"],
                "| nonzero:",
                result["nonzero_historical_count"],
                "| threshold:",
                result["threshold"],
                "| alert:",
                result["unusual"],
            )

    current_date += timedelta(days=1)


session.close()