"""Deterministic hashing for v4.5B.6 coverage and confidence."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_5b_6_coverage_confidence_models import (
    ConfidenceVisibilityRecord,
    CoverageConfidenceIdentity,
    CoverageConfidenceIntelligence,
    CoverageConfidenceSummaryRecord,
    CoverageDiagnosticRecord,
    CoverageVisibilityRecord,
    EvidenceCoverageRecord,
    ExplainabilityCoverageRecord,
    IncompleteUnknownCoverageRecord,
    ProvenanceLineageCoverageRecord,
    SupportCoverageRecord,
    UnsupportedCoverageConfidenceOperationalStateVisibility,
)
from .v4_5b_6_coverage_confidence_serialization import (
    export_confidence_visibility_record,
    export_coverage_confidence_identity,
    export_coverage_confidence_summary_record,
    export_coverage_diagnostic_record,
    export_coverage_visibility_record,
    export_evidence_coverage_record,
    export_explainability_coverage_record,
    export_incomplete_unknown_coverage_record,
    export_provenance_lineage_coverage_record,
    export_support_coverage_record,
    export_unsupported_coverage_confidence_operational_state_visibility,
    export_v4_5b_6_coverage_confidence,
    stable_serialize_v4_5b_6_coverage_confidence,
)


def deterministic_v4_5b_6_coverage_confidence_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_v4_5b_6_coverage_confidence(payload).encode("utf-8")
    ).hexdigest()


def hash_coverage_confidence_identity(identity: CoverageConfidenceIdentity) -> str:
    return deterministic_v4_5b_6_coverage_confidence_hash(
        export_coverage_confidence_identity(identity)
    )


def hash_coverage_visibility_record(record: CoverageVisibilityRecord) -> str:
    return deterministic_v4_5b_6_coverage_confidence_hash(
        export_coverage_visibility_record(record)
    )


def hash_support_coverage_record(record: SupportCoverageRecord) -> str:
    return deterministic_v4_5b_6_coverage_confidence_hash(
        export_support_coverage_record(record)
    )


def hash_evidence_coverage_record(record: EvidenceCoverageRecord) -> str:
    return deterministic_v4_5b_6_coverage_confidence_hash(
        export_evidence_coverage_record(record)
    )


def hash_explainability_coverage_record(
    record: ExplainabilityCoverageRecord,
) -> str:
    return deterministic_v4_5b_6_coverage_confidence_hash(
        export_explainability_coverage_record(record)
    )


def hash_provenance_lineage_coverage_record(
    record: ProvenanceLineageCoverageRecord,
) -> str:
    return deterministic_v4_5b_6_coverage_confidence_hash(
        export_provenance_lineage_coverage_record(record)
    )


def hash_confidence_visibility_record(record: ConfidenceVisibilityRecord) -> str:
    return deterministic_v4_5b_6_coverage_confidence_hash(
        export_confidence_visibility_record(record)
    )


def hash_incomplete_unknown_coverage_record(
    record: IncompleteUnknownCoverageRecord,
) -> str:
    return deterministic_v4_5b_6_coverage_confidence_hash(
        export_incomplete_unknown_coverage_record(record)
    )


def hash_coverage_confidence_summary_record(
    record: CoverageConfidenceSummaryRecord,
) -> str:
    return deterministic_v4_5b_6_coverage_confidence_hash(
        export_coverage_confidence_summary_record(record)
    )


def hash_coverage_diagnostic_record(record: CoverageDiagnosticRecord) -> str:
    return deterministic_v4_5b_6_coverage_confidence_hash(
        export_coverage_diagnostic_record(record)
    )


def hash_unsupported_coverage_confidence_operational_state_visibility(
    record: UnsupportedCoverageConfidenceOperationalStateVisibility,
) -> str:
    return deterministic_v4_5b_6_coverage_confidence_hash(
        export_unsupported_coverage_confidence_operational_state_visibility(record)
    )


def hash_v4_5b_6_coverage_confidence(
    intelligence: CoverageConfidenceIntelligence,
) -> str:
    return deterministic_v4_5b_6_coverage_confidence_hash(
        export_v4_5b_6_coverage_confidence(intelligence)
    )
