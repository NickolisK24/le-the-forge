"""Generate deterministic v4.0 trusted bundle lifecycle governance evidence."""

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

from operational_lifecycle.bundle_governance_audit import (  # noqa: E402
    audit_trusted_bundle_lifecycle_governance,
)
from operational_lifecycle.bundle_governance_hashing import deterministic_bundle_governance_hash  # noqa: E402
from operational_lifecycle.bundle_governance_models import (  # noqa: E402
    BUNDLE_SUPPORT_STATUS_UNSUPPORTED,
    BUNDLE_TRUST_STATUS_UNKNOWN,
    BUNDLE_VALIDATION_STATUS_STALE,
    TRUSTED_BUNDLE_GOVERNANCE_FINDING_TYPES,
    V4_0_TRUSTED_BUNDLE_GOVERNANCE_GENERATED_AT,
    V4_0_TRUSTED_BUNDLE_GOVERNANCE_PHASE_ID,
    V4_0_TRUSTED_BUNDLE_GOVERNANCE_STATUS_BLOCKED,
    V4_0_TRUSTED_BUNDLE_GOVERNANCE_STATUS_STABLE,
    TrustedBundleIdentity,
    TrustedBundleStatus,
    TrustedBundleSupportStatus,
    TrustedBundleValidationStatus,
)
from operational_lifecycle.bundle_governance_serialization import (  # noqa: E402
    export_trusted_bundle_governance_report,
)
from operational_lifecycle.bundle_governance_visibility import (  # noqa: E402
    count_governance_finding_types,
    count_governance_severities,
    validate_trusted_bundle_governance_visibility,
)
from operational_lifecycle.lifecycle_drift_detection import detect_lifecycle_drift  # noqa: E402
from scripts.report_v4_0_patch_lifecycle_drift_foundations import (  # noqa: E402
    build_representative_lifecycle_drift_pair,
)


REPORT_PATH = Path("docs/generated/v4_0_trusted_bundle_lifecycle_governance_report.json")


def build_representative_trusted_bundle_governance_inputs():
    lifecycle_foundation, target_lifecycle = build_representative_lifecycle_drift_pair()
    drift_report = detect_lifecycle_drift(lifecycle_foundation, target_lifecycle)
    bundle_identity = TrustedBundleIdentity(
        bundle_id="v4_0_patch_lifecycle_drift_trusted_bundle",
        patch_version=target_lifecycle.patch_identity.patch_version,
        extraction_version=target_lifecycle.patch_identity.extraction_version,
        schema_version=target_lifecycle.patch_identity.schema_version,
        generated_timestamp=V4_0_TRUSTED_BUNDLE_GOVERNANCE_GENERATED_AT,
        bundle_hash="sha256:v4_0_patch_lifecycle_drift_bundle",
        manifest_hash="sha256:v4_0_patch_lifecycle_drift_manifest",
        metadata_hash="sha256:v4_0_patch_lifecycle_drift_metadata",
    )
    trust_status = TrustedBundleStatus(
        status=BUNDLE_TRUST_STATUS_UNKNOWN,
        status_reference="v4_0_bundle_trust_status_unknown",
        explanation="Trust state is unknown and remains descriptive evidence.",
    )
    validation_status = TrustedBundleValidationStatus(
        status=BUNDLE_VALIDATION_STATUS_STALE,
        status_reference="v4_0_bundle_validation_status_stale",
        explanation="Validation state is stale and not automatically fixed.",
    )
    support_status = TrustedBundleSupportStatus(
        status=BUNDLE_SUPPORT_STATUS_UNSUPPORTED,
        status_reference="v4_0_bundle_support_status_unsupported",
        explanation="Bundle support state is unsupported and not implicitly upgraded.",
    )
    blocked_domains = (
        "blocked_schema_domain",
        "prohibited_production_consumption",
        "unknown_bundle_state_domain",
        "unsupported_modifier_domain",
    )
    return bundle_identity, trust_status, validation_status, support_status, blocked_domains, lifecycle_foundation, drift_report


