"""Trust visibility contract blueprint.

This route exposes deterministic read-only trust visibility metadata. It is a
contract surface only: it does not fetch frontend state, mutate trust state,
trigger planners, score records, or authorize operational behavior.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from flask import Blueprint, jsonify


trust_bp = Blueprint("trust", __name__)

SCHEMA_VERSION = "v4.5d.1"
ENDPOINT_CONTRACT_ID = "v4_5d_1_backend_trust_visibility_endpoint_contract"
ENDPOINT_ROUTE = "/api/trust/visibility"
HEALTH_ENDPOINT = "/api/health"
REPORT_REFERENCE_ID = "v4_5c_5_frontend_trust_closeout_backend_reflection_audit_report"
REPORT_NAME = "v4_5c_5_frontend_trust_closeout_backend_reflection_audit_report"
REPORT_PATH = (
    "docs/generated/"
    "v4_5c_5_frontend_trust_closeout_backend_reflection_audit_report.json"
)
SOURCE_STATUS_ID = "backend_report_backed_visibility_available"
BACKEND_REFLECTION_STATUS_ID = "backend_reflection_contract_defined"
FRONTEND_ALIGNMENT_STATUS_ID = "backend_contract_ready_frontend_fetch_deferred"

_REPO_ROOT = Path(__file__).resolve().parents[3]
_REPORT_FILE = _REPO_ROOT / REPORT_PATH

GUARANTEES = [
    "READ-ONLY",
    "DESCRIPTIVE-ONLY",
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
    "authorization_semantics",
    "approval_semantics",
    "production_enablement",
    "runtime_mutation",
    "operational_behavior",
    "mutable_trust_state",
    "frontend_live_fetch_integration",
]

NON_AUTHORITY_STATEMENT = (
    "Backend trust visibility endpoint contract does NOT imply frontend live "
    "fetch integration, planner authority, execution safety, correctness "
    "guarantees, operational readiness, production enablement, recommendation "
    "quality, ranking quality, scoring quality, triage priority, authorization, "
    "approval, or mutable trust state."
)


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
            "id": "frontend_fetch_deferred",
            "severity": "informational",
            "message": (
                "Backend trust visibility endpoint contract is defined; "
                "frontend live fetch integration remains deferred."
            ),
        },
        {
            "id": "health_trust_endpoint_distinction",
            "severity": "informational",
            "message": (
                "Backend health confirms process liveness and does not prove "
                "trust visibility alignment."
            ),
        },
        {
            "id": "unsupported_state_visibility_preserved",
            "severity": "informational",
            "message": "Unsupported states remain explicit in the trust visibility contract.",
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
                "the endpoint returns a fail-visible contract payload."
            ),
        },
        *diagnostics,
    ]


def build_trust_visibility_payload(report_path: Path = _REPORT_FILE) -> dict[str, Any]:
    report_reference = _load_report_reference(report_path)
    status = "available" if report_reference["status"] == "report_available" else "degraded"
    source_type = (
        "backend_report_backed_visibility"
        if status == "available"
        else "backend_report_reference_unavailable"
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
            "frontend_live_fetch_integration": "deferred",
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
            "live_frontend_fetch": False,
            "integration_readiness": "ready_for_v4_5d_2_frontend_fetch_integration",
        },
        "guarantees": GUARANTEES,
        "prohibitions": PROHIBITIONS,
        "diagnostics": _diagnostics_for_report(report_reference),
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
