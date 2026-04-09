"""
Tests for the build import system:
  - Importer factory (source detection, URL routing)
  - Last Epoch Tools importer (parsing, mapping)
  - Maxroll importer (parsing, mapping)
  - Import endpoint (success, failure, partial)
  - Admin import-failures endpoint (auth, pagination)
  - Discord notifier (graceful failure handling)
"""

import json
from unittest.mock import patch, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Importer Factory
# ---------------------------------------------------------------------------

class TestImporterFactory:
    def test_detects_lastepochtools(self):
        from app.services.importers import detect_source
        assert detect_source("https://www.lastepochtools.com/planner/B4XdLG56") == "lastepochtools"

    def test_detects_maxroll(self):
        from app.services.importers import detect_source
        assert detect_source("https://maxroll.gg/last-epoch/planner/zge0t60e") == "maxroll"

    def test_detects_maxroll_with_hash(self):
        from app.services.importers import detect_source
        assert detect_source("https://maxroll.gg/last-epoch/planner/zge0t60e#2") == "maxroll"

    def test_unsupported_url_raises(self):
        from app.services.importers import detect_source
        with pytest.raises(ValueError, match="Unsupported URL"):
            detect_source("https://example.com/some-build")

    def test_get_importer_lastepochtools(self):
        from app.services.importers import get_importer, LastEpochToolsImporter
        importer = get_importer("https://www.lastepochtools.com/planner/ABCD1234")
        assert isinstance(importer, LastEpochToolsImporter)

    def test_get_importer_maxroll(self):
        from app.services.importers import get_importer, MaxrollImporter
        importer = get_importer("https://maxroll.gg/last-epoch/planner/abc123")
        assert isinstance(importer, MaxrollImporter)

    def test_get_importer_unsupported(self):
        from app.services.importers import get_importer
        with pytest.raises(ValueError):
            get_importer("https://unknown-site.com/build/123")


# ---------------------------------------------------------------------------
# Last Epoch Tools Importer
# ---------------------------------------------------------------------------

# Sample LE Tools HTML with embedded buildInfo
_LET_HTML = '''
<html><head></head><body>
<script>
window["buildInfo"] = {
    "bio": {
        "level": 85,
        "characterClass": 3,
        "chosenMastery": 2
    },
    "charTree": {
        "selected": {"10": 5, "20": 3, "30": 1}
    },
    "skillTrees": [
        {
            "treeID": "dl73",
            "selected": {"1": 3, "2": 2},
            "level": 20,
            "slotNumber": 0
        },
        {
            "treeID": "rb31pl",
            "selected": {"5": 1},
            "level": 15,
            "slotNumber": 1
        }
    ],
    "hud": ["dl73", "rb31pl", "", "", ""]
};
</script>
</body></html>
'''


