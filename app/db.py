from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd

DATABASE_URL = "sqlite:///data/311.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

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

def init_db():
    Base.metadata.create_all(engine)

def save_complaints(df: pd.DataFrame):
    session = SessionLocal()

    for _, row in df.iterrows():
        unique_key = row.get("unique_key")

        # Skip if already exists
        if session.get(Complaint, unique_key):
            continue

        complaint = Complaint(
            unique_key=unique_key,
            created_date=pd.to_datetime(row.get("created_date")) if row.get("created_date") else None,
            agency=row.get("agency"),
            agency_name=row.get("agency_name"),
            complaint_type=row.get("complaint_type"),
            descriptor=row.get("descriptor"),
            borough=row.get("borough"),
            latitude=float(row.get("latitude")) if row.get("latitude") else None,
            longitude=float(row.get("longitude")) if row.get("longitude") else None,
        )

        session.add(complaint)

    session.commit()
    session.close()
