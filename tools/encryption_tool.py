from __future__ import annotations

import base64
from cryptography.fernet import Fernet
from tools.config import Config

class EncryptionTool:
    """Tool for encrypting and decrypting message content using AES-256 (Fernet)."""
    
    _fernet: Fernet | None = None

    @classmethod
    def _get_fernet(cls) -> Fernet:
        """Initialize and return the Fernet instance using the SECRET_KEY from config."""
        if cls._fernet is None:
            key = Config.SECRET_KEY
            if not key:
                raise EnvironmentError("SECRET_KEY must be set in the environment for encryption to work.")
            
            try:
                # Ensure key is in bytes and base64 encoded
                if isinstance(key, str):
                    key = key.encode()
                cls._fernet = Fernet(key)
            except Exception as e:
                raise ValueError(f"Invalid SECRET_KEY provided: {e}. Key must be a 32-byte base64-encoded string.")
        
        return cls._fernet

    @classmethod
    def encrypt(cls, text: str) -> str:
        """Encrypt plain text and return as a string."""
        if not text:
            return text
        f = cls._get_fernet()
        return f.encrypt(text.encode()).decode()

    @classmethod
    def decrypt(cls, token: str) -> str:
        """Decrypt encrypted token and return as plain text."""
        if not token:
            return token
        f = cls._get_fernet()
        return f.decrypt(token.encode()).decode()
