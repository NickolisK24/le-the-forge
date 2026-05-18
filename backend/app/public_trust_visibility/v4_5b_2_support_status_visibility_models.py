"""Deterministic v4.5B.2 support status visibility models.

The v4.5B.2 layer models public support status visibility without enabling
support authority, approval, authorization, ranking, recommendation, execution,
remediation, runtime mutation, planner integration, production consumption, or
operational behavior.
"""

from __future__ import annotations

from dataclasses import dataclass


V4_5B_2_SUPPORT_STATUS_VISIBILITY_PHASE_ID = "v4_5b_2_support_status_visibility"
V4_5B_2_SUPPORT_STATUS_VISIBILITY_SCHEMA_VERSION = (
    "v4_5b_2.support_status_visibility.1"
)
V4_5B_2_SUPPORT_STATUS_VISIBILITY_REPORT_SCHEMA_VERSION = (
    "v4_5b_2.support_status_visibility_report.1"
)
V4_5B_2_SUPPORT_STATUS_VISIBILITY_GENERATED_AT = "2026-05-18T00:00:00+00:00"
V4_5B_2_SUPPORT_STATUS_VISIBILITY_STATUS_STABLE = (
    "v4_5b_2_support_status_visibility_stable"
)
V4_5B_2_SUPPORT_STATUS_VISIBILITY_STATUS_BLOCKED = (
    "v4_5b_2_support_status_visibility_blocked"
)
V4_5B_2_SUPPORT_STATUS_VISIBILITY_PURPOSE = (
    "deterministic_governance_safe_support_status_visibility_descriptive_only"
)
V4_5B_2_SUPPORT_STATUS_VISIBILITY_CLASSIFICATION = (
    "governance_safe_public_support_status_visibility_descriptive_only"
)

V4_5B_1_TRUST_VISIBILITY_FOUNDATION_REPORT_REFERENCE = (
    "docs/generated/v4_5b_1_trust_visibility_foundations_report.json"
)
V4_5B_1_TRUST_VISIBILITY_FOUNDATION_REPORT_HASH_REFERENCE = (
    "e6bd404e3d548fe2d016621aa94ac584614e784a592d18c722ea1f5b174a8039"
)

SUPPORT_STATUS_VISIBILITY_STATEMENT = "Support status visibility is descriptive-only."
SUPPORT_CLASSIFICATION_NON_AUTHORITY_STATEMENT = (
    "Support classifications do NOT imply authorization, approval, operational "
    "readiness, execution safety, or production enablement."
)

SUPPORT_CLASSIFICATION_TYPES: tuple[str, ...] = (
    "supported",
    "partially_supported",
    "unsupported",
    "experimental",
    "deprecated",
    "blocked",
    "unknown",
)

PUBLIC_SUPPORT_SURFACE_TYPES: tuple[str, ...] = (
    "mechanics",
    "systems",
    "planner_sections",
    "data_sources",
    "evidence_chains",
    "explainability_surfaces",
    "continuity_surfaces",
    "diagnostics_surfaces",
)

UNSUPPORTED_SUPPORT_STATE_TYPES: tuple[str, ...] = (
    "unsupported_mechanics",
    "unsupported_planner_sections",
    "unsupported_evidence_chains",
    "unsupported_explainability_surfaces",
    "unsupported_continuity_surfaces",
    "unsupported_diagnostics_surfaces",
    "unsupported_operational_states",
)

EXPERIMENTAL_DEPRECATED_VISIBILITY_TYPES: tuple[str, ...] = (
    "experimental_systems",
    "experimental_surfaces",
    "deprecated_systems",
    "deprecated_surfaces",
    "blocked_systems",
    "blocked_surfaces",
    "unknown_support_states",
)

EVIDENCE_BASED_SUPPORT_VISIBILITY_TYPES: tuple[str, ...] = (
    "evidence_backed_support",
    "partially_evidenced_support",
    "unsupported_evidence_states",
    "continuity_backed_support_visibility",
    "explainability_backed_support_visibility",
    "diagnostics_backed_support_visibility",
)

EXPLAINABILITY_SUPPORT_VISIBILITY_TYPES: tuple[str, ...] = (
    "explainability_supported_states",
    "partially_explainable_states",
    "unsupported_explainability_states",
    "continuity_explainability_visibility",
    "fail_visible_explainability_diagnostics",
)

CONTINUITY_SUPPORT_VISIBILITY_TYPES: tuple[str, ...] = (
    "continuity_supported_states",
    "partially_continuous_states",
    "unsupported_continuity_states",
    "evidence_continuity_visibility",
    "fail_visible_continuity_diagnostics",
)

