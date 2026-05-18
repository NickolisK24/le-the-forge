"""Deterministic serialization for v4.5A.4 drift explainability intelligence."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_5a_4_drift_explainability_models import (
    DriftCauseVisibility,
    DriftExplainabilityIdentity,
    DriftExplainabilityIntelligence,
    EvidenceExplanationMapping,
    ExplanationCompletenessVisibility,
    ExplanationConfidenceVisibility,
    ExplanationDiagnostic,
    ExplanationRecord,
    IntegrityDegradationExplanation,
    PropagationExplanationChain,
    UnsupportedExplanationVisibility,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_v4_5a_4_drift_explainability_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_5a_4_drift_explainability_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_5a_4_drift_explainability_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [
            canonicalize_v4_5a_4_drift_explainability_evidence(value)
            for value in payload
        ]
    return payload


def stable_serialize_v4_5a_4_drift_explainability(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_5a_4_drift_explainability_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_drift_explainability_identity(
    identity: DriftExplainabilityIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_explanation_record(record: ExplanationRecord) -> dict[str, Any]:
    return asdict(record)


def export_drift_cause_visibility(record: DriftCauseVisibility) -> dict[str, Any]:
    return asdict(record)


def export_propagation_explanation_chain(
    record: PropagationExplanationChain,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_integrity_degradation_explanation(
    record: IntegrityDegradationExplanation,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_evidence_explanation_mapping(
    record: EvidenceExplanationMapping,
) -> dict[str, Any]:
    return asdict(record)


def export_explanation_completeness_visibility(
    record: ExplanationCompletenessVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_explanation_confidence_visibility(
    record: ExplanationConfidenceVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_explanation_diagnostic(record: ExplanationDiagnostic) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_unsupported_explanation_visibility(
    record: UnsupportedExplanationVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_v4_5a_4_drift_explainability_intelligence(
    intelligence: DriftExplainabilityIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["explainability_identity"] = export_drift_explainability_identity(
        intelligence.explainability_identity
    )
    data["explanation_records"] = [
        export_explanation_record(record)
        for record in sorted(
            intelligence.explanation_records,
            key=lambda item: (item.deterministic_order, item.explanation_id),
        )
    ]
    data["cause_visibility"] = [
        export_drift_cause_visibility(record)
        for record in sorted(
            intelligence.cause_visibility,
            key=lambda item: (item.deterministic_order, item.cause_id),
        )
    ]
    data["propagation_explanations"] = [
        export_propagation_explanation_chain(record)
        for record in sorted(
            intelligence.propagation_explanations,
            key=lambda item: (item.deterministic_order, item.propagation_explanation_id),
        )
    ]
    data["degradation_explanations"] = [
        export_integrity_degradation_explanation(record)
        for record in sorted(
            intelligence.degradation_explanations,
            key=lambda item: (item.deterministic_order, item.degradation_explanation_id),
        )
    ]
    data["evidence_mappings"] = [
        export_evidence_explanation_mapping(record)
        for record in sorted(
            intelligence.evidence_mappings,
            key=lambda item: (item.deterministic_order, item.mapping_id),
        )
    ]
    data["completeness_visibility"] = [
        export_explanation_completeness_visibility(record)
        for record in sorted(
            intelligence.completeness_visibility,
            key=lambda item: (item.deterministic_order, item.completeness_id),
        )
    ]
    data["confidence_visibility"] = [
        export_explanation_confidence_visibility(record)
        for record in sorted(
            intelligence.confidence_visibility,
            key=lambda item: (item.deterministic_order, item.confidence_id),
        )
    ]
    data["diagnostics"] = [
        export_explanation_diagnostic(record)
        for record in sorted(
            intelligence.diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["unsupported_explanation_visibility"] = [
        export_unsupported_explanation_visibility(record)
        for record in sorted(
            intelligence.unsupported_explanation_visibility,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["inherited_prohibitions"] = _sorted_tuple(data["inherited_prohibitions"])
    data["inherited_constraints"] = _sorted_tuple(data["inherited_constraints"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    return data


def serialize_drift_explainability_identity(
    identity: DriftExplainabilityIdentity,
) -> str:
    return stable_serialize_v4_5a_4_drift_explainability(
        export_drift_explainability_identity(identity)
    )


def serialize_v4_5a_4_drift_explainability_intelligence(
    intelligence: DriftExplainabilityIntelligence,
) -> str:
    return stable_serialize_v4_5a_4_drift_explainability(
        export_v4_5a_4_drift_explainability_intelligence(intelligence)
    )
