"""Generate deterministic v4.2 coordination manifest foundation evidence."""

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

from refresh_coordination.coordination_manifest_diagnostics import (  # noqa: E402
    build_coordination_manifest_diagnostics,
    coordination_manifest_identity_key,
    coordination_manifests_equal,
    count_coordination_dependency_states,
    validate_coordination_continuity_visibility,
    validate_coordination_lineage_continuity,
    validate_coordination_manifest_non_execution,
    validate_coordination_manifest_visibility,
)
from refresh_coordination.coordination_manifest_hashing import (  # noqa: E402
    deterministic_coordination_manifest_hash,
    hash_coordination_continuity,
    hash_coordination_dependency,
    hash_coordination_lineage,
    hash_coordination_manifest,
    hash_coordination_manifest_identity,
)
from refresh_coordination.coordination_manifest_models import (  # noqa: E402
    V4_2_COORDINATION_MANIFEST_GENERATED_AT,
    V4_2_COORDINATION_MANIFEST_PHASE_ID,
    V4_2_COORDINATION_MANIFEST_REPORT_SCHEMA_VERSION,
    V4_2_COORDINATION_MANIFEST_STATUS_BLOCKED,
    V4_2_COORDINATION_MANIFEST_STATUS_STABLE,
    default_coordination_manifest,
)
from refresh_coordination.coordination_manifest_serialization import (  # noqa: E402
    export_coordination_manifest,
    serialize_coordination_manifest,
)


REPORT_PATH = Path("docs/generated/v4_2_coordination_manifest_foundations_report.json")