SUPPORT_SUMMARY_TYPES: tuple[str, ...] = (
    "support_classification_summary",
    "surface_support_summary",
    "unsupported_state_summary",
    "experimental_deprecated_summary",
    "evidence_based_support_summary",
    "explainability_support_summary",
    "continuity_support_summary",
    "diagnostics_support_summary",
)

SUPPORT_DIAGNOSTIC_TYPES: tuple[str, ...] = (
    "missing_support_evidence",
    "unsupported_visibility_gaps",
    "unsupported_explainability_gaps",
    "unsupported_continuity_gaps",
    "blocked_visibility_states",
    "deprecated_visibility_states",
    "unknown_support_states",
    "inherited_limitation_visibility_gaps",
    "inherited_prohibition_visibility_gaps",
)

UNSUPPORTED_SUPPORT_OPERATIONAL_STATES: tuple[str, ...] = (
    "orchestration_execution",
    "orchestration_authorization",
    "orchestration_approval",
    "orchestration_dispatch",
    "orchestration_routing",
    "orchestration_traversal",
    "orchestration_scheduling",
    "orchestration_sequencing",
    "orchestration_decisions",
    "orchestration_recommendations",
    "support_based_authorization",
    "support_based_approval",
    "support_based_ranking",
    "support_based_recommendation",
    "automated_remediation",
    "automated_repair",
    "automated_mitigation",
    "automated_correction",
    "planner_integration",
    "production_consumption",
    "runtime_mutation",
    "operational_mutation",
    "implicit_operational_behavior",
)

V4_5B_2_SUPPORT_STATUS_VISIBILITY_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
    "enabled_runtime_execution_count",
    "enabled_orchestration_authorization_count",
    "enabled_orchestration_approval_count",
    "enabled_orchestration_dispatch_count",
    "enabled_orchestration_routing_count",
    "enabled_orchestration_traversal_count",
    "enabled_orchestration_scheduling_count",
    "enabled_orchestration_sequencing_count",
    "enabled_orchestration_decision_count",
    "enabled_orchestration_recommendation_count",
    "enabled_support_authorization_count",
    "enabled_support_approval_count",
    "enabled_support_ranking_count",
    "enabled_support_recommendation_count",
    "enabled_remediation_count",
    "enabled_repair_count",
    "enabled_mitigation_count",
    "enabled_auto_correction_count",
    "enabled_planner_integration_count",
    "enabled_production_consumption_count",
    "enabled_runtime_mutation_count",
    "enabled_operational_mutation_count",
)

V4_5B_2_SUPPORT_STATUS_VISIBILITY_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "deterministic_support_status_identity",
    "deterministic_support_classification_visibility",
    "deterministic_public_support_surface_visibility",
    "deterministic_unsupported_state_visibility",
    "deterministic_experimental_deprecated_visibility",
    "deterministic_evidence_based_support_visibility",
    "deterministic_explainability_support_visibility",
    "deterministic_continuity_support_visibility",
    "stable_replay_safe_serialization",
    "stable_replay_safe_hashing",
    "lineage_continuity_preserved",
    "provenance_continuity_preserved",
    "publicly_transparent_descriptive_only_support_visibility",
)

V4_5B_2_SUPPORT_STATUS_VISIBILITY_INHERITED_PROHIBITIONS: tuple[str, ...] = (
    "orchestration_execution_prohibited",
    "orchestration_authorization_prohibited",
    "orchestration_approval_prohibited",
    "orchestration_dispatch_prohibited",
    "orchestration_routing_prohibited",
    "orchestration_traversal_prohibited",
    "orchestration_scheduling_prohibited",
    "orchestration_sequencing_prohibited",
    "orchestration_decisions_prohibited",
    "orchestration_recommendations_prohibited",
    "support_based_authorization_prohibited",
    "support_based_approval_prohibited",
    "support_based_ranking_prohibited",
    "support_based_recommendation_prohibited",
    "automated_remediation_prohibited",
    "automated_repair_prohibited",
    "automated_mitigation_prohibited",
    "automated_correction_prohibited",
    "planner_integration_prohibited",
    "production_consumption_prohibited",
    "runtime_mutation_prohibited",
    "operational_mutation_prohibited",
    "implicit_operational_behavior_prohibited",
)

