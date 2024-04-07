import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger("main")

logger.info("Logger initializing...")
logger.debug("Test debug message")
logger.warning("Test warning message")
logger.error("Test error message")
logger.critical("Test critical message")

logger.info("Logger initialized")
