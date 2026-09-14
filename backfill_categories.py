"""
One-time migration script to populate the category column
for existing complaints in the SQLite database.

Uses the same categorization logic as process_data.py
so historical records match newly ingested records.

Run this script after adding the category column to the
complaints table. It is not part of the normal application pipeline.
"""

from src.app.db import SessionLocal, Complaint
from src.app.process_data import categorize_complaint


BATCH_SIZE = 5000

session = SessionLocal()

try:
    complaints = session.query(Complaint).yield_per(BATCH_SIZE)

    updated_count = 0

    for complaint in complaints:
        complaint.category = categorize_complaint(
            complaint.complaint_type,
            complaint.descriptor
        )

        updated_count += 1

        if updated_count % BATCH_SIZE == 0:
            session.commit()
            print(f"Updated {updated_count} complaints...")

    session.commit()

    print(f"Finished. Updated {updated_count} complaints.")

finally:
    session.close()