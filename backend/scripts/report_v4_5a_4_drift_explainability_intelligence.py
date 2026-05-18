"""Generate deterministic v4.5A.4 drift explainability intelligence visibility."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from orchestration_governance.v4_5a_4_drift_explainability_audit import (  # noqa: E402
    build_v4_5a_4_drift_explainability_intelligence_report,
)


REPORT_PATH = Path("docs/generated/v4_5a_4_drift_explainability_intelligence_report.json")


def write_report(report: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(REPORT_PATH),
        help="v4.5A.4 drift explainability intelligence JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_5a_4_drift_explainability_intelligence_report()
    write_report(report, output_path)
    summary = report["summary"]
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"explanation_record_count={summary['explanation_record_count']}")
    print(f"cause_visibility_count={summary['cause_visibility_count']}")
    print(f"propagation_explanation_count={summary['propagation_explanation_count']}")
    print(f"degradation_explanation_count={summary['degradation_explanation_count']}")
    print(f"evidence_mapping_count={summary['evidence_mapping_count']}")
    print(f"completeness_visibility_count={summary['completeness_visibility_count']}")
    print(f"confidence_visibility_count={summary['confidence_visibility_count']}")
    print(f"explanation_diagnostic_count={summary['explanation_diagnostic_count']}")
    print(
        "unsupported_explanation_state_count="
        f"{summary['unsupported_explanation_state_count']}"
    )
    print(
        "deterministic_serialization_verified="
        f"{summary['deterministic_serialization_verified']}"
    )
    print(f"deterministic_hashing_verified={summary['deterministic_hashing_verified']}")
    print(
        "explanation_chain_continuity_preserved="
        f"{summary['explanation_chain_continuity_preserved']}"
    )
    print(f"lineage_continuity_preserved={summary['lineage_continuity_preserved']}")
    print(
        "provenance_continuity_preserved="
        f"{summary['provenance_continuity_preserved']}"
    )
    print(
        "evidence_to_explanation_mapping_stable="
        f"{summary['evidence_to_explanation_mapping_stable']}"
    )
    print(f"replay_safe_mapping_verified={summary['replay_safe_mapping_verified']}")
    print(
        "provenance_safe_mapping_verified="
        f"{summary['provenance_safe_mapping_verified']}"
    )
    print(f"lineage_safe_mapping_verified={summary['lineage_safe_mapping_verified']}")
    print(f"explanation_visibility_verified={summary['explanation_visibility_verified']}")
    print(
        "fail_visible_unsupported_explanation_verified="
        f"{summary['fail_visible_unsupported_explanation_verified']}"
    )
    print(
        "descriptive_only_guarantees_verified="
        f"{summary['descriptive_only_guarantees_verified']}"
    )
    print(f"inherited_prohibition_count={summary['inherited_prohibition_count']}")
    print(f"inherited_constraint_count={summary['inherited_constraint_count']}")
    print(f"explicit_limitation_count={summary['explicit_limitation_count']}")
    print(f"validation_error_count={summary['validation_error_count']}")
    print(f"enabled_runtime_execution_count={summary['enabled_runtime_execution_count']}")
    print(
        "enabled_orchestration_authorization_count="
        f"{summary['enabled_orchestration_authorization_count']}"
    )
    print(
        "enabled_orchestration_approval_count="
        f"{summary['enabled_orchestration_approval_count']}"
    )
    print(
        "enabled_orchestration_dispatch_count="
        f"{summary['enabled_orchestration_dispatch_count']}"
    )
    print(
        "enabled_orchestration_routing_count="
        f"{summary['enabled_orchestration_routing_count']}"
    )
    print(
        "enabled_orchestration_traversal_count="
        f"{summary['enabled_orchestration_traversal_count']}"
    )
    print(
        "enabled_orchestration_scheduling_count="
        f"{summary['enabled_orchestration_scheduling_count']}"
    )
    print(
        "enabled_orchestration_sequencing_count="
        f"{summary['enabled_orchestration_sequencing_count']}"
    )
    print(f"enabled_remediation_count={summary['enabled_remediation_count']}")
    print(f"enabled_repair_count={summary['enabled_repair_count']}")
    print(f"enabled_mitigation_count={summary['enabled_mitigation_count']}")
    print(f"enabled_auto_correction_count={summary['enabled_auto_correction_count']}")
    print(
        "enabled_explanation_action_count="
        f"{summary['enabled_explanation_action_count']}"
    )
    print(
        "enabled_explanation_ranking_count="
        f"{summary['enabled_explanation_ranking_count']}"
    )
    print(
        "enabled_explanation_authorization_count="
        f"{summary['enabled_explanation_authorization_count']}"
    )
    print(
        "enabled_explanation_decision_count="
        f"{summary['enabled_explanation_decision_count']}"
    )
    print(
        "enabled_explanation_recommendation_count="
        f"{summary['enabled_explanation_recommendation_count']}"
    )
    print(f"enabled_runtime_mutation_count={summary['enabled_runtime_mutation_count']}")
    print(
        "enabled_operational_mutation_count="
        f"{summary['enabled_operational_mutation_count']}"
    )
    print(f"enabled_planner_integration_count={summary['enabled_planner_integration_count']}")
    print(
        "enabled_production_consumption_count="
        f"{summary['enabled_production_consumption_count']}"
    )
    print(f"repository_remains={','.join(summary['repository_remains'])}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
