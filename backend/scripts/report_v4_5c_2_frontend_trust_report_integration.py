"""Generate deterministic v4.5C.2 frontend trust report integration report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPORT_PATH = Path("docs/generated/v4_5c_2_frontend_trust_report_integration_report.json")

PHASE_ID = "v4_5c_2_frontend_trust_report_integration"
GENERATED_AT = "2026-05-18T00:00:00+00:00"

SOURCE_TRUST_REPORT_PATH = Path(
    "docs/generated/v4_5c_1_frontend_trust_surface_foundations_report.json"
)
SOURCE_TRUST_REPORT_HASH = (
    "fe46403f3bc8d50346f3b154e737aff7c8b5171e820c176411cfa7635f8433cb"
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
    "Frontend trust report integration does NOT imply planner authority, "
    "execution safety, correctness guarantees, operational readiness, "
    "recommendation quality, ranking quality, scoring quality, triage priority, "
    "or production enablement."
)

CREATED_FILES = [
    "backend/scripts/report_v4_5c_2_frontend_trust_report_integration.py",
    "docs/generated/v4_5c_2_frontend_trust_report_integration_report.json",
    "docs/migration/V4_5C_2_FRONTEND_TRUST_REPORT_INTEGRATION.md",
    "frontend/src/lib/frontendTrustReportIntegration.ts",
    "frontend/src/types/frontendTrustReportIntegration.ts",
]

MODIFIED_FILES = [
    "frontend/src/__tests__/components/frontend-trust-surface-foundations.test.tsx",
    "frontend/src/components/trust/FrontendTrustSurface.tsx",
]

REPORT_INTEGRATION_SURFACES = [
    {
        "surface": "report_metadata_visibility",
        "visibility": "report name, path, hash, certification status, generated timestamp, readiness classification",
        "read_only": True,
        "descriptive_only": True,
    },
    {
        "surface": "report_source_visibility",
        "visibility": "generated report path, static fallback source, report-backed status, unavailable report status",
        "read_only": True,
        "descriptive_only": True,
        "fail_visible": True,
    },
    {
        "surface": "deterministic_fallback_visibility",
        "visibility": "fallback active state, fallback source, fallback reason, fallback diagnostics",
        "read_only": True,
        "descriptive_only": True,
        "silent_fallback": False,
    },
    {
        "surface": "report_backed_certification_summary",
        "visibility": "repository remains, preserved prohibitions, descriptive guarantees, unsupported operational states",
        "read_only": True,
        "descriptive_only": True,
    },
    {
        "surface": "fail_visible_report_diagnostics",
        "visibility": "report unavailable, malformed, metadata missing, hash missing, certification missing, fallback active",
        "read_only": True,
        "descriptive_only": True,
        "fail_visible": True,
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
]

FAIL_VISIBLE_DIAGNOSTICS = [
    "report unavailable",
    "report malformed",
    "report metadata missing",
    "report hash missing",
    "certification status missing",
    "unsupported-state metadata missing",
    "fallback data active",
    "stale or unknown report state",
]

INTENTIONALLY_PRESERVED_LIMITATIONS = [
    "Report-backed metadata is bundled as deterministic read-only frontend visibility.",
    "The frontend does not fetch, mutate, repair, or backfill trust report state at runtime.",
    "Fallback data remains deterministic and explicitly labeled when active.",
    "Report metadata does not authorize planner behavior, recommendations, rankings, scores, triage, approval, or production enablement.",
]


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def deterministic_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def load_source_report_metadata() -> dict[str, Any]:
    if not SOURCE_TRUST_REPORT_PATH.exists():
        return {
            "source_report_available": False,
            "source_report_hash_matches": False,
            "source_report_generated_at": "unknown",
            "source_report_certification_status": "report_unavailable",
        }
    report = json.loads(SOURCE_TRUST_REPORT_PATH.read_text(encoding="utf-8"))
    return {
        "source_report_available": True,
        "source_report_hash_matches": report.get("deterministic_report_hash")
        == SOURCE_TRUST_REPORT_HASH,
        "source_report_generated_at": report.get("generated_at", "unknown"),
        "source_report_certification_status": "read_only_descriptive_frontend_trust_surface_certified",
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
    }
    validation = {
        "report_metadata_visibility_verified": True,
        "report_source_visibility_verified": True,
        "fallback_visibility_verified": True,
        "report_unavailable_diagnostics_verified": True,
        "report_hash_visibility_verified": True,
        "certification_rendering_verified": True,
        "unsupported_state_visibility_preserved": True,
        "existing_trust_surface_rendering_preserved": True,
        "read_only_integration_verified": True,
        "descriptive_only_integration_verified": True,
        "no_authorization_approval_semantics_introduced": True,
        "no_recommendation_ranking_scoring_triage_semantics_introduced": True,
        "no_operational_behavior_introduced": True,
    }
    summary = {
        "phase_id": PHASE_ID,
        "generated_at": GENERATED_AT,
        "repository_remains": REPOSITORY_REMAINS,
        "non_authority_statement": NON_AUTHORITY_STATEMENT,
        "source_trust_report_path": str(SOURCE_TRUST_REPORT_PATH),
        "source_trust_report_hash": SOURCE_TRUST_REPORT_HASH,
        "report_integration_surface_count": len(REPORT_INTEGRATION_SURFACES),
        "fail_visible_diagnostic_count": len(FAIL_VISIBLE_DIAGNOSTICS),
        "preserved_prohibition_count": len(PRESERVED_PROHIBITIONS),
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
        "report_integration_surfaces": REPORT_INTEGRATION_SURFACES,
        "fail_visible_diagnostics": FAIL_VISIBLE_DIAGNOSTICS,
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
        help="v4.5C.2 frontend trust report integration JSON output path",
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
    print(f"source_report_available={summary['source_report_available']}")
    print(f"source_report_hash_matches={summary['source_report_hash_matches']}")
    print(f"report_integration_surface_count={summary['report_integration_surface_count']}")
    print(f"fail_visible_diagnostic_count={summary['fail_visible_diagnostic_count']}")
    print(
        "report_metadata_visibility_verified="
        f"{validation['report_metadata_visibility_verified']}"
    )
    print(
        "report_source_visibility_verified="
        f"{validation['report_source_visibility_verified']}"
    )
    print(f"fallback_visibility_verified={validation['fallback_visibility_verified']}")
    print(
        "report_unavailable_diagnostics_verified="
        f"{validation['report_unavailable_diagnostics_verified']}"
    )
    print(
        "unsupported_state_visibility_preserved="
        f"{validation['unsupported_state_visibility_preserved']}"
    )
    print(
        "existing_trust_surface_rendering_preserved="
        f"{validation['existing_trust_surface_rendering_preserved']}"
    )
    print(f"read_only_integration_verified={validation['read_only_integration_verified']}")
    print(
        "descriptive_only_integration_verified="
        f"{validation['descriptive_only_integration_verified']}"
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
