"""Deterministic v4.5B.3 public explainability surface models.

The v4.5B.3 layer models public-facing explanation surfaces without enabling
explainability authority, approval, authorization, ranking, recommendation,
execution, remediation, runtime mutation, planner integration, production
consumption, or operational behavior.
"""

from __future__ import annotations

from dataclasses import dataclass


V4_5B_3_EXPLAINABILITY_SURFACE_PHASE_ID = "v4_5b_3_explainability_surfaces"
V4_5B_3_EXPLAINABILITY_SURFACE_SCHEMA_VERSION = (
    "v4_5b_3.explainability_surfaces.1"
)
V4_5B_3_EXPLAINABILITY_SURFACE_REPORT_SCHEMA_VERSION = (
    "v4_5b_3.explainability_surfaces_report.1"
)
V4_5B_3_EXPLAINABILITY_SURFACE_GENERATED_AT = "2026-05-18T00:00:00+00:00"
V4_5B_3_EXPLAINABILITY_SURFACE_STATUS_STABLE = (
    "v4_5b_3_explainability_surfaces_stable"
)
V4_5B_3_EXPLAINABILITY_SURFACE_STATUS_BLOCKED = (
    "v4_5b_3_explainability_surfaces_blocked"
)
V4_5B_3_EXPLAINABILITY_SURFACE_PURPOSE = (
    "deterministic_governance_safe_public_explainability_surfaces_descriptive_only"
)
V4_5B_3_EXPLAINABILITY_SURFACE_CLASSIFICATION = (
    "governance_safe_public_explainability_surfaces_descriptive_only"
)

V4_5B_2_SUPPORT_STATUS_VISIBILITY_REPORT_REFERENCE = (
    "docs/generated/v4_5b_2_support_status_visibility_report.json"
)
V4_5B_2_SUPPORT_STATUS_VISIBILITY_REPORT_HASH_REFERENCE = (
    "c716c22d2907e6f5d6d9eac4e5d3db7102b9b4411547dfe0b361dfedc5e2434e"
)

EXPLAINABILITY_SURFACE_STATEMENT = "Explainability surfaces are descriptive-only."
EXPLAINABILITY_VISIBILITY_NON_AUTHORITY_STATEMENT = (
    "Explainability visibility does NOT imply authorization, approval, operational "
    "readiness, execution safety, or production enablement."
)

SUPPORT_STATE_EXPLANATION_TYPES: tuple[str, ...] = (
    "supported_explanations",
    "partially_supported_explanations",
    "unsupported_explanations",
    "experimental_explanations",
    "deprecated_explanations",
    "blocked_explanations",
    "unknown_state_explanations",
)

EVIDENCE_TO_EXPLANATION_MAPPING_TYPES: tuple[str, ...] = (
    "evidence_backed_explanations",
    "partially_evidenced_explanations",
    "unsupported_evidence_explanations",
    "continuity_backed_explanations",
    "explainability_backed_explanations",
    "diagnostics_backed_explanations",
)

LIMITATION_EXPLANATION_TYPES: tuple[str, ...] = (
    "unsupported_limitation_explanations",
    "experimental_limitation_explanations",
    "deprecated_limitation_explanations",
    "blocked_limitation_explanations",
    "governance_limitation_explanations",
    "continuity_limitation_explanations",
    "evidence_limitation_explanations",
)

TRUST_EXPLANATION_TYPES: tuple[str, ...] = (
    "governance_transparency_explanations",
    "deterministic_guarantee_explanations",
    "explainability_continuity_explanations",
    "integrity_continuity_explanations",
    "fail_visible_diagnostic_explanations",
    "unsupported_state_explanations",
)

CONTINUITY_EXPLANATION_TYPES: tuple[str, ...] = (
    "evidence_continuity_explanations",
    "lineage_continuity_explanations",
    "provenance_continuity_explanations",
    "integrity_continuity_explanations",
    "diagnostics_continuity_explanations",
)

UNSUPPORTED_STATE_EXPLANATION_TYPES: tuple[str, ...] = (
    "unsupported_systems",
    "unsupported_planner_sections",
    "unsupported_evidence_chains",
    "unsupported_continuity_chains",
    "unsupported_operational_states",
    "unsupported_trust_states",
)

