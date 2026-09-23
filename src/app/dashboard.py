import streamlit as st

import math
import pandas as pd
import plotly.express as px

from datetime import datetime, timedelta

from src.app.db import (
    SessionLocal,
    get_total_complaints,
    get_complaint_count,
    get_latest_complaint_date,
    get_daily_complaint_counts,
    get_category_counts,
)

from src.alerts.detector import is_unusual


st.title("NYC 311 Monitor")

st.write("Dashboard is connected.")

count = get_total_complaints()

st.write(f"Total complaints: {count:,}")

now = datetime.now()

current_hour = now.replace(
    minute=0,
    second=0,
    microsecond=0,
)

start_time = current_hour - timedelta(hours=1)
end_time = current_hour

recent_count = get_complaint_count(start_time, end_time)

st.write(
    f"Complaints in the most recent completed hour: "
    f"{recent_count:,}"
)

latest_data = get_latest_complaint_date()

st.write(f"Last data received: {latest_data}")


st.subheader("Alert Investigation")

investigation_borough = st.selectbox(
    "Investigation Borough",
    ["BRONX", "BROOKLYN", "MANHATTAN", "QUEENS", "STATEN ISLAND"],
)

category = st.selectbox(
    "Category",
    [
        "Noise",
        "Heat/Hot Water",
        "Rodents",
        "Water System",
        "Sanitation",
        "Parking",
        "Other",
    ],
)


def format_hour(hour):
    return datetime(2000, 1, 1, hour).strftime("%I %p").lstrip("0")


hour_options = list(range(24))

selected_hour = st.selectbox(
    "Hour",
    hour_options,
    format_func=format_hour,
)

investigation_date = st.date_input(
    "Investigation date",
    value=datetime(2026, 6, 20),
)

investigation_start = datetime.combine(
    investigation_date,
    datetime.min.time(),
).replace(hour=selected_hour)

investigation_end = investigation_start + timedelta(hours=1)

session = SessionLocal()

try:
    investigation_result = is_unusual(
        session,
        investigation_borough,
        category,
        investigation_start,
        investigation_end,
    )
finally:
    session.close()

st.write(
    f"Current complaints: "
    f"{investigation_result['current_count']}"
)

if investigation_result["threshold"] is not None:
    st.write(
        f"Historical threshold: "
        f"{investigation_result['threshold']:.1f}"
    )
else:
    st.write("Historical threshold: Not enough historical data")

st.write(
    f"Comparable historical periods: "
    f"{investigation_result['historical_count']}"
)

st.write(
    f"Non-zero historical periods: "
    f"{investigation_result['nonzero_historical_count']}"
)

if investigation_result["unusual"]:
    st.success("Unusual activity detected")
else:
    st.info("No unusual activity detected")


st.subheader("Historical Complaint Trends")

borough = st.selectbox(
    "Borough",
    ["All", "BRONX", "BROOKLYN", "MANHATTAN", "QUEENS", "STATEN ISLAND"],
)

selected_borough = None if borough == "All" else borough

historical_start_date = st.date_input(
    "Start date",
    value=datetime(2026, 9, 1),
)

historical_end_date = st.date_input(
    "End date",
    value=datetime(2026, 9, 7),
)

historical_start = datetime.combine(
    historical_start_date,
    datetime.min.time(),
)

historical_end = datetime.combine(
    historical_end_date + timedelta(days=1),
    datetime.min.time(),
)

daily_counts = get_daily_complaint_counts(
    historical_start,
    historical_end,
    selected_borough,
)

category_counts = get_category_counts(
    historical_start,
    historical_end,
    selected_borough,
)

chart_data = pd.DataFrame(
    daily_counts,
    columns=["date", "complaints"],
)

category_data = pd.DataFrame(
    category_counts,
    columns=["category", "complaints"],
)

fig = px.line(
    chart_data,
    x="date",
    y="complaints",
)

min_complaints = chart_data["complaints"].min()
max_complaints = chart_data["complaints"].max()

axis_min = math.floor(min_complaints / 500) * 500
axis_max = math.ceil(max_complaints / 500) * 500

fig.update_yaxes(
    range=[axis_min, axis_max],
    tickmode="linear",
    tick0=axis_min,
    dtick=500,
    showline=True,
)

fig.add_hline(y=axis_min)
fig.add_hline(y=axis_max)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Complaints by Category")

st.bar_chart(
    category_data,
    x="category",
    y="complaints",
)
