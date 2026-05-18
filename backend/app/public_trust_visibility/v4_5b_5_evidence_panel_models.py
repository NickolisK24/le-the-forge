"""Deterministic v4.5B.5 public evidence panel models.

The v4.5B.5 layer models public-facing evidence panels without enabling
evidence authority, approval, authorization, scoring, ranking, recommendation,
execution, remediation, runtime mutation, planner integration, production
consumption, or operational behavior.
"""

from __future__ import annotations

from dataclasses import dataclass


V4_5B_5_EVIDENCE_PANEL_PHASE_ID = "v4_5b_5_evidence_panels"
V4_5B_5_EVIDENCE_PANEL_SCHEMA_VERSION = "v4_5b_5.evidence_panels.1"
V4_5B_5_EVIDENCE_PANEL_REPORT_SCHEMA_VERSION = "v4_5b_5.evidence_panels_report.1"
V4_5B_5_EVIDENCE_PANEL_GENERATED_AT = "2026-05-18T00:00:00+00:00"
V4_5B_5_EVIDENCE_PANEL_STATUS_STABLE = "v4_5b_5_evidence_panels_stable"
V4_5B_5_EVIDENCE_PANEL_STATUS_BLOCKED = "v4_5b_5_evidence_panels_blocked"
V4_5B_5_EVIDENCE_PANEL_PURPOSE = (
    "deterministic_governance_safe_public_evidence_panels_descriptive_only"
)
V4_5B_5_EVIDENCE_PANEL_CLASSIFICATION = (
    "governance_safe_public_evidence_panel_visibility_descriptive_only"
)

V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_REPORT_REFERENCE = (
    "docs/generated/v4_5b_4_provenance_lineage_visibility_report.json"
)
V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_REPORT_HASH_REFERENCE = (
    "54f92af249e375100b491234aee93f6f557042f4ee9cae9af81a05be9de4065e"
)

EVIDENCE_PANEL_STATEMENT = "Evidence panels are descriptive-only."
EVIDENCE_VISIBILITY_NON_AUTHORITY_STATEMENT = (
    "Evidence visibility does NOT imply authorization, approval, correctness "
    "guarantee, trust score, ranking, recommendation, operational readiness, "
    "execution safety, or production enablement."
)

EVIDENCE_GROUPING_TYPES: tuple[str, ...] = (
    "trust_summary_evidence",
    "support_status_evidence",
    "explainability_evidence",
    "provenance_evidence",
    "lineage_evidence",
    "limitation_evidence",
    "unsupported_state_evidence",
    "diagnostics_evidence",
)

EVIDENCE_SOURCE_VISIBILITY_TYPES: tuple[str, ...] = (
    "source_references",
    "evidence_origin_references",
    "evidence_provenance_references",
    "evidence_lineage_references",
    "evidence_continuity_references",
    "evidence_diagnostics_references",
)

EVIDENCE_FRESHNESS_VISIBILITY_TYPES: tuple[str, ...] = (
    "current_evidence",
    "stale_evidence",
    "unknown_freshness_evidence",
    "incomplete_freshness_evidence",
    "unsupported_freshness_evidence",
)

SUPPORT_STATUS_EVIDENCE_PANEL_TYPES: tuple[str, ...] = (
    "supported_status_evidence",
    "partially_supported_status_evidence",
    "unsupported_status_evidence",
    "experimental_status_evidence",
    "deprecated_status_evidence",
    "blocked_status_evidence",
    "unknown_status_evidence",
)

EXPLAINABILITY_EVIDENCE_PANEL_TYPES: tuple[str, ...] = (
    "support_explanation_evidence",
    "limitation_explanation_evidence",
    "unsupported_state_explanation_evidence",
    "continuity_explanation_evidence",
    "trust_explanation_evidence",
    "diagnostic_explanation_evidence",
)

PROVENANCE_LINEAGE_EVIDENCE_PANEL_TYPES: tuple[str, ...] = (
    "provenance_evidence",
    "lineage_evidence",
    "source_to_surface_evidence",
    "evidence_origin_panels",
    "stale_unknown_provenance_evidence",
    "incomplete_lineage_evidence",
)

