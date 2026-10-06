"""
R0 regression: import-failure telemetry must be truthful (IMP-3, OBS-1).

The 2026-10-06 alert for https://www.lastepochtools.com/planner/B5P5P8M3 read
"Missing Fields: None" / "Parsed Data: No data parsed" for an HTTP 403 transport
failure. Completeness was never evaluated, partial_data was dropped (build_data
was forwarded instead), and no upstream metadata was kept.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from app.models import ImportFailure
from app.services import discord_notifier
from app.services.import_diagnostics import (
    MISSING_FIELDS_PRESENT,
    NONE_MISSING,
    NOT_EVALUATED,
    classify_http_status,
    safe_upstream_headers,
)
from app.services.importers import LastEpochToolsImporter, MaxrollImporter
from app.services.importers.base_importer import ImportResult

INCIDENT_URL = "https://www.lastepochtools.com/planner/B5P5P8M3"

CLOUDFLARE_403_HEADERS = {
    "Server": "cloudflare",
    "CF-Ray": "8c1d2e3f4a5b6c7d-SJC",
    "CF-Mitigated": "challenge",
    "Content-Type": "text/html; charset=UTF-8",
    "Set-Cookie": "__cf_bm=secret-cookie-value; path=/",
    "Authorization": "Bearer should-never-be-kept",
}


def _http_403_response():
    resp = requests.Response()
    resp.status_code = 403
    resp.headers.update(CLOUDFLARE_403_HEADERS)
    resp._content = b"<html>Just a moment...</html>"
    resp.url = INCIDENT_URL
    return resp


def _raise_403(*args, **kwargs):
    resp = _http_403_response()
    resp.raise_for_status()


class _SyncThread:
    """Run the Discord post inline so the embed can be inspected."""

    def __init__(self, target, args=(), daemon=None, **kwargs):
        self._target, self._args = target, args

    def start(self):
        self._target(*self._args)


@pytest.fixture
def discord_capture(monkeypatch):
    monkeypatch.setattr(discord_notifier, "WEBHOOK_URL", "https://discord.example.invalid/webhook")
    monkeypatch.setattr(discord_notifier.threading, "Thread", _SyncThread)
    post = MagicMock(return_value=MagicMock(status_code=204))
    monkeypatch.setattr(discord_notifier.requests, "post", post)

    def embed():
        assert post.call_count == 1, post.call_count
        return post.call_args.kwargs["json"]["embeds"][0]

    return embed


def _field(embed, name):
    return next(f["value"] for f in embed["fields"] if f["name"] == name)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def test_safe_upstream_headers_allowlist_only():
    kept = safe_upstream_headers(CLOUDFLARE_403_HEADERS)
    assert kept == {
        "server": "cloudflare",
        "cf-ray": "8c1d2e3f4a5b6c7d-SJC",
        "cf-mitigated": "challenge",
        "content-type": "text/html; charset=UTF-8",
    }


@pytest.mark.parametrize("status,category", [
    (403, "upstream_blocked"), (401, "upstream_blocked"), (429, "upstream_rate_limited"),
    (404, "upstream_not_found"), (503, "upstream_server_error"), (None, "unknown"),
])
def test_classify_http_status(status, category):
    assert classify_http_status(status) == category


# ---------------------------------------------------------------------------
# The 2026-10-06 incident, reproduced at the importer and route layers
# ---------------------------------------------------------------------------

def test_let_importer_classifies_403_with_safe_upstream_metadata():
    with patch("app.services.importers.lastepochtools_importer._requests.get",
               return_value=_http_403_response()):
        result = LastEpochToolsImporter().parse(INCIDENT_URL)
    assert result.success is False
    diag = result.diagnostics
    assert diag["failure_stage"] == "fetch"
    assert diag["http_status"] == 403
    assert diag["error_category"] == "upstream_blocked"
    assert diag["parsing_started"] is False
    assert diag["upstream_headers"]["cf-mitigated"] == "challenge"
    assert "set-cookie" not in diag["upstream_headers"]
    assert "authorization" not in diag["upstream_headers"]


def test_incident_replay_records_truthful_failure_and_alert(app, db, discord_capture):
    """Drive the original server-side failure path directly (the route no longer
    reaches it for LET URLs) and check the stored record and the Discord embed."""
    from app.routes import import_route

    with app.test_request_context("/api/import/build", method="POST"), \
         patch("app.routes.import_route.get_importer", return_value=LastEpochToolsImporter()), \
         patch("app.services.importers.lastepochtools_importer._requests.get",
               return_value=_http_403_response()):
        body, status = import_route._do_import(INCIDENT_URL, "lastepochtools", None)

    assert status == 422
    failure = ImportFailure.query.one()
    diag = failure.diagnostics
    assert diag["failure_stage"] == "fetch"
    assert diag["http_status"] == 403
    assert diag["error_category"] == "upstream_blocked"
    assert diag["missing_field_state"] == NOT_EVALUATED
    assert diag["parsing_started"] is False
    assert diag["url"] == INCIDENT_URL
    assert diag["user"] == "anonymous"
    assert diag["replay"] == "url_retry"
    for key in ("app_version", "app_commit", "data_version", "extractor_version"):
        assert diag[key]
    assert "set-cookie" not in diag["upstream_headers"]

    embed = discord_capture()
    missing = _field(embed, "Missing Fields")
    assert missing != "None"
    assert missing.startswith("Not evaluated")
    assert _field(embed, "Parsed Data") == "Not attempted (failed at fetch)"
    assert _field(embed, "HTTP Status") == "403"
    assert _field(embed, "Category") == "upstream_blocked"
    assert _field(embed, "Stage") == "fetch"
    upstream = _field(embed, "Upstream")
    assert "cf-ray: 8c1d2e3f4a5b6c7d-SJC" in upstream
    assert "cf-mitigated: challenge" in upstream
    embed_text = " ".join(f["value"] for f in embed["fields"])
    assert "secret-cookie-value" not in embed_text
    assert "should-never-be-kept" not in embed_text
    assert _field(embed, "Failure ID") == failure.id


def test_maxroll_403_through_route_is_classified_not_called_expired(client, db, discord_capture):
    with patch("app.services.importers.maxroll_importer._requests.get",
               return_value=_http_403_response()):
        resp = client.post("/api/import/build", json={"url": "https://maxroll.gg/last-epoch/planner/abc123"})
    assert resp.status_code == 422
    message = resp.get_json()["errors"][0]["message"].lower()
    assert "expired" not in message
    assert "refused" in message
    diag = ImportFailure.query.one().diagnostics
    assert diag["http_status"] == 403
    assert diag["error_category"] == "upstream_blocked"
    assert diag["missing_field_state"] == NOT_EVALUATED
    assert diag["upstream_headers"]["server"] == "cloudflare"
    assert _field(discord_capture(), "Missing Fields").startswith("Not evaluated")


# ---------------------------------------------------------------------------
# partial_data forwarding and missing-field states
# ---------------------------------------------------------------------------

def test_hard_failure_forwards_importer_partial_data(client, db, discord_capture):
    partial = {"character_class": "Mage", "raw_keys": ["profiles", "activeProfile"]}
    importer = MagicMock()
    importer.parse.return_value = ImportResult(
        success=False, source="maxroll",
        error_message="Could not determine mastery",
        missing_fields=["mastery"],
        partial_data=partial,
    )
    with patch("app.routes.import_route.get_importer", return_value=importer):
        client.post("/api/import/build", json={"url": "https://maxroll.gg/last-epoch/planner/pd1"})
    failure = ImportFailure.query.one()
    assert failure.partial_data == partial
    assert failure.diagnostics["missing_field_state"] == MISSING_FIELDS_PRESENT
    assert failure.diagnostics["partial_data_summary"]["character_class"] == "Mage"
    embed = discord_capture()
    assert "mastery" in _field(embed, "Missing Fields")
    assert "Mage" in _field(embed, "Parsed Data")


def test_hard_failure_without_diagnostics_is_not_reported_complete(client, db, discord_capture):
    importer = MagicMock()
    importer.parse.return_value = ImportResult(success=False, source="maxroll",
                                               error_message="boom", missing_fields=[])
    with patch("app.routes.import_route.get_importer", return_value=importer):
        client.post("/api/import/build", json={"url": "https://maxroll.gg/last-epoch/planner/nd1"})
    assert ImportFailure.query.one().diagnostics["missing_field_state"] == NOT_EVALUATED
    assert _field(discord_capture(), "Missing Fields") != "None"


def test_persist_failure_after_complete_parse_is_none_missing(client, db, discord_capture):
    importer = MagicMock()
    importer.parse.return_value = ImportResult(
        success=True, source="maxroll",
        build_data={"name": "x", "character_class": "Mage", "mastery": "Sorcerer",
                    "level": 1, "passive_tree": [], "skills": [], "gear": []},
        missing_fields=[],
    )
    with patch("app.routes.import_route.get_importer", return_value=importer), \
         patch("app.routes.import_route.build_service.create_build", side_effect=RuntimeError("db down")):
        resp = client.post("/api/import/build", json={"url": "https://maxroll.gg/last-epoch/planner/pf1"})
    assert resp.status_code == 422
    diag = ImportFailure.query.one().diagnostics
    assert diag["failure_stage"] == "persist"
    assert diag["missing_field_state"] == NONE_MISSING
    assert _field(discord_capture(), "Missing Fields") == "None missing"


def test_alert_still_sent_when_failure_record_cannot_be_stored(app, db, monkeypatch):
    from app.routes import import_route

    sent = []
    monkeypatch.setattr(import_route, "send_import_failure_alert",
                        lambda failure, severity="hard": sent.append(failure))
    with app.test_request_context("/"), \
         patch.object(import_route.db.session, "commit", side_effect=RuntimeError("db unavailable")):
        import_route._record_and_alert(
            source="maxroll", url="https://maxroll.gg/last-epoch/planner/x", user_id=None,
            error_message="fetch failed", failure_stage="fetch",
        )
    assert len(sent) == 1
    assert sent[0].diagnostics["missing_field_state"] == NOT_EVALUATED


def test_diagnostics_migration_is_single_head():
    from pathlib import Path
    from alembic.config import Config as AlembicConfig
    from alembic.script import ScriptDirectory

    cfg = AlembicConfig()
    cfg.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "migrations"))
    script = ScriptDirectory.from_config(cfg)
    assert script.get_heads() == ["c5d8e2b7a913"]
    assert script.get_revision("c5d8e2b7a913").down_revision == "a7c3e91f4d20"
    assert "diagnostics" in ImportFailure.__table__.c
