"""Orchestrate the NYC 311 fetch, processing, persistence, and alert pipeline."""

from dotenv import load_dotenv
load_dotenv()

import argparse
import logging
from datetime import datetime, timedelta

from src.app.db import init_db, save_complaints
from src.app.fetch_data import fetch_311_data
from src.app.process_data import process_dataframe
from src.app.alerts import generate_alerts
from src.app.backfill import backfill

logger = logging.getLogger(__name__)


def main():
    """Entry point used by the scheduler."""
    run_full_pipeline()


def run_full_pipeline():
    """Fetch, process, save complaints, then generate alerts."""
    now = datetime.now()
    start = now - timedelta(minutes=15)

    logger.info(f"Fetching data from {start} to {now}...")
    df = fetch_311_data(start, now)

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
    parser.add_argument("--backfill", type=int, metavar="DAYS")
    args = parser.parse_args()

    print("Initializing database...")
    init_db()

    if args.backfill:
        logger.info(f"Running {args.backfill}-day backfill...")

        windows = backfill(args.backfill)
        failed_windows = []

        for window_start, window_end in windows:
            try:
                logger.info(
                    f"Fetching window: {window_start} → {window_end}"
                )

                df = fetch_311_data(window_start, window_end)

                logger.info("Processing window...")
                df = process_dataframe(df)

                logger.info("Saving window...")
                save_complaints(df)

            except Exception:
                logger.exception(
                    f"Backfill window failed: {window_start} → {window_end}"
                )
                failed_windows.append((window_start, window_end))

        logger.info("Backfill complete!")

        if failed_windows:
            logger.warning("Failed windows:")
            for window_start, window_end in failed_windows:
                logger.warning(f"{window_start} → {window_end}")

    elif args.run_alerts:
        run_alerts_only()

    else:
        run_full_pipeline()