UNSUPPORTED_MISSING_EVIDENCE_TYPES: tuple[str, ...] = (
    "missing_support_evidence",
    "missing_explanation_evidence",
    "missing_provenance_evidence",
    "missing_lineage_evidence",
    "unsupported_evidence_states",
    "incomplete_evidence_states",
    "blocked_evidence_states",
    "unknown_evidence_states",
)

EVIDENCE_PANEL_SUMMARY_TYPES: tuple[str, ...] = (
    "evidence_panel_summary",
    "evidence_grouping_summary",
    "evidence_source_summary",
    "evidence_freshness_summary",
    "support_status_evidence_summary",
    "explainability_evidence_summary",
    "provenance_lineage_evidence_summary",
    "unsupported_missing_evidence_summary",
    "diagnostics_evidence_summary",
)

EVIDENCE_PANEL_DIAGNOSTIC_TYPES: tuple[str, ...] = (
    "missing_evidence_panel_references",
    "incomplete_evidence_grouping",
    "missing_evidence_source_visibility",
    "stale_evidence_visibility",
    "unknown_freshness_visibility",
    "unsupported_evidence_panel_states",
    "source_to_panel_continuity_gaps",
    "inherited_evidence_limitation_gaps",
    "inherited_evidence_prohibition_gaps",
)

UNSUPPORTED_EVIDENCE_PANEL_OPERATIONAL_STATES: tuple[str, ...] = (
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
    "evidence_based_authorization",
    "evidence_based_approval",
    "evidence_based_ranking",
    "evidence_based_recommendation",
    "evidence_scoring",
    "trust_scoring",
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

V4_5B_5_EVIDENCE_PANEL_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
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
    "enabled_evidence_authorization_count",
    "enabled_evidence_approval_count",
    "enabled_evidence_ranking_count",
    "enabled_evidence_recommendation_count",
    "enabled_scoring_count",
    "enabled_remediation_count",
    "enabled_repair_count",
    "enabled_mitigation_count",
    "enabled_auto_correction_count",
    "enabled_planner_integration_count",
    "enabled_production_consumption_count",
    "enabled_runtime_mutation_count",
    "enabled_operational_mutation_count",
)

V4_5B_5_EVIDENCE_PANEL_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "deterministic_evidence_panel_identity",
    "deterministic_evidence_grouping_visibility",
    "deterministic_evidence_source_visibility",
    "deterministic_evidence_freshness_visibility",
    "deterministic_support_status_evidence_panels",
    "deterministic_explainability_evidence_panels",
    "deterministic_provenance_lineage_evidence_panels",
    "deterministic_unsupported_missing_evidence_visibility",
    "stable_replay_safe_serialization",
    "stable_replay_safe_hashing",
    "lineage_continuity_preserved",
    "provenance_continuity_preserved",
    "publicly_transparent_descriptive_only_evidence_panels",
)

V4_5B_5_EVIDENCE_PANEL_INHERITED_PROHIBITIONS: tuple[str, ...] = (
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
    "evidence_based_authorization_prohibited",
    "evidence_based_approval_prohibited",
    "evidence_based_ranking_prohibited",
    "evidence_based_recommendation_prohibited",
    "evidence_scoring_prohibited",
    "trust_scoring_prohibited",
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

V4_5B_5_EVIDENCE_PANEL_INHERITED_CONSTRAINTS: tuple[str, ...] = (
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
    "NON-scoring",
)

V4_5B_5_EVIDENCE_PANEL_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "evidence_panels_do_not_authorize",
    "evidence_panels_do_not_approve",
    "evidence_panels_do_not_rank",
    "evidence_panels_do_not_recommend",
    "evidence_panels_do_not_score",
    "evidence_panels_do_not_execute",
    "evidence_panels_do_not_enable_production",
    "evidence_panels_do_not_imply_correctness_guarantees",
    "evidence_panels_do_not_imply_execution_safety",
    "evidence_panels_do_not_remediate_or_repair",
    "evidence_panels_do_not_mitigate_or_correct",
    "evidence_panels_do_not_integrate_planners",
    "evidence_panels_do_not_mutate_runtime_state",
)


