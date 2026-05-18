"""Deterministic v4.5B.4 public provenance and lineage visibility models.

The v4.5B.4 layer models public-facing provenance and lineage visibility
without enabling source authority, approval, authorization, ranking,
recommendation, execution, remediation, runtime mutation, planner integration,
production consumption, or operational behavior.
"""

from __future__ import annotations

from dataclasses import dataclass


V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_PHASE_ID = (
    "v4_5b_4_provenance_lineage_visibility"
)
V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_SCHEMA_VERSION = (
    "v4_5b_4.provenance_lineage_visibility.1"
)
V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_REPORT_SCHEMA_VERSION = (
    "v4_5b_4.provenance_lineage_visibility_report.1"
)
V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_GENERATED_AT = (
    "2026-05-18T00:00:00+00:00"
)
V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_STATUS_STABLE = (
    "v4_5b_4_provenance_lineage_visibility_stable"
)
V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_STATUS_BLOCKED = (
    "v4_5b_4_provenance_lineage_visibility_blocked"
)
V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_PURPOSE = (
    "deterministic_governance_safe_public_provenance_lineage_visibility_descriptive_only"
)
V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_CLASSIFICATION = (
    "governance_safe_public_provenance_lineage_visibility_descriptive_only"
)

V4_5B_3_EXPLAINABILITY_SURFACES_REPORT_REFERENCE = (
    "docs/generated/v4_5b_3_explainability_surfaces_report.json"
)
V4_5B_3_EXPLAINABILITY_SURFACES_REPORT_HASH_REFERENCE = (
    "199de43c3e94cfb64397acc5fc10b77fb209476e2a66b57d771e5132462ef382"
)

PROVENANCE_LINEAGE_VISIBILITY_STATEMENT = (
    "Provenance and lineage visibility is descriptive-only."
)
SOURCE_VISIBILITY_NON_AUTHORITY_STATEMENT = (
    "Source visibility does NOT imply authorization, approval, correctness "
    "guarantee, ranking, recommendation, operational readiness, execution "
    "safety, or production enablement."
)

SOURCE_TO_SURFACE_VISIBILITY_TYPES: tuple[str, ...] = (
    "source_to_trust_summary",
    "source_to_support_status",
    "source_to_explainability_surface",
    "source_to_unsupported_state_surface",
    "source_to_diagnostics_surface",
    "source_to_continuity_surface",
    "source_to_limitation_surface",
)

EVIDENCE_ORIGIN_VISIBILITY_TYPES: tuple[str, ...] = (
    "evidence_origin_references",
    "evidence_source_references",
    "evidence_continuity_references",
    "evidence_provenance_references",
    "evidence_lineage_references",
    "evidence_freshness_references",
    "evidence_diagnostic_references",
)

SUPPORT_STATUS_LINEAGE_TYPES: tuple[str, ...] = (
    "supported_status_lineage",
    "partially_supported_status_lineage",
    "unsupported_status_lineage",
    "experimental_status_lineage",
    "deprecated_status_lineage",
    "blocked_status_lineage",
    "unknown_status_lineage",
)

EXPLAINABILITY_LINEAGE_TYPES: tuple[str, ...] = (
    "support_explanation_lineage",
    "limitation_explanation_lineage",
    "unsupported_state_explanation_lineage",
    "continuity_explanation_lineage",
    "trust_explanation_lineage",
    "diagnostic_explanation_lineage",
)

TRUST_SUMMARY_LINEAGE_TYPES: tuple[str, ...] = (
    "public_trust_summary_lineage",
    "governance_transparency_lineage",
    "deterministic_guarantee_lineage",
    "integrity_visibility_lineage",
    "continuity_visibility_lineage",
    "explainability_visibility_lineage",
)

STALE_UNKNOWN_PROVENANCE_TYPES: tuple[str, ...] = (
    "stale_provenance_states",
    "unknown_provenance_states",
    "incomplete_provenance_states",
    "incomplete_lineage_states",
    "unsupported_provenance_states",
    "unsupported_lineage_states",
)

PROVENANCE_LINEAGE_SUMMARY_TYPES: tuple[str, ...] = (
    "provenance_visibility_summary",
    "lineage_visibility_summary",
    "source_to_surface_summary",
    "evidence_origin_summary",
    "support_status_lineage_summary",
    "explainability_lineage_summary",
    "trust_summary_lineage_summary",
    "stale_unknown_provenance_summary",
    "diagnostics_provenance_lineage_summary",
)

