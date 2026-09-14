"""Explore hourly complaint patterns used to develop alert baselines."""
from datetime import date, timedelta
import statistics

from sqlalchemy import func

from src.app.db import SessionLocal, Complaint


session = SessionLocal()

start_date = date(2025, 9, 13)
end_date = date(2026, 9, 5)

saturdays = []

current_date = start_date

while current_date <= end_date:
    saturdays.append(current_date)
    current_date += timedelta(days=7)

rows = (
    session.query(
        func.date(Complaint.created_date).label("date"),
        func.count(Complaint.unique_key).label("count"),
    )
    .filter(Complaint.borough == "QUEENS")
    .filter(Complaint.complaint_type.like("Heat/Hot Water%"))
    .filter(func.strftime("%w", Complaint.created_date) == "6")
    .filter(func.strftime("%H", Complaint.created_date) == "22")
    .group_by(
        func.date(Complaint.created_date),
    )
    .order_by(
        func.date(Complaint.created_date),
    )
    .all()
)

counts_by_date = {row.date: row.count for row in rows}

counts = [counts_by_date.get(str(current_date), 0) for current_date in saturdays]

print("90th percentile:", statistics.quantiles(counts, n=100)[89])
print("95th percentile:", statistics.quantiles(counts, n=100)[94])
print("99th percentile:", statistics.quantiles(counts, n=100)[98])

print("Observations:", len(counts))
print("Minimum:", min(counts))
print("Maximum:", max(counts))
print("Average:", sum(counts) / len(counts))

for current_date, count in zip(saturdays, counts):
    print(current_date, count)

session.close()

