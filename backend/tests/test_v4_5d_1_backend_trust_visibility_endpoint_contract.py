from __future__ import annotations

from pathlib import Path

from app.routes.trust import (
    BACKEND_REFLECTION_STATUS_ID,
    ENDPOINT_ROUTE,
    FRONTEND_ALIGNMENT_STATUS_ID,
    HEALTH_ENDPOINT,
    SCHEMA_VERSION,
    build_trust_visibility_payload,
    deterministic_hash,
)


def _payload(client):
    response = client.get(ENDPOINT_ROUTE)
    assert response.status_code == 200
    return response.get_json()


def test_trust_visibility_endpoint_returns_deterministic_contract(client):
    first = _payload(client)
    second = _payload(client)

    assert first == second
    assert first["schema_version"] == SCHEMA_VERSION
    assert first["status"] == "available"
    assert first["source_type"] == "backend_expanded_report_backed_visibility"
    assert first["payload_hash"] == second["payload_hash"]

    replay_payload = dict(first)
    payload_hash = replay_payload.pop("payload_hash")
    assert payload_hash == deterministic_hash(replay_payload)


def test_trust_visibility_endpoint_includes_identity_and_report_metadata(client):
    payload = _payload(client)

    contract = payload["endpoint_contract"]
    assert contract["endpoint_route"] == ENDPOINT_ROUTE
    assert contract["schema_version"] == SCHEMA_VERSION
    assert contract["methods"] == ["GET"]
    assert contract["read_only"] is True
    assert contract["descriptive_only"] is True
    assert contract["non_mutating"] is True

    report_reference = payload["report_reference"]
    assert report_reference["name"] == (
        "v4_5d_2_frontend_trust_backend_fetch_integration_report"
    )
    assert report_reference["path"] == (
        "docs/generated/"
        "v4_5d_2_frontend_trust_backend_fetch_integration_report.json"
    )
    assert report_reference["available"] is True
    assert report_reference["status"] == "report_available"
    assert isinstance(report_reference["hash"], str)
    assert len(report_reference["hash"]) == 64


def test_trust_visibility_endpoint_includes_backend_reflection_and_frontend_alignment(client):
    payload = _payload(client)

    backend_reflection = payload["backend_reflection"]
    assert backend_reflection["status"] == BACKEND_REFLECTION_STATUS_ID
    assert backend_reflection["health_endpoint"] == HEALTH_ENDPOINT
    assert backend_reflection["trust_endpoint"] == ENDPOINT_ROUTE
    assert backend_reflection["alignment_status"] == FRONTEND_ALIGNMENT_STATUS_ID

    frontend_alignment = payload["frontend_alignment"]
    assert frontend_alignment["status"] == FRONTEND_ALIGNMENT_STATUS_ID
    assert frontend_alignment["live_frontend_fetch"] is True
    assert frontend_alignment["integration_readiness"] == (
        "backend_payload_ready_frontend_rendering_pending"
    )


def test_trust_visibility_endpoint_preserves_guarantees_and_prohibitions(client):
    payload = _payload(client)

    for guarantee in [
        "READ-ONLY",
        "DESCRIPTIVE-ONLY",
        "NON-operational",
        "NON-authorizing",
        "NON-approving",
        "NON-recommending",
        "NON-ranking",
        "NON-scoring",
        "NON-triaging",
    ]:
        assert guarantee in payload["guarantees"]

    for prohibition in [
        "planner_execution",
        "planner_recommendations",
        "planner_ranking",
        "trust_scoring",
        "authorization_semantics",
        "approval_semantics",
        "production_enablement",
        "runtime_mutation",
        "operational_behavior",
        "mutable_trust_state",
    ]:
        assert prohibition in payload["prohibitions"]

    text = str(payload).lower()
    assert "backend trust payload expansion does not imply" in text
    assert "frontend expanded rendering" in text


def test_trust_visibility_endpoint_missing_report_payload_is_fail_visible():
    missing_report = Path("backend/tests/missing-v4-5d-1-report.json")

    payload = build_trust_visibility_payload(missing_report)

    assert payload["status"] == "degraded"
    assert payload["source_type"] == "backend_expanded_report_reference_unavailable"
    assert payload["report_reference"]["available"] is False
    assert payload["report_reference"]["status"] == "report_missing"
    assert any(
        diagnostic["id"] == "report_missing"
        and diagnostic["severity"] == "warning"
        for diagnostic in payload["diagnostics"]
    )
    assert any(
        shape["id"] == "report_missing" and shape["fail_visible"] is True
        for shape in payload["fallback_payload_shapes"]
    )


def test_trust_visibility_route_is_get_only_and_non_mutating(app, client):
    matching_rules = [
        rule
        for rule in app.url_map.iter_rules()
        if rule.rule == ENDPOINT_ROUTE
    ]
    assert len(matching_rules) == 1

    allowed_methods = matching_rules[0].methods
    assert "GET" in allowed_methods
    assert "POST" not in allowed_methods
    assert "PUT" not in allowed_methods
    assert "PATCH" not in allowed_methods
    assert "DELETE" not in allowed_methods
