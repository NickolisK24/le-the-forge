"""Deterministic serialization for v4.5A.1 drift foundations."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_5a_1_drift_foundation_models import (
    DriftClassificationRecord,
    DriftContinuityVisibility,
    DriftDiagnosticRecord,
    DriftEvidenceReference,
    DriftFoundationIdentity,
    DriftFoundationIntelligence,
    DriftIdentityRecord,
    DriftSeverityVisibility,
    UnsupportedDriftStateVisibility,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_v4_5a_1_drift_foundation_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_5a_1_drift_foundation_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_5a_1_drift_foundation_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [
            canonicalize_v4_5a_1_drift_foundation_evidence(value)
            for value in payload
        ]
    return payload


def stable_serialize_v4_5a_1_drift_foundation(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_5a_1_drift_foundation_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_drift_foundation_identity(
    identity: DriftFoundationIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_drift_identity_record(record: DriftIdentityRecord) -> dict[str, Any]:
    return asdict(record)


def export_drift_classification_record(
    record: DriftClassificationRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_drift_evidence_reference(record: DriftEvidenceReference) -> dict[str, Any]:
    return asdict(record)


def export_drift_continuity_visibility(
    record: DriftContinuityVisibility,
) -> dict[str, Any]:
    return asdict(record)


def export_drift_diagnostic_record(record: DriftDiagnosticRecord) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_drift_severity_visibility(
    record: DriftSeverityVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["drift_ids"] = _sorted_tuple(data["drift_ids"])
    data["diagnostic_ids"] = _sorted_tuple(data["diagnostic_ids"])
    return data


def export_unsupported_drift_state_visibility(
    record: UnsupportedDriftStateVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_v4_5a_1_drift_foundations(
    foundations: DriftFoundationIntelligence,
) -> dict[str, Any]:
    data = asdict(foundations)
    data["foundation_identity"] = export_drift_foundation_identity(
        foundations.foundation_identity
    )
    data["drift_identities"] = [
        export_drift_identity_record(record)
        for record in sorted(
            foundations.drift_identities,
            key=lambda item: (item.deterministic_order, item.drift_id),
        )
    ]
    data["classifications"] = [
        export_drift_classification_record(record)
        for record in sorted(
            foundations.classifications,
            key=lambda item: (item.deterministic_order, item.classification_id),
        )
    ]
    data["evidence_references"] = [
        export_drift_evidence_reference(record)
        for record in sorted(
            foundations.evidence_references,
            key=lambda item: (item.deterministic_order, item.evidence_id),
        )
    ]
    data["continuity_visibility"] = [
        export_drift_continuity_visibility(record)
        for record in sorted(
            foundations.continuity_visibility,
            key=lambda item: (item.deterministic_order, item.continuity_id),
        )
    ]
    data["diagnostics"] = [
        export_drift_diagnostic_record(record)
        for record in sorted(
            foundations.diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["severity_visibility"] = [
        export_drift_severity_visibility(record)
        for record in sorted(
            foundations.severity_visibility,
            key=lambda item: (item.deterministic_order, item.severity_id),
        )
    ]
    data["unsupported_state_visibility"] = [
        export_unsupported_drift_state_visibility(record)
        for record in sorted(
            foundations.unsupported_state_visibility,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["inherited_prohibitions"] = _sorted_tuple(data["inherited_prohibitions"])
    data["inherited_constraints"] = _sorted_tuple(data["inherited_constraints"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    return data


def serialize_drift_foundation_identity(identity: DriftFoundationIdentity) -> str:
    return stable_serialize_v4_5a_1_drift_foundation(
        export_drift_foundation_identity(identity)
    )


def serialize_v4_5a_1_drift_foundations(
    foundations: DriftFoundationIntelligence,
) -> str:
    return stable_serialize_v4_5a_1_drift_foundation(
        export_v4_5a_1_drift_foundations(foundations)
    )
