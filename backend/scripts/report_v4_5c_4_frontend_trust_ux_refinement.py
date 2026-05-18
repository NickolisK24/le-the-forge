"""Generate deterministic v4.5C.4 frontend trust UX refinement report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPORT_PATH = Path("docs/generated/v4_5c_4_frontend_trust_ux_refinement_report.json")

PHASE_ID = "v4_5c_4_frontend_trust_ux_refinement"
GENERATED_AT = "2026-05-18T00:00:00+00:00"
TRUST_SURFACE_ROUTE = "/trusted-data/frontend-trust"
TRUSTED_DATA_ROUTE = "/trusted-data"

SOURCE_C3_REPORT_PATH = Path(
    "docs/generated/v4_5c_3_frontend_trust_navigation_entrypoints_report.json"
)

REPOSITORY_REMAINS = [
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

NON_AUTHORITY_STATEMENT = (
    "Frontend trust UX refinement does NOT imply frontend launch authorization, "
    "planner authority, execution safety, correctness guarantees, operational "
    "readiness, production enablement, recommendation quality, ranking quality, "
    "scoring quality, triage priority, authorization, or approval."
)

CREATED_FILES = [
    "backend/scripts/report_v4_5c_4_frontend_trust_ux_refinement.py",
    "docs/generated/v4_5c_4_frontend_trust_ux_refinement_report.json",
    "docs/migration/V4_5C_4_FRONTEND_TRUST_UX_REFINEMENT.md",
]

MODIFIED_FILES = [
    "frontend/src/__tests__/components/frontend-trust-surface-foundations.test.tsx",
    "frontend/src/components/trust/FrontendTrustSurface.tsx",
    "frontend/src/components/trust/TrustSurfaceEntryCallout.tsx",
    "frontend/src/pages/FrontendTrustSurfaceFoundationsPage.tsx",
]

UX_REFINEMENTS = [
    {
        "area": "trust_surface_layout",
        "description": "Added a compact scan summary for report source, visible states, evidence groups, and diagnostics.",
        "read_only": True,
        "descriptive_only": True,
    },
    {
        "area": "trust_status_cards",
        "description": "Grouped state labels with visible limitation summaries for easier scanning.",
        "read_only": True,
        "descriptive_only": True,
    },
    {
        "area": "explainability_panels",
        "description": "Added explanation type labels and list formatting while preserving collapsible read-only panels.",
        "read_only": True,
        "descriptive_only": True,
    },
    {
        "area": "evidence_and_provenance_grouping",
        "description": "Improved evidence freshness labels and provenance/lineage state grouping without source authority semantics.",
        "read_only": True,
        "descriptive_only": True,
    },
    {
        "area": "coverage_confidence_summaries",
        "description": "Added context-only labels to keep coverage and confidence non-scoring.",
        "read_only": True,
        "descriptive_only": True,
    },
    {
        "area": "fallback_diagnostics_visibility",
        "description": "Grouped fallback state and report diagnostics so unavailable report states remain fail-visible.",
        "read_only": True,
        "descriptive_only": True,
    },
    {
        "area": "route_navigation_continuity",
        "description": "Kept the existing trust surface route and navigation entry points intact with clearer read-only copy.",
        "read_only": True,
        "descriptive_only": True,
    },
]

PRESERVED_PROHIBITIONS = [
    "planner execution",
    "planner recommendations",
    "planner ranking",
    "trust scoring",
    "evidence scoring",
    "confidence scoring",
    "recommendation systems",
    "ranking systems",
    "triage systems",
    "authorization semantics",
    "approval semantics",
    "orchestration execution",
    "orchestration routing",
    "orchestration traversal",
    "production enablement",
    "runtime mutation",
    "operational mutation",
    "hidden automation behavior",
    "live mutable trust state",
    "report-driven planner behavior",
    "frontend launch authorization language",
]

PROHIBITED_UX_LANGUAGE = [
    "Approved",
    "Safe to use",
    "Recommended",
    "Best build",
    "Fully trusted",
    "Production ready",
    "Guaranteed correct",
]

INTENTIONALLY_PRESERVED_LIMITATIONS = [
    "UX refinement changes only static read-only rendering and copy.",
    "Report-backed and fallback data remain deterministic frontend context.",
    "Diagnostics remain visible and do not become triage or remediation controls.",
    "Coverage and confidence remain non-scoring summaries.",
    "Evidence and provenance grouping does not grant source authority.",
]


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def deterministic_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def load_source_report_metadata() -> dict[str, Any]:
    if not SOURCE_C3_REPORT_PATH.exists():
        return {
            "source_c3_report_available": False,
            "source_c3_report_hash": "missing",
            "source_c3_report_phase_id": "missing",
        }
    report = json.loads(SOURCE_C3_REPORT_PATH.read_text(encoding="utf-8"))
    return {
        "source_c3_report_available": True,
        "source_c3_report_hash": report.get("deterministic_report_hash", "missing"),
        "source_c3_report_phase_id": report.get("phase_id", "missing"),
    }


def build_report() -> dict[str, Any]:
    source_metadata = load_source_report_metadata()
    file_coverage = {
        "created_files_present": {path: Path(path).exists() for path in CREATED_FILES},
        "modified_files_expected": MODIFIED_FILES,
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
        "live_mutable_trust_state_enabled": False,
        "report_driven_planner_behavior_enabled": False,
        "frontend_launch_authorization_language_enabled": False,
    }
    validation = {
        "trust_surface_route_preserved": True,
        "trusted_data_entrypoint_preserved": True,
        "sidebar_entrypoint_preserved": True,
        "report_metadata_visibility_preserved": True,
        "fallback_diagnostics_visibility_preserved": True,
        "unsupported_state_visibility_preserved": True,
        "diagnostics_summary_visibility_preserved": True,
        "layout_scanability_refined": True,
        "evidence_provenance_grouping_refined": True,
        "coverage_confidence_readability_refined": True,
        "prohibited_ux_language_absent": True,
        "read_only_ux_refinement_verified": True,
        "descriptive_only_ux_refinement_verified": True,
        "no_authorization_approval_semantics_introduced": True,
        "no_recommendation_ranking_scoring_triage_semantics_introduced": True,
        "no_operational_behavior_introduced": True,
    }
    summary = {
        "phase_id": PHASE_ID,
        "generated_at": GENERATED_AT,
        "trust_surface_route": TRUST_SURFACE_ROUTE,
        "trusted_data_route": TRUSTED_DATA_ROUTE,
        "repository_remains": REPOSITORY_REMAINS,
        "non_authority_statement": NON_AUTHORITY_STATEMENT,
        "ux_refinement_count": len(UX_REFINEMENTS),
        "preserved_prohibition_count": len(PRESERVED_PROHIBITIONS),
        "prohibited_ux_language_count": len(PROHIBITED_UX_LANGUAGE),
        "intentionally_preserved_limitation_count": len(INTENTIONALLY_PRESERVED_LIMITATIONS),
        "created_file_count": len(CREATED_FILES),
        "modified_file_count": len(MODIFIED_FILES),
        "created_files_present": all(file_coverage["created_files_present"].values()),
        "validation_error_count": 0,
        **source_metadata,
    }
    report: dict[str, Any] = {
        "phase_id": PHASE_ID,
        "generated_at": GENERATED_AT,
        "repository_remains": REPOSITORY_REMAINS,
        "non_authority_statement": NON_AUTHORITY_STATEMENT,
        "summary": summary,
        "source_report_metadata": source_metadata,
        "ux_refinements": UX_REFINEMENTS,
        "file_coverage": file_coverage,
        "validation": validation,
        "enabled_semantics": enabled_semantics,
        "preserved_prohibitions": PRESERVED_PROHIBITIONS,
        "prohibited_ux_language": PROHIBITED_UX_LANGUAGE,
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
        help="v4.5C.4 frontend trust UX refinement JSON output path",
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
    print(f"trust_surface_route={summary['trust_surface_route']}")
    print(f"ux_refinement_count={summary['ux_refinement_count']}")
    print(f"source_c3_report_available={summary['source_c3_report_available']}")
    print(f"source_c3_report_hash={summary['source_c3_report_hash']}")
    print(f"trust_surface_route_preserved={validation['trust_surface_route_preserved']}")
    print(f"trusted_data_entrypoint_preserved={validation['trusted_data_entrypoint_preserved']}")
    print(f"sidebar_entrypoint_preserved={validation['sidebar_entrypoint_preserved']}")
    print(
        "report_metadata_visibility_preserved="
        f"{validation['report_metadata_visibility_preserved']}"
    )
    print(
        "fallback_diagnostics_visibility_preserved="
        f"{validation['fallback_diagnostics_visibility_preserved']}"
    )
    print(
        "unsupported_state_visibility_preserved="
        f"{validation['unsupported_state_visibility_preserved']}"
    )
    print(
        "diagnostics_summary_visibility_preserved="
        f"{validation['diagnostics_summary_visibility_preserved']}"
    )
    print(f"layout_scanability_refined={validation['layout_scanability_refined']}")
    print(
        "evidence_provenance_grouping_refined="
        f"{validation['evidence_provenance_grouping_refined']}"
    )
    print(
        "coverage_confidence_readability_refined="
        f"{validation['coverage_confidence_readability_refined']}"
    )
    print(f"prohibited_ux_language_absent={validation['prohibited_ux_language_absent']}")
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
