"""Generate the v3 operation semantics taxonomy audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REQUIRED_OPERATION_FAMILIES = (
    "flat",
    "increased",
    "more",
    "duration",
    "cost",
    "cooldown",
    "chance",
    "threshold",
    "conditional",
    "conversion",
    "unknown",
)

SEMANTIC_CONTRACT_FIELDS = (
    "operation_id",
    "operation_label",
    "source_operation_values",
    "planner_semantic_meaning",
    "allowed_domains",
    "stat_identity_dependency",
    "value_normalization_dependency",
    "stacking_semantics",
    "polarity_semantics",
    "rounding_policy_dependency",
    "conditional_requirements",
    "exclusion_rules",
    "source_examples",
    "golden_baseline_refs",
    "validation_status",
    "promotion_status",
    "blocked_reasons",
    "provenance",
)

PROMOTION_STATES = frozenset(
    {
        "audit_only",
        "candidate_needs_evidence",
        "blocked_by_unknown_operation",
        "blocked_by_value_normalization",
        "blocked_by_stat_identity",
        "blocked_by_missing_baseline",
        "blocked_by_conditional_behavior",
        "blocked_by_unsupported_behavior",
        "planner_semantics_experimental",
        "planner_semantics_stable",
    }
)

CURRENT_CLASSIFICATIONS = frozenset(
    {
        "audit_only",
        "candidate_needs_evidence",
        "blocked_by_unknown_operation",
        "blocked_by_value_normalization",
        "blocked_by_stat_identity",
        "blocked_by_missing_baseline",
        "blocked_by_conditional_behavior",
        "blocked_by_unsupported_behavior",
        "unknown_needs_review",
    }
)


def build_v3_operation_semantics_taxonomy_report(*, root: str | Path | None = None) -> dict[str, Any]:
    repo_root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    generated = repo_root / "docs" / "generated"
    dry_run = _read_json(generated / "v2_stat_modifier_dry_run_report.json")
    value_contract = _read_json(generated / "v3_value_normalization_contract_report.json")
    v3_plan = _read_json(generated / "v3_mechanical_intelligence_plan.json")

    operation_distribution = dry_run.get("operation_distribution", {})
    operation_families = _operation_families(operation_distribution)
    safety = {
        "operation_semantics_implemented": False,
        "modifier_calculations_changed": False,
        "values_normalized": False,
        "stable_calculable_promoted": False,
        "planner_calculable_promoted": False,
        "production_consumed": False,
        "production_planner_changed": False,
        "unknown_operations_blocked": True,
        "value_normalization_status": "audit_only",
        "unresolved_stat_identities_blocked": True,
        "unsupported_scripted_behavior_excluded": True,
        "planner_calculable_count": 0,
        "stable_calculable_count": 0,
        "skill_identity_bridge_status": "unbridged",
        "skill_identity_bridge_added": False,
    }

    return {
        "schema_version": "v3.operation_semantics_taxonomy.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "current_operation_distribution": {
            "modifier_row_count": dry_run.get("summary", {}).get("modifier_row_count"),
            "blocked_modifier_count": dry_run.get("summary", {}).get("blocked_modifier_count"),
            "operation_distribution": operation_distribution,
            "unknown_operation_count": operation_distribution.get("unknown", 0),
            "planner_calculable_count": dry_run.get("summary", {}).get("planner_calculable_modifier_count"),
            "stable_calculable_count": dry_run.get("summary", {}).get("stable_calculable_modifier_count"),
        },
        "operation_families": operation_families,
        "known_operation_families": [item for item in operation_families if item["current_count"] > 0 and item["operation_id"] != "unknown"],
        "unknown_operation_count": operation_distribution.get("unknown", 0),
        "blocked_operation_categories": _blocked_operation_categories(dry_run=dry_run, value_contract=value_contract),
        "semantic_contract_fields": list(SEMANTIC_CONTRACT_FIELDS),
        "required_evidence_before_promotion": _required_evidence(),
        "dependencies": {
            "value_normalization": {
                "required": True,
                "status": value_contract.get("safety_confirmations", {}).get("value_normalization_status", "audit_only"),
                "reason": "operation semantics cannot affect planner math until value scale treatment is approved",
            },
            "stat_identity": {
                "required": True,
                "unresolved_stat_identity_count": dry_run.get("stat_identity_findings", {}).get("unknown"),
                "reason": "operation semantics must target resolved canonical stats",
            },
            "unsupported_scripted_behavior_exclusions": {
                "required": True,
                "counts": dry_run.get("unsupported_scripted_text_only_counts", {}),
                "reason": "scripted, text-only, and unsupported mechanics remain excluded unless explicitly modeled",
            },
        },
        "required_golden_baseline_coverage": _required_golden_baselines(),
        "allowed_promotion_states": sorted(PROMOTION_STATES),
        "disallowed_assumptions": _disallowed_assumptions(),
        "future_sequence": _future_sequence(),
        "recommended_next_phase": "v3_stat_identity_resolution_policy",
        "source_report_evidence": {
            "value_contract_recommended_next_phase": value_contract.get("recommended_next_phase"),
            "v3_plan_recommended_sequence": v3_plan.get("recommended_v3_phase_sequence", []),
            "dry_run_comparison_category_summary": dry_run.get("comparison_category_summary", {}),
        },
        "safety_confirmations": safety,
        "metadata": {
            "source": "v3_operation_semantics_taxonomy",
            "design_only": True,
            "operation_semantics_implemented": False,
            "production_consumed": False,
            "planner_remap_performed": False,
        },
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    distribution = report["current_operation_distribution"]
    safety = report["safety_confirmations"]
    lines = [
        "# V3 Operation Semantics Taxonomy",
        "",
        "This document defines the operation semantics taxonomy contract.",
        "It does not implement operation calculations, stat math, value normalization, or planner output changes.",
        "",
        "## Current Operation Distribution",
        "",
    ]
    for operation, count in sorted(distribution["operation_distribution"].items()):
        lines.append(f"- `{operation}`: `{count}`")
    lines.extend(["", "## Operation Families", "", "| Operation | Classification | Count | Promotion |", "| --- | --- | ---: | --- |"])
    for family in report["operation_families"]:
        lines.append(
            f"| `{family['operation_id']}` | `{family['classification']}` | `{family['current_count']}` | `{family['promotion_status']}` |"
        )
    lines.extend(["", "## Semantic Contract Fields", ""])
    lines.extend(f"- `{field}`" for field in report["semantic_contract_fields"])
    lines.extend(["", "## Allowed Promotion States", ""])
    lines.extend(f"- `{state}`" for state in report["allowed_promotion_states"])
    lines.extend(["", "## Evidence Requirements", ""])
    lines.extend(f"- `{item['id']}`: {item['description']}" for item in report["required_evidence_before_promotion"])
    lines.extend(["", "## Disallowed Assumptions", ""])
    lines.extend(f"- {item}" for item in report["disallowed_assumptions"])
    lines.extend(["", "## Future Sequence", "", "| Order | Step |", "| ---: | --- |"])
    for step in report["future_sequence"]:
        lines.append(f"| `{step['order']}` | {step['description']} |")
    lines.extend(["", "## Safety Confirmations", ""])
    lines.extend(
        [
            f"- Operation semantics implemented: `{str(safety['operation_semantics_implemented']).lower()}`",
            f"- Modifier calculations changed: `{str(safety['modifier_calculations_changed']).lower()}`",
            f"- Values normalized: `{str(safety['values_normalized']).lower()}`",
            f"- Stable-calculable promoted: `{str(safety['stable_calculable_promoted']).lower()}`",
            f"- Planner-calculable promoted: `{str(safety['planner_calculable_promoted']).lower()}`",
            f"- Production consumed: `{str(safety['production_consumed']).lower()}`",
            f"- Unknown operations blocked: `{str(safety['unknown_operations_blocked']).lower()}`",
            f"- Value normalization: `{safety['value_normalization_status']}`",
            f"- Unresolved stat identities blocked: `{str(safety['unresolved_stat_identities_blocked']).lower()}`",
            f"- Unsupported/scripted behavior excluded: `{str(safety['unsupported_scripted_behavior_excluded']).lower()}`",
        ]
    )
    lines.extend(["", "## Recommended Next Phase", "", f"`{report['recommended_next_phase']}`"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _operation_families(operation_distribution: dict[str, int]) -> list[dict[str, Any]]:
    families: list[dict[str, Any]] = []
    for operation in REQUIRED_OPERATION_FAMILIES:
        count = int(operation_distribution.get(operation, 0) or 0)
        if operation == "unknown":
            classification = "blocked_by_unknown_operation"
            promotion = "blocked_by_unknown_operation"
            blocked = ["unknown_operation"]
        elif operation in {"threshold", "conditional"}:
            classification = "blocked_by_conditional_behavior"
            promotion = "blocked_by_conditional_behavior"
            blocked = ["conditional_behavior_not_modeled", "missing_golden_baseline"]
        elif count == 0:
            classification = "audit_only"
            promotion = "audit_only"
            blocked = ["not_present_in_current_distribution", "missing_golden_baseline"]
        elif operation in {"flat", "increased", "more", "duration", "cost", "cooldown", "chance", "conversion"}:
            classification = "candidate_needs_evidence"
            promotion = "candidate_needs_evidence"
            blocked = ["value_normalization_audit_only", "missing_operation_baseline", "stat_identity_dependency"]
        else:
            classification = "unknown_needs_review"
            promotion = "audit_only"
            blocked = ["unknown_needs_review"]
        families.append(
            {
                "operation_id": operation,
                "operation_label": operation.replace("_", " ").title(),
                "current_count": count,
                "classification": classification,
                "promotion_status": promotion,
                "planner_semantics_safe": False,
                "blocked_reasons": blocked,
                "requires_value_normalization": operation != "unknown",
                "requires_stat_identity": operation != "unknown",
                "requires_golden_baseline": True,
            }
        )
    return families


def _blocked_operation_categories(*, dry_run: dict[str, Any], value_contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"id": "unknown_operations", "count": dry_run.get("operation_distribution", {}).get("unknown", 0), "classification": "blocked_by_unknown_operation"},
        {"id": "value_normalization_audit_only", "count": dry_run.get("summary", {}).get("blocked_modifier_count", 0), "classification": "blocked_by_value_normalization"},
        {"id": "unresolved_stat_identities", "count": dry_run.get("stat_identity_findings", {}).get("unknown", 0), "classification": "blocked_by_stat_identity"},
        {"id": "missing_operation_baselines", "count": len(REQUIRED_OPERATION_FAMILIES), "classification": "blocked_by_missing_baseline"},
        {
            "id": "source_units_and_unknown_values",
            "count": (
                value_contract.get("current_value_scale_state", {}).get("source_units_value_scale_count", 0)
                + value_contract.get("current_value_scale_state", {}).get("unknown_value_scale_count", 0)
            ),
            "classification": "blocked_by_value_normalization",
        },
        {"id": "unsupported_scripted_text_only_behavior", "count": dry_run.get("blocked_reason_counts", {}).get("unsupported_behavior", 0), "classification": "blocked_by_unsupported_behavior"},
    ]


def _required_evidence() -> list[dict[str, str]]:
    return [
        {"id": "source_operation_examples", "description": "Representative source rows for each operation label."},
        {"id": "expected_planner_interpretation", "description": "Plain semantic meaning approved before calculation use."},
        {"id": "resolved_stat_identity", "description": "Canonical target stat identities for the operation domain."},
        {"id": "normalized_or_scale_independent_value", "description": "Value scale normalized or explicitly proven scale-independent."},
        {"id": "stacking_behavior", "description": "Known stacking and ordering behavior."},
        {"id": "polarity_behavior", "description": "Known positive, negative, inverse, and reduction semantics."},
        {"id": "conditional_behavior_policy", "description": "Conditional behavior either excluded or modeled with proof."},
        {"id": "golden_baseline_coverage", "description": "Representative old planner and operation-specific baselines."},
        {"id": "dry_run_comparison_result", "description": "Candidate output compared without production consumption."},
        {"id": "provenance_patch_traceability", "description": "Source path, bundle provenance, and patch/export version."},
    ]


def _required_golden_baselines() -> list[str]:
    return [
        "flat operation examples",
        "increased operation examples",
        "more/less operation examples",
        "duration/cooldown/cost operation examples",
        "chance operation examples",
        "conditional and threshold exclusion examples",
        "unknown operation blocked examples",
        "old planner versus dry-run operation comparison snapshots",
    ]


def _disallowed_assumptions() -> list[str]:
    return [
        "Do not infer operation semantics from tooltip text.",
        "Do not treat structural operation labels as planner-safe semantics.",
        "Do not assume flat, increased, and more share stacking behavior.",
        "Do not treat unknown operations as no-op or flat operations.",
        "Do not model conditional behavior without explicit policy and baselines.",
        "Do not promote operations while value normalization remains audit-only.",
        "Do not bridge unresolved skill identities to make operation semantics pass.",
    ]


def _future_sequence() -> list[dict[str, Any]]:
    return [
        {"order": 1, "description": "Classify source operation labels."},
        {"order": 2, "description": "Identify one narrow operation candidate."},
        {"order": 3, "description": "Confirm stat identity requirements."},
        {"order": 4, "description": "Confirm value normalization dependency."},
        {"order": 5, "description": "Define stacking and polarity semantics."},
        {"order": 6, "description": "Create operation golden baseline."},
        {"order": 7, "description": "Run dry-run comparison."},
        {"order": 8, "description": "Mark experimental only after evidence passes."},
        {"order": 9, "description": "Promote stable only after repeated validation."},
    ]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_operation_semantics_taxonomy_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_OPERATION_SEMANTICS_TAXONOMY.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_operation_semantics_taxonomy_report(root=repo_root)
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["current_operation_distribution"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
