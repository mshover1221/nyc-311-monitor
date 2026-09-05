from dotenv import load_dotenv
load_dotenv()

import argparse
import logging

from src.app.db import init_db, save_complaints
from src.app.fetch_data import fetch_311_data
from src.app.process_data import process_dataframe
from src.app.alerts import generate_alerts

logger = logging.getLogger(__name__)


def main():
    """Entry point used by the scheduler."""
    run_full_pipeline()


def run_full_pipeline():
    """Fetch, process, save complaints, then generate alerts."""
    logger.info("Fetching data...")
    df = fetch_311_data()

    logger.info("Processing data...")
    df = process_dataframe(df)

    logger.info("Saving complaints...")
    save_complaints(df)

    logger.info("Generating alerts...")
    alerts = generate_alerts()

    for alert in alerts:
        logger.info(f"ALERT: {alert}")

    logger.info("Done!")


def run_alerts_only():
    """Generate alerts using existing DB data."""
    logger.info("Generating alerts from existing DB data...")
    alerts = generate_alerts()

    for alert in alerts:
        logger.info(f"ALERT: {alert}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-alerts", action="store_true")
    args = parser.parse_args()

    print("Initializing database...")
    init_db()

    if args.run_alerts:
        run_alerts_only()
    else:
        run_full_pipeline()
