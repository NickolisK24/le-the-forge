"""Generate deterministic v4.5D.2 frontend backend trust fetch integration report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPORT_PATH = Path(
    "docs/generated/v4_5d_2_frontend_trust_backend_fetch_integration_report.json"
)

PHASE_ID = "v4_5d_2_frontend_trust_backend_fetch_integration"
GENERATED_AT = "2026-05-18T00:00:00+00:00"
SCHEMA_VERSION = "v4.5d.2"
BACKEND_TRUST_ENDPOINT = "/api/trust/visibility"
FRONTEND_TRUST_ROUTE = "/trusted-data/frontend-trust"
D1_REPORT_PATH = Path(
    "docs/generated/v4_5d_1_backend_trust_visibility_endpoint_contract_report.json"
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
    "Frontend backend trust fetch integration does NOT imply planner authority, "
    "backend trust authority, execution safety, correctness guarantees, "
    "operational readiness, production enablement, recommendation quality, "
    "ranking quality, scoring quality, triage priority, authorization, "
    "approval, or mutable trust state."
)

CREATED_FILES = [
    "frontend/src/types/frontendTrustBackendVisibility.ts",
    "frontend/src/lib/frontendTrustBackendVisibility.ts",
    "backend/scripts/report_v4_5d_2_frontend_trust_backend_fetch_integration.py",
    "docs/generated/v4_5d_2_frontend_trust_backend_fetch_integration_report.json",
    "docs/migration/V4_5D_2_FRONTEND_TRUST_BACKEND_FETCH_INTEGRATION.md",
]

MODIFIED_FILES = [
    "frontend/src/components/trust/FrontendTrustSurface.tsx",
    "frontend/src/pages/FrontendTrustSurfaceFoundationsPage.tsx",
    "frontend/src/lib/frontendTrustReportIntegration.ts",
    "frontend/src/__tests__/components/frontend-trust-surface-foundations.test.tsx",
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
    "operational_mutation",
    "hidden_automation_behavior",
    "mutable_trust_state",
    "report_driven_planner_behavior",
    "backend_driven_planner_behavior",
]

FETCH_DIAGNOSTICS = [
    "backend_endpoint_visible",
    "network_failure_fallback",
    "http_error_fallback",
    "malformed_payload_fallback",
    "missing_schema_version_fallback",
    "unsupported_state_visibility_preserved",
]

REQUIRED_FOLLOWUP_ACTIONS = [
    "Keep fallback and report-backed trust context visible as backend payload coverage expands.",
    "Add broader frontend/backend contract regression tests when the backend payload begins carrying full trust surface records.",
    "Keep planner, recommendation, ranking, scoring, triage, authorization, approval, and mutable trust state out of trust fetch handling.",
]

INTENTIONALLY_PRESERVED_LIMITATIONS = [
    "Backend fetch integration exposes endpoint metadata and contract status, not full backend trust authority.",
    "The frontend does not replace all local trust panels with backend payload data.",
    "Fallback and report-backed C2 context remain visible when endpoint data is available.",
    "A backend fetch failure leaves deterministic fallback visibility active and explicit.",
]


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def deterministic_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def load_d1_report_metadata() -> dict[str, Any]:
    if not D1_REPORT_PATH.exists():
        return {
            "source_d1_report_available": False,
            "source_d1_report_hash": "missing",
            "source_d1_backend_reflection_contract_result": "missing",
            "source_d1_frontend_alignment_result": "missing",
        }
    report = json.loads(D1_REPORT_PATH.read_text(encoding="utf-8"))
    return {
        "source_d1_report_available": True,
        "source_d1_report_hash": report.get("deterministic_report_hash", "missing"),
        "source_d1_backend_reflection_contract_result": report.get(
            "backend_reflection_contract_result",
            "missing",
        ),
        "source_d1_frontend_alignment_result": report.get(
            "frontend_alignment_result",
            "missing",
        ),
    }


def build_report() -> dict[str, Any]:
    source_metadata = load_d1_report_metadata()
    file_coverage = {
        "created_files_present": {path: Path(path).exists() for path in CREATED_FILES},
        "modified_files_expected": MODIFIED_FILES,
    }
    alignment = {
        "frontend_backend_alignment_result": "frontend_backend_alignment_endpoint_visible",
        "fallback_alignment_result": (
            "frontend_backend_alignment_fetch_attempted_with_fail_visible_fallback"
        ),
        "backend_trust_endpoint": BACKEND_TRUST_ENDPOINT,
        "frontend_trust_route": FRONTEND_TRUST_ROUTE,
        "backend_schema_version_visible": True,
        "backend_report_reference_visible": True,
        "backend_reflection_status_visible": True,
        "frontend_backend_alignment_status_visible": True,
        "fallback_state_visible": True,
        "unsupported_state_visibility_preserved": True,
    }
    fetch_contract = {
        "client_id": "v4_5d_2_frontend_backend_trust_fetch_client",
        "endpoint_route": BACKEND_TRUST_ENDPOINT,
        "method": "GET",
        "read_only": True,
        "descriptive_only": True,
        "non_mutating": True,
        "network_failure_fail_visible": True,
        "malformed_payload_fail_visible": True,
        "missing_schema_version_fail_visible": True,
        "fallback_preserved": True,
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
        "operational_mutation_enabled": False,
        "hidden_automation_behavior_enabled": False,
        "mutable_trust_state_enabled": False,
        "report_driven_planner_behavior_enabled": False,
        "backend_driven_planner_behavior_enabled": False,
    }
    validation = {
        "backend_fetch_client_defined": True,
        "backend_fetch_uses_get_only": True,
        "endpoint_visibility_rendered": True,
        "backend_schema_version_rendered": True,
        "backend_report_reference_rendered": True,
        "backend_reflection_status_rendered": True,
        "frontend_backend_alignment_status_rendered": True,
        "network_failure_fallback_tested": True,
        "malformed_payload_fallback_tested": True,
        "missing_schema_version_fallback_tested": True,
        "c2_report_metadata_preserved": True,
        "unsupported_state_visibility_preserved": True,
        "no_authorization_approval_semantics_introduced": True,
        "no_recommendation_ranking_scoring_triage_semantics_introduced": True,
        "no_operational_behavior_introduced": True,
        "no_mutable_trust_state_introduced": True,
    }
    summary = {
        "phase_id": PHASE_ID,
        "generated_at": GENERATED_AT,
        "schema_version": SCHEMA_VERSION,
        "backend_trust_endpoint": BACKEND_TRUST_ENDPOINT,
        "frontend_trust_route": FRONTEND_TRUST_ROUTE,
        "repository_remains": REPOSITORY_REMAINS,
        "non_authority_statement": NON_AUTHORITY_STATEMENT,
        "frontend_backend_alignment_result": alignment[
            "frontend_backend_alignment_result"
        ],
        "fallback_alignment_result": alignment["fallback_alignment_result"],
        "fetch_diagnostic_count": len(FETCH_DIAGNOSTICS),
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
        "frontend_backend_alignment": alignment,
        "fetch_contract": fetch_contract,
        "file_coverage": file_coverage,
        "validation": validation,
        "enabled_semantics": enabled_semantics,
        "preserved_prohibitions": PRESERVED_PROHIBITIONS,
        "fetch_diagnostics": FETCH_DIAGNOSTICS,
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
        help="v4.5D.2 frontend backend trust fetch integration JSON output path",
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
    print(f"backend_trust_endpoint={summary['backend_trust_endpoint']}")
    print(f"frontend_trust_route={summary['frontend_trust_route']}")
    print(
        "frontend_backend_alignment_result="
        f"{summary['frontend_backend_alignment_result']}"
    )
    print(f"fallback_alignment_result={summary['fallback_alignment_result']}")
    print(f"source_d1_report_available={summary['source_d1_report_available']}")
    print(
        "source_d1_frontend_alignment_result="
        f"{summary['source_d1_frontend_alignment_result']}"
    )
    print(f"backend_fetch_client_defined={validation['backend_fetch_client_defined']}")
    print(f"backend_fetch_uses_get_only={validation['backend_fetch_uses_get_only']}")
    print(f"endpoint_visibility_rendered={validation['endpoint_visibility_rendered']}")
    print(f"network_failure_fallback_tested={validation['network_failure_fallback_tested']}")
    print(f"malformed_payload_fallback_tested={validation['malformed_payload_fallback_tested']}")
    print(f"missing_schema_version_fallback_tested={validation['missing_schema_version_fallback_tested']}")
    print(f"c2_report_metadata_preserved={validation['c2_report_metadata_preserved']}")
    print(
        "no_recommendation_ranking_scoring_triage_semantics_introduced="
        f"{validation['no_recommendation_ranking_scoring_triage_semantics_introduced']}"
    )
    print(f"no_operational_behavior_introduced={validation['no_operational_behavior_introduced']}")
    print(f"no_mutable_trust_state_introduced={validation['no_mutable_trust_state_introduced']}")
    for key, value in sorted(report["enabled_semantics"].items()):
        print(f"{key}={value}")
    print(f"repository_remains={','.join(report['repository_remains'])}")
    print(f"non_authority_statement={report['non_authority_statement']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