V4_5B_2_SUPPORT_STATUS_VISIBILITY_INHERITED_CONSTRAINTS: tuple[str, ...] = (
    "deterministic",
    "governance-safe",
    "replay-safe",
    "rollback-safe",
    "lineage-safe",
    "provenance-safe",
    "integrity-safe",
    "explainability-first",
    "fail-visible",
    "descriptive-only",
    "publicly transparent",
    "NON-operational",
    "NON-authorizing",
    "NON-approving",
    "NON-executing",
    "NON-remediating",
    "NON-runtime-mutating",
    "NON-ranking",
    "NON-recommending",
)

V4_5B_2_SUPPORT_STATUS_VISIBILITY_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "support_visibility_does_not_authorize",
    "support_visibility_does_not_approve",
    "support_visibility_does_not_rank",
    "support_visibility_does_not_recommend",
    "support_visibility_does_not_execute",
    "support_visibility_does_not_enable_production",
    "support_visibility_does_not_imply_correctness_guarantees",
    "support_visibility_does_not_imply_execution_safety",
    "support_visibility_does_not_remediate_or_repair",
    "support_visibility_does_not_mitigate_or_correct",
    "support_visibility_does_not_integrate_planners",
    "support_visibility_does_not_mutate_runtime_state",
)


def _set_tuple_field(instance: object, field_name: str) -> None:
    object.__setattr__(instance, field_name, tuple(getattr(instance, field_name)))


@dataclass(frozen=True)
class SupportStatusIdentity:
    support_status_id: str
    support_summary_id: str
    support_scope_id: str
    support_reference_id: str
    evidence_reference_id: str
    explainability_reference_id: str
    continuity_reference_id: str
    diagnostics_reference_id: str
    lineage_reference_id: str
    provenance_reference_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    source_trust_visibility_report_reference: str
    source_trust_visibility_hash_reference: str


@dataclass(frozen=True)
class SupportVisibilityRecord:
    support_record_id: str
    support_status_id: str
    support_summary_id: str
    support_scope_id: str
    support_reference_id: str
    evidence_reference_id: str
    explainability_reference_id: str
    continuity_reference_id: str
    diagnostics_reference_id: str
    lineage_reference_id: str
    provenance_reference_id: str
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    publicly_transparent: bool = True
    fail_visible: bool = True
    non_authorizing: bool = True
    non_approving: bool = True
    support_authority_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    ranking_enabled: bool = False
    recommendation_enabled: bool = False
    execution_enabled: bool = False
    production_enablement_enabled: bool = False


