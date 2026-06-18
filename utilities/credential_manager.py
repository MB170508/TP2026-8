"""Platform-specific credential storage manager.

Desktop: Uses system keyrings (GNOME Keyring, Keychain, Credential Manager)
Mobile: Uses native credential storage (Android Keystore, iOS Keychain)
Fallback: Encrypted local storage or plaintext config
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

from utilities.logger import get_logger

logger = get_logger(__name__)

# Credential storage paths
CREDS_DIR = Path.home() / ".ittoolbox" / "creds"
CREDS_FILE = CREDS_DIR / "credentials.json"


def get_platform() -> str:
    """Detect platform: desktop (win/mac/linux), android, ios, or unknown."""
    system = sys.platform.lower()
    if system.startswith("win"):
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system.startswith("linux"):
        return "linux"

    try:
        import platform as sys_platform
        if "android" in sys_platform.system().lower():
            return "android"
        elif "ios" in sys_platform.system().lower():
            return "ios"
    except:
        pass

    return "unknown"


class CredentialManager:
    """Unified credential storage across platforms."""

    def __init__(self):
        self.platform = get_platform()
        self.keyring = None
        self.storage_type = None
        self._init_platform()

    def _init_platform(self):
        """Initialize platform-specific credential storage."""
        if self.platform in ("windows", "macos", "linux"):
            self._init_desktop()
        elif self.platform == "android":
            self._init_android()
        elif self.platform == "ios":
            self._init_ios()
        else:
            self._init_fallback()

    def _init_desktop(self):
        """Use keyring package for desktop."""
        try:
            import keyring
            self.keyring = keyring
            self.storage_type = "keyring"
            logger.info(f"Credential storage: keyring ({self.platform})")
        except ImportError:
            logger.warning("keyring not installed, falling back to encrypted storage")
            self._init_fallback()

    def _init_android(self):
        """Use Android Keystore via pyjnius."""
        try:
            import jnius
            self.storage_type = "android_keystore"
            logger.info("Credential storage: Android Keystore")
        except ImportError:
            logger.warning("pyjnius not available, falling back to encrypted storage")
            self._init_fallback()

    def _init_ios(self):
        """Use iOS Keychain via pyobjc."""
        try:
            import objc
            self.storage_type = "ios_keychain"
            logger.info("Credential storage: iOS Keychain")
        except ImportError:
            logger.warning("pyobjc not available, falling back to encrypted storage")
            self._init_fallback()

    def _init_fallback(self):
        """Fallback: encrypted local storage."""
        try:
            from cryptography.fernet import Fernet
            self.storage_type = "encrypted_local"
            CREDS_DIR.mkdir(parents=True, exist_ok=True)
            logger.info("Credential storage: encrypted local (cryptography)")
        except ImportError:
            self.storage_type = "plaintext_config"
            logger.warning("cryptography not available, credentials stored unencrypted")

    def set_credential(self, service: str, key: str, value: str) -> bool:
        """Store credential securely.

        Args:
            service: Service name (e.g., 'ittoolbox')
            key: Credential key (e.g., 'wolfram_api_key')
            value: Credential value

        Returns:
            True if stored successfully
        """
        try:
            if self.storage_type == "keyring":
                self.keyring.set_password(service, key, value)
                logger.debug(f"Stored credential via keyring: {service}/{key}")
                return True

            elif self.storage_type == "android_keystore":
                # TODO: Implement Android Keystore access
                return self._set_encrypted(service, key, value)

            elif self.storage_type == "ios_keychain":
                # TODO: Implement iOS Keychain access
                return self._set_encrypted(service, key, value)

            elif self.storage_type == "encrypted_local":
                return self._set_encrypted(service, key, value)

            else:
                return self._set_plaintext(service, key, value)

        except Exception as e:
            logger.error(f"Failed to set credential {service}/{key}: {e}")
            return False

    def get_credential(self, service: str, key: str) -> Optional[str]:
        """Retrieve credential securely.

        Args:
            service: Service name (e.g., 'ittoolbox')
            key: Credential key (e.g., 'wolfram_api_key')

        Returns:
            Credential value or None if not found
        """
        try:
            if self.storage_type == "keyring":
                value = self.keyring.get_password(service, key)
                if value:
                    logger.debug(f"Retrieved credential via keyring: {service}/{key}")
                return value

            elif self.storage_type in ("android_keystore", "ios_keychain"):
                return self._get_encrypted(service, key)

            elif self.storage_type == "encrypted_local":
                return self._get_encrypted(service, key)

            else:
                return self._get_plaintext(service, key)

        except Exception as e:
            logger.error(f"Failed to get credential {service}/{key}: {e}")
            return None

    def delete_credential(self, service: str, key: str) -> bool:
        """Delete stored credential.

        Args:
            service: Service name
            key: Credential key

        Returns:
            True if deleted successfully
        """
        try:
            if self.storage_type == "keyring":
                self.keyring.delete_password(service, key)
                logger.debug(f"Deleted credential via keyring: {service}/{key}")
                return True

            elif self.storage_type == "encrypted_local":
                return self._delete_encrypted(service, key)

            else:
                return self._delete_plaintext(service, key)

        except Exception as e:
            logger.error(f"Failed to delete credential {service}/{key}: {e}")
            return False

    def _set_encrypted(self, service: str, key: str, value: str) -> bool:
        """Encrypt and store locally."""
        try:
            from cryptography.fernet import Fernet
            import base64
            import hashlib

            creds = self._load_encrypted_creds() or {}
            if service not in creds:
                creds[service] = {}

            # Derive encryption key from machine
            key_hash = hashlib.sha256(
                (os.environ.get("USER", "user") + os.path.expanduser("~")).encode()
            ).digest()
            cipher_key = base64.urlsafe_b64encode(key_hash)
            cipher = Fernet(cipher_key)
            encrypted_value = cipher.encrypt(value.encode()).decode()

            creds[service][key] = encrypted_value

            CREDS_DIR.mkdir(parents=True, exist_ok=True)
            with open(CREDS_FILE, "w") as f:
                json.dump(creds, f, indent=2)
            os.chmod(CREDS_FILE, 0o600)  # Read/write for owner only
            logger.debug(f"Stored encrypted credential: {service}/{key}")
            return True
        except Exception as e:
            logger.error(f"Failed to store encrypted credential: {e}")
            return False

    def _get_encrypted(self, service: str, key: str) -> Optional[str]:
        """Decrypt and retrieve from local storage."""
        try:
            from cryptography.fernet import Fernet
            import base64
            import hashlib

            creds = self._load_encrypted_creds()
            if not creds or service not in creds or key not in creds[service]:
                return None

            # Derive same encryption key
            key_hash = hashlib.sha256(
                (os.environ.get("USER", "user") + os.path.expanduser("~")).encode()
            ).digest()
            cipher_key = base64.urlsafe_b64encode(key_hash)
            cipher = Fernet(cipher_key)
            encrypted_value = creds[service][key]
            decrypted_value = cipher.decrypt(encrypted_value.encode()).decode()
            logger.debug(f"Retrieved encrypted credential: {service}/{key}")
            return decrypted_value
        except Exception as e:
            logger.error(f"Failed to retrieve encrypted credential: {e}")
            return None

    def _delete_encrypted(self, service: str, key: str) -> bool:
        """Delete encrypted credential."""
        try:
            creds = self._load_encrypted_creds()
            if creds and service in creds and key in creds[service]:
                del creds[service][key]
                if not creds[service]:
                    del creds[service]

                with open(CREDS_FILE, "w") as f:
                    json.dump(creds, f, indent=2)
                logger.debug(f"Deleted encrypted credential: {service}/{key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete encrypted credential: {e}")
            return False

    def _load_encrypted_creds(self) -> Optional[dict]:
        """Load encrypted credentials file."""
        try:
            if CREDS_FILE.exists():
                with open(CREDS_FILE, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load encrypted credentials: {e}")
        return None

    def _set_plaintext(self, service: str, key: str, value: str) -> bool:
        """Fallback to plaintext config (least secure)."""
        from config import config_manager

        config_manager.set(f"{service}_{key}", value)
        logger.debug(f"Stored credential in config: {service}/{key}")
        return True

    def _get_plaintext(self, service: str, key: str) -> Optional[str]:
        """Fallback to plaintext config."""
        from config import config_manager

        return config_manager.get(f"{service}_{key}")

    def _delete_plaintext(self, service: str, key: str) -> bool:
        """Delete credential from plaintext config."""
        # Not easily reversible with current config system
        return False


# Global instance
cred_manager = CredentialManager()