def _set_tuple_field(instance: object, field_name: str) -> None:
    object.__setattr__(instance, field_name, tuple(getattr(instance, field_name)))


@dataclass(frozen=True)
class EvidencePanelIdentity:
    evidence_panel_id: str
    evidence_group_id: str
    evidence_item_id: str
    trust_summary_reference_id: str
    support_status_reference_id: str
    explainability_surface_reference_id: str
    provenance_visibility_reference_id: str
    lineage_visibility_reference_id: str
    diagnostics_reference_id: str
    continuity_reference_id: str
    lineage_reference_id: str
    provenance_reference_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    source_provenance_lineage_report_reference: str
    source_provenance_lineage_hash_reference: str


@dataclass(frozen=True)
class EvidencePanelRecord:
    panel_record_id: str
    evidence_panel_id: str
    evidence_group_id: str
    evidence_item_id: str
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    publicly_transparent: bool = True
    fail_visible: bool = True
    evidence_authority_enabled: bool = False
    evidence_authorization_enabled: bool = False
    evidence_approval_enabled: bool = False
    evidence_ranking_enabled: bool = False
    evidence_recommendation_enabled: bool = False
    evidence_scoring_enabled: bool = False
    trust_scoring_enabled: bool = False


@dataclass(frozen=True)
class EvidenceGroupRecord:
    group_record_id: str
    grouping_type: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    prioritization_enabled: bool = False
    ranking_enabled: bool = False
    recommendation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class EvidenceItemRecord:
    item_record_id: str
    evidence_item_type: str
    source_reference_id: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    replay_safe: bool = True
    provenance_safe: bool = True
    scoring_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class EvidenceSourceVisibility:
    source_visibility_id: str
    source_visibility_type: str
    source_reference_id: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    source_authority_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    scoring_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class EvidenceFreshnessVisibility:
    freshness_visibility_id: str
    freshness_type: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_refresh_enabled: bool = False
    fallback_substitution_enabled: bool = False
    scoring_enabled: bool = False
    authorization_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class SupportStatusEvidencePanel:
    support_panel_id: str
    support_evidence_type: str
    support_status_reference_id: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    approval_enabled: bool = False
    ranking_enabled: bool = False
    recommendation_enabled: bool = False
    operational_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ExplainabilityEvidencePanel:
    explainability_panel_id: str
    explainability_evidence_type: str
    explainability_surface_reference_id: str
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
class ProvenanceLineageEvidencePanel:
    provenance_lineage_panel_id: str
    provenance_lineage_evidence_type: str
    provenance_reference_id: str
    lineage_reference_id: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    deterministic_order: int
    descriptive_only: bool = True
    trust_scoring_enabled: bool = False
    source_scoring_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    ranking_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class UnsupportedMissingEvidenceVisibility:
    unsupported_missing_id: str
    unsupported_missing_type: str
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
class EvidencePanelSummaryRecord:
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
    scoring_enabled: bool = False
    execution_enablement_enabled: bool = False
    production_enablement_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class EvidencePanelDiagnosticRecord:
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
    scoring_enabled: bool = False
    orchestration_response_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class UnsupportedEvidencePanelOperationalStateVisibility:
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
    scoring_enabled: bool = False
    suppression_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class EvidencePanelIntelligence:
    evidence_identity: EvidencePanelIdentity
    evidence_panel_records: tuple[EvidencePanelRecord, ...]
    evidence_group_records: tuple[EvidenceGroupRecord, ...]
    evidence_item_records: tuple[EvidenceItemRecord, ...]
    evidence_source_visibility: tuple[EvidenceSourceVisibility, ...]
    evidence_freshness_visibility: tuple[EvidenceFreshnessVisibility, ...]
    support_status_evidence_panels: tuple[SupportStatusEvidencePanel, ...]
    explainability_evidence_panels: tuple[ExplainabilityEvidencePanel, ...]
    provenance_lineage_evidence_panels: tuple[ProvenanceLineageEvidencePanel, ...]
    unsupported_missing_evidence_visibility: tuple[
        UnsupportedMissingEvidenceVisibility, ...
    ]
    evidence_panel_summaries: tuple[EvidencePanelSummaryRecord, ...]
    evidence_panel_diagnostics: tuple[EvidencePanelDiagnosticRecord, ...]
    unsupported_operational_state_visibility: tuple[
        UnsupportedEvidencePanelOperationalStateVisibility, ...
    ]
    deterministic_guarantees: tuple[str, ...]
    inherited_prohibitions: tuple[str, ...]
    inherited_constraints: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    evidence_panel_statement: str = EVIDENCE_PANEL_STATEMENT
    evidence_visibility_non_authority_statement: str = (
        EVIDENCE_VISIBILITY_NON_AUTHORITY_STATEMENT
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
    non_scoring: bool = True
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
    evidence_authorization_enabled: bool = False
    evidence_approval_enabled: bool = False
    evidence_ranking_enabled: bool = False
    evidence_recommendation_enabled: bool = False
    evidence_scoring_enabled: bool = False
    trust_scoring_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    mitigation_enabled: bool = False
    auto_correction_enabled: bool = False
    ranking_enabled: bool = False
    recommendation_enabled: bool = False
    scoring_enabled: bool = False
    planner_integration_enabled: bool = False
    planner_execution_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "evidence_panel_records",
            "evidence_group_records",
            "evidence_item_records",
            "evidence_source_visibility",
            "evidence_freshness_visibility",
            "support_status_evidence_panels",
            "explainability_evidence_panels",
            "provenance_lineage_evidence_panels",
            "unsupported_missing_evidence_visibility",
            "evidence_panel_summaries",
            "evidence_panel_diagnostics",
            "unsupported_operational_state_visibility",
            "deterministic_guarantees",
            "inherited_prohibitions",
            "inherited_constraints",
            "explicit_limitations",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))


