"""Date handling utilities."""
from datetime import datetime

def get_current_date():
    """Return current date in standard format."""
    return datetime.now().strftime("%Y-%m-%d")

def format_date(date):
    """Format a datetime object in standard format."""
    return date.strftime("%Y-%m-%d")