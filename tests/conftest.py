import json
from pathlib import Path

import pytest
from django.conf import settings
from ninja.testing import TestClient

from runs.api import router as runs_router
from runs.models import Run
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


@pytest.fixture
def runs_auth_client(auth_token):
    client = TestClient(runs_router)
    client.headers = {"Authorization": f"Bearer {auth_token}"}
    return client


@pytest.fixture
def runs_public_client():
    return TestClient(runs_router)


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        email="other@example.com",
        password="testpassword123",
        nickname="otheruser",
    )


@pytest.fixture
def other_auth_client(db, other_user):
    token = create_token(
        subject=other_user.email,
        token_type="access",
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    client = TestClient(runs_router)
    client.headers = {"Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
def minimal_config():
    path = Path(__file__).parent.parent / "runs" / "default_template.json"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def test_run(db, test_user, minimal_config):
    return Run.objects.create(
        owner=test_user,
        template_config=minimal_config,
        current_config=minimal_config,
    )
