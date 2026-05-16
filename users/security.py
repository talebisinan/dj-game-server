from datetime import datetime, timedelta, timezone

from django.conf import settings
from jwt import decode, encode
from jwt.exceptions import PyJWTError
from typing_extensions import Literal

type TokenType = Literal["access", "refresh"]


def create_token(subject: str, token_type: TokenType, expires_minutes: float) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "exp": expire, "type": token_type}
    return encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, token_type: TokenType) -> str:
    payload = decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    if payload.get("type") != token_type:
        raise PyJWTError("Invalid token type")
    return payload["sub"]
