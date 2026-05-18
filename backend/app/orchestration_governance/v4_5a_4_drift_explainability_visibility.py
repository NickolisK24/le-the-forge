"""Descriptive visibility helpers for v4.5A.4 drift explainability intelligence."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_5a_4_drift_explainability_models import (
    DEGRADATION_EXPLANATION_TYPES,
    DRIFT_CAUSE_TYPES,
    EVIDENCE_MAPPING_TYPES,
    EXPLANATION_COMPLETENESS_TYPES,
    EXPLANATION_CONFIDENCE_TYPES,
    EXPLANATION_DIAGNOSTIC_TYPES,
    PROPAGATION_EXPLANATION_TYPES,
    UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES,
    DriftCauseVisibility,
    DriftExplainabilityIntelligence,
    EvidenceExplanationMapping,
    ExplanationCompletenessVisibility,
    ExplanationConfidenceVisibility,
    ExplanationDiagnostic,
    IntegrityDegradationExplanation,
    PropagationExplanationChain,
    UnsupportedExplanationVisibility,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def count_drift_cause_types(records: Iterable[DriftCauseVisibility]) -> dict[str, int]:
    counts = Counter(record.cause_type for record in records)
    return {item: int(counts.get(item, 0)) for item in DRIFT_CAUSE_TYPES}


def count_propagation_explanation_types(
    records: Iterable[PropagationExplanationChain],
) -> dict[str, int]:
    counts = Counter(record.propagation_type for record in records)
    return {item: int(counts.get(item, 0)) for item in PROPAGATION_EXPLANATION_TYPES}


def count_degradation_explanation_types(
    records: Iterable[IntegrityDegradationExplanation],
) -> dict[str, int]:
    counts = Counter(record.degradation_type for record in records)
    return {item: int(counts.get(item, 0)) for item in DEGRADATION_EXPLANATION_TYPES}


def count_evidence_mapping_types(
    records: Iterable[EvidenceExplanationMapping],
) -> dict[str, int]:
    counts = Counter(record.evidence_type for record in records)
    return {item: int(counts.get(item, 0)) for item in EVIDENCE_MAPPING_TYPES}


def count_completeness_types(
    records: Iterable[ExplanationCompletenessVisibility],
) -> dict[str, int]:
    counts = Counter(record.completeness_type for record in records)
    return {item: int(counts.get(item, 0)) for item in EXPLANATION_COMPLETENESS_TYPES}


def count_confidence_types(
    records: Iterable[ExplanationConfidenceVisibility],
) -> dict[str, int]:
    counts = Counter(record.confidence_type for record in records)
    return {item: int(counts.get(item, 0)) for item in EXPLANATION_CONFIDENCE_TYPES}


def count_explanation_diagnostic_types(
    records: Iterable[ExplanationDiagnostic],
) -> dict[str, int]:
    counts = Counter(record.diagnostic_type for record in records)
    return {item: int(counts.get(item, 0)) for item in EXPLANATION_DIAGNOSTIC_TYPES}


def count_unsupported_explanation_states(
    records: Iterable[UnsupportedExplanationVisibility],
) -> dict[str, int]:
    counts = Counter(record.unsupported_state for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES
    }


def explanation_summary_visibility(
    intelligence: DriftExplainabilityIntelligence,
) -> list[dict[str, Any]]:
    cause_by_explanation = {
        record.explanation_id: record for record in intelligence.cause_visibility
    }
    return [
        {
            "explanation_id": record.explanation_id,
            "explanation_chain_id": record.explanation_chain_id,
            "source_drift_id": record.source_drift_id,
            "propagation_chain_id": record.propagation_chain_id,
            "degradation_chain_id": record.degradation_chain_id,
            "evidence_chain_id": record.evidence_chain_id,
            "continuity_reference_id": record.continuity_reference_id,
            "lineage_reference_id": record.lineage_reference_id,
            "provenance_reference_id": record.provenance_reference_id,
            "cause_type": cause_by_explanation[record.explanation_id].cause_type,
            "descriptive_only": record.descriptive_only,
            "non_operational": record.non_operational,
        }
        for record in sorted(
            intelligence.explanation_records,
            key=lambda item: (item.deterministic_order, item.explanation_id),
        )
    ]


def cause_summary_visibility(
    records: Iterable[DriftCauseVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "cause_id": record.cause_id,
            "explanation_id": record.explanation_id,
            "cause_type": record.cause_type,
            "cause_reason": record.cause_reason,
            "descriptive_only": record.descriptive_only,
            "no_hidden_causal_assumption": record.no_hidden_causal_assumption,
            "no_blame_assignment": record.no_blame_assignment,
            "non_decisioning": record.non_decisioning,
            "automated_blame_enabled": record.automated_blame_enabled,
            "action_enabled": record.action_enabled,
            "decision_enabled": record.decision_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "authorization_enabled": record.authorization_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.cause_id))
    ]


def propagation_explanation_summary_visibility(
    records: Iterable[PropagationExplanationChain],
) -> list[dict[str, Any]]:
    return [
        {
            "propagation_explanation_id": record.propagation_explanation_id,
            "explanation_id": record.explanation_id,
            "propagation_type": record.propagation_type,
            "propagation_chain_id": record.propagation_chain_id,
            "explanation_chain_id": record.explanation_chain_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "correction_enabled": record.correction_enabled,
            "suppression_enabled": record.suppression_enabled,
            "mitigation_enabled": record.mitigation_enabled,
            "orchestration_response_enabled": record.orchestration_response_enabled,
            "recommendation_enabled": record.recommendation_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.propagation_explanation_id))
    ]


def degradation_explanation_summary_visibility(
    records: Iterable[IntegrityDegradationExplanation],
) -> list[dict[str, Any]]:
    return [
        {
            "degradation_explanation_id": record.degradation_explanation_id,
            "explanation_id": record.explanation_id,
            "degradation_type": record.degradation_type,
            "degradation_chain_id": record.degradation_chain_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "mitigation_enabled": record.mitigation_enabled,
            "correction_enabled": record.correction_enabled,
            "orchestration_response_enabled": record.orchestration_response_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.degradation_explanation_id))
    ]


def evidence_mapping_summary_visibility(
    records: Iterable[EvidenceExplanationMapping],
) -> list[dict[str, Any]]:
    return [
        {
            "mapping_id": record.mapping_id,
            "explanation_id": record.explanation_id,
            "evidence_type": record.evidence_type,
            "evidence_reference_id": record.evidence_reference_id,
            "evidence_chain_id": record.evidence_chain_id,
            "source_reference": record.source_reference,
            "source_hash_reference": record.source_hash_reference,
            "replay_safe": record.replay_safe,
            "rollback_safe": record.rollback_safe,
            "provenance_safe": record.provenance_safe,
            "lineage_safe": record.lineage_safe,
            "integrity_safe": record.integrity_safe,
            "hidden_assumption_used": record.hidden_assumption_used,
            "production_consumption_enabled": record.production_consumption_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.mapping_id))
    ]


def completeness_summary_visibility(
    records: Iterable[ExplanationCompletenessVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "completeness_id": record.completeness_id,
            "explanation_id": record.explanation_id,
            "completeness_type": record.completeness_type,
            "completeness_reason": record.completeness_reason,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "non_scoring": record.non_scoring,
            "non_ranking": record.non_ranking,
            "non_authorizing": record.non_authorizing,
            "scoring_enabled": record.scoring_enabled,
            "ranking_enabled": record.ranking_enabled,
            "authorization_enabled": record.authorization_enabled,
            "recommendation_enabled": record.recommendation_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.completeness_id))
    ]


def confidence_summary_visibility(
    records: Iterable[ExplanationConfidenceVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "confidence_id": record.confidence_id,
            "explanation_id": record.explanation_id,
            "confidence_type": record.confidence_type,
            "confidence_reason": record.confidence_reason,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "non_authorizing": record.non_authorizing,
            "non_ranking": record.non_ranking,
            "non_recommending": record.non_recommending,
            "authorization_enabled": record.authorization_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "execution_enabled": record.execution_enabled,
            "suppression_enabled": record.suppression_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.confidence_id))
    ]


def fail_visible_explanation_diagnostic_summaries(
    records: Iterable[ExplanationDiagnostic],
) -> list[dict[str, Any]]:
    return [
        {
            "diagnostic_id": record.diagnostic_id,
            "explanation_id": record.explanation_id,
            "diagnostic_type": record.diagnostic_type,
            "confidence_type": record.confidence_type,
            "message": record.message,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "hidden_assumption_used": record.hidden_assumption_used,
            "silent_fallback_enabled": record.silent_fallback_enabled,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "mitigation_enabled": record.mitigation_enabled,
            "auto_correction_enabled": record.auto_correction_enabled,
            "explanation_action_enabled": record.explanation_action_enabled,
            "explanation_ranking_enabled": record.explanation_ranking_enabled,
            "explanation_authorization_enabled": record.explanation_authorization_enabled,
            "orchestration_response_enabled": record.orchestration_response_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.diagnostic_id))
    ]


def unsupported_explanation_visibility_summaries(
    records: Iterable[UnsupportedExplanationVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "state_id": record.state_id,
            "unsupported_state": record.unsupported_state,
            "explicit_reason": record.explicit_reason,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "operational_enabled": record.operational_enabled,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "mitigation_enabled": record.mitigation_enabled,
            "automated_correction_enabled": record.automated_correction_enabled,
            "explanation_action_enabled": record.explanation_action_enabled,
            "explanation_ranking_enabled": record.explanation_ranking_enabled,
            "explanation_authorization_enabled": record.explanation_authorization_enabled,
            "authorization_enabled": record.authorization_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.state_id))
    ]


def validate_required_explanation_visibility(
    intelligence: DriftExplainabilityIntelligence,
) -> dict[str, Any]:
    cause_counts = count_drift_cause_types(intelligence.cause_visibility)
    propagation_counts = count_propagation_explanation_types(
        intelligence.propagation_explanations
    )
    degradation_counts = count_degradation_explanation_types(
        intelligence.degradation_explanations
    )
    evidence_counts = count_evidence_mapping_types(intelligence.evidence_mappings)
    completeness_counts = count_completeness_types(intelligence.completeness_visibility)
    confidence_counts = count_confidence_types(intelligence.confidence_visibility)
    diagnostic_counts = count_explanation_diagnostic_types(intelligence.diagnostics)
    unsupported_counts = count_unsupported_explanation_states(
        intelligence.unsupported_explanation_visibility
    )
    missing_cause_types = [key for key, count in cause_counts.items() if count <= 0]
    missing_propagation_types = [
        key for key, count in propagation_counts.items() if count <= 0
    ]
    missing_degradation_types = [
        key for key, count in degradation_counts.items() if count <= 0
    ]
    missing_evidence_types = [
        key for key, count in evidence_counts.items() if count <= 0
    ]
    missing_completeness_types = [
        key for key, count in completeness_counts.items() if count <= 0
    ]
    missing_confidence_types = [
        key for key, count in confidence_counts.items() if count <= 0
    ]
    missing_diagnostic_types = [
        key for key, count in diagnostic_counts.items() if count <= 0
    ]
    missing_unsupported_states = [
        key for key, count in unsupported_counts.items() if count <= 0
    ]
    return {
        "valid": not (
            missing_cause_types
            or missing_propagation_types
            or missing_degradation_types
            or missing_evidence_types
            or missing_completeness_types
            or missing_confidence_types
            or missing_diagnostic_types
            or missing_unsupported_states
        ),
        "cause_counts": cause_counts,
        "propagation_counts": propagation_counts,
        "degradation_counts": degradation_counts,
        "evidence_counts": evidence_counts,
        "completeness_counts": completeness_counts,
        "confidence_counts": confidence_counts,
        "diagnostic_counts": diagnostic_counts,
        "unsupported_state_counts": unsupported_counts,
        "missing_cause_types": missing_cause_types,
        "missing_propagation_types": missing_propagation_types,
        "missing_degradation_types": missing_degradation_types,
        "missing_evidence_types": missing_evidence_types,
        "missing_completeness_types": missing_completeness_types,
        "missing_confidence_types": missing_confidence_types,
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
    }


def descriptive_only_explanation_summary(
    intelligence: DriftExplainabilityIntelligence,
) -> dict[str, Any]:
    return {
        "descriptive_only": intelligence.descriptive_only,
        "non_operational": intelligence.non_operational,
        "non_executing": intelligence.non_executing,
        "non_authorizing": intelligence.non_authorizing,
        "non_remediating": intelligence.non_remediating,
        "non_runtime_mutating": intelligence.non_runtime_mutating,
        "non_operational_mutating": intelligence.non_operational_mutating,
        "non_routing": intelligence.non_routing,
        "non_dispatching": intelligence.non_dispatching,
        "non_traversing": intelligence.non_traversing,
        "non_scheduling": intelligence.non_scheduling,
        "non_sequencing": intelligence.non_sequencing,
        "non_recommending": intelligence.non_recommending,
        "non_deciding": intelligence.non_deciding,
        "non_ranking": intelligence.non_ranking,
        "runtime_execution_enabled": intelligence.runtime_execution_enabled,
        "orchestration_execution_enabled": intelligence.orchestration_execution_enabled,
        "orchestration_authorization_enabled": intelligence.orchestration_authorization_enabled,
        "orchestration_approval_enabled": intelligence.orchestration_approval_enabled,
        "orchestration_dispatch_enabled": intelligence.orchestration_dispatch_enabled,
        "orchestration_routing_enabled": intelligence.orchestration_routing_enabled,
        "orchestration_traversal_enabled": intelligence.orchestration_traversal_enabled,
        "orchestration_scheduling_enabled": intelligence.orchestration_scheduling_enabled,
        "orchestration_sequencing_enabled": intelligence.orchestration_sequencing_enabled,
        "orchestration_decision_enabled": intelligence.orchestration_decision_enabled,
        "orchestration_recommendation_enabled": intelligence.orchestration_recommendation_enabled,
        "remediation_enabled": intelligence.remediation_enabled,
        "repair_enabled": intelligence.repair_enabled,
        "mitigation_enabled": intelligence.mitigation_enabled,
        "auto_correction_enabled": intelligence.auto_correction_enabled,
        "explanation_action_enabled": intelligence.explanation_action_enabled,
        "explanation_ranking_enabled": intelligence.explanation_ranking_enabled,
        "explanation_authorization_enabled": intelligence.explanation_authorization_enabled,
        "explanation_decision_enabled": intelligence.explanation_decision_enabled,
        "explanation_recommendation_enabled": intelligence.explanation_recommendation_enabled,
        "runtime_mutation_enabled": intelligence.runtime_mutation_enabled,
        "operational_mutation_enabled": intelligence.operational_mutation_enabled,
        "planner_integration_enabled": intelligence.planner_integration_enabled,
        "planner_execution_enabled": intelligence.planner_execution_enabled,
        "production_consumption_enabled": intelligence.production_consumption_enabled,
    }
