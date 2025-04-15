import logging
import os
from datetime import datetime


def setup_logger(name):
    """Set up a logger for the given name"""
    # Create temp directory if it doesn't exist
    os.makedirs("temp/test_runs", exist_ok=True)

    # Create a custom logger
    logger = logging.getLogger(name)

    # Check if handlers already exist to avoid duplicate logs
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Create handlers
        c_handler = logging.StreamHandler()  # Console handler
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        f_handler = logging.FileHandler(f"temp/test_runs/test_run_{timestamp}.log")

        # Set log level for handlers
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(logging.INFO)

        # Create formatters and add to handlers
        c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

    return logger
