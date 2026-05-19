"""Trust visibility endpoint.

This route exposes deterministic read-only trust visibility metadata and
expanded visibility records. It does not mutate trust state, trigger planners,
score records, rank records, recommend actions, or authorize operational
behavior.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from flask import Blueprint, jsonify


trust_bp = Blueprint("trust", __name__)

SCHEMA_VERSION = "v4.5d.3"
ENDPOINT_CONTRACT_ID = "v4_5d_3_backend_trust_visibility_payload_expansion"
ENDPOINT_ROUTE = "/api/trust/visibility"
HEALTH_ENDPOINT = "/api/health"
REPORT_REFERENCE_ID = "v4_5d_2_frontend_trust_backend_fetch_integration_report"
REPORT_NAME = "v4_5d_2_frontend_trust_backend_fetch_integration_report"
REPORT_PATH = (
    "docs/generated/"
    "v4_5d_2_frontend_trust_backend_fetch_integration_report.json"
)
SOURCE_STATUS_ID = "backend_expanded_report_backed_visibility_available"
BACKEND_REFLECTION_STATUS_ID = "backend_reflection_expanded_payload_defined"
FRONTEND_ALIGNMENT_STATUS_ID = "frontend_backend_alignment_endpoint_visible"
FRONTEND_DISPLAY_READINESS_STATUS_ID = (
    "backend_payload_ready_frontend_rendering_pending"
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_REPORT_FILE = _REPO_ROOT / REPORT_PATH

GUARANTEES = [
    "READ-ONLY",
    "DESCRIPTIVE-ONLY",
    "GET-only",
    "NON-mutating",
    "NON-operational",
    "NON-authorizing",
    "NON-approving",
    "NON-recommending",
    "NON-ranking",
    "NON-scoring",
    "NON-triaging",
]

PROHIBITIONS = [
    "planner_execution",
    "planner_recommendations",
    "planner_ranking",
    "trust_scoring",
    "evidence_scoring",
    "confidence_scoring",
    "recommendation_systems",
    "ranking_systems",
    "triage_systems",
    "authorization_semantics",
    "approval_semantics",
    "orchestration_execution",
    "orchestration_routing",
    "orchestration_traversal",
    "production_enablement",
    "runtime_mutation",
    "operational_behavior",
    "mutable_trust_state",
    "report_driven_planner_behavior",
    "backend_driven_planner_behavior",
]

NON_AUTHORITY_STATEMENT = (
    "Backend trust payload expansion does NOT imply frontend expanded "
    "rendering, planner authority, execution safety, correctness guarantees, "
    "operational readiness, production enablement, recommendation quality, "
    "ranking quality, scoring quality, triage priority, authorization, "
    "approval, or mutable trust state."
)


SUPPORT_STATUSES = [
    {
        "id": "support_status_supported",
        "status": "supported",
        "scope": "backend_trust_visibility_endpoint_contract",
        "description": (
            "The backend trust visibility endpoint remains GET-only, read-only, "
            "descriptive-only, and non-mutating."
        ),
    },
    {
        "id": "support_status_partially_supported",
        "status": "partially_supported",
        "scope": "frontend_trust_surface",
        "description": (
            "Frontend trust surface has endpoint-backed metadata and deterministic "
            "fallback visibility; expanded backend rendering is deferred."
        ),
    },
    {
        "id": "support_status_unsupported",
        "status": "unsupported",
        "scope": "planner_execution",
        "description": "Planner execution remains unsupported and fail-visible.",
    },
    {
        "id": "support_status_experimental",
        "status": "experimental",
        "scope": "expanded_backend_payload_visibility",
        "description": (
            "Expanded backend payload records are available for future read-only "
            "frontend rendering without operational authority."
        ),
    },
    {
        "id": "support_status_deprecated",
        "status": "deprecated",
        "scope": "static_only_backend_reflection_gap",
        "description": (
            "The prior backend-reflection-missing state is superseded by this "
            "read-only endpoint payload expansion."
        ),
    },
    {
        "id": "support_status_blocked",
        "status": "blocked",
        "scope": "mutable_trust_state",
        "description": "Mutable trust state remains blocked.",
    },
    {
        "id": "support_status_unknown",
        "status": "unknown",
        "scope": "future_governance_aggregation_payloads",
        "description": (
            "Future governance aggregation payload coverage remains unknown until "
            "a dedicated phase defines it."
        ),
    },
]

EXPLAINABILITY_REFERENCES = [
    {
        "id": "support_explanation_visibility",
        "status": "visible",
        "description": "Support status explanations remain descriptive-only.",
    },
    {
        "id": "limitation_explanation_visibility",
        "status": "visible",
        "description": "Limitations remain explicit and fail-visible.",
    },
    {
        "id": "unsupported_state_explanation_visibility",
        "status": "visible",
        "description": "Unsupported-state explanations remain visible.",
    },
    {
        "id": "diagnostics_explanation_visibility",
        "status": "visible",
        "description": "Diagnostics explanations remain read-only.",
    },
]

EVIDENCE_PANEL_REFERENCES = [
    {
        "id": "support_evidence_reference",
        "status": "visible",
        "description": "Support evidence references remain grouped without scoring.",
    },
    {
        "id": "explainability_evidence_reference",
        "status": "visible",
        "description": "Explainability evidence references remain descriptive-only.",
    },
    {
        "id": "provenance_evidence_reference",
        "status": "visible",
        "description": "Provenance evidence references do not imply source authority.",
    },
    {
        "id": "lineage_evidence_reference",
        "status": "visible",
        "description": "Lineage evidence references preserve continuity visibility.",
    },
    {
        "id": "missing_evidence_reference",
        "status": "visible",
        "description": "Missing evidence remains fail-visible.",
    },
    {
        "id": "unsupported_evidence_reference",
        "status": "visible",
        "description": "Unsupported evidence remains explicit.",
    },
]

PROVENANCE_REFERENCES = [
    {
        "id": "source_reference_visibility",
        "status": "visible",
        "description": "Source references are descriptive and non-authoritative.",
    },
    {
        "id": "evidence_origin_reference_visibility",
        "status": "visible",
        "description": "Evidence origin references remain public and deterministic.",
    },
    {
        "id": "provenance_continuity_reference",
        "status": "visible",
        "description": "Provenance continuity remains visible without restoration behavior.",
    },
    {
        "id": "stale_provenance_reference",
        "status": "visible",
        "description": "Stale provenance remains explicit.",
    },
    {
        "id": "unknown_provenance_reference",
        "status": "visible",
        "description": "Unknown provenance remains fail-visible.",
    },
]

LINEAGE_REFERENCES = [
    {
        "id": "lineage_continuity_reference",
        "status": "visible",
        "description": "Lineage continuity remains visible without repair behavior.",
    },
    {
        "id": "source_to_surface_lineage_reference",
        "status": "visible",
        "description": "Source-to-surface lineage remains descriptive-only.",
    },
    {
        "id": "unknown_lineage_reference",
        "status": "visible",
        "description": "Unknown lineage remains explicit and fail-visible.",
    },
]

COVERAGE_REFERENCES = [
    {
        "id": "support_coverage_reference",
        "status": "visible",
        "description": "Support coverage remains descriptive-only.",
    },
    {
        "id": "evidence_coverage_reference",
        "status": "visible",
        "description": "Evidence coverage remains visible without ranking.",
    },
    {
        "id": "explainability_coverage_reference",
        "status": "visible",
        "description": "Explainability coverage remains read-only.",
    },
    {
        "id": "provenance_coverage_reference",
        "status": "visible",
        "description": "Provenance coverage does not imply source authority.",
    },
    {
        "id": "lineage_coverage_reference",
        "status": "visible",
        "description": "Lineage coverage remains visible without operational semantics.",
    },
    {
        "id": "incomplete_coverage_reference",
        "status": "visible",
        "description": "Incomplete coverage remains explicit.",
    },
]

CONFIDENCE_REFERENCES = [
    {
        "id": "evidence_supported_confidence_reference",
        "status": "visible",
        "description": "Confidence visibility remains non-scoring.",
    },
    {
        "id": "unknown_confidence_reference",
        "status": "visible",
        "description": "Unknown confidence remains fail-visible.",
    },
    {
        "id": "incomplete_confidence_reference",
        "status": "visible",
        "description": "Incomplete confidence remains descriptive-only.",
    },
]

UNSUPPORTED_STATES = [
    {
        "id": "unsupported_planner_execution",
        "state": "planner_execution",
        "status": "unsupported",
        "fail_visible": True,
    },
    {
        "id": "unsupported_recommendations",
        "state": "recommendations",
        "status": "unsupported",
        "fail_visible": True,
    },
    {
        "id": "unsupported_ranking",
        "state": "ranking",
        "status": "unsupported",
        "fail_visible": True,
    },
    {
        "id": "unsupported_scoring",
        "state": "scoring",
        "status": "unsupported",
        "fail_visible": True,
    },
    {
        "id": "unsupported_authorization",
        "state": "authorization",
        "status": "unsupported",
        "fail_visible": True,
    },
    {
        "id": "unsupported_approval",
        "state": "approval",
        "status": "unsupported",
        "fail_visible": True,
    },
    {
        "id": "unsupported_production_enablement",
        "state": "production_enablement",
        "status": "unsupported",
        "fail_visible": True,
    },
    {
        "id": "unsupported_runtime_mutation",
        "state": "runtime_mutation",
        "status": "unsupported",
        "fail_visible": True,
    },
    {
        "id": "unsupported_operational_behavior",
        "state": "operational_behavior",
        "status": "unsupported",
        "fail_visible": True,
    },
]


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def deterministic_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _load_report_reference(report_path: Path = _REPORT_FILE) -> dict[str, Any]:
    base_reference: dict[str, Any] = {
        "report_reference_id": REPORT_REFERENCE_ID,
        "name": REPORT_NAME,
        "path": REPORT_PATH,
        "hash": "missing",
        "available": False,
        "status": "report_missing",
    }
    try:
        raw = report_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return base_reference
    except OSError as exc:
        return {
            **base_reference,
            "status": "report_unreadable",
            "error": exc.__class__.__name__,
        }

    try:
        report = json.loads(raw)
    except json.JSONDecodeError:
        return {
            **base_reference,
            "status": "report_malformed",
            "available": True,
        }

    report_hash = report.get("deterministic_report_hash")
    if not isinstance(report_hash, str) or not report_hash:
        return {
            **base_reference,
            "status": "report_hash_missing",
            "available": True,
        }

    return {
        **base_reference,
        "hash": report_hash,
        "available": True,
        "status": "report_available",
        "phase_id": report.get("phase_id", "unknown"),
    }


def _diagnostics_for_report(report_reference: dict[str, Any]) -> list[dict[str, str]]:
    diagnostics = [
        {
            "id": "backend_payload_expanded",
            "severity": "informational",
            "message": (
                "Backend trust visibility payload includes deterministic "
                "read-only trust visibility records."
            ),
        },
        {
            "id": "frontend_rendering_pending",
            "severity": "informational",
            "message": (
                "Expanded backend payload is frontend-ready; dedicated frontend "
                "expanded rendering remains deferred."
            ),
        },
        {
            "id": "fallback_still_preserved",
            "severity": "informational",
            "message": "Frontend deterministic fallback visibility remains preserved.",
        },
        {
            "id": "unsupported_states_visible",
            "severity": "informational",
            "message": "Unsupported states remain explicit and fail-visible.",
        },
        {
            "id": "no_mutable_trust_state",
            "severity": "informational",
            "message": "The endpoint does not expose mutable trust state.",
        },
        {
            "id": "no_planner_authority",
            "severity": "informational",
            "message": "The endpoint does not expose planner authority.",
        },
    ]
    if report_reference["status"] == "report_available":
        return [
            {
                "id": "report_reference_available",
                "severity": "informational",
                "message": "Report-backed trust visibility metadata is available.",
            },
            *diagnostics,
        ]
    return [
        {
            "id": report_reference["status"],
            "severity": "warning",
            "message": (
                "Report-backed trust visibility metadata is unavailable or incomplete; "
                "the endpoint returns a fail-visible expanded payload."
            ),
        },
        *diagnostics,
    ]


def build_trust_visibility_payload(report_path: Path = _REPORT_FILE) -> dict[str, Any]:
    report_reference = _load_report_reference(report_path)
    status = "available" if report_reference["status"] == "report_available" else "degraded"
    source_type = (
        "backend_expanded_report_backed_visibility"
        if status == "available"
        else "backend_expanded_report_reference_unavailable"
    )
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "endpoint_contract": {
            "endpoint_contract_id": ENDPOINT_CONTRACT_ID,
            "endpoint_route": ENDPOINT_ROUTE,
            "schema_version": SCHEMA_VERSION,
            "methods": ["GET"],
            "read_only": True,
            "descriptive_only": True,
            "non_mutating": True,
        },
        "source_type": source_type,
        "source_status": {
            "source_status_id": SOURCE_STATUS_ID,
            "source_type": source_type,
            "report_backed": status == "available",
            "frontend_expanded_rendering": "deferred",
            "mutable_trust_state": False,
        },
        "report_reference": report_reference,
        "backend_reflection": {
            "status": BACKEND_REFLECTION_STATUS_ID,
            "backend_reflection_status_id": BACKEND_REFLECTION_STATUS_ID,
            "health_endpoint": HEALTH_ENDPOINT,
            "trust_endpoint": ENDPOINT_ROUTE,
            "alignment_status": FRONTEND_ALIGNMENT_STATUS_ID,
            "frontend_alignment_status_id": FRONTEND_ALIGNMENT_STATUS_ID,
        },
        "frontend_alignment": {
            "status": FRONTEND_ALIGNMENT_STATUS_ID,
            "live_frontend_fetch": True,
            "expanded_payload_rendering": "deferred_to_v4_5d_4",
            "integration_readiness": FRONTEND_DISPLAY_READINESS_STATUS_ID,
        },
        "trust_visibility": {
            "summary_id": "backend_trust_visibility_summary",
            "status": "descriptive_visibility_available",
            "source_type": source_type,
            "schema_version": SCHEMA_VERSION,
            "report_reference_id": report_reference["report_reference_id"],
            "description": "Read-only backend trust visibility payload.",
        },
        "support_statuses": SUPPORT_STATUSES,
        "explainability_references": EXPLAINABILITY_REFERENCES,
        "evidence_panel_references": EVIDENCE_PANEL_REFERENCES,
        "provenance_references": PROVENANCE_REFERENCES,
        "lineage_references": LINEAGE_REFERENCES,
        "coverage_references": COVERAGE_REFERENCES,
        "confidence_references": CONFIDENCE_REFERENCES,
        "diagnostics": _diagnostics_for_report(report_reference),
        "unsupported_states": UNSUPPORTED_STATES,
        "preserved_prohibitions": PROHIBITIONS,
        "frontend_display_readiness": {
            "status": FRONTEND_DISPLAY_READINESS_STATUS_ID,
            "description": (
                "Frontend may render expanded backend payload after dedicated "
                "frontend integration."
            ),
            "frontend_route": "/trusted-data/frontend-trust",
            "expanded_rendering_authorized": False,
            "descriptive_only": True,
        },
        "guarantees": GUARANTEES,
        "prohibitions": PROHIBITIONS,
        "fallback_payload_shapes": [
            {
                "id": "report_missing",
                "status": "degraded",
                "available": False,
                "fail_visible": True,
            },
            {
                "id": "report_unreadable",
                "status": "degraded",
                "available": False,
                "fail_visible": True,
            },
            {
                "id": "report_malformed",
                "status": "degraded",
                "available": True,
                "fail_visible": True,
            },
            {
                "id": "endpoint_contract_unavailable",
                "status": "degraded",
                "available": False,
                "fail_visible": True,
            },
            {
                "id": "unknown_backend_trust_state",
                "status": "degraded",
                "available": False,
                "fail_visible": True,
            },
        ],
        "non_authority_statement": NON_AUTHORITY_STATEMENT,
    }
    payload["payload_hash"] = deterministic_hash(payload)
    return payload


@trust_bp.get("/visibility")
def trust_visibility():
    return jsonify(build_trust_visibility_payload()), 200
