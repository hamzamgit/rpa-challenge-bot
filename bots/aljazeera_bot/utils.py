from datetime import datetime
from typing import Optional
from dateutil.parser import parse as date_parser, ParserError
from configs import logger as log


def parse_date_string(text: str) -> datetime | None:
    """
    Converts a text string to a datetime object.

    Args:
        text (str): The text string to be parsed into a datetime object.

    Returns:
        Optional[datetime.datetime]: A datetime object if parsing is successful,
        None otherwise.

    Raises:
        None: This function handles exceptions internally and logs errors.

    Example:
        get_date_obj("2 months ago")
        datetime.datetime(2020, 1, 1, 0, 0)

        get_date_obj("Invalid date string")
        None

    The function uses a fuzzy date parser to attempt to convert a given text string
    into a datetime object. If the parsing fails, it logs an error and returns None.
    """
    try:

        return date_parser(text, fuzzy=True)

    except (ValueError, ParserError) as e:

        log.error(f"Date not convertable {text}", exc_info=e)
        return None
