import streamlit as st

import math
import pandas as pd
import plotly.express as px

from datetime import datetime, timedelta

from src.app.db import (
    get_total_complaints,
    get_complaint_count,
    get_latest_complaint_date,
    get_daily_complaint_counts,
    get_category_counts,
)

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

st.write(f"Complaints in the most recent completed hour: {recent_count:,}")

latest_data = get_latest_complaint_date()

st.write(f"Last data received: {latest_data}")


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
)

category_counts = get_category_counts(
    historical_start,
    historical_end,
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
