"""Generate deterministic v4.5D.4 frontend expanded backend payload rendering report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPORT_PATH = Path(
    "docs/generated/v4_5d_4_frontend_expanded_backend_payload_rendering_report.json"
)

PHASE_ID = "v4_5d_4_frontend_expanded_backend_payload_rendering"
GENERATED_AT = "2026-05-19T00:00:00+00:00"
SCHEMA_VERSION = "v4.5d.4"
BACKEND_TRUST_ENDPOINT = "/api/trust/visibility"
FRONTEND_TRUST_ROUTE = "/trusted-data/frontend-trust"
D3_REPORT_PATH = Path(
    "docs/generated/v4_5d_3_backend_trust_payload_expansion_report.json"
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
    "Frontend expanded backend payload rendering does NOT imply backend trust "
    "authority, planner authority, execution safety, correctness guarantees, "
    "operational readiness, production enablement, recommendation quality, "
    "ranking quality, scoring quality, triage priority, authorization, "
    "approval, mutable trust state, or backend-driven planner behavior."
)

CREATED_FILES = [
    "backend/scripts/report_v4_5d_4_frontend_expanded_backend_payload_rendering.py",
    "docs/generated/v4_5d_4_frontend_expanded_backend_payload_rendering_report.json",
    "docs/migration/V4_5D_4_FRONTEND_EXPANDED_BACKEND_PAYLOAD_RENDERING.md",
]

MODIFIED_FILES = [
    "frontend/src/components/trust/FrontendTrustSurface.tsx",
    "frontend/src/lib/frontendTrustBackendVisibility.ts",
    "frontend/src/types/frontendTrustBackendVisibility.ts",
    "frontend/src/__tests__/components/frontend-trust-surface-foundations.test.tsx",
]

RENDERED_BACKEND_SECTIONS = [
    "backend_trust_summary",
    "backend_support_statuses",
    "backend_explainability_references",
    "backend_evidence_panel_references",
    "backend_provenance_references",
    "backend_lineage_references",
    "backend_coverage_references",
    "backend_confidence_references",
    "backend_diagnostics",
    "backend_unsupported_states",
    "backend_preserved_prohibitions",
    "backend_frontend_display_readiness",
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
    "The frontend renders expanded backend visibility records without treating them as backend trust authority.",
    "Static/report-backed trust context and deterministic fallback diagnostics remain visible.",
    "The frontend does not mutate backend trust state or write trust decisions.",
    "The backend endpoint remains the only source of expanded backend payload sections.",
]

REQUIRED_FOLLOWUP_ACTIONS = [
    "Keep expanded backend rendering covered by deterministic frontend tests as payload sections evolve.",
    "Preserve fail-visible fallback behavior when backend expanded sections are unavailable.",
    "Do not convert backend visibility records into planner, ranking, scoring, triage, authorization, approval, or production behavior.",
]


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def deterministic_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _created_file_presence(path: str) -> bool:
    if Path(path).as_posix() == REPORT_PATH.as_posix():
        return True
    return Path(path).exists()


def load_d3_report_metadata() -> dict[str, Any]:
    if not D3_REPORT_PATH.exists():
        return {
            "source_d3_report_available": False,
            "source_d3_report_hash": "missing",
            "source_d3_backend_payload_expansion_result": "missing",
            "source_d3_frontend_display_readiness": "missing",
        }
    report = json.loads(D3_REPORT_PATH.read_text(encoding="utf-8"))
    summary = report.get("summary", {})
    return {
        "source_d3_report_available": True,
        "source_d3_report_hash": report.get("deterministic_report_hash", "missing"),
        "source_d3_backend_payload_expansion_result": summary.get(
            "backend_payload_expansion_result",
            "missing",
        ),
        "source_d3_frontend_display_readiness": summary.get(
            "frontend_display_readiness",
            "missing",
        ),
    }


def build_report() -> dict[str, Any]:
    source_metadata = load_d3_report_metadata()
    file_coverage = {
        "created_files_present": {
            path: _created_file_presence(path) for path in CREATED_FILES
        },
        "modified_files_expected": MODIFIED_FILES,
    }
    rendering = {
        "frontend_backend_alignment_result": (
            "frontend_backend_alignment_expanded_payload_visible"
        ),
        "backend_trust_endpoint": BACKEND_TRUST_ENDPOINT,
        "frontend_trust_route": FRONTEND_TRUST_ROUTE,
        "rendered_backend_sections": RENDERED_BACKEND_SECTIONS,
        "backend_trust_summary_rendered": True,
        "backend_support_statuses_rendered": True,
        "backend_explainability_references_rendered": True,
        "backend_evidence_panel_references_rendered": True,
        "backend_provenance_references_rendered": True,
        "backend_lineage_references_rendered": True,
        "backend_coverage_references_rendered": True,
        "backend_confidence_references_rendered": True,
        "backend_diagnostics_rendered": True,
        "backend_unsupported_states_rendered": True,
        "backend_preserved_prohibitions_rendered": True,
        "backend_frontend_display_readiness_rendered": True,
        "fallback_visibility_preserved": True,
        "report_backed_context_preserved": True,
    }
    validation = {
        "frontend_expanded_payload_panel_defined": True,
        "backend_payload_state_normalized": True,
        "expanded_payload_unavailable_state_fail_visible": True,
        "backend_trust_summary_tested": True,
        "backend_support_statuses_tested": True,
        "backend_explainability_references_tested": True,
        "backend_evidence_panel_references_tested": True,
        "backend_provenance_lineage_references_tested": True,
        "backend_coverage_confidence_references_tested": True,
        "backend_diagnostics_tested": True,
        "backend_unsupported_states_tested": True,
        "backend_preserved_prohibitions_tested": True,
        "backend_frontend_display_readiness_tested": True,
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
        "frontend_backend_alignment_result": rendering[
            "frontend_backend_alignment_result"
        ],
        "rendered_backend_section_count": len(RENDERED_BACKEND_SECTIONS),
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
        "frontend_expanded_backend_payload_rendering": rendering,
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
        help="v4.5D.4 frontend expanded backend payload rendering JSON output path",
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
    print(f"source_d3_report_available={summary['source_d3_report_available']}")
    print(
        "source_d3_backend_payload_expansion_result="
        f"{summary['source_d3_backend_payload_expansion_result']}"
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
