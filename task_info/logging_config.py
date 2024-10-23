import logging
from datetime import datetime
import pytz


def setup_logging(log_file: str):
    logger = logging.getLogger()

    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)

        tz = pytz.timezone("Europe/Kiev")

        class CustomFormatter(logging.Formatter):
            def formatTime(self, record, datefmt=None):
                dt = datetime.fromtimestamp(record.created, tz)
                return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = CustomFormatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