@dataclass(frozen=True)
class SupportClassificationVisibility:
    classification_visibility_id: str
    support_classification: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    operational_approval_enabled: bool = False
    execution_semantics_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class PublicSupportSurfaceVisibility:
    surface_visibility_id: str
    support_surface: str
    support_classification: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    ranking_enabled: bool = False
    recommendation_enabled: bool = False
    operational_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class UnsupportedSupportStateVisibility:
    unsupported_visibility_id: str
    unsupported_state_type: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    suppression_enabled: bool = False
    hidden_fallback_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    remediation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ExperimentalDeprecatedVisibility:
    experimental_deprecated_id: str
    visibility_type: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    automatic_migration_enabled: bool = False
    operational_fallback_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class EvidenceBasedSupportVisibility:
    evidence_support_id: str
    evidence_support_type: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    replay_safe: bool = True
    provenance_safe: bool = True
    trust_scoring_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ExplainabilitySupportVisibility:
    explainability_support_id: str
    explainability_support_type: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    recommendation_enabled: bool = False
    operational_semantics_enabled: bool = False
    authorization_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ContinuitySupportVisibility:
    continuity_support_id: str
    continuity_support_type: str
    continuity_reference_id: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    restoration_enabled: bool = False
    repair_enabled: bool = False
    remediation_enabled: bool = False
    authorization_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class SupportSummaryRecord:
    support_summary_record_id: str
    support_summary_id: str
    summary_type: str
    evidence_reference_ids: tuple[str, ...]
    summary_state: str
    deterministic_order: int
    descriptive_only: bool = True
    authorization_enabled: bool = False
    approval_enabled: bool = False
    ranking_enabled: bool = False
    recommendation_enabled: bool = False
    execution_enablement_enabled: bool = False
    production_enablement_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class SupportDiagnosticRecord:
    diagnostic_id: str
    diagnostic_type: str
    evidence_reference_ids: tuple[str, ...]
    message: str
    visibility_state: str
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    silent_fallback_enabled: bool = False
    hidden_fallback_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    mitigation_enabled: bool = False
    auto_correction_enabled: bool = False
    ranking_enabled: bool = False
    recommendation_enabled: bool = False
    orchestration_response_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class UnsupportedSupportOperationalStateVisibility:
    state_id: str
    unsupported_state: str
    explicit_reason: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    authorization_enabled: bool = False
    approval_enabled: bool = False
    operational_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    mitigation_enabled: bool = False
    automated_correction_enabled: bool = False
    ranking_enabled: bool = False
    recommendation_enabled: bool = False
    suppression_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class SupportStatusVisibilityIntelligence:
    support_identity: SupportStatusIdentity
    support_visibility_records: tuple[SupportVisibilityRecord, ...]
    support_classifications: tuple[SupportClassificationVisibility, ...]
    support_surfaces: tuple[PublicSupportSurfaceVisibility, ...]
    unsupported_state_visibility: tuple[UnsupportedSupportStateVisibility, ...]
    experimental_deprecated_visibility: tuple[ExperimentalDeprecatedVisibility, ...]
    evidence_based_support_visibility: tuple[EvidenceBasedSupportVisibility, ...]
    explainability_support_visibility: tuple[ExplainabilitySupportVisibility, ...]
    continuity_support_visibility: tuple[ContinuitySupportVisibility, ...]
    support_summaries: tuple[SupportSummaryRecord, ...]
    support_diagnostics: tuple[SupportDiagnosticRecord, ...]
    unsupported_operational_state_visibility: tuple[
        UnsupportedSupportOperationalStateVisibility, ...
    ]
    deterministic_guarantees: tuple[str, ...]
    inherited_prohibitions: tuple[str, ...]
    inherited_constraints: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    support_status_visibility_statement: str = SUPPORT_STATUS_VISIBILITY_STATEMENT
    support_classification_non_authority_statement: str = (
        SUPPORT_CLASSIFICATION_NON_AUTHORITY_STATEMENT
    )
    descriptive_only: bool = True
    publicly_transparent: bool = True
    non_operational: bool = True
    non_authorizing: bool = True
    non_approving: bool = True
    non_executing: bool = True
    non_remediating: bool = True
    non_runtime_mutating: bool = True
    non_ranking: bool = True
    non_recommending: bool = True
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    orchestration_routing_enabled: bool = False
    orchestration_traversal_enabled: bool = False
    orchestration_scheduling_enabled: bool = False
    orchestration_sequencing_enabled: bool = False
    orchestration_decision_enabled: bool = False
    orchestration_recommendation_enabled: bool = False
    support_authorization_enabled: bool = False
    support_approval_enabled: bool = False
    support_ranking_enabled: bool = False
    support_recommendation_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    mitigation_enabled: bool = False
    auto_correction_enabled: bool = False
    ranking_enabled: bool = False
    recommendation_enabled: bool = False
    planner_integration_enabled: bool = False
    planner_execution_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "support_visibility_records",
            "support_classifications",
            "support_surfaces",
            "unsupported_state_visibility",
            "experimental_deprecated_visibility",
            "evidence_based_support_visibility",
            "explainability_support_visibility",
            "continuity_support_visibility",
            "support_summaries",
            "support_diagnostics",
            "unsupported_operational_state_visibility",
            "deterministic_guarantees",
            "inherited_prohibitions",
            "inherited_constraints",
            "explicit_limitations",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))


def default_support_status_identity() -> SupportStatusIdentity:
    return SupportStatusIdentity(
        support_status_id="v4_5b_2_support_status_visibility",
        support_summary_id="v4_5b_2_support_summary",
        support_scope_id="scope::v4_5b_2.public_support",
        support_reference_id="support::v4_5b_2.public_support",
        evidence_reference_id="evidence::v4_5b_2.public_support",
        explainability_reference_id="explainability::v4_5b_2.public_support",
        continuity_reference_id="continuity::v4_5b_2.public_support",
        diagnostics_reference_id="diagnostics::v4_5b_2.public_support",
        lineage_reference_id="lineage::v4_5b_2.public_support",
        provenance_reference_id="provenance::v4_5b_2.public_support",
        phase_id=V4_5B_2_SUPPORT_STATUS_VISIBILITY_PHASE_ID,
        schema_version=V4_5B_2_SUPPORT_STATUS_VISIBILITY_SCHEMA_VERSION,
        generated_at=V4_5B_2_SUPPORT_STATUS_VISIBILITY_GENERATED_AT,
        classification=V4_5B_2_SUPPORT_STATUS_VISIBILITY_CLASSIFICATION,
        source_trust_visibility_report_reference=(
            V4_5B_1_TRUST_VISIBILITY_FOUNDATION_REPORT_REFERENCE
        ),
        source_trust_visibility_hash_reference=(
            V4_5B_1_TRUST_VISIBILITY_FOUNDATION_REPORT_HASH_REFERENCE
        ),
    )


