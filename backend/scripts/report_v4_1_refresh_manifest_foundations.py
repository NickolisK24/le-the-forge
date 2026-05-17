"""Generate deterministic v4.1 refresh manifest foundation evidence."""

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

from operational_refresh.refresh_manifest_diagnostics import (  # noqa: E402
    build_refresh_manifest_diagnostics,
)
from operational_refresh.refresh_manifest_hashing import (  # noqa: E402
    deterministic_refresh_manifest_hash,
    hash_refresh_manifest,
    hash_refresh_manifest_continuity,
    hash_refresh_manifest_diagnostics,
    hash_refresh_manifest_identity,
)
from operational_refresh.refresh_manifest_integrity import (  # noqa: E402
    refresh_manifest_identity_normalization_report,
    refresh_manifests_equal,
    validate_refresh_manifest_integrity,
    validate_refresh_manifest_lineage_continuity,
    validate_refresh_manifest_non_execution,
    validate_refresh_manifest_provenance_continuity,
)
from operational_refresh.refresh_manifest_models import (  # noqa: E402
    V4_1_REFRESH_MANIFEST_DIAGNOSTICS_SCHEMA_VERSION,
    V4_1_REFRESH_MANIFEST_GENERATED_AT,
    V4_1_REFRESH_MANIFEST_PHASE_ID,
    V4_1_REFRESH_MANIFEST_PURPOSE,
    V4_1_REFRESH_MANIFEST_REPORT_SCHEMA_VERSION,
    V4_1_REFRESH_MANIFEST_STATUS_BLOCKED,
    V4_1_REFRESH_MANIFEST_STATUS_STABLE,
    default_refresh_manifest,
)
from operational_refresh.refresh_manifest_serialization import (  # noqa: E402
    export_refresh_manifest,
    serialize_refresh_manifest,
)
from operational_refresh.refresh_manifest_visibility import (  # noqa: E402
    count_refresh_manifest_states,
    validate_refresh_manifest_visibility,
)


REPORT_PATH = Path("docs/generated/v4_1_refresh_manifest_foundations_report.json")
DIAGNOSTICS_REPORT_PATH = Path("docs/generated/v4_1_refresh_manifest_diagnostics_report.json")


def _reordered_refresh_manifest():
    manifest = default_refresh_manifest()
    return replace(
        manifest,
        states=tuple(reversed(manifest.states)),
        source_lineage=tuple(reversed(manifest.source_lineage)),
        extraction_lineage=tuple(reversed(manifest.extraction_lineage)),
        patch_lineage=tuple(reversed(manifest.patch_lineage)),
        schema_version_visibility=tuple(reversed(manifest.schema_version_visibility)),
        dependency_visibility=tuple(reversed(manifest.dependency_visibility)),
        trust_visibility=tuple(reversed(manifest.trust_visibility)),
        validation_visibility=tuple(reversed(manifest.validation_visibility)),
        prohibited_domain_visibility=tuple(reversed(manifest.prohibited_domain_visibility)),
        unsupported_state_visibility=tuple(reversed(manifest.unsupported_state_visibility)),
        diagnostics_visibility=tuple(reversed(manifest.diagnostics_visibility)),
    )


