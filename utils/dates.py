from datetime import datetime, timedelta

def get_current_date():
    """Return current date in standard format."""
    return datetime.now().strftime("%Y-%m-%d")

def get_next_monday():
    """Get the date of the next upcoming Monday."""
    today = datetime.now()
    days_ahead = 7 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)

def format_date(date):
    """Format a datetime object in standard format."""
    return date.strftime("%Y-%m-%d")