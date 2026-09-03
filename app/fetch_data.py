import requests
import pandas as pd

BASE_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

def fetch_311_data(limit=1000):
    params = {
        "$limit": limit,
        "$order": "created_date DESC"
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code}")

    data = response.json()
    df = pd.DataFrame(data)

    return df
