from apscheduler.schedulers.blocking import BlockingScheduler
from run import main
from logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

scheduler = BlockingScheduler()

def job_wrapper():
    logger.info("Starting scheduled run...")
    try:
        main()
        logger.info("Run completed successfully.")
    except Exception as e:
        logger.exception(f"Error during scheduled run: {e}")

scheduler.add_job(job_wrapper, 'interval', minutes=15)

logger.info("Scheduler started. Fetching data every 15 minutes...")
scheduler.start()


