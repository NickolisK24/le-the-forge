from pathlib import Path

from scripts.report_forge_safe_slot_vocabulary_policy import (
    APPROVED_POLICY,
    BLOCKED_POLICY,
    MANUAL_REVIEW_POLICY,
    build_slot_policy,
)


ROOT = Path(__file__).resolve().parents[2]


def test_pure_vocabulary_candidates_become_policy_approved():
    policy = build_slot_policy(
        _slot_equivalence([_candidate("legacy_health", "pure_vocabulary_difference")]),
        source_path="slot.json",
    )

    approved = policy["policy_approved_candidates"][0]
    assert approved["legacy_stat_key"] == "legacy_health"
    assert approved["slot_policy_status"] == APPROVED_POLICY
    assert policy["summary"]["policy_approved_slot_candidate_count"] == 1


def test_blocked_candidates_remain_blocked():
    policy = build_slot_policy(
        _slot_equivalence([_candidate("legacy_health", "blocked_by_slot_applicability")]),
        source_path="slot.json",
    )

    blocked = policy["blocked_candidates"][0]
    assert blocked["legacy_stat_key"] == "legacy_health"
    assert blocked["slot_policy_status"] == BLOCKED_POLICY
    assert blocked["required_resolution"] == "manual_policy_decision_or_source_audit"


def test_needs_manual_review_candidates_remain_manual_review():
    policy = build_slot_policy(
        _slot_equivalence([_candidate("legacy_health", "needs_manual_review")]),
        source_path="slot.json",
    )

    manual = policy["manual_review_candidates"][0]
    assert manual["legacy_stat_key"] == "legacy_health"
    assert manual["slot_policy_status"] == MANUAL_REVIEW_POLICY


def test_health_on_kill_remains_blocked_when_input_is_blocked():
    policy = build_slot_policy(
        _slot_equivalence([_candidate("health_on_kill", "blocked_by_slot_applicability")]),
        source_path="slot.json",
    )

    blocked = policy["blocked_candidates"][0]
    assert blocked["legacy_stat_key"] == "health_on_kill"
    assert blocked["slot_policy_status"] == BLOCKED_POLICY
    assert any("health_on_kill remains blocked" in note for note in blocked["notes"])
    assert policy["summary"]["policy_approved_slot_candidate_count"] == 0


def test_metadata_safety_flags_are_set():
    policy = build_slot_policy(
        _slot_equivalence([_candidate("legacy_health", "pure_vocabulary_difference")]),
        source_path="slot.json",
    )

    assert policy["metadata"]["read_only"] is True
    assert policy["metadata"]["candidate_only"] is True
    assert policy["metadata"]["production_consumer"] is False
    assert policy["metadata"]["production_safe"] is False
    assert policy["metadata"]["consumption_status"] == "not_consumed"
    assert policy["summary"]["production_consumed"] is False


def test_production_modules_do_not_reference_slot_policy_artifact_or_generator():
    forbidden = [
        "forge_safe_slot_vocabulary_policy.json",
        "report_forge_safe_slot_vocabulary_policy",
    ]
    offenders = []
    for root in [ROOT / "backend" / "app", ROOT / "backend" / "data"]:
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                if token in text:
                    offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def _slot_equivalence(candidates):
    return {
        "summary": {
            "candidate_count": len(candidates),
            "production_consumed": False,
        },
        "candidate_slot_statuses": candidates,
        "metadata": {
            "read_only": True,
            "candidate_only": True,
            "experimental": True,
            "production_consumer": False,
            "production_safe": False,
        },
    }


def _candidate(legacy_stat_key, status):
    return {
        "legacy_stat_key": legacy_stat_key,
        "slot_status": status,
        "affix_count": 1,
        "example_affix_ids": [1],
        "legacy_slot_values": ["helm"],
        "bundle_item_values": ["HELMET"],
        "legacy_slot_sets": [["helm"]],
        "bundle_item_sets": [["HELMET"]],
    }
