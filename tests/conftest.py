import pytest
from django.conf import settings
from ninja.testing import TestClient

from users.api import router
from users.models import User
from users.security import create_token


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        email="test@example.com",
        password="testpassword123",
        nickname="testuser",
    )


@pytest.fixture
def auth_client(auth_token):
    client = TestClient(router)
    client.headers = {"Authorization": f"Bearer {auth_token}"}
    return client


@pytest.fixture
def public_client():
    return TestClient(router)


@pytest.fixture
def auth_token(test_user):
    return create_token(
        subject=test_user.email,
        token_type="access",
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


@pytest.fixture
def refresh_token(test_user):
    return create_token(
        subject=test_user.email,
        token_type="refresh",
        expires_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )


@pytest.fixture
def auth_header(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
