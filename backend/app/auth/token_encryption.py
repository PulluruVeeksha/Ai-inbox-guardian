from cryptography.fernet import Fernet, InvalidToken

from backend.app.config import TOKEN_ENCRYPTION_KEY


def get_fernet() -> Fernet:
    if not TOKEN_ENCRYPTION_KEY:
        raise RuntimeError(
            "TOKEN_ENCRYPTION_KEY is missing from the environment."
        )

    try:
        return Fernet(TOKEN_ENCRYPTION_KEY.encode("utf-8"))
    except (ValueError, TypeError) as exc:
        raise RuntimeError(
            "TOKEN_ENCRYPTION_KEY is invalid."
        ) from exc


def encrypt_token(token: str) -> str:
    if not token:
        raise ValueError("Cannot encrypt an empty token.")

    return get_fernet().encrypt(
        token.encode("utf-8")
    ).decode("utf-8")


def decrypt_token(encrypted_token: str) -> str:
    try:
        return get_fernet().decrypt(
            encrypted_token.encode("utf-8")
        ).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError(
            "Stored OAuth token could not be decrypted."
        ) from exc