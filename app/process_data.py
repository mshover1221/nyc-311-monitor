import logging
import pandas as pd

logger = logging.getLogger(__name__)

# Category mapping — expandable later
CATEGORY_MAP = {
    "Noise": ["Noise", "Loud Music", "Party", "Banging", "Construction"],
    "Heat/Hot Water": ["Heat", "Hot Water"],
    "Rodents": ["Rodent", "Mouse", "Rat"],
    "Water System": ["Leak", "Water", "Flood"],
    "Sanitation": ["Garbage", "Trash", "Litter"],
    "Parking": ["Blocked Driveway", "Illegal Parking"],
}


def categorize_complaint(complaint_type, descriptor):
    """Assign a category based on complaint_type + descriptor text."""
    text = f"{complaint_type} {descriptor}".lower()

    for category, keywords in CATEGORY_MAP.items():
        for kw in keywords:
            if kw.lower() in text:
                return category

    return "Other"


def time_bucket(hour):
    """Return a simple time-of-day bucket."""
    if hour is None:
        return "Unknown"
    if hour < 6:
        return "Overnight"
    if hour < 12:
        return "Morning"
    if hour < 18:
        return "Afternoon"
    if hour < 22:
        return "Evening"
    return "Late Night"


def hour_label(hour):
    """Return a human-friendly time-of-day label."""
    if hour is None:
        return "Unknown"
    if 0 <= hour < 6:
        return "Overnight (12 AM – 6 AM)"
    if 6 <= hour < 12:
        return "Morning (6 AM – 12 PM)"
    if 12 <= hour < 18:
        return "Afternoon (12 PM – 6 PM)"
    if 18 <= hour < 22:
        return "Evening (6 PM – 10 PM)"
    return "Late Night (10 PM – 12 AM)"


def process_dataframe(df: pd.DataFrame):
    """Clean, enrich, and categorize NYC 311 complaint data."""
    logger.info("Starting data processing...")
    logger.info(f"Initial DataFrame shape: {df.shape}")

    try:
        # Convert created_date to datetime
        df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
        logger.info("Converted created_date to datetime.")

        # Normalize borough
        df["borough"] = df["borough"].str.upper().fillna("UNKNOWN")
        logger.info("Normalized borough values.")

        # Hour-of-day features
        df["hour_of_day"] = df["created_date"].dt.hour
        df["time_bucket"] = df["hour_of_day"].apply(time_bucket)
        df["hour_label"] = df["hour_of_day"].apply(hour_label)
        logger.info("Added hour_of_day, time_bucket, and hour_label features.")

        # Day-of-week features
        df["day_of_week"] = df["created_date"].dt.day_name()
        df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"])
        logger.info("Added day_of_week and is_weekend features.")

        # Complaint category
        df["category"] = df.apply(
            lambda row: categorize_complaint(
                row.get("complaint_type", ""),
                row.get("descriptor", "")
            ),
            axis=1
        )
        logger.info("Assigned categories to complaints.")

    except Exception as e:
        logger.exception(f"Error during data processing: {e}")
        raise

    logger.info(f"Finished processing. Final DataFrame shape: {df.shape}")
    return df
