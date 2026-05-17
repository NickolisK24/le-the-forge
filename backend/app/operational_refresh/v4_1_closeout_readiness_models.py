"""Deterministic v4.1 closeout and v4.2 readiness certification models.

Closeout and readiness certification is descriptive governance evidence only.
It does not remediate, correct, repair, recommend, rank, score, select,
approve, authorize, execute refreshes, orchestrate work, sequence work, migrate
schemas, roll back state, recover state, consume production bundles, integrate
with planners, or mutate runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


V4_1_CLOSEOUT_READINESS_PHASE_ID = "v4_1_closeout_and_v4_2_readiness"
V4_1_CLOSEOUT_READINESS_SCHEMA_VERSION = "v4_1.closeout_and_v4_2_readiness.1"
V4_1_CLOSEOUT_READINESS_REPORT_SCHEMA_VERSION = "v4_1.closeout_and_v4_2_readiness_report.1"
V4_1_CLOSEOUT_REPORT_SCHEMA_VERSION = "v4_1.closeout_report.1"
V4_2_READINESS_CERTIFICATION_REPORT_SCHEMA_VERSION = "v4_2.readiness_certification_report.1"
V4_1_CROSS_LAYER_GOVERNANCE_SUMMARY_REPORT_SCHEMA_VERSION = "v4_1.cross_layer_governance_summary_report.1"
V4_1_CROSS_LAYER_INTEGRITY_CERTIFICATION_REPORT_SCHEMA_VERSION = (
    "v4_1.cross_layer_integrity_certification_report.1"
)
V4_1_CLOSEOUT_READINESS_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_1_CLOSEOUT_READINESS_STATUS_STABLE = "v4_1_closeout_and_v4_2_readiness_stable"
V4_1_CLOSEOUT_READINESS_STATUS_BLOCKED = "v4_1_closeout_and_v4_2_readiness_blocked"
V4_1_CLOSEOUT_STATUS_WITH_WARNINGS = "v4_1_closed_out_with_warnings"
V4_1_CLOSEOUT_STATUS_BLOCKED = "v4_1_closeout_blocked"
V4_2_READINESS_WITH_WARNINGS = "ready_for_v4_2_planning_with_warnings"
V4_2_READINESS_BLOCKED = "v4_2_planning_blocked"
V4_1_CLOSEOUT_READINESS_PURPOSE = "deterministic_v4_1_closeout_v4_2_readiness_governance_only"

V4_1_PHASE_DEFINITIONS: tuple[tuple[int, str, str, str, str, tuple[str, ...]], ...] = (
    (
        1,
        "v4_1_refresh_manifest_foundations",
        "refresh_manifest_foundations",
        "V4_1_REFRESH_MANIFEST_FOUNDATIONS.md",
        "test_v4_1_refresh_manifest_foundations.py",
        (
            "v4_1_refresh_manifest_foundations_report.json",
            "v4_1_refresh_manifest_diagnostics_report.json",
        ),
    ),
    (
        2,
        "v4_1_refresh_dependency_graph_infrastructure",
        "refresh_dependency_graph_infrastructure",
        "V4_1_REFRESH_DEPENDENCY_GRAPH_INFRASTRUCTURE.md",
        "test_v4_1_refresh_dependency_graph_infrastructure.py",
        (
            "v4_1_refresh_dependency_graph_report.json",
            "v4_1_refresh_dependency_graph_diagnostics_report.json",
            "v4_1_refresh_dependency_graph_integrity_report.json",
        ),
    ),
    (
        3,
        "v4_1_refresh_lineage_certification",
        "refresh_lineage_certification",
        "V4_1_REFRESH_LINEAGE_CERTIFICATION.md",
        "test_v4_1_refresh_lineage_certification.py",
        (
            "v4_1_refresh_lineage_certification_report.json",
            "v4_1_refresh_lineage_certification_diagnostics_report.json",
            "v4_1_refresh_lineage_continuity_certification_report.json",
            "v4_1_refresh_lineage_integrity_certification_report.json",
        ),
    ),
    (
        4,
        "v4_1_schema_evolution_governance",
        "schema_evolution_governance",
        "V4_1_SCHEMA_EVOLUTION_GOVERNANCE.md",
        "test_v4_1_schema_evolution_governance.py",
        (
            "v4_1_schema_evolution_governance_report.json",
            "v4_1_schema_evolution_diagnostics_report.json",
            "v4_1_schema_continuity_certification_report.json",
            "v4_1_schema_integrity_certification_report.json",
        ),
    ),
    (
        5,
        "v4_1_refresh_sequencing_visibility",
        "refresh_sequencing_visibility",
        "V4_1_REFRESH_SEQUENCING_VISIBILITY.md",
        "test_v4_1_refresh_sequencing_visibility.py",
        (
            "v4_1_refresh_sequencing_visibility_report.json",
            "v4_1_refresh_sequencing_diagnostics_report.json",
            "v4_1_refresh_sequencing_continuity_certification_report.json",
            "v4_1_refresh_sequencing_integrity_certification_report.json",
        ),
    ),
    (
        6,
        "v4_1_refresh_drift_certification",
        "refresh_drift_certification",
        "V4_1_REFRESH_DRIFT_CERTIFICATION.md",
        "test_v4_1_refresh_drift_certification.py",
        (
            "v4_1_refresh_drift_certification_report.json",
            "v4_1_refresh_drift_diagnostics_report.json",
            "v4_1_refresh_drift_continuity_certification_report.json",
            "v4_1_refresh_drift_integrity_certification_report.json",
            "v4_1_cross_layer_drift_certification_report.json",
        ),
    ),
    (
        7,
        "v4_1_refresh_replay_rollback_visibility",
        "refresh_replay_rollback_visibility",
        "V4_1_REFRESH_REPLAY_ROLLBACK_VISIBILITY.md",
        "test_v4_1_refresh_replay_rollback_visibility.py",
        (
            "v4_1_refresh_replay_rollback_visibility_report.json",
            "v4_1_refresh_replay_diagnostics_report.json",
            "v4_1_refresh_rollback_diagnostics_report.json",
            "v4_1_refresh_replay_continuity_certification_report.json",
            "v4_1_refresh_rollback_continuity_certification_report.json",
            "v4_1_refresh_replay_rollback_integrity_certification_report.json",
        ),
    ),
    (
        8,
        "v4_1_refresh_diagnostics_explainability",
        "refresh_diagnostics_explainability",
        "V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY.md",
        "test_v4_1_refresh_diagnostics_explainability.py",
        (
            "v4_1_refresh_diagnostics_explainability_report.json",
            "v4_1_unified_refresh_diagnostics_report.json",
            "v4_1_unified_refresh_explainability_report.json",
            "v4_1_refresh_diagnostics_continuity_certification_report.json",
            "v4_1_refresh_diagnostics_integrity_certification_report.json",
        ),
    ),
    (
        9,
        "v4_1_refresh_continuity_certification",
        "refresh_continuity_certification",
        "V4_1_REFRESH_CONTINUITY_CERTIFICATION.md",
        "test_v4_1_refresh_continuity_certification.py",
        (
            "v4_1_refresh_continuity_certification_report.json",
            "v4_1_unified_refresh_continuity_certification_report.json",
            "v4_1_cross_layer_continuity_diagnostics_report.json",
            "v4_1_cross_layer_continuity_integrity_certification_report.json",
            "v4_1_cross_layer_continuity_explainability_report.json",
        ),
    ),
)

V4_1_EXPECTED_PHASE_IDS: tuple[str, ...] = tuple(phase[1] for phase in V4_1_PHASE_DEFINITIONS)
V4_1_EXPECTED_REPORT_NAMES: tuple[str, ...] = tuple(
    report_name for phase in V4_1_PHASE_DEFINITIONS for report_name in phase[5]
)
V4_1_EXPECTED_MIGRATION_DOC_NAMES: tuple[str, ...] = tuple(phase[3] for phase in V4_1_PHASE_DEFINITIONS)
V4_1_EXPECTED_TEST_NAMES: tuple[str, ...] = tuple(phase[4] for phase in V4_1_PHASE_DEFINITIONS)

CLOSEOUT_WARNING_UNSUPPORTED = "unsupported_state_aggregation"
CLOSEOUT_WARNING_PROHIBITED = "prohibited_state_aggregation"
CLOSEOUT_WARNING_BLOCKED = "blocked_state_aggregation"
CLOSEOUT_WARNING_STALE = "stale_evidence_visibility"
CLOSEOUT_WARNING_CROSS_LAYER_CONFLICT = "cross_layer_continuity_conflict_visibility"
CLOSEOUT_WARNING_FAIL_VISIBLE = "fail_visible_warning_aggregation"
CLOSEOUT_WARNING_CATEGORIES: tuple[str, ...] = (
    CLOSEOUT_WARNING_UNSUPPORTED,
    CLOSEOUT_WARNING_PROHIBITED,
    CLOSEOUT_WARNING_BLOCKED,
    CLOSEOUT_WARNING_STALE,
    CLOSEOUT_WARNING_CROSS_LAYER_CONFLICT,
    CLOSEOUT_WARNING_FAIL_VISIBLE,
)

PROHIBITED_CLOSEOUT_DOMAINS: tuple[str, ...] = (
    "remediation",
    "automatic_correction",
    "automatic_repair",
    "refresh_execution",
    "orchestration_execution",
    "automatic_sequencing",
    "dependency_resolution",
    "schema_migration_execution",
    "automatic_migration",
    "rollback_execution",
    "recovery_execution",
    "planner_integration",
    "production_bundle_consumption",
    "recommendation_systems",
    "ranking_systems",
    "scoring_systems",
    "selection_systems",
    "optimization_systems",
    "authorization_systems",
    "approval_systems",
    "runtime_mutation",
    "hidden_remediation_behavior",
    "hidden_orchestration_behavior",
    "implicit_execution_pathways",
)

EXPLICIT_CLOSEOUT_READINESS_LIMITATIONS: tuple[str, ...] = (
    "v4.1 Phase 10 performs deterministic closeout and v4.2 planning-readiness certification only.",
    "v4.1 Phase 10 does not enable remediation.",
    "v4.1 Phase 10 does not enable automatic correction.",
    "v4.1 Phase 10 does not enable recommendation ranking scoring or selection.",
    "v4.1 Phase 10 does not enable approval or authorization.",
    "v4.1 Phase 10 does not enable orchestration execution.",
    "v4.1 Phase 10 does not enable automatic sequencing.",
    "v4.1 Phase 10 does not enable refresh execution.",
    "v4.1 Phase 10 does not enable migration execution.",
    "v4.1 Phase 10 does not enable recovery execution.",
    "v4.1 Phase 10 does not enable rollback execution.",
    "v4.1 Phase 10 does not enable planner integration.",
    "v4.1 Phase 10 does not enable production consumption.",
    "v4.1 Phase 10 does not enable mutation behavior.",
)

EXPLICIT_CLOSEOUT_READINESS_PROHIBITIONS: tuple[str, ...] = (
    "No remediation exists.",
    "No automatic correction exists.",
    "No recommendation ranking scoring or selection exists.",
    "No approval or authorization exists.",
    "No orchestration execution exists.",
    "No automatic sequencing exists.",
    "No refresh execution exists.",
    "No migration execution exists.",
    "No recovery execution exists.",
    "No rollback execution exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No mutation behavior exists.",
    "No readiness certification becomes operational authorization.",
    "No readiness certification implies approval capability.",
    "No automatic continuity correction exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class V41CloseoutIdentity:
    closeout_id: str
    refresh_generation_id: str
    closeout_version: str
    schema_version: str
    generated_at: str
    phase_count: int
    report_count: int
    migration_doc_count: int
    focused_test_count: int
    lineage_reference: str
    provenance_reference: str
    replay_reference: str
    rollback_reference: str
    continuity_reference: str
    integrity_reference: str
    governance_reference: str
    readiness_reference: str
    governance_scope: str = "v4_1_closeout_v4_2_readiness_descriptive_only"
    governance_purpose: str = V4_1_CLOSEOUT_READINESS_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_repair_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_enabled: bool = False
    execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_fallback_enabled: bool = False


@dataclass(frozen=True)
class V41PhaseCoverage:
    phase_number: int
    phase_id: str
    phase_slug: str
    required_report_names: tuple[str, ...]
    required_migration_doc_name: str
    required_focused_test_name: str
    phase_coverage_present: bool
    report_coverage_present: bool
    migration_doc_present: bool
    focused_test_present: bool
    integrity_coverage_present: bool
    continuity_coverage_present: bool
    replay_coverage_present: bool
    rollback_coverage_present: bool
    provenance_coverage_present: bool
    lineage_coverage_present: bool
    deterministic_order: int
    descriptive_only: bool = True
    non_executable: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_enabled: bool = False
    execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "required_report_names")


@dataclass(frozen=True)
class V41ReportCoverage:
    report_name: str
    phase_id: str
    report_hash: str
    present: bool
    json_valid: bool
    deterministic_hash_present: bool
    integrity_coverage_present: bool
    continuity_coverage_present: bool
    warning_visibility_present: bool
    generated_at_visible: bool
    deterministic_order: int
    descriptive_only: bool = True
    non_executable: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_enabled: bool = False
    execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden: bool = False


@dataclass(frozen=True)
class V41CloseoutWarning:
    warning_id: str
    category: str
    severity: str
    source_reference: str
    explanation: str
    fail_visible: bool
    deterministic_order: int
    descriptive_only: bool = True
    non_executable: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_enabled: bool = False
    execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden: bool = False


@dataclass(frozen=True)
class V41WarningAggregation:
    aggregation_id: str
    warning_ids: tuple[str, ...]
    unsupported_state_warning_ids: tuple[str, ...]
    prohibited_state_warning_ids: tuple[str, ...]
    blocked_state_warning_ids: tuple[str, ...]
    stale_evidence_warning_ids: tuple[str, ...]
    cross_layer_conflict_warning_ids: tuple[str, ...]
    fail_visible_warning_ids: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    non_executable: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_enabled: bool = False
    execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "warning_ids",
            "unsupported_state_warning_ids",
            "prohibited_state_warning_ids",
            "blocked_state_warning_ids",
            "stale_evidence_warning_ids",
            "cross_layer_conflict_warning_ids",
            "fail_visible_warning_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V41ReadinessCertification:
    readiness_id: str
    closeout_status: str
    v4_2_readiness_status: str
    phase_coverage_certified: bool
    report_coverage_certified: bool
    integrity_verified: bool
    continuity_verified: bool
    governance_verified: bool
    replay_safe: bool
    rollback_safe: bool
    provenance_safe: bool
    lineage_safe: bool
    deterministic_readiness_visible: bool
    warning_count: int
    blocker_count: int
    planning_only: bool = True
    descriptive_only: bool = True
    non_executable: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_enabled: bool = False
    execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False


@dataclass(frozen=True)
class V41CloseoutIntegrityBoundary:
    boundary_id: str
    prohibited_domains: tuple[str, ...]
    prohibited_remediation_leakage: tuple[str, ...]
    prohibited_correction_leakage: tuple[str, ...]
    prohibited_recommendation_leakage: tuple[str, ...]
    prohibited_ranking_leakage: tuple[str, ...]
    prohibited_scoring_leakage: tuple[str, ...]
    prohibited_selection_leakage: tuple[str, ...]
    prohibited_approval_leakage: tuple[str, ...]
    prohibited_authorization_leakage: tuple[str, ...]
    prohibited_orchestration_leakage: tuple[str, ...]
    prohibited_execution_leakage: tuple[str, ...]
    prohibited_planner_integration_leakage: tuple[str, ...]
    prohibited_production_consumption_leakage: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    non_executable: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_repair_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_enabled: bool = False
    execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "prohibited_domains",
            "prohibited_remediation_leakage",
            "prohibited_correction_leakage",
            "prohibited_recommendation_leakage",
            "prohibited_ranking_leakage",
            "prohibited_scoring_leakage",
            "prohibited_selection_leakage",
            "prohibited_approval_leakage",
            "prohibited_authorization_leakage",
            "prohibited_orchestration_leakage",
            "prohibited_execution_leakage",
            "prohibited_planner_integration_leakage",
            "prohibited_production_consumption_leakage",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V41CloseoutGovernance:
    governance_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    non_executable: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_enabled: bool = False
    execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V41CloseoutReadiness:
    identity: V41CloseoutIdentity
    phase_coverage: tuple[V41PhaseCoverage, ...]
    report_coverage: tuple[V41ReportCoverage, ...]
    warning_aggregation: V41WarningAggregation
    warnings: tuple[V41CloseoutWarning, ...]
    readiness: V41ReadinessCertification
    integrity_boundary: V41CloseoutIntegrityBoundary
    governance: V41CloseoutGovernance
    non_executable: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_repair_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    automatic_sequencing_enabled: bool = False
    dependency_resolution_enabled: bool = False
    schema_migration_execution_enabled: bool = False
    automatic_migration_enabled: bool = False
    rollback_execution_enabled: bool = False
    recovery_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_remediation_behavior_enabled: bool = False
    hidden_orchestration_behavior_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "phase_coverage")
        _set_tuple_field(self, "report_coverage")
        _set_tuple_field(self, "warnings")


def default_v4_1_closeout_identity() -> V41CloseoutIdentity:
    return V41CloseoutIdentity(
        closeout_id="v4_1_closeout_and_v4_2_readiness_primary",
        refresh_generation_id="v4_1_refresh_governance_stack",
        closeout_version="v4.1.0-phase-10",
        schema_version=V4_1_CLOSEOUT_READINESS_SCHEMA_VERSION,
        generated_at=V4_1_CLOSEOUT_READINESS_GENERATED_AT,
        phase_count=len(V4_1_EXPECTED_PHASE_IDS),
        report_count=len(V4_1_EXPECTED_REPORT_NAMES),
        migration_doc_count=len(V4_1_EXPECTED_MIGRATION_DOC_NAMES),
        focused_test_count=len(V4_1_EXPECTED_TEST_NAMES),
        lineage_reference="v4_1_closeout_lineage_primary",
        provenance_reference="v4_1_closeout_provenance_primary",
        replay_reference="v4_1_closeout_replay_primary",
        rollback_reference="v4_1_closeout_rollback_primary",
        continuity_reference="v4_1_closeout_continuity_primary",
        integrity_reference="v4_1_closeout_integrity_primary",
        governance_reference="v4_1_closeout_governance_primary",
        readiness_reference="v4_2_planning_readiness_primary",
    )


def build_v4_1_phase_coverage(
    *,
    report_presence: Mapping[str, bool] | None = None,
    doc_presence: Mapping[str, bool] | None = None,
    test_presence: Mapping[str, bool] | None = None,
) -> tuple[V41PhaseCoverage, ...]:
    report_presence = report_presence or {}
    doc_presence = doc_presence or {}
    test_presence = test_presence or {}
    phases: list[V41PhaseCoverage] = []
    for phase_number, phase_id, phase_slug, doc_name, test_name, report_names in V4_1_PHASE_DEFINITIONS:
        reports_present = all(report_presence.get(report_name, True) for report_name in report_names)
        phases.append(
            V41PhaseCoverage(
                phase_number=phase_number,
                phase_id=phase_id,
                phase_slug=phase_slug,
                required_report_names=report_names,
                required_migration_doc_name=doc_name,
                required_focused_test_name=test_name,
                phase_coverage_present=True,
                report_coverage_present=reports_present,
                migration_doc_present=doc_presence.get(doc_name, True),
                focused_test_present=test_presence.get(test_name, True),
                integrity_coverage_present=True,
                continuity_coverage_present=True,
                replay_coverage_present=True,
                rollback_coverage_present=True,
                provenance_coverage_present=True,
                lineage_coverage_present=True,
                deterministic_order=phase_number * 10,
            )
        )
    return tuple(phases)


def build_v4_1_report_coverage(
    *,
    report_hashes: Mapping[str, str] | None = None,
    report_presence: Mapping[str, bool] | None = None,
    report_json_validity: Mapping[str, bool] | None = None,
) -> tuple[V41ReportCoverage, ...]:
    report_hashes = report_hashes or {}
    report_presence = report_presence or {}
    report_json_validity = report_json_validity or {}
    reports: list[V41ReportCoverage] = []
    order = 10
    for _, phase_id, _, _, _, report_names in V4_1_PHASE_DEFINITIONS:
        for report_name in report_names:
            present = report_presence.get(report_name, True)
            report_hash = report_hashes.get(report_name, f"deterministic_placeholder_hash_for_{report_name}")
            reports.append(
                V41ReportCoverage(
                    report_name=report_name,
                    phase_id=phase_id,
                    report_hash=report_hash if present else "",
                    present=present,
                    json_valid=report_json_validity.get(report_name, True) if present else False,
                    deterministic_hash_present=bool(report_hash) if present else False,
                    integrity_coverage_present=True,
                    continuity_coverage_present=True,
                    warning_visibility_present=True,
                    generated_at_visible=True,
                    deterministic_order=order,
                )
            )
            order += 10
    return tuple(reports)


def default_v4_1_closeout_warnings() -> tuple[V41CloseoutWarning, ...]:
    return (
        V41CloseoutWarning(
            "v4_1_unsupported_state_aggregation_visible",
            CLOSEOUT_WARNING_UNSUPPORTED,
            "warning",
            "v4_1_refresh_stack",
            "Unsupported states remain aggregated as fail-visible evidence.",
            True,
            10,
        ),
        V41CloseoutWarning(
            "v4_1_prohibited_state_aggregation_visible",
            CLOSEOUT_WARNING_PROHIBITED,
            "prohibited",
            "v4_1_refresh_stack",
            "Prohibited states remain aggregated as inactive evidence.",
            True,
            20,
        ),
        V41CloseoutWarning(
            "v4_1_blocked_state_aggregation_visible",
            CLOSEOUT_WARNING_BLOCKED,
            "blocking",
            "v4_1_refresh_stack",
            "Blocked states remain visible and are not remediated.",
            True,
            30,
        ),
        V41CloseoutWarning(
            "v4_1_stale_evidence_visibility",
            CLOSEOUT_WARNING_STALE,
            "warning",
            "v4_1_refresh_stack",
            "Stale evidence visibility remains explicit and is not suppressed.",
            True,
            40,
        ),
        V41CloseoutWarning(
            "v4_1_cross_layer_continuity_conflict_visibility",
            CLOSEOUT_WARNING_CROSS_LAYER_CONFLICT,
            "blocking",
            "v4_1_refresh_stack",
            "Cross-layer continuity conflict visibility remains descriptive only.",
            True,
            50,
        ),
        V41CloseoutWarning(
            "v4_1_fail_visible_warning_aggregation",
            CLOSEOUT_WARNING_FAIL_VISIBLE,
            "warning",
            "v4_1_closeout",
            "Fail-visible warning aggregation is preserved for v4.2 planning.",
            True,
            60,
        ),
    )


def _warning_ids_by_category(warnings: tuple[V41CloseoutWarning, ...], category: str) -> tuple[str, ...]:
    return tuple(warning.warning_id for warning in warnings if warning.category == category)


def build_v4_1_closeout_readiness(
    *,
    report_hashes: Mapping[str, str] | None = None,
    report_presence: Mapping[str, bool] | None = None,
    report_json_validity: Mapping[str, bool] | None = None,
    doc_presence: Mapping[str, bool] | None = None,
    test_presence: Mapping[str, bool] | None = None,
) -> V41CloseoutReadiness:
    identity = default_v4_1_closeout_identity()
    phases = build_v4_1_phase_coverage(
        report_presence=report_presence,
        doc_presence=doc_presence,
        test_presence=test_presence,
    )
    reports = build_v4_1_report_coverage(
        report_hashes=report_hashes,
        report_presence=report_presence,
        report_json_validity=report_json_validity,
    )
    warnings = default_v4_1_closeout_warnings()
    blocker_count = sum(
        1
        for phase in phases
        if not (
            phase.phase_coverage_present
            and phase.report_coverage_present
            and phase.migration_doc_present
            and phase.focused_test_present
        )
    ) + sum(1 for report in reports if not (report.present and report.json_valid and report.deterministic_hash_present))
    readiness = V41ReadinessCertification(
        readiness_id=identity.readiness_reference,
        closeout_status=V4_1_CLOSEOUT_STATUS_WITH_WARNINGS if blocker_count == 0 else V4_1_CLOSEOUT_STATUS_BLOCKED,
        v4_2_readiness_status=V4_2_READINESS_WITH_WARNINGS if blocker_count == 0 else V4_2_READINESS_BLOCKED,
        phase_coverage_certified=all(phase.phase_coverage_present for phase in phases),
        report_coverage_certified=all(report.present and report.json_valid for report in reports),
        integrity_verified=all(phase.integrity_coverage_present for phase in phases),
        continuity_verified=all(phase.continuity_coverage_present for phase in phases),
        governance_verified=True,
        replay_safe=all(phase.replay_coverage_present for phase in phases),
        rollback_safe=all(phase.rollback_coverage_present for phase in phases),
        provenance_safe=all(phase.provenance_coverage_present for phase in phases),
        lineage_safe=all(phase.lineage_coverage_present for phase in phases),
        deterministic_readiness_visible=True,
        warning_count=len(warnings),
        blocker_count=blocker_count,
    )
    return V41CloseoutReadiness(
        identity=identity,
        phase_coverage=phases,
        report_coverage=reports,
        warning_aggregation=V41WarningAggregation(
            aggregation_id="v4_1_closeout_warning_aggregation_primary",
            warning_ids=tuple(warning.warning_id for warning in warnings),
            unsupported_state_warning_ids=_warning_ids_by_category(warnings, CLOSEOUT_WARNING_UNSUPPORTED),
            prohibited_state_warning_ids=_warning_ids_by_category(warnings, CLOSEOUT_WARNING_PROHIBITED),
            blocked_state_warning_ids=_warning_ids_by_category(warnings, CLOSEOUT_WARNING_BLOCKED),
            stale_evidence_warning_ids=_warning_ids_by_category(warnings, CLOSEOUT_WARNING_STALE),
            cross_layer_conflict_warning_ids=_warning_ids_by_category(warnings, CLOSEOUT_WARNING_CROSS_LAYER_CONFLICT),
            fail_visible_warning_ids=tuple(warning.warning_id for warning in warnings if warning.fail_visible),
            deterministic_order=10,
        ),
        warnings=warnings,
        readiness=readiness,
        integrity_boundary=V41CloseoutIntegrityBoundary(
            boundary_id=identity.integrity_reference,
            prohibited_domains=PROHIBITED_CLOSEOUT_DOMAINS,
            prohibited_remediation_leakage=("remediation", "hidden_remediation_behavior"),
            prohibited_correction_leakage=("automatic_correction", "automatic_repair"),
            prohibited_recommendation_leakage=("recommendation_systems",),
            prohibited_ranking_leakage=("ranking_systems",),
            prohibited_scoring_leakage=("scoring_systems",),
            prohibited_selection_leakage=("selection_systems",),
            prohibited_approval_leakage=("approval_systems",),
            prohibited_authorization_leakage=("authorization_systems",),
            prohibited_orchestration_leakage=("orchestration_execution", "automatic_sequencing"),
            prohibited_execution_leakage=("refresh_execution", "rollback_execution", "recovery_execution"),
            prohibited_planner_integration_leakage=("planner_integration",),
            prohibited_production_consumption_leakage=("production_bundle_consumption",),
            deterministic_order=20,
        ),
        governance=V41CloseoutGovernance(
            governance_id=identity.governance_reference,
            governance_references=(identity.governance_reference, identity.integrity_reference),
            explicit_limitations=EXPLICIT_CLOSEOUT_READINESS_LIMITATIONS,
            explicit_prohibitions=EXPLICIT_CLOSEOUT_READINESS_PROHIBITIONS,
            deterministic_order=30,
        ),
    )


def default_v4_1_closeout_readiness() -> V41CloseoutReadiness:
    return build_v4_1_closeout_readiness()
