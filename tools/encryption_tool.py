from __future__ import annotations

import base64
from cryptography.fernet import Fernet
from typing import Optional

from tools.config import Config

class MessageEncryptor:
    \"\"\"Handles AES-256 encryption and decryption of messages using Fernet.\"\"\"
    
    def __init__(self, key: Optional[str] = None):
        \"\"\"Initialize the encryptor with a key from config or provided key.\"\"\"
        self._key = key or Config.SECRET_KEY
        if not self._key:
            # We don't raise here to allow the module to be imported without crashing.
            # We will raise when encrypt/decrypt is actually called.
            self._fernet: Optional[Fernet] = None
        else:
            try:
                self._fernet = Fernet(self._key.encode())
            except Exception as e:
                raise ValueError(f\"Invalid SECRET_KEY. It must be a base64-encoded 32-byte key. {e}\")

    def _ensure_initialized(self) -> None:
        \"\"\"Ensure the Fernet instance is created.\"\"\"
        if self._fernet is None:
            if not Config.SECRET_KEY:
                raise EnvironmentError(\"SECRET_KEY must be set in the environment for encryption.\")
            try:
                self._fernet = Fernet(Config.SECRET_KEY.encode())
            except Exception as e:
                raise ValueError(f\"Invalid SECRET_KEY. It must be a base64-encoded 32-byte key. {e}\")

    def encrypt(self, text: str) -> str:
        \"\"\"Encrypt a plain text string and return a base64-encoded encrypted string.\"\"\"
        if not text:
            return text
        self._ensure_initialized()
        return self._fernet!.encrypt(text.encode()).decode()

    def decrypt(self, encrypted_text: str) -> str:
        \"\"\"Decrypt a base64-encoded encrypted string and return plain text.\"\"\"
        if not encrypted_text:
            return encrypted_text
        self._ensure_initialized()
        try:
            return self._fernet!.decrypt(encrypted_text.encode()).decode()
        except Exception:
            # Return original text if decryption fails (e.g. if it was plain text)
            # This is important for backward compatibility during migration.
            return encrypted_text

    @staticmethod
    def generate_key() -> str:
        \"\"\"Generate a new Fernet key.\"\"\"
        return Fernet.generate_key().decode()

# Singleton instance for use across the application
encryptor = MessageEncryptor()
