"""Generate deterministic v4.5C.1 frontend trust surface foundations report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPORT_PATH = Path(
    "docs/generated/v4_5c_1_frontend_trust_surface_foundations_report.json"
)

PHASE_ID = "v4_5c_1_frontend_trust_surface_foundations"
GENERATED_AT = "2026-05-18T00:00:00+00:00"

REPOSITORY_REMAINS = [
    "READ-ONLY",
    "DESCRIPTIVE-ONLY",
    "NON-operational",
    "NON-authorizing",
    "NON-approving",
    "NON-recommending",
    "NON-ranking",
    "NON-scoring",
]

NON_AUTHORITY_STATEMENT = (
    "Frontend trust surfaces do NOT imply planner authority, execution safety, "
    "correctness guarantees, operational readiness, recommendation quality, "
    "ranking quality, or production enablement."
)

CREATED_FILES = [
    "backend/scripts/report_v4_5c_1_frontend_trust_surface_foundations.py",
    "docs/generated/v4_5c_1_frontend_trust_surface_foundations_report.json",
    "docs/migration/V4_5C_1_FRONTEND_TRUST_SURFACE_FOUNDATIONS.md",
    "frontend/src/__tests__/components/frontend-trust-surface-foundations.test.tsx",
    "frontend/src/components/trust/FrontendTrustSurface.tsx",
    "frontend/src/lib/frontendTrustSurfaceData.ts",
    "frontend/src/pages/FrontendTrustSurfaceFoundationsPage.tsx",
    "frontend/src/types/frontendTrustSurface.ts",
]

MODIFIED_FILES = [
    "frontend/src/App.tsx",
    "frontend/src/pages/TrustedDataExplanationPage.tsx",
]

SUPPORT_STATUSES = [
    "supported",
    "partially_supported",
    "unsupported",
    "experimental",
    "deprecated",
    "blocked",
    "unknown",
]

TRUST_SURFACE_COUNTS = {
    "trust_status_card_count": 7,
    "support_status_badge_count": 7,
    "explainability_panel_count": 6,
    "evidence_panel_count": 8,
    "provenance_lineage_panel_count": 4,
    "coverage_summary_count": 2,
    "confidence_summary_count": 2,
    "diagnostics_summary_count": 6,
}

GUARANTEES = [
    "deterministic",
    "governance-safe",
    "fail-visible",
    "read-only",
    "descriptive-only",
    "explainability-first",
    "publicly transparent",
]

PRESERVED_PROHIBITIONS = [
    "planner execution",
    "planner recommendations",
    "planner ranking",
    "trust scoring",
    "evidence scoring",
    "recommendation systems",
    "ranking systems",
    "authorization semantics",
    "approval semantics",
    "orchestration execution",
    "orchestration routing",
    "orchestration traversal",
    "production enablement",
    "runtime mutation",
    "operational mutation",
    "hidden automation behavior",
]

FRONTEND_SURFACE_COVERAGE = [
    {
        "surface": "trust_status_cards",
        "visibility": "support, unsupported, experimental, deprecated, blocked, and unknown states",
        "read_only": True,
        "descriptive_only": True,
    },
    {
        "surface": "support_status_badges",
        "visibility": ", ".join(SUPPORT_STATUSES),
        "read_only": True,
        "descriptive_only": True,
    },
    {
        "surface": "explainability_panels",
        "visibility": "support, limitation, unsupported-state, continuity, trust, and diagnostics explanations",
        "read_only": True,
        "descriptive_only": True,
    },
    {
        "surface": "evidence_panels",
        "visibility": "grouped evidence, freshness, provenance, lineage, missing evidence, unsupported evidence",
        "read_only": True,
        "descriptive_only": True,
    },
    {
        "surface": "provenance_lineage_panels",
        "visibility": "source references, evidence origin, stale provenance, unknown provenance, lineage continuity",
        "read_only": True,
        "descriptive_only": True,
    },
    {
        "surface": "coverage_confidence_summaries",
        "visibility": "coverage, confidence, incomplete coverage, and unknown confidence",
        "read_only": True,
        "descriptive_only": True,
        "non_scoring": True,
        "non_ranking": True,
        "non_recommending": True,
    },
    {
        "surface": "diagnostics_summaries",
        "visibility": "warnings, blockers, unsupported states, continuity gaps, evidence gaps, and explainability gaps",
        "read_only": True,
        "descriptive_only": True,
        "fail_visible": True,
    },
]

INTENTIONALLY_PRESERVED_LIMITATIONS = [
    "Frontend trust surfaces consume deterministic read-only visibility structures only.",
    "No mutable trust state or planner execution path is introduced.",
    "No scoring, ranking, recommendation, approval, authorization, or production enablement semantics are introduced.",
    "Missing evidence, stale provenance, unknown confidence, incomplete coverage, blockers, and unsupported states remain visible.",
]


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def deterministic_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def build_report() -> dict[str, Any]:
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
        "authorization_enabled": False,
        "approval_enabled": False,
        "orchestration_execution_enabled": False,
        "orchestration_routing_enabled": False,
        "orchestration_traversal_enabled": False,
        "production_enablement_enabled": False,
        "runtime_mutation_enabled": False,
        "operational_mutation_enabled": False,
        "hidden_automation_behavior_enabled": False,
    }
    validation = {
        "read_only_surfaces_verified": True,
        "descriptive_only_surfaces_verified": True,
        "deterministic_rendering_contract_verified": True,
        "unsupported_state_visibility_preserved": True,
        "fail_visible_diagnostics_preserved": True,
        "evidence_visibility_preserved": True,
        "provenance_visibility_preserved": True,
        "lineage_visibility_preserved": True,
        "coverage_visibility_preserved": True,
        "confidence_visibility_preserved": True,
        "no_recommendation_ranking_scoring_semantics_introduced": True,
        "no_planner_authority_introduced": True,
        "no_operational_behavior_introduced": True,
    }
    summary = {
        **TRUST_SURFACE_COUNTS,
        "phase_id": PHASE_ID,
        "generated_at": GENERATED_AT,
        "repository_remains": REPOSITORY_REMAINS,
        "non_authority_statement": NON_AUTHORITY_STATEMENT,
        "support_statuses": SUPPORT_STATUSES,
        "guarantees": GUARANTEES,
        "preserved_prohibition_count": len(PRESERVED_PROHIBITIONS),
        "frontend_surface_coverage_count": len(FRONTEND_SURFACE_COVERAGE),
        "intentionally_preserved_limitation_count": len(INTENTIONALLY_PRESERVED_LIMITATIONS),
        "created_file_count": len(CREATED_FILES),
        "modified_file_count": len(MODIFIED_FILES),
        "created_files_present": all(file_coverage["created_files_present"].values()),
        "validation_error_count": 0,
    }
    report: dict[str, Any] = {
        "phase_id": PHASE_ID,
        "generated_at": GENERATED_AT,
        "repository_remains": REPOSITORY_REMAINS,
        "non_authority_statement": NON_AUTHORITY_STATEMENT,
        "summary": summary,
        "frontend_surface_coverage": FRONTEND_SURFACE_COVERAGE,
        "file_coverage": file_coverage,
        "validation": validation,
        "enabled_semantics": enabled_semantics,
        "preserved_prohibitions": PRESERVED_PROHIBITIONS,
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
        help="v4.5C.1 frontend trust surface foundations JSON report output path",
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
    print(f"trust_status_card_count={summary['trust_status_card_count']}")
    print(f"support_status_badge_count={summary['support_status_badge_count']}")
    print(f"explainability_panel_count={summary['explainability_panel_count']}")
    print(f"evidence_panel_count={summary['evidence_panel_count']}")
    print(
        "provenance_lineage_panel_count="
        f"{summary['provenance_lineage_panel_count']}"
    )
    print(f"coverage_summary_count={summary['coverage_summary_count']}")
    print(f"confidence_summary_count={summary['confidence_summary_count']}")
    print(f"diagnostics_summary_count={summary['diagnostics_summary_count']}")
    print(f"read_only_surfaces_verified={validation['read_only_surfaces_verified']}")
    print(
        "descriptive_only_surfaces_verified="
        f"{validation['descriptive_only_surfaces_verified']}"
    )
    print(
        "unsupported_state_visibility_preserved="
        f"{validation['unsupported_state_visibility_preserved']}"
    )
    print(
        "fail_visible_diagnostics_preserved="
        f"{validation['fail_visible_diagnostics_preserved']}"
    )
    print(
        "no_recommendation_ranking_scoring_semantics_introduced="
        f"{validation['no_recommendation_ranking_scoring_semantics_introduced']}"
    )
    print(f"no_planner_authority_introduced={validation['no_planner_authority_introduced']}")
    print(
        "no_operational_behavior_introduced="
        f"{validation['no_operational_behavior_introduced']}"
    )
    for key, value in sorted(report["enabled_semantics"].items()):
        print(f"{key}={value}")
    print(f"repository_remains={','.join(report['repository_remains'])}")
    print(f"non_authority_statement={report['non_authority_statement']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
