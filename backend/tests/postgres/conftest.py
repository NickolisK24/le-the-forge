"""PostgreSQL integration fixtures (AUDIT-R2 P15).

The suite runs only when ``FORGE_PG_TEST_URL`` points at a PostgreSQL server
the tests may create and drop databases on, for example
``postgresql://forge@127.0.0.1:5432/postgres``. CI provides one through a
service container; without it every test here is skipped, so the default
SQLite suite is unaffected.

Each test gets its own freshly created database, dropped afterwards. The
app is built with a test-only config subclass registered at runtime; no
production configuration changes.
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest

PG_URL = os.environ.get("FORGE_PG_TEST_URL")
BACKEND = Path(__file__).resolve().parents[2]
MIGRATIONS = str(BACKEND / "migrations")

pytestmark = pytest.mark.postgres


def pytest_collection_modifyitems(config, items):
    if PG_URL:
        return
    skip = pytest.mark.skip(reason="set FORGE_PG_TEST_URL to run the PostgreSQL suite")
    for item in items:
        if "tests/postgres" in str(item.fspath).replace("\\", "/"):
            item.add_marker(skip)


def _admin_engine():
    import sqlalchemy as sa
    return sa.create_engine(PG_URL, isolation_level="AUTOCOMMIT")


def _db_url(name: str) -> str:
    import sqlalchemy as sa
    return sa.engine.make_url(PG_URL).set(database=name).render_as_string(hide_password=False)


@pytest.fixture
def pg_app():
    """Factory: a Flask app bound to a brand-new, empty PostgreSQL database."""
    import sqlalchemy as sa

    from config import TestingConfig, config

    made = []

    def make():
        name = f"forge_p15_{uuid.uuid4().hex[:10]}"
        with _admin_engine().connect() as c:
            c.execute(sa.text(f'CREATE DATABASE "{name}"'))
        key = f"postgres_test_{name}"
        config[key] = type("PostgresTestingConfig", (TestingConfig,), {"SQLALCHEMY_DATABASE_URI": _db_url(name)})
        from app import create_app
        app = create_app(key)
        made.append((name, key, app))
        return app

    yield make

    from app import db
    for name, key, app in made:
        with app.app_context():
            db.session.remove()
            db.engine.dispose()
        config.pop(key, None)
        with _admin_engine().connect() as c:
            c.execute(sa.text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
