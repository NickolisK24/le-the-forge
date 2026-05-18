"""Deterministic hashing for v4.5B.4 provenance and lineage visibility."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_5b_4_provenance_lineage_visibility_models import (
    EvidenceOriginVisibility,
    ExplainabilityLineageVisibility,
    LineageVisibilityRecord,
    ProvenanceLineageDiagnosticRecord,
    ProvenanceLineageSummaryRecord,
    ProvenanceLineageVisibilityIdentity,
    ProvenanceLineageVisibilityIntelligence,
    ProvenanceVisibilityRecord,
    SourceToSurfaceVisibility,
    StaleUnknownProvenanceVisibility,
    SupportStatusLineageVisibility,
    TrustSummaryLineageVisibility,
    UnsupportedProvenanceLineageOperationalStateVisibility,
)
from .v4_5b_4_provenance_lineage_visibility_serialization import (
    export_evidence_origin_visibility,
    export_explainability_lineage_visibility,
    export_lineage_visibility_record,
    export_provenance_lineage_diagnostic_record,
    export_provenance_lineage_summary_record,
    export_provenance_lineage_visibility_identity,
    export_provenance_visibility_record,
    export_source_to_surface_visibility,
    export_stale_unknown_provenance_visibility,
    export_support_status_lineage_visibility,
    export_trust_summary_lineage_visibility,
    export_unsupported_provenance_lineage_operational_state_visibility,
    export_v4_5b_4_provenance_lineage_visibility,
    stable_serialize_v4_5b_4_provenance_lineage_visibility,
)


def deterministic_v4_5b_4_provenance_lineage_visibility_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_v4_5b_4_provenance_lineage_visibility(payload).encode("utf-8")
    ).hexdigest()


def hash_provenance_lineage_visibility_identity(
    identity: ProvenanceLineageVisibilityIdentity,
) -> str:
    return deterministic_v4_5b_4_provenance_lineage_visibility_hash(
        export_provenance_lineage_visibility_identity(identity)
    )


def hash_provenance_visibility_record(record: ProvenanceVisibilityRecord) -> str:
    return deterministic_v4_5b_4_provenance_lineage_visibility_hash(
        export_provenance_visibility_record(record)
    )


def hash_lineage_visibility_record(record: LineageVisibilityRecord) -> str:
    return deterministic_v4_5b_4_provenance_lineage_visibility_hash(
        export_lineage_visibility_record(record)
    )


def hash_source_to_surface_visibility(record: SourceToSurfaceVisibility) -> str:
    return deterministic_v4_5b_4_provenance_lineage_visibility_hash(
        export_source_to_surface_visibility(record)
    )


def hash_evidence_origin_visibility(record: EvidenceOriginVisibility) -> str:
    return deterministic_v4_5b_4_provenance_lineage_visibility_hash(
        export_evidence_origin_visibility(record)
    )


def hash_support_status_lineage_visibility(
    record: SupportStatusLineageVisibility,
) -> str:
    return deterministic_v4_5b_4_provenance_lineage_visibility_hash(
        export_support_status_lineage_visibility(record)
    )


def hash_explainability_lineage_visibility(
    record: ExplainabilityLineageVisibility,
) -> str:
    return deterministic_v4_5b_4_provenance_lineage_visibility_hash(
        export_explainability_lineage_visibility(record)
    )


def hash_trust_summary_lineage_visibility(
    record: TrustSummaryLineageVisibility,
) -> str:
    return deterministic_v4_5b_4_provenance_lineage_visibility_hash(
        export_trust_summary_lineage_visibility(record)
    )


def hash_stale_unknown_provenance_visibility(
    record: StaleUnknownProvenanceVisibility,
) -> str:
    return deterministic_v4_5b_4_provenance_lineage_visibility_hash(
        export_stale_unknown_provenance_visibility(record)
    )


def hash_provenance_lineage_summary_record(
    record: ProvenanceLineageSummaryRecord,
) -> str:
    return deterministic_v4_5b_4_provenance_lineage_visibility_hash(
        export_provenance_lineage_summary_record(record)
    )


def hash_provenance_lineage_diagnostic_record(
    record: ProvenanceLineageDiagnosticRecord,
) -> str:
    return deterministic_v4_5b_4_provenance_lineage_visibility_hash(
        export_provenance_lineage_diagnostic_record(record)
    )


def hash_unsupported_provenance_lineage_operational_state_visibility(
    record: UnsupportedProvenanceLineageOperationalStateVisibility,
) -> str:
    return deterministic_v4_5b_4_provenance_lineage_visibility_hash(
        export_unsupported_provenance_lineage_operational_state_visibility(record)
    )


def hash_v4_5b_4_provenance_lineage_visibility(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> str:
    return deterministic_v4_5b_4_provenance_lineage_visibility_hash(
        export_v4_5b_4_provenance_lineage_visibility(intelligence)
    )
