"""Module for managing application configuration."""
import json
import os
from typing import Dict, Any
from .paths import get_file_path

DEFAULT_CONFIG = {
    "rating": {
        "baseline": 1.0,
        "multiplier": 10
    },
    "length": {
        "target": 50000,
        "penalty_step": 2000
    },
    "member_penalties": {
        "last_selection": -15,
        "second_last": -10,
        "third_last": -5
    }
}

def get_config_path() -> str:
    """Get the path to the config file."""
    return get_file_path("config.json")

def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file or create with defaults if not exists."""
    config_path = get_config_path()
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Create config file with defaults if it doesn't exist
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to JSON file."""
    config_path = get_config_path()
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration structure and types."""
    try:
        required_structure = {
            "rating": {"baseline": float, "multiplier": (int, float)},
            "length": {"target": int, "penalty_step": int},
            "member_penalties": {
                "last_selection": (int, float),
                "second_last": (int, float),
                "third_last": (int, float)
            }
        }

        def check_structure(data, structure):
            if not isinstance(data, dict):
                return False
            for key, value in structure.items():
                if key not in data:
                    return False
                if isinstance(value, dict):
                    if not check_structure(data[key], value):
                        return False
                else:
                    if not isinstance(value, tuple):
                        value = (value,)
                    if not isinstance(data[key], value):
                        return False
            return True

        return check_structure(config, required_structure)
    except Exception:
        return False