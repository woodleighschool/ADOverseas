import configparser
from snippies import app_log

def get_option(item):
	config = configparser.ConfigParser()
	config.read('config.ini')
	try:
		return config["Options"][item]
	except KeyError as e:
		app_log.error(f"ERROR: config item {item} not found: {e}")

def get_credential(credential):
	config = configparser.ConfigParser()
	config.read('config.ini')
	try:
		return config["Credentials"][credential]
	except KeyError as e:
		app_log.error(f"ERROR: config credential {credential} not found: {e}")