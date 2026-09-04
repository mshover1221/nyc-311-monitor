import logging
from logging.handlers import RotatingFileHandler
import os

# ----------------------------------
# Logging setup
# ----------------------------------

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")


def setup_logging():
    """Configure application-wide logging with console + rotating file handlers."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # File handler (rotating)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5_000_000,   # ~5 MB
        backupCount=5         # keep 5 old log files
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )

    # Avoid duplicate handlers if setup_logging() is called multiple times
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
