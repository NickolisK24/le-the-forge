"""
R0 regression: backend dependency contract for the PostgreSQL driver.

A clean install previously resolved SQLAlchemy 2.1.x, whose default DBAPI for
``postgresql://`` URLs is psycopg (v3). Only psycopg2 is a declared dependency,
so engine creation failed with ModuleNotFoundError and deploys could not boot.
"""

import re
from pathlib import Path

import pytest
import sqlalchemy
from sqlalchemy import create_engine

from config import Config, ProductionConfig, normalize_database_url

REQUIREMENTS = Path(__file__).resolve().parents[1] / "requirements.txt"


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("postgresql://u:p@h:5432/db", "postgresql+psycopg2://u:p@h:5432/db"),
        ("postgres://u:p@h:5432/db", "postgresql+psycopg2://u:p@h:5432/db"),
        ("postgresql+psycopg2://u@h/db", "postgresql+psycopg2://u@h/db"),
        ("postgresql+psycopg://u@h/db", "postgresql+psycopg://u@h/db"),
        ("sqlite:///:memory:", "sqlite:///:memory:"),
        ("", ""),
    ],
)
def test_normalize_database_url(raw, expected):
    assert normalize_database_url(raw) == expected


def test_requirements_pin_sqlalchemy_to_2_0_line():
    text = REQUIREMENTS.read_text(encoding="utf-8")
    pins = re.findall(r"^SQLAlchemy==(\S+)\s*$", text, flags=re.MULTILINE | re.IGNORECASE)
    assert len(pins) == 1, "SQLAlchemy must be pinned exactly once in requirements.txt"
    assert pins[0].startswith("2.0."), f"SQLAlchemy pin {pins[0]} left the 2.0 line"


def test_requirements_declare_psycopg2():
    text = REQUIREMENTS.read_text(encoding="utf-8")
    assert re.search(r"^psycopg2-binary==", text, flags=re.MULTILINE)


def test_installed_sqlalchemy_matches_pinned_line():
    assert sqlalchemy.__version__.startswith("2.0."), sqlalchemy.__version__


def test_default_config_uri_selects_psycopg2():
    assert Config.SQLALCHEMY_DATABASE_URI.startswith("postgresql+psycopg2://")
    assert ProductionConfig.SQLALCHEMY_DATABASE_URI.startswith("postgresql+psycopg2://")


@pytest.mark.parametrize("raw", ["postgresql://u@127.0.0.1:1/db", "postgres://u@127.0.0.1:1/db"])
def test_engine_uses_installed_psycopg2_driver(raw):
    # create_engine imports the DBAPI eagerly but does not connect.
    engine = create_engine(normalize_database_url(raw))
    try:
        assert engine.dialect.name == "postgresql"
        assert engine.dialect.driver == "psycopg2"
    finally:
        engine.dispose()


def test_create_app_normalizes_uri_set_after_config_import(monkeypatch):
    """Even a raw postgresql:// URI patched onto the config class is pinned."""
    from app import create_app

    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "x" * 64)
    monkeypatch.setattr(ProductionConfig, "JWT_SECRET_KEY", "y" * 64)
    monkeypatch.setattr(
        ProductionConfig, "SQLALCHEMY_DATABASE_URI", "postgresql://forge:pw@db.example.com:5432/prod"
    )
    monkeypatch.setattr(ProductionConfig, "DISCORD_CLIENT_ID", "id")
    monkeypatch.setattr(ProductionConfig, "DISCORD_CLIENT_SECRET", "secret")
    monkeypatch.setattr(ProductionConfig, "FRONTEND_URL", "https://epochforge.gg")
    monkeypatch.setattr(ProductionConfig, "RATELIMIT_STORAGE_URI", "memory://")
    app = create_app("production")
    assert app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql+psycopg2://")
    with app.app_context():
        from app import db
        assert db.engine.dialect.driver == "psycopg2"
