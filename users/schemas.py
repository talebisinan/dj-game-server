from datetime import datetime

from ninja.schema import Schema
from pydantic import EmailStr


class MessageSchema(Schema):
    message: str


class RegisterSchema(Schema):
    email: EmailStr
    nickname: str
    password: str
    full_name: str = ""


class LoginSchema(Schema):
    email: EmailStr
    password: str


class TokenSchema(Schema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenSchema(Schema):
    refresh_token: str


class UserSchema(Schema):
    email: EmailStr
    nickname: str
    full_name: str
    created_at: datetime
