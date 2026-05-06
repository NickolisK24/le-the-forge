"""
Deployment readiness tests — verify the production config contract holds.

These tests keep the four invariants that matter for every Render deploy:
    1. /api/health returns the expected JSON shape with no auth required
    2. Production CORS whitelists only epochforge.gg + www.epochforge.gg
    3. Development CORS keeps the usual localhost origins working
    4. Every env var the app reads has a matching entry in .env.example
    5. render.yaml is valid YAML and declares the four expected services
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest
import yaml

from app import __version__, create_app


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RENDER_YAML = REPO_ROOT / "render.yaml"
ENV_EXAMPLE = REPO_ROOT / ".env.example"
BACKEND_SRC = REPO_ROOT / "backend"


# ---------------------------------------------------------------------------
# /api/health
# ---------------------------------------------------------------------------

def test_health_returns_ok_with_expected_shape(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "ok"
    assert body["version"] == __version__
    assert isinstance(body["patch_version"], str)
    assert isinstance(body["uptime_seconds"], int)
    assert body["uptime_seconds"] >= 0


def test_health_requires_no_authentication(client):
    """No Authorization header — still 200."""
    resp = client.get("/api/health")
    assert resp.status_code == 200


def test_health_survives_missing_version_json(monkeypatch, client):
    """Health check must not fail even if data/version.json disappears."""
    from app.routes import health as health_module

    monkeypatch.setattr(health_module, "_VERSION_JSON", Path("/nonexistent/path.json"))
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["patch_version"] == "unknown"


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

@pytest.fixture
def production_app(monkeypatch):
    """Spin up a real production-env Flask app. We patch the ProductionConfig
    class attributes directly because they're computed at import time from
    os.environ — setting env vars in the test has no effect."""
    from config import ProductionConfig

    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "x" * 64)
    monkeypatch.setattr(ProductionConfig, "JWT_SECRET_KEY", "y" * 64)
    monkeypatch.setattr(
        ProductionConfig,
        "SQLALCHEMY_DATABASE_URI",
        "postgresql://forge:pw@db.example.com:5432/prod",
    )
    monkeypatch.setattr(ProductionConfig, "DISCORD_CLIENT_ID", "prod-client-id")
    monkeypatch.setattr(
        ProductionConfig, "DISCORD_CLIENT_SECRET", "prod-client-secret"
    )
    monkeypatch.setattr(ProductionConfig, "FRONTEND_URL", "https://epochforge.gg")
    monkeypatch.setattr(ProductionConfig, "RATELIMIT_STORAGE_URI", "memory://")
    monkeypatch.setattr(ProductionConfig, "RATELIMIT_ENABLED", False, raising=False)
    return create_app("production")


@pytest.fixture
def development_app():
    return create_app("development")


def _preflight(app, origin: str):
    with app.test_client() as c:
        return c.options(
            "/api/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )


def test_production_cors_allows_bare_domain(production_app):
    resp = _preflight(production_app, "https://epochforge.gg")
    assert resp.headers.get("Access-Control-Allow-Origin") == "https://epochforge.gg"


def test_production_cors_allows_www_subdomain(production_app):
    resp = _preflight(production_app, "https://www.epochforge.gg")
    assert resp.headers.get("Access-Control-Allow-Origin") == "https://www.epochforge.gg"


def test_production_cors_blocks_unknown_origin(production_app):
    resp = _preflight(production_app, "https://evil.example.com")
    assert resp.headers.get("Access-Control-Allow-Origin") is None


def test_development_cors_allows_localhost_vite(development_app):
    resp = _preflight(development_app, "http://localhost:5173")
    assert resp.headers.get("Access-Control-Allow-Origin") == "http://localhost:5173"


def test_development_cors_allows_localhost_cra(development_app):
    resp = _preflight(development_app, "http://localhost:3000")
    assert resp.headers.get("Access-Control-Allow-Origin") == "http://localhost:3000"


def test_development_cors_allows_loopback_ip(development_app):
    resp = _preflight(development_app, "http://127.0.0.1:5173")
    assert resp.headers.get("Access-Control-Allow-Origin") == "http://127.0.0.1:5173"


# ---------------------------------------------------------------------------
# .env.example parity
# ---------------------------------------------------------------------------

def _parse_env_example() -> set[str]:
    keys: set[str] = set()
    for line in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped:
            keys.add(stripped.split("=", 1)[0].strip())
    return keys


def _scan_env_refs() -> set[str]:
    """Return every env var name referenced via os.environ[...] or
    os.environ.get(...) in the backend source tree."""
    pattern = re.compile(r"os\.environ(?:\.get)?\(\s*['\"]([A-Z_][A-Z0-9_]*)['\"]")
    keys: set[str] = set()
    for py in BACKEND_SRC.rglob("*.py"):
        if "tests" in py.parts or "__pycache__" in py.parts or "migrations" in py.parts:
            continue
        try:
            text = py.read_text(encoding="utf-8")
        except OSError:
            continue
        keys.update(pattern.findall(text))
    return keys


# Environment variables that are intentionally not in .env.example because
# they are platform-provided (Render sets them) or test-only.
_ENV_ALLOWLIST = {
    "PORT",                # Render injects this for web services
    "PYTHON_VERSION",      # Render Python runtime
    "NODE_VERSION",        # Render static site runtime
    "PYTHONUNBUFFERED",    # Render recommends this but it has no secret
    "DB_PASSWORD",         # Only used inside docker-compose interpolation
    "GUNICORN_WORKERS",    # Optional tuning knob, documented in deployment.md
    "GUNICORN_THREADS",    # Same
    "GUNICORN_TIMEOUT",    # Same
    "GUNICORN_BIND",       # Same
    "APP_VERSION",         # Render build metadata
    "HOST_PORT",           # docker-compose only
    "LOG_LEVEL",           # optional runtime override; sane defaults in config
    "LOG_FORMAT_JSON",     # optional runtime override
}


def test_every_referenced_env_var_is_documented():
    referenced = _scan_env_refs() - _ENV_ALLOWLIST
    declared = _parse_env_example()
    missing = referenced - declared
    assert not missing, (
        f"Env vars referenced in backend code but missing from .env.example: "
        f"{sorted(missing)}"
    )


# ---------------------------------------------------------------------------
# render.yaml
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def render_blueprint() -> dict:
    return yaml.safe_load(RENDER_YAML.read_text(encoding="utf-8"))


def test_render_yaml_is_valid(render_blueprint):
    assert isinstance(render_blueprint, dict)
    assert "services" in render_blueprint


def test_render_yaml_declares_postgres_database(render_blueprint):
    dbs = {db["name"]: db for db in render_blueprint.get("databases", [])}
    assert "epochforge-db" in dbs, "Missing epochforge-db Postgres in render.yaml"
    assert dbs["epochforge-db"]["plan"] == "starter"


def test_render_yaml_declares_redis_service(render_blueprint):
    services = {s["name"]: s for s in render_blueprint["services"]}
    assert "epochforge-redis" in services, "Missing epochforge-redis in render.yaml"
    assert services["epochforge-redis"]["type"] == "redis"
    assert services["epochforge-redis"]["plan"] == "starter"


def test_render_yaml_api_service_is_wired(render_blueprint):
    services = {s["name"]: s for s in render_blueprint["services"]}
    api = services["epochforge-api"]
    assert api["runtime"] == "python"
    assert api["rootDir"] == "backend"
    assert api["healthCheckPath"] == "/api/health"
    assert api["preDeployCommand"].strip() == "flask db upgrade"

    env = {e["key"]: e for e in api["envVars"]}
    assert env["FLASK_ENV"]["value"] == "production"
    assert "fromDatabase" in env["DATABASE_URL"]
    assert env["DATABASE_URL"]["fromDatabase"]["name"] == "epochforge-db"
    assert "fromService" in env["REDIS_URL"]
    assert env["REDIS_URL"]["fromService"]["name"] == "epochforge-redis"
    # Secrets must be sync:false so they aren't overwritten by blueprint apply.
    for secret_key in (
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "DISCORD_CLIENT_ID",
        "DISCORD_CLIENT_SECRET",
    ):
        assert env[secret_key].get("sync") is False, f"{secret_key} must be sync:false"


def test_render_yaml_frontend_spa_fallback(render_blueprint):
    services = {s["name"]: s for s in render_blueprint["services"]}
    fe = services["epochforge-frontend"]
    assert fe["runtime"] == "static"
    assert fe["rootDir"] == "frontend"
    assert fe["staticPublishPath"] == "dist"
    env = {e["key"]: e for e in fe["envVars"]}
    assert env["VITE_API_BASE_URL"]["value"] == "https://api.epochforge.gg"
    # SPA fallback must be present
    routes = fe.get("routes", [])
    assert any(
        r.get("source") == "/*" and r.get("destination") == "/index.html"
        for r in routes
    ), "Frontend SPA rewrite /* -> /index.html missing from render.yaml"
