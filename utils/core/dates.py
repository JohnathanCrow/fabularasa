from datetime import datetime, timedelta

from utils.common.constants import DATE_FORMAT


def get_current_date():
    return datetime.now().strftime(DATE_FORMAT)


def get_next_monday():
    today = datetime.now()
    days_ahead = 7 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)


def format_date(date):
    return date if isinstance(date, str) else date.strftime(DATE_FORMAT)
