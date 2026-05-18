"""Deterministic serialization for v4.5A.5 cross-boundary drift continuity."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_5a_5_cross_boundary_drift_continuity_models import (
    BoundaryPairContinuityRecord,
    CrossBoundaryContinuityDiagnostic,
    CrossBoundaryContinuityIdentity,
    CrossBoundaryContinuityRecord,
    CrossBoundaryDriftContinuityIntelligence,
    CrossBoundaryEvidenceContinuity,
    DegradationContinuityPreservation,
    DriftContinuityPreservation,
    ExplanationContinuityPreservation,
    PropagationContinuityPreservation,
    UnsupportedCrossBoundaryVisibility,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_v4_5a_5_cross_boundary_drift_continuity_evidence(
    payload: Any,
) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_5a_5_cross_boundary_drift_continuity_evidence(
            asdict(payload)
        )
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_5a_5_cross_boundary_drift_continuity_evidence(
                value
            )
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [
            canonicalize_v4_5a_5_cross_boundary_drift_continuity_evidence(value)
            for value in payload
        ]
    return payload


def stable_serialize_v4_5a_5_cross_boundary_drift_continuity(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_5a_5_cross_boundary_drift_continuity_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_cross_boundary_continuity_identity(
    identity: CrossBoundaryContinuityIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_cross_boundary_continuity_record(
    record: CrossBoundaryContinuityRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_boundary_pair_continuity_record(
    record: BoundaryPairContinuityRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_drift_continuity_preservation(
    record: DriftContinuityPreservation,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_propagation_continuity_preservation(
    record: PropagationContinuityPreservation,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_degradation_continuity_preservation(
    record: DegradationContinuityPreservation,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_explanation_continuity_preservation(
    record: ExplanationContinuityPreservation,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_cross_boundary_evidence_continuity(
    record: CrossBoundaryEvidenceContinuity,
) -> dict[str, Any]:
    return asdict(record)


def export_cross_boundary_continuity_diagnostic(
    record: CrossBoundaryContinuityDiagnostic,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_unsupported_cross_boundary_visibility(
    record: UnsupportedCrossBoundaryVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_v4_5a_5_cross_boundary_drift_continuity(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["continuity_identity"] = export_cross_boundary_continuity_identity(
        intelligence.continuity_identity
    )
    data["cross_boundary_continuity"] = [
        export_cross_boundary_continuity_record(record)
        for record in sorted(
            intelligence.cross_boundary_continuity,
            key=lambda item: (item.deterministic_order, item.cross_boundary_continuity_id),
        )
    ]
    data["boundary_pair_continuity"] = [
        export_boundary_pair_continuity_record(record)
        for record in sorted(
            intelligence.boundary_pair_continuity,
            key=lambda item: (item.deterministic_order, item.boundary_pair_record_id),
        )
    ]
    data["drift_continuity"] = [
        export_drift_continuity_preservation(record)
        for record in sorted(
            intelligence.drift_continuity,
            key=lambda item: (item.deterministic_order, item.drift_continuity_id),
        )
    ]
    data["propagation_continuity"] = [
        export_propagation_continuity_preservation(record)
        for record in sorted(
            intelligence.propagation_continuity,
            key=lambda item: (item.deterministic_order, item.propagation_continuity_id),
        )
    ]
    data["degradation_continuity"] = [
        export_degradation_continuity_preservation(record)
        for record in sorted(
            intelligence.degradation_continuity,
            key=lambda item: (item.deterministic_order, item.degradation_continuity_id),
        )
    ]
    data["explanation_continuity"] = [
        export_explanation_continuity_preservation(record)
        for record in sorted(
            intelligence.explanation_continuity,
            key=lambda item: (item.deterministic_order, item.explanation_continuity_id),
        )
    ]
    data["evidence_continuity"] = [
        export_cross_boundary_evidence_continuity(record)
        for record in sorted(
            intelligence.evidence_continuity,
            key=lambda item: (item.deterministic_order, item.evidence_continuity_id),
        )
    ]
    data["diagnostics"] = [
        export_cross_boundary_continuity_diagnostic(record)
        for record in sorted(
            intelligence.diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["unsupported_cross_boundary_visibility"] = [
        export_unsupported_cross_boundary_visibility(record)
        for record in sorted(
            intelligence.unsupported_cross_boundary_visibility,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["inherited_prohibitions"] = _sorted_tuple(data["inherited_prohibitions"])
    data["inherited_constraints"] = _sorted_tuple(data["inherited_constraints"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    return data


def serialize_cross_boundary_continuity_identity(
    identity: CrossBoundaryContinuityIdentity,
) -> str:
    return stable_serialize_v4_5a_5_cross_boundary_drift_continuity(
        export_cross_boundary_continuity_identity(identity)
    )


def serialize_v4_5a_5_cross_boundary_drift_continuity(
    intelligence: CrossBoundaryDriftContinuityIntelligence,
) -> str:
    return stable_serialize_v4_5a_5_cross_boundary_drift_continuity(
        export_v4_5a_5_cross_boundary_drift_continuity(intelligence)
    )
