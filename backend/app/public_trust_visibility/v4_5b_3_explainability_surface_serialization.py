"""Deterministic serialization for v4.5B.3 explainability surfaces."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_5b_3_explainability_surface_models import (
    ContinuityExplanationVisibility,
    EvidenceToExplanationMapping,
    ExplainabilitySurfaceIdentity,
    ExplainabilitySurfaceIntelligence,
    ExplainabilitySurfaceRecord,
    ExplanationDiagnosticRecord,
    ExplanationSummaryRecord,
    LimitationExplanationVisibility,
    PublicTrustExplanationVisibility,
    SupportStateExplanationSurface,
    UnsupportedExplanationOperationalStateVisibility,
    UnsupportedStateExplanationVisibility,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_v4_5b_3_explainability_surface_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_5b_3_explainability_surface_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_5b_3_explainability_surface_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [
            canonicalize_v4_5b_3_explainability_surface_evidence(value)
            for value in payload
        ]
    return payload


def stable_serialize_v4_5b_3_explainability_surfaces(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_5b_3_explainability_surface_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _export_with_sorted_references(record: object) -> dict[str, Any]:
    data = asdict(record)
    if "evidence_reference_ids" in data:
        data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    if "explanation_reference_ids" in data:
        data["explanation_reference_ids"] = _sorted_tuple(
            data["explanation_reference_ids"]
        )
    return data


def export_explainability_surface_identity(
    identity: ExplainabilitySurfaceIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_explainability_surface_record(
    record: ExplainabilitySurfaceRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_support_state_explanation_surface(
    record: SupportStateExplanationSurface,
) -> dict[str, Any]:
    return _export_with_sorted_references(record)


def export_evidence_to_explanation_mapping(
    record: EvidenceToExplanationMapping,
) -> dict[str, Any]:
    return _export_with_sorted_references(record)


def export_limitation_explanation_visibility(
    record: LimitationExplanationVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_references(record)


def export_public_trust_explanation_visibility(
    record: PublicTrustExplanationVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_references(record)


def export_continuity_explanation_visibility(
    record: ContinuityExplanationVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_references(record)


def export_unsupported_state_explanation_visibility(
    record: UnsupportedStateExplanationVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_references(record)


def export_explanation_summary_record(record: ExplanationSummaryRecord) -> dict[str, Any]:
    return _export_with_sorted_references(record)


def export_explanation_diagnostic_record(
    record: ExplanationDiagnosticRecord,
) -> dict[str, Any]:
    return _export_with_sorted_references(record)


def export_unsupported_explanation_operational_state_visibility(
    record: UnsupportedExplanationOperationalStateVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_references(record)


def export_v4_5b_3_explainability_surfaces(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["surface_identity"] = export_explainability_surface_identity(
        intelligence.surface_identity
    )
    data["surface_records"] = [
        export_explainability_surface_record(record)
        for record in sorted(
            intelligence.surface_records,
            key=lambda item: (item.deterministic_order, item.surface_record_id),
        )
    ]
    data["support_state_explanations"] = [
        export_support_state_explanation_surface(record)
        for record in sorted(
            intelligence.support_state_explanations,
            key=lambda item: (item.deterministic_order, item.support_state_explanation_id),
        )
    ]
    data["evidence_to_explanation_mappings"] = [
        export_evidence_to_explanation_mapping(record)
        for record in sorted(
            intelligence.evidence_to_explanation_mappings,
            key=lambda item: (item.deterministic_order, item.evidence_mapping_id),
        )
    ]
    data["limitation_explanations"] = [
        export_limitation_explanation_visibility(record)
        for record in sorted(
            intelligence.limitation_explanations,
            key=lambda item: (item.deterministic_order, item.limitation_explanation_id),
        )
    ]
    data["trust_explanations"] = [
        export_public_trust_explanation_visibility(record)
        for record in sorted(
            intelligence.trust_explanations,
            key=lambda item: (item.deterministic_order, item.trust_explanation_id),
        )
    ]
    data["continuity_explanations"] = [
        export_continuity_explanation_visibility(record)
        for record in sorted(
            intelligence.continuity_explanations,
            key=lambda item: (item.deterministic_order, item.continuity_explanation_id),
        )
    ]
    data["unsupported_state_explanations"] = [
        export_unsupported_state_explanation_visibility(record)
        for record in sorted(
            intelligence.unsupported_state_explanations,
            key=lambda item: (item.deterministic_order, item.unsupported_explanation_id),
        )
    ]
    data["explanation_summaries"] = [
        export_explanation_summary_record(record)
        for record in sorted(
            intelligence.explanation_summaries,
            key=lambda item: (
                item.deterministic_order,
                item.explanation_summary_record_id,
            ),
        )
    ]
    data["explanation_diagnostics"] = [
        export_explanation_diagnostic_record(record)
        for record in sorted(
            intelligence.explanation_diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["unsupported_operational_state_visibility"] = [
        export_unsupported_explanation_operational_state_visibility(record)
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


def serialize_explainability_surface_identity(
    identity: ExplainabilitySurfaceIdentity,
) -> str:
    return stable_serialize_v4_5b_3_explainability_surfaces(
        export_explainability_surface_identity(identity)
    )


def serialize_v4_5b_3_explainability_surfaces(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> str:
    return stable_serialize_v4_5b_3_explainability_surfaces(
        export_v4_5b_3_explainability_surfaces(intelligence)
    )
