"""Deterministic orchestration policy evaluation for v3.6."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_policy_models import (
    POLICY_BLOCKED,
    POLICY_BLOCKED_BY_DEPENDENCY_GAP,
    POLICY_BLOCKED_BY_EXPLAINABILITY_GAP,
    POLICY_BLOCKED_BY_GOVERNANCE_GAP,
    POLICY_BLOCKED_BY_HASH_MISMATCH,
    POLICY_BLOCKED_BY_INTEGRITY_GAP,
    POLICY_BLOCKED_BY_MISSING_DEPENDENCY,
    POLICY_BLOCKED_BY_PRODUCTION_LEAK,
    POLICY_BLOCKED_BY_PROHIBITION,
    POLICY_BLOCKED_BY_PROVENANCE_GAP,
    POLICY_BLOCKED_BY_UNSUPPORTED_STATE,
    POLICY_CONTINUITY_GAP,
    POLICY_CONTINUITY_PRESERVED,
    POLICY_DEPENDENCY_GAP,
    POLICY_DEPENDENCY_MISSING,
    POLICY_DEPENDENCY_PROHIBITED,
    POLICY_DEPENDENCY_SATISFIED,
    POLICY_DEPENDENCY_UNSUPPORTED,
    POLICY_EVALUATION_BLOCKED_BY_POLICY_CONTINUITY_GAP,
    POLICY_EVALUATION_REQUIRES_MANUAL_REVIEW,
    POLICY_EVALUATION_STABLE,
    POLICY_EVALUATION_STABLE_WITH_VISIBLE_BLOCKERS,
    POLICY_PROHIBITED,
    POLICY_REQUIRES_MANUAL_REVIEW,
    POLICY_SUPPORTED,
    POLICY_UNSUPPORTED,
    OrchestrationPolicyBlocker,
    OrchestrationPolicyDefinition,
    OrchestrationPolicyDependency,
    OrchestrationPolicyEvaluationInput,
    OrchestrationPolicyEvaluationRecord,
    OrchestrationPolicyEvaluationResult,
    OrchestrationPolicyRegistry,
    export_policy_evaluation_result,
    hash_policy_definition,
    hash_policy_evaluation_result,
    hash_policy_registry,
    serialize_policy_evaluation_result,
)
from .orchestration_policy_registry import default_orchestration_policy_registry


STRUCTURAL_BLOCKER_STATES: frozenset[str] = frozenset(
    {
        POLICY_BLOCKED_BY_MISSING_DEPENDENCY,
        POLICY_BLOCKED_BY_DEPENDENCY_GAP,
        POLICY_BLOCKED_BY_GOVERNANCE_GAP,
        POLICY_BLOCKED_BY_PROVENANCE_GAP,
        POLICY_BLOCKED_BY_INTEGRITY_GAP,
        POLICY_BLOCKED_BY_EXPLAINABILITY_GAP,
        POLICY_BLOCKED_BY_HASH_MISMATCH,
        POLICY_BLOCKED_BY_PRODUCTION_LEAK,
    }
)


def default_orchestration_policy_evaluation_input() -> OrchestrationPolicyEvaluationInput:
    return OrchestrationPolicyEvaluationInput(registry=default_orchestration_policy_registry())


def evaluate_orchestration_policy_compatibility(
    evaluation_input: OrchestrationPolicyEvaluationInput | None = None,
) -> OrchestrationPolicyEvaluationResult:
    source = evaluation_input or default_orchestration_policy_evaluation_input()
    policies_by_id = {policy.identifier.policy_id: policy for policy in source.registry.policies}
    records = tuple(_evaluate_policy(policy, policies_by_id, source) for policy in source.registry.policies)
    blockers = tuple(sorted((blocker for record in records for blocker in record.blockers), key=_blocker_sort_key))
    registry_hash = hash_policy_registry(source.registry)
    registry_hash_blocker = _registry_hash_blocker(source, registry_hash)
    if registry_hash_blocker is not None:
        blockers = tuple(sorted(blockers + (registry_hash_blocker,), key=_blocker_sort_key))
    manual_review = tuple(sorted(set(source.manual_review_reasons)))
    status = _evaluation_status(blockers, manual_review)
    result = OrchestrationPolicyEvaluationResult(
        registry_id=source.registry.registry_id,
        policy_evaluation_status=status,
        planning_only=True,
        non_production=True,
        policy_records=records,
        registered_policy_count=len(records),
        supported_policy_count=sum(1 for record in records if record.support_state == POLICY_SUPPORTED),
        prohibited_policy_count=sum(1 for record in records if record.support_state == POLICY_PROHIBITED),
        unsupported_policy_count=sum(1 for record in records if record.support_state == POLICY_UNSUPPORTED),
        blocker_count=len(blockers),
        supported_policy_ids=tuple(sorted(record.policy_id for record in records if record.support_state == POLICY_SUPPORTED)),
        prohibited_policy_ids=tuple(sorted(record.policy_id for record in records if record.support_state == POLICY_PROHIBITED)),
        unsupported_policy_ids=tuple(sorted(record.policy_id for record in records if record.support_state == POLICY_UNSUPPORTED)),
        dependency_continuity_status=_continuity_status(records, "dependency_state", POLICY_DEPENDENCY_SATISFIED),
        provenance_continuity_status=_continuity_status(records, "provenance_continuity_state", POLICY_CONTINUITY_PRESERVED),
        governance_continuity_status=_continuity_status(records, "governance_continuity_state", POLICY_CONTINUITY_PRESERVED),
        integrity_continuity_status=_continuity_status(records, "integrity_continuity_state", POLICY_CONTINUITY_PRESERVED),
        explainability_continuity_status=_continuity_status(records, "explainability_continuity_state", POLICY_CONTINUITY_PRESERVED),
        blocker_summary=blockers,
        manual_review_summary=manual_review,
        deterministic_registry_hash=registry_hash,
        deterministic_policy_evaluation_hash="",
        deterministic_explanation_summary=_explanation(status, blockers, manual_review),
    )
    return replace(result, deterministic_policy_evaluation_hash=hash_policy_evaluation_result(result))


def export_orchestration_policy_evaluation_result(result: OrchestrationPolicyEvaluationResult) -> dict[str, object]:
    return export_policy_evaluation_result(result)


def serialize_orchestration_policy_evaluation_result(result: OrchestrationPolicyEvaluationResult) -> str:
    return serialize_policy_evaluation_result(result)


def hash_orchestration_policy_evaluation_result(result: OrchestrationPolicyEvaluationResult) -> str:
    return hash_policy_evaluation_result(result)


def hash_orchestration_policy_evaluation_input(source: OrchestrationPolicyEvaluationInput) -> str:
    return hash_policy_registry(source.registry)


def _evaluate_policy(
    policy: OrchestrationPolicyDefinition,
    policies_by_id: dict[str, OrchestrationPolicyDefinition],
    source: OrchestrationPolicyEvaluationInput,
) -> OrchestrationPolicyEvaluationRecord:
    policy_id = policy.identifier.policy_id
    policy_hash = hash_policy_definition(policy)
    blockers: list[OrchestrationPolicyBlocker] = []
    dependency_state, dependency_blockers = _dependency_state(policy, policies_by_id)
    blockers.extend(dependency_blockers)
    governance_state, governance_blockers = _governance_state(policy)
    blockers.extend(governance_blockers)
    provenance_state, provenance_blockers = _provenance_state(policy)
    blockers.extend(provenance_blockers)
    integrity_state, integrity_blockers = _reference_state(policy_id, policy.integrity_reference_ids, POLICY_BLOCKED_BY_INTEGRITY_GAP)
    blockers.extend(integrity_blockers)
    explainability_state, explainability_blockers = _reference_state(
        policy_id,
        policy.explainability_reference_ids,
        POLICY_BLOCKED_BY_EXPLAINABILITY_GAP,
    )
    blockers.extend(explainability_blockers)
    expected_hash = source.expected_policy_hashes.get(policy_id) if source.expected_policy_hashes else None
    if expected_hash is not None and expected_hash != policy_hash:
        blockers.append(
            OrchestrationPolicyBlocker(
                policy_id=policy_id,
                blocker_state=POLICY_BLOCKED_BY_HASH_MISMATCH,
                reason="policy hash does not match expected deterministic hash",
                evidence_ids=(policy_hash, expected_hash),
            )
        )
    if policy.support_state == POLICY_PROHIBITED:
        blockers.extend(_state_blockers(policy, POLICY_BLOCKED_BY_PROHIBITION))
    if policy.support_state == POLICY_UNSUPPORTED:
        blockers.extend(_state_blockers(policy, POLICY_BLOCKED_BY_UNSUPPORTED_STATE))
    if policy.manual_review_reasons:
        blockers.append(
            OrchestrationPolicyBlocker(
                policy_id=policy_id,
                blocker_state=POLICY_REQUIRES_MANUAL_REVIEW,
                reason="policy requires manual review",
                evidence_ids=policy.manual_review_reasons,
            )
        )
    structural = any(blocker.blocker_state in STRUCTURAL_BLOCKER_STATES for blocker in blockers)
    return OrchestrationPolicyEvaluationRecord(
        policy_id=policy_id,
        classification=policy.classification,
        support_state=policy.support_state,
        effective_state=POLICY_BLOCKED if structural else policy.support_state,
        policy_hash=policy_hash,
        dependency_state=dependency_state,
        dependency_chain=tuple(sorted(dependency.required_policy_id for dependency in policy.dependencies)),
        governance_continuity_state=governance_state,
        provenance_continuity_state=provenance_state,
        integrity_continuity_state=integrity_state,
        explainability_continuity_state=explainability_state,
        blockers=tuple(sorted(blockers, key=_blocker_sort_key)),
    )


def _dependency_state(
    policy: OrchestrationPolicyDefinition,
    policies_by_id: dict[str, OrchestrationPolicyDefinition],
) -> tuple[str, list[OrchestrationPolicyBlocker]]:
    blockers: list[OrchestrationPolicyBlocker] = []
    states: list[str] = []
    policy_id = policy.identifier.policy_id
    for dependency in policy.dependencies:
        state, blocker = _dependency_item_state(policy_id, dependency, policies_by_id)
        states.append(state)
        if blocker is not None:
            blockers.append(blocker)
    if not states:
        return POLICY_DEPENDENCY_SATISFIED, blockers
    if POLICY_DEPENDENCY_MISSING in states:
        return POLICY_DEPENDENCY_MISSING, blockers
    if POLICY_DEPENDENCY_PROHIBITED in states:
        return POLICY_DEPENDENCY_PROHIBITED, blockers
    if POLICY_DEPENDENCY_UNSUPPORTED in states:
        return POLICY_DEPENDENCY_UNSUPPORTED, blockers
    if POLICY_DEPENDENCY_GAP in states:
        return POLICY_DEPENDENCY_GAP, blockers
    return POLICY_DEPENDENCY_SATISFIED, blockers


def _dependency_item_state(
    policy_id: str,
    dependency: OrchestrationPolicyDependency,
    policies_by_id: dict[str, OrchestrationPolicyDefinition],
) -> tuple[str, OrchestrationPolicyBlocker | None]:
    required = policies_by_id.get(dependency.required_policy_id)
    if required is None:
        return (
            POLICY_DEPENDENCY_MISSING,
            OrchestrationPolicyBlocker(
                policy_id=policy_id,
                blocker_state=POLICY_BLOCKED_BY_MISSING_DEPENDENCY,
                reason=f"missing required policy dependency {dependency.required_policy_id}",
                evidence_ids=(dependency.dependency_id, dependency.continuity_reference_id),
            ),
        )
    if required.support_state == POLICY_PROHIBITED:
        return (
            POLICY_DEPENDENCY_PROHIBITED,
            OrchestrationPolicyBlocker(
                policy_id=policy_id,
                blocker_state=POLICY_BLOCKED_BY_DEPENDENCY_GAP,
                reason=f"required policy dependency {dependency.required_policy_id} is prohibited",
                evidence_ids=(dependency.dependency_id, dependency.continuity_reference_id),
            ),
        )
    if required.support_state == POLICY_UNSUPPORTED:
        return (
            POLICY_DEPENDENCY_UNSUPPORTED,
            OrchestrationPolicyBlocker(
                policy_id=policy_id,
                blocker_state=POLICY_BLOCKED_BY_DEPENDENCY_GAP,
                reason=f"required policy dependency {dependency.required_policy_id} is unsupported",
                evidence_ids=(dependency.dependency_id, dependency.continuity_reference_id),
            ),
        )
    if required.support_state not in dependency.required_support_states:
        return (
            POLICY_DEPENDENCY_GAP,
            OrchestrationPolicyBlocker(
                policy_id=policy_id,
                blocker_state=dependency.blocker_state,
                reason=f"required policy dependency {dependency.required_policy_id} has incompatible state {required.support_state}",
                evidence_ids=(dependency.dependency_id, dependency.continuity_reference_id),
            ),
        )
    return POLICY_DEPENDENCY_SATISFIED, None


def _governance_state(policy: OrchestrationPolicyDefinition) -> tuple[str, list[OrchestrationPolicyBlocker]]:
    blockers: list[OrchestrationPolicyBlocker] = []
    metadata = policy.governance_metadata
    required_true = ("planning_only", "non_production", "deterministic_only", "governance_first")
    required_false = (
        "execution_enabled",
        "routing_enabled",
        "mutation_enabled",
        "autonomy_enabled",
        "production_runtime_reads_enabled",
        "production_runtime_writes_enabled",
        "persistent_writes_enabled",
    )
    for key in required_true:
        if metadata.get(key) is not True:
            blockers.append(_governance_blocker(policy, f"governance metadata {key} is not true"))
    for key in required_false:
        if metadata.get(key) is not False:
            blockers.append(_governance_blocker(policy, f"governance metadata {key} is not false"))
    if _execution_flag_leaked(policy):
        blockers.append(_governance_blocker(policy, "policy exposes execution, routing, mutation, trace, scheduling, or dispatch behavior"))
    if policy.production_consumption_enabled or policy.production_state_reads_enabled:
        blockers.append(
            OrchestrationPolicyBlocker(
                policy_id=policy.identifier.policy_id,
                blocker_state=POLICY_BLOCKED_BY_PRODUCTION_LEAK,
                reason="policy exposes production runtime access",
                evidence_ids=("production_runtime_access",),
            )
        )
    return (POLICY_CONTINUITY_GAP if blockers else POLICY_CONTINUITY_PRESERVED), blockers


def _provenance_state(policy: OrchestrationPolicyDefinition) -> tuple[str, list[OrchestrationPolicyBlocker]]:
    provenance = policy.provenance
    missing: list[str] = []
    if not provenance.source_phase:
        missing.append("source_phase")
    if not provenance.source_artifact:
        missing.append("source_artifact")
    if not provenance.replay_reference_ids:
        missing.append("replay_reference_ids")
    if not provenance.rollback_reference_ids:
        missing.append("rollback_reference_ids")
    if not provenance.governance_reference_ids:
        missing.append("governance_reference_ids")
    if not missing:
        return POLICY_CONTINUITY_PRESERVED, []
    return (
        POLICY_CONTINUITY_GAP,
        [
            OrchestrationPolicyBlocker(
                policy_id=policy.identifier.policy_id,
                blocker_state=POLICY_BLOCKED_BY_PROVENANCE_GAP,
                reason="policy provenance continuity gap",
                evidence_ids=tuple(sorted(missing)),
            )
        ],
    )


def _reference_state(policy_id: str, references: tuple[str, ...], blocker_state: str) -> tuple[str, list[OrchestrationPolicyBlocker]]:
    if references:
        return POLICY_CONTINUITY_PRESERVED, []
    return (
        POLICY_CONTINUITY_GAP,
        [
            OrchestrationPolicyBlocker(
                policy_id=policy_id,
                blocker_state=blocker_state,
                reason="policy continuity reference is missing",
                evidence_ids=(blocker_state,),
            )
        ],
    )


def _state_blockers(policy: OrchestrationPolicyDefinition, blocker_state: str) -> tuple[OrchestrationPolicyBlocker, ...]:
    evidence = policy.prohibited_state_ids if blocker_state == POLICY_BLOCKED_BY_PROHIBITION else policy.unsupported_state_ids
    reasons = policy.blocker_reasons or (policy.support_state,)
    return tuple(
        OrchestrationPolicyBlocker(
            policy_id=policy.identifier.policy_id,
            blocker_state=blocker_state,
            reason=reason,
            evidence_ids=evidence,
        )
        for reason in sorted(reasons)
    )


def _registry_hash_blocker(
    source: OrchestrationPolicyEvaluationInput,
    registry_hash: str,
) -> OrchestrationPolicyBlocker | None:
    if source.expected_registry_hash is None or source.expected_registry_hash == registry_hash:
        return None
    return OrchestrationPolicyBlocker(
        policy_id=source.registry.registry_id,
        blocker_state=POLICY_BLOCKED_BY_HASH_MISMATCH,
        reason="registry hash does not match expected deterministic hash",
        evidence_ids=(registry_hash, source.expected_registry_hash),
    )


def _continuity_status(records: tuple[OrchestrationPolicyEvaluationRecord, ...], field: str, stable_state: str) -> str:
    return POLICY_CONTINUITY_PRESERVED if all(getattr(record, field) == stable_state for record in records) else POLICY_CONTINUITY_GAP


def _evaluation_status(blockers: tuple[OrchestrationPolicyBlocker, ...], manual_review: tuple[str, ...]) -> str:
    if any(blocker.blocker_state in STRUCTURAL_BLOCKER_STATES for blocker in blockers):
        return POLICY_EVALUATION_BLOCKED_BY_POLICY_CONTINUITY_GAP
    if manual_review or any(blocker.blocker_state == POLICY_REQUIRES_MANUAL_REVIEW for blocker in blockers):
        return POLICY_EVALUATION_REQUIRES_MANUAL_REVIEW
    if blockers:
        return POLICY_EVALUATION_STABLE_WITH_VISIBLE_BLOCKERS
    return POLICY_EVALUATION_STABLE


def _execution_flag_leaked(policy: OrchestrationPolicyDefinition) -> bool:
    return any(
        (
            policy.runtime_execution_enabled,
            policy.orchestration_execution_enabled,
            policy.routing_behavior_enabled,
            policy.mutation_behavior_enabled,
            policy.audit_log_writing_enabled,
            policy.graph_execution_enabled,
            policy.graph_traversal_behavior_enabled,
            policy.scheduling_behavior_enabled,
            policy.orchestration_dispatch_enabled,
            policy.runtime_trace_capture_enabled,
            policy.live_replay_enabled,
            policy.persistent_audit_storage_enabled,
            policy.policy_execution_enabled,
        )
    )


def _governance_blocker(policy: OrchestrationPolicyDefinition, reason: str) -> OrchestrationPolicyBlocker:
    return OrchestrationPolicyBlocker(
        policy_id=policy.identifier.policy_id,
        blocker_state=POLICY_BLOCKED_BY_GOVERNANCE_GAP,
        reason=reason,
        evidence_ids=("governance_metadata",),
    )


def _explanation(status: str, blockers: tuple[OrchestrationPolicyBlocker, ...], manual_review: tuple[str, ...]) -> str:
    if status == POLICY_EVALUATION_STABLE:
        return "Policy evaluation is stable; no orchestration execution, routing, mutation, autonomy, or production runtime behavior is authorized."
    if status == POLICY_EVALUATION_STABLE_WITH_VISIBLE_BLOCKERS:
        return "Policy evaluation is stable with visible prohibited and unsupported policy blockers; policy intelligence remains planning-only."
    visible = tuple(sorted({f"{blocker.policy_id}:{blocker.blocker_state}" for blocker in blockers} | set(manual_review)))
    return f"Policy evaluation classified as {status}; visible policy entries: {', '.join(visible)}."


def _blocker_sort_key(blocker: OrchestrationPolicyBlocker) -> tuple[str, str, str]:
    return (blocker.policy_id, blocker.blocker_state, blocker.reason)
