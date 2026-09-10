"""Fetch NYC 311 data for specific datetime windows with retry handling."""

import logging
import requests
import pandas as pd
import time

logger = logging.getLogger(__name__)

BASE_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

EXPECTED_COLUMNS = [
    "unique_key",
    "created_date",
    "closed_date",
    "agency",
    "agency_name",
    "complaint_type",
    "descriptor",
    "borough",
    "latitude",
    "longitude",
]



def fetch_311_data(start_datetime, end_datetime, limit=50000, max_retries=3):
    """Fetch NYC 311 complaints for a specific datetime window."""
    logger.info(
        f"Fetching 311 data from {start_datetime} to {end_datetime} "
        f"(limit={limit})..."
    )

    params = {
        "$limit": limit,
        "$order": "created_date DESC",
        "$where": (
            f"created_date >= '{start_datetime.isoformat()}' "
            f"AND created_date < '{end_datetime.isoformat()}'"
        )
    }

    # Make API request
    for attempt in range(max_retries + 1):
        response = requests.get(BASE_URL, params=params)
        logger.info(f"API responded with status {response.status_code}")

        if response.status_code == 200:
            break

        if response.status_code not in RETRYABLE_STATUS_CODES:
            raise Exception(f"Error fetching data: {response.status_code}")
        
        if attempt < max_retries:
            delay = 2 ** attempt
            logger.warning(
                f"Request failed with status {response.status_code}. "
                f"Retrying in {delay} seconds..."
            )
            time.sleep(delay)

    if response.status_code != 200:
        raise Exception(
            f"Request failed after {max_retries} retries. "
            f"Final status code: {response.status_code}"
        )


    # Parse JSON
    try:
        data = response.json()
        logger.info(f"Parsed JSON successfully. Raw record count: {len(data)}")
    except Exception as e:
        logger.exception(f"Failed to parse JSON response: {e}")
        raise

    # Convert to DataFrame
    df = pd.DataFrame(data, columns=EXPECTED_COLUMNS)
    logger.info(f"Converted JSON to DataFrame with shape {df.shape}")

    return df
    
