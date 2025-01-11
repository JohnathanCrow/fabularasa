from datetime import datetime, timedelta

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def get_next_monday():
    today = datetime.now()
    days_ahead = 7 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)

def format_date(date):
    if isinstance(date, str):
        return date
    return date.strftime("%Y-%m-%d")