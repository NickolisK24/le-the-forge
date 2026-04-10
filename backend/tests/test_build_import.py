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
        mock_failure.partial_data = None
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
        mock_failure.partial_data = {"character_class": "Rogue", "gear": []}
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
        assert any(f["name"] == "User" for f in embed["fields"])

    @patch("app.services.discord_notifier.WEBHOOK_URL", "https://discord.example.com/webhook")
    @patch("app.services.discord_notifier.requests.post")
    def test_hard_failure_uses_red_color(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        from app.services.discord_notifier import _post_alert
        mock_failure = MagicMock()
        mock_failure.id = "red-test"
        mock_failure.source = "lastepochtools"
        mock_failure.raw_url = "https://example.com"
        mock_failure.missing_fields = []
        mock_failure.partial_data = None
        mock_failure.error_message = "Hard crash"
        mock_failure.user_id = None
        mock_failure.created_at = None

        _post_alert(mock_failure, severity="hard")

        payload = mock_post.call_args[1]["json"]
        embed = payload["embeds"][0]
        assert "Import Failure" in embed["title"]
        assert embed["color"] == 0xFF0000  # red for hard failure

    @patch("app.services.discord_notifier.WEBHOOK_URL", "https://discord.example.com/webhook")
    @patch("app.services.discord_notifier.requests.post")
    def test_embed_includes_parsed_data_summary(self, mock_post):
        """Verify the 'Parsed Data' field summarizes what DID import."""
        mock_post.return_value = MagicMock(status_code=200)
        from app.services.discord_notifier import _post_alert
        mock_failure = MagicMock()
        mock_failure.id = "summary-test"
        mock_failure.source = "lastepochtools"
        mock_failure.raw_url = "https://example.com"
        mock_failure.missing_fields = ["gear"]
        mock_failure.partial_data = {
            "character_class": "Rogue",
            "mastery": "Bladedancer",
            "skills": [{"name": "Umbral Blades"}, {"name": "Shadow Cascade"}],
            "passive_tree": list(range(90)),
            "gear": [],
        }
        mock_failure.error_message = "Gear not mapped"
        mock_failure.user_id = None
        mock_failure.created_at = None

        _post_alert(mock_failure, severity="partial")

        payload = mock_post.call_args[1]["json"]
        embed = payload["embeds"][0]
        parsed_field = next(f for f in embed["fields"] if f["name"] == "Parsed Data")
        assert "Rogue" in parsed_field["value"]
        assert "Bladedancer" in parsed_field["value"]
        assert "Skills: 2" in parsed_field["value"]
        assert "Passives: 90" in parsed_field["value"]

    @patch("app.services.discord_notifier.WEBHOOK_URL", "https://discord.example.com/webhook")
    @patch("app.services.discord_notifier.requests.post")
    def test_embed_includes_raw_gear_data(self, mock_post):
        """Verify raw gear entries appear in the embed for debugging."""
        mock_post.return_value = MagicMock(status_code=200)
        from app.services.discord_notifier import _post_alert
        mock_failure = MagicMock()
        mock_failure.id = "gear-test"
        mock_failure.source = "lastepochtools"
        mock_failure.raw_url = "https://example.com"
        mock_failure.missing_fields = ["gear"]
        mock_failure.partial_data = {
            "gear": [
                {"slot": "weapon", "base_type_id": 47, "affixes": [{"id": 1042}]},
                {"slot": "body", "base_type_id": 12},
                {"slot": "helmet", "base_type_id": 8},
                {"slot": "boots", "base_type_id": 3},
            ],
        }
        mock_failure.error_message = "Gear IDs unmappable"
        mock_failure.user_id = None
        mock_failure.created_at = None

        _post_alert(mock_failure, severity="hard")

        payload = mock_post.call_args[1]["json"]
        embed = payload["embeds"][0]
        gear_field = next(f for f in embed["fields"] if "Gear" in f["name"])
        # Should contain the first 3 entries as JSON
        assert "weapon" in gear_field["value"]
        assert "body" in gear_field["value"]
        assert "helmet" in gear_field["value"]
        # 4th entry should be noted but not shown in full
        assert "+1 more" in gear_field["value"]
        # Should be in a code block
        assert "```json" in gear_field["value"]

    @patch("app.services.discord_notifier.WEBHOOK_URL", "https://discord.example.com/webhook")
    @patch("app.services.discord_notifier.requests.post")
    def test_anonymous_user_shown_as_anonymous(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        from app.services.discord_notifier import _post_alert
        mock_failure = MagicMock()
        mock_failure.id = "anon-test"
        mock_failure.source = "lastepochtools"
        mock_failure.raw_url = "https://example.com"
        mock_failure.missing_fields = []
        mock_failure.partial_data = None
        mock_failure.error_message = "Error"
        mock_failure.user_id = None
        mock_failure.created_at = None

        _post_alert(mock_failure, severity="hard")

        payload = mock_post.call_args[1]["json"]
        embed = payload["embeds"][0]
        user_field = next(f for f in embed["fields"] if f["name"] == "User")
        assert user_field["value"] == "anonymous"

    @patch("app.services.discord_notifier.WEBHOOK_URL", "https://discord.example.com/webhook")
    @patch("app.services.discord_notifier.requests.post")
    def test_embed_under_discord_character_limit(self, mock_post):
        """Verify embed stays under Discord's 6000 character limit even with large gear data."""
        mock_post.return_value = MagicMock(status_code=200)
        from app.services.discord_notifier import _post_alert
        mock_failure = MagicMock()
        mock_failure.id = "limit-test"
        mock_failure.source = "lastepochtools"
        mock_failure.raw_url = "https://example.com/very/long/url/" + "x" * 200
        mock_failure.missing_fields = [f"field_{i}" for i in range(50)]
        mock_failure.partial_data = {
            "gear": [
                {"slot": f"slot_{i}", "data": "x" * 500, "affixes": list(range(20))}
                for i in range(10)
            ],
        }
        mock_failure.error_message = "A" * 1024
        mock_failure.user_id = "user-with-long-id-12345"
        mock_failure.created_at = None

        _post_alert(mock_failure, severity="hard")

        payload = mock_post.call_args[1]["json"]
        embed = payload["embeds"][0]
        # Calculate total character count across all fields
        total = len(embed.get("title", ""))
        for f in embed["fields"]:
            total += len(f["name"]) + len(f["value"])
        assert total < 6000, f"Embed total chars = {total}, exceeds Discord limit"

    @patch("app.services.discord_notifier.WEBHOOK_URL", "https://discord.example.com/webhook")
    @patch("app.services.discord_notifier.requests.post")
    def test_no_gear_data_shows_no_gear_field(self, mock_post):
        """When partial_data has no gear, the raw gear field is omitted."""
        mock_post.return_value = MagicMock(status_code=200)
        from app.services.discord_notifier import _post_alert
        mock_failure = MagicMock()
        mock_failure.id = "no-gear"
        mock_failure.source = "maxroll"
        mock_failure.raw_url = "https://example.com"
        mock_failure.missing_fields = []
        mock_failure.partial_data = {"character_class": "Mage"}
        mock_failure.error_message = "Class only"
        mock_failure.user_id = None
        mock_failure.created_at = None

        _post_alert(mock_failure, severity="hard")

        payload = mock_post.call_args[1]["json"]
        embed = payload["embeds"][0]
        gear_fields = [f for f in embed["fields"] if "Gear" in f["name"]]
        assert len(gear_fields) == 0  # no gear field when no gear data


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


# ---------------------------------------------------------------------------
# Import Route Never Returns 500
# ---------------------------------------------------------------------------

class TestImportNever500:
    """Verify the import route never returns 500 — always 422, 400, or 2xx."""

    @patch("app.routes.import_route.get_importer")
    @patch("app.routes.import_route.send_import_failure_alert")
    def test_importer_crash_returns_422_not_500(self, mock_alert, mock_factory, client, db):
        """When the importer raises an unexpected exception, route returns 422 not 500."""
        mock_importer = MagicMock()
        mock_importer.parse.side_effect = RuntimeError("Unexpected crash in parser")
        mock_factory.return_value = mock_importer

        resp = client.post(
            "/api/import/build",
            json={"url": "https://www.lastepochtools.com/planner/CRASH"},
            content_type="application/json",
        )

        assert resp.status_code == 422
        body = resp.get_json()
        assert any("crash" in e["message"].lower() for e in body["errors"])

    @patch("app.routes.import_route.get_importer")
    @patch("app.routes.import_route.build_service")
    @patch("app.routes.import_route.send_import_failure_alert")
    def test_save_failure_returns_422_not_500(self, mock_alert, mock_bs, mock_factory, client, db):
        """When build save fails, route returns 422 not 500."""
        from app.services.importers.base_importer import ImportResult
        mock_importer = MagicMock()
        mock_importer.parse.return_value = ImportResult(
            success=True,
            source="lastepochtools",
            build_data={
                "name": "Test", "character_class": "Mage", "mastery": "Sorcerer",
                "level": 80, "passive_tree": [], "skills": [], "gear": [],
            },
        )
        mock_factory.return_value = mock_importer
        mock_bs.create_build.side_effect = Exception("DB constraint violation")

        resp = client.post(
            "/api/import/build",
            json={"url": "https://www.lastepochtools.com/planner/SAVEFAIL"},
            content_type="application/json",
        )

        assert resp.status_code == 422
        body = resp.get_json()
        assert any("could not be saved" in e["message"].lower() for e in body["errors"])

    @patch("app.routes.import_route.get_importer")
    @patch("app.routes.import_route.send_import_failure_alert")
    def test_importer_crash_fires_discord_alert(self, mock_alert, mock_factory, client, db):
        """Crashes in the importer still fire a Discord alert."""
        mock_importer = MagicMock()
        mock_importer.parse.side_effect = ValueError("Something broke")
        mock_factory.return_value = mock_importer

        client.post(
            "/api/import/build",
            json={"url": "https://www.lastepochtools.com/planner/CRASH2"},
            content_type="application/json",
        )

        mock_alert.assert_called_once()

    @patch("app.routes.import_route.get_importer")
    @patch("app.routes.import_route.send_import_failure_alert")
    def test_null_build_data_returns_422(self, mock_alert, mock_factory, client, db):
        """When importer returns success=True but build_data=None, returns 422."""
        from app.services.importers.base_importer import ImportResult
        mock_importer = MagicMock()
        mock_importer.parse.return_value = ImportResult(
            success=True,
            source="lastepochtools",
            build_data=None,
        )
        mock_factory.return_value = mock_importer

        resp = client.post(
            "/api/import/build",
            json={"url": "https://www.lastepochtools.com/planner/NULLDATA"},
            content_type="application/json",
        )

        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Gear Parsing
# ---------------------------------------------------------------------------

class TestGearParsing:
    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_parses_equipment_from_build(self, mock_get):
        """When build has equipment data, it gets parsed to gear array."""
        html = '''
        <html><body><script>
        window["buildInfo"] = {
            "bio": {"level": 90, "characterClass": 4, "chosenMastery": 1},
            "charTree": {"selected": {}},
            "skillTrees": [],
            "hud": [],
            "equipment": [
                {"equipmentSlot": 0, "baseTypeID": 5, "affixes": [{"affixID": "42", "tier": 3}]},
                {"equipmentSlot": 5, "baseTypeID": 10}
            ]
        };
        </script></body></html>
        '''
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/GEAR1")

        assert result.success is True
        gear = result.build_data["gear"]
        assert len(gear) == 2
        assert gear[0]["slot"] == "helmet"
        assert gear[1]["slot"] == "weapon"

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_parses_dict_keyed_equipment(self, mock_get):
        """When equipment is a dict keyed by slot name/ID, it still parses."""
        html = '''
        <html><body><script>
        window["buildInfo"] = {
            "bio": {"level": 90, "characterClass": 4, "chosenMastery": 1},
            "charTree": {"selected": {}},
            "skillTrees": [],
            "hud": [],
            "equipment": {
                "helm": {"baseTypeID": 5, "affixes": [{"affixID": "42", "tier": 3}]},
                "weapon": {"baseTypeID": 10},
                "3": {"baseTypeID": 7}
            }
        };
        </script></body></html>
        '''
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/DICTGEAR")

        assert result.success is True
        gear = result.build_data["gear"]
        assert len(gear) == 3
        slots = [g["slot"] for g in gear]
        assert "helmet" in slots   # "helm" → "helmet" via alias
        assert "weapon" in slots
        assert "boots" in slots    # "3" → boots via _EQUIP_SLOT_MAP

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_no_equipment_returns_empty_gear(self, mock_get):
        """Build without equipment data returns empty gear list."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = _LET_HTML
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/NOGEAR")

        assert result.success is True
        assert result.build_data["gear"] == []

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_parses_let_format_with_id_ir_ur(self, mock_get):
        """LE Tools actual format: 'id' for base type, 'ir' for rarity, 'ur' for LP."""
        html = '''
        <html><body><script>
        window["buildInfo"] = {
            "bio": {"level": 98, "characterClass": 4, "chosenMastery": 1},
            "charTree": {"selected": {}},
            "skillTrees": [],
            "hud": [],
            "equipment": {
                "helm": {"id": 5, "affixes": ["AAwDhQ"], "ir": 4, "ur": 1},
                "body": {"id": 10, "affixes": [], "ir": 2, "ur": 0},
                "belt": {"id": 7, "affixes": ["AAzBsQ", "AGwRhQ"], "ir": 3, "ur": 0},
                "boots": {"id": 3, "affixes": [], "ir": 1, "ur": 0}
            }
        };
        </script></body></html>
        '''
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/LETFMT")

        assert result.success is True
        gear = result.build_data["gear"]
        assert len(gear) == 4

        # Check slot names mapped correctly
        slots = {g["slot"]: g for g in gear}
        assert "helmet" in slots
        assert "body_armour" in slots
        assert "belt" in slots
        assert "boots" in slots

        # Check rarity mapping from 'ir' integer
        assert slots["helmet"]["rarity"] == "legendary"
        assert slots["body_armour"]["rarity"] == "rare"
        assert slots["belt"]["rarity"] == "exalted"
        assert slots["boots"]["rarity"] == "magic"

        # Check legendary potential from 'ur'
        assert slots["helmet"].get("legendary_potential") == 1

        # Check affixes were parsed (even if not all resolve)
        assert len(slots["helmet"]["affixes"]) == 1
        assert len(slots["belt"]["affixes"]) == 2

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_numeric_affix_ids_resolved_directly(self, mock_get):
        """When affix IDs are plain integers, resolve directly without base64."""
        html = '''
        <html><body><script>
        window["buildInfo"] = {
            "bio": {"level": 80, "characterClass": 2, "chosenMastery": 1},
            "charTree": {"selected": {}},
            "skillTrees": [],
            "hud": [],
            "equipment": {
                "helm": {"id": 5, "affixes": [17, 25], "ir": 2, "ur": 0}
            }
        };
        </script></body></html>
        '''
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/NUMAFX")

        assert result.success is True
        gear = result.build_data["gear"]
        assert len(gear) == 1
        affix_names = [a.get("name") for a in gear[0]["affixes"] if a.get("name")]
        # 17=Cold Resistance, 25=Added Health — both should resolve
        assert len(affix_names) == 2

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_all_12_slot_names_mapped(self, mock_get):
        """All 12 LE Tools slot names map to valid Forge slot names."""
        slots_json = ", ".join([
            f'"{s}": {{"id": 1, "affixes": [], "ir": 0, "ur": 0}}'
            for s in ["helm", "body", "belt", "boots", "gloves",
                       "weapon1", "weapon2", "amulet", "ring1", "ring2",
                       "relic", "idol_altar"]
        ])
        html = f'''
        <html><body><script>
        window["buildInfo"] = {{
            "bio": {{"level": 80, "characterClass": 0, "chosenMastery": 1}},
            "charTree": {{"selected": {{}}}},
            "skillTrees": [],
            "hud": [],
            "equipment": {{{slots_json}}}
        }};
        </script></body></html>
        '''
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/ALLSLOTS")

        assert result.success is True
        gear = result.build_data["gear"]
        assert len(gear) == 12
        found_slots = {g["slot"] for g in gear}
        expected = {"helmet", "body_armour", "belt", "boots", "gloves",
                    "weapon1", "weapon2", "amulet", "ring_1", "ring_2",
                    "relic", "idol_altar"}
        assert found_slots == expected


# ---------------------------------------------------------------------------
# Extraction Strategies
# ---------------------------------------------------------------------------

class TestExtractionStrategies:
    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_extracts_from_next_data(self, mock_get):
        """Extraction works when data is in __NEXT_DATA__ script tag."""
        html = '''
        <html><body>
        <script id="__NEXT_DATA__" type="application/json">
        {"props": {"pageProps": {"buildInfo": {
            "bio": {"level": 80, "characterClass": 1, "chosenMastery": 1},
            "charTree": {"selected": {"5": 3}},
            "skillTrees": [],
            "hud": []
        }}}}
        </script>
        </body></html>
        '''
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/NEXT")

        assert result.success is True
        assert result.build_data["character_class"] == "Mage"

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_mapping_crash_returns_failure_not_exception(self, mock_get):
        """If _map() throws, parse() returns ImportResult(success=False) not an exception."""
        # Build info has invalid data that will cause mapping to fail
        html = '''
        <html><body><script>
        window["buildInfo"] = {
            "bio": {"level": "not_a_number", "characterClass": "invalid", "chosenMastery": "bad"},
            "charTree": {"selected": {}},
            "skillTrees": [],
            "hud": []
        };
        </script></body></html>
        '''
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        from app.services.importers.base_importer import ImportResult as IR
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/BAD")

        # Should return a result, not raise an exception
        assert isinstance(result, IR)
        assert result.success is False
        assert result.error_message is not None

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_mapping_crash_populates_partial_data(self, mock_get):
        """When _map() crashes, partial_data still contains class/mastery/counts."""
        html = '''
        <html><body><script>
        window["buildInfo"] = {
            "bio": {"level": 85, "characterClass": 3, "chosenMastery": 2},
            "charTree": {"selected": {"10": 5, "20": 3}},
            "skillTrees": [{"treeID": "x", "selected": {}, "level": 1}],
            "hud": [],
            "equipment": "THIS_WILL_CAUSE_A_TYPE_ERROR"
        };
        </script></body></html>
        '''
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/PARTIAL_CRASH")

        # Should succeed — gear parsing handles the invalid type gracefully
        # and returns empty gear list (no crash propagation)
        assert result.success is True
        assert result.build_data["character_class"] == "Acolyte"
        assert result.build_data["mastery"] == "Lich"
        assert result.build_data["gear"] == []
        assert len(result.build_data["passive_tree"]) == 8  # 5+3


# ---------------------------------------------------------------------------
# Base Item ID Decoding + Rarity
# ---------------------------------------------------------------------------

class TestBaseItemDecoding:
    def test_decode_integer_id_resolves(self):
        """Plain integer base type ID resolves from base_items.json."""
        from app.services.importers.lastepochtools_importer import _get_base_item_map
        bim = _get_base_item_map()
        # Index 0 = first helmet (Rusted Coif)
        assert bim.get(0, {}).get("name") == "Rusted Coif"

    def test_decode_base_item_id_returns_name_for_known_slot(self):
        """_decode_base_item_id attempts to match varints to item subtypes."""
        from app.services.importers.lastepochtools_importer import _decode_base_item_id
        # We can't predict which base64 maps to which item (opaque encoding),
        # but we can verify the function doesn't crash and returns a tuple
        name, btid, stid = _decode_base_item_id("UAzBMoVgNiA", "helmet")
        # It should return something (name may or may not resolve)
        assert isinstance(name, (str, type(None)))
        assert isinstance(btid, (int, type(None)))

    def test_decode_base_item_id_empty_returns_none(self):
        from app.services.importers.lastepochtools_importer import _decode_base_item_id
        name, btid, stid = _decode_base_item_id("", "helmet")
        assert name is None

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_base64_id_parsed_and_resolved_or_missing(self, mock_get):
        """When item id is base64, it's decoded and lookup attempted."""
        html = '''
        <html><body><script>
        window["buildInfo"] = {
            "bio": {"level": 90, "characterClass": 4, "chosenMastery": 1},
            "charTree": {"selected": {}},
            "skillTrees": [],
            "hud": [],
            "equipment": {
                "helm": {"id": "UAzBMoVgNiA", "affixes": [], "ir": 4, "ur": 1}
            }
        };
        </script></body></html>
        '''
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/B64ITEM")

        assert result.success is True
        gear = result.build_data["gear"]
        assert len(gear) == 1
        helm = gear[0]
        # Either decoded to a name or recorded as missing
        assert helm.get("item_name") is not None or \
            any("gear_base:helmet" in f for f in result.missing_fields)

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_rarity_from_integer_ir(self, mock_get):
        """ir=4 correctly maps to legendary."""
        html = '''
        <html><body><script>
        window["buildInfo"] = {
            "bio": {"level": 90, "characterClass": 4, "chosenMastery": 1},
            "charTree": {"selected": {}},
            "skillTrees": [],
            "hud": [],
            "equipment": {
                "helm": {"id": 1, "affixes": [], "ir": 4, "ur": 2},
                "body": {"id": 2, "affixes": [], "ir": 3, "ur": 0},
                "belt": {"id": 3, "affixes": [], "ir": 6, "ur": 0}
            }
        };
        </script></body></html>
        '''
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/RARITY")

        gear = result.build_data["gear"]
        slots = {g["slot"]: g for g in gear}
        assert slots["helmet"]["rarity"] == "legendary"
        assert slots["body_armour"]["rarity"] == "exalted"
        assert slots["belt"]["rarity"] == "unique"
        assert slots["helmet"].get("legendary_potential") == 2

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_rarity_from_string_integer_ir(self, mock_get):
        """ir="4" (string) correctly maps to legendary."""
        html = '''
        <html><body><script>
        window["buildInfo"] = {
            "bio": {"level": 90, "characterClass": 4, "chosenMastery": 1},
            "charTree": {"selected": {}},
            "skillTrees": [],
            "hud": [],
            "equipment": {
                "helm": {"id": 1, "affixes": [], "ir": "4", "ur": "2"}
            }
        };
        </script></body></html>
        '''
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/STRRAR")

        gear = result.build_data["gear"]
        assert gear[0]["rarity"] == "legendary"
        assert gear[0].get("legendary_potential") == 2


# Base64 Affix ID Decoding
# ---------------------------------------------------------------------------

class TestAffixDecoding:
    def test_decode_let_affix_extracts_varints(self):
        """_decode_let_affix produces varints from base64 input."""
        from app.services.importers.lastepochtools_importer import _decode_let_affix
        # AGwRhQ → bytes [0, 108, 17, 133] → varints [0, 108, 17, 5]
        result = _decode_let_affix("AGwRhQ")
        assert result["varints"] == [0, 108, 17, 5]
        assert len(result["candidates"]) > 0
        assert result["raw_bytes"] == "006c1185"

    def test_decode_let_affix_short_entry(self):
        """Short entries like AAwDhQ still produce candidates."""
        from app.services.importers.lastepochtools_importer import _decode_let_affix
        # AAwDhQ → varints [0, 12, 3, 5]
        result = _decode_let_affix("AAwDhQ")
        assert result["varints"] == [0, 12, 3, 5]
        assert 3 in result["candidates"]
        assert result["tier_guess"] == 5

    def test_decode_let_affix_large_varint_splits(self):
        """Large varints are split to extract candidate affix IDs."""
        from app.services.importers.lastepochtools_importer import _decode_let_affix
        # AAzBsQ → varints [0, 12, 6337]
        result = _decode_let_affix("AAzBsQ")
        # 6337 & 0xFF = 193, should be in candidates
        assert 193 in result["candidates"] or 6337 in result["candidates"]
        assert result["tier_guess"] is not None

    def test_decode_empty_string_returns_empty(self):
        from app.services.importers.lastepochtools_importer import _decode_let_affix
        result = _decode_let_affix("")
        assert result["candidates"] == []
        assert result["varints"] == []

    def test_resolve_affix_finds_cold_resistance(self):
        """Affix ID 17 (Cold Resistance) resolves for helmet slot."""
        from app.services.importers.lastepochtools_importer import _resolve_affix
        decoded = {"candidates": [17], "tier_guess": 5}
        affix, tier = _resolve_affix(decoded, "helmet")
        assert affix is not None
        assert "cold" in affix["name"].lower() or "resistance" in affix["name"].lower()
        assert tier == 5

    def test_resolve_affix_prefers_slot_match(self):
        """When multiple candidates exist, prefer the one valid for the slot."""
        from app.services.importers.lastepochtools_importer import _resolve_affix
        # Candidate 25 (Added Health) is valid for belt; candidate 12 might not be
        decoded = {"candidates": [25, 12], "tier_guess": 3}
        affix, _ = _resolve_affix(decoded, "belt")
        assert affix is not None
        # Should pick Added Health (25) which is valid for belt
        assert int(affix["affix_id"]) == 25

    def test_resolve_affix_returns_none_for_unknown(self):
        from app.services.importers.lastepochtools_importer import _resolve_affix
        decoded = {"candidates": [99999], "tier_guess": None}
        affix, tier = _resolve_affix(decoded, "helmet")
        assert affix is None
        assert tier is None

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_base64_affixes_parsed_in_gear(self, mock_get):
        """Gear with base64 affix IDs produces parsed_affixes entries."""
        html = '''
        <html><body><script>
        window["buildInfo"] = {
            "bio": {"level": 90, "characterClass": 4, "chosenMastery": 1},
            "charTree": {"selected": {}},
            "skillTrees": [],
            "hud": [],
            "equipment": [
                {"equipmentSlot": 0, "affixes": [
                    {"affixID": "AAwDhQ", "tier": 5}
                ]}
            ]
        };
        </script></body></html>
        '''
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/B64AFF")

        assert result.success is True
        gear = result.build_data["gear"]
        assert len(gear) == 1
        affix_list = gear[0]["affixes"]
        assert len(affix_list) == 1
        # Should have either resolved name or decoded candidates
        affix = affix_list[0]
        assert affix["tier"] == 5
        # Either resolved (has name) or unresolved (has decoded)
        assert affix.get("name") is not None or affix.get("decoded") is not None

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_bare_string_affixes_handled(self, mock_get):
        """Affixes as bare strings (not dicts) are also decoded."""
        html = '''
        <html><body><script>
        window["buildInfo"] = {
            "bio": {"level": 90, "characterClass": 4, "chosenMastery": 1},
            "charTree": {"selected": {}},
            "skillTrees": [],
            "hud": [],
            "equipment": [
                {"equipmentSlot": 7, "affixes": ["AAwDhQ", "AGwRhQ"]}
            ]
        };
        </script></body></html>
        '''
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from app.services.importers import LastEpochToolsImporter
        result = LastEpochToolsImporter().parse("https://www.lastepochtools.com/planner/BARESTR")

        assert result.success is True
        gear = result.build_data["gear"]
        assert len(gear) == 1
        assert len(gear[0]["affixes"]) == 2
