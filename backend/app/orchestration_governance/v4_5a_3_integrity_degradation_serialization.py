"""Deterministic serialization for v4.5A.3 integrity degradation intelligence."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_5a_3_integrity_degradation_models import (
    ContinuityDegradationVisibility,
    CrossBoundaryIntegrityVisibility,
    DegradationClassificationRecord,
    DegradationEvidenceChain,
    DegradationRecord,
    DegradationSeverityAccumulation,
    ExplainabilityDegradationVisibility,
    IntegrityDegradationDiagnostic,
    IntegrityDegradationIdentity,
    IntegrityDegradationIntelligence,
    UnsupportedDegradationVisibility,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_v4_5a_3_integrity_degradation_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_5a_3_integrity_degradation_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_5a_3_integrity_degradation_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [
            canonicalize_v4_5a_3_integrity_degradation_evidence(value)
            for value in payload
        ]
    return payload


def stable_serialize_v4_5a_3_integrity_degradation(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_5a_3_integrity_degradation_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_integrity_degradation_identity(
    identity: IntegrityDegradationIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_degradation_record(record: DegradationRecord) -> dict[str, Any]:
    return asdict(record)


def export_degradation_classification_record(
    record: DegradationClassificationRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_degradation_evidence_chain(
    record: DegradationEvidenceChain,
) -> dict[str, Any]:
    return asdict(record)


def export_continuity_degradation_visibility(
    record: ContinuityDegradationVisibility,
) -> dict[str, Any]:
    return asdict(record)


def export_degradation_severity_accumulation(
    record: DegradationSeverityAccumulation,
) -> dict[str, Any]:
    data = asdict(record)
    data["degradation_ids"] = _sorted_tuple(data["degradation_ids"])
    data["diagnostic_ids"] = _sorted_tuple(data["diagnostic_ids"])
    return data


def export_explainability_degradation_visibility(
    record: ExplainabilityDegradationVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_cross_boundary_integrity_visibility(
    record: CrossBoundaryIntegrityVisibility,
) -> dict[str, Any]:
    return asdict(record)


def export_integrity_degradation_diagnostic(
    record: IntegrityDegradationDiagnostic,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_unsupported_degradation_visibility(
    record: UnsupportedDegradationVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_v4_5a_3_integrity_degradation_intelligence(
    intelligence: IntegrityDegradationIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["degradation_identity"] = export_integrity_degradation_identity(
        intelligence.degradation_identity
    )
    data["degradation_records"] = [
        export_degradation_record(record)
        for record in sorted(
            intelligence.degradation_records,
            key=lambda item: (item.deterministic_order, item.degradation_id),
        )
    ]
    data["classifications"] = [
        export_degradation_classification_record(record)
        for record in sorted(
            intelligence.classifications,
            key=lambda item: (item.deterministic_order, item.classification_id),
        )
    ]
    data["evidence_chains"] = [
        export_degradation_evidence_chain(record)
        for record in sorted(
            intelligence.evidence_chains,
            key=lambda item: (item.deterministic_order, item.evidence_id),
        )
    ]
    data["continuity_degradation"] = [
        export_continuity_degradation_visibility(record)
        for record in sorted(
            intelligence.continuity_degradation,
            key=lambda item: (item.deterministic_order, item.continuity_id),
        )
    ]
    data["severity_accumulation"] = [
        export_degradation_severity_accumulation(record)
        for record in sorted(
            intelligence.severity_accumulation,
            key=lambda item: (item.deterministic_order, item.severity_id),
        )
    ]
    data["explainability_degradation"] = [
        export_explainability_degradation_visibility(record)
        for record in sorted(
            intelligence.explainability_degradation,
            key=lambda item: (item.deterministic_order, item.explainability_id),
        )
    ]
    data["cross_boundary_integrity"] = [
        export_cross_boundary_integrity_visibility(record)
        for record in sorted(
            intelligence.cross_boundary_integrity,
            key=lambda item: (item.deterministic_order, item.cross_boundary_id),
        )
    ]
    data["diagnostics"] = [
        export_integrity_degradation_diagnostic(record)
        for record in sorted(
            intelligence.diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["unsupported_degradation_visibility"] = [
        export_unsupported_degradation_visibility(record)
        for record in sorted(
            intelligence.unsupported_degradation_visibility,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["inherited_prohibitions"] = _sorted_tuple(data["inherited_prohibitions"])
    data["inherited_constraints"] = _sorted_tuple(data["inherited_constraints"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    return data


def serialize_integrity_degradation_identity(
    identity: IntegrityDegradationIdentity,
) -> str:
    return stable_serialize_v4_5a_3_integrity_degradation(
        export_integrity_degradation_identity(identity)
    )


def serialize_v4_5a_3_integrity_degradation_intelligence(
    intelligence: IntegrityDegradationIntelligence,
) -> str:
    return stable_serialize_v4_5a_3_integrity_degradation(
        export_v4_5a_3_integrity_degradation_intelligence(intelligence)
    )