EXPLANATION_SUMMARY_TYPES: tuple[str, ...] = (
    "explanation_surface_summary",
    "support_state_explanation_summary",
    "evidence_mapping_summary",
    "limitation_explanation_summary",
    "trust_explanation_summary",
    "continuity_explanation_summary",
    "unsupported_state_explanation_summary",
    "diagnostics_explanation_summary",
)

EXPLANATION_DIAGNOSTIC_TYPES: tuple[str, ...] = (
    "missing_explanation_evidence",
    "unsupported_explanation_gaps",
    "incomplete_continuity_explanations",
    "incomplete_integrity_explanations",
    "unsupported_trust_explanations",
    "unsupported_operational_explanations",
    "inherited_limitation_explanation_gaps",
    "inherited_prohibition_explanation_gaps",
)

UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES: tuple[str, ...] = (
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
    "explainability_based_authorization",
    "explainability_based_approval",
    "explainability_based_ranking",
    "explainability_based_recommendation",
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

V4_5B_3_EXPLAINABILITY_SURFACE_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
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
    "enabled_explainability_authorization_count",
    "enabled_explainability_approval_count",
    "enabled_explainability_ranking_count",
    "enabled_explainability_recommendation_count",
    "enabled_remediation_count",
    "enabled_repair_count",
    "enabled_mitigation_count",
    "enabled_auto_correction_count",
    "enabled_planner_integration_count",
    "enabled_production_consumption_count",
    "enabled_runtime_mutation_count",
    "enabled_operational_mutation_count",
)

V4_5B_3_EXPLAINABILITY_SURFACE_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "deterministic_explainability_surface_identity",
    "deterministic_support_state_explanation_visibility",
    "deterministic_evidence_to_explanation_mapping",
    "deterministic_limitation_explanation_visibility",
    "deterministic_public_trust_explanation_visibility",
    "deterministic_continuity_explanation_visibility",
    "deterministic_unsupported_state_explanation_visibility",
    "stable_replay_safe_serialization",
    "stable_replay_safe_hashing",
    "lineage_continuity_preserved",
    "provenance_continuity_preserved",
    "publicly_transparent_descriptive_only_explainability_surfaces",
)

