"""Deterministic serialization for v4.5A.2 drift propagation intelligence."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_5a_2_drift_propagation_models import (
    CrossBoundaryPropagationVisibility,
    DriftPropagationIdentity,
    DriftPropagationIntelligence,
    PropagationChainRecord,
    PropagationClassificationRecord,
    PropagationContinuityRecord,
    PropagationDiagnosticRecord,
    PropagationEvidenceChain,
    PropagationExplainabilityVisibility,
    PropagationSeverityAccumulation,
    UnsupportedPropagationVisibility,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_v4_5a_2_drift_propagation_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_5a_2_drift_propagation_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_5a_2_drift_propagation_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [
            canonicalize_v4_5a_2_drift_propagation_evidence(value)
            for value in payload
        ]
    return payload


def stable_serialize_v4_5a_2_drift_propagation(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_5a_2_drift_propagation_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_drift_propagation_identity(
    identity: DriftPropagationIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_propagation_chain_record(record: PropagationChainRecord) -> dict[str, Any]:
    return asdict(record)


def export_propagation_classification_record(
    record: PropagationClassificationRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_propagation_evidence_chain(record: PropagationEvidenceChain) -> dict[str, Any]:
    return asdict(record)


def export_propagation_continuity_record(
    record: PropagationContinuityRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_propagation_severity_accumulation(
    record: PropagationSeverityAccumulation,
) -> dict[str, Any]:
    data = asdict(record)
    data["propagation_ids"] = _sorted_tuple(data["propagation_ids"])
    data["diagnostic_ids"] = _sorted_tuple(data["diagnostic_ids"])
    return data


def export_propagation_explainability_visibility(
    record: PropagationExplainabilityVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_cross_boundary_propagation_visibility(
    record: CrossBoundaryPropagationVisibility,
) -> dict[str, Any]:
    return asdict(record)


def export_propagation_diagnostic_record(
    record: PropagationDiagnosticRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_unsupported_propagation_visibility(
    record: UnsupportedPropagationVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_v4_5a_2_drift_propagation_intelligence(
    intelligence: DriftPropagationIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["propagation_identity"] = export_drift_propagation_identity(
        intelligence.propagation_identity
    )
    data["propagation_chains"] = [
        export_propagation_chain_record(record)
        for record in sorted(
            intelligence.propagation_chains,
            key=lambda item: (item.deterministic_order, item.propagation_id),
        )
    ]
    data["classifications"] = [
        export_propagation_classification_record(record)
        for record in sorted(
            intelligence.classifications,
            key=lambda item: (item.deterministic_order, item.classification_id),
        )
    ]
    data["evidence_chains"] = [
        export_propagation_evidence_chain(record)
        for record in sorted(
            intelligence.evidence_chains,
            key=lambda item: (item.deterministic_order, item.evidence_id),
        )
    ]
    data["continuity_records"] = [
        export_propagation_continuity_record(record)
        for record in sorted(
            intelligence.continuity_records,
            key=lambda item: (item.deterministic_order, item.continuity_id),
        )
    ]
    data["severity_accumulation"] = [
        export_propagation_severity_accumulation(record)
        for record in sorted(
            intelligence.severity_accumulation,
            key=lambda item: (item.deterministic_order, item.severity_id),
        )
    ]
    data["explainability_visibility"] = [
        export_propagation_explainability_visibility(record)
        for record in sorted(
            intelligence.explainability_visibility,
            key=lambda item: (item.deterministic_order, item.explainability_id),
        )
    ]
    data["cross_boundary_visibility"] = [
        export_cross_boundary_propagation_visibility(record)
        for record in sorted(
            intelligence.cross_boundary_visibility,
            key=lambda item: (item.deterministic_order, item.cross_boundary_id),
        )
    ]
    data["diagnostics"] = [
        export_propagation_diagnostic_record(record)
        for record in sorted(
            intelligence.diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["unsupported_propagation_visibility"] = [
        export_unsupported_propagation_visibility(record)
        for record in sorted(
            intelligence.unsupported_propagation_visibility,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["inherited_prohibitions"] = _sorted_tuple(data["inherited_prohibitions"])
    data["inherited_constraints"] = _sorted_tuple(data["inherited_constraints"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    return data


def serialize_drift_propagation_identity(identity: DriftPropagationIdentity) -> str:
    return stable_serialize_v4_5a_2_drift_propagation(
        export_drift_propagation_identity(identity)
    )


def serialize_v4_5a_2_drift_propagation_intelligence(
    intelligence: DriftPropagationIntelligence,
) -> str:
    return stable_serialize_v4_5a_2_drift_propagation(
        export_v4_5a_2_drift_propagation_intelligence(intelligence)
    )
