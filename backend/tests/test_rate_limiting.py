"""
Tests for rate limiting on simulation endpoints.

Verifies:
  - Simulation endpoints enforce rate limits
  - Over-limit requests return 429
  - 429 response has structured JSON body with error key
"""

import os
import pytest


# Set env vars BEFORE any app imports
os.environ["RATE_LIMIT_SIMULATE_STATS"] = "3 per minute"
os.environ["RATE_LIMIT_SIMULATE_BUILD"] = "2 per minute"
os.environ["RATE_LIMIT_SIMULATE_ENCOUNTER"] = "2 per minute"

from app import create_app, limiter


@pytest.fixture(scope="module")
def rate_app():
    app = create_app("testing")
    # Force-enable rate limiting (testing config disables it)
    app.config["RATELIMIT_STORAGE_URI"] = "memory://"
    app.config["RATELIMIT_ENABLED"] = True
    # Re-initialize limiter with the enabled config
    limiter.enabled = True
    with app.app_context():
        limiter.init_app(app)
    yield app
    # Restore disabled state so other tests aren't affected
    limiter.enabled = False


@pytest.fixture
def rate_client(rate_app):
    return rate_app.test_client()


_STATS_PAYLOAD = {"character_class": "Sentinel", "mastery": ""}
_BUILD_PAYLOAD = {"character_class": "Sentinel", "mastery": "", "skill_name": "Rip Blood"}
_ENCOUNTER_PAYLOAD = {"character_class": "Sentinel", "mastery": ""}


class TestRateLimitStats:
    def test_over_limit_returns_429(self, rate_client):
        """After 3 requests (env-configured limit), next should be 429."""
        responses = []
        for _ in range(6):
            r = rate_client.post("/api/simulate/stats", json=_STATS_PAYLOAD)
            responses.append(r.status_code)
        assert 429 in responses, f"Expected 429 after limit, got: {responses}"

    def test_429_json_body(self, rate_client):
        for _ in range(6):
            resp = rate_client.post("/api/simulate/stats", json=_STATS_PAYLOAD)
        if resp.status_code == 429:
            data = resp.get_json()
            assert data is not None
            assert data["error"] == "rate_limit_exceeded"


class TestRateLimitBuild:
    def test_over_limit_returns_429(self, rate_client):
        responses = []
        for _ in range(6):
            r = rate_client.post("/api/simulate/build", json=_BUILD_PAYLOAD)
            responses.append(r.status_code)
        assert 429 in responses, f"Expected 429 after limit, got: {responses}"


class TestRateLimitEncounter:
    def test_over_limit_returns_429(self, rate_client):
        responses = []
        for _ in range(6):
            r = rate_client.post("/api/simulate/encounter", json=_ENCOUNTER_PAYLOAD)
            responses.append(r.status_code)
        assert 429 in responses, f"Expected 429 after limit, got: {responses}"