def default_evidence_panel_identity() -> EvidencePanelIdentity:
    return EvidencePanelIdentity(
        evidence_panel_id="v4_5b_5_evidence_panels",
        evidence_group_id="v4_5b_5_evidence_group",
        evidence_item_id="v4_5b_5_evidence_item",
        trust_summary_reference_id="trust::v4_5b_5.evidence_panels",
        support_status_reference_id="support::v4_5b_2.public_support",
        explainability_surface_reference_id="explainability::v4_5b_3.public_surfaces",
        provenance_visibility_reference_id="provenance::v4_5b_4.public_trust",
        lineage_visibility_reference_id="lineage::v4_5b_4.public_trust",
        diagnostics_reference_id="diagnostics::v4_5b_5.evidence_panels",
        continuity_reference_id="continuity::v4_5b_5.evidence_panels",
        lineage_reference_id="lineage::v4_5b_5.evidence_panels",
        provenance_reference_id="provenance::v4_5b_5.evidence_panels",
        phase_id=V4_5B_5_EVIDENCE_PANEL_PHASE_ID,
        schema_version=V4_5B_5_EVIDENCE_PANEL_SCHEMA_VERSION,
        generated_at=V4_5B_5_EVIDENCE_PANEL_GENERATED_AT,
        classification=V4_5B_5_EVIDENCE_PANEL_CLASSIFICATION,
        source_provenance_lineage_report_reference=(
            V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_REPORT_REFERENCE
        ),
        source_provenance_lineage_hash_reference=(
            V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_REPORT_HASH_REFERENCE
        ),
    )


def default_evidence_panel_records() -> tuple[EvidencePanelRecord, ...]:
    identity = default_evidence_panel_identity()
    return (
        EvidencePanelRecord(
            panel_record_id="public_evidence_panel_foundation",
            evidence_panel_id=identity.evidence_panel_id,
            evidence_group_id=identity.evidence_group_id,
            evidence_item_id=identity.evidence_item_id,
            visibility_state="public_evidence_panel_visible",
            deterministic_order=1,
        ),
    )


