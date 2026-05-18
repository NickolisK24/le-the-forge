"""Aggregation for v4.3 orchestration diagnostics and explainability.

The aggregation layer combines deterministic diagnostics and explainability
evidence from Phases 1 through 6. It is descriptive only: no recommendations,
ranking, scoring, selection, optimization, decisions, execution, activation,
planner integration, production consumption, repair, inference, or mutation are
introduced.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable, Sequence

from .orchestration_capability_diagnostics import (
    aggregate_blocked_capabilities,
    aggregate_conflicting_capabilities,
    aggregate_prohibited_capabilities,
    aggregate_stale_capabilities,
    aggregate_unsupported_capabilities,
)
from .orchestration_capability_hashing import hash_orchestration_capability_visibility
from .orchestration_capability_models import default_orchestration_capability_visibility
from .orchestration_coordination_diagnostics import (
    aggregate_blocked_coordinations,
    aggregate_conflicting_coordinations,
    aggregate_prohibited_coordinations,
    aggregate_stale_coordinations,
    aggregate_unsupported_coordinations,
)
from .orchestration_coordination_hashing import hash_orchestration_coordination_visibility
from .orchestration_coordination_models import default_orchestration_coordination_visibility
from .orchestration_diagnostics_hashing import (
    hash_aggregated_diagnostic_finding,
    hash_aggregated_explainability_summary,
    hash_cross_layer_state_summary,
    hash_governance_layer_diagnostic_summary,
    hash_orchestration_diagnostics_aggregation,
)
from .orchestration_diagnostics_models import (
    CROSS_LAYER_STATE_BLOCKED,
    CROSS_LAYER_STATE_CONFLICTING,
    CROSS_LAYER_STATE_PROHIBITED,
    CROSS_LAYER_STATE_STALE,
    CROSS_LAYER_STATE_TYPES,
    CROSS_LAYER_STATE_UNSUPPORTED,
    EXPLICIT_ORCHESTRATION_DIAGNOSTICS_PROHIBITIONS,
    GOVERNANCE_LAYER_CAPABILITY,
    GOVERNANCE_LAYER_COORDINATION,
    GOVERNANCE_LAYER_IDS,
    GOVERNANCE_LAYER_MANIFEST,
    GOVERNANCE_LAYER_POLICY,
    GOVERNANCE_LAYER_TOPOLOGY,
    GOVERNANCE_LAYER_TRANSITION,
    AggregatedDiagnosticFinding,
    AggregatedExplainabilitySummary,
    CrossLayerStateSummary,
    GovernanceLayerDiagnosticSummary,
    OrchestrationDiagnosticsAggregation,
    default_diagnostics_aggregation_identity,
    default_diagnostics_aggregation_metadata,
)
from .orchestration_diagnostics_serialization import serialize_orchestration_diagnostics_aggregation
from .orchestration_manifest_diagnostics import (
    aggregate_blocked_states,
    aggregate_conflicting_metadata_states,
    aggregate_prohibited_states,
    aggregate_stale_metadata_states,
    aggregate_unsupported_states,
)
from .orchestration_manifest_hashing import hash_orchestration_manifest
from .orchestration_manifest_models import default_orchestration_manifest
from .orchestration_policy_diagnostics import (
    aggregate_blocked_policies,
    aggregate_conflicting_policies,
    aggregate_prohibited_policies,
    aggregate_stale_policies,
    aggregate_unsupported_policies,
)
from .orchestration_policy_hashing import hash_orchestration_policy_visibility
from .orchestration_policy_models import default_orchestration_policy_visibility
from .orchestration_topology_diagnostics import (
    aggregate_blocked_relationships,
    aggregate_conflicting_relationships,
    aggregate_prohibited_relationships,
    aggregate_stale_relationships,
    aggregate_unsupported_relationships,
)
from .orchestration_topology_hashing import hash_orchestration_topology
from .orchestration_topology_models import default_orchestration_topology
from .orchestration_transition_diagnostics import (
    aggregate_blocked_transitions,
    aggregate_conflicting_transitions,
    aggregate_prohibited_transitions,
    aggregate_stale_transitions,
    aggregate_unsupported_transitions,
)
from .orchestration_transition_hashing import hash_orchestration_transition_visibility
from .orchestration_transition_models import default_orchestration_transition_visibility


DIAGNOSTICS_AGGREGATION_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "orchestration_execution_enabled",
    "orchestration_intelligence_execution_enabled",
    "orchestration_recommendation_enabled",
    "orchestration_decision_enabled",
    "orchestration_authorization_enabled",
    "readiness_approval_enabled",
    "orchestration_dispatch_enabled",
    "orchestration_activation_enabled",
    "runtime_coordination_enabled",
    "scheduling_execution_enabled",
    "sequencing_execution_enabled",
    "routing_execution_enabled",
    "traversal_execution_enabled",
    "dependency_resolution_enabled",
    "remediation_enabled",
    "repair_enabled",
    "inference_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "planning_engine_enabled",
    "decision_engine_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "runtime_mutation_enabled",
    "operational_mutation_enabled",
    "hidden_orchestration_pathway_enabled",
    "implicit_operational_authorization_enabled",
    "execution_enabled",
    "recommendation_enabled",
    "decision_enabled",
    "authorization_enabled",
    "mutation_enabled",
)

REQUIRED_EXPLAINABILITY_CATEGORIES: tuple[str, ...] = (
    "orchestration_non_executable",
    "orchestration_activation_unavailable",
    "orchestration_coordination_unavailable",
    "planner_integration_unavailable",
    "production_consumption_unavailable",
    "governance_constraints_exist",
    "operational_orchestration_prohibited",
    "fail_visible_governance_evidence_exists",
    "blocked_prohibited_unsupported_states_surfaced",
    "orchestration_decision_making_prohibited",
    "orchestration_recommendations_prohibited",
)


def _sorted_unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted({value for value in values if value}))


def _source_identity_reference(layer_id: str, source: object) -> str:
    identity = getattr(source, "identity")
    for field_name in (
        "manifest_id",
        "topology_id",
        "capability_set_id",
        "policy_set_id",
        "transition_set_id",
        "coordination_set_id",
    ):
        if hasattr(identity, field_name):
            return str(getattr(identity, field_name))
    return layer_id


def _source_hash_reference(layer_id: str, source: object) -> str:
    if layer_id == GOVERNANCE_LAYER_MANIFEST:
        return hash_orchestration_manifest(source)
    if layer_id == GOVERNANCE_LAYER_TOPOLOGY:
        return hash_orchestration_topology(source)
    if layer_id == GOVERNANCE_LAYER_CAPABILITY:
        return hash_orchestration_capability_visibility(source)
    if layer_id == GOVERNANCE_LAYER_POLICY:
        return hash_orchestration_policy_visibility(source)
    if layer_id == GOVERNANCE_LAYER_TRANSITION:
        return hash_orchestration_transition_visibility(source)
    if layer_id == GOVERNANCE_LAYER_COORDINATION:
        return hash_orchestration_coordination_visibility(source)
    raise ValueError(f"Unsupported governance layer: {layer_id}")


def _affected_reference_ids(source: object) -> tuple[str, ...]:
    data = asdict(source)
    affected: list[str] = []
    for key, value in data.items():
        if key.startswith("affected_") and key.endswith("_ids"):
            affected.extend(str(item) for item in tuple(value or ()))
    for key in ("source_reference", "source_reference_id", "target_reference_id"):
        if data.get(key):
            affected.append(str(data[key]))
    return _sorted_unique(affected)


def _diagnostic_category(source: object) -> str:
    return str(getattr(source, "diagnostic_category", getattr(source, "category", "unknown_diagnostic")))


def _diagnostic_message(source: object) -> str:
    return str(getattr(source, "message", getattr(source, "finding", "")))


def _explanation_category(source: object) -> str:
    return str(getattr(source, "explanation_category", getattr(source, "category", "unknown_explanation")))


def _state_reference_map() -> dict[str, dict[str, tuple[str, ...]]]:
    manifest = default_orchestration_manifest()
    topology = default_orchestration_topology()
    capability = default_orchestration_capability_visibility()
    policy = default_orchestration_policy_visibility()
    transition = default_orchestration_transition_visibility()
    coordination = default_orchestration_coordination_visibility()
    return {
        CROSS_LAYER_STATE_PROHIBITED: {
            GOVERNANCE_LAYER_MANIFEST: aggregate_prohibited_states(manifest),
            GOVERNANCE_LAYER_TOPOLOGY: aggregate_prohibited_relationships(topology),
            GOVERNANCE_LAYER_CAPABILITY: aggregate_prohibited_capabilities(capability),
            GOVERNANCE_LAYER_POLICY: aggregate_prohibited_policies(policy),
            GOVERNANCE_LAYER_TRANSITION: aggregate_prohibited_transitions(transition),
            GOVERNANCE_LAYER_COORDINATION: aggregate_prohibited_coordinations(coordination),
        },
        CROSS_LAYER_STATE_UNSUPPORTED: {
            GOVERNANCE_LAYER_MANIFEST: aggregate_unsupported_states(manifest),
            GOVERNANCE_LAYER_TOPOLOGY: aggregate_unsupported_relationships(topology),
            GOVERNANCE_LAYER_CAPABILITY: aggregate_unsupported_capabilities(capability),
            GOVERNANCE_LAYER_POLICY: aggregate_unsupported_policies(policy),
            GOVERNANCE_LAYER_TRANSITION: aggregate_unsupported_transitions(transition),
            GOVERNANCE_LAYER_COORDINATION: aggregate_unsupported_coordinations(coordination),
        },
        CROSS_LAYER_STATE_BLOCKED: {
            GOVERNANCE_LAYER_MANIFEST: aggregate_blocked_states(manifest),
            GOVERNANCE_LAYER_TOPOLOGY: aggregate_blocked_relationships(topology),
            GOVERNANCE_LAYER_CAPABILITY: aggregate_blocked_capabilities(capability),
            GOVERNANCE_LAYER_POLICY: aggregate_blocked_policies(policy),
            GOVERNANCE_LAYER_TRANSITION: aggregate_blocked_transitions(transition),
            GOVERNANCE_LAYER_COORDINATION: aggregate_blocked_coordinations(coordination),
        },
        CROSS_LAYER_STATE_STALE: {
            GOVERNANCE_LAYER_MANIFEST: aggregate_stale_metadata_states(manifest),
            GOVERNANCE_LAYER_TOPOLOGY: aggregate_stale_relationships(topology),
            GOVERNANCE_LAYER_CAPABILITY: aggregate_stale_capabilities(capability),
            GOVERNANCE_LAYER_POLICY: aggregate_stale_policies(policy),
            GOVERNANCE_LAYER_TRANSITION: aggregate_stale_transitions(transition),
            GOVERNANCE_LAYER_COORDINATION: aggregate_stale_coordinations(coordination),
        },
        CROSS_LAYER_STATE_CONFLICTING: {
            GOVERNANCE_LAYER_MANIFEST: aggregate_conflicting_metadata_states(manifest),
            GOVERNANCE_LAYER_TOPOLOGY: aggregate_conflicting_relationships(topology),
            GOVERNANCE_LAYER_CAPABILITY: aggregate_conflicting_capabilities(capability),
            GOVERNANCE_LAYER_POLICY: aggregate_conflicting_policies(policy),
            GOVERNANCE_LAYER_TRANSITION: aggregate_conflicting_transitions(transition),
            GOVERNANCE_LAYER_COORDINATION: aggregate_conflicting_coordinations(coordination),
        },
    }


def _default_sources() -> dict[str, object]:
    return {
        GOVERNANCE_LAYER_MANIFEST: default_orchestration_manifest(),
        GOVERNANCE_LAYER_TOPOLOGY: default_orchestration_topology(),
        GOVERNANCE_LAYER_CAPABILITY: default_orchestration_capability_visibility(),
        GOVERNANCE_LAYER_POLICY: default_orchestration_policy_visibility(),
        GOVERNANCE_LAYER_TRANSITION: default_orchestration_transition_visibility(),
        GOVERNANCE_LAYER_COORDINATION: default_orchestration_coordination_visibility(),
    }


def default_governance_layer_summaries(
    sources: dict[str, object] | None = None,
) -> tuple[GovernanceLayerDiagnosticSummary, ...]:
    source_map = sources or _default_sources()
    state_map = _state_reference_map()
    summaries: list[GovernanceLayerDiagnosticSummary] = []
    for index, layer_id in enumerate(GOVERNANCE_LAYER_IDS, start=1):
        source = source_map[layer_id]
        summaries.append(
            GovernanceLayerDiagnosticSummary(
                layer_id=layer_id,
                layer_name=f"v4_3_orchestration_{layer_id}_visibility",
                source_reference_id=_source_identity_reference(layer_id, source),
                source_hash_reference=_source_hash_reference(layer_id, source),
                diagnostic_count=len(getattr(source, "diagnostics")),
                explainability_count=len(getattr(source, "explainability_summaries")),
                prohibited_state_count=len(state_map[CROSS_LAYER_STATE_PROHIBITED][layer_id]),
                unsupported_state_count=len(state_map[CROSS_LAYER_STATE_UNSUPPORTED][layer_id]),
                blocked_state_count=len(state_map[CROSS_LAYER_STATE_BLOCKED][layer_id]),
                stale_state_count=len(state_map[CROSS_LAYER_STATE_STALE][layer_id]),
                conflicting_state_count=len(state_map[CROSS_LAYER_STATE_CONFLICTING][layer_id]),
                continuity_diagnostic_count=1,
                provenance_diagnostic_count=1,
                lineage_diagnostic_count=1,
                deterministic_order=index,
            )
        )
    return tuple(summaries)


def default_aggregated_diagnostics(
    sources: dict[str, object] | None = None,
) -> tuple[AggregatedDiagnosticFinding, ...]:
    source_map = sources or _default_sources()
    diagnostics: list[AggregatedDiagnosticFinding] = []
    for layer_index, layer_id in enumerate(GOVERNANCE_LAYER_IDS, start=1):
        for source_diagnostic in getattr(source_map[layer_id], "diagnostics"):
            source_id = str(getattr(source_diagnostic, "diagnostic_id"))
            order = layer_index * 1000 + int(getattr(source_diagnostic, "deterministic_order"))
            diagnostics.append(
                AggregatedDiagnosticFinding(
                    aggregated_diagnostic_id=f"v4_3_aggregated_{layer_id}_{source_id}",
                    source_layer_id=layer_id,
                    source_diagnostic_id=source_id,
                    diagnostic_category=_diagnostic_category(source_diagnostic),
                    severity=str(getattr(source_diagnostic, "severity")),
                    message=_diagnostic_message(source_diagnostic),
                    affected_reference_ids=_affected_reference_ids(source_diagnostic),
                    deterministic_order=order,
                )
            )

    state_map = _state_reference_map()
    base_order = 7000
    for offset, state_type in enumerate(CROSS_LAYER_STATE_TYPES, start=1):
        affected = _sorted_unique(
            reference
            for layer_references in state_map[state_type].values()
            for reference in layer_references
        )
        diagnostics.append(
            AggregatedDiagnosticFinding(
                aggregated_diagnostic_id=f"v4_3_cross_layer_{state_type}_state_diagnostic",
                source_layer_id="cross_layer",
                source_diagnostic_id=f"v4_3_cross_layer_{state_type}_state_diagnostic",
                diagnostic_category=f"cross_layer_{state_type}_state_visibility",
                severity="prohibited" if state_type == CROSS_LAYER_STATE_PROHIBITED else "blocker",
                message=(
                    f"Cross-layer {state_type} orchestration governance evidence is "
                    "aggregated without recommendations, repair, or decisions."
                ),
                affected_reference_ids=affected,
                deterministic_order=base_order + offset,
            )
        )

    diagnostics.extend(
        (
            AggregatedDiagnosticFinding(
                aggregated_diagnostic_id="v4_3_cross_layer_continuity_diagnostic",
                source_layer_id="cross_layer",
                source_diagnostic_id="v4_3_cross_layer_continuity_diagnostic",
                diagnostic_category="continuity_diagnostics_aggregation",
                severity="info",
                message="Continuity diagnostics are aggregated as replay-safe and rollback-safe evidence only.",
                affected_reference_ids=GOVERNANCE_LAYER_IDS,
                deterministic_order=7010,
            ),
            AggregatedDiagnosticFinding(
                aggregated_diagnostic_id="v4_3_cross_layer_provenance_diagnostic",
                source_layer_id="cross_layer",
                source_diagnostic_id="v4_3_cross_layer_provenance_diagnostic",
                diagnostic_category="provenance_diagnostics_aggregation",
                severity="info",
                message="Provenance diagnostics remain visible across layers without production consumption.",
                affected_reference_ids=GOVERNANCE_LAYER_IDS,
                deterministic_order=7011,
            ),
            AggregatedDiagnosticFinding(
                aggregated_diagnostic_id="v4_3_cross_layer_lineage_diagnostic",
                source_layer_id="cross_layer",
                source_diagnostic_id="v4_3_cross_layer_lineage_diagnostic",
                diagnostic_category="lineage_diagnostics_aggregation",
                severity="info",
                message="Lineage diagnostics remain visible across layers without planner integration.",
                affected_reference_ids=GOVERNANCE_LAYER_IDS,
                deterministic_order=7012,
            ),
            AggregatedDiagnosticFinding(
                aggregated_diagnostic_id="v4_3_cross_layer_non_execution_diagnostic",
                source_layer_id="cross_layer",
                source_diagnostic_id="v4_3_cross_layer_non_execution_diagnostic",
                diagnostic_category="non_execution_boundary_visibility",
                severity="prohibited",
                message="Diagnostics aggregation certifies enabled coordination, transition, policy, capability, decision, and recommendation counts remain 0.",
                affected_reference_ids=GOVERNANCE_LAYER_IDS,
                deterministic_order=7013,
            ),
            AggregatedDiagnosticFinding(
                aggregated_diagnostic_id="v4_3_cross_layer_non_decision_diagnostic",
                source_layer_id="cross_layer",
                source_diagnostic_id="v4_3_cross_layer_non_decision_diagnostic",
                diagnostic_category="non_decision_boundary_visibility",
                severity="prohibited",
                message="Diagnostics aggregation cannot recommend, rank, score, select, optimize, authorize, or decide orchestration actions.",
                affected_reference_ids=GOVERNANCE_LAYER_IDS,
                deterministic_order=7014,
            ),
        )
    )
    return tuple(diagnostics)


def default_aggregated_explainability(
    sources: dict[str, object] | None = None,
) -> tuple[AggregatedExplainabilitySummary, ...]:
    source_map = sources or _default_sources()
    summaries: list[AggregatedExplainabilitySummary] = []
    for layer_index, layer_id in enumerate(GOVERNANCE_LAYER_IDS, start=1):
        for source_summary in getattr(source_map[layer_id], "explainability_summaries"):
            source_id = str(getattr(source_summary, "explanation_id"))
            order = layer_index * 1000 + int(getattr(source_summary, "deterministic_order"))
            summaries.append(
                AggregatedExplainabilitySummary(
                    aggregated_explanation_id=f"v4_3_aggregated_{layer_id}_{source_id}",
                    source_layer_id=layer_id,
                    source_explanation_id=source_id,
                    explanation_category=_explanation_category(source_summary),
                    summary=str(getattr(source_summary, "summary")),
                    affected_reference_ids=_affected_reference_ids(source_summary),
                    deterministic_order=order,
                )
            )

    cross_layer_summaries = (
        (
            "orchestration_non_executable",
            "Orchestration remains non-executable because Phase 7 aggregates governance diagnostics only.",
        ),
        (
            "orchestration_activation_unavailable",
            "Orchestration activation remains unavailable because aggregated evidence cannot activate capabilities or transitions.",
        ),
        (
            "orchestration_coordination_unavailable",
            "Runtime coordination remains unavailable because coordination evidence is descriptive and non-coordinating.",
        ),
        (
            "planner_integration_unavailable",
            "Planner integration remains unavailable because diagnostics aggregation cannot steer operational planning.",
        ),
        (
            "production_consumption_unavailable",
            "Production consumption remains unavailable because aggregation output is replay-safe and rollback-safe evidence.",
        ),
        (
            "governance_constraints_exist",
            "Governance constraints exist to keep cross-layer orchestration evidence auditable without operational behavior.",
        ),
        (
            "operational_orchestration_prohibited",
            "Operational orchestration remains prohibited because no execution, dispatch, activation, routing, traversal, scheduling, sequencing, or dependency resolution exists.",
        ),
        (
            "fail_visible_governance_evidence_exists",
            "Fail-visible governance evidence exists so blocked, prohibited, unsupported, stale, and conflicting states are surfaced instead of inferred away.",
        ),
        (
            "blocked_prohibited_unsupported_states_surfaced",
            "Blocked, prohibited, and unsupported states are surfaced deterministically across all orchestration governance layers.",
        ),
        (
            "orchestration_decision_making_prohibited",
            "Orchestration decision-making remains prohibited because aggregation cannot recommend or authorize actions.",
        ),
        (
            "orchestration_recommendations_prohibited",
            "Orchestration recommendations remain prohibited because diagnostics aggregation does not rank, score, select, or optimize outcomes.",
        ),
    )
    for offset, (category, summary) in enumerate(cross_layer_summaries, start=1):
        summaries.append(
            AggregatedExplainabilitySummary(
                aggregated_explanation_id=f"v4_3_cross_layer_{category}_explanation",
                source_layer_id="cross_layer",
                source_explanation_id=f"v4_3_cross_layer_{category}_explanation",
                explanation_category=category,
                summary=summary,
                affected_reference_ids=GOVERNANCE_LAYER_IDS,
                deterministic_order=7000 + offset,
            )
        )
    return tuple(summaries)


def default_cross_layer_state_summaries(
    diagnostics: Sequence[AggregatedDiagnosticFinding],
    explainability: Sequence[AggregatedExplainabilitySummary],
) -> tuple[CrossLayerStateSummary, ...]:
    state_map = _state_reference_map()
    summaries: list[CrossLayerStateSummary] = []
    for index, state_type in enumerate(CROSS_LAYER_STATE_TYPES, start=1):
        layer_refs = state_map[state_type]
        source_layer_ids = tuple(layer_id for layer_id in GOVERNANCE_LAYER_IDS if layer_refs[layer_id])
        affected_reference_ids = _sorted_unique(
            reference for references in layer_refs.values() for reference in references
        )
        diagnostic_ids = _sorted_unique(
            diagnostic.aggregated_diagnostic_id
            for diagnostic in diagnostics
            if state_type in diagnostic.diagnostic_category
        )
        explanation_ids = _sorted_unique(
            summary.aggregated_explanation_id
            for summary in explainability
            if state_type in summary.explanation_category
            or (state_type in (CROSS_LAYER_STATE_PROHIBITED, CROSS_LAYER_STATE_UNSUPPORTED, CROSS_LAYER_STATE_BLOCKED)
                and summary.explanation_category == "blocked_prohibited_unsupported_states_surfaced")
        )
        summaries.append(
            CrossLayerStateSummary(
                state_summary_id=f"v4_3_cross_layer_{state_type}_state_summary",
                state_type=state_type,
                source_layer_ids=source_layer_ids,
                affected_reference_ids=affected_reference_ids,
                diagnostic_reference_ids=diagnostic_ids,
                explainability_reference_ids=explanation_ids,
                state_count=len(affected_reference_ids),
                deterministic_order=index,
            )
        )
    return tuple(summaries)


def default_orchestration_diagnostics_aggregation() -> OrchestrationDiagnosticsAggregation:
    sources = _default_sources()
    identity = default_diagnostics_aggregation_identity()
    diagnostics = default_aggregated_diagnostics(sources)
    explainability = default_aggregated_explainability(sources)
    return OrchestrationDiagnosticsAggregation(
        identity=identity,
        metadata=default_diagnostics_aggregation_metadata(identity),
        governance_layer_summaries=default_governance_layer_summaries(sources),
        diagnostics=diagnostics,
        explainability_summaries=explainability,
        cross_layer_state_summaries=default_cross_layer_state_summaries(diagnostics, explainability),
    )


def diagnostics_aggregation_flags(aggregation: OrchestrationDiagnosticsAggregation) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        aggregation,
        aggregation.identity,
        aggregation.metadata,
        *aggregation.governance_layer_summaries,
        *aggregation.diagnostics,
        *aggregation.explainability_summaries,
        *aggregation.cross_layer_state_summaries,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in DIAGNOSTICS_AGGREGATION_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_diagnostics_aggregation_flags(
    aggregation: OrchestrationDiagnosticsAggregation,
) -> dict[str, bool]:
    return {key: value for key, value in diagnostics_aggregation_flags(aggregation).items() if value}


def diagnostics_aggregation_identity_key(aggregation: OrchestrationDiagnosticsAggregation) -> str:
    identity = aggregation.identity
    return "|".join(
        (
            identity.schema_version,
            identity.aggregation_id,
            identity.aggregation_version,
            identity.source_manifest_reference,
            identity.source_manifest_hash_reference,
            identity.source_topology_reference,
            identity.source_topology_hash_reference,
            identity.source_capability_reference,
            identity.source_capability_hash_reference,
            identity.source_policy_reference,
            identity.source_policy_hash_reference,
            identity.source_transition_reference,
            identity.source_transition_hash_reference,
            identity.source_coordination_reference,
            identity.source_coordination_hash_reference,
            identity.governance_reference,
        )
    )


def diagnostics_aggregations_equal(
    left: OrchestrationDiagnosticsAggregation,
    right: OrchestrationDiagnosticsAggregation,
) -> bool:
    return serialize_orchestration_diagnostics_aggregation(
        left
    ) == serialize_orchestration_diagnostics_aggregation(right)


def enabled_coordination_execution_count(aggregation: OrchestrationDiagnosticsAggregation) -> int:
    return int(
        aggregation.enabled_coordination_execution_count
        or aggregation.runtime_coordination_enabled
        or aggregation.orchestration_dispatch_enabled
    )


def enabled_transition_execution_count(aggregation: OrchestrationDiagnosticsAggregation) -> int:
    return int(
        aggregation.enabled_transition_execution_count
        or aggregation.orchestration_activation_enabled
        or aggregation.orchestration_execution_enabled
    )


def enabled_policy_enforcement_count(aggregation: OrchestrationDiagnosticsAggregation) -> int:
    return int(
        aggregation.enabled_policy_enforcement_count
        or aggregation.orchestration_authorization_enabled
        or aggregation.readiness_approval_enabled
    )


def enabled_operational_capability_count(aggregation: OrchestrationDiagnosticsAggregation) -> int:
    return int(
        aggregation.enabled_operational_capability_count
        or aggregation.orchestration_execution_enabled
        or aggregation.orchestration_activation_enabled
        or aggregation.routing_execution_enabled
        or aggregation.traversal_execution_enabled
        or aggregation.scheduling_execution_enabled
        or aggregation.sequencing_execution_enabled
        or aggregation.dependency_resolution_enabled
        or aggregation.planner_integration_enabled
        or aggregation.production_consumption_enabled
        or aggregation.runtime_mutation_enabled
        or aggregation.operational_mutation_enabled
    )


def enabled_orchestration_decision_count(aggregation: OrchestrationDiagnosticsAggregation) -> int:
    return int(
        aggregation.enabled_orchestration_decision_count
        or aggregation.orchestration_decision_enabled
        or aggregation.decision_engine_enabled
        or any(diagnostic.decision_enabled for diagnostic in aggregation.diagnostics)
        or any(summary.decision_enabled for summary in aggregation.explainability_summaries)
    )


def enabled_orchestration_recommendation_count(aggregation: OrchestrationDiagnosticsAggregation) -> int:
    return int(
        aggregation.enabled_orchestration_recommendation_count
        or aggregation.orchestration_recommendation_enabled
        or aggregation.ranking_enabled
        or aggregation.scoring_enabled
        or aggregation.selection_enabled
        or aggregation.optimization_enabled
        or any(diagnostic.recommendation_enabled for diagnostic in aggregation.diagnostics)
        or any(summary.recommendation_enabled for summary in aggregation.explainability_summaries)
    )


def validate_diagnostics_aggregation_identity(
    aggregation: OrchestrationDiagnosticsAggregation,
) -> dict[str, object]:
    fields = asdict(aggregation.identity)
    required = (
        "aggregation_id",
        "aggregation_version",
        "aggregation_classification",
        "source_manifest_reference",
        "source_manifest_hash_reference",
        "source_topology_reference",
        "source_topology_hash_reference",
        "source_capability_reference",
        "source_capability_hash_reference",
        "source_policy_reference",
        "source_policy_hash_reference",
        "source_transition_reference",
        "source_transition_hash_reference",
        "source_coordination_reference",
        "source_coordination_hash_reference",
        "schema_version",
        "governance_reference",
        "governance_layer_reference",
        "cross_layer_diagnostics_reference",
        "cross_layer_explainability_reference",
        "lineage_reference",
        "provenance_reference",
        "continuity_reference",
        "non_execution_reference",
        "non_decision_reference",
    )
    missing_fields = tuple(sorted(field for field in required if not fields.get(field)))
    defaults = _default_sources()
    hash_mismatches = tuple(
        sorted(
            layer_id
            for layer_id in GOVERNANCE_LAYER_IDS
            if getattr(aggregation.identity, f"source_{layer_id}_hash_reference")
            != _source_hash_reference(layer_id, defaults[layer_id])
        )
    )
    return {
        "valid": len(missing_fields) == 0 and len(hash_mismatches) == 0,
        "missing_identity_fields": missing_fields,
        "source_hash_mismatches": hash_mismatches,
        "identity_key": diagnostics_aggregation_identity_key(aggregation),
        "aggregation_id": aggregation.identity.aggregation_id,
        "schema_version": aggregation.identity.schema_version,
        "descriptive_only": aggregation.identity.descriptive_only,
        "non_executable": aggregation.identity.non_executable,
        "non_decisioning": aggregation.identity.non_decisioning,
    }


def validate_diagnostics_aggregation_layers(
    aggregation: OrchestrationDiagnosticsAggregation,
) -> dict[str, object]:
    layer_ids = tuple(summary.layer_id for summary in aggregation.governance_layer_summaries)
    duplicate_layer_ids = tuple(
        sorted(layer_id for layer_id in set(layer_ids) if layer_ids.count(layer_id) > 1)
    )
    missing_layer_ids = tuple(sorted(layer_id for layer_id in GOVERNANCE_LAYER_IDS if layer_id not in layer_ids))
    non_descriptive_layers = tuple(
        sorted(summary.layer_id for summary in aggregation.governance_layer_summaries if not summary.descriptive_only)
    )
    enabled_layers = tuple(
        sorted(
            summary.layer_id
            for summary in aggregation.governance_layer_summaries
            if summary.orchestration_execution_enabled
            or summary.orchestration_decision_enabled
            or summary.orchestration_recommendation_enabled
            or summary.planner_integration_enabled
            or summary.production_consumption_enabled
        )
    )
    return {
        "valid": (
            len(duplicate_layer_ids) == 0
            and len(missing_layer_ids) == 0
            and len(non_descriptive_layers) == 0
            and len(enabled_layers) == 0
        ),
        "layer_ids": tuple(sorted(layer_ids)),
        "duplicate_layer_ids": duplicate_layer_ids,
        "missing_layer_ids": missing_layer_ids,
        "non_descriptive_layer_ids": non_descriptive_layers,
        "enabled_layer_ids": enabled_layers,
        "governance_layer_summary_count": len(aggregation.governance_layer_summaries),
        "continuity_diagnostics_visible": all(
            summary.continuity_diagnostic_count > 0 for summary in aggregation.governance_layer_summaries
        ),
        "provenance_diagnostics_visible": all(
            summary.provenance_diagnostic_count > 0 for summary in aggregation.governance_layer_summaries
        ),
        "lineage_diagnostics_visible": all(
            summary.lineage_diagnostic_count > 0 for summary in aggregation.governance_layer_summaries
        ),
    }


def validate_diagnostics_aggregation_state_visibility(
    aggregation: OrchestrationDiagnosticsAggregation,
) -> dict[str, object]:
    summaries_by_type = {summary.state_type: summary for summary in aggregation.cross_layer_state_summaries}
    missing_state_types = tuple(
        sorted(state_type for state_type in CROSS_LAYER_STATE_TYPES if state_type not in summaries_by_type)
    )
    empty_state_types = tuple(
        sorted(
            state_type
            for state_type, summary in summaries_by_type.items()
            if summary.state_count == 0 or not summary.affected_reference_ids
        )
    )
    enabled_state_summaries = tuple(
        sorted(
            summary.state_summary_id
            for summary in aggregation.cross_layer_state_summaries
            if summary.orchestration_execution_enabled
            or summary.orchestration_decision_enabled
            or summary.orchestration_recommendation_enabled
            or summary.repair_enabled
            or summary.inference_enabled
        )
    )
    return {
        "valid": len(missing_state_types) == 0 and len(empty_state_types) == 0 and len(enabled_state_summaries) == 0,
        "missing_state_types": missing_state_types,
        "empty_state_types": empty_state_types,
        "enabled_state_summary_ids": enabled_state_summaries,
        "prohibited_state_count": summaries_by_type[CROSS_LAYER_STATE_PROHIBITED].state_count,
        "unsupported_state_count": summaries_by_type[CROSS_LAYER_STATE_UNSUPPORTED].state_count,
        "blocked_state_count": summaries_by_type[CROSS_LAYER_STATE_BLOCKED].state_count,
        "stale_state_count": summaries_by_type[CROSS_LAYER_STATE_STALE].state_count,
        "conflicting_state_count": summaries_by_type[CROSS_LAYER_STATE_CONFLICTING].state_count,
        "prohibited_states_visible": summaries_by_type[CROSS_LAYER_STATE_PROHIBITED].state_count > 0,
        "unsupported_states_visible": summaries_by_type[CROSS_LAYER_STATE_UNSUPPORTED].state_count > 0,
        "blocked_states_visible": summaries_by_type[CROSS_LAYER_STATE_BLOCKED].state_count > 0,
        "stale_states_visible": summaries_by_type[CROSS_LAYER_STATE_STALE].state_count > 0,
        "conflicting_states_visible": summaries_by_type[CROSS_LAYER_STATE_CONFLICTING].state_count > 0,
    }


def validate_diagnostics_aggregation_explainability(
    aggregation: OrchestrationDiagnosticsAggregation,
) -> dict[str, object]:
    categories = tuple(
        sorted(summary.explanation_category for summary in aggregation.explainability_summaries)
    )
    missing_categories = tuple(
        sorted(category for category in REQUIRED_EXPLAINABILITY_CATEGORIES if category not in categories)
    )
    non_descriptive = tuple(
        sorted(
            summary.aggregated_explanation_id
            for summary in aggregation.explainability_summaries
            if not summary.descriptive_only
        )
    )
    enabled_explanations = tuple(
        sorted(
            summary.aggregated_explanation_id
            for summary in aggregation.explainability_summaries
            if summary.recommendation_enabled
            or summary.decision_enabled
            or summary.ranking_enabled
            or summary.scoring_enabled
            or summary.selection_enabled
            or summary.optimization_enabled
            or summary.orchestration_execution_enabled
            or summary.orchestration_activation_enabled
            or summary.planner_integration_enabled
            or summary.production_consumption_enabled
        )
    )
    return {
        "valid": len(missing_categories) == 0 and len(non_descriptive) == 0 and len(enabled_explanations) == 0,
        "explainability_categories": categories,
        "missing_explainability_categories": missing_categories,
        "non_descriptive_explanations": non_descriptive,
        "enabled_explanations": enabled_explanations,
        "deterministic": all(summary.deterministic for summary in aggregation.explainability_summaries),
        "replay_safe": all(summary.replay_safe for summary in aggregation.explainability_summaries),
        "rollback_safe": all(summary.rollback_safe for summary in aggregation.explainability_summaries),
    }


def validate_diagnostics_aggregation_non_execution_and_non_decision(
    aggregation: OrchestrationDiagnosticsAggregation,
) -> dict[str, object]:
    enabled_flags = enabled_diagnostics_aggregation_flags(aggregation)
    coordination_count = enabled_coordination_execution_count(aggregation)
    transition_count = enabled_transition_execution_count(aggregation)
    policy_count = enabled_policy_enforcement_count(aggregation)
    operational_count = enabled_operational_capability_count(aggregation)
    decision_count = enabled_orchestration_decision_count(aggregation)
    recommendation_count = enabled_orchestration_recommendation_count(aggregation)
    return {
        "valid": (
            len(enabled_flags) == 0
            and coordination_count == 0
            and transition_count == 0
            and policy_count == 0
            and operational_count == 0
            and decision_count == 0
            and recommendation_count == 0
            and aggregation.non_executable
            and aggregation.non_decisioning
            and aggregation.descriptive_only
        ),
        "enabled_diagnostics_aggregation_flags": enabled_flags,
        "enabled_coordination_execution_count": coordination_count,
        "enabled_transition_execution_count": transition_count,
        "enabled_policy_enforcement_count": policy_count,
        "enabled_operational_capability_count": operational_count,
        "enabled_orchestration_decision_count": decision_count,
        "enabled_orchestration_recommendation_count": recommendation_count,
        "non_executable": aggregation.non_executable,
        "non_decisioning": aggregation.non_decisioning,
        "descriptive_only": aggregation.descriptive_only,
        "orchestration_execution_disabled": not aggregation.orchestration_execution_enabled,
        "orchestration_intelligence_execution_disabled": (
            not aggregation.orchestration_intelligence_execution_enabled
        ),
        "orchestration_recommendation_disabled": not aggregation.orchestration_recommendation_enabled,
        "orchestration_decision_disabled": not aggregation.orchestration_decision_enabled,
        "orchestration_authorization_disabled": not aggregation.orchestration_authorization_enabled,
        "readiness_approval_disabled": not aggregation.readiness_approval_enabled,
        "orchestration_dispatch_disabled": not aggregation.orchestration_dispatch_enabled,
        "orchestration_activation_disabled": not aggregation.orchestration_activation_enabled,
        "runtime_coordination_disabled": not aggregation.runtime_coordination_enabled,
        "scheduling_execution_disabled": not aggregation.scheduling_execution_enabled,
        "sequencing_execution_disabled": not aggregation.sequencing_execution_enabled,
        "routing_execution_disabled": not aggregation.routing_execution_enabled,
        "traversal_execution_disabled": not aggregation.traversal_execution_enabled,
        "dependency_resolution_disabled": not aggregation.dependency_resolution_enabled,
        "remediation_disabled": not aggregation.remediation_enabled,
        "repair_disabled": not aggregation.repair_enabled,
        "inference_disabled": not aggregation.inference_enabled,
        "ranking_disabled": not aggregation.ranking_enabled,
        "scoring_disabled": not aggregation.scoring_enabled,
        "selection_disabled": not aggregation.selection_enabled,
        "optimization_disabled": not aggregation.optimization_enabled,
        "planning_engine_absent": not aggregation.planning_engine_enabled,
        "decision_engine_absent": not aggregation.decision_engine_enabled,
        "planner_integration_disabled": not aggregation.planner_integration_enabled,
        "production_consumption_disabled": not aggregation.production_consumption_enabled,
        "runtime_mutation_disabled": not aggregation.runtime_mutation_enabled,
        "operational_mutation_disabled": not aggregation.operational_mutation_enabled,
        "hidden_orchestration_pathway_absent": not aggregation.hidden_orchestration_pathway_enabled,
        "implicit_operational_authorization_absent": (
            not aggregation.implicit_operational_authorization_enabled
        ),
    }


def build_orchestration_diagnostics_aggregation_diagnostics(
    aggregation: OrchestrationDiagnosticsAggregation | None = None,
) -> dict[str, Any]:
    source = aggregation or default_orchestration_diagnostics_aggregation()
    identity = validate_diagnostics_aggregation_identity(source)
    layers = validate_diagnostics_aggregation_layers(source)
    state_visibility = validate_diagnostics_aggregation_state_visibility(source)
    explainability = validate_diagnostics_aggregation_explainability(source)
    non_execution = validate_diagnostics_aggregation_non_execution_and_non_decision(source)
    return {
        "diagnostics_aggregation_hash": hash_orchestration_diagnostics_aggregation(source),
        "governance_layer_hashes": [
            hash_governance_layer_diagnostic_summary(summary)
            for summary in source.governance_layer_summaries
        ],
        "diagnostic_hashes": [
            hash_aggregated_diagnostic_finding(diagnostic) for diagnostic in source.diagnostics
        ],
        "explainability_hashes": [
            hash_aggregated_explainability_summary(summary)
            for summary in source.explainability_summaries
        ],
        "cross_layer_state_hashes": [
            hash_cross_layer_state_summary(summary) for summary in source.cross_layer_state_summaries
        ],
        "identity_validation": identity,
        "governance_layer_validation": layers,
        "state_visibility_validation": state_visibility,
        "explainability_validation": explainability,
        "non_execution_and_non_decision_validation": non_execution,
        "aggregated_diagnostics_count": len(source.diagnostics),
        "aggregated_explainability_count": len(source.explainability_summaries),
        "governance_layer_summary_count": len(source.governance_layer_summaries),
        "cross_layer_blocked_state_count": state_visibility["blocked_state_count"],
        "cross_layer_prohibited_state_count": state_visibility["prohibited_state_count"],
        "cross_layer_unsupported_state_count": state_visibility["unsupported_state_count"],
        "cross_layer_stale_state_count": state_visibility["stale_state_count"],
        "cross_layer_conflicting_state_count": state_visibility["conflicting_state_count"],
        "diagnostic_categories": tuple(sorted(diagnostic.diagnostic_category for diagnostic in source.diagnostics)),
        "explainability_categories": tuple(
            sorted(summary.explanation_category for summary in source.explainability_summaries)
        ),
        "enabled_coordination_execution_count": non_execution["enabled_coordination_execution_count"],
        "enabled_transition_execution_count": non_execution["enabled_transition_execution_count"],
        "enabled_policy_enforcement_count": non_execution["enabled_policy_enforcement_count"],
        "enabled_operational_capability_count": non_execution["enabled_operational_capability_count"],
        "enabled_orchestration_decision_count": non_execution["enabled_orchestration_decision_count"],
        "enabled_orchestration_recommendation_count": non_execution[
            "enabled_orchestration_recommendation_count"
        ],
        "diagnostics_are_descriptive_only": all(diagnostic.descriptive_only for diagnostic in source.diagnostics),
        "explainability_is_descriptive_only": all(
            summary.descriptive_only for summary in source.explainability_summaries
        ),
        "explicit_prohibitions": EXPLICIT_ORCHESTRATION_DIAGNOSTICS_PROHIBITIONS,
    }
