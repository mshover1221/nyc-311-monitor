"""Explore hourly complaint patterns used to develop alert baselines."""

from sqlalchemy import func

from src.app.db import SessionLocal, Complaint


session = SessionLocal()

rows = (
    session.query(
        func.date(Complaint.created_date).label("date"),
        func.strftime("%H", Complaint.created_date).label("hour"),
        func.count(Complaint.unique_key).label("count"),
    )
    .filter(Complaint.borough == "BROOKLYN")
    .filter(Complaint.complaint_type.like("Noise%"))
    .group_by(
        func.date(Complaint.created_date),
        func.strftime("%H", Complaint.created_date),
    )
    .order_by(
        func.date(Complaint.created_date),
        func.strftime("%H", Complaint.created_date),
    )
    .all()
)

for row in rows:
    print(row)

session.close()