def default_support_visibility_records() -> tuple[SupportVisibilityRecord, ...]:
    identity = default_support_status_identity()
    return (
        SupportVisibilityRecord(
            support_record_id="public_support_status_visibility_foundation",
            support_status_id=identity.support_status_id,
            support_summary_id=identity.support_summary_id,
            support_scope_id=identity.support_scope_id,
            support_reference_id=identity.support_reference_id,
            evidence_reference_id=identity.evidence_reference_id,
            explainability_reference_id=identity.explainability_reference_id,
            continuity_reference_id=identity.continuity_reference_id,
            diagnostics_reference_id=identity.diagnostics_reference_id,
            lineage_reference_id=identity.lineage_reference_id,
            provenance_reference_id=identity.provenance_reference_id,
            visibility_state="public_support_status_visibility_visible",
            deterministic_order=1,
        ),
    )


def default_support_classifications() -> tuple[SupportClassificationVisibility, ...]:
    return tuple(
        SupportClassificationVisibility(
            classification_visibility_id=f"support_classification_{classification}",
            support_classification=classification,
            evidence_reference_ids=(f"evidence_{classification}_classification",),
            visibility_state="support_classification_descriptive_only",
            deterministic_order=order,
        )
        for order, classification in enumerate(SUPPORT_CLASSIFICATION_TYPES, start=1)
    )


def default_support_surfaces() -> tuple[PublicSupportSurfaceVisibility, ...]:
    classifications = (
        "supported",
        "partially_supported",
        "unsupported",
        "experimental",
        "deprecated",
        "blocked",
        "unknown",
        "partially_supported",
    )
    return tuple(
        PublicSupportSurfaceVisibility(
            surface_visibility_id=f"support_surface_{surface}",
            support_surface=surface,
            support_classification=classifications[order - 1],
            evidence_reference_ids=(f"evidence_{surface}_support_surface",),
            visibility_state="public_support_surface_visibility_visible",
            deterministic_order=order,
        )
        for order, surface in enumerate(PUBLIC_SUPPORT_SURFACE_TYPES, start=1)
    )


def default_unsupported_state_visibility() -> tuple[
    UnsupportedSupportStateVisibility, ...
]:
    return tuple(
        UnsupportedSupportStateVisibility(
            unsupported_visibility_id=f"unsupported_support_state_{state_type}",
            unsupported_state_type=state_type,
            evidence_reference_ids=(f"evidence_{state_type}",),
            visibility_state="unsupported_support_state_fail_visible",
            deterministic_order=order,
        )
        for order, state_type in enumerate(UNSUPPORTED_SUPPORT_STATE_TYPES, start=1)
    )


def default_experimental_deprecated_visibility() -> tuple[
    ExperimentalDeprecatedVisibility, ...
]:
    return tuple(
        ExperimentalDeprecatedVisibility(
            experimental_deprecated_id=f"experimental_deprecated_{visibility_type}",
            visibility_type=visibility_type,
            evidence_reference_ids=(f"evidence_{visibility_type}",),
            visibility_state="experimental_deprecated_visibility_descriptive_only",
            deterministic_order=order,
        )
        for order, visibility_type in enumerate(
            EXPERIMENTAL_DEPRECATED_VISIBILITY_TYPES,
            start=1,
        )
    )


def default_evidence_based_support_visibility() -> tuple[
    EvidenceBasedSupportVisibility, ...
]:
    return tuple(
        EvidenceBasedSupportVisibility(
            evidence_support_id=f"evidence_based_support_{visibility_type}",
            evidence_support_type=visibility_type,
            evidence_reference_ids=(f"evidence_{visibility_type}",),
            visibility_state="evidence_based_support_visibility_visible",
            deterministic_order=order,
        )
        for order, visibility_type in enumerate(
            EVIDENCE_BASED_SUPPORT_VISIBILITY_TYPES,
            start=1,
        )
    )


