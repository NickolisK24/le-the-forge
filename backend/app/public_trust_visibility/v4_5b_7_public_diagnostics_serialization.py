"""Deterministic serialization for v4.5B.7 public diagnostics."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_5b_7_public_diagnostics_models import (
    BlockerWarningSummaryRecord,
    CoverageConfidenceDiagnosticsRecord,
    DiagnosticsSummaryRecord,
    EvidencePanelDiagnosticsRecord,
    ExplainabilityDiagnosticsRecord,
    FailVisiblePublicDiagnosticRecord,
    InheritedLimitationVisibilityRecord,
    ProvenanceLineageDiagnosticsRecord,
    PublicDiagnosticsIdentity,
    PublicDiagnosticsIntelligence,
    PublicDiagnosticsVisibilityRecord,
    SupportDiagnosticsRecord,
    UnsupportedPublicDiagnosticsOperationalStateVisibility,
)


def canonicalize_v4_5b_7_public_diagnostics_payload(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_5b_7_public_diagnostics_payload(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_5b_7_public_diagnostics_payload(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [
            canonicalize_v4_5b_7_public_diagnostics_payload(value)
            for value in payload
        ]
    return payload


def stable_serialize_v4_5b_7_public_diagnostics(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_5b_7_public_diagnostics_payload(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def export_public_diagnostics_identity(
    identity: PublicDiagnosticsIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_public_diagnostics_visibility_record(
    record: PublicDiagnosticsVisibilityRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_support_diagnostics_record(record: SupportDiagnosticsRecord) -> dict[str, Any]:
    return asdict(record)


def export_explainability_diagnostics_record(
    record: ExplainabilityDiagnosticsRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_provenance_lineage_diagnostics_record(
    record: ProvenanceLineageDiagnosticsRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_evidence_panel_diagnostics_record(
    record: EvidencePanelDiagnosticsRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_coverage_confidence_diagnostics_record(
    record: CoverageConfidenceDiagnosticsRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_inherited_limitation_visibility_record(
    record: InheritedLimitationVisibilityRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_blocker_warning_summary_record(
    record: BlockerWarningSummaryRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_diagnostics_summary_record(
    record: DiagnosticsSummaryRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_fail_visible_public_diagnostic_record(
    record: FailVisiblePublicDiagnosticRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_unsupported_public_diagnostics_operational_state_visibility(
    record: UnsupportedPublicDiagnosticsOperationalStateVisibility,
) -> dict[str, Any]:
    return asdict(record)


def export_v4_5b_7_public_diagnostics(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["identity"] = export_public_diagnostics_identity(intelligence.identity)
    data["public_diagnostics_records"] = [
        export_public_diagnostics_visibility_record(record)
        for record in sorted(
            intelligence.public_diagnostics_records,
            key=lambda item: (item.deterministic_order, item.diagnostics_record_id),
        )
    ]
    data["support_diagnostics_records"] = [
        export_support_diagnostics_record(record)
        for record in sorted(
            intelligence.support_diagnostics_records,
            key=lambda item: (item.deterministic_order, item.support_diagnostics_id),
        )
    ]
    data["explainability_diagnostics_records"] = [
        export_explainability_diagnostics_record(record)
        for record in sorted(
            intelligence.explainability_diagnostics_records,
            key=lambda item: (
                item.deterministic_order,
                item.explainability_diagnostics_id,
            ),
        )
    ]
    data["provenance_lineage_diagnostics_records"] = [
        export_provenance_lineage_diagnostics_record(record)
        for record in sorted(
            intelligence.provenance_lineage_diagnostics_records,
            key=lambda item: (
                item.deterministic_order,
                item.provenance_lineage_diagnostics_id,
            ),
        )
    ]
    data["evidence_panel_diagnostics_records"] = [
        export_evidence_panel_diagnostics_record(record)
        for record in sorted(
            intelligence.evidence_panel_diagnostics_records,
            key=lambda item: (item.deterministic_order, item.evidence_diagnostics_id),
        )
    ]
    data["coverage_confidence_diagnostics_records"] = [
        export_coverage_confidence_diagnostics_record(record)
        for record in sorted(
            intelligence.coverage_confidence_diagnostics_records,
            key=lambda item: (
                item.deterministic_order,
                item.coverage_confidence_diagnostics_id,
            ),
        )
    ]
    data["inherited_limitation_records"] = [
        export_inherited_limitation_visibility_record(record)
        for record in sorted(
            intelligence.inherited_limitation_records,
            key=lambda item: (item.deterministic_order, item.inherited_limitation_id),
        )
    ]
    data["blocker_warning_records"] = [
        export_blocker_warning_summary_record(record)
        for record in sorted(
            intelligence.blocker_warning_records,
            key=lambda item: (item.deterministic_order, item.blocker_warning_id),
        )
    ]
    data["summary_records"] = [
        export_diagnostics_summary_record(record)
        for record in sorted(
            intelligence.summary_records,
            key=lambda item: (item.deterministic_order, item.summary_record_id),
        )
    ]
    data["fail_visible_diagnostic_records"] = [
        export_fail_visible_public_diagnostic_record(record)
        for record in sorted(
            intelligence.fail_visible_diagnostic_records,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["unsupported_operational_state_visibility"] = [
        export_unsupported_public_diagnostics_operational_state_visibility(record)
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


def serialize_public_diagnostics_identity(
    identity: PublicDiagnosticsIdentity,
) -> str:
    return stable_serialize_v4_5b_7_public_diagnostics(
        export_public_diagnostics_identity(identity)
    )


def serialize_v4_5b_7_public_diagnostics(
    intelligence: PublicDiagnosticsIntelligence,
) -> str:
    return stable_serialize_v4_5b_7_public_diagnostics(
        export_v4_5b_7_public_diagnostics(intelligence)
    )
