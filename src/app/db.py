"""Database setup and persistence for NYC 311 complaint data."""

import pandas as pd

from sqlalchemy import create_engine, Column, String, DateTime, Float
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
    created_date = Column(DateTime)
    agency = Column(String)
    agency_name = Column(String)
    complaint_type = Column(String)
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