V4_5B_3_EXPLAINABILITY_SURFACE_INHERITED_PROHIBITIONS: tuple[str, ...] = (
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
    "explainability_based_authorization_prohibited",
    "explainability_based_approval_prohibited",
    "explainability_based_ranking_prohibited",
    "explainability_based_recommendation_prohibited",
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

V4_5B_3_EXPLAINABILITY_SURFACE_INHERITED_CONSTRAINTS: tuple[str, ...] = (
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

V4_5B_3_EXPLAINABILITY_SURFACE_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "explainability_surfaces_do_not_authorize",
    "explainability_surfaces_do_not_approve",
    "explainability_surfaces_do_not_rank",
    "explainability_surfaces_do_not_recommend",
    "explainability_surfaces_do_not_execute",
    "explainability_surfaces_do_not_enable_production",
    "explainability_surfaces_do_not_imply_correctness_guarantees",
    "explainability_surfaces_do_not_imply_execution_safety",
    "explainability_surfaces_do_not_remediate_or_repair",
    "explainability_surfaces_do_not_mitigate_or_correct",
    "explainability_surfaces_do_not_integrate_planners",
    "explainability_surfaces_do_not_mutate_runtime_state",
)


def _set_tuple_field(instance: object, field_name: str) -> None:
    object.__setattr__(instance, field_name, tuple(getattr(instance, field_name)))


@dataclass(frozen=True)
class ExplainabilitySurfaceIdentity:
    explainability_surface_id: str
    explanation_summary_id: str
    support_visibility_reference_id: str
    evidence_reference_id: str
    continuity_reference_id: str
    trust_summary_reference_id: str
    diagnostics_reference_id: str
    lineage_reference_id: str
    provenance_reference_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    source_support_status_report_reference: str
    source_support_status_hash_reference: str


@dataclass(frozen=True)
class ExplainabilitySurfaceRecord:
    surface_record_id: str
    explainability_surface_id: str
    explanation_summary_id: str
    support_visibility_reference_id: str
    evidence_reference_id: str
    continuity_reference_id: str
    trust_summary_reference_id: str
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
    explainability_authority_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    ranking_enabled: bool = False
    recommendation_enabled: bool = False
    execution_enabled: bool = False
    production_enablement_enabled: bool = False


@dataclass(frozen=True)
class SupportStateExplanationSurface:
    support_state_explanation_id: str
    explanation_type: str
    evidence_reference_ids: tuple[str, ...]
    explanation_visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    correctness_guarantee_enabled: bool = False
    operational_readiness_enabled: bool = False
    execution_safety_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class EvidenceToExplanationMapping:
    evidence_mapping_id: str
    mapping_type: str
    evidence_reference_ids: tuple[str, ...]
    explanation_reference_ids: tuple[str, ...]
    mapping_state: str
    deterministic_order: int
    descriptive_only: bool = True
    replay_safe: bool = True
    provenance_safe: bool = True
    trust_scoring_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    ranking_enabled: bool = False
    recommendation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")
        _set_tuple_field(self, "explanation_reference_ids")


@dataclass(frozen=True)
class LimitationExplanationVisibility:
    limitation_explanation_id: str
    limitation_type: str
    evidence_reference_ids: tuple[str, ...]
    explanation_visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    operational_fallback_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    recommendation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class PublicTrustExplanationVisibility:
    trust_explanation_id: str
    trust_explanation_type: str
    evidence_reference_ids: tuple[str, ...]
    explanation_visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    authorization_enabled: bool = False
    approval_enabled: bool = False
    execution_semantics_enabled: bool = False
    operational_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ContinuityExplanationVisibility:
    continuity_explanation_id: str
    continuity_explanation_type: str
    continuity_reference_id: str
    evidence_reference_ids: tuple[str, ...]
    explanation_visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    restoration_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    authorization_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class UnsupportedStateExplanationVisibility:
    unsupported_explanation_id: str
    unsupported_state_type: str
    evidence_reference_ids: tuple[str, ...]
    explanation_visibility_state: str
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
class ExplanationSummaryRecord:
    explanation_summary_record_id: str
    explanation_summary_id: str
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
class ExplanationDiagnosticRecord:
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
class UnsupportedExplanationOperationalStateVisibility:
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
class ExplainabilitySurfaceIntelligence:
    surface_identity: ExplainabilitySurfaceIdentity
    surface_records: tuple[ExplainabilitySurfaceRecord, ...]
    support_state_explanations: tuple[SupportStateExplanationSurface, ...]
    evidence_to_explanation_mappings: tuple[EvidenceToExplanationMapping, ...]
    limitation_explanations: tuple[LimitationExplanationVisibility, ...]
    trust_explanations: tuple[PublicTrustExplanationVisibility, ...]
    continuity_explanations: tuple[ContinuityExplanationVisibility, ...]
    unsupported_state_explanations: tuple[UnsupportedStateExplanationVisibility, ...]
    explanation_summaries: tuple[ExplanationSummaryRecord, ...]
    explanation_diagnostics: tuple[ExplanationDiagnosticRecord, ...]
    unsupported_operational_state_visibility: tuple[
        UnsupportedExplanationOperationalStateVisibility, ...
    ]
    deterministic_guarantees: tuple[str, ...]
    inherited_prohibitions: tuple[str, ...]
    inherited_constraints: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explainability_surface_statement: str = EXPLAINABILITY_SURFACE_STATEMENT
    explainability_visibility_non_authority_statement: str = (
        EXPLAINABILITY_VISIBILITY_NON_AUTHORITY_STATEMENT
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
    explainability_authorization_enabled: bool = False
    explainability_approval_enabled: bool = False
    explainability_ranking_enabled: bool = False
    explainability_recommendation_enabled: bool = False
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
            "surface_records",
            "support_state_explanations",
            "evidence_to_explanation_mappings",
            "limitation_explanations",
            "trust_explanations",
            "continuity_explanations",
            "unsupported_state_explanations",
            "explanation_summaries",
            "explanation_diagnostics",
            "unsupported_operational_state_visibility",
            "deterministic_guarantees",
            "inherited_prohibitions",
            "inherited_constraints",
            "explicit_limitations",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))


