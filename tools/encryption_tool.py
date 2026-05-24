from __future__ import annotations

import base64
import hashlib
from cryptography.fernet import Fernet
from tools.config import Config

class EncryptionTool:
    # Handles AES-256 encryption and decryption using Fernet.

    def __init__(self) -> None:
        key = Config.SECRET_KEY
        if not key:
            key = 'default-secret-key-for-development-only'

        hashed_key = hashlib.sha256(key.encode()).digest()
        self.fernet = Fernet(base64.urlsafe_b64encode(hashed_key))

    def encrypt(self, text: str) -> str:
        # Encrypt a plaintext string.
        if not text:
            return text
        return self.fernet.encrypt(text.encode()).decode()

    def decrypt(self, token: str) -> str:
        # Decrypt an encrypted token.
        if not token:
            return token
        try:
            return self.fernet.decrypt(token.encode()).decode()
        except Exception:
            return token

# Singleton instance
encryption_tool = EncryptionTool()