def build_v4_1_refresh_manifest_foundations_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    manifest = default_refresh_manifest()
    repeated_manifest = default_refresh_manifest()
    reordered_manifest = _reordered_refresh_manifest()
    exported = export_refresh_manifest(manifest)
    visibility = validate_refresh_manifest_visibility(manifest)
    provenance_validation = validate_refresh_manifest_provenance_continuity(manifest)
    lineage_validation = validate_refresh_manifest_lineage_continuity(manifest)
    non_execution = validate_refresh_manifest_non_execution(manifest)
    integrity = validate_refresh_manifest_integrity(manifest)
    diagnostics = build_refresh_manifest_diagnostics(manifest)
    serialization_first = serialize_refresh_manifest(manifest)
    serialization_second = serialize_refresh_manifest(repeated_manifest)
    serialization_reordered = serialize_refresh_manifest(reordered_manifest)
    manifest_hash = hash_refresh_manifest(manifest)
    repeated_hash = hash_refresh_manifest(repeated_manifest)
    reordered_hash = hash_refresh_manifest(reordered_manifest)
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if provenance_validation["valid"] else 1,
            0 if lineage_validation["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if integrity["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if manifest_hash == repeated_hash == reordered_hash else 1,
            0 if refresh_manifests_equal(manifest, repeated_manifest) else 1,
        ]
    )
    status = (
        V4_1_REFRESH_MANIFEST_STATUS_STABLE
        if validation_error_count == 0
        else V4_1_REFRESH_MANIFEST_STATUS_BLOCKED
    )
    state_counts = count_refresh_manifest_states(manifest.states)
    exported_state_order = [item["state_id"] for item in exported["states"]]
    expected_state_order = [
        item["state_id"] for item in sorted(exported["states"], key=lambda item: (item["deterministic_order"], item["state_id"]))
    ]
    report = {
        "schema_version": V4_1_REFRESH_MANIFEST_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_MANIFEST_GENERATED_AT,
        "phase_id": V4_1_REFRESH_MANIFEST_PHASE_ID,
        "phase_name": "v4.1_phase_1_refresh_manifest_foundations",
        "repo_root": str(root),
        "architectural_purpose": "deterministic operational refresh governance intelligence foundations without execution behavior",
        "refresh_governance_mode": "descriptive_only",
        "foundation_status": status,
        "manifest_model_counts": {
            "identity_count": 1,
            "state_count": len(manifest.states),
            "source_lineage_count": len(manifest.source_lineage),
            "extraction_lineage_count": len(manifest.extraction_lineage),
            "patch_lineage_count": len(manifest.patch_lineage),
            "schema_version_visibility_count": len(manifest.schema_version_visibility),
            "dependency_visibility_count": len(manifest.dependency_visibility),
            "trust_visibility_count": len(manifest.trust_visibility),
            "validation_visibility_count": len(manifest.validation_visibility),
            "prohibited_domain_visibility_count": len(manifest.prohibited_domain_visibility),
            "unsupported_state_visibility_count": len(manifest.unsupported_state_visibility),
            "diagnostics_visibility_count": len(manifest.diagnostics_visibility),
            "state_counts": state_counts,
        },
        "lineage_continuity_visibility": lineage_validation,
        "provenance_continuity_visibility": provenance_validation,
        "fail_visible_visibility": {
            "fail_visible_refresh_manifest_state_count": visibility["fail_visible_refresh_manifest_state_count"],
            "unsupported_state_visibility_count": visibility["unsupported_state_visibility_count"],
            "unknown_state_visibility_count": visibility["unknown_state_visibility_count"],
            "blocked_state_visibility_count": visibility["blocked_state_visibility_count"],
            "prohibited_state_visibility_count": visibility["prohibited_state_visibility_count"],
            "stale_state_visibility_count": visibility["stale_state_visibility_count"],
            "prohibited_domain_visibility_count": visibility["prohibited_domain_visibility_count"],
            "visible_blocked_reason_count": visibility["visible_blocked_reason_count"],
            "dependency_warning_visibility_count": visibility["dependency_warning_visibility_count"],
            "trust_warning_visibility_count": visibility["trust_warning_visibility_count"],
            "validation_warning_visibility_count": visibility["validation_warning_visibility_count"],
            "diagnostics_warning_visibility_count": visibility["diagnostics_warning_visibility_count"],
            "unsupported_states_visible": visibility["unsupported_states_visible"],
            "unknown_states_visible": visibility["unknown_states_visible"],
            "blocked_states_visible": visibility["blocked_states_visible"],
            "prohibited_states_visible": visibility["prohibited_states_visible"],
            "stale_states_visible": visibility["stale_states_visible"],
            "prohibited_domains_visible": visibility["prohibited_domains_visible"],
            "visibility_is_descriptive_only": visibility["visibility_is_descriptive_only"],
        },
        "deterministic_serialization_verification": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_1_refresh_manifest_foundations",
            "payload_length": len(serialization_first),
            "deterministic_order_preserved": exported_state_order == expected_state_order,
            "unsupported_states_preserved": visibility["unsupported_state_visibility_count"] > 0,
            "prohibited_states_preserved": visibility["prohibited_state_visibility_count"] > 0,
            "unknown_states_preserved": visibility["unknown_state_visibility_count"] > 0,
            "blocked_states_preserved": visibility["blocked_state_visibility_count"] > 0,
            "stale_states_preserved": visibility["stale_state_visibility_count"] > 0,
            "hidden_omission_enabled": False,
        },
        "deterministic_hashing_verification": {
            "stable": manifest_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_1_refresh_manifest_foundations",
            "manifest_hash": manifest_hash,
            "identity_hash": hash_refresh_manifest_identity(manifest.identity),
            "continuity_hash": hash_refresh_manifest_continuity(manifest.continuity_metadata),
            "diagnostics_hashes": [
                hash_refresh_manifest_diagnostics(record) for record in manifest.diagnostics_visibility
            ],
        },
        "deterministic_equality_verification": {
            "dataclass_equality_stable": manifest == repeated_manifest,
            "dataclass_hash_stable": hash(manifest) == hash(repeated_manifest),
            "serialized_equality_stable": refresh_manifests_equal(manifest, repeated_manifest),
            "reordered_serialized_equality_stable": refresh_manifests_equal(manifest, reordered_manifest),
        },
        "refresh_manifest_identity_normalization": refresh_manifest_identity_normalization_report(manifest.identity),
        "diagnostics_visibility": diagnostics,
        "integrity_validation": integrity,
        "non_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "deterministic_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_hashing_verified": manifest_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": refresh_manifests_equal(manifest, repeated_manifest),
            "deterministic_visibility_verified": visibility["valid"],
            "lineage_continuity_verified": lineage_validation["valid"],
            "provenance_continuity_verified": provenance_validation["valid"],
            "replay_continuity_verified": lineage_validation["replay_safe"],
            "rollback_continuity_verified": lineage_validation["rollback_safe"],
            "fail_visible_unsupported_state_validation": visibility["unsupported_states_visible"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
            "descriptive_only_verified": manifest.descriptive_only and manifest.non_executable,
        },
        "refresh_manifest": exported,
        "explicit_limitations": list(manifest.governance_visibility.explicit_limitations),
        "explicit_prohibitions": list(manifest.governance_visibility.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_manifest_diagnostics_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    manifest = default_refresh_manifest()
    diagnostics = build_refresh_manifest_diagnostics(manifest)
    non_execution = validate_refresh_manifest_non_execution(manifest)
    status = (
        V4_1_REFRESH_MANIFEST_STATUS_STABLE
        if diagnostics["visibility_validation"]["valid"] and diagnostics["enabled_capability_count"] == 0
        else V4_1_REFRESH_MANIFEST_STATUS_BLOCKED
    )
    report = {
        "schema_version": V4_1_REFRESH_MANIFEST_DIAGNOSTICS_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_MANIFEST_GENERATED_AT,
        "phase_id": V4_1_REFRESH_MANIFEST_PHASE_ID,
        "phase_name": "v4.1_phase_1_refresh_manifest_diagnostics",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh manifest diagnostics visibility without remediation or execution",
        "diagnostics_mode": "fail_visible_descriptive_only",
        "foundation_status": status,
        "manifest_hash": diagnostics["manifest_hash"],
        "diagnostics_hashes": diagnostics["diagnostics_hashes"],
        "visibility_validation": diagnostics["visibility_validation"],
        "enabled_capability_count": diagnostics["enabled_capability_count"],
        "enabled_capability_flags": diagnostics["enabled_capability_flags"],
        "unsupported_state_ids": diagnostics["unsupported_state_ids"],
        "unknown_state_ids": diagnostics["unknown_state_ids"],
        "blocked_state_ids": diagnostics["blocked_state_ids"],
        "prohibited_state_ids": diagnostics["prohibited_state_ids"],
        "stale_state_ids": diagnostics["stale_state_ids"],
        "prohibited_domains": diagnostics["prohibited_domains"],
        "warning_visibility": diagnostics["warning_visibility"],
        "blocker_visibility": diagnostics["blocker_visibility"],
        "fail_visible_warning_count": diagnostics["fail_visible_warning_count"],
        "non_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "diagnostics_visible": diagnostics["diagnostics_visible"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "remediation_absent": diagnostics["remediation_absent"],
            "silent_fallback_absent": diagnostics["silent_fallback_absent"],
            "automatic_recovery_absent": diagnostics["automatic_recovery_absent"],
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
        },
        "explicit_limitations": list(manifest.governance_visibility.explicit_limitations),
        "explicit_prohibitions": list(manifest.governance_visibility.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_refresh_manifest_hash(payload)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Refresh manifest JSON report output path")
    parser.add_argument(
        "--diagnostics-output",
        default=str(DIAGNOSTICS_REPORT_PATH),
        help="Refresh manifest diagnostics JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    diagnostics_output_path = Path(args.diagnostics_output)
    report = build_v4_1_refresh_manifest_foundations_report()
    diagnostics_report = build_v4_1_refresh_manifest_diagnostics_report()
    write_report(report, output_path)
    write_report(diagnostics_report, diagnostics_output_path)
    print(f"wrote {output_path}")
    print(f"wrote {diagnostics_output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"diagnostics_status={diagnostics_report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    print(f"deterministic_diagnostics_report_hash={diagnostics_report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