PROVENANCE_LINEAGE_DIAGNOSTIC_TYPES: tuple[str, ...] = (
    "missing_source_references",
    "incomplete_provenance_visibility",
    "incomplete_lineage_visibility",
    "stale_provenance_visibility",
    "unknown_provenance_visibility",
    "unsupported_provenance_states",
    "unsupported_lineage_states",
    "source_to_surface_continuity_gaps",
    "inherited_provenance_limitation_gaps",
    "inherited_lineage_limitation_gaps",
)

UNSUPPORTED_PROVENANCE_LINEAGE_OPERATIONAL_STATES: tuple[str, ...] = (
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
    "source_based_authorization",
    "source_based_approval",
    "provenance_based_ranking",
    "lineage_based_recommendation",
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

V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
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
    "enabled_source_authorization_count",
    "enabled_source_approval_count",
    "enabled_provenance_ranking_count",
    "enabled_lineage_recommendation_count",
    "enabled_remediation_count",
    "enabled_repair_count",
    "enabled_mitigation_count",
    "enabled_auto_correction_count",
    "enabled_planner_integration_count",
    "enabled_production_consumption_count",
    "enabled_runtime_mutation_count",
    "enabled_operational_mutation_count",
)

V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "deterministic_provenance_visibility_identity",
    "deterministic_lineage_visibility_identity",
    "deterministic_source_to_surface_visibility",
    "deterministic_evidence_origin_visibility",
    "deterministic_support_status_lineage_visibility",
    "deterministic_explainability_lineage_visibility",
    "deterministic_trust_summary_lineage_visibility",
    "deterministic_stale_unknown_provenance_visibility",
    "stable_replay_safe_serialization",
    "stable_replay_safe_hashing",
    "lineage_continuity_preserved",
    "provenance_continuity_preserved",
    "publicly_transparent_descriptive_only_provenance_lineage_visibility",
)

