"""Deterministic hashing for v4.4 closeout and v4.5 readiness."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_4_closeout_readiness_models import (
    CloseoutCertificationRecord,
    CloseoutInheritedConstraintRecord,
    CloseoutInheritedProhibitionRecord,
    CloseoutReadinessLineageRecord,
    CloseoutReadinessProvenanceRecord,
    CloseoutReadinessReplayRollbackRecord,
    CloseoutReadinessSummaryRecord,
    NonOperationalCloseoutCertificationRecord,
    PhaseChainEvidenceIdentity,
    PhaseChainEvidenceRecord,
    PreservedBlockerRecord,
    PreservedLimitationRecord,
    PreservedWarningRecord,
    V44CloseoutAndV45ReadinessCertification,
    V44CloseoutCertificationIdentity,
    V45InheritedLimitationRecord,
    V45PlanningBoundaryRecord,
    V45ReadinessCertificationIdentity,
    V45ReadinessCertificationRecord,
)
from .v4_4_closeout_readiness_serialization import (
    export_closeout_certification_record,
    export_closeout_identity,
    export_closeout_readiness_lineage,
    export_closeout_readiness_provenance,
    export_closeout_readiness_replay_rollback,
    export_closeout_readiness_summary,
    export_inherited_constraint_record,
    export_inherited_prohibition_record,
    export_non_operational_closeout_certification,
    export_phase_chain_evidence_identity,
    export_phase_chain_evidence_record,
    export_preserved_blocker_record,
    export_preserved_limitation_record,
    export_preserved_warning_record,
    export_readiness_identity,
    export_v4_4_closeout_readiness_certification,
    export_v4_5_inherited_limitation,
    export_v4_5_planning_boundary,
    export_v4_5_readiness_certification_record,
    stable_serialize_v4_4_closeout_readiness,
)


def deterministic_v4_4_closeout_readiness_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_v4_4_closeout_readiness(payload).encode("utf-8")
    ).hexdigest()


def hash_closeout_identity(identity: V44CloseoutCertificationIdentity) -> str:
    return deterministic_v4_4_closeout_readiness_hash(export_closeout_identity(identity))


def hash_readiness_identity(identity: V45ReadinessCertificationIdentity) -> str:
    return deterministic_v4_4_closeout_readiness_hash(export_readiness_identity(identity))


def hash_phase_chain_evidence_identity(identity: PhaseChainEvidenceIdentity) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_phase_chain_evidence_identity(identity)
    )


def hash_phase_chain_evidence_record(record: PhaseChainEvidenceRecord) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_phase_chain_evidence_record(record)
    )


def hash_closeout_certification_record(record: CloseoutCertificationRecord) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_closeout_certification_record(record)
    )


def hash_v4_5_readiness_certification_record(
    record: V45ReadinessCertificationRecord,
) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_v4_5_readiness_certification_record(record)
    )


def hash_preserved_limitation_record(record: PreservedLimitationRecord) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_preserved_limitation_record(record)
    )


def hash_preserved_blocker_record(record: PreservedBlockerRecord) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_preserved_blocker_record(record)
    )


def hash_preserved_warning_record(record: PreservedWarningRecord) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_preserved_warning_record(record)
    )


def hash_inherited_prohibition_record(record: CloseoutInheritedProhibitionRecord) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_inherited_prohibition_record(record)
    )


def hash_inherited_constraint_record(record: CloseoutInheritedConstraintRecord) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_inherited_constraint_record(record)
    )


def hash_v4_5_planning_boundary(record: V45PlanningBoundaryRecord) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_v4_5_planning_boundary(record)
    )


def hash_v4_5_inherited_limitation(record: V45InheritedLimitationRecord) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_v4_5_inherited_limitation(record)
    )


def hash_non_operational_closeout_certification(
    record: NonOperationalCloseoutCertificationRecord,
) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_non_operational_closeout_certification(record)
    )


def hash_closeout_readiness_provenance(record: CloseoutReadinessProvenanceRecord) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_closeout_readiness_provenance(record)
    )


def hash_closeout_readiness_lineage(record: CloseoutReadinessLineageRecord) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_closeout_readiness_lineage(record)
    )


def hash_closeout_readiness_replay_rollback(
    record: CloseoutReadinessReplayRollbackRecord,
) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_closeout_readiness_replay_rollback(record)
    )


def hash_closeout_readiness_summary(record: CloseoutReadinessSummaryRecord) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_closeout_readiness_summary(record)
    )


def hash_v4_4_closeout_readiness_certification(
    certification: V44CloseoutAndV45ReadinessCertification,
) -> str:
    return deterministic_v4_4_closeout_readiness_hash(
        export_v4_4_closeout_readiness_certification(certification)
    )
