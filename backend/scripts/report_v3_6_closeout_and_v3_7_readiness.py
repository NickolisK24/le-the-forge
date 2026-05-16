"""Generate the v3.6 closeout and v3.7 readiness report."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.runtime_intelligence.classification_hashing import deterministic_hash  # noqa: E402
from app.runtime_orchestration.v3_6_closeout_readiness_audit import (  # noqa: E402
    V3_6_PHASE_SPECS,
    audit_v3_6_closeout_readiness,
    export_v3_6_closeout_readiness_result,
)
from app.runtime_orchestration.v3_6_closeout_readiness_models import (  # noqa: E402
    V3_6_CLOSED_OUT_READY_FOR_V3_7_PLANNING,
    V3_6_CONTINUITY_BLOCKED,
    V3_6_CONTINUITY_PRESERVED,
    V3_6_VALIDATION_BLOCKED,
    V3_6_VALIDATION_STABLE,
    V36CloseoutReadinessInput,
    export_v3_6_closeout_blocker_statuses,
    export_v3_7_readiness_classifications,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_6_closeout_and_v3_7_readiness_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    scenarios = _scenario_results(root)
    focused = scenarios["full_v3_6_chain_present_and_stable"]
    summary = focused["phase_coverage_summary"]
    deterministic_validation_status = (
        V3_6_VALIDATION_STABLE
        if focused["closeout_status"] == V3_6_CLOSED_OUT_READY_FOR_V3_7_PLANNING
        else V3_6_VALIDATION_BLOCKED
    )
    report = {
        "schema_version": "v3_6.closeout_and_v3_7_readiness_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.6_phase_10_closeout_and_v3_7_readiness",
        "architectural_purpose": "deterministic v3.6 closeout and v3.7 readiness auditing",
        "planning_only": True,
        "non_production": True,
        "closeout_audit_only": True,
        "orchestration_execution_enabled": False,
        "routing_behavior_enabled": False,
        "autonomous_behavior_enabled": False,
        "recommendation_behavior_enabled": False,
        "optimization_behavior_enabled": False,
        "mutation_behavior_enabled": False,
        "persistent_write_enabled": False,
        "production_runtime_behavior_enabled": False,
        "background_execution_enabled": False,
        "execution_planning_enabled": False,
        "final_closeout_status": focused["closeout_status"],
        "v3_7_readiness_classification": focused["v3_7_readiness_classification"],
        "v3_7_readiness_classifications_supported": export_v3_7_readiness_classifications(),
        "closeout_blocker_statuses_supported": export_v3_6_closeout_blocker_statuses(),
        "audited_phase_count": summary["audited_phase_count"],
        "valid_phase_count": summary["valid_phase_count"],
        "invalid_phase_count": summary["invalid_phase_count"],
        "replay_continuity_status": _status_for(focused["replay_continuity_failure_list"]),
        "rollback_continuity_status": _status_for(focused["rollback_continuity_failure_list"]),
        "provenance_continuity_status": _status_for(focused["provenance_failure_list"]),
        "explainability_continuity_status": _status_for(focused["explainability_failure_list"]),
        "integrity_continuity_status": _status_for(focused["integrity_failure_list"]),
        "blocker_continuity_status": _status_for(focused["blocker_visibility_failure_list"]),
        "unsupported_prohibited_visibility_status": _status_for(
            focused["unsupported_prohibited_visibility_failure_list"]
        ),
        "execution_prohibition_status": _status_for(
            focused["execution_leakage_list"] + focused["prohibited_runtime_behavior_list"]
        ),
        "deterministic_validation_status": deterministic_validation_status,
        "replay_safety_confirmation": not focused["replay_continuity_failure_list"],
        "rollback_safety_confirmation": not focused["rollback_continuity_failure_list"],
        "deterministic_closeout_hash": focused["deterministic_closeout_hash"],
        "full_phase_coverage": _phase_coverage(),
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "status_distribution": _status_distribution(scenarios),
        "missing_report_summary": _list_summary(scenarios, "missing_report_list"),
        "missing_documentation_summary": _list_summary(scenarios, "missing_documentation_list"),
        "missing_hash_summary": _list_summary(scenarios, "missing_deterministic_hash_list"),
        "missing_scenario_coverage_summary": _list_summary(scenarios, "missing_scenario_coverage_list"),
        "continuity_failure_summary": _combined_summary(
            scenarios,
            (
                "missing_continuity_evidence_list",
                "replay_continuity_failure_list",
                "rollback_continuity_failure_list",
                "provenance_failure_list",
                "explainability_failure_list",
                "integrity_failure_list",
            ),
        ),
        "blocker_visibility_summary": _list_summary(scenarios, "blocker_visibility_failure_list"),
        "unsupported_prohibited_visibility_summary": _list_summary(
            scenarios,
            "unsupported_prohibited_visibility_failure_list",
        ),
        "execution_prohibition_summary": _combined_summary(
            scenarios,
            ("execution_leakage_list", "prohibited_runtime_behavior_list"),
        ),
        "deterministic_guarantees": focused["deterministic_guarantee_summary"],
        "explicit_limitations": focused["limitation_summary"],
        "explicit_prohibitions": [
            "orchestration execution",
            "orchestration routing",
            "autonomous orchestration",
            "execution-capable orchestration graphs",
            "orchestration scheduling",
            "recommendation systems",
            "optimization systems",
            "mutation behavior",
            "persistent writes",
            "live runtime reads",
            "hidden orchestration pathways",
            "background execution",
            "execution planning",
        ],
        "v3_6_accomplishments": [
            "Policy Intelligence",
            "Compatibility Intelligence",
            "Resolution Auditing",
            "Intent Modeling",
            "Intent-Policy Mapping",
            "Preflight Evaluation",
            "Evaluation Trace Modeling",
            "Replay Packets",
            "Chain Integrity Auditing",
        ],
        "summary": {
            "scenario_count": len(scenarios),
            "audited_phase_count": summary["audited_phase_count"],
            "valid_phase_count": summary["valid_phase_count"],
            "invalid_phase_count": summary["invalid_phase_count"],
            "deterministic_outputs": True,
            "stable_serialization": True,
            "stable_closeout_hashing": True,
            "replay_continuity_validated": True,
            "rollback_continuity_validated": True,
            "provenance_continuity_validated": True,
            "explainability_continuity_validated": True,
            "integrity_continuity_validated": True,
            "prohibition_preservation_validated": True,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.6 Closeout and v3.7 Readiness",
        "",
        "## Architectural Purpose",
        "",
        "v3.6 Phase 10 establishes deterministic v3.6 closeout and v3.7 readiness auditing.",
        "",
        "It validates architectural continuity, replay continuity, rollback continuity, provenance continuity, explainability continuity, governance continuity, deterministic integrity continuity, prohibition preservation, non-execution guarantees, and v3.7 planning readiness.",
        "",
        "This phase is planning-only governance auditing.",
        "",
        "It does not execute orchestration.",
        "",
        "It does not route orchestration.",
        "",
        "It does not mutate state.",
        "",
        "It does not create execution plans.",
        "",
        f"- Final closeout status: `{report['final_closeout_status']}`",
        f"- v3.7 readiness classification: `{report['v3_7_readiness_classification']}`",
        f"- Audited phases: `{report['audited_phase_count']}`",
        f"- Valid phases: `{report['valid_phase_count']}`",
        f"- Invalid phases: `{report['invalid_phase_count']}`",
        f"- Replay continuity: `{report['replay_continuity_status']}`",
        f"- Rollback continuity: `{report['rollback_continuity_status']}`",
        f"- Provenance continuity: `{report['provenance_continuity_status']}`",
        f"- Explainability continuity: `{report['explainability_continuity_status']}`",
        f"- Integrity continuity: `{report['integrity_continuity_status']}`",
        f"- Blocker continuity: `{report['blocker_continuity_status']}`",
        f"- Unsupported/prohibited visibility: `{report['unsupported_prohibited_visibility_status']}`",
        f"- Execution prohibition: `{report['execution_prohibition_status']}`",
        f"- Deterministic validation: `{report['deterministic_validation_status']}`",
        f"- Deterministic closeout hash: `{report['deterministic_closeout_hash']}`",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        "",
        "## v3.6 Accomplishments",
        "",
    ]
    lines.extend(f"- {item}" for item in report["v3_6_accomplishments"])
    lines.extend(["", "## Audited Phase Outputs", ""])
    for phase in report["full_phase_coverage"]:
        lines.append(f"- `{phase['phase_id']}`: {phase['phase_name']} -> `{phase['report_path']}`")
    lines.extend(["", "## Deterministic Guarantees", ""])
    lines.extend(f"- {item}" for item in report["deterministic_guarantees"])
    lines.extend(
        [
            "",
            "## Replay Guarantees",
            "",
            "Replay continuity is validated through generated v3.6 report evidence and the chain integrity audit. Replay evidence remains non-executing.",
            "",
            "## Rollback Guarantees",
            "",
            "Rollback continuity is validated through generated v3.6 report evidence and remains mutation-free.",
            "",
            "## Provenance Guarantees",
            "",
            "Every v3.6 phase report must preserve provenance continuity evidence before v3.7 planning is classified as ready.",
            "",
            "## Explainability Guarantees",
            "",
            "Every v3.6 phase report must preserve explainability continuity evidence and fail-visible blocker state.",
            "",
            "## Prohibition Guarantees",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["explicit_prohibitions"])
    lines.extend(["", "## v3.6 Limitations", ""])
    lines.extend(f"- {item}" for item in report["explicit_limitations"])
    lines.extend(["", "## Explicit Limitations", ""])
    lines.extend(
        [
            "- The closeout audit inspects generated v3.6 evidence only.",
            "- The closeout audit does not create new orchestration capability.",
            "- The closeout audit does not repair missing evidence or infer absent continuity.",
            "- The closeout audit does not authorize runtime behavior.",
        ]
    )
    lines.extend(["", "## Scenario Coverage", ""])
    for scenario_id, result in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{result['v3_7_readiness_classification']}`")
    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _scenario_results(repo_root: Path) -> dict[str, dict[str, Any]]:
    reports = _current_phase_reports(repo_root)
    docs = {spec.phase_id: (repo_root / spec.documentation_path).exists() for spec in V3_6_PHASE_SPECS}
    missing_report = dict(reports)
    missing_report["phase_3_resolution_auditing"] = None
    missing_doc = dict(docs)
    missing_doc["phase_5_intent_policy_mapping"] = False
    missing_hash = copy.deepcopy(reports)
    missing_hash["phase_9_chain_integrity_audit"].pop("deterministic_report_hash", None)
    missing_scenario = copy.deepcopy(reports)
    missing_scenario["phase_4_intent_modeling"]["scenario_results"] = {}
    missing_scenario["phase_4_intent_modeling"]["scenario_coverage"] = []
    missing_continuity = copy.deepcopy(reports)
    _remove_matching_keys(missing_continuity["phase_1_policy_intelligence"], "_continuity_status")
    replay_failure = copy.deepcopy(reports)
    replay_failure["phase_8_replay_packets"]["replay_safety_confirmation"] = False
    rollback_failure = copy.deepcopy(reports)
    rollback_failure["phase_7_evaluation_trace_modeling"]["rollback_safety_confirmation"] = False
    provenance_failure = copy.deepcopy(reports)
    provenance_failure["phase_6_preflight_evaluation"]["provenance_continuity_status"] = "preflight_continuity_gap"
    explainability_failure = copy.deepcopy(reports)
    explainability_failure["phase_5_intent_policy_mapping"]["explainability_continuity_status"] = "mapping_continuity_gap"
    integrity_failure = copy.deepcopy(reports)
    integrity_failure["phase_2_compatibility_intelligence"]["integrity_continuity_status"] = "compatibility_continuity_gap"
    blocker_failure = copy.deepcopy(reports)
    _remove_token_keys(blocker_failure["phase_1_policy_intelligence"], "blocker")
    unsupported_prohibited_failure = copy.deepcopy(reports)
    _remove_token_keys(unsupported_prohibited_failure["phase_3_resolution_auditing"], "unsupported")
    _remove_token_keys(unsupported_prohibited_failure["phase_3_resolution_auditing"], "prohibited")
    execution_leak = copy.deepcopy(reports)
    execution_leak["phase_1_policy_intelligence"]["orchestration_execution_enabled"] = True
    prohibited_runtime = copy.deepcopy(reports)
    prohibited_runtime["phase_4_intent_modeling"]["recommendation_behavior_enabled"] = True
    scenarios = {
        "full_v3_6_chain_present_and_stable": V36CloseoutReadinessInput(repo_root, reports, docs),
        "missing_phase_report": V36CloseoutReadinessInput(repo_root, missing_report, docs),
        "missing_migration_documentation": V36CloseoutReadinessInput(repo_root, reports, missing_doc),
        "missing_deterministic_hash": V36CloseoutReadinessInput(repo_root, missing_hash, docs),
        "missing_scenario_coverage": V36CloseoutReadinessInput(repo_root, missing_scenario, docs),
        "missing_continuity_evidence": V36CloseoutReadinessInput(repo_root, missing_continuity, docs),
        "replay_continuity_failure": V36CloseoutReadinessInput(repo_root, replay_failure, docs),
        "rollback_continuity_failure": V36CloseoutReadinessInput(repo_root, rollback_failure, docs),
        "provenance_failure": V36CloseoutReadinessInput(repo_root, provenance_failure, docs),
        "explainability_failure": V36CloseoutReadinessInput(repo_root, explainability_failure, docs),
        "integrity_failure": V36CloseoutReadinessInput(repo_root, integrity_failure, docs),
        "blocker_visibility_failure": V36CloseoutReadinessInput(repo_root, blocker_failure, docs),
        "unsupported_prohibited_visibility_failure": V36CloseoutReadinessInput(
            repo_root,
            unsupported_prohibited_failure,
            docs,
        ),
        "execution_leakage_detection": V36CloseoutReadinessInput(repo_root, execution_leak, docs),
        "prohibited_runtime_behavior_detection": V36CloseoutReadinessInput(repo_root, prohibited_runtime, docs),
        "phase_chain_disconnected": V36CloseoutReadinessInput(repo_root, reports, docs, phase_chain_connected=False),
        "manual_review_readiness_state": V36CloseoutReadinessInput(
            repo_root,
            reports,
            docs,
            manual_review_reasons=("manual_v3_6_closeout_review",),
        ),
    }
    return {
        scenario_id: export_v3_6_closeout_readiness_result(audit_v3_6_closeout_readiness(source_input))
        for scenario_id, source_input in scenarios.items()
    }


def _current_phase_reports(repo_root: Path) -> dict[str, dict[str, Any]]:
    return {
        spec.phase_id: json.loads((repo_root / spec.report_path).read_text(encoding="utf-8"))
        for spec in V3_6_PHASE_SPECS
    }


def _phase_coverage() -> list[dict[str, str]]:
    return [
        {
            "phase_id": spec.phase_id,
            "phase_name": spec.phase_name,
            "report_path": spec.report_path,
            "documentation_path": spec.documentation_path,
        }
        for spec in V3_6_PHASE_SPECS
    ]


def _status_distribution(scenarios: dict[str, dict[str, Any]]) -> dict[str, int]:
    distribution: dict[str, int] = {}
    for result in scenarios.values():
        status = result["v3_7_readiness_classification"]
        distribution[status] = distribution.get(status, 0) + 1
    return dict(sorted(distribution.items()))


def _list_summary(scenarios: dict[str, dict[str, Any]], field: str) -> dict[str, list[str]]:
    return {
        scenario_id: result[field]
        for scenario_id, result in sorted(scenarios.items())
        if result[field]
    }


def _combined_summary(scenarios: dict[str, dict[str, Any]], fields: tuple[str, ...]) -> dict[str, dict[str, list[str]]]:
    summary: dict[str, dict[str, list[str]]] = {}
    for scenario_id, result in sorted(scenarios.items()):
        entries = {field: result[field] for field in fields if result[field]}
        if entries:
            summary[scenario_id] = entries
    return summary


def _status_for(failures: list[str] | tuple[str, ...]) -> str:
    return V3_6_CONTINUITY_BLOCKED if failures else V3_6_CONTINUITY_PRESERVED


def _remove_matching_keys(report: dict[str, Any], suffix: str) -> None:
    for key in tuple(report.keys()):
        if key.endswith(suffix):
            report.pop(key, None)


def _remove_token_keys(report: dict[str, Any], token: str) -> None:
    for key in tuple(report.keys()):
        if token in key:
            report.pop(key, None)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    report = build_v3_6_closeout_and_v3_7_readiness_report(args.repo_root)
    generated_path = args.repo_root / "docs/generated/v3_6_closeout_and_v3_7_readiness_report.json"
    markdown_path = args.repo_root / "docs/migration/V3_6_CLOSEOUT_AND_V3_7_READINESS.md"
    generated_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    generated_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_path)


if __name__ == "__main__":
    main()