V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_INHERITED_PROHIBITIONS: tuple[str, ...] = (
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
    "source_based_authorization_prohibited",
    "source_based_approval_prohibited",
    "provenance_based_ranking_prohibited",
    "lineage_based_recommendation_prohibited",
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

V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_INHERITED_CONSTRAINTS: tuple[str, ...] = (
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

V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "provenance_visibility_does_not_authorize",
    "provenance_visibility_does_not_approve",
    "provenance_visibility_does_not_rank",
    "lineage_visibility_does_not_recommend",
    "source_visibility_does_not_execute",
    "source_visibility_does_not_enable_production",
    "source_visibility_does_not_imply_correctness_guarantees",
    "source_visibility_does_not_imply_execution_safety",
    "source_visibility_does_not_remediate_or_repair",
    "source_visibility_does_not_mitigate_or_correct",
    "source_visibility_does_not_integrate_planners",
    "source_visibility_does_not_mutate_runtime_state",
)


def _set_tuple_field(instance: object, field_name: str) -> None:
    object.__setattr__(instance, field_name, tuple(getattr(instance, field_name)))


@dataclass(frozen=True)
class ProvenanceLineageVisibilityIdentity:
    provenance_visibility_id: str
    lineage_visibility_id: str
    source_reference_id: str
    evidence_reference_id: str
    support_status_reference_id: str
    explainability_surface_reference_id: str
    trust_summary_reference_id: str
    diagnostics_reference_id: str
    continuity_reference_id: str
    lineage_reference_id: str
    provenance_reference_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    source_explainability_report_reference: str
    source_explainability_hash_reference: str


@dataclass(frozen=True)
class ProvenanceVisibilityRecord:
    provenance_record_id: str
    provenance_visibility_id: str
    source_reference_id: str
    evidence_reference_id: str
    provenance_reference_id: str
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    publicly_transparent: bool = True
    fail_visible: bool = True
    source_authority_enabled: bool = False
    source_authorization_enabled: bool = False
    source_approval_enabled: bool = False
    provenance_ranking_enabled: bool = False
    trust_scoring_enabled: bool = False


@dataclass(frozen=True)
class LineageVisibilityRecord:
    lineage_record_id: str
    lineage_visibility_id: str
    source_reference_id: str
    lineage_reference_id: str
    continuity_reference_id: str
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    publicly_transparent: bool = True
    fail_visible: bool = True
    lineage_recommendation_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    operational_enabled: bool = False


@dataclass(frozen=True)
class SourceToSurfaceVisibility:
    source_surface_id: str
    visibility_type: str
    source_reference_id: str
    surface_reference_id: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    source_authority_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class EvidenceOriginVisibility:
    evidence_origin_id: str
    evidence_origin_type: str
    source_reference_id: str
    evidence_reference_ids: tuple[str, ...]
    provenance_reference_id: str
    lineage_reference_id: str
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    replay_safe: bool = True
    provenance_safe: bool = True
    trust_scoring_enabled: bool = False
    ranking_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class SupportStatusLineageVisibility:
    support_lineage_id: str
    support_lineage_type: str
    support_status_reference_id: str
    lineage_reference_id: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    recommendation_enabled: bool = False
    operational_semantics_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ExplainabilityLineageVisibility:
    explainability_lineage_id: str
    explainability_lineage_type: str
    explainability_surface_reference_id: str
    lineage_reference_id: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    explanation_approval_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    ranking_enabled: bool = False
    recommendation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class TrustSummaryLineageVisibility:
    trust_lineage_id: str
    trust_lineage_type: str
    trust_summary_reference_id: str
    lineage_reference_id: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    trust_scoring_enabled: bool = False
    operational_readiness_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class StaleUnknownProvenanceVisibility:
    stale_unknown_id: str
    provenance_state_type: str
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
class ProvenanceLineageSummaryRecord:
    summary_record_id: str
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
class ProvenanceLineageDiagnosticRecord:
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
class UnsupportedProvenanceLineageOperationalStateVisibility:
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
class ProvenanceLineageVisibilityIntelligence:
    visibility_identity: ProvenanceLineageVisibilityIdentity
    provenance_visibility_records: tuple[ProvenanceVisibilityRecord, ...]
    lineage_visibility_records: tuple[LineageVisibilityRecord, ...]
    source_to_surface_visibility: tuple[SourceToSurfaceVisibility, ...]
    evidence_origin_visibility: tuple[EvidenceOriginVisibility, ...]
    support_status_lineage_visibility: tuple[SupportStatusLineageVisibility, ...]
    explainability_lineage_visibility: tuple[ExplainabilityLineageVisibility, ...]
    trust_summary_lineage_visibility: tuple[TrustSummaryLineageVisibility, ...]
    stale_unknown_provenance_visibility: tuple[StaleUnknownProvenanceVisibility, ...]
    provenance_lineage_summaries: tuple[ProvenanceLineageSummaryRecord, ...]
    provenance_lineage_diagnostics: tuple[ProvenanceLineageDiagnosticRecord, ...]
    unsupported_operational_state_visibility: tuple[
        UnsupportedProvenanceLineageOperationalStateVisibility, ...
    ]
    deterministic_guarantees: tuple[str, ...]
    inherited_prohibitions: tuple[str, ...]
    inherited_constraints: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    provenance_lineage_visibility_statement: str = PROVENANCE_LINEAGE_VISIBILITY_STATEMENT
    source_visibility_non_authority_statement: str = (
        SOURCE_VISIBILITY_NON_AUTHORITY_STATEMENT
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
    source_authorization_enabled: bool = False
    source_approval_enabled: bool = False
    provenance_ranking_enabled: bool = False
    lineage_recommendation_enabled: bool = False
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
            "provenance_visibility_records",
            "lineage_visibility_records",
            "source_to_surface_visibility",
            "evidence_origin_visibility",
            "support_status_lineage_visibility",
            "explainability_lineage_visibility",
            "trust_summary_lineage_visibility",
            "stale_unknown_provenance_visibility",
            "provenance_lineage_summaries",
            "provenance_lineage_diagnostics",
            "unsupported_operational_state_visibility",
            "deterministic_guarantees",
            "inherited_prohibitions",
            "inherited_constraints",
            "explicit_limitations",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))


