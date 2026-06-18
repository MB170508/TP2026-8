"""Configuration management for IT Toolbox.

Manages config file at ~/.ittoolbox/config.json
Auto-creates with sensible defaults if missing.
Secrets are stored securely via credential manager.
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
    "wolfram_timeout": 15,
    "lunch_timeout": 10,
    "edupage_timeout": 20,
    "rate_limit_calls": 5,
    "rate_limit_window": 60,
}

# Sensitive keys stored in secure credential storage (not in config file)
SECRET_KEYS = {"wolfram_api_key", "edupage_username", "edupage_password"}


class ConfigManager:
    """Singleton config manager with JSON persistence and secure credential storage."""

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
        """Get config value by key (for non-sensitive values).

        Args:
            key: Config key (e.g., 'wolfram_timeout')
            default: Value to return if key not found

        Returns:
            Config value or default
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set config value and persist to file (for non-sensitive values).

        Args:
            key: Config key
            value: New value
        """
        if key in SECRET_KEYS:
            logger.warning(f"Use set_secret() for sensitive values like {key}")
            return

        self._config[key] = value
        self.save()
        logger.debug(f"Set {key} = {value}")

    def get_secret(self, key: str, default: str = "") -> str:
        """Get secret value from secure credential storage.

        Args:
            key: Secret key (e.g., 'wolfram_api_key')
            default: Default value if not found

        Returns:
            Secret value or default
        """
        if key not in SECRET_KEYS:
            logger.warning(f"{key} is not a known secret key")

        from utilities.credential_manager import cred_manager

        value = cred_manager.get_credential("ittoolbox", key)
        return value if value is not None else default

    def set_secret(self, key: str, value: str) -> bool:
        """Store secret value in secure credential storage.

        Args:
            key: Secret key (e.g., 'wolfram_api_key')
            value: Secret value

        Returns:
            True if stored successfully
        """
        if key not in SECRET_KEYS:
            logger.warning(f"{key} is not a known secret key")

        from utilities.credential_manager import cred_manager

        return cred_manager.set_credential("ittoolbox", key, value)

    def delete_secret(self, key: str) -> bool:
        """Delete secret from secure credential storage.

        Args:
            key: Secret key

        Returns:
            True if deleted successfully
        """
        from utilities.credential_manager import cred_manager

        return cred_manager.delete_credential("ittoolbox", key)


# Global instance
config_manager = ConfigManager()
