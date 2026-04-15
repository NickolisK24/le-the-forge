"""
Tests for the build import pipeline.

Covers:
  base_importer       — ImportResult / BaseImporter.validate()
  lastepochtools      — URL extraction, successful parse with mocked HTTP,
                        HTTP-failure error handling
  maxroll             — URL extraction, successful parse with mocked HTTP,
                        HTTP-failure error handling

All HTTP calls are mocked via unittest.mock.patch — no real network access.
"""

from __future__ import annotations

import re
from unittest.mock import MagicMock, patch

import pytest

from app.services.importers import ImportResult, LastEpochToolsImporter, MaxrollImporter
from app.services.importers.base_importer import BaseImporter
from app.services.importers.lastepochtools_importer import URL_PATTERN as LET_URL_PATTERN
from app.services.importers.maxroll_importer import URL_PATTERN as MAXROLL_URL_PATTERN


# ---------------------------------------------------------------------------
# Minimal LET HTML fixture with the three fields validate() checks
# ---------------------------------------------------------------------------

_LET_HTML = '''
<html><body><script>
window["buildInfo"] = {
    "bio": {"level": 80, "characterClass": 4, "chosenMastery": 1},
    "charTree": {"selected": {"1": 1, "2": 2}},
    "skillTrees": [
        {"treeID": "rb31pl", "selected": {"1": 3}, "level": 18, "slotNumber": 0}
    ],
    "hud": ["rb31pl", "", "", "", ""]
};
</script></body></html>
'''


def _mock_let_response(status_code: int = 200, text: str = _LET_HTML) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    resp.raise_for_status = MagicMock()
    return resp


