from __future__ import annotations

import pytest
from tools.encryption_tool import EncryptionTool
from tools.config import Config

def test_encryption_decryption():
    # Test that a message can be encrypted and then decrypted back to original.
    Config.SECRET_KEY = 'test-secret-key-123'
    encryptor = EncryptionTool()
    original_text = 'Hello, this is a secret message!'
    encrypted_text = encryptor.encrypt(original_text)
    assert encrypted_text != original_text
    assert encryptor.decrypt(encrypted_text) == original_text

def test_decryption_fallback():
    # Test that decrypting plain text returns the plain text (fallback).
    Config.SECRET_KEY = 'test-secret-key-123'
    encryptor = EncryptionTool()
    plain_text = 'I am not encrypted'
    assert encryptor.decrypt(plain_text) == plain_text

def test_encryption_with_different_keys():
    # Test that messages encrypted with one key cannot be decrypted with another.
    Config.SECRET_KEY = 'key-one'
    encryptor_one = EncryptionTool()
    Config.SECRET_KEY = 'key-two'
    encryptor_two = EncryptionTool()
    original_text = 'Secret Message'
    encrypted_one = encryptor_one.encrypt(original_text)
    assert encryptor_two.decrypt(encrypted_one) == encrypted_one
    assert encryptor_two.decrypt(encrypted_one) != original_text

def test_empty_string_handling():
    # Test that empty strings are handled gracefully.
    encryptor = EncryptionTool()
    assert encryptor.encrypt('') == ''
    assert encryptor.decrypt('') == ''
