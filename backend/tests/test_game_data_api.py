"""J14 — Tests for POST /api/load/game-data

The reload endpoint is admin-only and disabled unless GAME_DATA_MUTATION_ENABLED
is set (see test_r0_game_data_mutation.py for the denial cases). These tests
exercise the authorized operator path.
"""

import pytest
from flask_jwt_extended import create_access_token

from app.models import User


@pytest.fixture
def client(app, db, monkeypatch):
    monkeypatch.setitem(app.config, "GAME_DATA_MUTATION_ENABLED", True)
    admin = User(discord_id="j14-admin", username="J14Admin", is_admin=True)
    db.session.add(admin)
    db.session.commit()
    with app.app_context():
        token = create_access_token(identity=admin.id)
    test_client = app.test_client()
    test_client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    return test_client


class TestDataLoadingRequestValidation:
    def test_load_endpoint_returns_200(self, client):
        resp = client.post("/api/load/game-data")
        assert resp.status_code == 200

    def test_response_has_version_field(self, client):
        resp = client.post("/api/load/game-data")
        body = resp.get_json()
        assert "data" in body
        assert "version" in body["data"]

    def test_response_has_counts(self, client):
        resp = client.post("/api/load/game-data")
        body = resp.get_json()
        counts = body["data"]["counts"]
        assert "skills" in counts
        assert "affixes" in counts
        assert "enemies" in counts
        assert "passives" in counts


class TestResponseIntegrity:
    def test_counts_are_positive(self, client):
        resp = client.post("/api/load/game-data")
        counts = resp.get_json()["data"]["counts"]
        assert counts["skills"] > 0
        assert counts["affixes"] > 0

    def test_integrity_summary_present(self, client):
        resp = client.post("/api/load/game-data")
        integrity = resp.get_json()["data"]["integrity"]
        assert "total" in integrity
        assert "errors" in integrity

    def test_issues_list_present(self, client):
        resp = client.post("/api/load/game-data")
        body = resp.get_json()["data"]
        assert "issues" in body
        assert isinstance(body["issues"], list)
