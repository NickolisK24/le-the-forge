"""Alembic migration chain on real PostgreSQL (AUDIT-R2 P15, DB-5).

Covers: single head and a complete revision graph; clean database -> head;
model/schema drift against a measured baseline; foreign-key delete rules
and behaviour; downgrade/upgrade round trip for every revision, with known
debt declared in ``migration_registry``.
"""
from __future__ import annotations

import pytest
import sqlalchemy as sa
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from flask_migrate import downgrade, upgrade

from .conftest import MIGRATIONS
from .migration_registry import KNOWN_BROKEN_DOWNGRADES, KNOWN_LOSSY_DOWNGRADES, KNOWN_SCHEMA_DRIFT

pytestmark = pytest.mark.postgres


def _script() -> ScriptDirectory:
    cfg = Config()
    cfg.set_main_option("script_location", MIGRATIONS)
    return ScriptDirectory.from_config(cfg)


REVISIONS = [r for r in reversed(list(_script().walk_revisions())) if r.down_revision is not None]


def test_single_head_and_complete_graph():
    sd = _script()
    assert len(sd.get_heads()) == 1
    known = {r.revision for r in sd.walk_revisions()}
    for r in sd.walk_revisions():
        downs = r.down_revision if isinstance(r.down_revision, tuple) else (r.down_revision,)
        assert all(d is None or d in known for d in downs), r.revision


def test_clean_database_upgrades_to_head(pg_app):
    from app import db
    app = pg_app()
    with app.app_context():
        upgrade(directory=MIGRATIONS)
        with db.engine.connect() as conn:
            ver = conn.execute(sa.text("select version_num from alembic_version")).scalars().all()
            tables = set(sa.inspect(conn).get_table_names())
    assert ver == _script().get_heads()
    assert {t.name for t in db.metadata.sorted_tables} <= tables


def _drift(conn, metadata) -> set[tuple[str, str, str]]:
    """Normalised autogenerate diff: (table, column-or-object, kind)."""
    mc = MigrationContext.configure(conn, opts={"compare_server_default": True, "compare_type": True})
    out = set()
    for d in compare_metadata(mc, metadata):
        for it in (d if isinstance(d, list) else [d]):
            kind = it[0]
            if kind.startswith("modify_"):
                out.add((it[2], it[3], kind))
            else:  # add_/remove_ table, column, index, constraint
                obj = it[-1] if kind.endswith("_column") else it[1]
                table = getattr(getattr(obj, "table", None), "name", None) or getattr(obj, "name", str(obj))
                out.add((str(table), str(getattr(obj, "name", "")), kind))
    return out


def test_model_schema_drift_matches_baseline(pg_app):
    """No new drift between models and migrations; resolved drift must leave the registry."""
    from app import db
    app = pg_app()
    with app.app_context():
        upgrade(directory=MIGRATIONS)
        with db.engine.connect() as conn:
            drift = _drift(conn, db.metadata)
    assert drift - KNOWN_SCHEMA_DRIFT == set(), "new model/migration drift"
    assert KNOWN_SCHEMA_DRIFT - drift == set(), "drift was fixed: remove it from KNOWN_SCHEMA_DRIFT"


def test_foreign_key_delete_rules_match_models(pg_app):
    from app import db
    rule = {"a": None, "r": "RESTRICT", "c": "CASCADE", "n": "SET NULL", "d": "SET DEFAULT"}
    app = pg_app()
    with app.app_context():
        upgrade(directory=MIGRATIONS)
        with db.engine.connect() as conn:
            rows = conn.execute(sa.text(
                "select conrelid::regclass::text, a.attname, confrelid::regclass::text, confdeltype "
                "from pg_constraint c join pg_attribute a on a.attrelid = c.conrelid and a.attnum = c.conkey[1] "
                "where contype = 'f'")).all()
    in_db = {(t, col, ref): rule[d] for t, col, ref, d in rows}
    in_models = {(t.name, fk.parent.name, fk.column.table.name): (fk.ondelete.upper() if fk.ondelete else None)
                 for t in db.metadata.sorted_tables for fk in t.foreign_keys}
    assert in_db == in_models


