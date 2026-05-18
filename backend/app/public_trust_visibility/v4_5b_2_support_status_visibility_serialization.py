"""Deterministic serialization for v4.5B.2 support status visibility."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_5b_2_support_status_visibility_models import (
    ContinuitySupportVisibility,
    EvidenceBasedSupportVisibility,
    ExperimentalDeprecatedVisibility,
    ExplainabilitySupportVisibility,
    PublicSupportSurfaceVisibility,
    SupportClassificationVisibility,
    SupportDiagnosticRecord,
    SupportStatusIdentity,
    SupportStatusVisibilityIntelligence,
    SupportSummaryRecord,
    SupportVisibilityRecord,
    UnsupportedSupportOperationalStateVisibility,
    UnsupportedSupportStateVisibility,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_v4_5b_2_support_status_visibility_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_5b_2_support_status_visibility_evidence(
            asdict(payload)
        )
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_5b_2_support_status_visibility_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [
            canonicalize_v4_5b_2_support_status_visibility_evidence(value)
            for value in payload
        ]
    return payload


def stable_serialize_v4_5b_2_support_status_visibility(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_5b_2_support_status_visibility_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _export_with_sorted_evidence(record: object) -> dict[str, Any]:
    data = asdict(record)
    if "evidence_reference_ids" in data:
        data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_support_status_identity(identity: SupportStatusIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_support_visibility_record(record: SupportVisibilityRecord) -> dict[str, Any]:
    return asdict(record)


def export_support_classification_visibility(
    record: SupportClassificationVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_public_support_surface_visibility(
    record: PublicSupportSurfaceVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_unsupported_support_state_visibility(
    record: UnsupportedSupportStateVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_experimental_deprecated_visibility(
    record: ExperimentalDeprecatedVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_evidence_based_support_visibility(
    record: EvidenceBasedSupportVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_explainability_support_visibility(
    record: ExplainabilitySupportVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_continuity_support_visibility(
    record: ContinuitySupportVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_support_summary_record(record: SupportSummaryRecord) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_support_diagnostic_record(record: SupportDiagnosticRecord) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_unsupported_support_operational_state_visibility(
    record: UnsupportedSupportOperationalStateVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_v4_5b_2_support_status_visibility(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["support_identity"] = export_support_status_identity(
        intelligence.support_identity
    )
    data["support_visibility_records"] = [
        export_support_visibility_record(record)
        for record in sorted(
            intelligence.support_visibility_records,
            key=lambda item: (item.deterministic_order, item.support_record_id),
        )
    ]
    data["support_classifications"] = [
        export_support_classification_visibility(record)
        for record in sorted(
            intelligence.support_classifications,
            key=lambda item: (
                item.deterministic_order,
                item.classification_visibility_id,
            ),
        )
    ]
    data["support_surfaces"] = [
        export_public_support_surface_visibility(record)
        for record in sorted(
            intelligence.support_surfaces,
            key=lambda item: (item.deterministic_order, item.surface_visibility_id),
        )
    ]
    data["unsupported_state_visibility"] = [
        export_unsupported_support_state_visibility(record)
        for record in sorted(
            intelligence.unsupported_state_visibility,
            key=lambda item: (item.deterministic_order, item.unsupported_visibility_id),
        )
    ]
    data["experimental_deprecated_visibility"] = [
        export_experimental_deprecated_visibility(record)
        for record in sorted(
            intelligence.experimental_deprecated_visibility,
            key=lambda item: (item.deterministic_order, item.experimental_deprecated_id),
        )
    ]
    data["evidence_based_support_visibility"] = [
        export_evidence_based_support_visibility(record)
        for record in sorted(
            intelligence.evidence_based_support_visibility,
            key=lambda item: (item.deterministic_order, item.evidence_support_id),
        )
    ]
    data["explainability_support_visibility"] = [
        export_explainability_support_visibility(record)
        for record in sorted(
            intelligence.explainability_support_visibility,
            key=lambda item: (item.deterministic_order, item.explainability_support_id),
        )
    ]
    data["continuity_support_visibility"] = [
        export_continuity_support_visibility(record)
        for record in sorted(
            intelligence.continuity_support_visibility,
            key=lambda item: (item.deterministic_order, item.continuity_support_id),
        )
    ]
    data["support_summaries"] = [
        export_support_summary_record(record)
        for record in sorted(
            intelligence.support_summaries,
            key=lambda item: (item.deterministic_order, item.support_summary_record_id),
        )
    ]
    data["support_diagnostics"] = [
        export_support_diagnostic_record(record)
        for record in sorted(
            intelligence.support_diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["unsupported_operational_state_visibility"] = [
        export_unsupported_support_operational_state_visibility(record)
        for record in sorted(
            intelligence.unsupported_operational_state_visibility,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["inherited_prohibitions"] = _sorted_tuple(data["inherited_prohibitions"])
    data["inherited_constraints"] = _sorted_tuple(data["inherited_constraints"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    return data


def serialize_support_status_identity(identity: SupportStatusIdentity) -> str:
    return stable_serialize_v4_5b_2_support_status_visibility(
        export_support_status_identity(identity)
    )


def serialize_v4_5b_2_support_status_visibility(
    intelligence: SupportStatusVisibilityIntelligence,
) -> str:
    return stable_serialize_v4_5b_2_support_status_visibility(
        export_v4_5b_2_support_status_visibility(intelligence)
    )
