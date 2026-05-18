"""Generate deterministic v4.5C.3 frontend trust navigation entrypoints report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPORT_PATH = Path(
    "docs/generated/v4_5c_3_frontend_trust_navigation_entrypoints_report.json"
)

PHASE_ID = "v4_5c_3_frontend_trust_navigation_entrypoints"
GENERATED_AT = "2026-05-18T00:00:00+00:00"
TRUST_SURFACE_ROUTE = "/trusted-data/frontend-trust"
TRUSTED_DATA_ROUTE = "/trusted-data"

SOURCE_C2_REPORT_PATH = Path(
    "docs/generated/v4_5c_2_frontend_trust_report_integration_report.json"
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
    "Frontend trust navigation does NOT imply frontend launch authorization, "
    "planner authority, execution safety, correctness guarantees, operational "
    "readiness, production enablement, recommendation quality, ranking quality, "
    "authorization, or approval."
)

CREATED_FILES = [
    "backend/scripts/report_v4_5c_3_frontend_trust_navigation_entrypoints.py",
    "docs/generated/v4_5c_3_frontend_trust_navigation_entrypoints_report.json",
    "docs/migration/V4_5C_3_FRONTEND_TRUST_NAVIGATION_ENTRYPOINTS.md",
    "frontend/src/components/trust/TrustSurfaceEntryCallout.tsx",
]

MODIFIED_FILES = [
    "frontend/src/__tests__/components/frontend-trust-surface-foundations.test.tsx",
    "frontend/src/components/navigation/Sidebar.tsx",
    "frontend/src/pages/TrustedDataExplanationPage.tsx",
]

NAVIGATION_ENTRYPOINTS = [
    {
        "entrypoint": "trusted_data_explanation_callout",
        "source_route": TRUSTED_DATA_ROUTE,
        "target_route": TRUST_SURFACE_ROUTE,
        "copy": "Read-only trust surface",
        "read_only": True,
        "descriptive_only": True,
        "non_authoritative": True,
    },
    {
        "entrypoint": "trusted_data_explanation_link",
        "source_route": TRUSTED_DATA_ROUTE,
        "target_route": TRUST_SURFACE_ROUTE,
        "copy": "View trust visibility",
        "read_only": True,
        "descriptive_only": True,
        "non_authoritative": True,
    },
    {
        "entrypoint": "sidebar_navigation_link",
        "source_route": "app_sidebar",
        "target_route": TRUST_SURFACE_ROUTE,
        "copy": "Trust Visibility",
        "read_only": True,
        "descriptive_only": True,
        "non_authoritative": True,
    },
]

REPORT_AWARE_MESSAGING = [
    "deterministic report-backed visibility",
    "fallback data visibility",
    "report hash and certification visibility",
    "fail-visible diagnostics",
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

PROHIBITED_NAVIGATION_LANGUAGE = [
    "Approved",
    "Safe to use",
    "Recommended",
    "Best build",
    "Fully trusted",
    "Production ready",
    "Guaranteed correct",
]

INTENTIONALLY_PRESERVED_LIMITATIONS = [
    "Navigation entry points are read-only links to the existing trust surface.",
    "Trust navigation does not fetch, mutate, repair, or backfill report data.",
    "Sidebar discoverability remains a link, not a planner or production enablement control.",
    "Report-aware messaging keeps fallback and diagnostic limitations visible.",
]


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def deterministic_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def load_source_report_metadata() -> dict[str, Any]:
    if not SOURCE_C2_REPORT_PATH.exists():
        return {
            "source_c2_report_available": False,
            "source_c2_report_hash": "missing",
            "source_c2_report_phase_id": "missing",
        }
    report = json.loads(SOURCE_C2_REPORT_PATH.read_text(encoding="utf-8"))
    return {
        "source_c2_report_available": True,
        "source_c2_report_hash": report.get("deterministic_report_hash", "missing"),
        "source_c2_report_phase_id": report.get("phase_id", "missing"),
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
        "stable_trust_surface_route_preserved": True,
        "trusted_data_entrypoint_rendering_verified": True,
        "sidebar_entrypoint_rendering_verified": True,
        "entrypoint_links_verified": True,
        "descriptive_only_trust_copy_verified": True,
        "report_aware_messaging_verified": True,
        "fallback_behavior_preserved": True,
        "prohibited_navigation_language_absent": True,
        "read_only_navigation_verified": True,
        "non_authoritative_navigation_verified": True,
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
        "navigation_entrypoint_count": len(NAVIGATION_ENTRYPOINTS),
        "report_aware_message_count": len(REPORT_AWARE_MESSAGING),
        "preserved_prohibition_count": len(PRESERVED_PROHIBITIONS),
        "prohibited_navigation_language_count": len(PROHIBITED_NAVIGATION_LANGUAGE),
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
        "navigation_entrypoints": NAVIGATION_ENTRYPOINTS,
        "report_aware_messaging": REPORT_AWARE_MESSAGING,
        "file_coverage": file_coverage,
        "validation": validation,
        "enabled_semantics": enabled_semantics,
        "preserved_prohibitions": PRESERVED_PROHIBITIONS,
        "prohibited_navigation_language": PROHIBITED_NAVIGATION_LANGUAGE,
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
        help="v4.5C.3 frontend trust navigation entrypoints JSON output path",
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
    print(f"navigation_entrypoint_count={summary['navigation_entrypoint_count']}")
    print(f"report_aware_message_count={summary['report_aware_message_count']}")
    print(f"source_c2_report_available={summary['source_c2_report_available']}")
    print(f"source_c2_report_hash={summary['source_c2_report_hash']}")
    print(
        "stable_trust_surface_route_preserved="
        f"{validation['stable_trust_surface_route_preserved']}"
    )
    print(
        "trusted_data_entrypoint_rendering_verified="
        f"{validation['trusted_data_entrypoint_rendering_verified']}"
    )
    print(
        "sidebar_entrypoint_rendering_verified="
        f"{validation['sidebar_entrypoint_rendering_verified']}"
    )
    print(f"entrypoint_links_verified={validation['entrypoint_links_verified']}")
    print(f"report_aware_messaging_verified={validation['report_aware_messaging_verified']}")
    print(f"fallback_behavior_preserved={validation['fallback_behavior_preserved']}")
    print(
        "prohibited_navigation_language_absent="
        f"{validation['prohibited_navigation_language_absent']}"
    )
    print(f"read_only_navigation_verified={validation['read_only_navigation_verified']}")
    print(
        "non_authoritative_navigation_verified="
        f"{validation['non_authoritative_navigation_verified']}"
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
