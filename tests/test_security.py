import pytest
from jwt.exceptions import PyJWTError

from users.security import create_token, decode_token


def test_create_token_is_valid_jwt():
    email = "test@example.com"
    token = create_token(subject=email, token_type="access", expires_minutes=30)

    decoded = decode_token(token, "access")
    assert decoded == email


def test_decode_raises_pyjwt_error():
    token = create_token(
        subject="test@example.com", token_type="access", expires_minutes=30
    )
    with pytest.raises(PyJWTError):
        decode_token(token, "refresh")


def test_expired_token_raises_pyjwt_error():
    token = create_token(
        subject="test@example.com", token_type="access", expires_minutes=-1
    )
    with pytest.raises(PyJWTError):
        decode_token(token, "access")
