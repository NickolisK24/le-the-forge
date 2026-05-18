"""Deterministic hashing for v4.4 blocker resolution closeout evidence."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_4_boundary_blocker_resolution_models import (
    BlockerClassificationIdentity,
    BlockerClassificationRecord,
    BlockerResolutionLineageRecord,
    BlockerResolutionProvenanceRecord,
    BlockerResolutionReplayRollbackRecord,
    BoundaryBlockerResolutionCloseoutPreparation,
    CloseoutEligibilityIdentity,
    CloseoutEligibilityRecord,
    CloseoutPreparationSummaryRecord,
    EscalationRecord,
    FailVisibleExplanationRecord,
    InheritedConstraintRecord,
    InheritedProhibitionRecord,
    NonOperationalBlockerCertificationRecord,
    Phase8ReadinessEvidenceReference,
    UnresolvedLimitationRecord,
    V45InheritedPlanningBoundaryIdentity,
    V45InheritedPlanningBoundaryRecord,
    WarningClassificationIdentity,
    WarningClassificationRecord,
)
from .v4_4_boundary_blocker_resolution_serialization import (
    export_blocker_classification_identity,
    export_blocker_classification_record,
    export_blocker_resolution_lineage,
    export_blocker_resolution_provenance,
    export_blocker_resolution_replay_rollback,
    export_boundary_blocker_resolution_closeout_preparation,
    export_closeout_eligibility_identity,
    export_closeout_eligibility_record,
    export_closeout_preparation_summary,
    export_escalation_record,
    export_fail_visible_explanation_record,
    export_inherited_constraint_record,
    export_inherited_prohibition_record,
    export_non_operational_blocker_certification,
    export_phase8_readiness_evidence_reference,
    export_unresolved_limitation_record,
    export_v4_5_inherited_planning_boundary_identity,
    export_v4_5_inherited_planning_boundary_record,
    export_warning_classification_identity,
    export_warning_classification_record,
    stable_serialize_boundary_blocker_resolution,
)


def deterministic_boundary_blocker_resolution_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_boundary_blocker_resolution(payload).encode("utf-8")
    ).hexdigest()


def hash_blocker_classification_identity(identity: BlockerClassificationIdentity) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_blocker_classification_identity(identity)
    )


def hash_warning_classification_identity(identity: WarningClassificationIdentity) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_warning_classification_identity(identity)
    )


def hash_closeout_eligibility_identity(identity: CloseoutEligibilityIdentity) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_closeout_eligibility_identity(identity)
    )


def hash_v4_5_inherited_planning_boundary_identity(
    identity: V45InheritedPlanningBoundaryIdentity,
) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_v4_5_inherited_planning_boundary_identity(identity)
    )


def hash_phase8_readiness_evidence_reference(
    record: Phase8ReadinessEvidenceReference,
) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_phase8_readiness_evidence_reference(record)
    )


def hash_blocker_classification_record(record: BlockerClassificationRecord) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_blocker_classification_record(record)
    )


def hash_warning_classification_record(record: WarningClassificationRecord) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_warning_classification_record(record)
    )


def hash_inherited_prohibition_record(record: InheritedProhibitionRecord) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_inherited_prohibition_record(record)
    )


def hash_inherited_constraint_record(record: InheritedConstraintRecord) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_inherited_constraint_record(record)
    )


def hash_unresolved_limitation_record(record: UnresolvedLimitationRecord) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_unresolved_limitation_record(record)
    )


def hash_escalation_record(record: EscalationRecord) -> str:
    return deterministic_boundary_blocker_resolution_hash(export_escalation_record(record))


def hash_closeout_eligibility_record(record: CloseoutEligibilityRecord) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_closeout_eligibility_record(record)
    )


def hash_v4_5_inherited_planning_boundary_record(
    record: V45InheritedPlanningBoundaryRecord,
) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_v4_5_inherited_planning_boundary_record(record)
    )


def hash_fail_visible_explanation_record(record: FailVisibleExplanationRecord) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_fail_visible_explanation_record(record)
    )


def hash_non_operational_blocker_certification(
    record: NonOperationalBlockerCertificationRecord,
) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_non_operational_blocker_certification(record)
    )


def hash_blocker_resolution_provenance(record: BlockerResolutionProvenanceRecord) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_blocker_resolution_provenance(record)
    )


def hash_blocker_resolution_lineage(record: BlockerResolutionLineageRecord) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_blocker_resolution_lineage(record)
    )


def hash_blocker_resolution_replay_rollback(
    record: BlockerResolutionReplayRollbackRecord,
) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_blocker_resolution_replay_rollback(record)
    )


def hash_closeout_preparation_summary(record: CloseoutPreparationSummaryRecord) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_closeout_preparation_summary(record)
    )


def hash_boundary_blocker_resolution_closeout_preparation(
    certification: BoundaryBlockerResolutionCloseoutPreparation,
) -> str:
    return deterministic_boundary_blocker_resolution_hash(
        export_boundary_blocker_resolution_closeout_preparation(certification)
    )
