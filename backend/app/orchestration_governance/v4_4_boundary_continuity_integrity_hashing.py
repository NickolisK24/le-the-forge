"""Deterministic hashing for v4.4 boundary continuity and integrity."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_4_boundary_continuity_integrity_models import (
    BoundaryContinuityCertificationIdentity,
    BoundaryContinuityIntegrityCertification,
    BoundaryIntegrityCertificationIdentity,
    CertificationDiagnosticRecord,
    CertificationLimitationRecord,
    CertificationSummaryRecord,
    ContinuityCertificationRecord,
    IntegrityCertificationRecord,
    LineageContinuityRecord,
    PhaseChainCertificationIdentity,
    PhaseEvidenceReference,
    ProvenanceContinuityRecord,
    ReplayRollbackSafetyRecord,
)
from .v4_4_boundary_continuity_integrity_serialization import (
    export_boundary_continuity_integrity_certification,
    export_certification_diagnostic_record,
    export_certification_limitation_record,
    export_certification_summary_record,
    export_continuity_certification_identity,
    export_continuity_certification_record,
    export_integrity_certification_identity,
    export_integrity_certification_record,
    export_lineage_continuity_record,
    export_phase_chain_certification_identity,
    export_phase_evidence_reference,
    export_provenance_continuity_record,
    export_replay_rollback_safety_record,
    stable_serialize_boundary_continuity_integrity,
)


def deterministic_boundary_continuity_integrity_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_boundary_continuity_integrity(payload).encode("utf-8")
    ).hexdigest()


def hash_continuity_certification_identity(
    identity: BoundaryContinuityCertificationIdentity,
) -> str:
    return deterministic_boundary_continuity_integrity_hash(
        export_continuity_certification_identity(identity)
    )


def hash_integrity_certification_identity(
    identity: BoundaryIntegrityCertificationIdentity,
) -> str:
    return deterministic_boundary_continuity_integrity_hash(
        export_integrity_certification_identity(identity)
    )


def hash_phase_chain_certification_identity(
    identity: PhaseChainCertificationIdentity,
) -> str:
    return deterministic_boundary_continuity_integrity_hash(
        export_phase_chain_certification_identity(identity)
    )


def hash_phase_evidence_reference(record: PhaseEvidenceReference) -> str:
    return deterministic_boundary_continuity_integrity_hash(
        export_phase_evidence_reference(record)
    )


def hash_continuity_certification_record(record: ContinuityCertificationRecord) -> str:
    return deterministic_boundary_continuity_integrity_hash(
        export_continuity_certification_record(record)
    )


def hash_integrity_certification_record(record: IntegrityCertificationRecord) -> str:
    return deterministic_boundary_continuity_integrity_hash(
        export_integrity_certification_record(record)
    )


def hash_certification_limitation_record(record: CertificationLimitationRecord) -> str:
    return deterministic_boundary_continuity_integrity_hash(
        export_certification_limitation_record(record)
    )


def hash_certification_diagnostic_record(record: CertificationDiagnosticRecord) -> str:
    return deterministic_boundary_continuity_integrity_hash(
        export_certification_diagnostic_record(record)
    )


def hash_provenance_continuity_record(record: ProvenanceContinuityRecord) -> str:
    return deterministic_boundary_continuity_integrity_hash(
        export_provenance_continuity_record(record)
    )


def hash_lineage_continuity_record(record: LineageContinuityRecord) -> str:
    return deterministic_boundary_continuity_integrity_hash(
        export_lineage_continuity_record(record)
    )


def hash_replay_rollback_safety_record(record: ReplayRollbackSafetyRecord) -> str:
    return deterministic_boundary_continuity_integrity_hash(
        export_replay_rollback_safety_record(record)
    )


def hash_certification_summary_record(record: CertificationSummaryRecord) -> str:
    return deterministic_boundary_continuity_integrity_hash(
        export_certification_summary_record(record)
    )


def hash_boundary_continuity_integrity_certification(
    certification: BoundaryContinuityIntegrityCertification,
) -> str:
    return deterministic_boundary_continuity_integrity_hash(
        export_boundary_continuity_integrity_certification(certification)
    )