def build_v4_0_trusted_bundle_lifecycle_governance_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    (
        bundle_identity,
        trust_status,
        validation_status,
        support_status,
        blocked_domains,
        lifecycle_foundation,
        drift_report,
    ) = build_representative_trusted_bundle_governance_inputs()
    governance_report = audit_trusted_bundle_lifecycle_governance(
        bundle_identity=bundle_identity,
        trust_status=trust_status,
        validation_status=validation_status,
        support_status=support_status,
        blocked_domains=blocked_domains,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
    )
    exported = export_trusted_bundle_governance_report(governance_report)
    visibility_validation = validate_trusted_bundle_governance_visibility(governance_report)
    finding_type_counts = count_governance_finding_types(governance_report.findings)
    severity_counts = count_governance_severities(governance_report.findings)
    validation_error_count = 0 if visibility_validation["valid"] else 1
    status = (
        V4_0_TRUSTED_BUNDLE_GOVERNANCE_STATUS_STABLE
        if validation_error_count == 0
        else V4_0_TRUSTED_BUNDLE_GOVERNANCE_STATUS_BLOCKED
    )
    report = {
        "schema_version": "v4_0.trusted_bundle_lifecycle_governance_report.1",
        "generated_at": V4_0_TRUSTED_BUNDLE_GOVERNANCE_GENERATED_AT,
        "phase_id": V4_0_TRUSTED_BUNDLE_GOVERNANCE_PHASE_ID,
        "phase_name": "v4.0_phase_3_trusted_bundle_lifecycle_governance",
        "repo_root": str(root),
        "architectural_purpose": "deterministic trusted bundle lifecycle governance without production consumption",
        "governance_mode": "descriptive_only",
        "foundation_status": status,
        "bundle_identity": exported["bundle_identity"],
        "lifecycle_identity": governance_report.lifecycle_identity,
        "drift_report_hash": governance_report.drift_report_hash,
        "trust_status": governance_report.trust_status,
        "validation_status": governance_report.validation_status,
        "support_status": governance_report.support_status,
        "blocked_domain_count": len(governance_report.blocked_domains),
        "blocked_domains": exported["blocked_domains"],
        "total_governance_findings": governance_report.finding_count,
        "finding_type_counts": finding_type_counts,
        "severity_counts": severity_counts,
        "unsupported_count": governance_report.unsupported_count,
        "prohibited_count": governance_report.prohibited_count,
        "blocked_count": governance_report.blocked_count,
        "unknown_count": governance_report.unknown_count,
        "warning_count": governance_report.warning_count,
        "replay_safety_status": governance_report.replay_safe,
        "rollback_safety_status": governance_report.rollback_safe,
        "provenance_safety_status": governance_report.provenance_safe,
        "lineage_safety_status": governance_report.lineage_safe,
        "production_consumption_authorization_status": governance_report.production_consumption_authorized,
        "deterministic_governance_report_hash": governance_report.deterministic_report_hash,
        "implemented_governance_finding_types": list(TRUSTED_BUNDLE_GOVERNANCE_FINDING_TYPES),
        "deterministic_guarantees": {
            "stable_finding_order": [finding["deterministic_key"] for finding in exported["findings"]]
            == sorted(finding["deterministic_key"] for finding in exported["findings"]),
            "bundle_identity_preserved": bool(exported["bundle_identity"]["bundle_id"]),
            "lifecycle_identity_preserved": bool(governance_report.lifecycle_identity),
            "drift_report_hash_preserved": bool(governance_report.drift_report_hash),
            "blocked_domains_preserved": len(exported["blocked_domains"]) == len(blocked_domains),
            "production_consumption_authorized_false": governance_report.production_consumption_authorized is False,
        },
        "fail_visible_guarantees": {
            "untrusted_or_unknown_status_visible": governance_report.unknown_count > 0,
            "unsupported_bundle_visible": governance_report.unsupported_count > 0,
            "prohibited_bundle_visible": governance_report.prohibited_count > 0,
            "blocked_bundle_domains_visible": governance_report.blocked_count > 0,
            "lifecycle_alignment_visible": finding_type_counts["lifecycle_alignment_visibility"] > 0,
            "drift_alignment_visible": finding_type_counts["drift_alignment_visibility"] > 0,
            "provenance_continuity_visible": finding_type_counts["provenance_continuity_visibility"] > 0,
            "lineage_continuity_visible": finding_type_counts["lineage_continuity_visibility"] > 0,
            "production_consumption_prohibition_visible": (
                finding_type_counts["production_consumption_prohibited"] > 0
            ),
        },
        "non_execution_guarantees": {
            "descriptive_only": governance_report.descriptive_only,
            "approval_absent": not governance_report.approval_enabled,
            "authorization_absent": not governance_report.authorization_enabled,
            "remediation_absent": not governance_report.remediation_enabled,
            "execution_absent": not governance_report.execution_enabled,
            "routing_absent": not governance_report.routing_enabled,
            "scheduling_absent": not governance_report.scheduling_enabled,
            "dispatch_absent": not governance_report.dispatch_enabled,
            "orchestration_execution_absent": not governance_report.orchestration_execution_enabled,
            "runtime_mutation_absent": not governance_report.runtime_mutation_enabled,
            "production_bundle_consumption_absent": not governance_report.production_bundle_consumption_enabled,
            "production_consumption_authorized": governance_report.production_consumption_authorized,
        },
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "total_governance_findings": governance_report.finding_count,
            "visibility_validation_passed": visibility_validation["valid"],
            "capability_enabled_count": visibility_validation["capability_enabled_count"],
            "replay_safe": governance_report.replay_safe,
            "rollback_safe": governance_report.rollback_safe,
            "provenance_safe": governance_report.provenance_safe,
            "lineage_safe": governance_report.lineage_safe,
            "production_consumption_authorized": governance_report.production_consumption_authorized,
        },
        "governance_report": exported,
        "explicit_limitations": [
            "v4.0 Phase 3 governs trusted bundle lifecycle evidence but does not approve bundles.",
            "v4.0 Phase 3 does not authorize production consumption.",
            "v4.0 Phase 3 does not load bundles into production planners.",
            "v4.0 Phase 3 does not deploy, remediate, execute, route, schedule, dispatch, or mutate bundles.",
        ],
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_bundle_governance_hash(payload)


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
    report = build_v4_0_trusted_bundle_lifecycle_governance_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    print(f"deterministic_governance_report_hash={report['deterministic_governance_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
