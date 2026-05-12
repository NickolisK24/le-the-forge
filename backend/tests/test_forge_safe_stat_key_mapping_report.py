from scripts.report_forge_safe_stat_key_mapping import build_mapping_report


def test_reports_one_to_one_mapping():
    report = build_mapping_report(_comparison([
        _difference("1", "legacy_health", ["ADDED:Health:None"], ["equipment:1"]),
        _difference("2", "legacy_health", ["ADDED:Health:None"], ["equipment:2"]),
    ]))

    mapping = _mapping(report, "legacy_health")
    assert mapping["mapping_shape"] == "one_to_one"
    assert mapping["migration_risk"] == "low"
    assert report["summary"]["one_to_one_mapping_count"] == 1


def test_reports_one_to_many_mapping_for_consistent_split():
    report = build_mapping_report(_comparison([
        _difference(
            "1",
            "legacy_combo",
            ["ADDED:Health:None", "INCREASED:Damage:Fire"],
            ["equipment:1#slot0", "equipment:1#slot1"],
            bundle_modifier_count=2,
        ),
        _difference(
            "2",
            "legacy_combo",
            ["ADDED:Health:None", "INCREASED:Damage:Fire"],
            ["equipment:2#slot0", "equipment:2#slot1"],
            bundle_modifier_count=2,
        ),
    ]))

    mapping = _mapping(report, "legacy_combo")
    assert mapping["mapping_shape"] == "one_to_many"
    assert mapping["migration_risk"] == "medium"
    assert mapping["split_affix_count"] == 2
    assert report["summary"]["one_to_many_mapping_count"] == 1


def test_reports_missing_mapping():
    report = build_mapping_report(_comparison([
        _difference("1", "legacy_missing", [], [], bundle_modifier_count=0),
    ]))

    mapping = _mapping(report, "legacy_missing")
    assert mapping["mapping_shape"] == "missing"
    assert mapping["migration_risk"] == "high"
    assert report["summary"]["missing_mapping_count"] == 1


def test_reports_ambiguous_mapping_for_conflicting_single_references():
    report = build_mapping_report(_comparison([
        _difference("1", "legacy_conflict", ["ADDED:Health:None"], ["equipment:1"]),
        _difference("2", "legacy_conflict", ["INCREASED:Damage:Fire"], ["equipment:2"]),
    ]))

    mapping = _mapping(report, "legacy_conflict")
    assert mapping["mapping_shape"] == "ambiguous"
    assert mapping["migration_risk"] == "high"
    assert report["summary"]["ambiguous_mapping_count"] == 1


def test_counts_one_to_two_splits_and_safety_metadata():
    report = build_mapping_report(_comparison([
        _difference(
            "1",
            "legacy_combo",
            ["ADDED:Health:None", "INCREASED:Damage:Fire"],
            ["equipment:1#slot0", "equipment:1#slot1"],
            bundle_modifier_count=2,
        ),
    ]))

    assert report["summary"]["one_to_two_affix_count"] == 1
    assert report["one_to_two_splits"][0]["legacy_stat_key"] == "legacy_combo"
    assert report["metadata"]["read_only"] is True
    assert report["metadata"]["experimental"] is True
    assert report["metadata"]["production_consumer"] is False
    assert report["metadata"]["production_safe"] is False


def _mapping(report, legacy_stat_key):
    return next(
        mapping
        for mapping in report["mappings"]
        if mapping["legacy_stat_key"] == legacy_stat_key
    )


def _comparison(differences):
    return {
        "summary": {
            "matched_count": len(differences),
            "stat_key_difference_count": len(differences),
        },
        "differences": differences,
        "metadata": {
            "read_only": True,
            "experimental": True,
            "production_consumer": False,
            "production_safe": False,
            "truncated": {"differences": False},
        },
    }


def _difference(
    affix_id,
    legacy_stat_key,
    bundle_stat_keys,
    modifier_ids,
    *,
    bundle_modifier_count=1,
):
    return {
        "affix_id": affix_id,
        "legacy": {
            "affix_id": int(affix_id),
            "id": f"legacy_{affix_id}",
            "name": f"Legacy {affix_id}",
            "stat_keys": [legacy_stat_key],
            "modifier_count": 1,
        },
        "bundle": {
            "affix_id": int(affix_id),
            "id": f"equipment:{affix_id}",
            "name": f"Bundle {affix_id}",
            "stat_keys": bundle_stat_keys,
            "modifier_ids": modifier_ids,
            "modifier_count": bundle_modifier_count,
        },
    }
