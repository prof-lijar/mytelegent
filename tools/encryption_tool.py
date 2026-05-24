from __future__ import annotations

import base64
from cryptography.fernet import Fernet
from tools.config import Config

class EncryptionTool:
    \"\"\"Handles encryption and decryption of messages using Fernet (AES).\"\"\"

    def __init__(self) -> None:
        self._key = self._get_or_generate_key()
        self._fernet = Fernet(self._key)

    def _get_or_generate_key(self) -> bytes:
        \"\"\"Retrieve the secret key from config or derive it from the SECRET_KEY string.\"\"\"
        secret = Config.SECRET_KEY
        if not secret:
            # In a real production app, we would raise an error.
            # For this tool, we will use a fallback or raise EnvironmentError.
            raise EnvironmentError(\"SECRET_KEY must be set in the environment for encryption to work.\")
        
        # Fernet keys must be 32 url-safe base64-encoded bytes.
        # We ensure the secret is converted to the correct format.
        # We use a simple padding/truncation to ensure it's 32 bytes before encoding.
        key_bytes = secret.encode().ljust(32, b'0')[:32]
        return base64.urlsafe_b64encode(key_bytes)

    def encrypt(self, plaintext: str) -> str:
        \"\"\"Encrypt a string and return the base64 encoded ciphertext.\"\"\"
        if not plaintext:
            return plaintext
        ciphertext = self._fernet.encrypt(plaintext.encode())
        return ciphertext.decode()

    def decrypt(self, ciphertext: str) -> str:
        \"\"\"Decrypt a base64 encoded ciphertext and return the plaintext string.\"\"\"
        if not ciphertext:
            return ciphertext
        try:
            plaintext = self._fernet.decrypt(ciphertext.encode())
            return plaintext.decode()
        except Exception as e:
            # Log failure but return original or empty to avoid crashing the scheduler
            # However, for this implementation, we'll let the exception bubble up 
            # or handle it in the db_tool.
            raise ValueError(f\"Decryption failed: {e}\")

# Singleton instance
encryption_tool = EncryptionTool()
