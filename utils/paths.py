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