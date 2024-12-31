"""Module for managing application paths."""
import os
import sys
from pathlib import Path

def get_data_dir() -> str:
    """Get or create the application data directory."""
    if sys.platform == "win32":
        # Windows
        app_data = os.getenv('APPDATA')
        base_path = Path(app_data) / "FabulaRasa"
    elif sys.platform == "darwin":
        # macOS
        base_path = Path.home() / "Library" / "Application Support" / "FabulaRasa"
    else:
        # Linux/Unix
        base_path = Path.home() / ".FabulaRasa"

    # Create directory if it doesn't exist
    base_path.mkdir(parents=True, exist_ok=True)
    return str(base_path)

def get_file_path(filename: str) -> str:
    """Get the full path for a data file."""
    return str(Path(get_data_dir()) / filename)

def resource_path(relative_path: str) -> str:
    """Get the absolute path to a resource, works both for development and PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Get the absolute path to the parent directory of 'utils'
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    full_path = os.path.join(base_path, relative_path)
    # Convert to forward slashes and ensure it's absolute
    return os.path.abspath(full_path).replace('\\', '/')
