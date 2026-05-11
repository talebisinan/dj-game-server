from typing import cast

from django.contrib.auth import authenticate
from ninja import Router
from ninja.errors import HttpError

from users.security import create_access_token

from .auth import BearerAuth
from .models import User
from .schemas import LoginSchema, RegisterSchema, TokenSchema, UserSchema

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
    token = create_access_token(subject=typed_user.email)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response=UserSchema, auth=BearerAuth())
def me(request):
    return request.auth
