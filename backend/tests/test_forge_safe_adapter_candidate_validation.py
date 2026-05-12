from pathlib import Path

from scripts.report_forge_safe_adapter_candidate_validation import (
    APPROVED,
    BLOCKED_BOTH,
    BLOCKED_SLOT,
    BLOCKED_VALUE,
    NEEDS_REVIEW,
    build_validation_report,
)


ROOT = Path(__file__).resolve().parents[2]


def test_candidate_without_slot_or_value_blockers_is_approved():
    report = build_validation_report(
        _adapter_candidates([_candidate("legacy_health")]),
        _comparison([_difference("1", "legacy_health", ["stat_key"])]),
        adapter_candidates_path="candidates.json",
        comparison_report_path="comparison.json",
    )

    row = report["validated_candidates"][0]
    assert row["candidate_status"] == APPROVED
    assert report["summary"]["approved_for_test_adapter_candidate_count"] == 1


def test_candidate_with_value_difference_is_blocked_by_value_scale():
    report = build_validation_report(
        _adapter_candidates([_candidate("legacy_health")]),
        _comparison([_difference("1", "legacy_health", ["tier", "stat_key"])]),
        adapter_candidates_path="candidates.json",
        comparison_report_path="comparison.json",
    )

    row = report["validated_candidates"][0]
    assert row["candidate_status"] == BLOCKED_VALUE
    assert row["blockers"]["value_scale"]


def test_candidate_with_slot_difference_is_blocked_by_slot_applicability():
    report = build_validation_report(
        _adapter_candidates([_candidate("legacy_health")]),
        _comparison([_difference("1", "legacy_health", ["slot", "stat_key"])]),
        adapter_candidates_path="candidates.json",
        comparison_report_path="comparison.json",
    )

    row = report["validated_candidates"][0]
    assert row["candidate_status"] == BLOCKED_SLOT
    assert row["blockers"]["slot_applicability"]


def test_candidate_with_slot_and_value_differences_is_blocked_by_both():
    report = build_validation_report(
        _adapter_candidates([_candidate("legacy_health")]),
        _comparison([_difference("1", "legacy_health", ["slot", "tier", "stat_key"])]),
        adapter_candidates_path="candidates.json",
        comparison_report_path="comparison.json",
    )

    row = report["validated_candidates"][0]
    assert row["candidate_status"] == BLOCKED_BOTH
    assert report["summary"]["blocked_by_both_count"] == 1


def test_candidate_with_missing_comparison_evidence_needs_manual_review():
    report = build_validation_report(
        _adapter_candidates([_candidate("legacy_health")]),
        _comparison([]),
        adapter_candidates_path="candidates.json",
        comparison_report_path="comparison.json",
    )

    row = report["validated_candidates"][0]
    assert row["candidate_status"] == NEEDS_REVIEW
    assert report["summary"]["needs_manual_review_count"] == 1


def test_metadata_safety_flags_are_preserved():
    report = build_validation_report(
        _adapter_candidates([_candidate("legacy_health")]),
        _comparison([_difference("1", "legacy_health", ["slot", "tier", "stat_key"])]),
        adapter_candidates_path="candidates.json",
        comparison_report_path="comparison.json",
    )

    assert report["metadata"]["read_only"] is True
    assert report["metadata"]["candidate_only"] is True
    assert report["metadata"]["production_consumer"] is False
    assert report["metadata"]["production_safe"] is False
    assert report["metadata"]["consumption_status"] == "not_consumed"
    assert report["summary"]["production_consumed"] is False


def test_production_modules_do_not_reference_validation_artifact_or_generator():
    forbidden = [
        "forge_safe_adapter_candidate_validation.json",
        "report_forge_safe_adapter_candidate_validation",
    ]
    offenders = []
    for root in [ROOT / "backend" / "app", ROOT / "backend" / "data"]:
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                if token in text:
                    offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def _adapter_candidates(candidates):
    return {
        "summary": {"candidate_count": len(candidates), "production_consumed": False},
        "candidates": candidates,
        "metadata": {
            "read_only": True,
            "candidate_only": True,
            "experimental": True,
            "production_consumer": False,
            "production_safe": False,
        },
    }


def _candidate(legacy_stat_key):
    return {
        "legacy_stat_key": legacy_stat_key,
        "bundle_modifier_reference": {
            "modifier_id": "equipment:1",
            "property": "Health",
            "property_path": "ADDED:Health:None",
        },
        "affix_count": 1,
        "example_affix_ids": [1],
        "candidate_status": "reviewed_candidate",
        "consumption_status": "not_consumed",
    }


def _comparison(differences):
    return {
        "summary": {"difference_count": len(differences)},
        "differences": differences,
        "metadata": {
            "read_only": True,
            "experimental": True,
            "production_consumer": False,
            "production_safe": False,
            "truncated": {"differences": False},
        },
    }


def _difference(affix_id, legacy_stat_key, difference_types):
    return {
        "affix_id": affix_id,
        "difference_types": difference_types,
        "legacy": {
            "affix_id": int(affix_id),
            "stat_keys": [legacy_stat_key],
        },
        "bundle": {
            "affix_id": int(affix_id),
        },
    }