def default_provenance_lineage_visibility_identity() -> (
    ProvenanceLineageVisibilityIdentity
):
    return ProvenanceLineageVisibilityIdentity(
        provenance_visibility_id="v4_5b_4_provenance_visibility",
        lineage_visibility_id="v4_5b_4_lineage_visibility",
        source_reference_id="source::v4_5b_4.public_trust",
        evidence_reference_id="evidence::v4_5b_4.public_trust",
        support_status_reference_id="support::v4_5b_2.public_support",
        explainability_surface_reference_id=(
            "explainability::v4_5b_3.public_surfaces"
        ),
        trust_summary_reference_id="trust::v4_5b_4.public_trust",
        diagnostics_reference_id="diagnostics::v4_5b_4.public_trust",
        continuity_reference_id="continuity::v4_5b_4.public_trust",
        lineage_reference_id="lineage::v4_5b_4.public_trust",
        provenance_reference_id="provenance::v4_5b_4.public_trust",
        phase_id=V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_PHASE_ID,
        schema_version=V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_SCHEMA_VERSION,
        generated_at=V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_GENERATED_AT,
        classification=V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_CLASSIFICATION,
        source_explainability_report_reference=(
            V4_5B_3_EXPLAINABILITY_SURFACES_REPORT_REFERENCE
        ),
        source_explainability_hash_reference=(
            V4_5B_3_EXPLAINABILITY_SURFACES_REPORT_HASH_REFERENCE
        ),
    )


def default_provenance_visibility_records() -> tuple[ProvenanceVisibilityRecord, ...]:
    identity = default_provenance_lineage_visibility_identity()
    return (
        ProvenanceVisibilityRecord(
            provenance_record_id="public_provenance_visibility_foundation",
            provenance_visibility_id=identity.provenance_visibility_id,
            source_reference_id=identity.source_reference_id,
            evidence_reference_id=identity.evidence_reference_id,
            provenance_reference_id=identity.provenance_reference_id,
            visibility_state="public_provenance_visibility_visible",
            deterministic_order=1,
        ),
    )


def default_lineage_visibility_records() -> tuple[LineageVisibilityRecord, ...]:
    identity = default_provenance_lineage_visibility_identity()
    return (
        LineageVisibilityRecord(
            lineage_record_id="public_lineage_visibility_foundation",
            lineage_visibility_id=identity.lineage_visibility_id,
            source_reference_id=identity.source_reference_id,
            lineage_reference_id=identity.lineage_reference_id,
            continuity_reference_id=identity.continuity_reference_id,
            visibility_state="public_lineage_visibility_visible",
            deterministic_order=1,
        ),
    )


def default_source_to_surface_visibility() -> tuple[SourceToSurfaceVisibility, ...]:
    return tuple(
        SourceToSurfaceVisibility(
            source_surface_id=f"source_surface_{item}",
            visibility_type=item,
            source_reference_id=f"source_reference_{item}",
            surface_reference_id=f"surface_reference_{item}",
            evidence_reference_ids=(f"evidence_{item}",),
            visibility_state="source_to_surface_visibility_descriptive_only",
            deterministic_order=order,
        )
        for order, item in enumerate(SOURCE_TO_SURFACE_VISIBILITY_TYPES, start=1)
    )


