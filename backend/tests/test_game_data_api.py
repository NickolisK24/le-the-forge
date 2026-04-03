"""J14 — Tests for POST /api/load/game-data"""

import pytest


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
