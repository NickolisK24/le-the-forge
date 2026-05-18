"""Deterministic serialization for v4.5B.1 trust visibility foundations."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_5b_1_trust_visibility_foundation_models import (
    GovernanceTransparencyVisibility,
    PublicExplainabilityVisibility,
    PublicIntegrityVisibility,
    PublicTrustDiagnosticRecord,
    PublicTrustEvidenceVisibility,
    TrustSummaryRecord,
    TrustVisibilityFoundationIntelligence,
    TrustVisibilityIdentity,
    TrustVisibilityRecord,
    UnsupportedPublicTrustVisibility,
    UnsupportedStateVisibility,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_v4_5b_1_trust_visibility_foundation_evidence(
    payload: Any,
) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_5b_1_trust_visibility_foundation_evidence(
            asdict(payload)
        )
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_5b_1_trust_visibility_foundation_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [
            canonicalize_v4_5b_1_trust_visibility_foundation_evidence(value)
            for value in payload
        ]
    return payload


def stable_serialize_v4_5b_1_trust_visibility_foundation(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_5b_1_trust_visibility_foundation_evidence(payload),
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


def export_trust_visibility_identity(
    identity: TrustVisibilityIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_trust_visibility_record(
    record: TrustVisibilityRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_public_trust_evidence_visibility(
    record: PublicTrustEvidenceVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_unsupported_state_visibility(
    record: UnsupportedStateVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_governance_transparency_visibility(
    record: GovernanceTransparencyVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_trust_summary_record(record: TrustSummaryRecord) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_public_explainability_visibility(
    record: PublicExplainabilityVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_public_integrity_visibility(
    record: PublicIntegrityVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_public_trust_diagnostic_record(
    record: PublicTrustDiagnosticRecord,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_unsupported_public_trust_visibility(
    record: UnsupportedPublicTrustVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_v4_5b_1_trust_visibility_foundation(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["trust_identity"] = export_trust_visibility_identity(
        intelligence.trust_identity
    )
    data["trust_visibility_records"] = [
        export_trust_visibility_record(record)
        for record in sorted(
            intelligence.trust_visibility_records,
            key=lambda item: (item.deterministic_order, item.trust_record_id),
        )
    ]
    data["evidence_visibility"] = [
        export_public_trust_evidence_visibility(record)
        for record in sorted(
            intelligence.evidence_visibility,
            key=lambda item: (item.deterministic_order, item.evidence_visibility_id),
        )
    ]
    data["unsupported_state_visibility"] = [
        export_unsupported_state_visibility(record)
        for record in sorted(
            intelligence.unsupported_state_visibility,
            key=lambda item: (item.deterministic_order, item.unsupported_visibility_id),
        )
    ]
    data["governance_transparency_visibility"] = [
        export_governance_transparency_visibility(record)
        for record in sorted(
            intelligence.governance_transparency_visibility,
            key=lambda item: (
                item.deterministic_order,
                item.transparency_visibility_id,
            ),
        )
    ]
    data["trust_summaries"] = [
        export_trust_summary_record(record)
        for record in sorted(
            intelligence.trust_summaries,
            key=lambda item: (item.deterministic_order, item.trust_summary_record_id),
        )
    ]
    data["explainability_visibility"] = [
        export_public_explainability_visibility(record)
        for record in sorted(
            intelligence.explainability_visibility,
            key=lambda item: (
                item.deterministic_order,
                item.explainability_visibility_id,
            ),
        )
    ]
    data["integrity_visibility"] = [
        export_public_integrity_visibility(record)
        for record in sorted(
            intelligence.integrity_visibility,
            key=lambda item: (item.deterministic_order, item.integrity_visibility_id),
        )
    ]
    data["public_trust_diagnostics"] = [
        export_public_trust_diagnostic_record(record)
        for record in sorted(
            intelligence.public_trust_diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["unsupported_public_trust_visibility"] = [
        export_unsupported_public_trust_visibility(record)
        for record in sorted(
            intelligence.unsupported_public_trust_visibility,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["inherited_prohibitions"] = _sorted_tuple(data["inherited_prohibitions"])
    data["inherited_constraints"] = _sorted_tuple(data["inherited_constraints"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    return data


def serialize_trust_visibility_identity(identity: TrustVisibilityIdentity) -> str:
    return stable_serialize_v4_5b_1_trust_visibility_foundation(
        export_trust_visibility_identity(identity)
    )


def serialize_v4_5b_1_trust_visibility_foundation(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> str:
    return stable_serialize_v4_5b_1_trust_visibility_foundation(
        export_v4_5b_1_trust_visibility_foundation(intelligence)
    )
