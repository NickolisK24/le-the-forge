"""Deterministic hashing for v4.4 boundary readiness transition."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_4_boundary_readiness_transition_models import (
    BlockerWarningVisibilityRecord,
    BoundaryReadinessCertificationIdentity,
    BoundaryReadinessTransitionCertification,
    CompletenessSummaryRecord,
    LimitationVisibilityRecord,
    NonOperationalCertificationRecord,
    PhaseChainCompletenessIdentity,
    PhaseEvidenceReference,
    ReadinessCertificationRecord,
    ReadinessLineageContinuityRecord,
    ReadinessProvenanceContinuityRecord,
    ReadinessReplayRollbackEvidenceRecord,
    TransitionCertificationRecord,
    TransitionSummaryRecord,
    UnresolvedDiagnosticVisibilityRecord,
    V45DriftIntegrityPreparationRecord,
    V45PlanningConstraintRecord,
    V45TransitionCertificationIdentity,
)
from .v4_4_boundary_readiness_transition_serialization import (
    export_blocker_warning_visibility,
    export_boundary_readiness_transition_certification,
    export_completeness_summary,
    export_limitation_visibility,
    export_non_operational_certification,
    export_phase_chain_completeness_identity,
    export_phase_evidence_reference,
    export_readiness_certification_identity,
    export_readiness_certification_record,
    export_readiness_lineage_continuity,
    export_readiness_provenance_continuity,
    export_readiness_replay_rollback_evidence,
    export_transition_certification_identity,
    export_transition_certification_record,
    export_transition_summary,
    export_unresolved_diagnostic_visibility,
    export_v4_5_drift_integrity_preparation,
    export_v4_5_planning_constraint,
    stable_serialize_boundary_readiness_transition,
)


def deterministic_boundary_readiness_transition_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_boundary_readiness_transition(payload).encode("utf-8")
    ).hexdigest()


def hash_readiness_certification_identity(
    identity: BoundaryReadinessCertificationIdentity,
) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_readiness_certification_identity(identity)
    )


def hash_transition_certification_identity(
    identity: V45TransitionCertificationIdentity,
) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_transition_certification_identity(identity)
    )


def hash_phase_chain_completeness_identity(
    identity: PhaseChainCompletenessIdentity,
) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_phase_chain_completeness_identity(identity)
    )


def hash_phase_evidence_reference(record: PhaseEvidenceReference) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_phase_evidence_reference(record)
    )


def hash_readiness_certification_record(record: ReadinessCertificationRecord) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_readiness_certification_record(record)
    )


def hash_transition_certification_record(record: TransitionCertificationRecord) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_transition_certification_record(record)
    )


def hash_completeness_summary(record: CompletenessSummaryRecord) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_completeness_summary(record)
    )


def hash_unresolved_diagnostic_visibility(
    record: UnresolvedDiagnosticVisibilityRecord,
) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_unresolved_diagnostic_visibility(record)
    )


def hash_limitation_visibility(record: LimitationVisibilityRecord) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_limitation_visibility(record)
    )


def hash_blocker_warning_visibility(record: BlockerWarningVisibilityRecord) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_blocker_warning_visibility(record)
    )


def hash_v4_5_planning_constraint(record: V45PlanningConstraintRecord) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_v4_5_planning_constraint(record)
    )


def hash_v4_5_drift_integrity_preparation(
    record: V45DriftIntegrityPreparationRecord,
) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_v4_5_drift_integrity_preparation(record)
    )


def hash_non_operational_certification(record: NonOperationalCertificationRecord) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_non_operational_certification(record)
    )


def hash_readiness_provenance_continuity(
    record: ReadinessProvenanceContinuityRecord,
) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_readiness_provenance_continuity(record)
    )


def hash_readiness_lineage_continuity(record: ReadinessLineageContinuityRecord) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_readiness_lineage_continuity(record)
    )


def hash_readiness_replay_rollback_evidence(
    record: ReadinessReplayRollbackEvidenceRecord,
) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_readiness_replay_rollback_evidence(record)
    )


def hash_transition_summary(record: TransitionSummaryRecord) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_transition_summary(record)
    )


def hash_boundary_readiness_transition_certification(
    certification: BoundaryReadinessTransitionCertification,
) -> str:
    return deterministic_boundary_readiness_transition_hash(
        export_boundary_readiness_transition_certification(certification)
    )
