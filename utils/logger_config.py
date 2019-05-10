import os
import logging
from logging.handlers import TimedRotatingFileHandler


def get_formatter():
    return logging.Formatter('%(asctime)s — %(name)s — %(levelname)s — %(message)s')


def get_log_file_name():
    root_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_directory = os.path.join(root_directory, 'logs')
    os.makedirs(logs_directory, exist_ok=True)
    log_file_name = 'underground_chat_client.log'
    return os.path.join(logs_directory, log_file_name)


def get_file_handler():
    file_handler = TimedRotatingFileHandler(get_log_file_name(), when='midnight')
    file_handler.setFormatter(get_formatter())
    return file_handler


def get_logger(logger_name, logging_lvl):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_lvl)
    logger.addHandler(get_file_handler())
    logger.propagate = False
    return logger
