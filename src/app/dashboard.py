import math
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from src.app.db import (
    SessionLocal,
    get_category_counts,
    get_complaint_count,
    get_daily_complaint_counts,
    get_latest_complaint_date,
    get_total_complaints,
)

from src.alerts.detector import is_unusual


st.set_page_config(
    page_title="NYC 311 Monitor",
    page_icon="🏙️",
    layout="wide",
)

st.title("NYC 311 Monitor")
st.caption("Historical complaint monitoring and contextual anomaly investigation")


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------

count = get_total_complaints()

now = datetime.now()

current_hour = now.replace(
    minute=0,
    second=0,
    microsecond=0,
)

start_time = current_hour - timedelta(hours=1)
end_time = current_hour

recent_count = get_complaint_count(start_time, end_time)
latest_data = get_latest_complaint_date()

metric_1, metric_2, metric_3 = st.columns(3)

with metric_1:
    st.metric("Total complaints", f"{count:,}")

with metric_2:
    st.metric("Most recent completed hour", f"{recent_count:,}")

with metric_3:
    st.metric(
        "Last data received",
        str(latest_data) if latest_data else "No data",
    )


st.divider()


# ---------------------------------------------------------------------------
# Alert Investigation
# ---------------------------------------------------------------------------

st.subheader("Alert Investigation")
st.caption(
    "Compare a selected hour against historically comparable periods."
)

investigation_col1, investigation_col2, investigation_col3, investigation_col4 = (
    st.columns(4)
)

with investigation_col1:
    investigation_borough = st.selectbox(
        "Borough",
        ["BRONX", "BROOKLYN", "MANHATTAN", "QUEENS", "STATEN ISLAND"],
    )

with investigation_col2:
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


with investigation_col3:
    selected_hour = st.selectbox(
        "Hour",
        list(range(24)),
        format_func=format_hour,
    )

with investigation_col4:
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


result_col1, result_col2, result_col3, result_col4 = st.columns(4)

with result_col1:
    st.metric(
        "Current complaints",
        investigation_result["current_count"],
    )

with result_col2:
    threshold = investigation_result["threshold"]

    st.metric(
        "Historical threshold",
        f"{threshold:.1f}" if threshold is not None else "N/A",
    )

with result_col3:
    st.metric(
        "Comparable periods",
        investigation_result["historical_count"],
    )

with result_col4:
    st.metric(
        "Non-zero periods",
        investigation_result["nonzero_historical_count"],
    )

if investigation_result["unusual"]:
    st.success("Unusual activity detected")
else:
    st.info("No unusual activity detected")


st.divider()


# ---------------------------------------------------------------------------
# Historical Complaint Trends
# ---------------------------------------------------------------------------

st.subheader("Historical Complaint Trends")
st.caption("Explore complaint volume over time and by category.")

trend_col1, trend_col2, trend_col3 = st.columns(3)

with trend_col1:
    borough = st.selectbox(
        "Borough",
        ["All", "BRONX", "BROOKLYN", "MANHATTAN", "QUEENS", "STATEN ISLAND"],
    )

with trend_col2:
    historical_start_date = st.date_input(
        "Start date",
        value=datetime(2026, 9, 1),
    )

with trend_col3:
    historical_end_date = st.date_input(
        "End date",
        value=datetime(2026, 9, 7),
    )

selected_borough = None if borough == "All" else borough

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


chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("#### Daily complaint volume")

    if not chart_data.empty:
        fig = px.line(
            chart_data,
            x="date",
            y="complaints",
            markers=True,
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

        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title=None,
            yaxis_title="Complaints",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )
    else:
        st.info("No complaint data available for this period.")


with chart_col2:
    st.markdown("#### Complaints by category")

    if not category_data.empty:
        st.bar_chart(
            category_data,
            x="category",
            y="complaints",
        )
    else:
        st.info("No complaint data available for this period.")
