def test_create_run_success(runs_auth_client, minimal_config):
    response = runs_auth_client.post(
        "/",
        json={"template_config": minimal_config},
    )
    assert response.status_code == 200
    assert "invite_code" in response.data
    assert response.data["is_started"] is False


def test_create_run_unauthenticated(runs_public_client, minimal_config):
    response = runs_public_client.post(
        "/",
        json={"template_config": minimal_config},
    )
    assert response.status_code == 401


def test_get_run_success(runs_auth_client, test_run):
    response = runs_auth_client.get(f"/{test_run.invite_code}")
    assert response.status_code == 200
    assert response.data["invite_code"] == test_run.invite_code


def test_get_run_invalid_code(runs_auth_client):
    response = runs_auth_client.get("/XXXXXX")
    assert response.status_code == 404


def test_start_run_success(runs_auth_client, test_run):
    response = runs_auth_client.post(f"/{test_run.invite_code}/start/")
    assert response.status_code == 200
    assert response.data["is_started"] is True


def test_start_run_non_owner(other_auth_client, test_run):
    response = other_auth_client.post(f"/{test_run.invite_code}/start/")
    assert response.status_code == 403


def test_start_run_invalid_code(runs_auth_client):
    response = runs_auth_client.post("/XXXXXX/start/")
    assert response.status_code == 404


def test_export_run_success(runs_auth_client, test_run, minimal_config):
    response = runs_auth_client.get(f"/{test_run.invite_code}/export/")
    assert response.status_code == 200
    assert response.data["name"] == minimal_config["name"]
