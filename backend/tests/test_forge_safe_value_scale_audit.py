from pathlib import Path

from scripts.report_forge_safe_value_scale_audit import (
    MALFORMED,
    MIN_MAX,
    NEEDS_REVIEW,
    POLARITY,
    SCALE,
    STRUCTURAL,
    TIER_COUNT,
    build_value_scale_audit,
)


ROOT = Path(__file__).resolve().parents[2]


def test_structurally_equivalent_classification():
    report = _report_for(_difference("legacy_health", _tiers([1, 2]), _tiers([1, 2])))

    row = report["value_scale_statuses"][0]
    assert row["value_status"] == STRUCTURAL
    assert row["future_test_adapter_candidate"] is True


def test_consistent_scale_factor_classification():
    report = _report_for(_difference("legacy_health", _tiers([1, 2]), _tiers([100, 200])))

    row = report["value_scale_statuses"][0]
    assert row["value_status"] == SCALE
    assert row["scale_factor"] == "1E+2"
    assert row["future_test_adapter_candidate"] is True


def test_polarity_difference_classification():
    report = _report_for(_difference("legacy_health", _tiers([1, 2]), _tiers([-1, -2])))

    row = report["value_scale_statuses"][0]
    assert row["value_status"] == POLARITY
    assert row["future_test_adapter_candidate"] is False


def test_min_max_shape_difference_classification():
    report = _report_for(_difference("legacy_health", _tiers([1, 2]), _tiers([2, 5])))

    row = report["value_scale_statuses"][0]
    assert row["value_status"] == MIN_MAX
    assert row["future_test_adapter_candidate"] is False


def test_tier_count_difference_classification():
    report = _report_for(_difference("legacy_health", _tiers([1, 2]), _tiers([1, 2, 3])))

    row = report["value_scale_statuses"][0]
    assert row["value_status"] == TIER_COUNT
    assert row["future_test_adapter_candidate"] is False


def test_malformed_or_missing_values_classification():
    report = _report_for(_difference("legacy_health", None, _tiers([1, 2])))

    row = report["value_scale_statuses"][0]
    assert row["value_status"] == MALFORMED
    assert row["future_test_adapter_candidate"] is False


def test_mixed_candidate_evidence_needs_manual_review():
    report = build_value_scale_audit(
        _slot_policy(["legacy_health"]),
        _comparison([
            _difference("legacy_health", _tiers([1, 2]), _tiers([1, 2]), affix_id="1"),
            _difference("legacy_health", _tiers([1, 2]), _tiers([100, 200]), affix_id="2"),
        ]),
        slot_policy_path="slot.json",
        comparison_report_path="comparison.json",
    )

    row = report["value_scale_statuses"][0]
    assert row["value_status"] == NEEDS_REVIEW
    assert row["future_test_adapter_candidate"] is False


def test_slot_blocked_candidate_is_excluded():
    report = build_value_scale_audit(
        {
            "policy_approved_candidates": [],
            "blocked_candidates": [
                {"legacy_stat_key": "health_on_kill", "affix_count": 2, "example_affix_ids": [20, 44]}
            ],
            "metadata": _metadata(),
        },
        _comparison([]),
        slot_policy_path="slot.json",
        comparison_report_path="comparison.json",
    )

    assert report["summary"]["audited_candidate_count"] == 0
    assert report["summary"]["excluded_slot_blocked_candidate_count"] == 1
    assert report["excluded_candidates"][0]["legacy_stat_key"] == "health_on_kill"
    assert report["excluded_candidates"][0]["reason"] == "slot_policy_blocked"


def test_metadata_safety_flags_are_set():
    report = _report_for(_difference("legacy_health", _tiers([1]), _tiers([1])))

    assert report["metadata"]["read_only"] is True
    assert report["metadata"]["candidate_only"] is True
    assert report["metadata"]["production_consumer"] is False
    assert report["metadata"]["production_safe"] is False
    assert report["metadata"]["consumption_status"] == "not_consumed"
    assert report["summary"]["production_consumed"] is False


def test_production_modules_do_not_reference_value_audit_artifact_or_generator():
    forbidden = [
        "forge_safe_value_scale_audit.json",
        "report_forge_safe_value_scale_audit",
    ]
    offenders = []
    for root in [ROOT / "backend" / "app", ROOT / "backend" / "data"]:
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                if token in text:
                    offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def _report_for(difference):
    return build_value_scale_audit(
        _slot_policy(["legacy_health"]),
        _comparison([difference]),
        slot_policy_path="slot.json",
        comparison_report_path="comparison.json",
    )


def _slot_policy(stat_keys):
    return {
        "policy_approved_candidates": [
            {
                "legacy_stat_key": stat_key,
                "affix_count": 1,
                "example_affix_ids": [1],
                "slot_policy_status": "policy_approved_for_test_adapter",
            }
            for stat_key in stat_keys
        ],
        "blocked_candidates": [],
        "metadata": _metadata(),
    }


def _metadata():
    return {
        "read_only": True,
        "candidate_only": True,
        "experimental": True,
        "production_consumer": False,
        "production_safe": False,
    }


def _comparison(differences):
    return {
        "summary": {"difference_count": len(differences)},
        "differences": differences,
        "metadata": {
            "truncated": {"differences": False},
            **_metadata(),
        },
    }


def _difference(legacy_stat_key, legacy_tiers, bundle_tiers, *, affix_id="1"):
    legacy = {
        "affix_id": int(affix_id),
        "stat_keys": [legacy_stat_key],
        "tier_count": len(legacy_tiers) if legacy_tiers is not None else 0,
        "has_malformed_tiers": False,
    }
    bundle = {
        "affix_id": int(affix_id),
        "tier_count": len(bundle_tiers) if bundle_tiers is not None else 0,
        "has_malformed_tiers": False,
    }
    if legacy_tiers is not None:
        legacy["tiers"] = legacy_tiers
    if bundle_tiers is not None:
        bundle["tiers"] = bundle_tiers
    return {
        "affix_id": affix_id,
        "legacy": legacy,
        "bundle": bundle,
        "difference_types": ["tier", "stat_key"],
    }


def _tiers(values):
    return [
        {"tier": index + 1, "min": value, "max": value}
        for index, value in enumerate(values)
    ]