def test_foreign_key_behaviour_on_build_delete(pg_app):
    """build_views cascade with the build; votes and build_skills block a raw delete (NO ACTION)."""
    from app import db
    app = pg_app()
    with app.app_context():
        upgrade(directory=MIGRATIONS)
        with db.engine.begin() as conn:
            _seed_build(conn)
            _insert(conn, "build_views", {"id": "v1", "build_id": "b1"})
            conn.execute(sa.text("delete from builds where id = 'b1'"))
            assert conn.execute(sa.text("select count(*) from build_views")).scalar() == 0
        with db.engine.begin() as conn:
            _seed_build(conn)
            _insert(conn, "votes", {"id": "x1", "user_id": "u1", "build_id": "b1"})
        with pytest.raises(sa.exc.IntegrityError):
            with db.engine.begin() as conn:
                conn.execute(sa.text("delete from builds where id = 'b1'"))


def _insert(conn, table: str, vals: dict) -> None:
    """Insert a row, filling NOT NULL columns without defaults with type-appropriate placeholders."""
    cols = {c["name"]: c for c in sa.inspect(conn).get_columns(table)}
    vals = dict(vals)
    _fill_required(cols, vals)
    conn.execute(sa.text(f"insert into {table} ({', '.join(vals)}) values ({', '.join(':' + k for k in vals)})"),
                 vals)


def _seed_build(conn):
    """Insert a minimal user + build using only columns that exist."""
    if conn.execute(sa.text("select count(*) from users where id = 'u1'")).scalar() == 0:
        _insert(conn, "users", {"id": "u1", "username": "u"})
    _insert(conn, "builds", {"id": "b1", "slug": "b1", "name": "n", "character_class": "Mage",
                             "mastery": "Sorcerer", "author_id": "u1"})


def _fill_required(cols, vals):
    for name, c in cols.items():
        if name in vals or c["nullable"] or c.get("default") is not None or c.get("autoincrement") is True:
            continue
        t = str(c["type"]).upper()
        if "BOOL" in t:
            vals[name] = False
        elif "INT" in t or "NUMERIC" in t or "FLOAT" in t or "DOUBLE" in t:
            vals[name] = 0
        elif "TIMESTAMP" in t or "DATE" in t:
            vals[name] = "2026-01-01T00:00:00"
        elif "JSON" in t:
            vals[name] = "[]"
        else:
            vals[name] = "x"


@pytest.mark.parametrize("rev", [r.revision for r in REVISIONS])
def test_downgrade_upgrade_round_trip(pg_app, rev):
    """Upgrade to ``rev``, downgrade one step, upgrade again, on a fresh database."""
    if rev in KNOWN_BROKEN_DOWNGRADES:
        pytest.xfail(KNOWN_BROKEN_DOWNGRADES[rev])
    script = _script().get_revision(rev)
    downs = script.down_revision if isinstance(script.down_revision, tuple) else (script.down_revision,)
    app = pg_app()
    with app.app_context():
        upgrade(directory=MIGRATIONS, revision=rev)
        downgrade(directory=MIGRATIONS, revision=downs[0] if len(downs) > 1 else f"{rev}-1")
        upgrade(directory=MIGRATIONS, revision=rev)


@pytest.mark.parametrize("rev", sorted(KNOWN_BROKEN_DOWNGRADES))
def test_known_broken_downgrades_still_fail(pg_app, rev):
    """Ratchet: when a broken downgrade is fixed, this fails until the registry entry is removed."""
    app = pg_app()
    with app.app_context():
        upgrade(directory=MIGRATIONS, revision=rev)
        with pytest.raises(sa.exc.CompileError):
            downgrade(directory=MIGRATIONS, revision=f"{rev}-1")


def test_lossy_downgrade_is_declared(pg_app):
    """a1b2c3d4e5f6 rebuilds passive_nodes: rows do not survive downgrade + upgrade."""
    from app import db
    rev = "a1b2c3d4e5f6"
    assert rev in KNOWN_LOSSY_DOWNGRADES
    app = pg_app()
    with app.app_context():
        upgrade(directory=MIGRATIONS, revision=rev)
        with db.engine.begin() as conn:
            _insert(conn, "passive_nodes", {"id": "ac_0"})
        downgrade(directory=MIGRATIONS, revision=f"{rev}-1")
        upgrade(directory=MIGRATIONS, revision=rev)
        with db.engine.connect() as conn:
            assert conn.execute(sa.text("select count(*) from passive_nodes")).scalar() == 0
