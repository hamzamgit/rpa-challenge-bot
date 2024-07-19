from loguru import logger
import sys


def setup_logger(log_path):
    # Remove the default logger
    logger.remove()
    # Add a logger that outputs to the console
    format = "{time} - {name} - {level} - {message}"
    logger.add(sys.stdout, format=format, level="DEBUG")

    # Add a logger that outputs to a file with rotation and compression
    logger.add(
        f"{log_path}/app.log", rotation="5 MB", retention="10 days", compression="zip", level="DEBUG",
        format=format
    )

    # Add a logger for errors only
    logger.add(
        f"{log_path}/error.log", level="ERROR", rotation="1 MB", retention="10 days",
        format=format
    )
