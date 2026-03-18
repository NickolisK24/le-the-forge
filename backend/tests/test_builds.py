"""
Tests for the builds API — CRUD routes + voting.
"""

import json
import pytest


VALID_BUILD = {
    "name": "Bone Curse Lich",
    "description": "The ward-stacking powerhouse.",
    "character_class": "Acolyte",
    "mastery": "Lich",
    "passive_tree": [1, 5, 12, 20, 33],
    "is_ssf": True,
    "is_ladder_viable": True,
    "patch_version": "1.2.1",
}


class TestBuildCRUD:

    def test_create_build_returns_201(self, client):
        resp = client.post("/api/builds", json=VALID_BUILD)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["data"]["name"] == "Bone Curse Lich"
        assert data["data"]["slug"] is not None

    def test_create_build_invalid_class(self, client):
        bad = {**VALID_BUILD, "character_class": "InvalidClass"}
        resp = client.post("/api/builds", json=bad)
        assert resp.status_code == 422
        errors = resp.get_json()["errors"]
        assert any("character_class" in (e.get("field", "")) for e in errors)

    def test_create_build_mastery_mismatch(self, client):
        bad = {**VALID_BUILD, "character_class": "Mage", "mastery": "Necromancer"}
        resp = client.post("/api/builds", json=bad)
        assert resp.status_code == 422

    def test_get_build_by_slug(self, client, sample_build):
        resp = client.get(f"/api/builds/{sample_build.slug}")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["slug"] == sample_build.slug
        assert data["character_class"] == "Acolyte"

    def test_get_nonexistent_build_returns_404(self, client):
        resp = client.get("/api/builds/does-not-exist")
        assert resp.status_code == 404

    def test_list_builds_returns_paginated(self, client, sample_build):
        resp = client.get("/api/builds")
        assert resp.status_code == 200
        body = resp.get_json()
        assert "data" in body
        assert "meta" in body
        assert "page" in body["meta"]
        assert isinstance(body["data"], list)

    def test_list_builds_filter_by_class(self, client, sample_build):
        resp = client.get("/api/builds?class=Acolyte")
        assert resp.status_code == 200
        builds = resp.get_json()["data"]
        for b in builds:
            assert b["character_class"] == "Acolyte"

    def test_update_build_requires_auth(self, client, sample_build):
        resp = client.patch(f"/api/builds/{sample_build.slug}", json={"name": "New Name"})
        assert resp.status_code == 401

    def test_update_build_as_owner(self, client, sample_build, auth_headers):
        resp = client.patch(
            f"/api/builds/{sample_build.slug}",
            json={"name": "Updated Lich Build"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["data"]["name"] == "Updated Lich Build"

    def test_delete_build_requires_auth(self, client, sample_build):
        resp = client.delete(f"/api/builds/{sample_build.slug}")
        assert resp.status_code == 401

    def test_delete_build_as_owner(self, client, sample_build, auth_headers):
        resp = client.delete(
            f"/api/builds/{sample_build.slug}",
            headers=auth_headers,
        )
        assert resp.status_code == 204

        # Verify gone
        resp2 = client.get(f"/api/builds/{sample_build.slug}")
        assert resp2.status_code == 404

    def test_view_count_increments(self, client, sample_build):
        initial_views = sample_build.view_count or 0
        client.get(f"/api/builds/{sample_build.slug}")
        client.get(f"/api/builds/{sample_build.slug}")
        from app.models import Build
        refreshed = Build.query.get(sample_build.id)
        assert (refreshed.view_count or 0) >= initial_views + 1


class TestVoting:

    def test_vote_requires_auth(self, client, sample_build):
        resp = client.post(
            f"/api/builds/{sample_build.slug}/vote",
            json={"direction": 1},
        )
        assert resp.status_code == 401

    def test_upvote_increases_count(self, client, sample_build, auth_headers):
        initial = sample_build.vote_count
        resp = client.post(
            f"/api/builds/{sample_build.slug}/vote",
            json={"direction": 1},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["data"]["vote_count"] == initial + 1

    def test_voting_same_direction_toggles_off(self, client, sample_build, auth_headers):
        # First vote
        client.post(
            f"/api/builds/{sample_build.slug}/vote",
            json={"direction": 1},
            headers=auth_headers,
        )
        # Second vote same direction — should toggle off
        resp = client.post(
            f"/api/builds/{sample_build.slug}/vote",
            json={"direction": 1},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["user_vote"] == 0

    def test_invalid_vote_direction(self, client, sample_build, auth_headers):
        resp = client.post(
            f"/api/builds/{sample_build.slug}/vote",
            json={"direction": 2},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_downvote(self, client, sample_build, auth_headers):
        resp = client.post(
            f"/api/builds/{sample_build.slug}/vote",
            json={"direction": -1},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["user_vote"] == -1


class TestMetaSnapshot:

    def test_snapshot_returns_expected_keys(self, client, sample_build):
        resp = client.get("/api/builds/meta/snapshot")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert "total_builds" in data
        assert "class_distribution" in data
        assert "s_tier_builds" in data
