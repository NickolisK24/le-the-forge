"""
R0 regression: production game data must be read-only to ordinary users.

Covers PATCH /api/admin/affixes/<id> (wrote data/items/affixes.json) and
POST /api/load/game-data (hot-reloaded the live pipeline), both previously
reachable without authentication.
"""

import hashlib
import json
import shutil

import pytest
from flask_jwt_extended import create_access_token

from app.models import User
from app.routes import admin as admin_routes
from config import ProductionConfig

PATCH_BODY = {"name": "R0-TAMPER"}


def _sha(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def affix_copy(tmp_path, monkeypatch):
    """Point the admin routes at a scratch copy so a regression can never
    modify the real data file; the real file's hash is checked as well."""
    real = admin_routes.AFFIXES_PATH
    copy = tmp_path / "affixes.json"
    shutil.copyfile(real, copy)
    monkeypatch.setattr(admin_routes, "AFFIXES_PATH", copy)
    return {"real": real, "copy": copy, "real_sha": _sha(real), "copy_sha": _sha(copy)}


@pytest.fixture
def affix_id(affix_copy):
    data = json.loads(affix_copy["copy"].read_text(encoding="utf-8"))
    return data[0]["id"]


@pytest.fixture
def admin_headers(app, db):
    admin = User(discord_id="r0-admin", username="R0Admin", is_admin=True)
    db.session.add(admin)
    db.session.commit()
    with app.app_context():
        token = create_access_token(identity=admin.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mutation_enabled(app, monkeypatch):
    monkeypatch.setitem(app.config, "GAME_DATA_MUTATION_ENABLED", True)


def _pipeline_snapshot(app):
    pipeline = app.extensions["game_data"]
    return pipeline, pipeline._cache.get("affixes"), pipeline._version


def _assert_untouched(app, affix_copy, snapshot):
    pipeline, affixes_obj, version = snapshot
    assert _sha(affix_copy["real"]) == affix_copy["real_sha"]
    assert _sha(affix_copy["copy"]) == affix_copy["copy_sha"]
    assert app.extensions["game_data"] is pipeline
    assert pipeline._cache.get("affixes") is affixes_obj
    assert pipeline._version == version


def test_production_config_cannot_enable_mutation():
    assert ProductionConfig.GAME_DATA_MUTATION_ENABLED is False


def test_testing_config_defaults_to_disabled(app):
    assert app.config["GAME_DATA_MUTATION_ENABLED"] is False


# --- disabled (default / production behaviour) -----------------------------

@pytest.mark.parametrize("who", ["anonymous", "user", "admin"])
def test_affix_patch_disabled_for_everyone(app, client, db, affix_copy, affix_id,
                                           auth_headers, admin_headers, who):
    headers = {"anonymous": {}, "user": auth_headers, "admin": admin_headers}[who]
    snap = _pipeline_snapshot(app)
    resp = client.patch(f"/api/admin/affixes/{affix_id}", json=PATCH_BODY, headers=headers)
    assert resp.status_code == 404
    _assert_untouched(app, affix_copy, snap)


@pytest.mark.parametrize("who", ["anonymous", "user", "admin"])
def test_reload_disabled_for_everyone(app, client, db, affix_copy,
                                      auth_headers, admin_headers, who):
    headers = {"anonymous": {}, "user": auth_headers, "admin": admin_headers}[who]
    snap = _pipeline_snapshot(app)
    resp = client.post("/api/load/game-data", headers=headers)
    assert resp.status_code == 404
    _assert_untouched(app, affix_copy, snap)


# --- enabled (local operator tooling) --------------------------------------

def test_affix_patch_enabled_rejects_anonymous(app, client, db, mutation_enabled,
                                               affix_copy, affix_id):
    snap = _pipeline_snapshot(app)
    resp = client.patch(f"/api/admin/affixes/{affix_id}", json=PATCH_BODY)
    assert resp.status_code == 401
    _assert_untouched(app, affix_copy, snap)


def test_affix_patch_enabled_rejects_normal_user(app, client, db, mutation_enabled,
                                                 affix_copy, affix_id, auth_headers):
    snap = _pipeline_snapshot(app)
    resp = client.patch(f"/api/admin/affixes/{affix_id}", json=PATCH_BODY, headers=auth_headers)
    assert resp.status_code == 403
    _assert_untouched(app, affix_copy, snap)


def test_affix_patch_enabled_allows_admin(app, client, db, mutation_enabled,
                                          affix_copy, affix_id, admin_headers):
    resp = client.patch(f"/api/admin/affixes/{affix_id}", json=PATCH_BODY, headers=admin_headers)
    assert resp.status_code == 200
    written = json.loads(affix_copy["copy"].read_text(encoding="utf-8"))
    assert next(a for a in written if a["id"] == affix_id)["name"] == "R0-TAMPER"
    # The real repository file is never the target of the test write.
    assert _sha(affix_copy["real"]) == affix_copy["real_sha"]


def test_reload_enabled_rejects_anonymous(app, client, db, mutation_enabled, affix_copy):
    snap = _pipeline_snapshot(app)
    assert client.post("/api/load/game-data").status_code == 401
    _assert_untouched(app, affix_copy, snap)


def test_reload_enabled_rejects_normal_user(app, client, db, mutation_enabled,
                                            affix_copy, auth_headers):
    snap = _pipeline_snapshot(app)
    assert client.post("/api/load/game-data", headers=auth_headers).status_code == 403
    _assert_untouched(app, affix_copy, snap)


def test_affix_listing_remains_readable(client, db, affix_copy):
    resp = client.get("/api/admin/affixes")
    assert resp.status_code == 200