def default_explainability_support_visibility() -> tuple[
    ExplainabilitySupportVisibility, ...
]:
    return tuple(
        ExplainabilitySupportVisibility(
            explainability_support_id=f"explainability_support_{visibility_type}",
            explainability_support_type=visibility_type,
            evidence_reference_ids=(f"evidence_{visibility_type}",),
            visibility_state="explainability_support_visibility_visible",
            deterministic_order=order,
        )
        for order, visibility_type in enumerate(
            EXPLAINABILITY_SUPPORT_VISIBILITY_TYPES,
            start=1,
        )
    )


def default_continuity_support_visibility() -> tuple[ContinuitySupportVisibility, ...]:
    return tuple(
        ContinuitySupportVisibility(
            continuity_support_id=f"continuity_support_{visibility_type}",
            continuity_support_type=visibility_type,
            continuity_reference_id=f"continuity_reference_{visibility_type}",
            evidence_reference_ids=(f"evidence_{visibility_type}",),
            visibility_state="continuity_support_visibility_visible",
            deterministic_order=order,
        )
        for order, visibility_type in enumerate(
            CONTINUITY_SUPPORT_VISIBILITY_TYPES,
            start=1,
        )
    )


def default_support_summaries() -> tuple[SupportSummaryRecord, ...]:
    identity = default_support_status_identity()
    return tuple(
        SupportSummaryRecord(
            support_summary_record_id=f"support_summary_{summary_type}",
            support_summary_id=identity.support_summary_id,
            summary_type=summary_type,
            evidence_reference_ids=(f"evidence_{summary_type}",),
            summary_state="support_summary_descriptive_only",
            deterministic_order=order,
        )
        for order, summary_type in enumerate(SUPPORT_SUMMARY_TYPES, start=1)
    )


def default_support_diagnostics() -> tuple[SupportDiagnosticRecord, ...]:
    return tuple(
        SupportDiagnosticRecord(
            diagnostic_id=f"support_diagnostic_{diagnostic_type}",
            diagnostic_type=diagnostic_type,
            evidence_reference_ids=(f"evidence_{diagnostic_type}",),
            message=(
                f"{diagnostic_type} remains explicit, fail-visible, and "
                "descriptive-only for support status visibility."
            ),
            visibility_state="fail_visible_support_diagnostic_visible",
            deterministic_order=order,
        )
        for order, diagnostic_type in enumerate(SUPPORT_DIAGNOSTIC_TYPES, start=1)
    )


def default_unsupported_operational_state_visibility() -> tuple[
    UnsupportedSupportOperationalStateVisibility, ...
]:
    return tuple(
        UnsupportedSupportOperationalStateVisibility(
            state_id=f"unsupported_support_operational_state_{unsupported_state}",
            unsupported_state=unsupported_state,
            explicit_reason=(
                f"{unsupported_state} remains unsupported for v4.5B.2 support "
                "status visibility."
            ),
            evidence_reference_ids=("evidence_unsupported_support_operational_states",),
            visibility_state="unsupported_support_operational_state_fail_visible",
            deterministic_order=order,
        )
        for order, unsupported_state in enumerate(
            UNSUPPORTED_SUPPORT_OPERATIONAL_STATES,
            start=1,
        )
    )


def default_v4_5b_2_support_status_visibility() -> SupportStatusVisibilityIntelligence:
    return SupportStatusVisibilityIntelligence(
        support_identity=default_support_status_identity(),
        support_visibility_records=default_support_visibility_records(),
        support_classifications=default_support_classifications(),
        support_surfaces=default_support_surfaces(),
        unsupported_state_visibility=default_unsupported_state_visibility(),
        experimental_deprecated_visibility=(
            default_experimental_deprecated_visibility()
        ),
        evidence_based_support_visibility=default_evidence_based_support_visibility(),
        explainability_support_visibility=default_explainability_support_visibility(),
        continuity_support_visibility=default_continuity_support_visibility(),
        support_summaries=default_support_summaries(),
        support_diagnostics=default_support_diagnostics(),
        unsupported_operational_state_visibility=(
            default_unsupported_operational_state_visibility()
        ),
        deterministic_guarantees=(
            V4_5B_2_SUPPORT_STATUS_VISIBILITY_DETERMINISTIC_GUARANTEES
        ),
        inherited_prohibitions=(
            V4_5B_2_SUPPORT_STATUS_VISIBILITY_INHERITED_PROHIBITIONS
        ),
        inherited_constraints=(
            V4_5B_2_SUPPORT_STATUS_VISIBILITY_INHERITED_CONSTRAINTS
        ),
        explicit_limitations=(
            V4_5B_2_SUPPORT_STATUS_VISIBILITY_EXPLICIT_LIMITATIONS
        ),
    )
