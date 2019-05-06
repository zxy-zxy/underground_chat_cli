import logging
from logging.handlers import TimedRotatingFileHandler

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = "underground_chat_client.log"


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name, logging_lvl):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_lvl)
    logger.addHandler(get_file_handler())
    logger.propagate = False
    return logger
