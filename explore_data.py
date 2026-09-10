"""Explore NYC 311 complaint volume and time-of-week patterns."""

import requests
import pandas as pd


URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

params = {
    "$limit": 100000,
    "$where": (
        "created_date >= '2026-07-14T00:00:00' "
        "AND created_date < '2026-09-08T00:00:00'"
    ),
    "$order": "created_date ASC",
}

response = requests.get(URL, params=params)
print("Status:", response.status_code)

data = response.json()
df = pd.DataFrame(data)

df["created_date"] = pd.to_datetime(df["created_date"])

print("Rows:", len(df))
print("Range:", df["created_date"].min(), "to", df["created_date"].max())

print("\nComplaints by day:")
print(
    df["created_date"]
    .dt.day_name()
    .value_counts()
    .sort_index()
)

noise = df[df["complaint_type"].str.contains("Noise", case=False, na=False)]

print("\nNoise complaints by day:")
print(
    noise["created_date"]
    .dt.day_name()
    .value_counts()
    .sort_index()
)

print("\nNoise complaints by day and hour:")
print(
    noise.groupby(
        [
            noise["created_date"].dt.day_name(),
            noise["created_date"].dt.hour,
        ]
    )
    .size()
    .unstack(fill_value=0)
)