def default_explainability_surface_identity() -> ExplainabilitySurfaceIdentity:
    return ExplainabilitySurfaceIdentity(
        explainability_surface_id="v4_5b_3_explainability_surfaces",
        explanation_summary_id="v4_5b_3_explanation_summary",
        support_visibility_reference_id="support::v4_5b_2.public_support",
        evidence_reference_id="evidence::v4_5b_3.explainability_surfaces",
        continuity_reference_id="continuity::v4_5b_3.explainability_surfaces",
        trust_summary_reference_id="trust::v4_5b_3.explainability_surfaces",
        diagnostics_reference_id="diagnostics::v4_5b_3.explainability_surfaces",
        lineage_reference_id="lineage::v4_5b_3.explainability_surfaces",
        provenance_reference_id="provenance::v4_5b_3.explainability_surfaces",
        phase_id=V4_5B_3_EXPLAINABILITY_SURFACE_PHASE_ID,
        schema_version=V4_5B_3_EXPLAINABILITY_SURFACE_SCHEMA_VERSION,
        generated_at=V4_5B_3_EXPLAINABILITY_SURFACE_GENERATED_AT,
        classification=V4_5B_3_EXPLAINABILITY_SURFACE_CLASSIFICATION,
        source_support_status_report_reference=(
            V4_5B_2_SUPPORT_STATUS_VISIBILITY_REPORT_REFERENCE
        ),
        source_support_status_hash_reference=(
            V4_5B_2_SUPPORT_STATUS_VISIBILITY_REPORT_HASH_REFERENCE
        ),
    )


def default_surface_records() -> tuple[ExplainabilitySurfaceRecord, ...]:
    identity = default_explainability_surface_identity()
    return (
        ExplainabilitySurfaceRecord(
            surface_record_id="public_explainability_surface_foundation",
            explainability_surface_id=identity.explainability_surface_id,
            explanation_summary_id=identity.explanation_summary_id,
            support_visibility_reference_id=identity.support_visibility_reference_id,
            evidence_reference_id=identity.evidence_reference_id,
            continuity_reference_id=identity.continuity_reference_id,
            trust_summary_reference_id=identity.trust_summary_reference_id,
            diagnostics_reference_id=identity.diagnostics_reference_id,
            lineage_reference_id=identity.lineage_reference_id,
            provenance_reference_id=identity.provenance_reference_id,
            visibility_state="public_explainability_surface_visible",
            deterministic_order=1,
        ),
    )


