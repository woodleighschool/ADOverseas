import logging
import os
from snippies import config

def configure_logging():
	FORMAT="%(asctime)s|%(levelname)s|%(name)s|%(module)s|%(funcName)s|%(message)s"
	if config.get_option("LOGLEVEL") == "debug":
		logging.basicConfig(level=logging.DEBUG, format=FORMAT)
	else:
		logging.basicConfig()
	logger = logging.getLogger(name="ADOverseas")
	logger.debug("Logging configured")

def critical(message):
	logger = logging.getLogger(name="ADOverseas")
	logger.critical(message)

def error(message):
	logger = logging.getLogger(name="ADOverseas")
	logger.error(message)

def warning(message):
	logger = logging.getLogger(name="ADOverseas")
	logger.warning(message)

def info(message):
	logger = logging.getLogger(name="ADOverseas")
	logger.info(message)

def debug(message):
	logger = logging.getLogger(name="ADOverseas")
	logger.debug(message)
	
	