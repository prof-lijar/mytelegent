from __future__ import annotations

import base64
from cryptography.fernet import Fernet
from tools.config import Config

class EncryptionTool:
    """Tool for encrypting and decrypting message content using AES-256 (Fernet)."""

    @classmethod
    def _get_fernet(cls) -> Fernet:
        """Initialize Fernet with the secret key from config."""
        key = Config.SECRET_KEY
        if not key:
            raise EnvironmentError("SECRET_KEY must be set in the environment for encryption to work.")
        
        try:
            # Fernet key must be 32 url-safe base64-encoded bytes
            return Fernet(key.encode())
        except Exception as e:
            raise ValueError(f"Invalid SECRET_KEY provided: {e}")

    @classmethod
    def encrypt(cls, text: str) -> str:
        """Encrypt a plain text string."""
        if not text:
            return text
        f = cls._get_fernet()
        return f.encrypt(text.encode()).decode()

    @classmethod
    def decrypt(cls, token: str) -> str:
        """Decrypt an encrypted token string."""
        if not token:
            return token
        f = cls._get_fernet()
        try:
            return f.decrypt(token.encode()).decode()
        except Exception:
            # If decryption fails (e.g. data was not encrypted), return as is 
            # to maintain backward compatibility with existing plain text data
            return token
