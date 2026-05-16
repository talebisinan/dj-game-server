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


def test_join_run_success(other_auth_client, test_run):
    response = other_auth_client.post(f"/{test_run.invite_code}/join")
    assert response.status_code == 200
    assert any(p["nickname"] == "otheruser" for p in response.data["pending_players"])


def test_join_run_already_pending(other_auth_client, test_run):
    other_auth_client.post(f"/{test_run.invite_code}/join")
    response = other_auth_client.post(f"/{test_run.invite_code}/join")
    assert response.status_code == 400


def test_join_run_already_participant(
    other_auth_client, runs_auth_client, test_run, other_user
):
    other_auth_client.post(f"/{test_run.invite_code}/join")
    runs_auth_client.post(f"/{test_run.invite_code}/accept/{other_user.id}")
    response = other_auth_client.post(f"/{test_run.invite_code}/join")
    assert response.status_code == 400


def test_accept_player_success(
    runs_auth_client, other_auth_client, test_run, other_user
):
    other_auth_client.post(f"/{test_run.invite_code}/join")
    response = runs_auth_client.post(f"/{test_run.invite_code}/accept/{other_user.id}")
    assert response.status_code == 200
    assert any(p["nickname"] == "otheruser" for p in response.data["participants"])
    assert not any(
        p["nickname"] == "otheruser" for p in response.data["pending_players"]
    )


def test_accept_player_non_owner(other_auth_client, test_run, test_user):
    response = other_auth_client.post(f"/{test_run.invite_code}/accept/{test_user.id}")
    assert response.status_code == 403


def test_accept_player_not_pending(runs_auth_client, test_run, other_user):
    response = runs_auth_client.post(f"/{test_run.invite_code}/accept/{other_user.id}")
    assert response.status_code == 403


def test_reject_player_success(
    runs_auth_client, other_auth_client, test_run, other_user
):
    other_auth_client.post(f"/{test_run.invite_code}/join")
    response = runs_auth_client.post(f"/{test_run.invite_code}/reject/{other_user.id}")
    assert response.status_code == 200
    assert not any(
        p["nickname"] == "otheruser" for p in response.data["pending_players"]
    )


def test_reject_player_non_owner(other_auth_client, test_run, test_user):
    response = other_auth_client.post(f"/{test_run.invite_code}/reject/{test_user.id}")
    assert response.status_code == 403


def test_reject_player_not_pending(runs_auth_client, test_run, other_user):
    response = runs_auth_client.post(f"/{test_run.invite_code}/reject/{other_user.id}")
    assert response.status_code == 403


def test_claim_character_success(
    other_auth_client, runs_auth_client, test_run, other_user, minimal_config
):
    # join and get accepted first
    other_auth_client.post(f"/{test_run.invite_code}/join")
    runs_auth_client.post(f"/{test_run.invite_code}/accept/{other_user.id}")

    response = other_auth_client.post(f"/{test_run.invite_code}/claim/mage")
    assert response.status_code == 200
    assert any(c["character_id"] == "mage" for c in response.data["pending_claims"])


def test_claim_character_not_participant(other_auth_client, test_run):
    response = other_auth_client.post(f"/{test_run.invite_code}/claim/mage")
    assert response.status_code == 400


def test_claim_character_does_not_exist(
    other_auth_client, runs_auth_client, test_run, other_user
):
    other_auth_client.post(f"/{test_run.invite_code}/join")
    runs_auth_client.post(f"/{test_run.invite_code}/accept/{other_user.id}")

    response = other_auth_client.post(f"/{test_run.invite_code}/claim/nonexistent")
    assert response.status_code == 400


def test_claim_character_already_pending(
    other_auth_client, runs_auth_client, test_run, other_user
):
    other_auth_client.post(f"/{test_run.invite_code}/join")
    runs_auth_client.post(f"/{test_run.invite_code}/accept/{other_user.id}")
    other_auth_client.post(f"/{test_run.invite_code}/claim/mage")

    response = other_auth_client.post(f"/{test_run.invite_code}/claim/mage")
    assert response.status_code == 400


def test_approve_claim_success(
    runs_auth_client, other_auth_client, test_run, other_user
):
    other_auth_client.post(f"/{test_run.invite_code}/join")
    runs_auth_client.post(f"/{test_run.invite_code}/accept/{other_user.id}")
    other_auth_client.post(f"/{test_run.invite_code}/claim/mage")

    response = runs_auth_client.post(f"/{test_run.invite_code}/claim/mage/approve")
    assert response.status_code == 200
    assert any(
        p["character_id"] == "mage" and p["user_id"] == str(other_user.id)
        for p in response.data["current_config"]["player_characters"]
    )
    assert not any(c["character_id"] == "mage" for c in response.data["pending_claims"])


def test_approve_claim_non_owner(other_auth_client, test_run):
    response = other_auth_client.post(f"/{test_run.invite_code}/claim/mage/approve")
    assert response.status_code == 403


def test_approve_claim_not_pending(runs_auth_client, test_run):
    response = runs_auth_client.post(f"/{test_run.invite_code}/claim/mage/approve")
    assert response.status_code == 403


def test_reject_claim_success(
    runs_auth_client, other_auth_client, test_run, other_user
):
    other_auth_client.post(f"/{test_run.invite_code}/join")
    runs_auth_client.post(f"/{test_run.invite_code}/accept/{other_user.id}")
    other_auth_client.post(f"/{test_run.invite_code}/claim/mage")

    response = runs_auth_client.post(f"/{test_run.invite_code}/claim/mage/reject")
    assert response.status_code == 200
    assert not any(c["character_id"] == "mage" for c in response.data["pending_claims"])


def test_reject_claim_non_owner(other_auth_client, test_run):
    response = other_auth_client.post(f"/{test_run.invite_code}/claim/mage/reject")
    assert response.status_code == 403


def test_reject_claim_not_pending(runs_auth_client, test_run):
    response = runs_auth_client.post(f"/{test_run.invite_code}/claim/mage/reject")
    assert response.status_code == 403
