from app.fetch_data import fetch_311_data
from app.db import init_db, save_complaints
from app.process_data import process_dataframe
from app.alerts import generate_alerts
import logging
logger = logging.getLogger(__name__)

def main():
    print("Fetching data...")
    df = fetch_311_data()

    print("Processing data...")
    df = process_dataframe(df)

    print("Saving complaints...")
    save_complaints(df)

    print("Generating alerts...")
    alerts = generate_alerts()

    for alert in alerts:
        print("ALERT:", alert)

    print("Done!")

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    main()




