from __future__ import unicode_literals

from dotenv import load_dotenv
import schedule
import time
import os
import logging

from common.utils import configure_logger
from managers.db_manager import DBManager
from managers.google_drive_manager import GoogleDriveManager
from chart_tracker import ChartTracker


if __name__ == "__main__":
    load_dotenv()
    configure_logger()
    logger = logging.getLogger(__name__)

    logger.info("Kifixo 27 Chart Tracker is starting up!")

    db_manager = DBManager()
    gdrive_manager = GoogleDriveManager()
    chart_tracker = ChartTracker(db_manager, gdrive_manager)
    logger.info("Ready to track changes!")


    schedule.every().hour.do(chart_tracker.track_playlist_changes)
    schedule.every().hour.do(chart_tracker.backup_songs)
    schedule.every().day.do(chart_tracker.backup_db)

    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(1)