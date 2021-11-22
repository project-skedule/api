from datetime import datetime


def current_day_of_week() -> int:
    """Return current day of week

    Returns:
        int: day of week
    """
    return datetime.today().weekday() + 1
