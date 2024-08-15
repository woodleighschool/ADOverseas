import configparser
from snippies import app_log

def get_item(item):
	config = configparser.ConfigParser()
	config.read('config.ini')
	try:
		return config[item]
	except KeyError as e:
		app_log.error(f"ERROR: config item {item} not found: {e}")