def default_evidence_group_records() -> tuple[EvidenceGroupRecord, ...]:
    return tuple(
        EvidenceGroupRecord(
            group_record_id=f"evidence_group_{item}",
            grouping_type=item,
            evidence_reference_ids=(f"evidence_{item}",),
            visibility_state="evidence_grouping_descriptive_only",
            deterministic_order=order,
        )
        for order, item in enumerate(EVIDENCE_GROUPING_TYPES, start=1)
    )


def default_evidence_item_records() -> tuple[EvidenceItemRecord, ...]:
    return tuple(
        EvidenceItemRecord(
            item_record_id=f"evidence_item_{item}",
            evidence_item_type=item,
            source_reference_id=f"source_reference_{item}",
            evidence_reference_ids=(f"evidence_item_reference_{item}",),
            visibility_state="evidence_item_replay_safe",
            deterministic_order=order,
        )
        for order, item in enumerate(EVIDENCE_GROUPING_TYPES, start=1)
    )


def default_evidence_source_visibility() -> tuple[EvidenceSourceVisibility, ...]:
    return tuple(
        EvidenceSourceVisibility(
            source_visibility_id=f"evidence_source_{item}",
            source_visibility_type=item,
            source_reference_id=f"source_reference_{item}",
            evidence_reference_ids=(f"evidence_{item}",),
            visibility_state="evidence_source_visibility_descriptive_only",
            deterministic_order=order,
        )
        for order, item in enumerate(EVIDENCE_SOURCE_VISIBILITY_TYPES, start=1)
    )


