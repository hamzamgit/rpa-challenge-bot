from loguru import logger
import sys
from robocorp.tasks import get_output_dir


def setup_logger():
    # Remove the default logger
    logger.remove()
    # Add a logger that outputs to the console
    logger.add(sys.stdout, format="{time} - {name} - {level} - {message}", level="DEBUG")

    # Add a logger that outputs to a file with rotation and compression
    logger.add(
        f"{get_output_dir()}/app.log", rotation="5 MB", retention="10 days", compression="zip", level="DEBUG",
        format="{time} - {name} - {level} - {message}"
    )

    # Add a logger for errors only
    logger.add(
        f"{get_output_dir()}/error.log", level="ERROR", rotation="1 MB", retention="10 days",
        format="{time} - {name} - {level} - {message}"
    )


setup_logger()

