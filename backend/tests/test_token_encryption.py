
import pytest

from backend.app.auth.token_encryption import (
    encrypt_token,
    decrypt_token,
)


def test_token_encryption_round_trip():
    token = "test-refresh-token-123"

    encrypted = encrypt_token(token)
    decrypted = decrypt_token(encrypted)

    assert encrypted != token
    assert decrypted == token


def test_encrypted_token_is_not_plaintext():
    token = "sensitive-test-token"

    encrypted = encrypt_token(token)

    assert token not in encrypted


def test_encrypt_empty_token_fails():
    with pytest.raises(ValueError):
        encrypt_token("")


def test_decrypt_invalid_token_fails():
    with pytest.raises(ValueError):
        decrypt_token("invalid-encrypted-token")
