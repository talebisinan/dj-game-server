from typing import cast

from django.conf import settings
from django.contrib.auth import authenticate
from jwt.exceptions import PyJWTError
from ninja import Router
from ninja.errors import HttpError

from users.security import create_token, decode_token

from .auth import BearerAuth
from .models import User
from .schemas import (
    LoginSchema,
    RefreshTokenSchema,
    RegisterSchema,
    TokenSchema,
    UserSchema,
)

router = Router(tags=["users"])


@router.post("/register", response=UserSchema)
def register(request, payload: RegisterSchema):
    if User.objects.filter(email=payload.email).exists():
        raise HttpError(400, "Email already registered")

    if User.objects.filter(nickname=payload.nickname).exists():
        raise HttpError(400, "Nickname already taken")
    user = User.objects.create_user(
        email=payload.email,
        password=payload.password,
        nickname=payload.nickname,
        full_name=payload.full_name,
    )
    return user


@router.post("/login", response=TokenSchema)
def login(request, payload: LoginSchema):
    user = authenticate(request, email=payload.email, password=payload.password)
    if not user:
        raise HttpError(401, "Invalid email or password")

    typed_user = cast(User, user)
    access_token = create_token(
        subject=typed_user.email,
        token_type="access",
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    refresh_token = create_token(
        subject=typed_user.email,
        token_type="refresh",
        expires_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response=TokenSchema)
def refresh(request, payload: RefreshTokenSchema):
    try:
        email = decode_token(token=payload.refresh_token, token_type="refresh")
    except PyJWTError:
        raise HttpError(401, "Invalid refresh token")

    access_token = create_token(
        subject=email,
        token_type="access",
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return {
        "access_token": access_token,
        "refresh_token": payload.refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response=UserSchema, auth=BearerAuth())
def me(request):
    return request.auth
