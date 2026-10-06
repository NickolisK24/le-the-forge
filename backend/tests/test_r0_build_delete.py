"""
R0 regression: deleting a build that has view records (DB-1).

The ORM previously nulled build_views.build_id (NOT NULL) and the delete
returned 500. View rows are owned by their build and are deleted with it,
both by the ORM cascade and by ON DELETE CASCADE on the foreign key.
"""

from pathlib import Path

import pytest
from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory
from flask_jwt_extended import create_access_token

from app.models import Build, BuildView, User
from app.services import build_service

MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"


@pytest.fixture
def viewed_build(db, user):
    build = build_service.create_build(
        {"name": "R0 Viewed", "character_class": "Mage", "mastery": "Sorcerer"},
        user_id=user.id,
    )
    for i in range(3):
        db.session.add(BuildView(build_id=build.id, viewer_ip_hash=f"{i:064d}"))
    db.session.commit()
    return build


def _counts(db, build_id):
    db.session.expire_all()
    return (
        Build.query.filter_by(id=build_id).count(),
        BuildView.query.filter_by(build_id=build_id).count(),
    )


def test_owner_can_delete_viewed_build(client, db, viewed_build, auth_headers):
    build_id = viewed_build.id
    assert _counts(db, build_id) == (1, 3)
    resp = client.delete(f"/api/builds/{viewed_build.slug}", headers=auth_headers)
    assert resp.status_code == 204
    assert _counts(db, build_id) == (0, 0)


def test_other_user_cannot_delete_viewed_build(app, client, db, viewed_build):
    other = User(discord_id="r0-delete-other", username="Other")
    db.session.add(other)
    db.session.commit()
    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity=other.id)}"}
    resp = client.delete(f"/api/builds/{viewed_build.slug}", headers=headers)
    assert resp.status_code == 403
    assert _counts(db, viewed_build.id) == (1, 3)


def test_anonymous_cannot_delete_viewed_build(client, db, viewed_build):
    resp = client.delete(f"/api/builds/{viewed_build.slug}")
    assert resp.status_code == 401
    assert _counts(db, viewed_build.id) == (1, 3)


def test_build_views_fk_declares_on_delete_cascade():
    fk = next(iter(BuildView.__table__.c.build_id.foreign_keys))
    assert fk.ondelete == "CASCADE"


def test_migration_chain_has_single_head_with_cascade_migration():
    cfg = AlembicConfig()
    cfg.set_main_option("script_location", str(MIGRATIONS))
    script = ScriptDirectory.from_config(cfg)
    assert "a7c3e91f4d20" in {r.revision for r in script.walk_revisions()}
    assert len(script.get_heads()) == 1
    rev = script.get_revision("a7c3e91f4d20")
    assert rev.down_revision == "dd1840cac963"
