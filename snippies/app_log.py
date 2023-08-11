import logging

def configure_logging():
    logging.basicConfig(filename="/var/log/ADOverseas/app.log")
    logger = logging.getLogger(name="ADOverseas")
    logger.debug("Logging configured")

def message(level, message):
    logger = logging.getLogger(name="ADOverseas")
    
    match level:
        case "critical":
            logger.critical(message)
        case "error":
            logger.error(message)
        case "warning":
            logger.warning(message)
        case "info":
            logger.info(message)
        case "debug":
            logger.debug(message)
        case _:
            logger.debug(message)
    
    
    