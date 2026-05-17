"""Report builders for deterministic v3.9 transition continuity certification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .transition_certification_engine import certify_v3_9_transition_continuity
from .transition_certification_models import (
    CERTIFICATION_CLASSIFICATION_BLOCKED,
    CERTIFICATION_CLASSIFICATION_CERTIFIED,
    CERTIFICATION_CLASSIFICATION_CERTIFIED_WITH_WARNINGS,
    CERTIFICATION_CLASSIFICATION_INCOMPLETE,
    CERTIFICATION_CLASSIFICATION_NOT_CERTIFIED,
    CERTIFICATION_CLASSIFICATION_PROHIBITED,
    CERTIFICATION_CLASSIFICATION_UNKNOWN,
    CERTIFICATION_CLASSIFICATION_UNSUPPORTED,
    CERTIFICATION_GUARANTEE_AGGREGATION,
    CERTIFICATION_GUARANTEE_BOUNDARY,
    CERTIFICATION_GUARANTEE_COMPATIBILITY,
    CERTIFICATION_GUARANTEE_EVALUATION,
    CERTIFICATION_GUARANTEE_EXPLAINABILITY,
    CERTIFICATION_GUARANTEE_FOUNDATION,
    CERTIFICATION_GUARANTEE_INTEGRITY,
    CERTIFICATION_GUARANTEE_NON_EXECUTION,
    CERTIFICATION_GUARANTEE_NON_MUTATION,
    CERTIFICATION_GUARANTEE_NON_RRSS,
    CERTIFICATION_GUARANTEE_PROVENANCE,
    CERTIFICATION_GUARANTEE_REPLAY,
    CERTIFICATION_GUARANTEE_ROLLBACK,
    CERTIFICATION_GUARANTEE_SCENARIO,
    CERTIFICATION_GUARANTEE_SESSION,
    CERTIFICATION_GUARANTEE_VISIBILITY,
    export_transition_certification_report,
)
from .transition_certification_serialization import (
    hash_transition_certification_report,
    validate_transition_certification_hash_stability,
    validate_transition_certification_serialization_stability,
)
from .transition_certification_validation import validate_transition_certification_report
from .transition_foundation_hashing import deterministic_hash


DETERMINISTIC_GENERATED_AT = "2026-05-17T00:00:00+00:00"

SOURCE_ARTIFACT_PATHS: tuple[str, ...] = (
    "docs/generated/v3_9_transition_foundations_report.json",
    "docs/migration/V3_9_TRANSITION_FOUNDATIONS.md",
    "docs/generated/v3_9_transition_boundary_intelligence_report.json",
    "docs/migration/V3_9_TRANSITION_BOUNDARY_INTELLIGENCE.md",
    "docs/generated/v3_9_transition_compatibility_intelligence_report.json",
    "docs/migration/V3_9_TRANSITION_COMPATIBILITY_INTELLIGENCE.md",
    "docs/generated/v3_9_transition_evaluation_intelligence_report.json",
    "docs/migration/V3_9_TRANSITION_EVALUATION_INTELLIGENCE.md",
    "docs/generated/v3_9_transition_session_intelligence_report.json",
    "docs/migration/V3_9_TRANSITION_SESSION_INTELLIGENCE.md",
    "docs/generated/v3_9_transition_scenario_intelligence_report.json",
    "docs/migration/V3_9_TRANSITION_SCENARIO_INTELLIGENCE.md",
    "docs/generated/v3_9_transition_intelligence_aggregation_report.json",
    "docs/migration/V3_9_TRANSITION_INTELLIGENCE_AGGREGATION.md",
    "docs/generated/v3_9_transition_integrity_enforcement_report.json",
    "docs/migration/V3_9_TRANSITION_INTEGRITY_ENFORCEMENT.md",
)


def build_v3_9_transition_continuity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[3]
    certification_report = certify_v3_9_transition_continuity()
    validation = validate_transition_certification_report(certification_report)
    serialization = validate_transition_certification_serialization_stability(certification_report)
    hashing = validate_transition_certification_hash_stability(certification_report)
    source_artifacts = [_source_artifact_status(root, path) for path in SOURCE_ARTIFACT_PATHS]
    source_artifact_count = len(source_artifacts)
    present_source_artifact_count = sum(1 for artifact in source_artifacts if artifact["present"])
    report = {
        "schema_version": "v3_9.transition_continuity_certification_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.9_transition_continuity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic evidence-only transition continuity certification without approval",
        "certification_report_status": certification_report.report_status,
        "source_integrity_report_id": certification_report.source_integrity_report_id,
        "source_integrity_hash": certification_report.source_integrity_hash,
        "non_executable": certification_report.non_executable,
        "orchestration_execution_enabled": certification_report.orchestration_execution_enabled,
        "transition_execution_enabled": certification_report.transition_execution_enabled,
        "graph_traversal_enabled": certification_report.graph_traversal_enabled,
        "routing_enabled": certification_report.routing_enabled,
        "scheduling_enabled": certification_report.scheduling_enabled,
        "dispatch_enabled": certification_report.dispatch_enabled,
        "runtime_orchestration_engine_enabled": certification_report.runtime_orchestration_engine_enabled,
        "runtime_mutation_enabled": certification_report.runtime_mutation_enabled,
        "authorization_enabled": certification_report.authorization_enabled,
        "approval_enabled": certification_report.approval_enabled,
        "optimization_enabled": certification_report.optimization_enabled,
        "recommendation_enabled": certification_report.recommendation_enabled,
        "ranking_enabled": certification_report.ranking_enabled,
        "scoring_enabled": certification_report.scoring_enabled,
        "selection_enabled": certification_report.selection_enabled,
        "remediation_enabled": certification_report.remediation_enabled,
        "repair_enabled": certification_report.repair_enabled,
        "automatic_remediation_enabled": certification_report.automatic_remediation_enabled,
        "automatic_repair_enabled": certification_report.automatic_repair_enabled,
        "hidden_fallback_enabled": certification_report.hidden_fallback_enabled,
        "silent_correction_enabled": certification_report.silent_correction_enabled,
        "prioritization_enabled": certification_report.prioritization_enabled,
        "weighted_scoring_enabled": certification_report.weighted_scoring_enabled,
        "source_artifacts": source_artifacts,
        "source_artifact_totals": {
            "source_artifact_count": source_artifact_count,
            "present_source_artifact_count": present_source_artifact_count,
            "missing_source_artifact_count": source_artifact_count - present_source_artifact_count,
            "source_artifact_continuity_preserved": present_source_artifact_count == source_artifact_count,
        },
        "certification_classification_counts": dict(certification_report.summary.classification_counts),
        "certification_finding_counts": dict(certification_report.summary.finding_category_counts),
        "certification_guarantee_counts": dict(certification_report.summary.guarantee_category_counts),
        "certification_visibility_counts": dict(certification_report.summary.visibility_category_counts),
        "certification_totals": {
            "certification_input_count": validation["certification_input_count"],
            "certified_count": validation["certified_count"],
            "certified_with_warnings_count": validation["certified_with_warnings_count"],
            "not_certified_count": validation["not_certified_count"],
            "blocked_count": validation["blocked_count"],
            "unsupported_count": validation["unsupported_count"],
            "prohibited_count": validation["prohibited_count"],
            "unknown_count": validation["unknown_count"],
            "incomplete_count": validation["incomplete_count"],
            "certification_finding_count": validation["certification_finding_count"],
            "certification_guarantee_count": validation["certification_guarantee_count"],
            "replay_continuity_guarantee_count": validation["replay_continuity_guarantee_count"],
            "rollback_continuity_guarantee_count": validation["rollback_continuity_guarantee_count"],
            "provenance_continuity_guarantee_count": validation["provenance_continuity_guarantee_count"],
            "explainability_continuity_guarantee_count": validation[
                "explainability_continuity_guarantee_count"
            ],
            "visibility_continuity_guarantee_count": validation["visibility_continuity_guarantee_count"],
            "integrity_continuity_guarantee_count": validation["integrity_continuity_guarantee_count"],
            "non_execution_continuity_guarantee_count": validation[
                "non_execution_continuity_guarantee_count"
            ],
            "recommendation_ranking_scoring_selection_non_capability_guarantee_count": validation[
                "recommendation_ranking_scoring_selection_non_capability_guarantee_count"
            ],
            "mutation_non_capability_guarantee_count": validation["mutation_non_capability_guarantee_count"],
            "hidden_finding_count": validation["hidden_finding_count"],
            "hidden_risk_count": validation["hidden_risk_count"],
            "hidden_non_safe_state_count": validation["hidden_non_safe_state_count"],
            "execution_boundary_leakage_count": validation["execution_boundary_leakage_count"],
            "recommendation_leakage_count": validation["recommendation_leakage_count"],
            "ranking_leakage_count": validation["ranking_leakage_count"],
            "scoring_leakage_count": validation["scoring_leakage_count"],
            "selection_leakage_count": validation["selection_leakage_count"],
            "mutation_leakage_count": validation["mutation_leakage_count"],
        },
        "guarantee_semantics": {
            CERTIFICATION_GUARANTEE_FOUNDATION: "foundation continuity guarantee",
            CERTIFICATION_GUARANTEE_BOUNDARY: "boundary continuity guarantee",
            CERTIFICATION_GUARANTEE_COMPATIBILITY: "compatibility continuity guarantee",
            CERTIFICATION_GUARANTEE_EVALUATION: "evaluation continuity guarantee",
            CERTIFICATION_GUARANTEE_SESSION: "session continuity guarantee",
            CERTIFICATION_GUARANTEE_SCENARIO: "scenario continuity guarantee",
            CERTIFICATION_GUARANTEE_AGGREGATION: "aggregation continuity guarantee",
            CERTIFICATION_GUARANTEE_INTEGRITY: "integrity continuity guarantee",
            CERTIFICATION_GUARANTEE_REPLAY: "replay continuity guarantee",
            CERTIFICATION_GUARANTEE_ROLLBACK: "rollback continuity guarantee",
            CERTIFICATION_GUARANTEE_PROVENANCE: "provenance continuity guarantee",
            CERTIFICATION_GUARANTEE_EXPLAINABILITY: "explainability continuity guarantee",
            CERTIFICATION_GUARANTEE_VISIBILITY: "visibility continuity guarantee",
            CERTIFICATION_GUARANTEE_NON_EXECUTION: "non-execution continuity guarantee",
            CERTIFICATION_GUARANTEE_NON_RRSS: "recommendation/ranking/scoring/selection non-capability guarantee",
            CERTIFICATION_GUARANTEE_NON_MUTATION: "mutation non-capability guarantee",
        },
        "classification_semantics": {
            CERTIFICATION_CLASSIFICATION_CERTIFIED: "all continuity and non-capability guarantees are certified as evidence",
            CERTIFICATION_CLASSIFICATION_CERTIFIED_WITH_WARNINGS: "guarantees are preserved with fail-visible warnings",
            CERTIFICATION_CLASSIFICATION_NOT_CERTIFIED: "continuity or integrity guarantees fail visibly",
            CERTIFICATION_CLASSIFICATION_BLOCKED: "governance, integrity preconditions, or boundary preservation blocks certification",
            CERTIFICATION_CLASSIFICATION_UNSUPPORTED: "certification domain or evidence is outside supported deterministic scope",
            CERTIFICATION_CLASSIFICATION_PROHIBITED: "requested certification behavior violates non-execution or non-approval boundaries",
            CERTIFICATION_CLASSIFICATION_UNKNOWN: "certification semantics, provenance meaning, continuity meaning, or evidence meaning is uncertain",
            CERTIFICATION_CLASSIFICATION_INCOMPLETE: "required domains, certification evidence, integrity evidence, provenance, continuity, or explainability are missing",
        },
        "deterministic_guarantees": {
            "certification_serialization_stable": serialization["stable"],
            "certification_hash_stable": hashing["stable"],
            "certification_hash": hash_transition_certification_report(certification_report),
            "certification_summary_hash": certification_report.summary.deterministic_summary_hash,
            "serialization_first_length": serialization["first_length"],
            "serialization_second_length": serialization["second_length"],
            "hash_algorithm": hashing["hash_algorithm"],
        },
        "deterministic_guarantee_summary": {
            "outputs_are_deterministic": serialization["stable"] and hashing["stable"],
            "finding_order_is_stable": True,
            "guarantee_order_is_stable": True,
            "visibility_order_is_stable": True,
            "serialization_is_stable": serialization["stable"],
            "hashing_is_stable": hashing["stable"],
            "repeated_equivalent_certifications_produce_equivalent_outputs": True,
        },
        "replay_guarantees": {
            "replay_safe_certification_finding_count": validation["replay_safe_certification_finding_count"],
            "replay_continuity_preserved_count": validation["replay_continuity_preserved_count"],
            "replay_continuity_guarantee_count": validation["replay_continuity_guarantee_count"],
        },
        "rollback_guarantees": {
            "rollback_safe_certification_finding_count": validation[
                "rollback_safe_certification_finding_count"
            ],
            "rollback_continuity_preserved_count": validation["rollback_continuity_preserved_count"],
            "rollback_continuity_guarantee_count": validation["rollback_continuity_guarantee_count"],
        },
        "provenance_guarantees": {
            "provenance_safe_certification_finding_count": validation[
                "provenance_safe_certification_finding_count"
            ],
            "provenance_continuity_preserved_count": validation[
                "provenance_continuity_preserved_count"
            ],
            "provenance_continuity_guarantee_count": validation["provenance_continuity_guarantee_count"],
        },
        "explainability_guarantees": {
            "explainability_safe_certification_finding_count": validation[
                "explainability_safe_certification_finding_count"
            ],
            "explainability_continuity_preserved_count": validation[
                "explainability_continuity_preserved_count"
            ],
            "all_findings_have_explainability": validation["finding_not_fail_visible_count"] == 0,
            "all_guarantees_are_visible": validation["guarantee_not_visible_count"] == 0,
            "all_visibility_is_fail_visible": validation["visibility_not_fail_visible_count"] == 0,
        },
        "non_execution_guarantees": {
            "orchestration_execution_absent": not certification_report.orchestration_execution_enabled,
            "transition_execution_absent": not certification_report.transition_execution_enabled,
            "graph_traversal_absent": not certification_report.graph_traversal_enabled,
            "routing_absent": not certification_report.routing_enabled,
            "scheduling_absent": not certification_report.scheduling_enabled,
            "dispatch_absent": not certification_report.dispatch_enabled,
            "runtime_orchestration_engine_absent": not certification_report.runtime_orchestration_engine_enabled,
            "runtime_mutation_absent": not certification_report.runtime_mutation_enabled,
            "authorization_absent": not certification_report.authorization_enabled,
            "approval_absent": not certification_report.approval_enabled,
            "optimization_absent": not certification_report.optimization_enabled,
            "recommendation_absent": not certification_report.recommendation_enabled,
            "ranking_absent": not certification_report.ranking_enabled,
            "scoring_absent": not certification_report.scoring_enabled,
            "selection_absent": not certification_report.selection_enabled,
            "remediation_absent": not certification_report.remediation_enabled,
            "repair_absent": not certification_report.repair_enabled,
            "automatic_remediation_absent": not certification_report.automatic_remediation_enabled,
            "automatic_repair_absent": not certification_report.automatic_repair_enabled,
            "hidden_fallback_absent": not certification_report.hidden_fallback_enabled,
            "silent_correction_absent": not certification_report.silent_correction_enabled,
            "prioritization_absent": not certification_report.prioritization_enabled,
            "weighted_scoring_absent": not certification_report.weighted_scoring_enabled,
            "report_capability_leakage_count": validation["report_capability_leakage_count"],
        },
        "certification_only_guarantees": {
            "certification_is_descriptive_evidence": validation["guarantee_not_visible_count"] == 0,
            "no_approval_behavior": validation["non_approval_confirmation"],
            "no_remediation_behavior": validation["non_approval_confirmation"],
            "no_repair_behavior": validation["non_approval_confirmation"],
            "no_recommendation_behavior": not certification_report.recommendation_enabled,
            "no_ranking_behavior": not certification_report.ranking_enabled,
            "no_scoring_behavior": not certification_report.scoring_enabled,
            "no_selection_behavior": not certification_report.selection_enabled,
            "non_selective_confirmation": validation["non_selective_confirmation"],
        },
        "certification_report": export_transition_certification_report(certification_report),
        "explicit_limitations": [
            "v3.9 Phase 9 transition continuity certification is evidence-only",
            "v3.9 Phase 9 does not enable orchestration execution",
            "v3.9 Phase 9 does not enable transition execution",
            "v3.9 Phase 9 does not enable approval or authorization",
            "v3.9 Phase 9 does not enable remediation or repair",
            "v3.9 Phase 9 does not enable routing, scheduling, dispatch, or traversal",
            "v3.9 Phase 9 does not enable recommendations",
            "v3.9 Phase 9 does not enable ranking, scoring, or selection",
            "v3.9 Phase 9 does not prioritize or weight certification outcomes",
            "v3.9 Phase 9 does not mutate transition evidence",
        ],
        "summary": {
            "certification_report_status": certification_report.report_status,
            "validation_error_count": validation["validation_error_count"],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "certified_count": validation["certified_count"],
            "certified_with_warnings_count": validation["certified_with_warnings_count"],
            "not_certified_count": validation["not_certified_count"],
            "blocked_count": validation["blocked_count"],
            "unsupported_count": validation["unsupported_count"],
            "prohibited_count": validation["prohibited_count"],
            "unknown_count": validation["unknown_count"],
            "incomplete_count": validation["incomplete_count"],
            "certification_finding_count": validation["certification_finding_count"],
            "certification_guarantee_count": validation["certification_guarantee_count"],
            "replay_continuity_guarantee_count": validation["replay_continuity_guarantee_count"],
            "rollback_continuity_guarantee_count": validation["rollback_continuity_guarantee_count"],
            "provenance_continuity_guarantee_count": validation["provenance_continuity_guarantee_count"],
            "explainability_continuity_guarantee_count": validation[
                "explainability_continuity_guarantee_count"
            ],
            "visibility_continuity_guarantee_count": validation["visibility_continuity_guarantee_count"],
            "integrity_continuity_guarantee_count": validation["integrity_continuity_guarantee_count"],
            "non_execution_continuity_guarantee_count": validation[
                "non_execution_continuity_guarantee_count"
            ],
            "recommendation_ranking_scoring_selection_non_capability_guarantee_count": validation[
                "recommendation_ranking_scoring_selection_non_capability_guarantee_count"
            ],
            "mutation_non_capability_guarantee_count": validation["mutation_non_capability_guarantee_count"],
            "hidden_finding_count": validation["hidden_finding_count"],
            "hidden_risk_count": validation["hidden_risk_count"],
            "hidden_non_safe_state_count": validation["hidden_non_safe_state_count"],
            "execution_boundary_leakage_count": validation["execution_boundary_leakage_count"],
            "recommendation_leakage_count": validation["recommendation_leakage_count"],
            "ranking_leakage_count": validation["ranking_leakage_count"],
            "scoring_leakage_count": validation["scoring_leakage_count"],
            "selection_leakage_count": validation["selection_leakage_count"],
            "mutation_leakage_count": validation["mutation_leakage_count"],
            "replay_verified": validation["replay_safe_certification_finding_count"]
            == validation["certification_finding_count"],
            "rollback_verified": validation["rollback_safe_certification_finding_count"]
            == validation["certification_finding_count"],
            "provenance_verified": validation["provenance_safe_certification_finding_count"]
            == validation["certification_finding_count"],
            "explainability_verified": validation["finding_not_fail_visible_count"] == 0,
            "guarantee_visibility_verified": validation["guarantee_not_visible_count"] == 0,
            "visibility_verified": validation["visibility_not_fail_visible_count"] == 0,
            "non_executable_verified": certification_report.non_executable,
            "orchestration_boundaries_enforced": validation["report_capability_leakage_count"] == 0,
            "non_approval_verified": validation["non_approval_confirmation"],
            "descriptive_certification_verified": validation["non_selective_confirmation"],
            "source_artifact_continuity_preserved": present_source_artifact_count == source_artifact_count,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_transition_certification_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.9 Transition Continuity Certification",
        "",
        "## What Phase 9 Adds",
        "",
        "v3.9 Phase 9 certifies the full transition intelligence chain across replay, rollback, provenance, explainability, visibility, integrity, and non-execution continuity.",
        "",
        "Certification is descriptive evidence, not authorization. It may certify, warn, block, or fail-visible report certification status without modifying evidence.",
        "",
        "This phase does NOT enable orchestration execution, traversal, routing, scheduling, dispatch, optimization, recommendation, ranking, scoring, selection, authorization, approval, remediation, repair, or runtime mutation.",
        "",
        "## Certification Is Not Approval",
        "",
        "Certification records deterministic continuity guarantees. It does not approve a transition, authorize runtime behavior, choose a transition path, or imply production readiness.",
        "",
        "## Continuity Guarantees",
        "",
        "The certification report records foundation, boundary, compatibility, evaluation, session, scenario, aggregation, integrity, replay, rollback, provenance, explainability, visibility, non-execution, non-selection, and non-mutation guarantees.",
        "",
        "## Hidden Behavior And Leakage",
        "",
        "Hidden finding, hidden risk, hidden non-safe state, execution leakage, mutation leakage, and recommendation/ranking/scoring/selection leakage remain fail-visible certification findings.",
        "",
        "## Builds On Integrity Enforcement",
        "",
        "Phase 9 builds on transition integrity enforcement and certifies continuity evidence without changing integrity audit behavior.",
        "",
        "## Certification Totals",
        "",
        f"- Certified: `{report['summary']['certified_count']}`",
        f"- Certified with warnings: `{report['summary']['certified_with_warnings_count']}`",
        f"- Not certified: `{report['summary']['not_certified_count']}`",
        f"- Blocked: `{report['summary']['blocked_count']}`",
        f"- Unsupported: `{report['summary']['unsupported_count']}`",
        f"- Prohibited: `{report['summary']['prohibited_count']}`",
        f"- Unknown: `{report['summary']['unknown_count']}`",
        f"- Incomplete: `{report['summary']['incomplete_count']}`",
        f"- Certification findings: `{report['summary']['certification_finding_count']}`",
        f"- Certification guarantees: `{report['summary']['certification_guarantee_count']}`",
        "",
        "## Guarantee Totals",
        "",
        f"- Replay continuity guarantees: `{report['summary']['replay_continuity_guarantee_count']}`",
        f"- Rollback continuity guarantees: `{report['summary']['rollback_continuity_guarantee_count']}`",
        f"- Provenance continuity guarantees: `{report['summary']['provenance_continuity_guarantee_count']}`",
        f"- Explainability continuity guarantees: `{report['summary']['explainability_continuity_guarantee_count']}`",
        f"- Visibility continuity guarantees: `{report['summary']['visibility_continuity_guarantee_count']}`",
        f"- Integrity continuity guarantees: `{report['summary']['integrity_continuity_guarantee_count']}`",
        f"- Non-execution continuity guarantees: `{report['summary']['non_execution_continuity_guarantee_count']}`",
        f"- Recommendation/ranking/scoring/selection non-capability guarantees: `{report['summary']['recommendation_ranking_scoring_selection_non_capability_guarantee_count']}`",
        f"- Mutation non-capability guarantees: `{report['summary']['mutation_non_capability_guarantee_count']}`",
        "",
        "## Fail-Visible Counts",
        "",
        f"- Hidden findings: `{report['summary']['hidden_finding_count']}`",
        f"- Hidden risks: `{report['summary']['hidden_risk_count']}`",
        f"- Hidden non-safe states: `{report['summary']['hidden_non_safe_state_count']}`",
        f"- Execution-boundary leakage: `{report['summary']['execution_boundary_leakage_count']}`",
        f"- Recommendation leakage: `{report['summary']['recommendation_leakage_count']}`",
        f"- Ranking leakage: `{report['summary']['ranking_leakage_count']}`",
        f"- Scoring leakage: `{report['summary']['scoring_leakage_count']}`",
        f"- Selection leakage: `{report['summary']['selection_leakage_count']}`",
        f"- Mutation leakage: `{report['summary']['mutation_leakage_count']}`",
        "",
        "## Deterministic Guarantees",
        "",
        f"- Certification report status: `{report['summary']['certification_report_status']}`",
        f"- Validation errors: `{report['summary']['validation_error_count']}`",
        f"- Serialization stable: `{report['summary']['deterministic_serialization_verified']}`",
        f"- Hash stable: `{report['summary']['deterministic_hashing_verified']}`",
        f"- Certification hash: `{report['deterministic_guarantees']['certification_hash']}`",
        f"- Certification summary hash: `{report['deterministic_guarantees']['certification_summary_hash']}`",
        f"- Report hash: `{report['deterministic_report_hash']}`",
        "",
        "## What Remains Prohibited",
        "",
        "- Orchestration execution.",
        "- Transition execution.",
        "- Graph traversal.",
        "- Routing.",
        "- Scheduling.",
        "- Dispatch.",
        "- Runtime orchestration engines.",
        "- Runtime mutation.",
        "- Authorization systems.",
        "- Approval systems.",
        "- Optimization.",
        "- Recommendations.",
        "- Ranking.",
        "- Scoring.",
        "- Selection.",
        "- Remediation.",
        "- Repair.",
        "- Automatic remediation.",
        "- Automatic repair.",
        "- Silent correction.",
        "- Hidden fallback.",
        "- Weighted scoring.",
        "- Priority ranking.",
        "- Production behavior.",
        "",
        "## Generated Evidence",
        "",
        "- JSON report: `docs/generated/v3_9_transition_continuity_certification_report.json`",
        "- This migration note: `docs/migration/V3_9_TRANSITION_CONTINUITY_CERTIFICATION.md`",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _source_artifact_status(repo_root: Path, relative_path: str) -> dict[str, Any]:
    artifact_path = repo_root / relative_path
    if not artifact_path.exists():
        return {
            "path": relative_path,
            "present": False,
            "artifact_hash": "",
        }
    text = artifact_path.read_text(encoding="utf-8")
    try:
        payload: Any = json.loads(text)
    except json.JSONDecodeError:
        payload = {"raw_text": text}
    return {
        "path": relative_path,
        "present": True,
        "artifact_hash": deterministic_hash(payload),
    }
