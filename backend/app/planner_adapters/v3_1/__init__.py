"""V3.1 trusted production shadow-consumption safety scaffolds."""

from .dual_run_comparison import (
    DRIFT_CLASSIFICATIONS,
    V31DualRunComparison,
    build_sample_dual_run_inputs,
)
from .baseline_fixture_workflows import (
    FIXTURE_WORKFLOW_STATES,
    V31BaselineFixtureWorkflows,
    build_sample_baseline_fixture_workflow_inputs,
)
from .persisted_fixture_sets import (
    FIXTURE_SET_LIFECYCLE_STATES,
    V31PersistedFixtureSets,
    build_sample_persisted_fixture_set_inputs,
)
from .planner_snapshot_baselines import (
    BASELINE_READINESS_CLASSIFICATIONS,
    V31PlannerSnapshotBaselines,
    build_sample_planner_snapshot_baseline_inputs,
)
from .baseline_semantic_expectations import (
    BASELINE_SEMANTIC_EXPECTATION_STATUSES,
    build_baseline_semantic_expectations,
)
from .baseline_trace_expectation_backfill import (
    BASELINE_TRACE_EXPECTATION_BACKFILL_STATUSES,
    build_baseline_trace_expectation_backfill,
)
from .trace_backfilled_semantic_parity import (
    TRACE_BACKFILLED_SEMANTIC_PARITY_STATUSES,
    build_trace_backfilled_semantic_parity,
)
from .controlled_consumption_promotion_readiness import (
    CONTROLLED_CONSUMPTION_PROMOTION_READINESS_STATUSES,
    build_controlled_consumption_promotion_readiness,
)
from .review_policy_evaluation import (
    REVIEW_POLICY_OUTCOMES,
    V31ReviewPolicyEvaluation,
    build_sample_review_policy_inputs,
)
from .fixture_set_readiness_gate import (
    FIXTURE_SET_READINESS_CLASSIFICATIONS,
    build_fixture_set_readiness_gate,
)
from .fixture_source_admission_policy import (
    FIXTURE_SOURCE_ADMISSION_STATUSES,
    evaluate_fixture_source_admission_policy,
)
from .approval_manifest_candidates import (
    APPROVAL_MANIFEST_CANDIDATE_STATUSES,
    build_approval_manifest_candidates,
)
from .approval_blocker_diagnosis import (
    APPROVAL_BLOCKER_CLASSIFICATIONS,
    build_approval_blocker_diagnosis,
)
from .admission_aware_policy_evaluation import (
    ADMISSION_AWARE_POLICY_STATUSES,
    build_admission_aware_policy_evaluation,
)
from .admission_aware_readiness_gate import (
    ADMISSION_AWARE_READINESS_STATUSES,
    build_admission_aware_readiness_gate,
)
from .admission_aware_manifest_candidates import (
    ADMISSION_AWARE_MANIFEST_CANDIDATE_STATUSES,
    build_admission_aware_manifest_candidates,
)
from .admission_aware_manifest_serialization import (
    ADMISSION_AWARE_SERIALIZED_MANIFEST_STATUSES,
    serialize_admission_aware_manifest_candidates,
)
from .manifest_consumption_eligibility import (
    MANIFEST_CONSUMPTION_ELIGIBILITY_STATUSES,
    evaluate_manifest_consumption_eligibility,
)
from .controlled_test_consumption import (
    CONTROLLED_TEST_CONSUMPTION_STATUSES,
    build_controlled_test_consumption,
)
from .controlled_consumption_output_validation import (
    CONTROLLED_CONSUMPTION_OUTPUT_VALIDATION_STATUSES,
    validate_controlled_consumption_output,
)
from .controlled_consumption_parity_snapshot import (
    CONTROLLED_CONSUMPTION_PARITY_STATUSES,
    build_controlled_consumption_parity_snapshot,
)
from .controlled_consumption_semantic_parity import (
    CONTROLLED_CONSUMPTION_SEMANTIC_PARITY_STATUSES,
    build_controlled_consumption_semantic_parity,
)
from .approval_manifest_diff_audit import (
    APPROVAL_MANIFEST_DIFF_CLASSIFICATIONS,
    audit_approval_manifest_diffs,
)
from .approval_manifest_serialization import (
    SERIALIZED_APPROVAL_MANIFEST_STATUSES,
    serialize_approval_manifest_candidates,
)
from .reviewed_fixture_inputs import (
    REVIEWED_FIXTURE_INPUT_STATUSES,
    discover_default_reviewed_fixture_input_sources,
    normalize_reviewed_fixture_inputs,
)
from .trusted_shadow_consumption import (
    SUPPORTED_TRUSTED_SHADOW_DOMAINS,
    V31TrustedProductionShadowConsumption,
    build_default_trusted_repository_probes,
    deterministic_hash,
)

