"""Developer-only context coverage report for bundle item type dry-run resolution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.game_data.bundle_item_type_dry_run_resolver import (
    BundleItemTypeDryRunResolver,
    DryRunResolution,
    summarize_resolutions,
)


COLLAPSED_GROUP_REASONS = {
    "axe": "Forge slug collapses one-handed/two-handed bundle distinctions.",
    "mace": "Forge slug collapses one-handed/two-handed bundle distinctions.",
    "sword": "Forge slug collapses one-handed/two-handed bundle distinctions.",
    "idol_1x1": "Forge idol shape alias collapses Eterra/Lagon bundle distinctions.",
}


@dataclass(frozen=True)
class ContextInput:
    forge_item_type: str
    base_type_id: int | None = None
    subtype_id: int | None = None
    source: str = "sample"

    def to_dict(self) -> dict[str, Any]:
        return {
            "forge_item_type": self.forge_item_type,
            "base_type_id": self.base_type_id,
            "subtype_id": self.subtype_id,
            "source": self.source,
        }


def build_current_forge_context_inputs() -> list[ContextInput]:
    from app.constants.base_type_id_to_item_type_id import BASE_TYPE_ID_TO_ITEM_TYPE_ID
    from app.constants.item_type_ids import ITEM_TYPE_IDS

    inputs = [
        ContextInput(
            forge_item_type=forge_item_type,
            base_type_id=int(base_type_id),
            source="BASE_TYPE_ID_TO_ITEM_TYPE_ID",
        )
        for base_type_id, forge_item_type in sorted(BASE_TYPE_ID_TO_ITEM_TYPE_ID.items())
    ]
    inputs.extend(
        ContextInput(forge_item_type=forge_item_type, source="ITEM_TYPE_IDS")
        for forge_item_type in sorted(set(ITEM_TYPE_IDS))
    )
    return inputs


def build_context_coverage_report(
    inputs: list[ContextInput] | None = None,
    resolver: BundleItemTypeDryRunResolver | None = None,
) -> dict[str, Any]:
    resolver = resolver or BundleItemTypeDryRunResolver()
    inputs = inputs if inputs is not None else build_current_forge_context_inputs()
    results = [
        resolver.resolve(item.forge_item_type, item.base_type_id, item.subtype_id)
        for item in inputs
    ]
    summary = summarize_resolutions(results)
    missing_context = [
        (item, result)
        for item, result in zip(inputs, results)
        if item.base_type_id is None and result.status == "needs_context"
    ]
    with_context = [item for item in inputs if item.base_type_id is not None]
    needs_review = [
        (item, result)
        for item, result in zip(inputs, results)
        if result.status == "needs_review"
    ]
    collapsed_groups = _collapsed_groups(inputs, results)

    return {
        "production_safe": False,
        "total_inputs": len(inputs),
        "with_base_type_id": len(with_context),
        "missing_base_type_id": len(missing_context),
        "status_counts": summary["counts"],
        "collapsed_groups": collapsed_groups,
        "needs_context_examples": _example_results(missing_context),
        "resolved_examples": _example_results(
            [
                (item, result)
                for item, result in zip(inputs, results)
                if result.status == "resolved"
            ]
        ),
        "needs_review_examples": _example_results(needs_review),
        "subtype_id_only_matching_attempted": summary["subtype_id_only_matching_attempted"],
        "recommendations": _recommendations(missing_context, collapsed_groups, needs_review),
    }


def render_context_coverage_report(report: dict[str, Any]) -> str:
    lines = [
        "# Bundle Item Type Context Coverage Report",
        "",
        "- production_safe: false",
        f"- total inputs: {report['total_inputs']}",
        f"- with base_type_id: {report['with_base_type_id']}",
        f"- missing base_type_id: {report['missing_base_type_id']}",
        "",
        "## Resolver Status Counts",
        "",
    ]
    for status, count in report["status_counts"].items():
        lines.append(f"- {status}: {count}")
    lines.extend(["", "## Collapsed Groups Requiring Context", ""])
    for group in report["collapsed_groups"] or [{"forge_item_type": "none", "reason": "none", "examples": []}]:
        lines.append(f"- {group['forge_item_type']}: {group['reason']}")
        for example in group.get("examples", [])[:5]:
            lines.append(f"  - {example}")
    lines.extend(["", "## Needs Context Examples", ""])
    lines.extend(_format_examples(report["needs_context_examples"]))
    lines.extend(["", "## Resolved Examples", ""])
    lines.extend(_format_examples(report["resolved_examples"]))
    lines.extend(["", "## Needs Review Examples", ""])
    lines.extend(_format_examples(report["needs_review_examples"]))
    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in report["recommendations"])
    lines.append("")
    return "\n".join(lines)


def _collapsed_groups(inputs: list[ContextInput], results: list[DryRunResolution]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    by_type = {item_type: [] for item_type in COLLAPSED_GROUP_REASONS}
    for item, result in zip(inputs, results):
        if item.forge_item_type in by_type and result.status in {"resolved", "needs_context"}:
            by_type[item.forge_item_type].append(
                f"{item.forge_item_type} base_type_id={item.base_type_id} status={result.status}"
            )
    for item_type, examples in by_type.items():
        if examples:
            groups.append(
                {
                    "forge_item_type": item_type,
                    "reason": COLLAPSED_GROUP_REASONS[item_type],
                    "required_context": ["base_type_id"],
                    "examples": examples,
                }
            )
    return groups


def _example_results(pairs: list[tuple[ContextInput, DryRunResolution]], limit: int = 10) -> list[dict[str, Any]]:
    return [
        {
            **item.to_dict(),
            "status": result.status,
            "bundle_item_type_id": result.bundle_item_type_id,
            "match_source": result.match_source,
            "production_safe": result.production_safe,
            "warnings": result.warnings,
        }
        for item, result in pairs[:limit]
    ]


def _format_examples(examples: list[dict[str, Any]]) -> list[str]:
    if not examples:
        return ["- none"]
    return [
        f"- forge={item['forge_item_type']} base_type_id={item['base_type_id']} "
        f"source={item['source']} status={item['status']} bundle={item['bundle_item_type_id'] or 'null'}"
        for item in examples
    ]


def _recommendations(
    missing_context: list[tuple[ContextInput, DryRunResolution]],
    collapsed_groups: list[dict[str, Any]],
    needs_review: list[tuple[ContextInput, DryRunResolution]],
) -> list[str]:
    recommendations = [
        "Thread base_type_id through any developer consumer before resolving canonical bundle item_type IDs.",
        "Keep production_safe=false until a separate migration defines fallback behavior and consumer tests.",
    ]
    if missing_context:
        recommendations.append("Do not resolve missing-context inputs from Forge slug alone.")
    if collapsed_groups:
        recommendations.append("Preserve collapsed weapon/idol distinctions by requiring base_type_id context.")
    if needs_review:
        recommendations.append("Review blocked inputs such as spear before adding any translation.")
    return recommendations