def default_evidence_freshness_visibility() -> tuple[EvidenceFreshnessVisibility, ...]:
    return tuple(
        EvidenceFreshnessVisibility(
            freshness_visibility_id=f"evidence_freshness_{item}",
            freshness_type=item,
            evidence_reference_ids=(f"evidence_{item}",),
            visibility_state="evidence_freshness_fail_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(EVIDENCE_FRESHNESS_VISIBILITY_TYPES, start=1)
    )


def default_support_status_evidence_panels() -> tuple[SupportStatusEvidencePanel, ...]:
    return tuple(
        SupportStatusEvidencePanel(
            support_panel_id=f"support_status_evidence_panel_{item}",
            support_evidence_type=item,
            support_status_reference_id=f"support_status_reference_{item}",
            evidence_reference_ids=(f"evidence_{item}",),
            visibility_state="support_status_evidence_panel_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(SUPPORT_STATUS_EVIDENCE_PANEL_TYPES, start=1)
    )


def default_explainability_evidence_panels() -> tuple[ExplainabilityEvidencePanel, ...]:
    return tuple(
        ExplainabilityEvidencePanel(
            explainability_panel_id=f"explainability_evidence_panel_{item}",
            explainability_evidence_type=item,
            explainability_surface_reference_id=f"explainability_reference_{item}",
            evidence_reference_ids=(f"evidence_{item}",),
            visibility_state="explainability_evidence_panel_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(EXPLAINABILITY_EVIDENCE_PANEL_TYPES, start=1)
    )


def default_provenance_lineage_evidence_panels() -> tuple[
    ProvenanceLineageEvidencePanel, ...
]:
    return tuple(
        ProvenanceLineageEvidencePanel(
            provenance_lineage_panel_id=f"provenance_lineage_evidence_panel_{item}",
            provenance_lineage_evidence_type=item,
            provenance_reference_id=f"provenance_reference_{item}",
            lineage_reference_id=f"lineage_reference_{item}",
            evidence_reference_ids=(f"evidence_{item}",),
            visibility_state="provenance_lineage_evidence_panel_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(PROVENANCE_LINEAGE_EVIDENCE_PANEL_TYPES, start=1)
    )


def default_unsupported_missing_evidence_visibility() -> tuple[
    UnsupportedMissingEvidenceVisibility, ...
]:
    return tuple(
        UnsupportedMissingEvidenceVisibility(
            unsupported_missing_id=f"unsupported_missing_evidence_{item}",
            unsupported_missing_type=item,
            evidence_reference_ids=(f"evidence_{item}",),
            visibility_state="unsupported_missing_evidence_fail_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(UNSUPPORTED_MISSING_EVIDENCE_TYPES, start=1)
    )


def default_evidence_panel_summaries() -> tuple[EvidencePanelSummaryRecord, ...]:
    return tuple(
        EvidencePanelSummaryRecord(
            summary_record_id=f"evidence_panel_summary_{item}",
            summary_type=item,
            evidence_reference_ids=(f"evidence_{item}",),
            summary_state="evidence_panel_summary_descriptive_only",
            deterministic_order=order,
        )
        for order, item in enumerate(EVIDENCE_PANEL_SUMMARY_TYPES, start=1)
    )


def default_evidence_panel_diagnostics() -> tuple[EvidencePanelDiagnosticRecord, ...]:
    return tuple(
        EvidencePanelDiagnosticRecord(
            diagnostic_id=f"evidence_panel_diagnostic_{item}",
            diagnostic_type=item,
            evidence_reference_ids=(f"evidence_{item}",),
            message=(
                f"{item} remains explicit, fail-visible, and descriptive-only "
                "for deterministic public evidence panels."
            ),
            visibility_state="fail_visible_evidence_panel_diagnostic_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(EVIDENCE_PANEL_DIAGNOSTIC_TYPES, start=1)
    )


def default_unsupported_operational_state_visibility() -> tuple[
    UnsupportedEvidencePanelOperationalStateVisibility, ...
]:
    return tuple(
        UnsupportedEvidencePanelOperationalStateVisibility(
            state_id=f"unsupported_evidence_panel_operational_state_{item}",
            unsupported_state=item,
            explicit_reason=(
                f"{item} remains unsupported for v4.5B.5 deterministic "
                "public evidence panels."
            ),
            evidence_reference_ids=("evidence_unsupported_evidence_panel_states",),
            visibility_state="unsupported_evidence_panel_operational_state_fail_visible",
            deterministic_order=order,
        )
        for order, item in enumerate(
            UNSUPPORTED_EVIDENCE_PANEL_OPERATIONAL_STATES,
            start=1,
        )
    )


def default_v4_5b_5_evidence_panels() -> EvidencePanelIntelligence:
    return EvidencePanelIntelligence(
        evidence_identity=default_evidence_panel_identity(),
        evidence_panel_records=default_evidence_panel_records(),
        evidence_group_records=default_evidence_group_records(),
        evidence_item_records=default_evidence_item_records(),
        evidence_source_visibility=default_evidence_source_visibility(),
        evidence_freshness_visibility=default_evidence_freshness_visibility(),
        support_status_evidence_panels=default_support_status_evidence_panels(),
        explainability_evidence_panels=default_explainability_evidence_panels(),
        provenance_lineage_evidence_panels=(
            default_provenance_lineage_evidence_panels()
        ),
        unsupported_missing_evidence_visibility=(
            default_unsupported_missing_evidence_visibility()
        ),
        evidence_panel_summaries=default_evidence_panel_summaries(),
        evidence_panel_diagnostics=default_evidence_panel_diagnostics(),
        unsupported_operational_state_visibility=(
            default_unsupported_operational_state_visibility()
        ),
        deterministic_guarantees=V4_5B_5_EVIDENCE_PANEL_DETERMINISTIC_GUARANTEES,
        inherited_prohibitions=V4_5B_5_EVIDENCE_PANEL_INHERITED_PROHIBITIONS,
        inherited_constraints=V4_5B_5_EVIDENCE_PANEL_INHERITED_CONSTRAINTS,
        explicit_limitations=V4_5B_5_EVIDENCE_PANEL_EXPLICIT_LIMITATIONS,
    )
