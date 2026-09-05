from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from run import main
from logging_config import setup_logging
import logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = BlockingScheduler()

def job_wrapper():
    logger.info("Starting scheduled run...")
    try:
        main()
        logger.info("Run completed successfully.")
    except Exception as e:
        logger.exception(f"Error during scheduled run: {e}")

# Schedule job to run immediately, then every 15 minutes
scheduler.add_job(
    job_wrapper,
    'interval',
    minutes=15,
    next_run_time=datetime.now()
)

logger.info("Scheduler started. Fetching data every 15 minutes...")
scheduler.start()
