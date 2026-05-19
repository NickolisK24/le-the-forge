from __future__ import annotations

from pathlib import Path

from app.routes.trust import (
    ENDPOINT_ROUTE,
    FRONTEND_DISPLAY_READINESS_STATUS_ID,
    SCHEMA_VERSION,
    build_trust_visibility_payload,
    deterministic_hash,
)


def _payload(client):
    response = client.get(ENDPOINT_ROUTE)
    assert response.status_code == 200
    return response.get_json()


def test_trust_visibility_endpoint_returns_v4_5d_3_expanded_payload(client):
    payload = _payload(client)

    assert payload["schema_version"] == "v4.5d.3"
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["status"] == "available"
    assert payload["source_type"] == "backend_expanded_report_backed_visibility"
    assert payload["endpoint_contract"]["methods"] == ["GET"]
    assert payload["endpoint_contract"]["read_only"] is True
    assert payload["endpoint_contract"]["descriptive_only"] is True
    assert payload["endpoint_contract"]["non_mutating"] is True


def test_expanded_payload_is_deterministic(client):
    first = _payload(client)
    second = _payload(client)

    assert first == second
    assert first["payload_hash"] == second["payload_hash"]

    replay_payload = dict(first)
    payload_hash = replay_payload.pop("payload_hash")
    assert payload_hash == deterministic_hash(replay_payload)


def test_expanded_payload_includes_trust_summary_and_frontend_readiness(client):
    payload = _payload(client)

    trust_visibility = payload["trust_visibility"]
    assert trust_visibility["summary_id"] == "backend_trust_visibility_summary"
    assert trust_visibility["status"] == "descriptive_visibility_available"
    assert trust_visibility["schema_version"] == SCHEMA_VERSION
    assert trust_visibility["description"] == "Read-only backend trust visibility payload."

    readiness = payload["frontend_display_readiness"]
    assert readiness["status"] == FRONTEND_DISPLAY_READINESS_STATUS_ID
    assert readiness["expanded_rendering_authorized"] is False
    assert readiness["descriptive_only"] is True


def test_expanded_payload_includes_support_status_records(client):
    payload = _payload(client)

    statuses = [item["status"] for item in payload["support_statuses"]]
    assert statuses == [
        "supported",
        "partially_supported",
        "unsupported",
        "experimental",
        "deprecated",
        "blocked",
        "unknown",
    ]
    assert all(item["description"] for item in payload["support_statuses"])


def test_expanded_payload_includes_explainability_and_evidence_references(client):
    payload = _payload(client)

    explanation_ids = {item["id"] for item in payload["explainability_references"]}
    evidence_ids = {item["id"] for item in payload["evidence_panel_references"]}

    assert {
        "support_explanation_visibility",
        "limitation_explanation_visibility",
        "unsupported_state_explanation_visibility",
        "diagnostics_explanation_visibility",
    }.issubset(explanation_ids)
    assert {
        "support_evidence_reference",
        "explainability_evidence_reference",
        "provenance_evidence_reference",
        "lineage_evidence_reference",
        "missing_evidence_reference",
        "unsupported_evidence_reference",
    }.issubset(evidence_ids)


def test_expanded_payload_includes_provenance_lineage_coverage_and_confidence(client):
    payload = _payload(client)

    provenance_ids = {item["id"] for item in payload["provenance_references"]}
    lineage_ids = {item["id"] for item in payload["lineage_references"]}
    coverage_ids = {item["id"] for item in payload["coverage_references"]}
    confidence_ids = {item["id"] for item in payload["confidence_references"]}

    assert "source_reference_visibility" in provenance_ids
    assert "evidence_origin_reference_visibility" in provenance_ids
    assert "stale_provenance_reference" in provenance_ids
    assert "unknown_provenance_reference" in provenance_ids
    assert "lineage_continuity_reference" in lineage_ids
    assert "source_to_surface_lineage_reference" in lineage_ids
    assert "support_coverage_reference" in coverage_ids
    assert "evidence_coverage_reference" in coverage_ids
    assert "incomplete_coverage_reference" in coverage_ids
    assert "unknown_confidence_reference" in confidence_ids
    assert "incomplete_confidence_reference" in confidence_ids


def test_expanded_payload_includes_fail_visible_diagnostics_and_unsupported_states(client):
    payload = _payload(client)

    diagnostic_ids = {item["id"] for item in payload["diagnostics"]}
    unsupported_states = {item["state"] for item in payload["unsupported_states"]}

    assert {
        "backend_payload_expanded",
        "frontend_rendering_pending",
        "fallback_still_preserved",
        "unsupported_states_visible",
        "no_mutable_trust_state",
        "no_planner_authority",
    }.issubset(diagnostic_ids)
    assert {
        "planner_execution",
        "recommendations",
        "ranking",
        "scoring",
        "authorization",
        "approval",
        "production_enablement",
        "runtime_mutation",
        "operational_behavior",
    } == unsupported_states
    assert all(item["fail_visible"] is True for item in payload["unsupported_states"])


def test_expanded_payload_preserves_prohibitions_without_authority(client):
    payload = _payload(client)

    assert payload["preserved_prohibitions"] == payload["prohibitions"]
    for prohibition in [
        "planner_execution",
        "planner_recommendations",
        "planner_ranking",
        "trust_scoring",
        "evidence_scoring",
        "confidence_scoring",
        "authorization_semantics",
        "approval_semantics",
        "production_enablement",
        "runtime_mutation",
        "operational_behavior",
        "mutable_trust_state",
    ]:
        assert prohibition in payload["preserved_prohibitions"]

    text = str(payload).lower()
    assert "does not imply frontend expanded rendering" in text
    assert "planner authority" in text
    assert "mutable trust state" in text


def test_expanded_payload_missing_report_state_remains_fail_visible():
    missing = build_trust_visibility_payload(Path("backend/tests/missing-v4-5d-3-report.json"))

    assert missing["status"] == "degraded"
    assert missing["source_type"] == "backend_expanded_report_reference_unavailable"
    assert missing["report_reference"]["status"] == "report_missing"
    assert missing["trust_visibility"]["status"] == "descriptive_visibility_available"
    assert any(
        item["id"] == "report_missing" and item["severity"] == "warning"
        for item in missing["diagnostics"]
    )


def test_trust_visibility_endpoint_remains_get_only(app):
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