class TestLastEpochToolsImporter:
    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_parse_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = _LET_HTML
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        importer = LastEpochToolsImporter()
        result = importer.parse("https://www.lastepochtools.com/planner/B4XdLG56")

        assert result.success is True
        assert result.source == "lastepochtools"
        assert result.build_data is not None
        assert result.build_data["character_class"] == "Acolyte"
        assert result.build_data["mastery"] == "Lich"
        assert result.build_data["level"] == 85

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_maps_passive_tree(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = _LET_HTML
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/B4XdLG56")

        passive = result.build_data["passive_tree"]
        # node 10 x5 + node 20 x3 + node 30 x1 = 9 total
        assert len(passive) == 9
        assert passive.count(10) == 5
        assert passive.count(20) == 3
        assert passive.count(30) == 1

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_maps_skills(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = _LET_HTML
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/B4XdLG56")

        skills = result.build_data["skills"]
        assert len(skills) == 2
        # First skill from HUD position 0
        assert skills[0]["slot"] == 0
        assert skills[0]["points_allocated"] == 20
        assert len(skills[0]["spec_tree"]) == 5  # node 1 x3 + node 2 x2

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_puts_unknown_skill_ids_in_missing_fields(self, mock_get):
        # Use a fake tree ID that won't be in skills_metadata
        html = _LET_HTML.replace('"dl73"', '"unknown_id"')
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/B4XdLG56")

        assert result.success is True
        assert any("skill_id:unknown_id" in f for f in result.missing_fields)

    def test_invalid_url_returns_failure(self):
        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://example.com/not-a-build")
        assert result.success is False
        assert "Invalid URL" in result.error_message

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_404_returns_failure(self, mock_get):
        from requests import HTTPError
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.raise_for_status = MagicMock(
            side_effect=HTTPError(response=mock_resp)
        )
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/INVALID")
        assert result.success is False
        assert "not found" in result.error_message.lower()


# ---------------------------------------------------------------------------
# Maxroll Importer
# ---------------------------------------------------------------------------

class TestMaxrollImporter:
    @patch("app.services.importers.maxroll_importer._requests.get")
    def test_parse_from_api(self, mock_get):
        """Maxroll API returns JSON with class/mastery/skills."""
        api_data = {
            "data": {
                "class": "Mage",
                "mastery": "Sorcerer",
                "level": 90,
                "passives": {"100": 3, "200": 5},
                "skills": [
                    {
                        "name": "Fireball",
                        "slot": 0,
                        "level": 20,
                        "nodes": {"1": 4, "2": 2},
                    }
                ],
                "equipment": [],
            }
        }

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = api_data
        mock_get.return_value = mock_resp

        from app.services.importers import MaxrollImporter
        result = MaxrollImporter().parse("https://maxroll.gg/last-epoch/planner/zge0t60e")

        assert result.success is True
        assert result.source == "maxroll"
        assert result.build_data["character_class"] == "Mage"
        assert result.build_data["mastery"] == "Sorcerer"
        assert result.build_data["level"] == 90

    @patch("app.services.importers.maxroll_importer._requests.get")
    def test_maps_passives_and_skills(self, mock_get):
        api_data = {
            "data": {
                "class": "Acolyte",
                "mastery": "Necromancer",
                "level": 70,
                "passives": {"5": 2, "10": 4},
                "skills": [
                    {"name": "Summon Skeleton", "slot": 0, "level": 20, "nodes": {"1": 3}},
                ],
            }
        }
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = api_data
        mock_get.return_value = mock_resp

        from app.services.importers import MaxrollImporter
        result = MaxrollImporter().parse("https://maxroll.gg/last-epoch/planner/test123")

        assert len(result.build_data["passive_tree"]) == 6  # 2+4
        assert len(result.build_data["skills"]) == 1
        assert result.build_data["skills"][0]["skill_name"] == "Summon Skeleton"
        assert len(result.build_data["skills"][0]["spec_tree"]) == 3

    @patch("app.services.importers.maxroll_importer._requests.get")
    def test_missing_class_is_hard_failure(self, mock_get):
        api_data = {"data": {"level": 70}}  # No class field
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = api_data
        mock_get.return_value = mock_resp

        from app.services.importers import MaxrollImporter
        result = MaxrollImporter().parse("https://maxroll.gg/last-epoch/planner/test")

        assert result.success is False
        assert "character_class" in result.missing_fields

    def test_invalid_url_returns_failure(self):
        from app.services.importers import MaxrollImporter
        result = MaxrollImporter().parse("https://example.com/not-maxroll")
        assert result.success is False


# ---------------------------------------------------------------------------
# Import Endpoint
# ---------------------------------------------------------------------------

class TestImportEndpoint:
    @patch("app.routes.import_route.get_importer")
    def test_success_creates_build(self, mock_factory, client, db):
        from app.services.importers.base_importer import ImportResult
        mock_importer = MagicMock()
        mock_importer.parse.return_value = ImportResult(
            success=True,
            source="lastepochtools",
            build_data={
                "name": "Test Import",
                "character_class": "Sentinel",
                "mastery": "Paladin",
                "level": 80,
                "passive_tree": [1, 2, 3],
                "skills": [],
                "gear": [],
            },
            missing_fields=[],
        )
        mock_factory.return_value = mock_importer

        resp = client.post(
            "/api/import/build",
            json={"url": "https://www.lastepochtools.com/planner/TEST1234"},
            content_type="application/json",
        )

        assert resp.status_code == 201
        data = resp.get_json()
        assert data["data"]["slug"] is not None
        assert data["data"]["source"] == "lastepochtools"
        assert data["data"]["build_name"] == "Test Import"
        assert data["data"]["missing_fields"] == []

    @patch("app.routes.import_route.get_importer")
    @patch("app.routes.import_route.send_import_failure_alert")
    def test_hard_failure_creates_import_failure(self, mock_alert, mock_factory, client, db):
        from app.services.importers.base_importer import ImportResult
        from app.models import ImportFailure

        mock_importer = MagicMock()
        mock_importer.parse.return_value = ImportResult(
            success=False,
            source="lastepochtools",
            error_message="Could not parse class",
            missing_fields=["character_class"],
        )
        mock_factory.return_value = mock_importer

        resp = client.post(
            "/api/import/build",
            json={"url": "https://www.lastepochtools.com/planner/BAD"},
            content_type="application/json",
        )

        assert resp.status_code == 422
        # Check ImportFailure was created
        failures = ImportFailure.query.all()
        assert len(failures) == 1
        assert failures[0].source == "lastepochtools"
        assert failures[0].error_message == "Could not parse class"
        # Discord alert was fired
        mock_alert.assert_called_once()

    @patch("app.routes.import_route.get_importer")
    @patch("app.routes.import_route.send_import_failure_alert")
    def test_partial_import_returns_warnings(self, mock_alert, mock_factory, client, db):
        from app.services.importers.base_importer import ImportResult

        mock_importer = MagicMock()
        mock_importer.parse.return_value = ImportResult(
            success=True,
            source="maxroll",
            build_data={
                "name": "Partial Import",
                "character_class": "Mage",
                "mastery": "Sorcerer",
                "level": 75,
                "passive_tree": [],
                "skills": [],
                "gear": [],
            },
            missing_fields=["skill_id:unknown_abc"],
        )
        mock_factory.return_value = mock_importer

        resp = client.post(
            "/api/import/build",
            json={"url": "https://maxroll.gg/last-epoch/planner/PARTIAL"},
            content_type="application/json",
        )

        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert len(data["warnings"]) > 0
        assert data["missing_fields"] == ["skill_id:unknown_abc"]
        # Discord alert fires with severity "partial"
        mock_alert.assert_called_once()
        call_args = mock_alert.call_args
        assert call_args[1]["severity"] == "partial" or call_args[0][1] == "partial"

    def test_missing_url_returns_400(self, client):
        resp = client.post(
            "/api/import/build",
            json={},
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_unsupported_url_returns_400(self, client):
        resp = client.post(
            "/api/import/build",
            json={"url": "https://unknown.com/build/123"},
            content_type="application/json",
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Admin Import Failures Endpoint
# ---------------------------------------------------------------------------

class TestAdminImportFailures:
    def test_returns_403_for_non_admin(self, client, auth_headers, user, db):
        """Non-admin authenticated user gets 403."""
        resp = client.get("/api/admin/import-failures", headers=auth_headers)
        assert resp.status_code == 403

    def test_returns_401_for_unauthenticated(self, client):
        resp = client.get("/api/admin/import-failures")
        assert resp.status_code == 401

    def test_returns_paginated_results_for_admin(self, client, db, user):
        """Admin user gets paginated import failures."""
        from flask_jwt_extended import create_access_token
        from flask import current_app
        from app.models import ImportFailure

        # Make user admin
        user.is_admin = True
        db.session.commit()

        # Create some test failures
        for i in range(3):
            f = ImportFailure(
                source="lastepochtools",
                raw_url=f"https://example.com/test-{i}",
                missing_fields=["field_a"],
                error_message=f"Error {i}",
            )
            db.session.add(f)
        db.session.commit()

        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get("/api/admin/import-failures", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["data"]) == 3
        assert data["meta"]["total"] == 3


# ---------------------------------------------------------------------------
# Discord Notifier
# ---------------------------------------------------------------------------

class TestDiscordNotifier:
    @patch("app.services.discord_notifier.WEBHOOK_URL", "")
    def test_does_not_crash_without_webhook_url(self):
        """When webhook URL is not set, just logs and returns."""
        from app.services.discord_notifier import send_import_failure_alert
        mock_failure = MagicMock()
        mock_failure.id = "test-id"
        mock_failure.source = "lastepochtools"
        mock_failure.raw_url = "https://example.com"
        mock_failure.missing_fields = []
        mock_failure.error_message = "Test error"
        mock_failure.user_id = None
        mock_failure.created_at = None

        # Should not raise
        send_import_failure_alert(mock_failure)

    @patch("app.services.discord_notifier.WEBHOOK_URL", "https://discord.example.com/webhook")
    @patch("app.services.discord_notifier.requests.post")
    def test_does_not_crash_on_webhook_failure(self, mock_post):
        """When webhook POST fails, logs error but doesn't crash."""
        mock_post.side_effect = Exception("Connection refused")

        from app.services.discord_notifier import _post_alert
        mock_failure = MagicMock()
        mock_failure.id = "test-id"
        mock_failure.source = "maxroll"
        mock_failure.raw_url = "https://example.com"
        mock_failure.missing_fields = ["field_a"]
        mock_failure.error_message = "Test error"
        mock_failure.user_id = None
        mock_failure.created_at = None

        # Should not raise — just logs the error
        _post_alert(mock_failure, severity="hard")

    @patch("app.services.discord_notifier.WEBHOOK_URL", "https://discord.example.com/webhook")
    @patch("app.services.discord_notifier.requests.post")
    def test_sends_correct_embed_format(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        from app.services.discord_notifier import _post_alert
        mock_failure = MagicMock()
        mock_failure.id = "embed-test"
        mock_failure.source = "lastepochtools"
        mock_failure.raw_url = "https://lastepochtools.com/planner/ABC"
        mock_failure.missing_fields = ["mastery", "skill_id:xyz"]
        mock_failure.error_message = "Partial import"
        mock_failure.user_id = "user-123"
        mock_failure.created_at = None

        _post_alert(mock_failure, severity="partial")

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        payload = call_kwargs["json"]
        embed = payload["embeds"][0]

        assert "Partial Import" in embed["title"]
        assert embed["color"] == 0xFF8C00  # orange for partial
        assert any(f["name"] == "URL" for f in embed["fields"])
        assert any(f["name"] == "User ID" for f in embed["fields"])


# ---------------------------------------------------------------------------
# Base Importer Validation
# ---------------------------------------------------------------------------

class TestBaseImporterValidation:
    def test_validates_known_class(self):
        from app.services.importers.base_importer import BaseImporter, ImportResult

        class DummyImporter(BaseImporter):
            source_name = "test"
            def parse(self, url):
                return ImportResult(success=True)

        result = ImportResult(
            success=True,
            build_data={
                "character_class": "Acolyte",
                "mastery": "Lich",
                "skills": [],
            },
        )
        validated = DummyImporter().validate(result)
        # "Acolyte" and "Lich" are valid — no missing fields for them
        assert not any("class:Acolyte" in f for f in validated.missing_fields)
        assert not any("mastery:Lich" in f for f in validated.missing_fields)

    def test_flags_unknown_class(self):
        from app.services.importers.base_importer import BaseImporter, ImportResult

        class DummyImporter(BaseImporter):
            source_name = "test"
            def parse(self, url):
                return ImportResult(success=True)

        result = ImportResult(
            success=True,
            build_data={
                "character_class": "FakeClass",
                "mastery": "FakeMastery",
                "skills": [],
            },
        )
        validated = DummyImporter().validate(result)
        assert any("class:FakeClass" in f for f in validated.missing_fields)
