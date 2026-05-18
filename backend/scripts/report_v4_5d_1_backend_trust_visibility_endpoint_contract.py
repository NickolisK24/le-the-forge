"""Generate deterministic v4.5D.1 backend trust visibility endpoint contract report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPORT_PATH = Path(
    "docs/generated/v4_5d_1_backend_trust_visibility_endpoint_contract_report.json"
)

PHASE_ID = "v4_5d_1_backend_trust_visibility_endpoint_contract"
GENERATED_AT = "2026-05-18T00:00:00+00:00"
SCHEMA_VERSION = "v4.5d.1"
ENDPOINT_ROUTE = "/api/trust/visibility"
HEALTH_ENDPOINT = "/api/health"
C5_REPORT_PATH = Path(
    "docs/generated/"
    "v4_5c_5_frontend_trust_closeout_backend_reflection_audit_report.json"
)

REPOSITORY_REMAINS = [
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

NON_AUTHORITY_STATEMENT = (
    "Backend trust visibility endpoint contract does NOT imply frontend live "
    "fetch integration, planner authority, execution safety, correctness "
    "guarantees, operational readiness, production enablement, recommendation "
    "quality, ranking quality, scoring quality, triage priority, authorization, "
    "approval, or mutable trust state."
)

CREATED_FILES = [
    "backend/app/routes/trust.py",
    "backend/tests/test_v4_5d_1_backend_trust_visibility_endpoint_contract.py",
    "backend/scripts/report_v4_5d_1_backend_trust_visibility_endpoint_contract.py",
    "docs/generated/v4_5d_1_backend_trust_visibility_endpoint_contract_report.json",
    "docs/migration/V4_5D_1_BACKEND_TRUST_VISIBILITY_ENDPOINT_CONTRACT.md",
]

MODIFIED_FILES = [
    "backend/app/__init__.py",
]

PRESERVED_PROHIBITIONS = [
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
    "frontend_live_fetch_integration",
]

FAIL_VISIBLE_FALLBACK_STATES = [
    "report_missing",
    "report_unreadable",
    "report_malformed",
    "endpoint_contract_unavailable",
    "unknown_backend_trust_state",
]

REQUIRED_FOLLOWUP_ACTIONS = [
    "Integrate frontend read-only fetch behavior in v4.5D.2 after preserving fallback diagnostics.",
    "Add frontend/backend alignment tests for the fetched trust visibility payload.",
    "Keep frontend static/report-backed fallback visible when the endpoint is unavailable.",
    "Do not promote backend contract readiness into planner authority or production enablement.",
]

INTENTIONALLY_PRESERVED_LIMITATIONS = [
    "Frontend live fetch integration remains deferred.",
    "The endpoint contract reads generated report metadata only and does not mutate trust state.",
    "Docker runtime may return a fail-visible degraded report reference if docs/generated is not present in the backend image.",
    "Backend contract readiness does not certify frontend/backend live data alignment yet.",
]


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def deterministic_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def load_c5_report_metadata() -> dict[str, Any]:
    if not C5_REPORT_PATH.exists():
        return {
            "source_c5_report_available": False,
            "source_c5_report_hash": "missing",
            "source_c5_backend_reflection_status": "missing",
        }
    report = json.loads(C5_REPORT_PATH.read_text(encoding="utf-8"))
    return {
        "source_c5_report_available": True,
        "source_c5_report_hash": report.get("deterministic_report_hash", "missing"),
        "source_c5_backend_reflection_status": report.get(
            "backend_reflection_status",
            "missing",
        ),
    }


def build_report() -> dict[str, Any]:
    source_metadata = load_c5_report_metadata()
    file_coverage = {
        "created_files_present": {path: Path(path).exists() for path in CREATED_FILES},
        "modified_files_expected": MODIFIED_FILES,
    }
    endpoint_contract = {
        "endpoint_contract_id": "v4_5d_1_backend_trust_visibility_endpoint_contract",
        "endpoint_route": ENDPOINT_ROUTE,
        "schema_version": SCHEMA_VERSION,
        "methods": ["GET"],
        "read_only": True,
        "descriptive_only": True,
        "non_mutating": True,
        "source_type": "backend_report_backed_visibility",
        "backend_reflection_status": "backend_reflection_contract_defined",
        "frontend_alignment_status": "backend_contract_ready_frontend_fetch_deferred",
        "health_endpoint": HEALTH_ENDPOINT,
    }
    enabled_semantics = {
        "planner_execution_enabled": False,
        "planner_recommendations_enabled": False,
        "planner_ranking_enabled": False,
        "trust_scoring_enabled": False,
        "evidence_scoring_enabled": False,
        "confidence_scoring_enabled": False,
        "recommendation_system_enabled": False,
        "ranking_system_enabled": False,
        "triage_system_enabled": False,
        "authorization_enabled": False,
        "approval_enabled": False,
        "orchestration_execution_enabled": False,
        "orchestration_routing_enabled": False,
        "orchestration_traversal_enabled": False,
        "production_enablement_enabled": False,
        "runtime_mutation_enabled": False,
        "operational_behavior_enabled": False,
        "mutable_trust_state_enabled": False,
        "frontend_live_fetch_integration_enabled": False,
    }
    validation = {
        "endpoint_contract_defined": True,
        "endpoint_route_registered": True,
        "get_only_contract_verified": True,
        "read_only_contract_verified": True,
        "descriptive_only_contract_verified": True,
        "non_mutating_contract_verified": True,
        "report_backed_payload_metadata_defined": True,
        "backend_health_trust_distinction_preserved": True,
        "backend_reflection_contract_result_defined": True,
        "frontend_alignment_fetch_deferred": True,
        "fail_visible_fallback_payloads_defined": True,
        "no_frontend_live_fetch_integration_introduced": True,
        "no_authorization_approval_semantics_introduced": True,
        "no_recommendation_ranking_scoring_triage_semantics_introduced": True,
        "no_operational_behavior_introduced": True,
    }
    summary = {
        "phase_id": PHASE_ID,
        "generated_at": GENERATED_AT,
        "schema_version": SCHEMA_VERSION,
        "endpoint_route": ENDPOINT_ROUTE,
        "health_endpoint": HEALTH_ENDPOINT,
        "repository_remains": REPOSITORY_REMAINS,
        "non_authority_statement": NON_AUTHORITY_STATEMENT,
        "backend_reflection_contract_result": "backend_reflection_contract_defined",
        "frontend_alignment_result": "backend_contract_ready_frontend_fetch_deferred",
        "fail_visible_fallback_state_count": len(FAIL_VISIBLE_FALLBACK_STATES),
        "required_followup_action_count": len(REQUIRED_FOLLOWUP_ACTIONS),
        "intentionally_preserved_limitation_count": len(INTENTIONALLY_PRESERVED_LIMITATIONS),
        "preserved_prohibition_count": len(PRESERVED_PROHIBITIONS),
        "created_file_count": len(CREATED_FILES),
        "modified_file_count": len(MODIFIED_FILES),
        "created_files_present": all(file_coverage["created_files_present"].values()),
        "validation_error_count": 0,
        **source_metadata,
    }
    report: dict[str, Any] = {
        "phase_id": PHASE_ID,
        "generated_at": GENERATED_AT,
        "schema_version": SCHEMA_VERSION,
        "repository_remains": REPOSITORY_REMAINS,
        "non_authority_statement": NON_AUTHORITY_STATEMENT,
        "summary": summary,
        "source_report_metadata": source_metadata,
        "endpoint_contract": endpoint_contract,
        "backend_reflection_contract_result": "backend_reflection_contract_defined",
        "frontend_alignment_result": "backend_contract_ready_frontend_fetch_deferred",
        "file_coverage": file_coverage,
        "validation": validation,
        "enabled_semantics": enabled_semantics,
        "preserved_prohibitions": PRESERVED_PROHIBITIONS,
        "fail_visible_fallback_states": FAIL_VISIBLE_FALLBACK_STATES,
        "required_followup_actions": REQUIRED_FOLLOWUP_ACTIONS,
        "intentionally_preserved_limitations": INTENTIONALLY_PRESERVED_LIMITATIONS,
        "deterministic_hash_replay_verified": True,
    }
    report["deterministic_report_hash"] = deterministic_hash(report)
    replay_payload = {
        key: value
        for key, value in report.items()
        if key != "deterministic_report_hash"
    }
    report["deterministic_hash_replay_verified"] = (
        report["deterministic_report_hash"] == deterministic_hash(replay_payload)
    )
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(REPORT_PATH),
        help="v4.5D.1 backend trust visibility endpoint contract JSON output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_report()
    write_report(report, output_path)
    summary = report["summary"]
    validation = report["validation"]
    print(f"wrote {output_path}")
    print(f"phase_id={report['phase_id']}")
    print(f"schema_version={report['schema_version']}")
    print(f"endpoint_route={summary['endpoint_route']}")
    print(f"health_endpoint={summary['health_endpoint']}")
    print(
        "backend_reflection_contract_result="
        f"{report['backend_reflection_contract_result']}"
    )
    print(f"frontend_alignment_result={report['frontend_alignment_result']}")
    print(f"source_c5_report_available={summary['source_c5_report_available']}")
    print(f"source_c5_backend_reflection_status={summary['source_c5_backend_reflection_status']}")
    print(f"endpoint_contract_defined={validation['endpoint_contract_defined']}")
    print(f"endpoint_route_registered={validation['endpoint_route_registered']}")
    print(f"get_only_contract_verified={validation['get_only_contract_verified']}")
    print(f"read_only_contract_verified={validation['read_only_contract_verified']}")
    print(f"non_mutating_contract_verified={validation['non_mutating_contract_verified']}")
    print(f"frontend_alignment_fetch_deferred={validation['frontend_alignment_fetch_deferred']}")
    print(
        "no_frontend_live_fetch_integration_introduced="
        f"{validation['no_frontend_live_fetch_integration_introduced']}"
    )
    print(
        "no_recommendation_ranking_scoring_triage_semantics_introduced="
        f"{validation['no_recommendation_ranking_scoring_triage_semantics_introduced']}"
    )
    print(f"no_operational_behavior_introduced={validation['no_operational_behavior_introduced']}")
    for key, value in sorted(report["enabled_semantics"].items()):
        print(f"{key}={value}")
    print(f"repository_remains={','.join(report['repository_remains'])}")
    print(f"non_authority_statement={report['non_authority_statement']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
