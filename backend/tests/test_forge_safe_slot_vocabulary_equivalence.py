from pathlib import Path

from scripts.report_forge_safe_slot_vocabulary_equivalence import (
    BLOCKED,
    NEEDS_REVIEW,
    PURE,
    build_slot_equivalence_report,
)


ROOT = Path(__file__).resolve().parents[2]


def test_one_to_one_slot_mapping_classification():
    report = build_slot_equivalence_report(
        _adapter_candidates(["legacy_health"]),
        _comparison([_difference("1", "legacy_health", ["amulet"], ["AMULET"])]),
        adapter_candidates_path="candidates.json",
        comparison_report_path="comparison.json",
    )

    mapping = _slot_mapping(report, "amulet")
    assert mapping["mapping_shape"] == "one_to_one"
    assert mapping["migration_risk"] == "low"


def test_one_to_many_slot_mapping_classification():
    report = build_slot_equivalence_report(
        _adapter_candidates(["legacy_weapon"]),
        _comparison([
            _difference("1", "legacy_weapon", ["weapon"], ["ONE_HANDED_AXE", "TWO_HANDED_AXE"]),
        ]),
        adapter_candidates_path="candidates.json",
        comparison_report_path="comparison.json",
    )

    mapping = _slot_mapping(report, "weapon")
    assert mapping["mapping_shape"] == "one_to_many"
    assert mapping["migration_risk"] == "medium"


def test_missing_slot_mapping_classification():
    report = build_slot_equivalence_report(
        _adapter_candidates(["legacy_missing"]),
        _comparison([_difference("1", "legacy_missing", ["amulet"], [])]),
        adapter_candidates_path="candidates.json",
        comparison_report_path="comparison.json",
    )

    mapping = _slot_mapping(report, "amulet")
    assert mapping["mapping_shape"] == "missing"
    assert mapping["migration_risk"] == "high"


def test_ambiguous_inconsistent_slot_mapping_classification():
    report = build_slot_equivalence_report(
        _adapter_candidates(["legacy_a", "legacy_b"]),
        _comparison([
            _difference("1", "legacy_a", ["idol"], ["IDOL_1x3"]),
            _difference("2", "legacy_b", ["idol"], ["IDOL_3x1"]),
        ]),
        adapter_candidates_path="candidates.json",
        comparison_report_path="comparison.json",
    )

    mapping = _slot_mapping(report, "idol")
    assert mapping["mapping_shape"] == "ambiguous"
    assert mapping["migration_risk"] == "high"


def test_candidate_pure_vocabulary_difference_classification():
    report = build_slot_equivalence_report(
        _adapter_candidates(["legacy_health"]),
        _comparison([_difference("1", "legacy_health", ["helm"], ["HELMET"])]),
        adapter_candidates_path="candidates.json",
        comparison_report_path="comparison.json",
    )

    status = report["candidate_slot_statuses"][0]
    assert status["slot_status"] == PURE
    assert report["summary"]["pure_vocabulary_candidate_count"] == 1


def test_candidate_blocked_by_inconsistent_slot_applicability():
    report = build_slot_equivalence_report(
        _adapter_candidates(["legacy_health"]),
        _comparison([
            _difference("1", "legacy_health", ["idol"], ["IDOL_1x3"]),
            _difference("2", "legacy_health", ["idol"], ["IDOL_3x1"]),
        ]),
        adapter_candidates_path="candidates.json",
        comparison_report_path="comparison.json",
    )

    status = report["candidate_slot_statuses"][0]
    assert status["slot_status"] == BLOCKED
    assert report["summary"]["slot_blocked_candidate_count"] == 1


def test_candidate_without_evidence_needs_manual_review():
    report = build_slot_equivalence_report(
        _adapter_candidates(["legacy_health"]),
        _comparison([]),
        adapter_candidates_path="candidates.json",
        comparison_report_path="comparison.json",
    )

    status = report["candidate_slot_statuses"][0]
    assert status["slot_status"] == NEEDS_REVIEW
    assert report["summary"]["needs_manual_review_count"] == 1


def test_metadata_safety_flags_are_set():
    report = build_slot_equivalence_report(
        _adapter_candidates(["legacy_health"]),
        _comparison([_difference("1", "legacy_health", ["helm"], ["HELMET"])]),
        adapter_candidates_path="candidates.json",
        comparison_report_path="comparison.json",
    )

    assert report["metadata"]["read_only"] is True
    assert report["metadata"]["candidate_only"] is True
    assert report["metadata"]["production_consumer"] is False
    assert report["metadata"]["production_safe"] is False
    assert report["metadata"]["consumption_status"] == "not_consumed"
    assert report["summary"]["production_consumed"] is False


def test_production_modules_do_not_reference_slot_equivalence_artifact_or_generator():
    forbidden = [
        "forge_safe_slot_vocabulary_equivalence.json",
        "report_forge_safe_slot_vocabulary_equivalence",
    ]
    offenders = []
    for root in [ROOT / "backend" / "app", ROOT / "backend" / "data"]:
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                if token in text:
                    offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def _slot_mapping(report, legacy_slot):
    return next(
        mapping
        for mapping in report["slot_mappings"]
        if mapping["legacy_slot_value"] == legacy_slot
    )


def _adapter_candidates(stat_keys):
    return {
        "summary": {"candidate_count": len(stat_keys), "production_consumed": False},
        "candidates": [
            {
                "legacy_stat_key": stat_key,
                "affix_count": 1,
                "example_affix_ids": [index + 1],
                "candidate_status": "reviewed_candidate",
                "consumption_status": "not_consumed",
            }
            for index, stat_key in enumerate(stat_keys)
        ],
        "metadata": {
            "read_only": True,
            "candidate_only": True,
            "experimental": True,
            "production_consumer": False,
            "production_safe": False,
        },
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


def _difference(affix_id, legacy_stat_key, legacy_slots, bundle_slots):
    return {
        "affix_id": affix_id,
        "difference_types": ["slot", "stat_key"],
        "legacy": {
            "affix_id": int(affix_id),
            "stat_keys": [legacy_stat_key],
            "slots": legacy_slots,
        },
        "bundle": {
            "affix_id": int(affix_id),
            "slots": bundle_slots,
        },
    }
