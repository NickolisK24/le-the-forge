"""Generate deterministic v4.3 orchestration manifest foundation evidence."""

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

from orchestration_governance.orchestration_manifest_diagnostics import (  # noqa: E402
    build_orchestration_manifest_diagnostics,
    count_orchestration_capability_states,
    orchestration_manifest_identity_key,
    orchestration_manifests_equal,
    validate_orchestration_continuity_metadata,
    validate_orchestration_explainability,
    validate_orchestration_manifest_non_execution,
    validate_orchestration_manifest_visibility,
)
from orchestration_governance.orchestration_manifest_hashing import (  # noqa: E402
    deterministic_orchestration_manifest_hash,
    hash_orchestration_boundary_visibility,
    hash_orchestration_capability_visibility,
    hash_orchestration_continuity_metadata,
    hash_orchestration_explainability_summary,
    hash_orchestration_manifest,
    hash_orchestration_manifest_identity,
)
from orchestration_governance.orchestration_manifest_models import (  # noqa: E402
    EXPLICIT_ORCHESTRATION_MANIFEST_LIMITATIONS,
    EXPLICIT_ORCHESTRATION_MANIFEST_PROHIBITIONS,
    V4_3_ORCHESTRATION_MANIFEST_GENERATED_AT,
    V4_3_ORCHESTRATION_MANIFEST_PHASE_ID,
    V4_3_ORCHESTRATION_MANIFEST_REPORT_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_MANIFEST_STATUS_BLOCKED,
    V4_3_ORCHESTRATION_MANIFEST_STATUS_STABLE,
    default_orchestration_manifest,
)
from orchestration_governance.orchestration_manifest_serialization import (  # noqa: E402
    export_orchestration_manifest,
    serialize_orchestration_manifest,
)


REPORT_PATH = Path("docs/generated/v4_3_orchestration_manifest_foundations_report.json")