def _mock_maxroll_api_response(payload: dict, status_code: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload
    resp.text = ""
    resp.raise_for_status = MagicMock()
    return resp


# ---------------------------------------------------------------------------
# base_importer.py
# ---------------------------------------------------------------------------

class _DummyImporter(BaseImporter):
    """Concrete BaseImporter for exercising the shared validate() logic."""
    source_name = "dummy"

    def parse(self, url: str) -> ImportResult:   # pragma: no cover — unused
        return ImportResult(success=True, source=self.source_name)


class TestBaseImporterValidate:
    """Covers the shared validation logic on BaseImporter (the module's
    equivalent of validate_build_data / normalize_skill_list)."""

    def test_validate_accepts_valid_build_dict(self):
        importer = _DummyImporter()
        result = ImportResult(
            success=True,
            source="dummy",
            build_data={
                "character_class": "Rogue",  # known class
                "mastery": "Bladedancer",    # known mastery for Rogue
                "skills": [{"skill_name": "Shift", "slot": 0}],
            },
        )
        validated = importer.validate(result)
        # A valid build leaves missing_fields empty.
        assert validated.missing_fields == []

    def test_validate_rejects_unknown_class(self):
        importer = _DummyImporter()
        result = ImportResult(
            success=True,
            source="dummy",
            build_data={"character_class": "NotARealClass", "skills": []},
        )
        validated = importer.validate(result)
        assert any(f.startswith("class:") for f in validated.missing_fields)

    def test_validate_rejects_unknown_mastery_for_class(self):
        importer = _DummyImporter()
        result = ImportResult(
            success=True,
            source="dummy",
            build_data={
                "character_class": "Rogue",
                "mastery": "NotAMastery",
                "skills": [],
            },
        )
        validated = importer.validate(result)
        assert any(f.startswith("mastery:") for f in validated.missing_fields)

    def test_validate_flags_skills_with_empty_names(self):
        importer = _DummyImporter()
        result = ImportResult(
            success=True,
            source="dummy",
            build_data={
                "character_class": "Rogue",
                "mastery": "Bladedancer",
                "skills": [{"skill_name": "", "slot": 0}],
            },
        )
        validated = importer.validate(result)
        assert "skill:empty_name" in validated.missing_fields

    def test_validate_noop_when_result_already_failed(self):
        importer = _DummyImporter()
        result = ImportResult(success=False, source="dummy", error_message="fetch failed")
        validated = importer.validate(result)
        # Failed results pass through untouched.
        assert validated is result
        assert validated.missing_fields == []


# ---------------------------------------------------------------------------
# lastepochtools_importer.py
# ---------------------------------------------------------------------------

class TestLastEpochToolsUrlExtraction:
    """LET uses URL_PATTERN.search(url) inside parse() to extract the code."""

    def test_extracts_code_from_valid_url(self):
        url = "https://www.lastepochtools.com/planner/B4XdLG56"
        match = LET_URL_PATTERN.search(url)
        assert match is not None
        assert match.group(1) == "B4XdLG56"

    def test_returns_no_match_for_invalid_url(self):
        match = LET_URL_PATTERN.search("https://example.com/some-build")
        assert match is None


class TestLastEpochToolsImport:
    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_import_with_mocked_response_populates_result(self, mock_get):
        mock_get.return_value = _mock_let_response()
        importer = LastEpochToolsImporter()
        result = importer.parse("https://www.lastepochtools.com/planner/B4XdLG56")

        assert result.success is True
        assert result.source == "lastepochtools"
        assert result.build_data is not None
        # Class 4 + mastery 1 → Rogue / Bladedancer
        assert result.build_data["character_class"] == "Rogue"
        assert result.build_data["mastery"] == "Bladedancer"
        # Single skill in skillTrees
        assert len(result.build_data["skills"]) == 1

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_import_on_http_failure_returns_failure_with_message(self, mock_get):
        from requests import HTTPError

        bad = MagicMock()
        bad.status_code = 500
        bad.raise_for_status = MagicMock(side_effect=HTTPError(response=bad))
        mock_get.return_value = bad

        result = LastEpochToolsImporter().parse(
            "https://www.lastepochtools.com/planner/ANYCODE"
        )
        assert result.success is False
        assert result.error_message is not None
        assert result.build_data is None

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_import_404_returns_specific_not_found_message(self, mock_get):
        from requests import HTTPError

        bad = MagicMock()
        bad.status_code = 404
        bad.raise_for_status = MagicMock(side_effect=HTTPError(response=bad))
        mock_get.return_value = bad

        result = LastEpochToolsImporter().parse(
            "https://www.lastepochtools.com/planner/DOESNOTEXIST"
        )
        assert result.success is False
        assert "not found" in result.error_message.lower()

    def test_import_with_invalid_url_does_not_fetch(self):
        # Invalid URLs should be rejected up front — no HTTP call required.
        result = LastEpochToolsImporter().parse("https://example.com/bogus")
        assert result.success is False
        assert "Invalid URL" in (result.error_message or "")

    @patch("app.services.importers.lastepochtools_importer._requests.get")
    def test_import_failure_carries_diagnostic_partial_data(self, mock_get):
        # HTML with no buildInfo block → parser records partial_data so the
        # route layer can persist an ImportFailure record.
        mock_get.return_value = _mock_let_response(text="<html></html>")
        result = LastEpochToolsImporter().parse(
            "https://www.lastepochtools.com/planner/B4XdLG56"
        )
        assert result.success is False
        assert result.partial_data is not None
        assert result.partial_data.get("code") == "B4XdLG56"


# ---------------------------------------------------------------------------
# maxroll_importer.py
# ---------------------------------------------------------------------------

class TestMaxrollUrlExtraction:
    def test_extracts_code_from_valid_url(self):
        url = "https://maxroll.gg/last-epoch/planner/zge0t60e#2"
        match = MAXROLL_URL_PATTERN.search(url)
        assert match is not None
        assert match.group(1) == "zge0t60e"

    def test_returns_no_match_for_invalid_url(self):
        match = MAXROLL_URL_PATTERN.search("https://example.com/planner/foo")
        assert match is None


class TestMaxrollImport:
    @patch("app.services.importers.maxroll_importer._requests.get")
    def test_import_with_mocked_response_populates_result(self, mock_get):
        payload = {
            "data": {
                "class": "Mage",
                "mastery": "Sorcerer",
                "level": 92,
                "passives": {"100": 2, "200": 4},
                "skills": [
                    {"name": "Fireball", "slot": 0, "level": 20, "nodes": {"1": 3}},
                ],
                "equipment": [],
            }
        }
        mock_get.return_value = _mock_maxroll_api_response(payload)

        result = MaxrollImporter().parse(
            "https://maxroll.gg/last-epoch/planner/zge0t60e"
        )
        assert result.success is True
        assert result.source == "maxroll"
        assert result.build_data is not None
        assert result.build_data["character_class"] == "Mage"
        assert result.build_data["mastery"] == "Sorcerer"
        assert result.build_data["level"] == 92

    @patch("app.services.importers.maxroll_importer._requests.get")
    def test_import_on_http_failure_returns_failure_with_message(self, mock_get):
        # All API attempts return 500 AND the HTML fallback also fails →
        # the importer should surface a user-visible error message.
        bad = MagicMock()
        bad.status_code = 500
        bad.text = ""
        bad.json.side_effect = ValueError("not json")
        mock_get.return_value = bad

        result = MaxrollImporter().parse(
            "https://maxroll.gg/last-epoch/planner/zge0t60e"
        )
        assert result.success is False
        assert result.error_message is not None

    def test_import_with_invalid_url_does_not_fetch(self):
        result = MaxrollImporter().parse("https://example.com/not-maxroll")
        assert result.success is False
        assert "Invalid URL" in (result.error_message or "")