def _reordered_coordination_manifest():
    manifest = default_coordination_manifest()
    return replace(
        manifest,
        dependency_references=tuple(reversed(manifest.dependency_references)),
        lineage_references=tuple(reversed(manifest.lineage_references)),
        continuity_references=tuple(reversed(manifest.continuity_references)),
        diagnostics=tuple(reversed(manifest.diagnostics)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_coordination_manifest_hash(payload)


def build_v4_2_coordination_manifest_foundations_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    manifest = default_coordination_manifest()
    repeated = default_coordination_manifest()
    reordered = _reordered_coordination_manifest()
    exported = export_coordination_manifest(manifest)
    visibility = validate_coordination_manifest_visibility(manifest)
    lineage = validate_coordination_lineage_continuity(manifest)
    continuity = validate_coordination_continuity_visibility(manifest)
    non_execution = validate_coordination_manifest_non_execution(manifest)
    diagnostics = build_coordination_manifest_diagnostics(manifest)
    serialization_first = serialize_coordination_manifest(manifest)
    serialization_second = serialize_coordination_manifest(repeated)
    serialization_reordered = serialize_coordination_manifest(reordered)
    manifest_hash = hash_coordination_manifest(manifest)
    repeated_hash = hash_coordination_manifest(repeated)
    reordered_hash = hash_coordination_manifest(reordered)
    dependency_hashes = [
        hash_coordination_dependency(reference) for reference in manifest.dependency_references
    ]
    lineage_hashes = [hash_coordination_lineage(reference) for reference in manifest.lineage_references]
    continuity_hashes = [
        hash_coordination_continuity(reference) for reference in manifest.continuity_references
    ]
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if lineage["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if manifest_hash == repeated_hash == reordered_hash else 1,
            0 if coordination_manifests_equal(manifest, repeated) else 1,
        ]
    )
    status = (
        V4_2_COORDINATION_MANIFEST_STATUS_STABLE
        if validation_error_count == 0
        else V4_2_COORDINATION_MANIFEST_STATUS_BLOCKED
    )
    exported_dependency_order = [item["dependency_id"] for item in exported["dependency_references"]]
    expected_dependency_order = [
        item["dependency_id"]
        for item in sorted(
            exported["dependency_references"],
            key=lambda item: (item["deterministic_order"], item["dependency_id"]),
        )
    ]
    report = {
        "schema_version": V4_2_COORDINATION_MANIFEST_REPORT_SCHEMA_VERSION,
        "generated_at": V4_2_COORDINATION_MANIFEST_GENERATED_AT,
        "phase_id": V4_2_COORDINATION_MANIFEST_PHASE_ID,
        "phase_name": "v4.2_phase_1_refresh_coordination_manifest_foundations",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh coordination governance intelligence foundations without execution behavior",
        "coordination_mode": "descriptive_only_non_executable",
        "foundation_status": status,
        "manifest_counts": {
            "identity_count": 1,
            "metadata_count": 1,
            "dependency_count": len(manifest.dependency_references),
            "lineage_reference_count": len(manifest.lineage_references),
            "continuity_reference_count": len(manifest.continuity_references),
            "diagnostic_count": len(manifest.diagnostics),
            "prohibited_state_visibility_count": visibility["prohibited_state_visibility_count"],
            "unsupported_state_visibility_count": visibility["unsupported_state_visibility_count"],
            "dependency_state_counts": count_coordination_dependency_states(manifest.dependency_references),
        },
        "dependency_visibility": {
            "dependency_hashes": dependency_hashes,
            "unsupported_state_ids": diagnostics["unsupported_state_ids"],
            "blocked_coordination_ids": diagnostics["blocked_coordination_ids"],
            "stale_state_ids": diagnostics["stale_state_ids"],
            "prohibited_state_ids": diagnostics["prohibited_state_ids"],
            "dependency_visibility_valid": visibility["valid"],
        },
        "lineage_visibility": {
            "identity_key": coordination_manifest_identity_key(manifest),
            "lineage_hashes": lineage_hashes,
            "lineage_continuity": lineage,
        },
        "continuity_visibility": {
            "continuity_hashes": continuity_hashes,
            "continuity_validation": continuity,
            "replay_safe_evidence": continuity["replay_safe"],
            "rollback_safe_evidence": continuity["rollback_safe"],
            "provenance_safe_evidence": continuity["provenance_safe"],
            "lineage_safe_evidence": continuity["lineage_safe"],
        },
        "prohibited_state_visibility": {
            "prohibited_state_ids": diagnostics["prohibited_state_ids"],
            "prohibited_capability_visibility_count": visibility["prohibited_capability_visibility_count"],
            "blocked_reason_visibility_count": visibility["blocked_reason_visibility_count"],
            "prohibited_states_visible": visibility["prohibited_states_visible"],
            "prohibited_capabilities_visible": visibility["prohibited_capabilities_visible"],
        },
        "unsupported_state_visibility": {
            "unsupported_state_ids": diagnostics["unsupported_state_ids"],
            "unknown_state_ids": diagnostics["unknown_state_ids"],
            "blocked_coordination_ids": diagnostics["blocked_coordination_ids"],
            "stale_state_ids": diagnostics["stale_state_ids"],
            "unsupported_states_visible": visibility["unsupported_states_visible"],
            "unknown_states_visible": visibility["unknown_states_visible"],
            "blocked_states_visible": visibility["blocked_states_visible"],
            "stale_states_visible": visibility["stale_states_visible"],
        },
        "diagnostic_aggregation": {
            "diagnostic_categories": diagnostics["diagnostic_categories"],
            "diagnostic_count": diagnostics["diagnostic_count"],
            "fail_visible_diagnostic_count": diagnostics["fail_visible_diagnostic_count"],
            "fail_visible_warning_count": diagnostics["fail_visible_warning_count"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "remediation_absent": diagnostics["remediation_absent"],
            "authorization_absent": diagnostics["authorization_absent"],
            "approval_absent": diagnostics["approval_absent"],
            "execution_absent": diagnostics["execution_absent"],
        },
        "hashing_stability_evidence": {
            "stable": manifest_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_2_coordination_manifest_foundations",
            "manifest_hash": manifest_hash,
            "repeated_manifest_hash": repeated_hash,
            "reordered_manifest_hash": reordered_hash,
            "identity_hash": hash_coordination_manifest_identity(manifest.identity),
            "dependency_hashes": dependency_hashes,
            "lineage_hashes": lineage_hashes,
            "continuity_hashes": continuity_hashes,
        },
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_2_coordination_manifest_foundations",
            "payload_length": len(serialization_first),
            "deterministic_order_preserved": exported_dependency_order == expected_dependency_order,
            "unsupported_states_preserved": visibility["unsupported_state_visibility_count"] > 0,
            "prohibited_states_preserved": visibility["prohibited_state_visibility_count"] > 0,
            "blocked_states_preserved": visibility["blocked_state_visibility_count"] > 0,
            "stale_states_preserved": visibility["stale_state_visibility_count"] > 0,
            "unknown_states_preserved": visibility["unknown_state_visibility_count"] > 0,
        },
        "non_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_hashing_verified": manifest_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": coordination_manifests_equal(manifest, repeated),
            "deterministic_ordering_verified": exported_dependency_order == expected_dependency_order,
            "dependency_visibility_verified": visibility["valid"],
            "lineage_continuity_verified": lineage["valid"],
            "continuity_visibility_verified": continuity["valid"],
            "replay_safe_evidence_generated": continuity["replay_safe"],
            "rollback_safe_evidence_generated": continuity["rollback_safe"],
            "prohibited_state_visibility_verified": visibility["prohibited_states_visible"],
            "unsupported_state_visibility_verified": visibility["unsupported_states_visible"],
            "fail_visible_diagnostics_verified": diagnostics["fail_visible_diagnostic_count"] == len(manifest.diagnostics),
            "non_execution_enforcement_validated": non_execution["valid"],
            "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
            "refresh_execution_disabled": non_execution["refresh_execution_disabled"],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
        },
        "coordination_manifest": exported,
        "explicit_limitations": list(manifest.governance_visibility.explicit_limitations),
        "explicit_prohibitions": list(manifest.governance_visibility.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Coordination manifest JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_2_coordination_manifest_foundations_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