def _reordered_orchestration_manifest():
    manifest = default_orchestration_manifest()
    return replace(
        manifest,
        capability_visibility=tuple(reversed(manifest.capability_visibility)),
        boundary_visibility=tuple(reversed(manifest.boundary_visibility)),
        continuity_metadata=tuple(reversed(manifest.continuity_metadata)),
        diagnostics=tuple(reversed(manifest.diagnostics)),
        explainability_summaries=tuple(reversed(manifest.explainability_summaries)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_orchestration_manifest_hash(payload)


def build_v4_3_orchestration_manifest_foundations_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    manifest = default_orchestration_manifest()
    repeated = default_orchestration_manifest()
    reordered = _reordered_orchestration_manifest()
    exported = export_orchestration_manifest(manifest)
    visibility = validate_orchestration_manifest_visibility(manifest)
    continuity = validate_orchestration_continuity_metadata(manifest)
    explainability = validate_orchestration_explainability(manifest)
    non_execution = validate_orchestration_manifest_non_execution(manifest)
    diagnostics = build_orchestration_manifest_diagnostics(manifest)
    serialization_first = serialize_orchestration_manifest(manifest)
    serialization_second = serialize_orchestration_manifest(repeated)
    serialization_reordered = serialize_orchestration_manifest(reordered)
    manifest_hash = hash_orchestration_manifest(manifest)
    repeated_hash = hash_orchestration_manifest(repeated)
    reordered_hash = hash_orchestration_manifest(reordered)
    capability_hashes = [
        hash_orchestration_capability_visibility(visibility_record)
        for visibility_record in manifest.capability_visibility
    ]
    boundary_hashes = [
        hash_orchestration_boundary_visibility(visibility_record)
        for visibility_record in manifest.boundary_visibility
    ]
    continuity_hashes = [
        hash_orchestration_continuity_metadata(metadata) for metadata in manifest.continuity_metadata
    ]
    explainability_hashes = [
        hash_orchestration_explainability_summary(summary) for summary in manifest.explainability_summaries
    ]
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if explainability["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if manifest_hash == repeated_hash == reordered_hash else 1,
            0 if orchestration_manifests_equal(manifest, repeated) else 1,
        ]
    )
    status = (
        V4_3_ORCHESTRATION_MANIFEST_STATUS_STABLE
        if validation_error_count == 0
        else V4_3_ORCHESTRATION_MANIFEST_STATUS_BLOCKED
    )
    exported_capability_order = [item["capability_id"] for item in exported["capability_visibility"]]
    expected_capability_order = [
        item["capability_id"]
        for item in sorted(
            exported["capability_visibility"],
            key=lambda item: (item["deterministic_order"], item["capability_id"]),
        )
    ]
    deterministic_ordering_verified = exported_capability_order == expected_capability_order
    report = {
        "schema_version": V4_3_ORCHESTRATION_MANIFEST_REPORT_SCHEMA_VERSION,
        "generated_at": V4_3_ORCHESTRATION_MANIFEST_GENERATED_AT,
        "phase_id": V4_3_ORCHESTRATION_MANIFEST_PHASE_ID,
        "phase_name": "v4.3_phase_1_governance_safe_orchestration_manifest_foundations",
        "repo_root": str(root),
        "architectural_purpose": "deterministic governance-safe orchestration modeling without execution behavior",
        "orchestration_mode": "descriptive_only_non_executable",
        "foundation_status": status,
        "manifest_counts": {
            "identity_count": 1,
            "metadata_count": 1,
            "capability_visibility_count": len(manifest.capability_visibility),
            "boundary_visibility_count": len(manifest.boundary_visibility),
            "continuity_metadata_count": len(manifest.continuity_metadata),
            "diagnostic_count": len(manifest.diagnostics),
            "explainability_summary_count": len(manifest.explainability_summaries),
            "capability_state_counts": count_orchestration_capability_states(manifest.capability_visibility),
            "prohibited_state_count": visibility["prohibited_state_visibility_count"],
            "unsupported_state_count": visibility["unsupported_state_visibility_count"],
            "blocked_state_count": visibility["blocked_state_visibility_count"],
            "missing_metadata_state_count": visibility["missing_metadata_visibility_count"],
            "conflicting_metadata_state_count": visibility["conflicting_metadata_visibility_count"],
            "stale_metadata_state_count": visibility["stale_metadata_visibility_count"],
            "unknown_state_count": visibility["unknown_state_visibility_count"],
        },
        "capability_visibility": {
            "capability_hashes": capability_hashes,
            "unsupported_state_ids": diagnostics["unsupported_state_ids"],
            "prohibited_state_ids": diagnostics["prohibited_state_ids"],
            "blocked_state_ids": diagnostics["blocked_state_ids"],
            "missing_metadata_ids": diagnostics["missing_metadata_ids"],
            "conflicting_metadata_ids": diagnostics["conflicting_metadata_ids"],
            "stale_metadata_ids": diagnostics["stale_metadata_ids"],
            "unknown_state_ids": diagnostics["unknown_state_ids"],
            "capability_visibility_valid": visibility["valid"],
        },
        "governance_boundary_visibility": {
            "boundary_hashes": boundary_hashes,
            "boundary_count": len(manifest.boundary_visibility),
            "non_execution_boundary_visible": all(
                boundary.non_execution_boundary and boundary.boundary_visible
                for boundary in manifest.boundary_visibility
            ),
            "governance_boundary_guarantees": {
                "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
                "runtime_execution_disabled": non_execution["runtime_execution_disabled"],
                "routing_execution_disabled": non_execution["routing_execution_disabled"],
                "scheduling_execution_disabled": non_execution["scheduling_execution_disabled"],
                "sequencing_execution_disabled": non_execution["sequencing_execution_disabled"],
                "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
                "orchestration_remediation_disabled": non_execution["orchestration_remediation_disabled"],
                "orchestration_repair_disabled": non_execution["orchestration_repair_disabled"],
                "orchestration_inference_disabled": non_execution["orchestration_inference_disabled"],
                "orchestration_authorization_disabled": non_execution["orchestration_authorization_disabled"],
                "readiness_approval_disabled": non_execution["readiness_approval_disabled"],
                "planner_integration_disabled": non_execution["planner_integration_disabled"],
                "production_consumption_disabled": non_execution["production_consumption_disabled"],
                "automatic_correction_disabled": non_execution["automatic_correction_disabled"],
                "automatic_rollback_disabled": non_execution["automatic_rollback_disabled"],
                "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
                "operational_state_mutation_disabled": non_execution["operational_state_mutation_disabled"],
                "recommendation_disabled": non_execution["recommendation_disabled"],
                "ranking_disabled": non_execution["ranking_disabled"],
                "scoring_disabled": non_execution["scoring_disabled"],
                "selection_disabled": non_execution["selection_disabled"],
                "orchestration_engine_absent": non_execution["orchestration_engine_absent"],
                "state_machine_execution_absent": non_execution["state_machine_execution_absent"],
            },
        },
        "continuity_visibility": {
            "identity_key": orchestration_manifest_identity_key(manifest),
            "continuity_hashes": continuity_hashes,
            "continuity_validation": continuity,
            "replay_safe_evidence": continuity["replay_safe"],
            "rollback_safe_evidence": continuity["rollback_safe"],
            "provenance_continuity_preserved": continuity["provenance_continuity_preserved"],
            "lineage_continuity_preserved": continuity["lineage_continuity_preserved"],
            "explainability_continuity_preserved": continuity["explainability_continuity_preserved"],
        },
        "explainability_visibility": {
            "explainability_hashes": explainability_hashes,
            "explainability_validation": explainability,
            "blocked_explainability_visible": "blocked_state" in explainability["explainability_categories"],
            "unsupported_explainability_visible": "unsupported_state" in explainability["explainability_categories"],
            "prohibited_explainability_visible": "prohibited_state" in explainability["explainability_categories"],
            "capability_unavailable_explainability_visible": (
                "capability_unavailable" in explainability["explainability_categories"]
            ),
            "governance_boundary_explainability_visible": (
                "governance_boundary" in explainability["explainability_categories"]
            ),
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
            "blocked_state_ids": diagnostics["blocked_state_ids"],
            "missing_metadata_ids": diagnostics["missing_metadata_ids"],
            "conflicting_metadata_ids": diagnostics["conflicting_metadata_ids"],
            "stale_metadata_ids": diagnostics["stale_metadata_ids"],
            "unknown_state_ids": diagnostics["unknown_state_ids"],
            "unsupported_states_visible": visibility["unsupported_states_visible"],
            "blocked_states_visible": visibility["blocked_states_visible"],
            "missing_metadata_visible": visibility["missing_metadata_visible"],
            "conflicting_metadata_visible": visibility["conflicting_metadata_visible"],
            "stale_metadata_visible": visibility["stale_metadata_visible"],
            "unknown_states_visible": visibility["unknown_states_visible"],
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
            "selection_systems_absent": diagnostics["selection_systems_absent"],
        },
        "hashing_stability_evidence": {
            "stable": manifest_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_3_orchestration_manifest_foundations",
            "manifest_hash": manifest_hash,
            "repeated_manifest_hash": repeated_hash,
            "reordered_manifest_hash": reordered_hash,
            "identity_hash": hash_orchestration_manifest_identity(manifest.identity),
            "capability_hashes": capability_hashes,
            "boundary_hashes": boundary_hashes,
            "continuity_hashes": continuity_hashes,
            "explainability_hashes": explainability_hashes,
        },
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_3_orchestration_manifest_foundations",
            "payload_length": len(serialization_first),
            "deterministic_order_preserved": deterministic_ordering_verified,
            "unsupported_states_preserved": visibility["unsupported_state_visibility_count"] > 0,
            "prohibited_states_preserved": visibility["prohibited_state_visibility_count"] > 0,
            "blocked_states_preserved": visibility["blocked_state_visibility_count"] > 0,
            "missing_metadata_states_preserved": visibility["missing_metadata_visibility_count"] > 0,
            "conflicting_metadata_states_preserved": visibility["conflicting_metadata_visibility_count"] > 0,
            "stale_metadata_states_preserved": visibility["stale_metadata_visibility_count"] > 0,
            "unknown_states_preserved": visibility["unknown_state_visibility_count"] > 0,
        },
        "non_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_hashing_verified": manifest_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": orchestration_manifests_equal(manifest, repeated),
            "deterministic_ordering_verified": deterministic_ordering_verified,
            "capability_visibility_verified": visibility["valid"],
            "continuity_visibility_verified": continuity["valid"],
            "explainability_visibility_verified": explainability["valid"],
            "replay_safe_evidence_generated": continuity["replay_safe"],
            "rollback_safe_evidence_generated": continuity["rollback_safe"],
            "provenance_continuity_preserved": continuity["provenance_continuity_preserved"],
            "lineage_continuity_preserved": continuity["lineage_continuity_preserved"],
            "prohibited_state_visibility_verified": visibility["prohibited_states_visible"],
            "unsupported_state_visibility_verified": visibility["unsupported_states_visible"],
            "blocked_state_visibility_verified": visibility["blocked_states_visible"],
            "missing_metadata_visibility_verified": visibility["missing_metadata_visible"],
            "conflicting_metadata_visibility_verified": visibility["conflicting_metadata_visible"],
            "stale_metadata_visibility_verified": visibility["stale_metadata_visible"],
            "fail_visible_diagnostics_verified": diagnostics["fail_visible_diagnostic_count"] == len(manifest.diagnostics),
            "non_execution_enforcement_validated": non_execution["valid"],
            "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
            "runtime_execution_disabled": non_execution["runtime_execution_disabled"],
            "routing_execution_disabled": non_execution["routing_execution_disabled"],
            "scheduling_execution_disabled": non_execution["scheduling_execution_disabled"],
            "sequencing_execution_disabled": non_execution["sequencing_execution_disabled"],
            "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
            "operational_state_mutation_disabled": non_execution["operational_state_mutation_disabled"],
            "orchestration_engine_absent": non_execution["orchestration_engine_absent"],
            "state_machine_execution_absent": non_execution["state_machine_execution_absent"],
        },
        "orchestration_manifest": exported,
        "explicit_limitations": list(EXPLICIT_ORCHESTRATION_MANIFEST_LIMITATIONS),
        "explicit_prohibitions": list(EXPLICIT_ORCHESTRATION_MANIFEST_PROHIBITIONS),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Orchestration manifest JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_3_orchestration_manifest_foundations_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
