import logging
from logging.handlers import RotatingFileHandler
import os

def configure_logger():
        # Set the logging level for specific loggers
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("selenium").setLevel(logging.CRITICAL)

        # Configure the console logger
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(levelname)s [%(asctime)s] %(name)s [%(filename)s:%(lineno)d] - %(message)s'))

        # Configure the file logger
        file_handler = RotatingFileHandler('monitor.log', maxBytes=10e6)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(levelname)s [%(asctime)s] %(name)s - %(message)s'))

        # Configure the root logger with both handlers
        logging.basicConfig(level=logging.NOTSET,
                                handlers=[console_handler, file_handler])

def debug_mode():
        return os.getenv('DEBUG') == '1'