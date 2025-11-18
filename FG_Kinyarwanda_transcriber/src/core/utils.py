# src/core/utils.py

import time
from datetime import datetime

def format_timestamp(ts: float) -> str:
    """Formats a timestamp in seconds to the HH:MM:SS format.

    Args:
        ts: The timestamp in seconds.

    Returns:
        A string representing the timestamp in HH:MM:SS format.
    """
    minutes, seconds = divmod(ts, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


def get_current_time() -> str:
    """Gets the current time as a formatted string.

    Returns:
        A string representing the current time in "YYYY-MM-DD HH:MM:SS" format.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Add any other shared utility functions here.
