from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
from run import run_ingestion, run_alerts_only
from logging_config import setup_logging
import logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = BlockingScheduler()

def job_wrapper(job):
    logger.info("Starting scheduled run...")
    try:
        job()
        logger.info("Run completed successfully.")
    except Exception as e:
        logger.exception(f"Error during scheduled run: {e}")

# Schedule job to run immediately, then every 15 minutes
def alert_job(now=None):
    """Evaluate the previous completed clock hour."""
    if now is None:
        now = datetime.now()
    end_time = now.replace(minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(hours=1)

    run_alerts_only(start_time, end_time)

scheduler.add_job(
    job_wrapper,
    'interval',
    minutes=15,
    next_run_time=datetime.now(),
    kwargs={"job": run_ingestion}
)

scheduler.add_job(
    job_wrapper,
    'cron',
    minute=5,
    kwargs={"job": alert_job}
)

if __name__ == "__main__":
    logger.info("Scheduler started. Fetching data every 15 minutes...")
    scheduler.start()
