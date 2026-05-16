"""Deterministic orchestration policy resolution integrity auditing."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_policy_compatibility_registry import default_orchestration_policy_compatibility_registry
from .orchestration_policy_resolution_auditor import audit_orchestration_policy_resolution
from .orchestration_policy_resolution_explainability import explain_orchestration_policy_resolution
from .orchestration_policy_resolution_models import (
    RESOLUTION_CONTINUITY_GAP,
    RESOLUTION_EVIDENCE_INCOMPLETE,
    RESOLUTION_EXPLAINABILITY_STABLE,
    RESOLUTION_FUTURE_CANDIDATE,
    RESOLUTION_INTEGRITY_BLOCKED_BY_BLOCKER_GAP,
    RESOLUTION_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP,
    RESOLUTION_INTEGRITY_BLOCKED_BY_EVIDENCE_GAP,
    RESOLUTION_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    RESOLUTION_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    RESOLUTION_INTEGRITY_BLOCKED_BY_HASH_GAP,
    RESOLUTION_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    RESOLUTION_INTEGRITY_BLOCKED_BY_REGISTRY_GAP,
    RESOLUTION_INTEGRITY_STABLE,
    RESOLUTION_INTENTIONAL_BLOCK,
    RESOLUTION_UNSUPPORTED_BY_DESIGN,
    OrchestrationPolicyResolutionAuditInput,
    OrchestrationPolicyResolutionIntegrityInput,
    OrchestrationPolicyResolutionIntegrityResult,
    OrchestrationPolicyResolutionIntegritySummary,
    OrchestrationPolicyResolutionRecord,
    OrchestrationPolicyResolutionRegistry,
    export_resolution_integrity_result,
    hash_resolution_integrity_result,
    hash_resolution_record,
    hash_resolution_registry,
    serialize_resolution_integrity_result,
    serialize_resolution_registry,
)
from .orchestration_policy_resolution_registry import default_orchestration_policy_resolution_registry


def default_orchestration_policy_resolution_integrity_input() -> OrchestrationPolicyResolutionIntegrityInput:
    registry = default_orchestration_policy_resolution_registry()
    audit = audit_orchestration_policy_resolution(
        OrchestrationPolicyResolutionAuditInput(resolution_registry=registry)
    )
    explainability = explain_orchestration_policy_resolution(registry, audit)
    return OrchestrationPolicyResolutionIntegrityInput(
        resolution_registry=registry,
        audit_result=audit,
        explainability_result=explainability,
    )


def audit_orchestration_policy_resolution_integrity(
    integrity_input: OrchestrationPolicyResolutionIntegrityInput | None = None,
) -> OrchestrationPolicyResolutionIntegrityResult:
    source = integrity_input or default_orchestration_policy_resolution_integrity_input()
    registry_hash = hash_resolution_registry(source.resolution_registry)
    registry = _registry_integrity(source, registry_hash)
    resolution_hash = _resolution_hash_integrity(source.resolution_registry)
    provenance = _provenance_integrity(source.resolution_registry)
    explainability = _explainability_integrity(source)
    blocker = _blocker_integrity(source)
    evidence = _evidence_integrity(source)
    governance = _governance_integrity(source)
    compatibility = _compatibility_integrity(source.resolution_registry)
    serialization = _serialization_integrity(source.resolution_registry)
    failures = _failure_summary(
        registry,
        resolution_hash,
        provenance,
        explainability,
        blocker,
        evidence,
        governance,
        compatibility,
        serialization,
    )
    manual_review = tuple(sorted(set(source.manual_review_reasons)))
    status = _integrity_status(
        registry,
        resolution_hash,
        provenance,
        explainability,
        blocker,
        evidence,
        governance,
        compatibility,
    )
    result = OrchestrationPolicyResolutionIntegrityResult(
        registry_id=source.resolution_registry.registry_id,
        resolution_integrity_status=status,
        planning_only=True,
        registry_integrity=registry,
        resolution_hash_integrity=resolution_hash,
        provenance_integrity=provenance,
        explainability_integrity=explainability,
        blocker_integrity=blocker,
        evidence_integrity=evidence,
        governance_integrity=governance,
        compatibility_integrity=compatibility,
        deterministic_serialization_integrity=serialization,
        failure_classification_summary=failures,
        manual_review_summary=manual_review,
        deterministic_resolution_integrity_hash="",
        deterministic_explanation_summary=_summary(status, failures),
    )
    return replace(result, deterministic_resolution_integrity_hash=hash_resolution_integrity_result(result))


def export_orchestration_policy_resolution_integrity_result(
    result: OrchestrationPolicyResolutionIntegrityResult,
) -> dict[str, object]:
    return export_resolution_integrity_result(result)


def serialize_orchestration_policy_resolution_integrity_result(
    result: OrchestrationPolicyResolutionIntegrityResult,
) -> str:
    return serialize_resolution_integrity_result(result)


def hash_orchestration_policy_resolution_integrity_result(
    result: OrchestrationPolicyResolutionIntegrityResult,
) -> str:
    return hash_resolution_integrity_result(result)


def _registry_integrity(
    source: OrchestrationPolicyResolutionIntegrityInput,
    registry_hash: str,
) -> OrchestrationPolicyResolutionIntegritySummary:
    failures: list[str] = []
    if not source.resolution_registry.records:
        failures.append("resolution_registry_has_no_records")
    if source.expected_registry_hash is not None and source.expected_registry_hash != registry_hash:
        failures.append("resolution_registry_hash_mismatch")
    if not source.resolution_registry.planning_only or not source.resolution_registry.non_production:
        failures.append("resolution_registry_boundary_not_planning_only_non_production")
    return OrchestrationPolicyResolutionIntegritySummary("registry", (registry_hash,), tuple(sorted(failures)))


def _resolution_hash_integrity(
    registry: OrchestrationPolicyResolutionRegistry,
) -> OrchestrationPolicyResolutionIntegritySummary:
    references = tuple(sorted(f"{record.identifier.resolution_id}:{hash_resolution_record(record)}" for record in registry.records))
    ids = [record.identifier.resolution_id for record in registry.records]
    duplicates = sorted({resolution_id for resolution_id in ids if ids.count(resolution_id) > 1})
    relationship_ids = [record.identifier.relationship_id for record in registry.records]
    relationship_duplicates = sorted({relationship_id for relationship_id in relationship_ids if relationship_ids.count(relationship_id) > 1})
    failures = tuple(
        sorted(
            [f"duplicate_resolution_id:{resolution_id}" for resolution_id in duplicates]
            + [f"duplicate_resolution_relationship_id:{relationship_id}" for relationship_id in relationship_duplicates]
        )
    )
    return OrchestrationPolicyResolutionIntegritySummary("resolution_hash", references, failures)


def _provenance_integrity(
    registry: OrchestrationPolicyResolutionRegistry,
) -> OrchestrationPolicyResolutionIntegritySummary:
    references: list[str] = []
    failures: list[str] = []
    for record in registry.records:
        provenance = record.provenance
        references.extend(
            [
                provenance.source_phase,
                provenance.source_artifact,
                provenance.compatibility_relationship_id,
                *provenance.replay_reference_ids,
                *provenance.rollback_reference_ids,
                *provenance.governance_reference_ids,
            ]
        )
        if not provenance.source_phase or not provenance.source_artifact:
            failures.append(f"{record.identifier.resolution_id}:source_provenance_gap")
        if not provenance.compatibility_relationship_id:
            failures.append(f"{record.identifier.resolution_id}:compatibility_provenance_gap")
        if not provenance.replay_reference_ids:
            failures.append(f"{record.identifier.resolution_id}:replay_provenance_gap")
        if not provenance.rollback_reference_ids:
            failures.append(f"{record.identifier.resolution_id}:rollback_provenance_gap")
        if not provenance.governance_reference_ids:
            failures.append(f"{record.identifier.resolution_id}:governance_provenance_gap")
    return OrchestrationPolicyResolutionIntegritySummary("provenance", tuple(sorted(set(references))), tuple(sorted(failures)))


def _explainability_integrity(
    source: OrchestrationPolicyResolutionIntegrityInput,
) -> OrchestrationPolicyResolutionIntegritySummary:
    references = (
        source.audit_result.deterministic_resolution_audit_hash,
        source.explainability_result.deterministic_resolution_explainability_hash,
    )
    failures: list[str] = []
    if source.explainability_result.resolution_explainability_status != RESOLUTION_EXPLAINABILITY_STABLE:
        failures.append(f"resolution_explainability_status:{source.explainability_result.resolution_explainability_status}")
    if source.expected_audit_hash is not None and source.expected_audit_hash != source.audit_result.deterministic_resolution_audit_hash:
        failures.append("resolution_audit_hash_mismatch")
    if source.expected_explainability_hash is not None and source.expected_explainability_hash != source.explainability_result.deterministic_resolution_explainability_hash:
        failures.append("resolution_explainability_hash_mismatch")
    return OrchestrationPolicyResolutionIntegritySummary("explainability", references, tuple(sorted(failures)))


def _blocker_integrity(
    source: OrchestrationPolicyResolutionIntegrityInput,
) -> OrchestrationPolicyResolutionIntegritySummary:
    references = tuple(sorted(f"{record.resolution_id}:{record.blocker_chain_count}" for record in source.audit_result.audit_records))
    failures: list[str] = []
    for record in source.audit_result.audit_records:
        blocked_by_design = (
            RESOLUTION_INTENTIONAL_BLOCK in record.resolution_classifications
            or RESOLUTION_UNSUPPORTED_BY_DESIGN in record.resolution_classifications
        )
        if blocked_by_design and record.blocker_chain_count == 0:
            failures.append(f"{record.resolution_id}:missing_blocker_chain_visibility")
    if source.audit_result.blocker_chain_total != sum(record.blocker_chain_count for record in source.audit_result.audit_records):
        failures.append("resolution_blocker_chain_total_mismatch")
    return OrchestrationPolicyResolutionIntegritySummary("blocker", references, tuple(sorted(failures)))


def _evidence_integrity(
    source: OrchestrationPolicyResolutionIntegrityInput,
) -> OrchestrationPolicyResolutionIntegritySummary:
    references = tuple(sorted(f"{record.resolution_id}:{record.evidence_gap_count}" for record in source.audit_result.audit_records))
    failures: list[str] = []
    for record in source.audit_result.audit_records:
        needs_evidence = (
            RESOLUTION_FUTURE_CANDIDATE in record.resolution_classifications
            or RESOLUTION_EVIDENCE_INCOMPLETE in record.resolution_classifications
        )
        if needs_evidence and record.evidence_gap_count == 0:
            failures.append(f"{record.resolution_id}:missing_evidence_gap_visibility")
    return OrchestrationPolicyResolutionIntegritySummary("evidence", references, tuple(sorted(failures)))


def _governance_integrity(
    source: OrchestrationPolicyResolutionIntegrityInput,
) -> OrchestrationPolicyResolutionIntegritySummary:
    references = tuple(sorted(record.resolution_id for record in source.audit_result.audit_records))
    failures: list[str] = []
    for audit_record in source.audit_result.audit_records:
        if audit_record.integrity_continuity_state == RESOLUTION_CONTINUITY_GAP:
            failures.append(f"{audit_record.resolution_id}:integrity_continuity_gap")
        source_record = _record_by_id(source.resolution_registry, audit_record.resolution_id)
        if source_record is not None and _governance_gap(source_record):
            failures.append(f"{audit_record.resolution_id}:governance_boundary_gap")
    for field in (
        "runtime_execution_enabled",
        "orchestration_execution_enabled",
        "routing_behavior_enabled",
        "mutation_behavior_enabled",
        "production_consumption_enabled",
        "automatic_resolution_enabled",
    ):
        if getattr(source.audit_result, field):
            failures.append(f"{field}:enabled")
    return OrchestrationPolicyResolutionIntegritySummary("governance", references, tuple(sorted(failures)))


def _compatibility_integrity(
    registry: OrchestrationPolicyResolutionRegistry,
) -> OrchestrationPolicyResolutionIntegritySummary:
    compatibility_registry = default_orchestration_policy_compatibility_registry()
    compatibility_by_id = {
        relationship.identifier.relationship_id: relationship
        for relationship in compatibility_registry.relationships
    }
    references: list[str] = []
    failures: list[str] = []
    for record in registry.records:
        relationship = compatibility_by_id.get(record.identifier.relationship_id)
        references.append(record.identifier.relationship_id)
        if relationship is None:
            failures.append(f"{record.identifier.resolution_id}:missing_compatibility_relationship")
            continue
        if relationship.compatibility_state != record.compatibility_state:
            failures.append(f"{record.identifier.resolution_id}:compatibility_state_mismatch")
    return OrchestrationPolicyResolutionIntegritySummary("compatibility", tuple(sorted(references)), tuple(sorted(failures)))


def _serialization_integrity(
    registry: OrchestrationPolicyResolutionRegistry,
) -> OrchestrationPolicyResolutionIntegritySummary:
    first = serialize_resolution_registry(registry)
    second = serialize_resolution_registry(registry)
    failures = () if first == second else ("resolution_registry_serialization_not_stable",)
    return OrchestrationPolicyResolutionIntegritySummary("deterministic_serialization", (hash_resolution_registry(registry),), failures)


def _record_by_id(
    registry: OrchestrationPolicyResolutionRegistry,
    resolution_id: str,
) -> OrchestrationPolicyResolutionRecord | None:
    for record in registry.records:
        if record.identifier.resolution_id == resolution_id:
            return record
    return None


def _governance_gap(record: OrchestrationPolicyResolutionRecord) -> bool:
    metadata = record.governance_metadata
    required_true = ("planning_only", "non_production", "deterministic_only", "governance_first", "resolution_audit_only")
    required_false = (
        "execution_enabled",
        "routing_enabled",
        "mutation_enabled",
        "autonomy_enabled",
        "automatic_resolution_enabled",
        "production_runtime_reads_enabled",
        "production_runtime_writes_enabled",
        "persistent_writes_enabled",
    )
    if any(metadata.get(key) is not True for key in required_true):
        return True
    if any(metadata.get(key) is not False for key in required_false):
        return True
    return any(
        (
            record.status_change_allowed,
            record.automatic_resolution_enabled,
            record.runtime_execution_enabled,
            record.orchestration_execution_enabled,
            record.routing_behavior_enabled,
            record.mutation_behavior_enabled,
            record.production_consumption_enabled,
            record.background_processing_enabled,
        )
    )


def _failure_summary(*summaries: OrchestrationPolicyResolutionIntegritySummary) -> tuple[str, ...]:
    failures: set[str] = set()
    for summary in summaries:
        failures.update(summary.failures)
    return tuple(sorted(failures))


def _integrity_status(
    registry: OrchestrationPolicyResolutionIntegritySummary,
    resolution_hash: OrchestrationPolicyResolutionIntegritySummary,
    provenance: OrchestrationPolicyResolutionIntegritySummary,
    explainability: OrchestrationPolicyResolutionIntegritySummary,
    blocker: OrchestrationPolicyResolutionIntegritySummary,
    evidence: OrchestrationPolicyResolutionIntegritySummary,
    governance: OrchestrationPolicyResolutionIntegritySummary,
    compatibility: OrchestrationPolicyResolutionIntegritySummary,
) -> str:
    if registry.failures:
        return RESOLUTION_INTEGRITY_BLOCKED_BY_HASH_GAP if "resolution_registry_hash_mismatch" in registry.failures else RESOLUTION_INTEGRITY_BLOCKED_BY_REGISTRY_GAP
    if resolution_hash.failures:
        return RESOLUTION_INTEGRITY_BLOCKED_BY_HASH_GAP
    if provenance.failures:
        return RESOLUTION_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP
    if explainability.failures:
        return RESOLUTION_INTEGRITY_BLOCKED_BY_HASH_GAP if any("hash_mismatch" in failure for failure in explainability.failures) else RESOLUTION_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP
    if blocker.failures:
        return RESOLUTION_INTEGRITY_BLOCKED_BY_BLOCKER_GAP
    if evidence.failures:
        return RESOLUTION_INTEGRITY_BLOCKED_BY_EVIDENCE_GAP
    if governance.failures:
        return RESOLUTION_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP
    if compatibility.failures:
        return RESOLUTION_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP
    return RESOLUTION_INTEGRITY_STABLE


def _summary(status: str, failures: tuple[str, ...]) -> str:
    if status == RESOLUTION_INTEGRITY_STABLE:
        return (
            "Resolution integrity is stable; registry, hashes, provenance, explainability, blocker, evidence, "
            "governance, compatibility, and serialization continuity remain deterministic and non-executing."
        )
    return f"Resolution integrity classified as {status}; failures: {', '.join(failures)}."
