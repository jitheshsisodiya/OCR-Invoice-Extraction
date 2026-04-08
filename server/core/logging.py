"""Configure Loguru logging."""
import sys
from loguru import logger


def setup_logging(debug: bool = False) -> None:
    logger.remove()
    level = "DEBUG" if debug else "INFO"
    logger.add(sys.stderr, level=level, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")
    logger.add("logs/server.log", rotation="10 MB", retention="7 days", level="DEBUG", enqueue=True)
