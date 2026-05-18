"""Deterministic v4.4 boundary continuity and integrity certification models.

The v4.4 Phase 7 layer certifies continuity and integrity visibility across the
completed v4.4 boundary intelligence chain. Certification is descriptive
governance evidence only: it does not authorize execution, approve
orchestration, imply production readiness, unlock planner integration, make
recommendations or decisions, activate runtime behavior, or mutate state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_4_BOUNDARY_CONTINUITY_INTEGRITY_PHASE_ID = "v4_4_boundary_continuity_integrity"
V4_4_BOUNDARY_CONTINUITY_INTEGRITY_SCHEMA_VERSION = "v4_4.boundary_continuity_integrity.1"
V4_4_BOUNDARY_CONTINUITY_INTEGRITY_REPORT_SCHEMA_VERSION = (
    "v4_4.boundary_continuity_integrity_report.1"
)
V4_4_BOUNDARY_CONTINUITY_INTEGRITY_GENERATED_AT = "2026-05-18T00:00:00+00:00"
V4_4_BOUNDARY_CONTINUITY_INTEGRITY_STATUS_STABLE = (
    "v4_4_boundary_continuity_integrity_stable"
)
V4_4_BOUNDARY_CONTINUITY_INTEGRITY_STATUS_BLOCKED = (
    "v4_4_boundary_continuity_integrity_blocked"
)
V4_4_BOUNDARY_CONTINUITY_INTEGRITY_PURPOSE = (
    "deterministic_governance_safe_boundary_continuity_integrity_certification_descriptive_only"
)
V4_4_BOUNDARY_CONTINUITY_INTEGRITY_CLASSIFICATION = (
    "governance_safe_descriptive_boundary_continuity_integrity_certification"
)

CERTIFICATION_STATE_CERTIFIED = "certified"
CERTIFICATION_STATE_PARTIALLY_CERTIFIED = "partially_certified"
CERTIFICATION_STATE_UNCERTIFIED = "uncertified"
CERTIFICATION_STATE_CONTINUOUS = "continuous"
CERTIFICATION_STATE_DISCONTINUOUS = "discontinuous"
CERTIFICATION_STATE_INTEGRITY_SAFE = "integrity_safe"
CERTIFICATION_STATE_INTEGRITY_WARNING = "integrity_warning"
CERTIFICATION_STATE_INTEGRITY_BLOCKED = "integrity_blocked"
CERTIFICATION_STATE_REPLAY_SAFE = "replay_safe"
CERTIFICATION_STATE_ROLLBACK_SAFE = "rollback_safe"
CERTIFICATION_STATE_PROVENANCE_SAFE = "provenance_safe"
CERTIFICATION_STATE_LINEAGE_SAFE = "lineage_safe"
CERTIFICATION_STATE_UNSUPPORTED = "unsupported"
CERTIFICATION_STATE_PROHIBITED = "prohibited"
CERTIFICATION_STATE_STALE = "stale"
CERTIFICATION_STATE_CONFLICTING = "conflicting"
CERTIFICATION_STATE_AMBIGUOUS = "ambiguous"
CERTIFICATION_STATE_DEGRADED = "degraded"
BOUNDARY_CONTINUITY_INTEGRITY_STATES: tuple[str, ...] = (
    CERTIFICATION_STATE_CERTIFIED,
    CERTIFICATION_STATE_PARTIALLY_CERTIFIED,
    CERTIFICATION_STATE_UNCERTIFIED,
    CERTIFICATION_STATE_CONTINUOUS,
    CERTIFICATION_STATE_DISCONTINUOUS,
    CERTIFICATION_STATE_INTEGRITY_SAFE,
    CERTIFICATION_STATE_INTEGRITY_WARNING,
    CERTIFICATION_STATE_INTEGRITY_BLOCKED,
    CERTIFICATION_STATE_REPLAY_SAFE,
    CERTIFICATION_STATE_ROLLBACK_SAFE,
    CERTIFICATION_STATE_PROVENANCE_SAFE,
    CERTIFICATION_STATE_LINEAGE_SAFE,
    CERTIFICATION_STATE_UNSUPPORTED,
    CERTIFICATION_STATE_PROHIBITED,
    CERTIFICATION_STATE_STALE,
    CERTIFICATION_STATE_CONFLICTING,
    CERTIFICATION_STATE_AMBIGUOUS,
    CERTIFICATION_STATE_DEGRADED,
)
FAIL_VISIBLE_CONTINUITY_INTEGRITY_STATES: tuple[str, ...] = (
    CERTIFICATION_STATE_PARTIALLY_CERTIFIED,
    CERTIFICATION_STATE_UNCERTIFIED,
    CERTIFICATION_STATE_DISCONTINUOUS,
    CERTIFICATION_STATE_INTEGRITY_WARNING,
    CERTIFICATION_STATE_INTEGRITY_BLOCKED,
    CERTIFICATION_STATE_UNSUPPORTED,
    CERTIFICATION_STATE_PROHIBITED,
    CERTIFICATION_STATE_STALE,
    CERTIFICATION_STATE_CONFLICTING,
    CERTIFICATION_STATE_AMBIGUOUS,
    CERTIFICATION_STATE_DEGRADED,
)

V4_4_BOUNDARY_CONTINUITY_INTEGRITY_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
    "enabled_runtime_execution_count",
    "enabled_orchestration_authorization_count",
    "enabled_orchestration_approval_count",
    "enabled_dispatch_execution_count",
    "enabled_routing_execution_count",
    "enabled_scheduling_execution_count",
    "enabled_recommendation_count",
    "enabled_decision_count",
    "enabled_certification_authorization_count",
    "enabled_integrity_approval_count",
    "enabled_operational_mutation_count",
)

V4_4_BOUNDARY_CONTINUITY_INTEGRITY_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "continuity_ordering_stability",
    "integrity_ordering_stability",
    "continuity_serialization_stability",
    "integrity_serialization_stability",
    "continuity_hashing_stability",
    "integrity_hashing_stability",
    "phase_evidence_reference_stability",
    "certification_limitation_visibility",
    "fail_visible_diagnostic_preservation",
    "replay_safe_evidence",
    "rollback_safe_evidence",
    "provenance_continuity_preservation",
    "lineage_continuity_preservation",
    "governance_safe_descriptive_only_enforcement",
    "non_operational_certification",
)

V4_4_BOUNDARY_CONTINUITY_INTEGRITY_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "v4.4 Phase 7 certifies boundary continuity and integrity visibility only.",
    "v4.4 Phase 7 certification does not authorize orchestration behavior.",
    "v4.4 Phase 7 integrity status does not imply production readiness.",
    "v4.4 Phase 7 continuity status does not activate runtime behavior.",
    "v4.4 Phase 7 does not execute orchestration.",
    "v4.4 Phase 7 does not authorize or approve orchestration.",
    "v4.4 Phase 7 does not dispatch, route, traverse, schedule, or sequence orchestration.",
    "v4.4 Phase 7 does not recommend, rank, score, select, optimize, or decide orchestration.",
    "v4.4 Phase 7 does not integrate planners or consume production bundles.",
    "v4.4 Phase 7 does not repair, remediate, or mutate runtime or operational state.",
)

V4_4_BOUNDARY_CONTINUITY_INTEGRITY_EXPLICIT_PROHIBITIONS: tuple[str, ...] = (
    "No certification system grants runtime authority.",
    "No integrity result authorizes orchestration behavior.",
    "No continuity result is a production readiness, recommendation, decision, approval, or activation signal.",
    "No certification output becomes an authorization signal.",
    "No integrity status becomes a production-consumption signal.",
    "No continuity status becomes runtime activation.",
    "No orchestration execution exists.",
    "No orchestration authorization exists.",
    "No orchestration approval exists.",
    "No orchestration dispatch exists.",
    "No orchestration routing exists.",
    "No orchestration traversal exists.",
    "No orchestration scheduling exists.",
    "No orchestration sequencing exists.",
    "No orchestration recommendation exists.",
    "No orchestration ranking, scoring, selection, or optimization exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No automatic remediation exists.",
    "No automatic repair exists.",
    "No runtime mutation exists.",
    "No operational mutation exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class BoundaryContinuityCertificationIdentity:
    continuity_certification_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    phase_chain_reference: str
    continuity_reference: str
    provenance_reference: str
    lineage_reference: str
    replay_rollback_reference: str
    non_operational_reference: str
    purpose: str = V4_4_BOUNDARY_CONTINUITY_INTEGRITY_PURPOSE
    deterministic: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    governance_safe: bool = True
    integrity_safe: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    non_operational: bool = True
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    certification_authorization_enabled: bool = False
    integrity_approval_enabled: bool = False
    operational_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class BoundaryIntegrityCertificationIdentity:
    integrity_certification_id: str
    phase_id: str
    integrity_reference: str
    diagnostic_reference: str
    limitation_reference: str
    deterministic_order: int
    descriptive_only: bool = True
    non_operational: bool = True
    certification_authorization_enabled: bool = False
    integrity_approval_enabled: bool = False


@dataclass(frozen=True)
class PhaseChainCertificationIdentity:
    phase_chain_id: str
    phase_ids: tuple[str, ...]
    phase_chain_state: str
    deterministic_order: int
    descriptive_only: bool = True
    runtime_activation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "phase_ids")


@dataclass(frozen=True)
class PhaseEvidenceReference:
    evidence_id: str
    phase_id: str
    phase_label: str
    report_reference: str
    hash_reference: str
    certification_state: str
    continuity_state: str
    integrity_state: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ContinuityCertificationRecord:
    continuity_id: str
    subject_id: str
    continuity_state: str
    certification_state: str
    continuity_reference_ids: tuple[str, ...]
    continuity_reason: str
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    runtime_activation_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "continuity_reference_ids")


@dataclass(frozen=True)
class IntegrityCertificationRecord:
    integrity_id: str
    subject_id: str
    integrity_state: str
    certification_state: str
    integrity_reference_ids: tuple[str, ...]
    integrity_reason: str
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    certification_authorization_enabled: bool = False
    integrity_approval_enabled: bool = False
    production_readiness_inferred: bool = False
    planner_integration_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "integrity_reference_ids")


@dataclass(frozen=True)
class CertificationLimitationRecord:
    limitation_id: str
    subject_id: str
    limitation_state: str
    limitation_type: str
    limitation_reason: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    automatic_remediation_enabled: bool = False
    automatic_repair_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class CertificationDiagnosticRecord:
    diagnostic_id: str
    subject_id: str
    diagnostic_state: str
    severity: str
    diagnostic_summary: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    authorization_enabled: bool = False
    approval_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    automatic_remediation_enabled: bool = False
    automatic_repair_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ProvenanceContinuityRecord:
    provenance_id: str
    source_reference_ids: tuple[str, ...]
    source_hash_references: tuple[str, ...]
    provenance_state: str
    deterministic_order: int
    provenance_continuity_preserved: bool = True
    hidden_source_inference_used: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("source_reference_ids", "source_hash_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class LineageContinuityRecord:
    lineage_id: str
    lineage_reference_ids: tuple[str, ...]
    lineage_hash_references: tuple[str, ...]
    lineage_state: str
    deterministic_order: int
    lineage_continuity_preserved: bool = True
    ambiguous_lineage_inferred: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("lineage_reference_ids", "lineage_hash_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class ReplayRollbackSafetyRecord:
    safety_id: str
    replay_state: str
    rollback_state: str
    phase_evidence_ids: tuple[str, ...]
    replay_evidence_ids: tuple[str, ...]
    rollback_evidence_ids: tuple[str, ...]
    deterministic_order: int
    replay_safe: bool = True
    rollback_safe: bool = True
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("phase_evidence_ids", "replay_evidence_ids", "rollback_evidence_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CertificationSummaryRecord:
    summary_id: str
    certification_state: str
    continuity_state: str
    integrity_state: str
    summary_reference_ids: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    non_operational: bool = True
    authorization_signal_enabled: bool = False
    production_readiness_signal_enabled: bool = False
    runtime_activation_signal_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "summary_reference_ids")


@dataclass(frozen=True)
class BoundaryContinuityIntegrityCertification:
    continuity_identity: BoundaryContinuityCertificationIdentity
    integrity_identity: BoundaryIntegrityCertificationIdentity
    phase_chain_identity: PhaseChainCertificationIdentity
    phase_evidence_references: tuple[PhaseEvidenceReference, ...]
    continuity_records: tuple[ContinuityCertificationRecord, ...]
    integrity_records: tuple[IntegrityCertificationRecord, ...]
    limitation_records: tuple[CertificationLimitationRecord, ...]
    diagnostic_records: tuple[CertificationDiagnosticRecord, ...]
    provenance_record: ProvenanceContinuityRecord
    lineage_record: LineageContinuityRecord
    replay_rollback_record: ReplayRollbackSafetyRecord
    certification_summaries: tuple[CertificationSummaryRecord, ...]
    deterministic_guarantees: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    descriptive_only: bool = True
    non_operational: bool = True
    non_authoritative: bool = True
    non_authorizing: bool = True
    non_approving: bool = True
    non_recommending: bool = True
    non_deciding: bool = True
    non_remediating: bool = True
    non_mutating: bool = True
    runtime_readiness_inference_disabled: bool = True
    runtime_execution_enabled: bool = False
    orchestration_runtime_behavior_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    certification_authorization_enabled: bool = False
    integrity_approval_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    automatic_remediation_enabled: bool = False
    automatic_repair_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "phase_evidence_references",
            "continuity_records",
            "integrity_records",
            "limitation_records",
            "diagnostic_records",
            "certification_summaries",
            "deterministic_guarantees",
            "explicit_limitations",
            "explicit_prohibitions",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))


def default_continuity_identity() -> BoundaryContinuityCertificationIdentity:
    return BoundaryContinuityCertificationIdentity(
        continuity_certification_id="v4_4_boundary_continuity_certification",
        phase_id=V4_4_BOUNDARY_CONTINUITY_INTEGRITY_PHASE_ID,
        schema_version=V4_4_BOUNDARY_CONTINUITY_INTEGRITY_SCHEMA_VERSION,
        generated_at=V4_4_BOUNDARY_CONTINUITY_INTEGRITY_GENERATED_AT,
        classification=V4_4_BOUNDARY_CONTINUITY_INTEGRITY_CLASSIFICATION,
        phase_chain_reference="v4_4_phase_1_through_6_boundary_chain",
        continuity_reference="v4_4_boundary_continuity_certification_records",
        provenance_reference="v4_4_boundary_provenance_continuity",
        lineage_reference="v4_4_boundary_lineage_continuity",
        replay_rollback_reference="v4_4_boundary_replay_rollback_safety",
        non_operational_reference="v4_4_boundary_continuity_integrity_non_operational_certification",
    )


def default_integrity_identity() -> BoundaryIntegrityCertificationIdentity:
    return BoundaryIntegrityCertificationIdentity(
        integrity_certification_id="v4_4_boundary_integrity_certification",
        phase_id=V4_4_BOUNDARY_CONTINUITY_INTEGRITY_PHASE_ID,
        integrity_reference="v4_4_boundary_integrity_certification_records",
        diagnostic_reference="v4_4_boundary_integrity_diagnostics",
        limitation_reference="v4_4_boundary_certification_limitations",
        deterministic_order=1,
    )


def default_phase_ids() -> tuple[str, ...]:
    return (
        "v4_4_boundary_intelligence_foundations",
        "v4_4_boundary_inheritance_refinement",
        "v4_4_boundary_conflict_drift",
        "v4_4_cross_boundary_consistency",
        "v4_4_boundary_segmentation_scope",
        "v4_4_boundary_explainability_aggregation",
    )


def default_phase_chain_identity() -> PhaseChainCertificationIdentity:
    return PhaseChainCertificationIdentity(
        phase_chain_id="v4_4_boundary_intelligence_phase_chain",
        phase_ids=default_phase_ids(),
        phase_chain_state=CERTIFICATION_STATE_CONTINUOUS,
        deterministic_order=1,
    )


def default_phase_evidence_references() -> tuple[PhaseEvidenceReference, ...]:
    definitions = (
        ("evidence_boundary_foundations", "v4_4_boundary_intelligence_foundations", "Phase 1 boundary foundations", CERTIFICATION_STATE_CERTIFIED, CERTIFICATION_STATE_CONTINUOUS, CERTIFICATION_STATE_INTEGRITY_SAFE),
        ("evidence_inheritance_refinement", "v4_4_boundary_inheritance_refinement", "Phase 2 inheritance refinement", CERTIFICATION_STATE_PARTIALLY_CERTIFIED, CERTIFICATION_STATE_CONTINUOUS, CERTIFICATION_STATE_INTEGRITY_WARNING),
        ("evidence_conflict_drift", "v4_4_boundary_conflict_drift", "Phase 3 conflict drift", CERTIFICATION_STATE_CERTIFIED, CERTIFICATION_STATE_DISCONTINUOUS, CERTIFICATION_STATE_INTEGRITY_WARNING),
        ("evidence_cross_boundary_consistency", "v4_4_cross_boundary_consistency", "Phase 4 cross-boundary consistency", CERTIFICATION_STATE_CERTIFIED, CERTIFICATION_STATE_CONTINUOUS, CERTIFICATION_STATE_INTEGRITY_SAFE),
        ("evidence_segmentation_scope", "v4_4_boundary_segmentation_scope", "Phase 5 segmentation scope", CERTIFICATION_STATE_PARTIALLY_CERTIFIED, CERTIFICATION_STATE_CONTINUOUS, CERTIFICATION_STATE_INTEGRITY_BLOCKED),
        ("evidence_explainability_aggregation", "v4_4_boundary_explainability_aggregation", "Phase 6 explainability aggregation", CERTIFICATION_STATE_CERTIFIED, CERTIFICATION_STATE_CONTINUOUS, CERTIFICATION_STATE_INTEGRITY_SAFE),
    )
    return tuple(
        PhaseEvidenceReference(
            evidence_id=evidence_id,
            phase_id=phase_id,
            phase_label=phase_label,
            report_reference=f"docs/generated/{phase_id}_report.json",
            hash_reference=f"{phase_id}.deterministic_report_hash",
            certification_state=certification_state,
            continuity_state=continuity_state,
            integrity_state=integrity_state,
            evidence_reference_ids=(phase_id, evidence_id, f"{phase_id}.deterministic_report_hash"),
            deterministic_order=index,
            fail_visible=(
                certification_state in FAIL_VISIBLE_CONTINUITY_INTEGRITY_STATES
                or continuity_state in FAIL_VISIBLE_CONTINUITY_INTEGRITY_STATES
                or integrity_state in FAIL_VISIBLE_CONTINUITY_INTEGRITY_STATES
            ),
        )
        for index, (
            evidence_id,
            phase_id,
            phase_label,
            certification_state,
            continuity_state,
            integrity_state,
        ) in enumerate(definitions, start=1)
    )


def default_continuity_records() -> tuple[ContinuityCertificationRecord, ...]:
    definitions = (
        ("continuity_phase_chain", "v4_4_boundary_intelligence_phase_chain", CERTIFICATION_STATE_CONTINUOUS, CERTIFICATION_STATE_CERTIFIED),
        ("continuity_boundary_foundations", "v4_4_boundary_intelligence_foundations", CERTIFICATION_STATE_CONTINUOUS, CERTIFICATION_STATE_CERTIFIED),
        ("continuity_inheritance_refinement", "v4_4_boundary_inheritance_refinement", CERTIFICATION_STATE_CONTINUOUS, CERTIFICATION_STATE_PARTIALLY_CERTIFIED),
        ("continuity_conflict_drift", "v4_4_boundary_conflict_drift", CERTIFICATION_STATE_DISCONTINUOUS, CERTIFICATION_STATE_PARTIALLY_CERTIFIED),
        ("continuity_cross_boundary_consistency", "v4_4_cross_boundary_consistency", CERTIFICATION_STATE_CONTINUOUS, CERTIFICATION_STATE_CERTIFIED),
        ("continuity_segmentation_scope", "v4_4_boundary_segmentation_scope", CERTIFICATION_STATE_CONTINUOUS, CERTIFICATION_STATE_PARTIALLY_CERTIFIED),
        ("continuity_explainability_aggregation", "v4_4_boundary_explainability_aggregation", CERTIFICATION_STATE_CONTINUOUS, CERTIFICATION_STATE_CERTIFIED),
        ("continuity_replay_safety", "v4_4_boundary_replay_safety", CERTIFICATION_STATE_REPLAY_SAFE, CERTIFICATION_STATE_CERTIFIED),
        ("continuity_rollback_safety", "v4_4_boundary_rollback_safety", CERTIFICATION_STATE_ROLLBACK_SAFE, CERTIFICATION_STATE_CERTIFIED),
        ("continuity_provenance", "v4_4_boundary_provenance", CERTIFICATION_STATE_PROVENANCE_SAFE, CERTIFICATION_STATE_CERTIFIED),
        ("continuity_lineage", "v4_4_boundary_lineage", CERTIFICATION_STATE_LINEAGE_SAFE, CERTIFICATION_STATE_CERTIFIED),
    )
    return tuple(
        ContinuityCertificationRecord(
            continuity_id=continuity_id,
            subject_id=subject_id,
            continuity_state=continuity_state,
            certification_state=certification_state,
            continuity_reference_ids=(subject_id, continuity_id, V4_4_BOUNDARY_CONTINUITY_INTEGRITY_PHASE_ID),
            continuity_reason=f"{continuity_state} continuity certification is visible and non-authorizing",
            deterministic_order=index,
            fail_visible=(
                continuity_state in FAIL_VISIBLE_CONTINUITY_INTEGRITY_STATES
                or certification_state in FAIL_VISIBLE_CONTINUITY_INTEGRITY_STATES
            ),
        )
        for index, (continuity_id, subject_id, continuity_state, certification_state) in enumerate(
            definitions,
            start=1,
        )
    )


def default_integrity_records() -> tuple[IntegrityCertificationRecord, ...]:
    definitions = (
        ("integrity_phase_evidence", "phase_evidence_references", CERTIFICATION_STATE_INTEGRITY_SAFE, CERTIFICATION_STATE_CERTIFIED),
        ("integrity_source_references", "source_evidence_references", CERTIFICATION_STATE_INTEGRITY_SAFE, CERTIFICATION_STATE_CERTIFIED),
        ("integrity_serialization", "deterministic_serialization", CERTIFICATION_STATE_INTEGRITY_SAFE, CERTIFICATION_STATE_CERTIFIED),
        ("integrity_hashing", "deterministic_hashing", CERTIFICATION_STATE_INTEGRITY_SAFE, CERTIFICATION_STATE_CERTIFIED),
        ("integrity_diagnostics", "fail_visible_diagnostics", CERTIFICATION_STATE_INTEGRITY_WARNING, CERTIFICATION_STATE_PARTIALLY_CERTIFIED),
        ("integrity_explainability", "explainability_records", CERTIFICATION_STATE_INTEGRITY_SAFE, CERTIFICATION_STATE_CERTIFIED),
        ("integrity_provenance", "provenance_continuity", CERTIFICATION_STATE_INTEGRITY_SAFE, CERTIFICATION_STATE_CERTIFIED),
        ("integrity_lineage", "lineage_continuity", CERTIFICATION_STATE_INTEGRITY_SAFE, CERTIFICATION_STATE_CERTIFIED),
        ("integrity_limitations", "certification_limitations", CERTIFICATION_STATE_INTEGRITY_BLOCKED, CERTIFICATION_STATE_PARTIALLY_CERTIFIED),
        ("integrity_summary", "certification_summary", CERTIFICATION_STATE_INTEGRITY_SAFE, CERTIFICATION_STATE_CERTIFIED),
    )
    return tuple(
        IntegrityCertificationRecord(
            integrity_id=integrity_id,
            subject_id=subject_id,
            integrity_state=integrity_state,
            certification_state=certification_state,
            integrity_reference_ids=(subject_id, integrity_id, V4_4_BOUNDARY_CONTINUITY_INTEGRITY_PHASE_ID),
            integrity_reason=f"{integrity_state} integrity certification is visible and non-approving",
            deterministic_order=index,
            fail_visible=(
                integrity_state in FAIL_VISIBLE_CONTINUITY_INTEGRITY_STATES
                or certification_state in FAIL_VISIBLE_CONTINUITY_INTEGRITY_STATES
            ),
        )
        for index, (integrity_id, subject_id, integrity_state, certification_state) in enumerate(
            definitions,
            start=1,
        )
    )


def default_limitation_records() -> tuple[CertificationLimitationRecord, ...]:
    definitions = (
        ("limitation_unsupported_state", "unsupported_boundary_visibility", CERTIFICATION_STATE_UNSUPPORTED),
        ("limitation_prohibited_authority", "prohibited_authority_visibility", CERTIFICATION_STATE_PROHIBITED),
        ("limitation_stale_evidence", "stale_evidence_visibility", CERTIFICATION_STATE_STALE),
        ("limitation_conflicting_chain", "conflicting_chain_visibility", CERTIFICATION_STATE_CONFLICTING),
        ("limitation_ambiguous_scope", "ambiguous_scope_visibility", CERTIFICATION_STATE_AMBIGUOUS),
        ("limitation_degraded_lineage", "degraded_lineage_visibility", CERTIFICATION_STATE_DEGRADED),
        ("limitation_uncertified_runtime", "runtime_readiness_visibility", CERTIFICATION_STATE_UNCERTIFIED),
    )
    return tuple(
        CertificationLimitationRecord(
            limitation_id=limitation_id,
            subject_id=subject_id,
            limitation_state=limitation_state,
            limitation_type=f"{limitation_state}_certification_limitation",
            limitation_reason=f"{limitation_state} limitation remains visible and non-remediating",
            evidence_reference_ids=(subject_id, limitation_id),
            deterministic_order=index,
        )
        for index, (limitation_id, subject_id, limitation_state) in enumerate(definitions, start=1)
    )


def _severity_for_state(state: str) -> str:
    return {
        CERTIFICATION_STATE_PROHIBITED: "prohibited",
        CERTIFICATION_STATE_INTEGRITY_BLOCKED: "blocked",
        CERTIFICATION_STATE_UNCERTIFIED: "blocked",
        CERTIFICATION_STATE_UNSUPPORTED: "warning",
        CERTIFICATION_STATE_STALE: "warning",
        CERTIFICATION_STATE_CONFLICTING: "warning",
        CERTIFICATION_STATE_AMBIGUOUS: "warning",
        CERTIFICATION_STATE_DEGRADED: "warning",
        CERTIFICATION_STATE_INTEGRITY_WARNING: "warning",
        CERTIFICATION_STATE_DISCONTINUOUS: "warning",
    }.get(state, "informational")


def default_diagnostic_records() -> tuple[CertificationDiagnosticRecord, ...]:
    subjects = (
        *default_limitation_records(),
        default_integrity_records()[4],
        default_integrity_records()[8],
        default_continuity_records()[3],
    )
    records: list[CertificationDiagnosticRecord] = []
    for index, subject in enumerate(subjects, start=1):
        state = (
            getattr(subject, "limitation_state", None)
            or getattr(subject, "integrity_state", None)
            or getattr(subject, "continuity_state")
        )
        subject_id = (
            getattr(subject, "limitation_id", None)
            or getattr(subject, "integrity_id", None)
            or getattr(subject, "continuity_id")
        )
        records.append(
            CertificationDiagnosticRecord(
                diagnostic_id=f"diagnostic_{subject_id}",
                subject_id=str(subject_id),
                diagnostic_state=str(state),
                severity=_severity_for_state(str(state)),
                diagnostic_summary=f"{state} certification diagnostic remains visible without action trigger",
                evidence_reference_ids=(str(subject_id), str(state)),
                deterministic_order=index,
                fail_visible=str(state) in FAIL_VISIBLE_CONTINUITY_INTEGRITY_STATES,
            )
        )
    return tuple(records)


def default_provenance_record() -> ProvenanceContinuityRecord:
    phases = default_phase_evidence_references()
    return ProvenanceContinuityRecord(
        provenance_id="v4_4_boundary_provenance_continuity",
        source_reference_ids=tuple(phase.report_reference for phase in phases),
        source_hash_references=tuple(phase.hash_reference for phase in phases),
        provenance_state=CERTIFICATION_STATE_PROVENANCE_SAFE,
        deterministic_order=1,
    )


def default_lineage_record() -> LineageContinuityRecord:
    return LineageContinuityRecord(
        lineage_id="v4_4_boundary_lineage_continuity",
        lineage_reference_ids=default_phase_ids() + (V4_4_BOUNDARY_CONTINUITY_INTEGRITY_PHASE_ID,),
        lineage_hash_references=tuple(f"{phase_id}.deterministic_hash_reference" for phase_id in default_phase_ids()),
        lineage_state=CERTIFICATION_STATE_LINEAGE_SAFE,
        deterministic_order=1,
    )


def default_replay_rollback_record() -> ReplayRollbackSafetyRecord:
    evidence_ids = tuple(phase.evidence_id for phase in default_phase_evidence_references())
    return ReplayRollbackSafetyRecord(
        safety_id="v4_4_boundary_replay_rollback_safety",
        replay_state=CERTIFICATION_STATE_REPLAY_SAFE,
        rollback_state=CERTIFICATION_STATE_ROLLBACK_SAFE,
        phase_evidence_ids=evidence_ids,
        replay_evidence_ids=evidence_ids,
        rollback_evidence_ids=evidence_ids,
        deterministic_order=1,
    )


def default_certification_summaries() -> tuple[CertificationSummaryRecord, ...]:
    return (
        CertificationSummaryRecord(
            summary_id="summary_boundary_chain_certification",
            certification_state=CERTIFICATION_STATE_CERTIFIED,
            continuity_state=CERTIFICATION_STATE_CONTINUOUS,
            integrity_state=CERTIFICATION_STATE_INTEGRITY_SAFE,
            summary_reference_ids=("v4_4_boundary_intelligence_phase_chain",),
            deterministic_order=1,
        ),
        CertificationSummaryRecord(
            summary_id="summary_boundary_limitations_visible",
            certification_state=CERTIFICATION_STATE_PARTIALLY_CERTIFIED,
            continuity_state=CERTIFICATION_STATE_DISCONTINUOUS,
            integrity_state=CERTIFICATION_STATE_INTEGRITY_WARNING,
            summary_reference_ids=("certification_limitations", "fail_visible_diagnostics"),
            deterministic_order=2,
        ),
        CertificationSummaryRecord(
            summary_id="summary_runtime_readiness_not_certified",
            certification_state=CERTIFICATION_STATE_UNCERTIFIED,
            continuity_state=CERTIFICATION_STATE_DISCONTINUOUS,
            integrity_state=CERTIFICATION_STATE_INTEGRITY_BLOCKED,
            summary_reference_ids=("runtime_readiness_visibility", "non_operational_certification"),
            deterministic_order=3,
        ),
    )


def default_boundary_continuity_integrity_certification() -> BoundaryContinuityIntegrityCertification:
    return BoundaryContinuityIntegrityCertification(
        continuity_identity=default_continuity_identity(),
        integrity_identity=default_integrity_identity(),
        phase_chain_identity=default_phase_chain_identity(),
        phase_evidence_references=default_phase_evidence_references(),
        continuity_records=default_continuity_records(),
        integrity_records=default_integrity_records(),
        limitation_records=default_limitation_records(),
        diagnostic_records=default_diagnostic_records(),
        provenance_record=default_provenance_record(),
        lineage_record=default_lineage_record(),
        replay_rollback_record=default_replay_rollback_record(),
        certification_summaries=default_certification_summaries(),
        deterministic_guarantees=V4_4_BOUNDARY_CONTINUITY_INTEGRITY_DETERMINISTIC_GUARANTEES,
        explicit_limitations=V4_4_BOUNDARY_CONTINUITY_INTEGRITY_EXPLICIT_LIMITATIONS,
        explicit_prohibitions=V4_4_BOUNDARY_CONTINUITY_INTEGRITY_EXPLICIT_PROHIBITIONS,
    )
