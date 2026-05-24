from __future__ import annotations

from cryptography.fernet import Fernet
from tools.config import Config

class MessageEncryptor:
    \"\"\"Handles AES-256 encryption and decryption of messages using Fernet.\"\"\"
    
    def __init__(self) -> None:
        self._key = Config.SECRET_KEY
        if not self._key:
            raise RuntimeError(\"SECRET_KEY must be set in the environment/env file.\")

        try:
            # Fernet requires a base64-encoded 32-byte key.
            self._fernet = Fernet(self._key.encode())
        except Exception as e:
            raise RuntimeError(f\"Invalid SECRET_KEY: {e}\")

    def encrypt(self, plaintext: str) -> str:
        \"\"\"Encrypt a plaintext string and return the encrypted string.\"\"\"
        if not plaintext:
            return plaintext
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        \"\"\"Decrypt an encrypted string and return the plaintext string.\"\"\"
        if not ciphertext:
            return ciphertext
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except Exception:
            # If decryption fails (e.g., because the message was stored in plain text previously),
            # return the original text as a fallback.
            return ciphertext

def get_encryptor() -> MessageEncryptor:
    \"\"\"Provide a singleton instance of MessageEncryptor.\"\"\"
    if not hasattr(get_encryptor, \"_instance\"):
        get_encryptor._instance = MessageEncryptor()
    return get_encryptor._instance
