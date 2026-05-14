"""Generate read-only slot vocabulary policy for Forge-safe candidates."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SLOT_EQUIVALENCE = (
    ROOT / "docs" / "generated" / "forge_safe_slot_vocabulary_equivalence.json"
)
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "forge_safe_slot_vocabulary_policy.json"
DEFAULT_MARKDOWN_OUTPUT = (
    ROOT / "docs" / "migration" / "FORGE_SAFE_SLOT_VOCABULARY_POLICY.md"
)

PURE = "pure_vocabulary_difference"
BLOCKED = "blocked_by_slot_applicability"
NEEDS_REVIEW = "needs_manual_review"
APPROVED_POLICY = "policy_approved_for_test_adapter"
BLOCKED_POLICY = "blocked_by_inconsistent_applicability"
MANUAL_REVIEW_POLICY = "manual_review_required"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a read-only slot vocabulary policy artifact."
    )
    parser.add_argument("--slot-equivalence", type=Path, default=DEFAULT_SLOT_EQUIVALENCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args()


def load_slot_equivalence(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("slot equivalence report must be a JSON object")
    metadata = payload.get("metadata") or {}
    if metadata.get("production_safe") is not False:
        raise ValueError("slot equivalence report must be production_safe=false")
    if metadata.get("read_only") is not True:
        raise ValueError("slot equivalence report must be read_only=true")
    return payload


def build_slot_policy(report: dict[str, Any], *, source_path: str) -> dict[str, Any]:
    approved = []
    blocked = []
    manual_review = []

    for candidate in report.get("candidate_slot_statuses") or []:
        status = candidate.get("slot_status")
        if status == PURE:
            approved.append(policy_approved_candidate(candidate))
        elif status == BLOCKED:
            blocked.append(blocked_candidate(candidate))
        elif status == NEEDS_REVIEW:
            manual_review.append(manual_review_candidate(candidate))

    summary = {
        "candidate_count": len(approved) + len(blocked) + len(manual_review),
        "policy_approved_slot_candidate_count": len(approved),
        "slot_blocked_candidate_count": len(blocked),
        "needs_manual_review_count": len(manual_review),
        "production_consumed": False,
    }

    return {
        "summary": summary,
        "policy_approved_candidates": sorted(
            approved, key=lambda item: item["legacy_stat_key"]
        ),
        "blocked_candidates": sorted(
            blocked, key=lambda item: item["legacy_stat_key"]
        ),
        "manual_review_candidates": sorted(
            manual_review, key=lambda item: item["legacy_stat_key"]
        ),
        "metadata": {
            "source": "forge_safe_slot_vocabulary_equivalence",
            "source_path": source_path,
            "read_only": True,
            "candidate_only": True,
            "experimental": True,
            "production_consumer": False,
            "production_safe": False,
            "consumption_status": "not_consumed",
            "value_scale_status": "unresolved",
        },
    }


def policy_approved_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "legacy_stat_key": candidate.get("legacy_stat_key"),
        "slot_policy_status": APPROVED_POLICY,
        "legacy_slot_values": list(candidate.get("legacy_slot_values") or []),
        "bundle_item_values": list(candidate.get("bundle_item_values") or []),
        "legacy_slot_sets": list(candidate.get("legacy_slot_sets") or []),
        "bundle_item_sets": list(candidate.get("bundle_item_sets") or []),
        "affix_count": candidate.get("affix_count", 0),
        "example_affix_ids": list(candidate.get("example_affix_ids") or []),
        "consumption_status": "not_consumed",
        "notes": [
            "Approved only as a slot-vocabulary policy candidate for future test-only adapter work.",
            "Value-scale blockers remain unresolved.",
            "Not approved for production consumption.",
        ],
    }


def blocked_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    legacy_stat_key = candidate.get("legacy_stat_key")
    notes = [
        "Blocked from initial adapter subset because applicability evidence is inconsistent.",
        "Requires manual policy decision or source audit.",
        "Must not be included in any initial adapter subset.",
    ]
    if legacy_stat_key == "health_on_kill":
        notes.insert(
            0,
            "health_on_kill remains blocked while the input report classifies it as blocked_by_slot_applicability.",
        )
    return {
        "legacy_stat_key": legacy_stat_key,
        "slot_policy_status": BLOCKED_POLICY,
        "legacy_slot_values": list(candidate.get("legacy_slot_values") or []),
        "bundle_item_values": list(candidate.get("bundle_item_values") or []),
        "legacy_slot_sets": list(candidate.get("legacy_slot_sets") or []),
        "bundle_item_sets": list(candidate.get("bundle_item_sets") or []),
        "affix_count": candidate.get("affix_count", 0),
        "example_affix_ids": list(candidate.get("example_affix_ids") or []),
        "required_resolution": "manual_policy_decision_or_source_audit",
        "consumption_status": "not_consumed",
        "notes": notes,
    }


def manual_review_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "legacy_stat_key": candidate.get("legacy_stat_key"),
        "slot_policy_status": MANUAL_REVIEW_POLICY,
        "legacy_slot_values": list(candidate.get("legacy_slot_values") or []),
        "bundle_item_values": list(candidate.get("bundle_item_values") or []),
        "affix_count": candidate.get("affix_count", 0),
        "example_affix_ids": list(candidate.get("example_affix_ids") or []),
        "required_resolution": "complete_slot_evidence_review",
        "consumption_status": "not_consumed",
        "notes": [
            "Input evidence is incomplete or not deterministically comparable.",
            "Not approved for adapter subset.",
        ],
    }


def render_markdown(policy: dict[str, Any], slot_equivalence_path: Path, command: str) -> str:
    summary = policy["summary"]
    blocked = policy["blocked_candidates"]
    blocked_health = [
        candidate for candidate in blocked
        if candidate.get("legacy_stat_key") == "health_on_kill"
    ]
    health = blocked_health[0] if blocked_health else None
    lines = [
        "# Forge-Safe Slot Vocabulary Policy",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Purpose",
        "",
        "This read-only policy records which slot vocabulary translations are approved for future test-only adapter work. It does not approve production migration, does not build a runtime adapter, and does not address value-scale normalization.",
        "",
        "## Source",
        "",
        f"Source slot equivalence report: `{slot_equivalence_path}`",
        "",
        "Generation command:",
        "",
        "```powershell",
        command,
        "```",
        "",
        "## Policy Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
    ]
    for key, value in summary.items():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Approved Slot Policy",
        "",
        f"{summary['policy_approved_slot_candidate_count']} candidates are approved only for future test-only adapter consideration from a slot-vocabulary perspective. These candidates still have unresolved value-scale blockers and are not production-safe.",
        "",
        "## health_on_kill Decision",
        "",
    ])
    if health:
        lines.extend([
            "`health_on_kill` remains blocked from adapter candidate approval.",
            "",
            f"- Affix count: {health['affix_count']}",
            f"- Example affix IDs: {', '.join(str(value) for value in health['example_affix_ids'])}",
            "- Reason: inconsistent applicability evidence across two affixes.",
            "- Required resolution: manual policy decision or source audit.",
            "- Initial adapter subset: excluded.",
        ])
    else:
        lines.append("No `health_on_kill` blocker was present in the input report.")

    lines.extend([
        "",
        "## Production Boundary",
        "",
        "This policy is for future test-only adapter work. It is marked `read_only=true`, `candidate_only=true`, `production_safe=false`, and `consumption_status=not_consumed`. Planner, crafting, stat aggregation, simulation, registries, and `/api/ref/affixes` must not consume it.",
        "",
        "## Value-Scale Boundary",
        "",
        "Value-scale blockers remain unresolved. Slot policy approval does not prove numerical equivalence, tier compatibility, gameplay correctness, or simulation behavior.",
        "",
        "## Migration Implications",
        "",
        "Slot vocabulary policy is now mostly settled for candidate planning: pure vocabulary differences can proceed to value-scale audit, while `health_on_kill` stays blocked until a manual policy or source audit resolves its applicability mismatch.",
        "",
        "Recommended next task: run a value-scale normalization audit for the 559 slot-policy-approved candidates, excluding `health_on_kill` from the initial subset.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    slot_equivalence = load_slot_equivalence(args.slot_equivalence)
    policy = build_slot_policy(slot_equivalence, source_path=str(args.slot_equivalence))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
    command = (
        ".\\backend\\.venv\\Scripts\\python.exe "
        "backend\\scripts\\report_forge_safe_slot_vocabulary_policy.py "
        "--slot-equivalence docs\\generated\\forge_safe_slot_vocabulary_equivalence.json "
        "--output docs\\generated\\forge_safe_slot_vocabulary_policy.json "
        "--markdown-output docs\\migration\\FORGE_SAFE_SLOT_VOCABULARY_POLICY.md"
    )
    args.markdown_output.write_text(
        render_markdown(policy, args.slot_equivalence, command),
        encoding="utf-8",
    )
    print(json.dumps({"summary": policy["summary"], "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
