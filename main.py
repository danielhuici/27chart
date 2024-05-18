from __future__ import unicode_literals
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import schedule
import time

from chart_tracker import ChartTracker

def configure_logger():
        # Set the logging level for specific loggers
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)

        # Configure the console logger
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(levelname)s [%(asctime)s] %(name)s - %(message)s'))

        # Configure the file logger
        file_handler = RotatingFileHandler('monitor.log', maxBytes=10e6)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(levelname)s [%(asctime)s] %(name)s - %(message)s'))

        # Configure the root logger with both handlers
        logging.basicConfig(level=logging.NOTSET,
                            handlers=[console_handler, file_handler])


if __name__ == "__main__":
    load_dotenv()
    configure_logger()
    logger = logging.getLogger(__name__)

    logger.info("Kifixo 27 Chart Tracker is starting up!")
    chartTracker = ChartTracker()
    logger.info("Ready to track changes!")
    schedule.every().hour.do(chartTracker.track_playlist_changes)
    schedule.every().hour.do(chartTracker.backup_songs)
    schedule.every().day.do(chartTracker.check_songs_availability)
    schedule.every().day.do(chartTracker.backup_db)

    schedule.run_all() # Run everything on the beginning
    while True:
        schedule.run_pending()
        time.sleep(1)