"""Database setup and persistence for NYC 311 complaint data."""

import pandas as pd

from sqlalchemy import create_engine, Column, String, DateTime, Float, func
from sqlalchemy.orm import declarative_base, sessionmaker


# ----------------------------------
# Database setup
# ----------------------------------

DATABASE_URL = "sqlite:///data/311.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


# ----------------------------------
# ORM Model
# ----------------------------------

class Complaint(Base):
    __tablename__ = "complaints"

    unique_key = Column(String, primary_key=True)
    created_date = Column(DateTime, index=True)
    agency = Column(String)
    agency_name = Column(String)
    complaint_type = Column(String)
    category = Column(String)
    descriptor = Column(String)
    borough = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)


# ----------------------------------
# DB Initialization
# ----------------------------------

def init_db():
    """Create database tables if they do not already exist."""
    Base.metadata.create_all(engine)


# ----------------------------------
# Save complaints
# ----------------------------------

def save_complaints(df: pd.DataFrame):
    """
    Insert new complaints into the database.

    Existing complaints are skipped using unique_key.
    This function is responsible only for persistence.
    """

    session = SessionLocal()
    inserted_count = 0

    try:
        for _, row in df.iterrows():
            unique_key = row.get("unique_key")

            if not unique_key:
                continue

            # Skip duplicates
            if session.get(Complaint, unique_key):
                continue

            complaint = Complaint(
                unique_key=unique_key,
                created_date=(
                    pd.to_datetime(row.get("created_date"))
                    if row.get("created_date")
                    else None
                ),
                agency=row.get("agency"),
                agency_name=row.get("agency_name"),
                complaint_type=row.get("complaint_type"),
                category=row.get("category"),
                descriptor=row.get("descriptor"),
                borough=row.get("borough"),
                latitude=(
                    float(row.get("latitude"))
                    if row.get("latitude") not in (None, "")
                    else None
                ),
                longitude=(
                    float(row.get("longitude"))
                    if row.get("longitude") not in (None, "")
                    else None
                ),
            )

            session.add(complaint)
            inserted_count += 1

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

    return inserted_count


# ----------------------------------
# Load complaints
# ----------------------------------

def load_complaints():
    """Return all complaints in the database as a DataFrame."""

    session = SessionLocal()

    try:
        rows = session.query(Complaint).all()

        data = [
            {
                "unique_key": r.unique_key,
                "created_date": r.created_date,
                "agency": r.agency,
                "agency_name": r.agency_name,
                "complaint_type": r.complaint_type,
                "descriptor": r.descriptor,
                "borough": r.borough,
                "latitude": r.latitude,
                "longitude": r.longitude,
            }
            for r in rows
        ]

        return pd.DataFrame(data)

    finally:
        session.close()


def get_total_complaints():
    """Return the count of total complaints"""

    session = SessionLocal()

    try:
        count = session.query(Complaint).count()

        return count

    finally:
        session.close()


def get_complaint_count(start_time, end_time):
    """Get complaint count for a specific date range."""

    session = SessionLocal()

    try:
        count_range = (
            session.query(Complaint)
            .filter(
                Complaint.created_date >= start_time,
                Complaint.created_date < end_time,
            )
            .count()
        )

        return count_range

    finally:
        session.close()


def get_latest_complaint_date():
    """Get the timestamp of the most recent complaint in the database."""

    session = SessionLocal()

    try:
        latest_timestamp = (
            session.query(Complaint.created_date)
            .order_by(Complaint.created_date.desc())
            .first()
        )

        return latest_timestamp[0] if latest_timestamp else None

    finally:
        session.close()



def get_daily_complaint_counts(start_time, end_time, borough=None):
    """Get the number of complaints for each day in a date range."""

    session = SessionLocal()

    try:
        filters = [
            Complaint.created_date >= start_time,
            Complaint.created_date < end_time,
        ]

        if borough:
            filters.append(Complaint.borough == borough)

        daily_counts = (
            session.query(
                func.date(Complaint.created_date),
                func.count(Complaint.unique_key),
            )
            .filter(*filters)
            .group_by(func.date(Complaint.created_date))
            .order_by(func.date(Complaint.created_date))
        )

        return daily_counts.all()

    finally:
        session.close()



def get_category_counts(start_time, end_time, borough=None):
    """Get complaint counts by category for a date range."""

    session = SessionLocal()

    try:
        filters = [
            Complaint.created_date >= start_time,
            Complaint.created_date < end_time,
        ]

        if borough:
            filters.append(Complaint.borough == borough)

        category_counts = (
            session.query(
                Complaint.category,
                func.count(Complaint.unique_key),
            )
            .filter(*filters)
            .group_by(Complaint.category)
            .order_by(func.count(Complaint.unique_key).desc())
        )

        return category_counts.all()

    finally:
        session.close()
