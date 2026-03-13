import logging
import sys
import os
from logging.handlers import RotatingFileHandler

class LogColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: LogColors.OKCYAN,
        logging.INFO: LogColors.OKBLUE,
        logging.WARNING: LogColors.WARNING,
        logging.ERROR: LogColors.FAIL,
        logging.CRITICAL: LogColors.BOLD + LogColors.FAIL,
    }

    def format(self, record):
        level_color = self.COLORS.get(record.levelno, '')
        reset = LogColors.ENDC
        
        orig_levelname = record.levelname
        orig_msg = record.msg
        
        if level_color:
            record.levelname = f"{level_color}{orig_levelname}{reset}"
            record.msg = f"{level_color}{orig_msg}{reset}"
        
        formatted = super().format(record)
        
        # Restore original values to avoid affecting other handlers
        record.levelname = orig_levelname
        record.msg = orig_msg
        
        return formatted

def setup_logging():
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "vulnsight.log")

    # Use a named logger instead of the root logger to avoid duplication
    logger = logging.getLogger("vulnsight")
    logger.setLevel(logging.INFO)
    logger.propagate = False # Prevent logs from being passed to the root logger

    # Clear existing handlers if any
    if logger.hasHandlers():
        logger.handlers.clear()

    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Also capture logs from our app modules
    logging.getLogger("app").handlers = logger.handlers
    logging.getLogger("app").setLevel(logging.INFO)
    logging.getLogger("app").propagate = False

    return logger