__all__ = [
    "DRIFT_CLASSIFICATIONS",
    "BASELINE_READINESS_CLASSIFICATIONS",
    "BASELINE_SEMANTIC_EXPECTATION_STATUSES",
    "BASELINE_TRACE_EXPECTATION_BACKFILL_STATUSES",
    "TRACE_BACKFILLED_SEMANTIC_PARITY_STATUSES",
    "CONTROLLED_CONSUMPTION_PROMOTION_READINESS_STATUSES",
    "FIXTURE_WORKFLOW_STATES",
    "FIXTURE_SET_LIFECYCLE_STATES",
    "REVIEW_POLICY_OUTCOMES",
    "REVIEWED_FIXTURE_INPUT_STATUSES",
    "FIXTURE_SET_READINESS_CLASSIFICATIONS",
    "FIXTURE_SOURCE_ADMISSION_STATUSES",
    "APPROVAL_MANIFEST_CANDIDATE_STATUSES",
    "APPROVAL_BLOCKER_CLASSIFICATIONS",
    "ADMISSION_AWARE_POLICY_STATUSES",
    "ADMISSION_AWARE_READINESS_STATUSES",
    "ADMISSION_AWARE_MANIFEST_CANDIDATE_STATUSES",
    "ADMISSION_AWARE_SERIALIZED_MANIFEST_STATUSES",
    "MANIFEST_CONSUMPTION_ELIGIBILITY_STATUSES",
    "CONTROLLED_TEST_CONSUMPTION_STATUSES",
    "CONTROLLED_CONSUMPTION_OUTPUT_VALIDATION_STATUSES",
    "CONTROLLED_CONSUMPTION_PARITY_STATUSES",
    "CONTROLLED_CONSUMPTION_SEMANTIC_PARITY_STATUSES",
    "APPROVAL_MANIFEST_DIFF_CLASSIFICATIONS",
    "SERIALIZED_APPROVAL_MANIFEST_STATUSES",
    "SUPPORTED_TRUSTED_SHADOW_DOMAINS",
    "V31BaselineFixtureWorkflows",
    "V31DualRunComparison",
    "V31PersistedFixtureSets",
    "V31PlannerSnapshotBaselines",
    "V31ReviewPolicyEvaluation",
    "V31TrustedProductionShadowConsumption",
    "build_sample_baseline_fixture_workflow_inputs",
    "build_sample_planner_snapshot_baseline_inputs",
    "build_sample_persisted_fixture_set_inputs",
    "build_sample_review_policy_inputs",
    "build_sample_dual_run_inputs",
    "build_baseline_semantic_expectations",
    "build_baseline_trace_expectation_backfill",
    "build_trace_backfilled_semantic_parity",
    "build_controlled_consumption_promotion_readiness",
    "build_default_trusted_repository_probes",
    "build_fixture_set_readiness_gate",
    "evaluate_fixture_source_admission_policy",
    "build_approval_manifest_candidates",
    "build_approval_blocker_diagnosis",
    "build_admission_aware_policy_evaluation",
    "build_admission_aware_readiness_gate",
    "build_admission_aware_manifest_candidates",
    "serialize_admission_aware_manifest_candidates",
    "evaluate_manifest_consumption_eligibility",
    "build_controlled_test_consumption",
    "validate_controlled_consumption_output",
    "build_controlled_consumption_parity_snapshot",
    "build_controlled_consumption_semantic_parity",
    "audit_approval_manifest_diffs",
    "discover_default_reviewed_fixture_input_sources",
    "deterministic_hash",
    "normalize_reviewed_fixture_inputs",
    "serialize_approval_manifest_candidates",
]
