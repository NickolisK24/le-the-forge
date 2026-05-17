"""Generate deterministic v4.0 operational lifecycle continuity certification evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from operational_lifecycle.continuity_certification_engine import (  # noqa: E402
    certify_operational_lifecycle_continuity,
)
from operational_lifecycle.continuity_certification_hashing import (  # noqa: E402
    deterministic_operational_continuity_hash,
)
from operational_lifecycle.continuity_certification_models import (  # noqa: E402
    OPERATIONAL_CONTINUITY_FINDING_TYPES,
    V4_0_CONTINUITY_CERTIFICATION_GENERATED_AT,
    V4_0_CONTINUITY_CERTIFICATION_PHASE_ID,
    V4_0_CONTINUITY_CERTIFICATION_STATUS_BLOCKED,
    V4_0_CONTINUITY_CERTIFICATION_STATUS_STABLE,
)
from operational_lifecycle.continuity_certification_serialization import (  # noqa: E402
    export_operational_continuity_certification_report,
)
from operational_lifecycle.continuity_certification_visibility import (  # noqa: E402
    count_continuity_finding_types,
    count_continuity_severities,
    validate_operational_continuity_visibility,
)
from operational_lifecycle.integrity_enforcement_audit import audit_operational_lifecycle_integrity  # noqa: E402
from scripts.report_v4_0_operational_lifecycle_integrity_enforcement import (  # noqa: E402
    build_representative_operational_integrity_inputs,
)


REPORT_PATH = Path("docs/generated/v4_0_operational_lifecycle_continuity_certification_report.json")


def build_representative_operational_continuity_inputs():
    (
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
    ) = build_representative_operational_integrity_inputs()
    integrity_report = audit_operational_lifecycle_integrity(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
    )
    return (
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
        integrity_report,
    )


def build_v4_0_operational_lifecycle_continuity_certification_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    inputs = build_representative_operational_continuity_inputs()
    continuity_report = certify_operational_lifecycle_continuity(*inputs)
    exported = export_operational_continuity_certification_report(continuity_report)
    visibility_validation = validate_operational_continuity_visibility(continuity_report)
    finding_type_counts = count_continuity_finding_types(continuity_report.findings)
    severity_counts = count_continuity_severities(continuity_report.findings)
    validation_error_count = 0 if visibility_validation["valid"] else 1
    status = (
        V4_0_CONTINUITY_CERTIFICATION_STATUS_STABLE
        if validation_error_count == 0
        else V4_0_CONTINUITY_CERTIFICATION_STATUS_BLOCKED
    )
    rebuilt_hash = certify_operational_lifecycle_continuity(*inputs).deterministic_report_hash
    continuity_booleans = {
        "replay_safe": continuity_report.replay_safe,
        "rollback_safe": continuity_report.rollback_safe,
        "provenance_safe": continuity_report.provenance_safe,
        "lineage_safe": continuity_report.lineage_safe,
        "serialization_stable": continuity_report.serialization_stable,
        "hashing_stable": continuity_report.hashing_stable,
        "visibility_preserved": continuity_report.visibility_preserved,
        "integrity_preserved": continuity_report.integrity_preserved,
        "execution_authorized": continuity_report.execution_authorized,
        "remediation_authorized": continuity_report.remediation_authorized,
        "production_consumption_enabled": continuity_report.production_consumption_enabled,
    }
    report = {
        "schema_version": "v4_0.operational_lifecycle_continuity_certification_report.1",
        "generated_at": V4_0_CONTINUITY_CERTIFICATION_GENERATED_AT,
        "phase_id": V4_0_CONTINUITY_CERTIFICATION_PHASE_ID,
        "phase_name": "v4.0_phase_9_operational_lifecycle_continuity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic operational lifecycle continuity certification without authorization",
        "certification_mode": "descriptive_certification_only",
        "foundation_status": status,
        "lifecycle_identity": continuity_report.lifecycle_identity,
        "drift_report_hash": continuity_report.drift_report_hash,
        "governance_report_hash": continuity_report.governance_report_hash,
        "validation_report_hash": continuity_report.validation_report_hash,
        "production_consumption_report_hash": continuity_report.production_consumption_report_hash,
        "recovery_report_hash": continuity_report.recovery_report_hash,
        "diagnostics_report_hash": continuity_report.diagnostics_report_hash,
        "integrity_report_hash": continuity_report.integrity_report_hash,
        "continuity_status": continuity_report.continuity_status,
        "finding_count": continuity_report.finding_count,
        "finding_type_counts": finding_type_counts,
        "severity_counts": severity_counts,
        "certified_count": continuity_report.certified_count,
        "warning_count": continuity_report.warning_count,
        "broken_count": continuity_report.broken_count,
        "blocked_count": continuity_report.blocked_count,
        "prohibited_count": continuity_report.prohibited_count,
        "unknown_count": continuity_report.unknown_count,
        "critical_count": continuity_report.critical_count,
        "replay_safety_status": continuity_report.replay_safe,
        "rollback_safety_status": continuity_report.rollback_safe,
        "provenance_safety_status": continuity_report.provenance_safe,
        "lineage_safety_status": continuity_report.lineage_safe,
        "serialization_stability_status": continuity_report.serialization_stable,
        "hashing_stability_status": continuity_report.hashing_stable,
        "visibility_preservation_status": continuity_report.visibility_preserved,
        "integrity_preservation_status": continuity_report.integrity_preserved,
        "execution_authorization_status": continuity_report.execution_authorized,
        "remediation_authorization_status": continuity_report.remediation_authorized,
        "production_consumption_enabled_status": continuity_report.production_consumption_enabled,
        "deterministic_continuity_report_hash": continuity_report.deterministic_report_hash,
        "implemented_continuity_finding_types": list(OPERATIONAL_CONTINUITY_FINDING_TYPES),
        "continuity_booleans": continuity_booleans,
        "deterministic_guarantees": {
            "stable_finding_order": [finding["deterministic_key"] for finding in exported["findings"]]
            == sorted(finding["deterministic_key"] for finding in exported["findings"]),
            "all_report_hashes_preserved": all(
                bool(value)
                for value in (
                    continuity_report.drift_report_hash,
                    continuity_report.governance_report_hash,
                    continuity_report.validation_report_hash,
                    continuity_report.production_consumption_report_hash,
                    continuity_report.recovery_report_hash,
                    continuity_report.diagnostics_report_hash,
                    continuity_report.integrity_report_hash,
                )
            ),
            "continuity_hash_stable": continuity_report.deterministic_report_hash == rebuilt_hash,
            "serialization_stable": continuity_report.serialization_stable,
            "hashing_stable": continuity_report.hashing_stable,
            "visibility_preserved": continuity_report.visibility_preserved,
            "integrity_preserved": continuity_report.integrity_preserved,
        },
        "fail_visible_guarantees": {
            finding_type: count > 0 for finding_type, count in finding_type_counts.items() if finding_type != "invalid"
        },
        "non_execution_guarantees": {
            "descriptive_only": continuity_report.descriptive_only,
            "approval_absent": not continuity_report.approval_enabled,
            "authorization_absent": not continuity_report.authorization_enabled,
            "execution_authorization_absent": not continuity_report.execution_authorized,
            "remediation_authorization_absent": not continuity_report.remediation_authorized,
            "production_consumption_disabled": not continuity_report.production_consumption_enabled,
            "execution_absent": not continuity_report.execution_enabled,
            "orchestration_execution_absent": not continuity_report.orchestration_execution_enabled,
            "recommendation_absent": not continuity_report.recommendation_enabled,
            "ranking_absent": not continuity_report.ranking_enabled,
            "scoring_absent": not continuity_report.scoring_enabled,
            "selection_absent": not continuity_report.selection_enabled,
            "optimization_absent": not continuity_report.optimization_enabled,
            "runtime_mutation_absent": not continuity_report.runtime_mutation_enabled,
        },
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "finding_count": continuity_report.finding_count,
            "visibility_validation_passed": visibility_validation["valid"],
            "capability_enabled_count": visibility_validation["capability_enabled_count"],
            "continuity_status": continuity_report.continuity_status,
            "certified_count": continuity_report.certified_count,
            "broken_count": continuity_report.broken_count,
            "replay_safe": continuity_report.replay_safe,
            "rollback_safe": continuity_report.rollback_safe,
            "provenance_safe": continuity_report.provenance_safe,
            "lineage_safe": continuity_report.lineage_safe,
            "serialization_stable": continuity_report.serialization_stable,
            "hashing_stable": continuity_report.hashing_stable,
            "visibility_preserved": continuity_report.visibility_preserved,
            "integrity_preserved": continuity_report.integrity_preserved,
        },
        "operational_continuity_certification_report": exported,
        "explicit_limitations": [
            "v4.0 Phase 9 certifies deterministic continuity evidence only.",
            "v4.0 Phase 9 does not authorize execution.",
            "v4.0 Phase 9 does not authorize remediation.",
            "v4.0 Phase 9 does not enable production consumption.",
            "v4.0 Phase 9 does not recommend, rank, score, select, optimize, approve, repair, execute, orchestrate, or mutate runtime state.",
        ],
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_operational_continuity_hash(payload)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_0_operational_lifecycle_continuity_certification_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    print(f"deterministic_continuity_report_hash={report['deterministic_continuity_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
