"""Deterministic lifecycle drift detection for v4.0 patch lifecycle foundations.

Detection compares immutable source and target lifecycle evidence. It does not
mutate either side, repair drift, remediate drift, authorize drift, execute
refresh behavior, or create callable operational workflows.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Iterable

from .lifecycle_drift_hashing import hash_lifecycle_drift_report
from .lifecycle_drift_models import (
    DRIFT_SEVERITY_BLOCKING,
    DRIFT_SEVERITY_PROHIBITED,
    DRIFT_SEVERITY_UNKNOWN,
    DRIFT_SEVERITY_WARNING,
    DRIFT_TYPE_EXTRACTION_VERSION,
    DRIFT_TYPE_GENERATION,
    DRIFT_TYPE_IDENTITY,
    DRIFT_TYPE_INTEGRITY_WARNING,
    DRIFT_TYPE_LINEAGE,
    DRIFT_TYPE_PATCH_VERSION,
    DRIFT_TYPE_PROVENANCE,
    DRIFT_TYPE_REPLAY_CONTINUITY,
    DRIFT_TYPE_ROLLBACK_CONTINUITY,
    DRIFT_TYPE_SCHEMA_VERSION,
    DRIFT_TYPE_STATE,
    DRIFT_TYPE_VISIBILITY,
    LifecycleDriftFinding,
    LifecycleDriftReport,
)
from .lifecycle_drift_visibility import (
    blocking_drift_count,
    prohibited_drift_count,
    unknown_drift_count,
    unsupported_drift_count,
)
from .lifecycle_identity import lifecycle_identity_key
from .lifecycle_models import PatchIdentity, PatchLifecycleFoundation
from .lifecycle_serialization import (
    export_lifecycle_lineage_record,
    export_lifecycle_provenance_record,
    export_lifecycle_state,
    export_lifecycle_visibility_record,
    stable_serialize,
)


def detect_lifecycle_drift(
    source: PatchLifecycleFoundation,
    target: PatchLifecycleFoundation,
) -> LifecycleDriftReport:
    findings = order_lifecycle_drift_findings(
        (
            *compare_patch_identity(source.patch_identity, target.patch_identity),
            *compare_provenance_records(source, target),
            *compare_lineage_records(source, target),
            *compare_lifecycle_states(source, target),
            *compare_visibility_records(source, target),
            *compare_replay_continuity(source, target),
            *compare_rollback_continuity(source, target),
        )
    )
    placeholder = LifecycleDriftReport(
        source_lifecycle_identity=lifecycle_identity_key(source.patch_identity),
        target_lifecycle_identity=lifecycle_identity_key(target.patch_identity),
        finding_count=len(findings),
        findings=findings,
        unsupported_drift_count=unsupported_drift_count(findings),
        prohibited_drift_count=prohibited_drift_count(findings),
        unknown_drift_count=unknown_drift_count(findings),
        blocking_drift_count=blocking_drift_count(findings),
        replay_safe=_lineage_replay_safe(source) and _lineage_replay_safe(target),
        rollback_safe=_lineage_rollback_safe(source) and _lineage_rollback_safe(target),
        provenance_safe=_provenance_safe(source) and _provenance_safe(target),
        deterministic_report_hash="pending",
    )
    return replace(placeholder, deterministic_report_hash=hash_lifecycle_drift_report(placeholder))


def compare_patch_identity(source: PatchIdentity, target: PatchIdentity) -> tuple[LifecycleDriftFinding, ...]:
    findings: list[LifecycleDriftFinding] = []
    source_key = lifecycle_identity_key(source)
    target_key = lifecycle_identity_key(target)
    if source_key != target_key:
        findings.append(
            build_lifecycle_drift_finding(
                drift_type=DRIFT_TYPE_IDENTITY,
                field_name="lifecycle_identity",
                before_value=source_key,
                after_value=target_key,
                source=source,
                target=target,
                severity=DRIFT_SEVERITY_WARNING,
                explanation="Source and target lifecycle identity keys differ.",
            )
        )
    field_specs = (
        ("patch_version", DRIFT_TYPE_PATCH_VERSION, DRIFT_SEVERITY_WARNING),
        ("extraction_version", DRIFT_TYPE_EXTRACTION_VERSION, DRIFT_SEVERITY_WARNING),
        ("schema_version", DRIFT_TYPE_SCHEMA_VERSION, DRIFT_SEVERITY_BLOCKING),
        ("lifecycle_generation", DRIFT_TYPE_GENERATION, DRIFT_SEVERITY_WARNING),
        ("provenance_reference", DRIFT_TYPE_PROVENANCE, DRIFT_SEVERITY_BLOCKING),
        ("lineage_reference", DRIFT_TYPE_LINEAGE, DRIFT_SEVERITY_BLOCKING),
    )
    for field_name, drift_type, severity in field_specs:
        findings.extend(compare_identity_field(source, target, field_name, drift_type, severity))
    return order_lifecycle_drift_findings(findings)


def compare_identity_field(
    source: PatchIdentity,
    target: PatchIdentity,
    field_name: str,
    drift_type: str,
    severity: str,
) -> tuple[LifecycleDriftFinding, ...]:
    before_value = getattr(source, field_name)
    after_value = getattr(target, field_name)
    if before_value == after_value:
        return ()
    return (
        build_lifecycle_drift_finding(
            drift_type=drift_type,
            field_name=field_name,
            before_value=before_value,
            after_value=after_value,
            source=source,
            target=target,
            severity=severity,
            explanation=f"Lifecycle identity field `{field_name}` changed.",
        ),
    )


def compare_lifecycle_states(
    source: PatchLifecycleFoundation,
    target: PatchLifecycleFoundation,
) -> tuple[LifecycleDriftFinding, ...]:
    source_states = _state_fingerprint(source)
    target_states = _state_fingerprint(target)
    if source_states == target_states:
        return ()
    return (
        build_lifecycle_drift_finding(
            drift_type=DRIFT_TYPE_STATE,
            field_name="lifecycle_states",
            before_value=source_states,
            after_value=target_states,
            source=source.patch_identity,
            target=target.patch_identity,
            severity=_state_drift_severity(source_states, target_states),
            explanation="Lifecycle state classifications or fail-visible state metadata changed.",
        ),
    )


def compare_provenance_records(
    source: PatchLifecycleFoundation,
    target: PatchLifecycleFoundation,
) -> tuple[LifecycleDriftFinding, ...]:
    source_provenance = _provenance_fingerprint(source)
    target_provenance = _provenance_fingerprint(target)
    if source_provenance == target_provenance:
        return ()
    return (
        build_lifecycle_drift_finding(
            drift_type=DRIFT_TYPE_PROVENANCE,
            field_name="provenance_records",
            before_value=source_provenance,
            after_value=target_provenance,
            source=source.patch_identity,
            target=target.patch_identity,
            severity=DRIFT_SEVERITY_BLOCKING,
            explanation="Lifecycle provenance records changed without inferring or correcting provenance.",
        ),
    )


def compare_lineage_records(
    source: PatchLifecycleFoundation,
    target: PatchLifecycleFoundation,
) -> tuple[LifecycleDriftFinding, ...]:
    source_lineage = _lineage_fingerprint(source)
    target_lineage = _lineage_fingerprint(target)
    if source_lineage == target_lineage:
        return ()
    return (
        build_lifecycle_drift_finding(
            drift_type=DRIFT_TYPE_LINEAGE,
            field_name="lineage_records",
            before_value=source_lineage,
            after_value=target_lineage,
            source=source.patch_identity,
            target=target.patch_identity,
            severity=DRIFT_SEVERITY_BLOCKING,
            explanation="Lifecycle lineage records changed without applying lifecycle transitions.",
        ),
    )


def compare_visibility_records(
    source: PatchLifecycleFoundation,
    target: PatchLifecycleFoundation,
) -> tuple[LifecycleDriftFinding, ...]:
    source_visibility = _visibility_fingerprint(source)
    target_visibility = _visibility_fingerprint(target)
    fields = (
        ("unsupported_state_visibility", DRIFT_TYPE_VISIBILITY, DRIFT_SEVERITY_WARNING),
        ("prohibited_state_visibility", DRIFT_TYPE_VISIBILITY, DRIFT_SEVERITY_PROHIBITED),
        ("unknown_state_visibility", DRIFT_TYPE_VISIBILITY, DRIFT_SEVERITY_UNKNOWN),
        ("integrity_warning_visibility", DRIFT_TYPE_INTEGRITY_WARNING, DRIFT_SEVERITY_WARNING),
        ("fail_visible_findings", DRIFT_TYPE_VISIBILITY, DRIFT_SEVERITY_WARNING),
        ("lifecycle_continuity_visibility", DRIFT_TYPE_VISIBILITY, DRIFT_SEVERITY_BLOCKING),
        ("lineage_gap_visibility", DRIFT_TYPE_LINEAGE, DRIFT_SEVERITY_BLOCKING),
    )
    findings: list[LifecycleDriftFinding] = []
    for field_name, drift_type, severity in fields:
        before_value = source_visibility.get(field_name, ())
        after_value = target_visibility.get(field_name, ())
        if before_value == after_value:
            continue
        findings.append(
            build_lifecycle_drift_finding(
                drift_type=drift_type,
                field_name=field_name,
                before_value=before_value,
                after_value=after_value,
                source=source.patch_identity,
                target=target.patch_identity,
                severity=severity,
                explanation=f"Lifecycle visibility field `{field_name}` changed.",
            )
        )
    return order_lifecycle_drift_findings(findings)


def compare_replay_continuity(
    source: PatchLifecycleFoundation,
    target: PatchLifecycleFoundation,
) -> tuple[LifecycleDriftFinding, ...]:
    source_replay = _continuity_references_containing(source, "replay")
    target_replay = _continuity_references_containing(target, "replay")
    if source_replay == target_replay:
        return ()
    return (
        build_lifecycle_drift_finding(
            drift_type=DRIFT_TYPE_REPLAY_CONTINUITY,
            field_name="replay_continuity_references",
            before_value=source_replay,
            after_value=target_replay,
            source=source.patch_identity,
            target=target.patch_identity,
            severity=DRIFT_SEVERITY_BLOCKING,
            explanation="Replay continuity references changed without executing replay behavior.",
        ),
    )


def compare_rollback_continuity(
    source: PatchLifecycleFoundation,
    target: PatchLifecycleFoundation,
) -> tuple[LifecycleDriftFinding, ...]:
    source_rollback = _rollback_references(source)
    target_rollback = _rollback_references(target)
    if source_rollback == target_rollback:
        return ()
    return (
        build_lifecycle_drift_finding(
            drift_type=DRIFT_TYPE_ROLLBACK_CONTINUITY,
            field_name="rollback_continuity_references",
            before_value=source_rollback,
            after_value=target_rollback,
            source=source.patch_identity,
            target=target.patch_identity,
            severity=DRIFT_SEVERITY_BLOCKING,
            explanation="Rollback continuity references changed without executing rollback behavior.",
        ),
    )


def build_lifecycle_drift_finding(
    *,
    drift_type: str,
    field_name: str,
    before_value: Any,
    after_value: Any,
    source: PatchIdentity,
    target: PatchIdentity,
    severity: str,
    explanation: str,
) -> LifecycleDriftFinding:
    deterministic_key = stable_serialize(
        {
            "drift_type": drift_type,
            "field_name": field_name,
            "source_identity": lifecycle_identity_key(source),
            "target_identity": lifecycle_identity_key(target),
            "before_value": before_value,
            "after_value": after_value,
        }
    )
    return LifecycleDriftFinding(
        drift_type=drift_type,
        severity=severity,
        before_value=before_value,
        after_value=after_value,
        provenance_reference=f"{source.provenance_reference}|{target.provenance_reference}",
        lineage_reference=f"{source.lineage_reference}|{target.lineage_reference}",
        visibility_reference="v4_0_patch_lifecycle_drift_visibility",
        explanation=explanation,
        deterministic_key=deterministic_key,
    )


def order_lifecycle_drift_findings(
    findings: Iterable[LifecycleDriftFinding],
) -> tuple[LifecycleDriftFinding, ...]:
    return tuple(sorted(tuple(findings), key=lambda item: item.deterministic_key))


def _state_fingerprint(foundation: PatchLifecycleFoundation) -> tuple[str, ...]:
    return tuple(
        stable_serialize(
            {
                "state_id": record["state_id"],
                "state": record["state"],
                "visibility_status": record["visibility_status"],
                "severity": record["severity"],
                "fail_visible": record["fail_visible"],
                "hidden": record["hidden"],
            }
        )
        for record in sorted(
            (export_lifecycle_state(state) for state in foundation.lifecycle_states),
            key=lambda item: (item["deterministic_order"], item["state_id"]),
        )
    )


def _visibility_fingerprint(foundation: PatchLifecycleFoundation) -> dict[str, tuple[str, ...]]:
    exported = [
        export_lifecycle_visibility_record(record)
        for record in sorted(
            foundation.visibility_records,
            key=lambda item: (item.deterministic_order, item.visibility_reference_id),
        )
    ]
    merged: dict[str, tuple[str, ...]] = {}
    for field_name in (
        "unsupported_state_visibility",
        "prohibited_state_visibility",
        "unknown_state_visibility",
        "integrity_warning_visibility",
        "fail_visible_findings",
        "lifecycle_continuity_visibility",
        "lineage_gap_visibility",
    ):
        merged[field_name] = tuple(sorted(item for record in exported for item in record[field_name]))
    return merged


def _provenance_fingerprint(foundation: PatchLifecycleFoundation) -> tuple[str, ...]:
    return tuple(
        stable_serialize(export_lifecycle_provenance_record(record))
        for record in sorted(foundation.provenance_records, key=lambda item: item.provenance_reference_id)
    )


def _lineage_fingerprint(foundation: PatchLifecycleFoundation) -> tuple[str, ...]:
    return tuple(
        stable_serialize(export_lifecycle_lineage_record(record))
        for record in sorted(foundation.lineage_records, key=lambda item: (item.deterministic_order, item.lineage_reference_id))
    )


def _continuity_references_containing(foundation: PatchLifecycleFoundation, token: str) -> tuple[str, ...]:
    needle = token.lower()
    references = []
    for record in foundation.lineage_records:
        references.extend(item for item in record.continuity_references if needle in item.lower())
    for record in foundation.provenance_records:
        references.extend(item for item in record.continuity_references if needle in item.lower())
    return tuple(sorted(references))


def _rollback_references(foundation: PatchLifecycleFoundation) -> tuple[str, ...]:
    references = []
    for record in foundation.lineage_records:
        references.extend(record.rollback_references)
        references.extend(item for item in record.continuity_references if "rollback" in item.lower())
    for record in foundation.provenance_records:
        references.extend(item for item in record.continuity_references if "rollback" in item.lower())
    return tuple(sorted(references))


def _lineage_replay_safe(foundation: PatchLifecycleFoundation) -> bool:
    return all(record.replay_safe and not record.execution_enabled for record in foundation.lineage_records)


def _lineage_rollback_safe(foundation: PatchLifecycleFoundation) -> bool:
    return all(record.rollback_safe and not record.execution_enabled for record in foundation.lineage_records)


def _provenance_safe(foundation: PatchLifecycleFoundation) -> bool:
    return all(
        record.provenance_preserved and record.no_inferred_provenance and not record.execution_enabled
        for record in foundation.provenance_records
    )


def _state_drift_severity(source_states: tuple[str, ...], target_states: tuple[str, ...]) -> str:
    combined = "|".join((*source_states, *target_states)).lower()
    if "prohibited" in combined:
        return DRIFT_SEVERITY_PROHIBITED
    if "unknown" in combined:
        return DRIFT_SEVERITY_UNKNOWN
    if "blocked" in combined:
        return DRIFT_SEVERITY_BLOCKING
    return DRIFT_SEVERITY_WARNING