def default_evidence_origin_visibility() -> tuple[EvidenceOriginVisibility, ...]:
    return tuple(
        EvidenceOriginVisibility(
            evidence_origin_id=f"evidence_origin_{item}",
            evidence_origin_type=item,
            source_reference_id=f"source_reference_{item}",
            evidence_reference_ids=(f"evidence_{item}",),
            provenance_reference_id=f"provenance_reference_{item}",
            lineage_reference_id=f"lineage_reference_{item}",
            visibility_state="evidence_origin_visibility_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(EVIDENCE_ORIGIN_VISIBILITY_TYPES, start=1)
    )


def default_support_status_lineage_visibility() -> tuple[
    SupportStatusLineageVisibility, ...
]:
    return tuple(
        SupportStatusLineageVisibility(
            support_lineage_id=f"support_status_lineage_{item}",
            support_lineage_type=item,
            support_status_reference_id=f"support_status_reference_{item}",
            lineage_reference_id=f"lineage_reference_{item}",
            evidence_reference_ids=(f"evidence_{item}",),
            visibility_state="support_status_lineage_visibility_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(SUPPORT_STATUS_LINEAGE_TYPES, start=1)
    )


def default_explainability_lineage_visibility() -> tuple[
    ExplainabilityLineageVisibility, ...
]:
    return tuple(
        ExplainabilityLineageVisibility(
            explainability_lineage_id=f"explainability_lineage_{item}",
            explainability_lineage_type=item,
            explainability_surface_reference_id=f"explainability_reference_{item}",
            lineage_reference_id=f"lineage_reference_{item}",
            evidence_reference_ids=(f"evidence_{item}",),
            visibility_state="explainability_lineage_visibility_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(EXPLAINABILITY_LINEAGE_TYPES, start=1)
    )


def default_trust_summary_lineage_visibility() -> tuple[
    TrustSummaryLineageVisibility, ...
]:
    return tuple(
        TrustSummaryLineageVisibility(
            trust_lineage_id=f"trust_summary_lineage_{item}",
            trust_lineage_type=item,
            trust_summary_reference_id=f"trust_summary_reference_{item}",
            lineage_reference_id=f"lineage_reference_{item}",
            evidence_reference_ids=(f"evidence_{item}",),
            visibility_state="trust_summary_lineage_visibility_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(TRUST_SUMMARY_LINEAGE_TYPES, start=1)
    )


def default_stale_unknown_provenance_visibility() -> tuple[
    StaleUnknownProvenanceVisibility, ...
]:
    return tuple(
        StaleUnknownProvenanceVisibility(
            stale_unknown_id=f"stale_unknown_provenance_{item}",
            provenance_state_type=item,
            evidence_reference_ids=(f"evidence_{item}",),
            visibility_state="stale_unknown_provenance_fail_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(STALE_UNKNOWN_PROVENANCE_TYPES, start=1)
    )


def default_provenance_lineage_summaries() -> tuple[
    ProvenanceLineageSummaryRecord, ...
]:
    return tuple(
        ProvenanceLineageSummaryRecord(
            summary_record_id=f"provenance_lineage_summary_{item}",
            summary_type=item,
            evidence_reference_ids=(f"evidence_{item}",),
            summary_state="provenance_lineage_summary_descriptive_only",
            deterministic_order=order,
        )
        for order, item in enumerate(PROVENANCE_LINEAGE_SUMMARY_TYPES, start=1)
    )


def default_provenance_lineage_diagnostics() -> tuple[
    ProvenanceLineageDiagnosticRecord, ...
]:
    return tuple(
        ProvenanceLineageDiagnosticRecord(
            diagnostic_id=f"provenance_lineage_diagnostic_{item}",
            diagnostic_type=item,
            evidence_reference_ids=(f"evidence_{item}",),
            message=(
                f"{item} remains explicit, fail-visible, and descriptive-only "
                "for public provenance and lineage visibility."
            ),
            visibility_state="fail_visible_provenance_lineage_diagnostic_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(PROVENANCE_LINEAGE_DIAGNOSTIC_TYPES, start=1)
    )


def default_unsupported_operational_state_visibility() -> tuple[
    UnsupportedProvenanceLineageOperationalStateVisibility, ...
]:
    return tuple(
        UnsupportedProvenanceLineageOperationalStateVisibility(
            state_id=f"unsupported_provenance_lineage_operational_state_{item}",
            unsupported_state=item,
            explicit_reason=(
                f"{item} remains unsupported for v4.5B.4 public provenance "
                "and lineage visibility."
            ),
            evidence_reference_ids=(
                "evidence_unsupported_provenance_lineage_operational_states",
            ),
            visibility_state="unsupported_provenance_lineage_operational_state_fail_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(
            UNSUPPORTED_PROVENANCE_LINEAGE_OPERATIONAL_STATES,
            start=1,
        )
    )


def default_v4_5b_4_provenance_lineage_visibility() -> (
    ProvenanceLineageVisibilityIntelligence
):
    return ProvenanceLineageVisibilityIntelligence(
        visibility_identity=default_provenance_lineage_visibility_identity(),
        provenance_visibility_records=default_provenance_visibility_records(),
        lineage_visibility_records=default_lineage_visibility_records(),
        source_to_surface_visibility=default_source_to_surface_visibility(),
        evidence_origin_visibility=default_evidence_origin_visibility(),
        support_status_lineage_visibility=default_support_status_lineage_visibility(),
        explainability_lineage_visibility=default_explainability_lineage_visibility(),
        trust_summary_lineage_visibility=default_trust_summary_lineage_visibility(),
        stale_unknown_provenance_visibility=(
            default_stale_unknown_provenance_visibility()
        ),
        provenance_lineage_summaries=default_provenance_lineage_summaries(),
        provenance_lineage_diagnostics=default_provenance_lineage_diagnostics(),
        unsupported_operational_state_visibility=(
            default_unsupported_operational_state_visibility()
        ),
        deterministic_guarantees=(
            V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_DETERMINISTIC_GUARANTEES
        ),
        inherited_prohibitions=(
            V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_INHERITED_PROHIBITIONS
        ),
        inherited_constraints=(
            V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_INHERITED_CONSTRAINTS
        ),
        explicit_limitations=(
            V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_EXPLICIT_LIMITATIONS
        ),
    )
