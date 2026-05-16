def test_login_returns_both_tokens(public_client, test_user):
    response = public_client.post(
        "/login",
        json={
            "email": test_user.email,
            "password": "testpassword123",
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.data
    assert "refresh_token" in response.data


def test_login_returns_401_for_invalid_credentials(public_client, test_user):
    response = public_client.post(
        "/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert "access_token" not in response.data
    assert "refresh_token" not in response.data


def test_login_raises_for_missing_credentials(public_client):
    response = public_client.post(
        "/login",
        json={
            "email": "",
            "password": "",
        },
    )
    assert response.status_code == 422
    assert "access_token" not in response.data
    assert "refresh_token" not in response.data


def test_me_returns_authenticated_user_(auth_client, test_user):
    response = auth_client.get("/me")
    assert response.status_code == 200
    assert response.data["email"] == test_user.email
    assert response.data["nickname"] == test_user.nickname


def test_me_returns_401_for_unauthenticated(public_client):
    response = public_client.get("/me")
    assert response.status_code == 401
    assert "access_token" not in response.data
    assert "refresh_token" not in response.data


def test_refresh_returns_new_access_token(auth_client, test_user, refresh_token):
    response = auth_client.post("/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.data
    assert response.data["refresh_token"] == refresh_token
