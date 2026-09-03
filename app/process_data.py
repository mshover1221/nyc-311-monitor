import pandas as pd

# Simple category mapping for now — we can expand this later
CATEGORY_MAP = {
    "Noise": ["Noise", "Loud Music", "Party", "Banging", "Construction"],
    "Heat/Hot Water": ["Heat", "Hot Water"],
    "Rodents": ["Rodent", "Mouse", "Rat"],
    "Water System": ["Leak", "Water", "Flood"],
    "Sanitation": ["Garbage", "Trash", "Litter"],
    "Parking": ["Blocked Driveway", "Illegal Parking"],
}

def categorize_complaint(complaint_type, descriptor):
    text = f"{complaint_type} {descriptor}".lower()

    for category, keywords in CATEGORY_MAP.items():
        for kw in keywords:
            if kw.lower() in text:
                return category

    return "Other"

# -----------------------------
# Improved hour features
# -----------------------------

def time_bucket(h):
    if h is None:
        return "Unknown"
    if h < 6:
        return "Overnight"
    if h < 12:
        return "Morning"
    if h < 18:
        return "Afternoon"
    if h < 22:
        return "Evening"
    return "Late Night"

def hour_label(h):
    if h is None:
        return "Unknown"
    if 0 <= h < 6:
        return "Overnight (12 AM – 6 AM)"
    if 6 <= h < 12:
        return "Morning (6 AM – 12 PM)"
    if 12 <= h < 18:
        return "Afternoon (12 PM – 6 PM)"
    if 18 <= h < 22:
        return "Evening (6 PM – 10 PM)"
    return "Late Night (10 PM – 12 AM)"

def process_dataframe(df: pd.DataFrame):
    # Ensure created_date is a datetime
    df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")

    # Normalize borough
    df["borough"] = df["borough"].str.upper().fillna("UNKNOWN")

    # Add numeric hour
    df["hour_of_day"] = df["created_date"].dt.hour

    # Add human-friendly time bucket
    df["time_bucket"] = df["hour_of_day"].apply(time_bucket)

    # Add fully descriptive label
    df["hour_label"] = df["hour_of_day"].apply(hour_label)

    # Add day-of-week features
    df["day_of_week"] = df["created_date"].dt.day_name()
    df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"])

    # Add category
    df["category"] = df.apply(
        lambda row: categorize_complaint(row.get("complaint_type", ""), row.get("descriptor", "")),
        axis=1
    )

    return df

