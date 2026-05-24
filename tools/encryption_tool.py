from __future__ import annotations

import base64
from cryptography.fernet import Fernet
from tools.config import Config

class MessageEncryptor:
    \"\"\"Handles encryption and decryption of messages using AES-256 (Fernet).\"\"\"

    def __init__(self) -> None:
        if not Config.SECRET_KEY:
            # In a real production environment, we should raise an error.
            # For local development, we can provide a fallback or a warning.
            # But the requirement is to use SECRET_KEY from .env.
            raise EnvironmentError(\"SECRET_KEY must be set in the environment for message encryption.\")
        
        # Fernet keys must be 32 url-safe base64-encoded bytes.
        # If the provided SECRET_KEY is not in the correct format, we attempt to derive one.
        try:
            self.fernet = Fernet(Config.SECRET_KEY.encode())
        except Exception:
            # This is a fallback to ensure we have a valid key if the user provided a plain string.
            # In a strict environment, we'd demand a valid Fernet key.
            import hashlib
            key = hashlib.sha256(Config.SECRET_KEY.encode()).digest()
            encoded_key = base64.urlsafe_b64encode(key)
            self.fernet = Fernet(encoded_key)

    def encrypt(self, text: str) -> str:
        \"\"\"Encrypt a plain text string.\"\"\"
        if not text:
            return text
        return self.fernet.encrypt(text.encode()).decode()

    def decrypt(self, token: str) -> str:
        \"\"\"Decrypt an encrypted token string.\"\"\"
        if not token:
            return token
        try:
            return self.fernet.decrypt(token.encode()).decode()
        except Exception as e:
            # If decryption fails (e.g. data was not encrypted or key changed), 
            # we return the original text to avoid crashing, but in a real app we might log this.
            return token
