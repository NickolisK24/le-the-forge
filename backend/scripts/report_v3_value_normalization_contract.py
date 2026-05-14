"""Generate the v3 value normalization contract design audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REQUIRED_CONTRACT_FIELDS = (
    "family_id",
    "source_scale",
    "target_scale",
    "domain",
    "operation_type",
    "stat_identity_status",
    "value_transform_rule",
    "unit_semantics",
    "polarity_semantics",
    "rounding_policy",
    "stacking_policy_dependency",
    "applicability_scope",
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
        "blocked_by_unknown_scale",
        "blocked_by_source_units",
        "blocked_by_operation_semantics",
        "blocked_by_stat_identity",
        "blocked_by_missing_baseline",
        "blocked_by_behavioral_risk",
        "planner_normalized_experimental",
        "planner_normalized_stable",
    }
)

CURRENT_CLASSIFICATIONS = frozenset(
    {
        "audit_only",
        "candidate_needs_evidence",
        "blocked_by_unknown_scale",
        "blocked_by_source_units",
        "blocked_by_operation_semantics",
        "blocked_by_stat_identity",
        "blocked_by_missing_baseline",
        "blocked_by_behavioral_risk",
        "unknown_needs_review",
    }
)


def build_v3_value_normalization_contract_report(*, root: str | Path | None = None) -> dict[str, Any]:
    repo_root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    generated = repo_root / "docs" / "generated"
    dry_run = _read_json(generated / "v2_stat_modifier_dry_run_report.json")
    policy_report = _read_json(generated / "v2_value_normalization_policy_report.json")
    candidate_report = _read_json(generated / "v2_value_normalization_candidate_families.json")
    v3_plan = _read_json(generated / "v3_mechanical_intelligence_plan.json")

    dry_summary = dry_run.get("summary", {})
    value_scale_distribution = dry_run.get("value_scale_distribution", {})
    candidate_families = candidate_report.get("candidate_families", [])
    blocked_families = policy_report.get("blocked_families", [])
    family_classifications = _family_classifications(
        candidate_families=candidate_families,
        blocked_families=blocked_families,
        dry_run=dry_run,
    )
    safety = {
        "values_normalized": False,
        "stable_calculable_promoted": False,
        "planner_calculable_promoted": False,
        "production_consumed": False,
        "production_planner_changed": False,
        "value_normalization_status": "audit_only",
        "unknown_values_blocked": True,
        "source_units_values_blocked": True,
        "unknown_operations_blocked": True,
        "unresolved_stat_identities_blocked": True,
        "stable_calculable_count": 0,
        "planner_calculable_count": 0,
        "skill_identity_bridge_status": "unbridged",
        "skill_identity_bridge_added": False,
    }

    return {
        "schema_version": "v3.value_normalization_contract.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "current_value_scale_state": {
            "modifier_row_count": dry_summary.get("modifier_row_count"),
            "blocked_modifier_count": dry_summary.get("blocked_modifier_count"),
            "planner_calculable_count": dry_summary.get("planner_calculable_modifier_count"),
            "stable_calculable_count": dry_summary.get("stable_calculable_modifier_count"),
            "value_normalization_status": dry_summary.get("value_normalization_status"),
            "value_scale_distribution": value_scale_distribution,
            "source_units_value_scale_count": dry_summary.get("source_unit_value_scale_count"),
            "unknown_value_scale_count": dry_summary.get("unknown_value_scale_count"),
            "unknown_operation_count": dry_run.get("operation_distribution", {}).get("unknown"),
            "unresolved_stat_identity_count": dry_run.get("stat_identity_findings", {}).get("unknown"),
        },
        "value_family_candidates": _candidate_summary(candidate_report),
        "blocked_family_counts": {
            "candidate_family_count": candidate_report.get("summary", {}).get("candidate_family_count", 0),
            "safe_family_count": candidate_report.get("summary", {}).get("safe_family_count", 0),
            "blocked_family_count": len(blocked_families),
            "classification_counts": _classification_counts(family_classifications),
        },
        "required_contract_fields": list(REQUIRED_CONTRACT_FIELDS),
        "required_evidence_before_promotion": _required_evidence(),
        "required_golden_baseline_coverage": _required_golden_baselines(),
        "required_operation_semantics_dependency": {
            "required": True,
            "reason": "value transforms cannot be approved until operation meaning and stacking are defined",
            "current_unknown_operation_count": dry_run.get("operation_distribution", {}).get("unknown"),
        },
        "required_stat_identity_dependency": {
            "required": True,
            "reason": "value transforms must target resolved canonical stat identities",
            "current_unresolved_stat_identity_count": dry_run.get("stat_identity_findings", {}).get("unknown"),
        },
        "allowed_promotion_states": sorted(PROMOTION_STATES),
        "current_family_classifications": family_classifications,
        "disallowed_assumptions": _disallowed_assumptions(),
        "production_remap_blockers": _production_remap_blockers(dry_run=dry_run, v3_plan=v3_plan),
        "future_sequence": _future_sequence(),
        "recommended_next_phase": "v3_operation_semantics_taxonomy",
        "safety_confirmations": safety,
        "metadata": {
            "source": "v3_value_normalization_contract",
            "design_only": True,
            "normalization_implemented": False,
            "production_consumed": False,
            "planner_remap_performed": False,
        },
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    state = report["current_value_scale_state"]
    safety = report["safety_confirmations"]
    lines = [
        "# V3 Value Normalization Contract",
        "",
        "This document defines the design contract for future value normalization.",
        "It does not convert values, promote records, or change planner output.",
        "",
        "## Current Blocker State",
        "",
        f"- Modifier rows: `{state['modifier_row_count']}`",
        f"- Blocked modifier rows: `{state['blocked_modifier_count']}`",
        f"- Planner-calculable count: `{state['planner_calculable_count']}`",
        f"- Stable-calculable count: `{state['stable_calculable_count']}`",
        f"- Value normalization: `{state['value_normalization_status']}`",
        f"- Source-unit values: `{state['source_units_value_scale_count']}`",
        f"- Unknown values: `{state['unknown_value_scale_count']}`",
        f"- Unknown operations: `{state['unknown_operation_count']}`",
        f"- Unresolved stat identities: `{state['unresolved_stat_identity_count']}`",
        "",
        "## Required Contract Fields",
        "",
    ]
    lines.extend(f"- `{field}`" for field in report["required_contract_fields"])
    lines.extend(["", "## Allowed Promotion States", ""])
    lines.extend(f"- `{state_name}`" for state_name in report["allowed_promotion_states"])
    lines.extend(["", "## Evidence Requirements", ""])
    lines.extend(f"- `{item['id']}`: {item['description']}" for item in report["required_evidence_before_promotion"])
    lines.extend(["", "## Family Classifications", "", "| Family | Classification | Count |", "| --- | --- | ---: |"])
    for item in report["current_family_classifications"]:
        lines.append(f"| `{item['family_id']}` | `{item['classification']}` | `{item['modifier_count']}` |")
    lines.extend(["", "## Disallowed Assumptions", ""])
    lines.extend(f"- {item}" for item in report["disallowed_assumptions"])
    lines.extend(["", "## Future Sequence", "", "| Order | Step |", "| ---: | --- |"])
    for step in report["future_sequence"]:
        lines.append(f"| `{step['order']}` | {step['description']} |")
    lines.extend(["", "## Safety Confirmations", ""])
    lines.extend(
        [
            f"- Values normalized: `{str(safety['values_normalized']).lower()}`",
            f"- Stable-calculable promoted: `{str(safety['stable_calculable_promoted']).lower()}`",
            f"- Planner-calculable promoted: `{str(safety['planner_calculable_promoted']).lower()}`",
            f"- Production consumed: `{str(safety['production_consumed']).lower()}`",
            f"- Value normalization status: `{safety['value_normalization_status']}`",
            f"- Unknown values blocked: `{str(safety['unknown_values_blocked']).lower()}`",
            f"- Source-unit values blocked: `{str(safety['source_units_values_blocked']).lower()}`",
            f"- Unknown operations blocked: `{str(safety['unknown_operations_blocked']).lower()}`",
            f"- Unresolved stat identities blocked: `{str(safety['unresolved_stat_identities_blocked']).lower()}`",
        ]
    )
    lines.extend(["", "## Recommended Next Phase", "", f"`{report['recommended_next_phase']}`"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _candidate_summary(candidate_report: dict[str, Any]) -> dict[str, Any]:
    candidates = candidate_report.get("candidate_families", [])
    return {
        "candidate_family_count": candidate_report.get("summary", {}).get("candidate_family_count", 0),
        "safe_family_count": candidate_report.get("summary", {}).get("safe_family_count", 0),
        "sample_candidates": [
            {
                "family_id": item.get("family_key"),
                "modifier_count": item.get("modifier_count"),
                "operation": item.get("operation"),
                "source_type": item.get("source_type"),
                "stat_family": item.get("stat_family"),
                "value_scale_counts": item.get("value_scale_counts", {}),
                "policy_status": item.get("policy_status"),
                "blocked_reasons": item.get("blocked_reasons", []),
            }
            for item in candidates[:10]
        ],
    }


def _family_classifications(
    *,
    candidate_families: list[dict[str, Any]],
    blocked_families: list[dict[str, Any]],
    dry_run: dict[str, Any],
) -> list[dict[str, Any]]:
    classifications: list[dict[str, Any]] = [
        {
            "family_id": "all_unknown_value_scales",
            "classification": "blocked_by_unknown_scale",
            "modifier_count": dry_run.get("summary", {}).get("unknown_value_scale_count", 0),
            "promotion_state": "blocked_by_unknown_scale",
            "blocked_reasons": ["unknown_value_scale"],
        },
        {
            "family_id": "all_source_units_value_scales",
            "classification": "blocked_by_source_units",
            "modifier_count": dry_run.get("summary", {}).get("source_unit_value_scale_count", 0),
            "promotion_state": "blocked_by_source_units",
            "blocked_reasons": ["source_units_value_scale", "missing_explicit_scale_evidence"],
        },
        {
            "family_id": "unknown_operations",
            "classification": "blocked_by_operation_semantics",
            "modifier_count": dry_run.get("operation_distribution", {}).get("unknown", 0),
            "promotion_state": "blocked_by_operation_semantics",
            "blocked_reasons": ["unknown_operation"],
        },
        {
            "family_id": "unresolved_stat_identities",
            "classification": "blocked_by_stat_identity",
            "modifier_count": dry_run.get("stat_identity_findings", {}).get("unknown", 0),
            "promotion_state": "blocked_by_stat_identity",
            "blocked_reasons": ["unresolved_stat_identity"],
        },
    ]
    for item in candidate_families[:8]:
        classifications.append(
            {
                "family_id": item.get("family_key"),
                "classification": "candidate_needs_evidence",
                "modifier_count": item.get("modifier_count", 0),
                "promotion_state": "candidate_needs_evidence",
                "blocked_reasons": item.get("blocked_reasons", ["missing_explicit_scale_evidence"]),
            }
        )
    for item in blocked_families[:4]:
        reasons = item.get("blocked_reasons", [])
        if "unknown_value_scale" in reasons:
            classification = "blocked_by_unknown_scale"
            promotion_state = "blocked_by_unknown_scale"
        elif "unknown_operation" in reasons:
            classification = "blocked_by_operation_semantics"
            promotion_state = "blocked_by_operation_semantics"
        elif "unknown_stat_id" in reasons:
            classification = "blocked_by_stat_identity"
            promotion_state = "blocked_by_stat_identity"
        else:
            classification = "blocked_by_behavioral_risk"
            promotion_state = "blocked_by_behavioral_risk"
        classifications.append(
            {
                "family_id": item.get("family_key"),
                "classification": classification,
                "modifier_count": item.get("modifier_count", 0),
                "promotion_state": promotion_state,
                "blocked_reasons": reasons,
            }
        )
    return classifications


def _required_evidence() -> list[dict[str, str]]:
    return [
        {"id": "source_examples", "description": "Representative source records for the family."},
        {"id": "known_raw_value_examples", "description": "Raw min/max values from trusted source data."},
        {"id": "expected_normalized_value_examples", "description": "Expected planner values approved by policy and baseline evidence."},
        {"id": "operation_semantics", "description": "Approved operation meaning, stacking, and scope."},
        {"id": "resolved_stat_identity", "description": "Canonical stat identity resolved for the target domain."},
        {"id": "golden_baseline_test", "description": "Existing planner output or explicit mechanical baseline."},
        {"id": "old_planner_comparison", "description": "Dry-run comparison against current planner output where applicable."},
        {"id": "unsupported_exclusion", "description": "Proof that scripted and unsupported mechanics remain excluded."},
        {"id": "provenance_source", "description": "Traceable source path and generated bundle provenance."},
        {"id": "patch_version_traceability", "description": "Patch/export version associated with the evidence."},
    ]


def _required_golden_baselines() -> list[str]:
    return [
        "value scale examples for each proposed family",
        "operation examples for flat, increased, more, less, duration, cooldown, cost, and chance",
        "known item affix stat output",
        "known passive node stat output",
        "known skill node stat output",
        "unsupported unique/set exclusion snapshots",
        "old planner versus v3 dry-run comparison snapshots",
    ]


def _disallowed_assumptions() -> list[str]:
    return [
        "Do not infer value scale from display text.",
        "Do not infer value scale from tooltip text.",
        "Do not treat source_units as planner-normalized.",
        "Do not treat unknown values as zero or identity values.",
        "Do not assume percent-like operations use the same transform family.",
        "Do not promote a family without operation semantics and stat identity evidence.",
        "Do not bridge unresolved skill identities to make value normalization pass.",
    ]


def _production_remap_blockers(*, dry_run: dict[str, Any], v3_plan: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"id": "value_normalization_audit_only", "evidence": dry_run.get("summary", {}).get("value_normalization_status")},
        {"id": "unknown_value_scales", "evidence": dry_run.get("summary", {}).get("unknown_value_scale_count")},
        {"id": "source_units_value_scales", "evidence": dry_run.get("summary", {}).get("source_unit_value_scale_count")},
        {"id": "unknown_operations", "evidence": dry_run.get("operation_distribution", {}).get("unknown")},
        {"id": "unresolved_stat_identities", "evidence": dry_run.get("stat_identity_findings", {}).get("unknown")},
        {"id": "missing_production_remap_gates", "evidence": v3_plan.get("production_remap_readiness", {}).get("blocked_by", [])},
    ]


def _future_sequence() -> list[dict[str, Any]]:
    return [
        {"order": 1, "description": "Define operation semantics taxonomy."},
        {"order": 2, "description": "Define stat identity resolution policy."},
        {"order": 3, "description": "Select one narrow value family candidate."},
        {"order": 4, "description": "Gather raw source examples."},
        {"order": 5, "description": "Define transform rule."},
        {"order": 6, "description": "Create golden baseline."},
        {"order": 7, "description": "Run dry-run comparison."},
        {"order": 8, "description": "Mark experimental only after evidence passes."},
        {"order": 9, "description": "Promote stable only after repeated validation."},
    ]


def _classification_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(item.get("classification") or "unknown_needs_review") for item in items)
    return {key: counts[key] for key in sorted(counts)}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_value_normalization_contract_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_VALUE_NORMALIZATION_CONTRACT.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_value_normalization_contract_report(root=repo_root)
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["current_value_scale_state"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
