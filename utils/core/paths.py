import os
import sys
from pathlib import Path

def get_data_dir(profile=None) -> str:
    base_path = None
    if sys.platform == "win32":
        app_data = os.getenv('APPDATA')
        base_path = Path(app_data) / "FabulaRasa"
    elif sys.platform == "darwin":
        base_path = Path.home() / "Library" / "Application Support" / "FabulaRasa"
    else:
        base_path = Path.home() / ".FabulaRasa"
    
    # Always use 'default' profile if none specified
    profile = profile or 'default'
    base_path = base_path / profile
        
    base_path.mkdir(parents=True, exist_ok=True)
    return str(base_path)

def get_file_path(filename: str, profile=None) -> str:
    return str(Path(get_data_dir(profile)) / filename)

def get_profiles() -> list:
    if sys.platform == "win32":
        app_data = os.getenv('APPDATA')
        base_dir = Path(app_data) / "FabulaRasa"
    elif sys.platform == "darwin":
        base_dir = Path.home() / "Library" / "Application Support" / "FabulaRasa"
    else:
        base_dir = Path.home() / ".FabulaRasa"
        
    profiles = []
    try:
        for item in os.listdir(base_dir):
            if os.path.isdir(os.path.join(base_dir, item)):
                profiles.append(item)
    except FileNotFoundError:
        pass
    return profiles or ['default']

def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    
    full_path = os.path.join(base_path, relative_path)
    return os.path.abspath(full_path).replace('\\', '/')