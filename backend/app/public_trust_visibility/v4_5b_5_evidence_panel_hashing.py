"""Deterministic hashing for v4.5B.5 evidence panels."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_5b_5_evidence_panel_models import (
    EvidenceFreshnessVisibility,
    EvidenceGroupRecord,
    EvidenceItemRecord,
    EvidencePanelDiagnosticRecord,
    EvidencePanelIdentity,
    EvidencePanelIntelligence,
    EvidencePanelRecord,
    EvidencePanelSummaryRecord,
    EvidenceSourceVisibility,
    ExplainabilityEvidencePanel,
    ProvenanceLineageEvidencePanel,
    SupportStatusEvidencePanel,
    UnsupportedEvidencePanelOperationalStateVisibility,
    UnsupportedMissingEvidenceVisibility,
)
from .v4_5b_5_evidence_panel_serialization import (
    export_evidence_freshness_visibility,
    export_evidence_group_record,
    export_evidence_item_record,
    export_evidence_panel_diagnostic_record,
    export_evidence_panel_identity,
    export_evidence_panel_record,
    export_evidence_panel_summary_record,
    export_evidence_source_visibility,
    export_explainability_evidence_panel,
    export_provenance_lineage_evidence_panel,
    export_support_status_evidence_panel,
    export_unsupported_evidence_panel_operational_state_visibility,
    export_unsupported_missing_evidence_visibility,
    export_v4_5b_5_evidence_panels,
    stable_serialize_v4_5b_5_evidence_panels,
)


def deterministic_v4_5b_5_evidence_panel_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_v4_5b_5_evidence_panels(payload).encode("utf-8")
    ).hexdigest()


def hash_evidence_panel_identity(identity: EvidencePanelIdentity) -> str:
    return deterministic_v4_5b_5_evidence_panel_hash(
        export_evidence_panel_identity(identity)
    )


def hash_evidence_panel_record(record: EvidencePanelRecord) -> str:
    return deterministic_v4_5b_5_evidence_panel_hash(
        export_evidence_panel_record(record)
    )


def hash_evidence_group_record(record: EvidenceGroupRecord) -> str:
    return deterministic_v4_5b_5_evidence_panel_hash(
        export_evidence_group_record(record)
    )


def hash_evidence_item_record(record: EvidenceItemRecord) -> str:
    return deterministic_v4_5b_5_evidence_panel_hash(export_evidence_item_record(record))


def hash_evidence_source_visibility(record: EvidenceSourceVisibility) -> str:
    return deterministic_v4_5b_5_evidence_panel_hash(
        export_evidence_source_visibility(record)
    )


def hash_evidence_freshness_visibility(record: EvidenceFreshnessVisibility) -> str:
    return deterministic_v4_5b_5_evidence_panel_hash(
        export_evidence_freshness_visibility(record)
    )


def hash_support_status_evidence_panel(record: SupportStatusEvidencePanel) -> str:
    return deterministic_v4_5b_5_evidence_panel_hash(
        export_support_status_evidence_panel(record)
    )


def hash_explainability_evidence_panel(record: ExplainabilityEvidencePanel) -> str:
    return deterministic_v4_5b_5_evidence_panel_hash(
        export_explainability_evidence_panel(record)
    )


def hash_provenance_lineage_evidence_panel(
    record: ProvenanceLineageEvidencePanel,
) -> str:
    return deterministic_v4_5b_5_evidence_panel_hash(
        export_provenance_lineage_evidence_panel(record)
    )


def hash_unsupported_missing_evidence_visibility(
    record: UnsupportedMissingEvidenceVisibility,
) -> str:
    return deterministic_v4_5b_5_evidence_panel_hash(
        export_unsupported_missing_evidence_visibility(record)
    )


def hash_evidence_panel_summary_record(record: EvidencePanelSummaryRecord) -> str:
    return deterministic_v4_5b_5_evidence_panel_hash(
        export_evidence_panel_summary_record(record)
    )


def hash_evidence_panel_diagnostic_record(
    record: EvidencePanelDiagnosticRecord,
) -> str:
    return deterministic_v4_5b_5_evidence_panel_hash(
        export_evidence_panel_diagnostic_record(record)
    )


def hash_unsupported_evidence_panel_operational_state_visibility(
    record: UnsupportedEvidencePanelOperationalStateVisibility,
) -> str:
    return deterministic_v4_5b_5_evidence_panel_hash(
        export_unsupported_evidence_panel_operational_state_visibility(record)
    )


def hash_v4_5b_5_evidence_panels(
    intelligence: EvidencePanelIntelligence,
) -> str:
    return deterministic_v4_5b_5_evidence_panel_hash(
        export_v4_5b_5_evidence_panels(intelligence)
    )
