import contextlib
import os
import sys
from pathlib import Path


def get_base_dir() -> Path:
    """Get the base FabulaRasa directory."""
    if sys.platform == "win32":
        return Path(os.getenv("APPDATA")) / "FabulaRasa"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "FabulaRasa"
    else:
        return Path.home() / ".FabulaRasa"


def get_state_dir() -> Path:
    """Get the directory for app-wide state files."""
    state_dir = get_base_dir() / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def get_profiles_dir() -> Path:
    """Get the directory containing all profiles."""
    profiles_dir = get_base_dir() / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    return profiles_dir


def get_data_dir(profile=None) -> str:
    """Get a specific profile's directory."""
    profile = profile or "default"
    profile_dir = get_profiles_dir() / profile
    profile_dir.mkdir(parents=True, exist_ok=True)
    return str(profile_dir)


def get_file_path(filename: str, profile=None) -> str:
    """Get path for a profile-specific file."""
    return str(Path(get_data_dir(profile)) / filename)


def get_state_file_path(filename: str) -> str:
    """Get path for an app-wide state file."""
    return str(get_state_dir() / filename)


def get_profiles() -> list:
    """Get list of available profiles."""
    profiles = []
    with contextlib.suppress(FileNotFoundError):
        profiles_dir = get_profiles_dir()
        profiles.extend(
            item
            for item in os.listdir(profiles_dir)
            if os.path.isdir(os.path.join(profiles_dir, item))
        )
    return profiles or ["default"]


def resource_path(relative_path: str) -> str:
    """Get path for application resources."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

    full_path = os.path.join(base_path, relative_path)
    return os.path.abspath(full_path).replace("\\", "/")
