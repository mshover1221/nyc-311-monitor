import requests
import pandas as pd
import logging
logger = logging.getLogger(__name__)

BASE_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

def fetch_311_data(limit=1000):
    logger.info(f"Fetching 311 data from NYC API (limit={limit})...")

    params = {
        "$limit": limit,
        "$order": "created_date DESC"
    }

    try:
        response = requests.get(BASE_URL, params=params)
        logger.info(f"API responded with status {response.status_code}")
    except Exception as e:
        logger.exception(f"Request to NYC API failed: {e}")
        raise

    if response.status_code != 200:
        logger.error(f"Unexpected status code: {response.status_code}")
        raise Exception(f"Error fetching data: {response.status_code}")

    try:
        data = response.json()
        logger.info(f"Parsed JSON successfully. Raw record count: {len(data)}")
    except Exception as e:
        logger.exception(f"Failed to parse JSON response: {e}")
        raise

    df = pd.DataFrame(data)
    logger.info(f"Converted JSON to DataFrame with shape {df.shape}")

    return df

