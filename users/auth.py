from jwt import PyJWTError
from ninja.errors import HttpError
from ninja.security import HttpBearer

from .models import User
from .security import decode_access_token


class BearerAuth(HttpBearer):
    def authenticate(self, request, token: str):
        try:
            email = decode_access_token(token)
        except PyJWTError:
            raise HttpError(401, "Invalid or expired token")

        try:
            return User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            raise HttpError(401, "User not found or inactive")
