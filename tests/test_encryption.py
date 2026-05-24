from __future__ import annotations

import pytest
from cryptography.fernet import Fernet
from tools.encryption_tool import MessageEncryptor, get_encryptor
from tools.config import Config

def test_encryption_decryption():
    \"\"\"Test that a message can be encrypted and then decrypted back to original.\"\"\"
    # Generate a valid Fernet key for testing
    test_key = Fernet.generate_key().decode()
    Config.SECRET_KEY = test_key
    
    # We need to bypass the singleton if it was already initialized
    # For this test, we'll instantiate a new encryptor
    encryptor = MessageEncryptor()
    
    original_text = \"Hello, this is a secret message!\"
    encrypted_text = encryptor.encrypt(original_text)
    
    assert encrypted_text != original_text
    assert encryptor.decrypt(encrypted_text) == original_text

def test_decryption_fallback():
    \"\"\"Test that decrypting plain text returns the plain text (fallback).\"\"\"
    test_key = Fernet.generate_key().decode()
    Config.SECRET_KEY = test_key
    encryptor = MessageEncryptor()
    
    plain_text = \"I am not encrypted\"
    # decrypt should return the input if it fails to decrypt
    assert encryptor.decrypt(plain_text) == plain_text

def test_invalid_key():
    \"\"\"Test that an invalid key raises a RuntimeError.\"\"\"
    Config.SECRET_KEY = \"invalid-key-not-base64\"
    with pytest.raises(RuntimeError, match=\"Invalid SECRET_KEY\"):
        MessageEncryptor()
