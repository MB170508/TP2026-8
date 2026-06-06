"""Configuration management for IT Toolbox.

Manages config file at ~/.ittoolbox/config.json
Auto-creates with sensible defaults if missing.
"""

import json
from pathlib import Path
from typing import Any, Optional

from utilities.logger import get_logger

logger = get_logger(__name__)

# Configuration locations and defaults
CONFIG_DIR = Path.home() / ".ittoolbox"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "wolfram_api_key": "",
    "edupage_username": "",
    "edupage_password": "",
    "wolfram_timeout": 15,
    "lunch_timeout": 10,
    "edupage_timeout": 20,
    "rate_limit_calls": 5,
    "rate_limit_window": 60,
}


class ConfigManager:
    """Singleton config manager with JSON persistence."""

    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def __init__(self):
        if not self._loaded:
            self.load()
            self._loaded = True

    def load(self) -> None:
        """Load config from file or create with defaults."""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r") as f:
                    file_config = json.load(f)
                    # Merge file config with defaults (file overrides defaults)
                    self._config = {**DEFAULT_CONFIG, **file_config}
                    logger.info(f"Loaded config from {CONFIG_FILE}")
            else:
                self._config = DEFAULT_CONFIG.copy()
                self.save()
                logger.info(f"Created new config at {CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}. Using defaults.")
            self._config = DEFAULT_CONFIG.copy()

    def save(self) -> None:
        """Write current config to JSON file."""
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, "w") as f:
                json.dump(self._config, f, indent=2)
            logger.debug(f"Saved config to {CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by key.

        Args:
            key: Config key (e.g., 'wolfram_timeout')
            default: Value to return if key not found

        Returns:
            Config value or default
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set config value and persist to file.

        Args:
            key: Config key
            value: New value
        """
        self._config[key] = value
        self.save()
        logger.debug(f"Set {key} = {value}")


# Global instance
config_manager = ConfigManager()