def default_support_state_explanations() -> tuple[
    SupportStateExplanationSurface, ...
]:
    return tuple(
        SupportStateExplanationSurface(
            support_state_explanation_id=f"support_state_explanation_{item}",
            explanation_type=item,
            evidence_reference_ids=(f"evidence_{item}",),
            explanation_visibility_state="support_state_explanation_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(SUPPORT_STATE_EXPLANATION_TYPES, start=1)
    )


def default_evidence_to_explanation_mappings() -> tuple[
    EvidenceToExplanationMapping, ...
]:
    return tuple(
        EvidenceToExplanationMapping(
            evidence_mapping_id=f"evidence_to_explanation_{item}",
            mapping_type=item,
            evidence_reference_ids=(f"evidence_{item}",),
            explanation_reference_ids=(f"explanation_{item}",),
            mapping_state="evidence_to_explanation_mapping_replay_safe",
            deterministic_order=order,
        )
        for order, item in enumerate(
            EVIDENCE_TO_EXPLANATION_MAPPING_TYPES,
            start=1,
        )
    )


def default_limitation_explanations() -> tuple[LimitationExplanationVisibility, ...]:
    return tuple(
        LimitationExplanationVisibility(
            limitation_explanation_id=f"limitation_explanation_{item}",
            limitation_type=item,
            evidence_reference_ids=(f"evidence_{item}",),
            explanation_visibility_state="limitation_explanation_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(LIMITATION_EXPLANATION_TYPES, start=1)
    )


def default_trust_explanations() -> tuple[PublicTrustExplanationVisibility, ...]:
    return tuple(
        PublicTrustExplanationVisibility(
            trust_explanation_id=f"trust_explanation_{item}",
            trust_explanation_type=item,
            evidence_reference_ids=(f"evidence_{item}",),
            explanation_visibility_state="public_trust_explanation_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(TRUST_EXPLANATION_TYPES, start=1)
    )


def default_continuity_explanations() -> tuple[ContinuityExplanationVisibility, ...]:
    return tuple(
        ContinuityExplanationVisibility(
            continuity_explanation_id=f"continuity_explanation_{item}",
            continuity_explanation_type=item,
            continuity_reference_id=f"continuity_reference_{item}",
            evidence_reference_ids=(f"evidence_{item}",),
            explanation_visibility_state="continuity_explanation_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(CONTINUITY_EXPLANATION_TYPES, start=1)
    )


def default_unsupported_state_explanations() -> tuple[
    UnsupportedStateExplanationVisibility, ...
]:
    return tuple(
        UnsupportedStateExplanationVisibility(
            unsupported_explanation_id=f"unsupported_state_explanation_{item}",
            unsupported_state_type=item,
            evidence_reference_ids=(f"evidence_{item}",),
            explanation_visibility_state="unsupported_state_explanation_fail_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(UNSUPPORTED_STATE_EXPLANATION_TYPES, start=1)
    )


def default_explanation_summaries() -> tuple[ExplanationSummaryRecord, ...]:
    identity = default_explainability_surface_identity()
    return tuple(
        ExplanationSummaryRecord(
            explanation_summary_record_id=f"explanation_summary_{item}",
            explanation_summary_id=identity.explanation_summary_id,
            summary_type=item,
            evidence_reference_ids=(f"evidence_{item}",),
            summary_state="explanation_summary_descriptive_only",
            deterministic_order=order,
        )
        for order, item in enumerate(EXPLANATION_SUMMARY_TYPES, start=1)
    )


def default_explanation_diagnostics() -> tuple[ExplanationDiagnosticRecord, ...]:
    return tuple(
        ExplanationDiagnosticRecord(
            diagnostic_id=f"explanation_diagnostic_{item}",
            diagnostic_type=item,
            evidence_reference_ids=(f"evidence_{item}",),
            message=(
                f"{item} remains explicit, fail-visible, and descriptive-only "
                "for public explainability surfaces."
            ),
            visibility_state="fail_visible_explanation_diagnostic_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(EXPLANATION_DIAGNOSTIC_TYPES, start=1)
    )


def default_unsupported_operational_state_visibility() -> tuple[
    UnsupportedExplanationOperationalStateVisibility, ...
]:
    return tuple(
        UnsupportedExplanationOperationalStateVisibility(
            state_id=f"unsupported_explanation_operational_state_{item}",
            unsupported_state=item,
            explicit_reason=(
                f"{item} remains unsupported for v4.5B.3 public "
                "explainability surfaces."
            ),
            evidence_reference_ids=(
                "evidence_unsupported_explanation_operational_states",
            ),
            visibility_state="unsupported_explanation_operational_state_fail_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(
            UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES,
            start=1,
        )
    )


def default_v4_5b_3_explainability_surfaces() -> ExplainabilitySurfaceIntelligence:
    return ExplainabilitySurfaceIntelligence(
        surface_identity=default_explainability_surface_identity(),
        surface_records=default_surface_records(),
        support_state_explanations=default_support_state_explanations(),
        evidence_to_explanation_mappings=default_evidence_to_explanation_mappings(),
        limitation_explanations=default_limitation_explanations(),
        trust_explanations=default_trust_explanations(),
        continuity_explanations=default_continuity_explanations(),
        unsupported_state_explanations=default_unsupported_state_explanations(),
        explanation_summaries=default_explanation_summaries(),
        explanation_diagnostics=default_explanation_diagnostics(),
        unsupported_operational_state_visibility=(
            default_unsupported_operational_state_visibility()
        ),
        deterministic_guarantees=(
            V4_5B_3_EXPLAINABILITY_SURFACE_DETERMINISTIC_GUARANTEES
        ),
        inherited_prohibitions=(
            V4_5B_3_EXPLAINABILITY_SURFACE_INHERITED_PROHIBITIONS
        ),
        inherited_constraints=V4_5B_3_EXPLAINABILITY_SURFACE_INHERITED_CONSTRAINTS,
        explicit_limitations=V4_5B_3_EXPLAINABILITY_SURFACE_EXPLICIT_LIMITATIONS,
    )
