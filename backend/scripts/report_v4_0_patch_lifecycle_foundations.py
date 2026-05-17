"""Generate deterministic v4.0 patch lifecycle foundation evidence."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from operational_lifecycle.lifecycle_equality import (  # noqa: E402
    patch_lifecycle_foundations_equal,
)
from operational_lifecycle.lifecycle_hashing import (  # noqa: E402
    deterministic_lifecycle_hash,
    hash_lifecycle_lineage_record,
    hash_lifecycle_provenance_record,
    hash_lifecycle_visibility_record,
    hash_patch_identity,
    hash_patch_lifecycle_foundation,
    hash_patch_operational_metadata,
)
from operational_lifecycle.lifecycle_identity import (  # noqa: E402
    patch_identity_normalization_report,
)
from operational_lifecycle.lifecycle_lineage import (  # noqa: E402
    validate_lifecycle_lineage_continuity,
)
from operational_lifecycle.lifecycle_models import (  # noqa: E402
    V4_0_PATCH_LIFECYCLE_GENERATED_AT,
    V4_0_PATCH_LIFECYCLE_PHASE_ID,
    V4_0_PATCH_LIFECYCLE_SCHEMA_VERSION,
    V4_0_PATCH_LIFECYCLE_STATUS_BLOCKED,
    V4_0_PATCH_LIFECYCLE_STATUS_STABLE,
    default_patch_lifecycle_foundation,
)
from operational_lifecycle.lifecycle_provenance import (  # noqa: E402
    validate_lifecycle_provenance_continuity,
)
from operational_lifecycle.lifecycle_serialization import (  # noqa: E402
    export_patch_lifecycle_foundation,
    serialize_patch_lifecycle_foundation,
)
from operational_lifecycle.lifecycle_visibility import (  # noqa: E402
    count_lifecycle_states,
    validate_lifecycle_visibility,
)


REPORT_PATH = Path("docs/generated/v4_0_patch_lifecycle_foundations_report.json")


def build_v4_0_patch_lifecycle_foundations_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    foundation = default_patch_lifecycle_foundation()
    repeated_foundation = default_patch_lifecycle_foundation()
    reordered_foundation = replace(
        foundation,
        lifecycle_states=tuple(reversed(foundation.lifecycle_states)),
        provenance_records=tuple(reversed(foundation.provenance_records)),
        lineage_records=tuple(reversed(foundation.lineage_records)),
        visibility_records=tuple(reversed(foundation.visibility_records)),
    )
    exported = export_patch_lifecycle_foundation(foundation)
    visibility = validate_lifecycle_visibility(foundation)
    provenance_validations = [
        validate_lifecycle_provenance_continuity(record) for record in foundation.provenance_records
    ]
    lineage_validations = [validate_lifecycle_lineage_continuity(record) for record in foundation.lineage_records]
    serialization_first = serialize_patch_lifecycle_foundation(foundation)
    serialization_second = serialize_patch_lifecycle_foundation(repeated_foundation)
    serialization_reordered = serialize_patch_lifecycle_foundation(reordered_foundation)
    foundation_hash = hash_patch_lifecycle_foundation(foundation)
    repeated_hash = hash_patch_lifecycle_foundation(repeated_foundation)
    reordered_hash = hash_patch_lifecycle_foundation(reordered_foundation)
    execution_boundary_enabled_count = _execution_boundary_enabled_count(foundation)
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            sum(0 if item["valid"] else 1 for item in provenance_validations),
            sum(0 if item["valid"] else 1 for item in lineage_validations),
            0 if execution_boundary_enabled_count == 0 else 1,
        ]
    )
    status = (
        V4_0_PATCH_LIFECYCLE_STATUS_STABLE
        if validation_error_count == 0
        else V4_0_PATCH_LIFECYCLE_STATUS_BLOCKED
    )
    state_counts = count_lifecycle_states(foundation.lifecycle_states)
    report = {
        "schema_version": "v4_0.patch_lifecycle_foundations_report.1",
        "generated_at": V4_0_PATCH_LIFECYCLE_GENERATED_AT,
        "phase_id": V4_0_PATCH_LIFECYCLE_PHASE_ID,
        "phase_name": "v4.0_phase_1_patch_lifecycle_foundations",
        "repo_root": str(root),
        "architectural_purpose": "deterministic operational lifecycle intelligence foundations without operational execution",
        "operational_lifecycle_mode": "descriptive_only",
        "foundation_status": status,
        "lifecycle_model_counts": {
            "patch_identity_count": 1,
            "lifecycle_state_count": len(foundation.lifecycle_states),
            "lifecycle_provenance_record_count": len(foundation.provenance_records),
            "lifecycle_lineage_record_count": len(foundation.lineage_records),
            "lifecycle_visibility_record_count": len(foundation.visibility_records),
            "patch_operational_metadata_count": 1,
            "lifecycle_state_counts": state_counts,
        },
        "lineage_continuity_visibility": {
            "lineage_record_count": len(foundation.lineage_records),
            "lineage_continuity_reference_count": sum(
                len(record.continuity_references) for record in foundation.lineage_records
            ),
            "lineage_gap_visibility_count": visibility["lineage_gap_visibility_count"],
            "lineage_validations": lineage_validations,
        },
        "provenance_continuity_visibility": {
            "provenance_record_count": len(foundation.provenance_records),
            "provenance_continuity_reference_count": sum(
                len(record.continuity_references) for record in foundation.provenance_records
            ),
            "provenance_validations": provenance_validations,
        },
        "fail_visible_visibility": {
            "fail_visible_lifecycle_state_count": visibility["fail_visible_lifecycle_state_count"],
            "unsupported_state_visibility_count": visibility["unsupported_state_visibility_count"],
            "prohibited_state_visibility_count": visibility["prohibited_state_visibility_count"],
            "unknown_state_visibility_count": visibility["unknown_state_visibility_count"],
            "integrity_warning_visibility_count": visibility["integrity_warning_visibility_count"],
            "lifecycle_continuity_visibility_count": visibility["lifecycle_continuity_visibility_count"],
            "lineage_gap_visibility_count": visibility["lineage_gap_visibility_count"],
            "unsupported_states_visible": visibility["unsupported_states_visible"],
            "prohibited_states_visible": visibility["prohibited_states_visible"],
            "unknown_states_visible": visibility["unknown_states_visible"],
            "visibility_is_descriptive_only": visibility["visibility_is_descriptive_only"],
        },
        "deterministic_serialization_verification": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_0_patch_lifecycle_foundations",
            "payload_length": len(serialization_first),
            "unsupported_states_preserved": visibility["unsupported_state_visibility_count"] > 0,
            "prohibited_states_preserved": visibility["prohibited_state_visibility_count"] > 0,
            "unknown_states_preserved": visibility["unknown_state_visibility_count"] > 0,
            "integrity_warnings_preserved": visibility["integrity_warning_visibility_count"] > 0,
            "hidden_omission_enabled": False,
        },
        "deterministic_hashing_verification": {
            "stable": foundation_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_0_patch_lifecycle_foundations",
            "foundation_hash": foundation_hash,
            "patch_identity_hash": hash_patch_identity(foundation.patch_identity),
            "provenance_hashes": [
                hash_lifecycle_provenance_record(record) for record in foundation.provenance_records
            ],
            "lineage_hashes": [hash_lifecycle_lineage_record(record) for record in foundation.lineage_records],
            "visibility_hashes": [
                hash_lifecycle_visibility_record(record) for record in foundation.visibility_records
            ],
            "metadata_hash": hash_patch_operational_metadata(foundation.operational_metadata),
        },
        "deterministic_equality_verification": {
            "dataclass_equality_stable": foundation == repeated_foundation,
            "dataclass_hash_stable": hash(foundation) == hash(repeated_foundation),
            "serialized_equality_stable": patch_lifecycle_foundations_equal(foundation, repeated_foundation),
            "reordered_serialized_equality_stable": patch_lifecycle_foundations_equal(
                foundation,
                reordered_foundation,
            ),
        },
        "lifecycle_identity_normalization": patch_identity_normalization_report(foundation.patch_identity),
        "non_execution_guarantees": _non_execution_guarantees(foundation),
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "execution_boundary_enabled_count": execution_boundary_enabled_count,
            "deterministic_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_hashing_verified": foundation_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": patch_lifecycle_foundations_equal(
                foundation,
                repeated_foundation,
            ),
            "provenance_continuity_verified": all(item["valid"] for item in provenance_validations),
            "lineage_continuity_verified": all(item["valid"] for item in lineage_validations),
            "replay_continuity_verified": all(item["replay_safe"] for item in lineage_validations),
            "rollback_continuity_verified": all(item["rollback_safe"] for item in lineage_validations),
            "integrity_safe_visibility_preserved": visibility["valid"],
            "unsupported_state_visibility_count": visibility["unsupported_state_visibility_count"],
            "prohibited_state_visibility_count": visibility["prohibited_state_visibility_count"],
            "unknown_state_visibility_count": visibility["unknown_state_visibility_count"],
            "integrity_warning_visibility_count": visibility["integrity_warning_visibility_count"],
            "lineage_gap_visibility_count": visibility["lineage_gap_visibility_count"],
            "descriptive_only_verified": foundation.descriptive_only and foundation.non_executable,
        },
        "foundation": exported,
        "explicit_limitations": [
            "v4.0 Phase 1 does not enable orchestration execution.",
            "v4.0 Phase 1 does not enable patch execution or patch application.",
            "v4.0 Phase 1 does not enable deployment execution.",
            "v4.0 Phase 1 does not enable scheduling, routing, or dispatch.",
            "v4.0 Phase 1 does not enable optimization, recommendation, ranking, scoring, or selection.",
            "v4.0 Phase 1 does not enable authorization, approval, remediation, or repair.",
            "v4.0 Phase 1 does not enable runtime mutation or autonomous behavior.",
            "v4.0 Phase 1 remains descriptive-only operational lifecycle intelligence.",
        ],
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def _non_execution_guarantees(foundation) -> dict[str, bool]:
    return {
        "non_executable": foundation.non_executable,
        "descriptive_only": foundation.descriptive_only,
        "lifecycle_execution_absent": not foundation.lifecycle_execution_enabled,
        "patch_execution_absent": not foundation.patch_execution_enabled,
        "patch_application_absent": not foundation.patch_application_enabled,
        "deployment_execution_absent": not foundation.deployment_execution_enabled,
        "scheduling_absent": not foundation.scheduling_enabled,
        "routing_absent": not foundation.routing_enabled,
        "dispatch_absent": not foundation.dispatch_enabled,
        "optimization_absent": not foundation.optimization_enabled,
        "recommendation_absent": not foundation.recommendation_enabled,
        "ranking_absent": not foundation.ranking_enabled,
        "scoring_absent": not foundation.scoring_enabled,
        "selection_absent": not foundation.selection_enabled,
        "authorization_absent": not foundation.authorization_enabled,
        "approval_absent": not foundation.approval_enabled,
        "remediation_absent": not foundation.remediation_enabled,
        "repair_absent": not foundation.repair_enabled,
        "autonomous_behavior_absent": not foundation.autonomous_behavior_enabled,
        "runtime_mutation_absent": not foundation.runtime_mutation_enabled,
        "hidden_lifecycle_state_mutation_absent": not foundation.hidden_lifecycle_state_mutation_enabled,
        "implicit_operational_state_transition_absent": not foundation.implicit_operational_state_transition_enabled,
        "automatic_patch_transition_logic_absent": not foundation.automatic_patch_transition_logic_enabled,
        "callable_operational_flow_absent": not foundation.callable_operational_flow_enabled,
        "production_automation_absent": not foundation.production_automation_enabled,
    }


def _execution_boundary_enabled_count(foundation) -> int:
    return sum(1 for value in _non_execution_guarantees(foundation).values() if value is False)


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_lifecycle_hash(payload)


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
    report = build_v4_0_patch_lifecycle_foundations_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
