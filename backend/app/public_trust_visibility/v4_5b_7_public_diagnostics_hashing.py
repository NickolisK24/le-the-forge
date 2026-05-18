"""Deterministic hashing for v4.5B.7 public diagnostics."""

from __future__ import annotations

import hashlib
from typing import Any

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
from .v4_5b_7_public_diagnostics_serialization import (
    export_blocker_warning_summary_record,
    export_coverage_confidence_diagnostics_record,
    export_diagnostics_summary_record,
    export_evidence_panel_diagnostics_record,
    export_explainability_diagnostics_record,
    export_fail_visible_public_diagnostic_record,
    export_inherited_limitation_visibility_record,
    export_provenance_lineage_diagnostics_record,
    export_public_diagnostics_identity,
    export_public_diagnostics_visibility_record,
    export_support_diagnostics_record,
    export_unsupported_public_diagnostics_operational_state_visibility,
    export_v4_5b_7_public_diagnostics,
    stable_serialize_v4_5b_7_public_diagnostics,
)


def deterministic_v4_5b_7_public_diagnostics_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_v4_5b_7_public_diagnostics(payload).encode("utf-8")
    ).hexdigest()


def hash_public_diagnostics_identity(identity: PublicDiagnosticsIdentity) -> str:
    return deterministic_v4_5b_7_public_diagnostics_hash(
        export_public_diagnostics_identity(identity)
    )


def hash_public_diagnostics_visibility_record(
    record: PublicDiagnosticsVisibilityRecord,
) -> str:
    return deterministic_v4_5b_7_public_diagnostics_hash(
        export_public_diagnostics_visibility_record(record)
    )


def hash_support_diagnostics_record(record: SupportDiagnosticsRecord) -> str:
    return deterministic_v4_5b_7_public_diagnostics_hash(
        export_support_diagnostics_record(record)
    )


def hash_explainability_diagnostics_record(
    record: ExplainabilityDiagnosticsRecord,
) -> str:
    return deterministic_v4_5b_7_public_diagnostics_hash(
        export_explainability_diagnostics_record(record)
    )


def hash_provenance_lineage_diagnostics_record(
    record: ProvenanceLineageDiagnosticsRecord,
) -> str:
    return deterministic_v4_5b_7_public_diagnostics_hash(
        export_provenance_lineage_diagnostics_record(record)
    )


def hash_evidence_panel_diagnostics_record(
    record: EvidencePanelDiagnosticsRecord,
) -> str:
    return deterministic_v4_5b_7_public_diagnostics_hash(
        export_evidence_panel_diagnostics_record(record)
    )


def hash_coverage_confidence_diagnostics_record(
    record: CoverageConfidenceDiagnosticsRecord,
) -> str:
    return deterministic_v4_5b_7_public_diagnostics_hash(
        export_coverage_confidence_diagnostics_record(record)
    )


def hash_inherited_limitation_visibility_record(
    record: InheritedLimitationVisibilityRecord,
) -> str:
    return deterministic_v4_5b_7_public_diagnostics_hash(
        export_inherited_limitation_visibility_record(record)
    )


def hash_blocker_warning_summary_record(record: BlockerWarningSummaryRecord) -> str:
    return deterministic_v4_5b_7_public_diagnostics_hash(
        export_blocker_warning_summary_record(record)
    )


def hash_diagnostics_summary_record(record: DiagnosticsSummaryRecord) -> str:
    return deterministic_v4_5b_7_public_diagnostics_hash(
        export_diagnostics_summary_record(record)
    )


def hash_fail_visible_public_diagnostic_record(
    record: FailVisiblePublicDiagnosticRecord,
) -> str:
    return deterministic_v4_5b_7_public_diagnostics_hash(
        export_fail_visible_public_diagnostic_record(record)
    )


def hash_unsupported_public_diagnostics_operational_state_visibility(
    record: UnsupportedPublicDiagnosticsOperationalStateVisibility,
) -> str:
    return deterministic_v4_5b_7_public_diagnostics_hash(
        export_unsupported_public_diagnostics_operational_state_visibility(record)
    )


def hash_v4_5b_7_public_diagnostics(
    intelligence: PublicDiagnosticsIntelligence,
) -> str:
    return deterministic_v4_5b_7_public_diagnostics_hash(
        export_v4_5b_7_public_diagnostics(intelligence)
    )
