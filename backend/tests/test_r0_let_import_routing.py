"""
R0 regression: the retired server-side Last Epoch Tools fetch (IMP-1, IMP-2).

LET blocks server-side requests (production received HTTP 403 for
https://www.lastepochtools.com/planner/B5P5P8M3). LET URLs must never trigger a
server fetch; the response points the user at the JSON/bookmarklet flow.
"""

from unittest.mock import patch

import pytest

from app.models import ImportFailure

INCIDENT_URL = "https://www.lastepochtools.com/planner/B5P5P8M3"


def _no_network(*args, **kwargs):  # pragma: no cover - must never be called
    raise AssertionError("server-side fetch attempted for a LET URL")


@pytest.fixture
def guarded():
    """Fail the test if any HTTP fetch, importer lookup or alert happens."""
    with patch("requests.get", side_effect=_no_network) as req_get, \
         patch("requests.Session.get", side_effect=_no_network), \
         patch("app.routes.import_route.get_importer", side_effect=_no_network) as factory, \
         patch("app.routes.import_route.send_import_failure_alert") as alert:
        yield {"get": req_get, "factory": factory, "alert": alert}


def _assert_unsupported(resp, url):
    assert resp.status_code == 422
    body = resp.get_json()
    assert body["errors"][0]["code"] == "LET_SERVER_FETCH_UNSUPPORTED"
    message = body["errors"][0]["message"].lower()
    assert "invalid" not in message and "expired" not in message
    assert body["meta"]["supported_flow"] == "let_json"
    assert body["meta"]["supported_endpoint"] == "/api/import/let/json"
    assert body["meta"]["original_url"] == url
    assert body["meta"]["source"] == "lastepochtools"


@pytest.mark.parametrize("url", [
    INCIDENT_URL,
    "https://lastepochtools.com/planner/abcd1234",
    "  https://www.lastepochtools.com/planner/B5P5P8M3  ",
])
def test_import_build_with_let_url_never_fetches(client, db, guarded, url):
    resp = client.post("/api/import/build", json={"url": url})
    _assert_unsupported(resp, url.strip())
    guarded["get"].assert_not_called()
    guarded["factory"].assert_not_called()
    guarded["alert"].assert_not_called()
    assert ImportFailure.query.count() == 0


def test_legacy_import_url_endpoint_never_fetches(client, db, guarded):
    resp = client.post("/api/import/url", json={"url": INCIDENT_URL})
    _assert_unsupported(resp, INCIDENT_URL)
    guarded["get"].assert_not_called()
    guarded["alert"].assert_not_called()


def test_legacy_import_url_still_validates_input(client, db, guarded):
    assert client.post("/api/import/url", json={}).status_code == 400
    assert client.post("/api/import/url", json={"url": "https://example.com/x"}).status_code == 400


def test_unknown_source_still_rejected(client, db, guarded):
    resp = client.post("/api/import/build", json={"url": "https://unknown.com/build/123"})
    assert resp.status_code == 400
    assert "Unsupported URL" in resp.get_json()["errors"][0]["message"]


def test_maxroll_url_still_uses_server_importer(client, db):
    from app.services.importers.base_importer import ImportResult

    with patch("app.routes.import_route.get_importer") as factory:
        factory.return_value.parse.return_value = ImportResult(
            success=True, source="maxroll",
            build_data={"name": "Mx", "character_class": "Mage", "mastery": "Sorcerer",
                        "level": 70, "passive_tree": [], "skills": [], "gear": []},
        )
        resp = client.post("/api/import/build", json={"url": "https://maxroll.gg/last-epoch/planner/abc"})
    assert resp.status_code == 201
    factory.assert_called_once()


def test_let_json_import_still_works(client, db, guarded):
    build_info = {
        "bio": {"level": 85, "characterClass": 2, "chosenMastery": 3},
        "charTree": {"selected": {"10": 5}},
        "skillTrees": [],
        "hud": [],
    }
    resp = client.post("/api/import/let/json", json={"build_info": build_info})
    assert resp.status_code == 200
    assert resp.get_json()["data"]["build"]["character_class"] == "Sentinel"
    guarded["get"].assert_not_called()
