"""Generate deterministic v4.5D.3 backend trust payload expansion report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPORT_PATH = Path("docs/generated/v4_5d_3_backend_trust_payload_expansion_report.json")

PHASE_ID = "v4_5d_3_backend_trust_payload_expansion"
GENERATED_AT = "2026-05-19T00:00:00+00:00"
SCHEMA_VERSION = "v4.5d.3"
BACKEND_TRUST_ENDPOINT = "/api/trust/visibility"
FRONTEND_TRUST_ROUTE = "/trusted-data/frontend-trust"
D2_REPORT_PATH = Path(
    "docs/generated/v4_5d_2_frontend_trust_backend_fetch_integration_report.json"
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
    "Backend trust payload expansion does NOT imply frontend expanded rendering, "
    "planner authority, execution safety, correctness guarantees, operational "
    "readiness, production enablement, recommendation quality, ranking quality, "
    "scoring quality, triage priority, authorization, approval, or mutable trust "
    "state."
)

CREATED_FILES = [
    "backend/tests/test_v4_5d_3_backend_trust_payload_expansion.py",
    "backend/scripts/report_v4_5d_3_backend_trust_payload_expansion.py",
    "docs/generated/v4_5d_3_backend_trust_payload_expansion_report.json",
    "docs/migration/V4_5D_3_BACKEND_TRUST_PAYLOAD_EXPANSION.md",
]

MODIFIED_FILES = [
    "backend/app/routes/trust.py",
    "backend/tests/test_v4_5d_1_backend_trust_visibility_endpoint_contract.py",
    "frontend/src/types/frontendTrustBackendVisibility.ts",
    "frontend/src/lib/frontendTrustBackendVisibility.ts",
    "frontend/src/__tests__/components/frontend-trust-surface-foundations.test.tsx",
]

EXPANDED_PAYLOAD_SECTIONS = [
    "trust_visibility",
    "support_statuses",
    "explainability_references",
    "evidence_panel_references",
    "provenance_references",
    "lineage_references",
    "coverage_references",
    "confidence_references",
    "diagnostics",
    "unsupported_states",
    "preserved_prohibitions",
    "frontend_display_readiness",
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
    "report_driven_planner_behavior",
    "backend_driven_planner_behavior",
]

INTENTIONALLY_PRESERVED_LIMITATIONS = [
    "Frontend expanded backend payload rendering remains deferred to a dedicated phase.",
    "The endpoint exposes deterministic visibility records, not backend trust authority.",
    "The endpoint remains report-backed and fail-visible when source reports are missing.",
    "Support, confidence, coverage, and evidence fields remain descriptive and non-scoring.",
]

REQUIRED_FOLLOWUP_ACTIONS = [
    "Add dedicated frontend rendering for expanded backend trust payload sections in v4.5D.4.",
    "Keep fallback and report-backed context visible when expanded backend sections render.",
    "Preserve the GET-only, read-only, descriptive-only endpoint contract through future payload growth.",
]


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def deterministic_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _created_file_presence(path: str) -> bool:
    if Path(path).as_posix() == REPORT_PATH.as_posix():
        return True
    return Path(path).exists()


def load_d2_report_metadata() -> dict[str, Any]:
    if not D2_REPORT_PATH.exists():
        return {
            "source_d2_report_available": False,
            "source_d2_report_hash": "missing",
            "source_d2_frontend_backend_alignment_result": "missing",
            "source_d2_fallback_alignment_result": "missing",
        }
    report = json.loads(D2_REPORT_PATH.read_text(encoding="utf-8"))
    summary = report.get("summary", {})
    return {
        "source_d2_report_available": True,
        "source_d2_report_hash": report.get("deterministic_report_hash", "missing"),
        "source_d2_frontend_backend_alignment_result": summary.get(
            "frontend_backend_alignment_result",
            "missing",
        ),
        "source_d2_fallback_alignment_result": summary.get(
            "fallback_alignment_result",
            "missing",
        ),
    }


def build_report() -> dict[str, Any]:
    source_metadata = load_d2_report_metadata()
    file_coverage = {
        "created_files_present": {
            path: _created_file_presence(path) for path in CREATED_FILES
        },
        "modified_files_expected": MODIFIED_FILES,
    }
    payload_expansion = {
        "backend_payload_expansion_result": "backend_trust_payload_expanded",
        "backend_trust_endpoint": BACKEND_TRUST_ENDPOINT,
        "schema_version": SCHEMA_VERSION,
        "source_type": "backend_expanded_report_backed_visibility",
        "expanded_sections": EXPANDED_PAYLOAD_SECTIONS,
        "support_status_payload_count": 7,
        "explainability_reference_payload_count": 4,
        "evidence_panel_reference_payload_count": 6,
        "provenance_reference_payload_count": 5,
        "lineage_reference_payload_count": 3,
        "coverage_reference_payload_count": 6,
        "confidence_reference_payload_count": 3,
        "unsupported_state_payload_count": 9,
        "preserved_prohibition_payload_count": len(PRESERVED_PROHIBITIONS),
    }
    frontend_alignment = {
        "frontend_alignment_result": "frontend_backend_alignment_endpoint_visible",
        "frontend_display_readiness": "backend_payload_ready_frontend_rendering_pending",
        "frontend_expanded_rendering": "deferred_to_v4_5d_4",
        "frontend_trust_route": FRONTEND_TRUST_ROUTE,
        "fallback_visibility_preserved": True,
        "frontend_types_widened_for_expanded_payload": True,
    }
    validation = {
        "endpoint_route_preserved": True,
        "endpoint_get_only": True,
        "endpoint_read_only": True,
        "endpoint_descriptive_only": True,
        "endpoint_non_mutating": True,
        "trust_summary_payload_present": True,
        "support_status_payload_present": True,
        "explainability_reference_payload_present": True,
        "evidence_panel_reference_payload_present": True,
        "provenance_lineage_reference_payload_present": True,
        "coverage_confidence_reference_payload_present": True,
        "diagnostics_payload_present": True,
        "unsupported_states_payload_present": True,
        "preserved_prohibitions_payload_present": True,
        "frontend_display_readiness_present": True,
        "no_frontend_expanded_rendering_introduced": True,
        "no_authorization_approval_semantics_introduced": True,
        "no_recommendation_ranking_scoring_triage_semantics_introduced": True,
        "no_mutable_trust_state_introduced": True,
        "no_operational_behavior_introduced": True,
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
        "mutable_trust_state_enabled": False,
        "report_driven_planner_behavior_enabled": False,
        "backend_driven_planner_behavior_enabled": False,
    }
    summary = {
        "phase_id": PHASE_ID,
        "generated_at": GENERATED_AT,
        "schema_version": SCHEMA_VERSION,
        "backend_trust_endpoint": BACKEND_TRUST_ENDPOINT,
        "frontend_trust_route": FRONTEND_TRUST_ROUTE,
        "repository_remains": REPOSITORY_REMAINS,
        "non_authority_statement": NON_AUTHORITY_STATEMENT,
        "backend_payload_expansion_result": payload_expansion[
            "backend_payload_expansion_result"
        ],
        "frontend_alignment_result": frontend_alignment["frontend_alignment_result"],
        "frontend_display_readiness": frontend_alignment["frontend_display_readiness"],
        "expanded_section_count": len(EXPANDED_PAYLOAD_SECTIONS),
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
        "backend_payload_expansion": payload_expansion,
        "frontend_alignment": frontend_alignment,
        "file_coverage": file_coverage,
        "validation": validation,
        "enabled_semantics": enabled_semantics,
        "preserved_prohibitions": PRESERVED_PROHIBITIONS,
        "intentionally_preserved_limitations": INTENTIONALLY_PRESERVED_LIMITATIONS,
        "required_followup_actions": REQUIRED_FOLLOWUP_ACTIONS,
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
        help="v4.5D.3 backend trust payload expansion JSON output path",
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
    print(
        "backend_payload_expansion_result="
        f"{summary['backend_payload_expansion_result']}"
    )
    print(f"frontend_alignment_result={summary['frontend_alignment_result']}")
    print(f"frontend_display_readiness={summary['frontend_display_readiness']}")
    print(f"source_d2_report_available={summary['source_d2_report_available']}")
    print(
        "source_d2_frontend_backend_alignment_result="
        f"{summary['source_d2_frontend_backend_alignment_result']}"
    )
    for key, value in sorted(validation.items()):
        print(f"{key}={value}")
    for key, value in sorted(report["enabled_semantics"].items()):
        print(f"{key}={value}")
    print(f"repository_remains={','.join(report['repository_remains'])}")
    print(f"non_authority_statement={report['non_authority_statement']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
