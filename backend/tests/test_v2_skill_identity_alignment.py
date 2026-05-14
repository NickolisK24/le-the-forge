from backend.scripts.report_v2_skill_identity_alignment import build_report


def _class_bundle(*refs: str) -> dict:
    return {
        "records": {
            "classes": [
                {
                    "canonical_id": "class:test",
                    "linked_skill_source_ids": list(refs),
                    "skill_ids": list(refs),
                }
            ],
            "masteries": [],
        }
    }


def _skill_bundle(*skills: dict) -> dict:
    return {"records": {"skills": list(skills)}}


def _skill(canonical_id: str, source_skill_id: str, display_name: str) -> dict:
    return {
        "canonical_id": canonical_id,
        "source_skill_id": source_skill_id,
        "display_name": display_name,
        "raw_reference": {"source_skill_id": source_skill_id},
    }


def _source_skills(*skills: dict) -> dict:
    return {"skills": list(skills)}


def test_unresolved_links_are_reported() -> None:
    report = build_report(
        _class_bundle("skill_path:100"),
        _skill_bundle(_skill("skill:abc", "abc", "A Test Skill")),
        {},
        {"classes": []},
        _source_skills({"id": "abc", "name": "A Test Skill"}),
    )

    assert report["summary"]["total_class_mastery_skill_references"] == 1
    assert report["summary"]["unresolved_reference_count"] == 1
    assert report["summary"]["bridge_safe"] is False
    assert report["references"][0]["status"] == "unresolved"


def test_top_level_path_match_can_be_safe_when_complete() -> None:
    report = build_report(
        _class_bundle("skill_path:100"),
        _skill_bundle(_skill("skill:abc", "abc", "A Test Skill")),
        {},
        {"classes": []},
        _source_skills({"id": "abc", "name": "A Test Skill", "abilityPathId": 100}),
    )

    assert report["summary"]["exact_path_match_count"] == 1
    assert report["summary"]["top_level_path_match_count"] == 1
    assert report["summary"]["unresolved_reference_count"] == 0
    assert report["summary"]["ambiguous_match_count"] == 0
    assert report["summary"]["bridge_safe"] is True


def test_source_identity_skill_path_is_top_level_match() -> None:
    report = build_report(
        _class_bundle("skill_path:100"),
        _skill_bundle(_skill("skill:abc", "abc", "A Test Skill")),
        {},
        {"classes": []},
        _source_skills(
            {
                "id": "abc",
                "name": "A Test Skill",
                "sourceIdentity": {
                    "skillPath": "skill_path:100",
                    "identitySource": "SkillTree.ability PPtr",
                    "identityConfidence": "top_level_owner_pptr",
                },
            }
        ),
    )

    assert report["summary"]["exact_path_match_count"] == 1
    assert report["summary"]["top_level_path_match_count"] == 1
    assert report["summary"]["bridge_safe"] is True
    assert report["references"][0]["exact_path_matches"][0]["field_path"] == "sourceIdentity.skillPath"


def test_nested_path_match_is_not_bridge_safe() -> None:
    report = build_report(
        _class_bundle("skill_path:100"),
        _skill_bundle(_skill("skill:abc", "abc", "A Test Skill")),
        {},
        {"classes": []},
        _source_skills({"id": "abc", "name": "A Test Skill", "summonedActors": [{"resolvedAbilityPathId": 100}]}),
    )

    assert report["summary"]["exact_path_match_count"] == 1
    assert report["summary"]["top_level_path_match_count"] == 0
    assert report["summary"]["bridge_safe"] is False
    assert report["summary"]["recommended_mapping_strategy"] == "do_not_bridge_from_nested_path_evidence"


def test_ambiguous_mappings_are_not_silently_accepted() -> None:
    report = build_report(
        _class_bundle("skill_path:100"),
        _skill_bundle(
            _skill("skill:abc", "abc", "A Test Skill"),
            _skill("skill:def", "def", "Another Skill"),
        ),
        {},
        {"classes": []},
        _source_skills(
            {"id": "abc", "name": "A Test Skill", "abilityPathId": 100},
            {"id": "def", "name": "Another Skill", "abilityPathId": 100},
        ),
    )

    assert report["summary"]["ambiguous_match_count"] == 1
    assert report["summary"]["bridge_safe"] is False
    assert report["references"][0]["status"] == "ambiguous"


def test_exact_source_id_match_is_counted_separately() -> None:
    report = build_report(
        _class_bundle("skill:abc"),
        _skill_bundle(_skill("skill:abc", "abc", "A Test Skill")),
        {},
        {"classes": []},
        _source_skills({"id": "abc", "name": "A Test Skill"}),
    )

    assert report["summary"]["total_class_mastery_skill_references"] == 1
    assert report["summary"]["exact_id_match_count"] == 1
    assert report["summary"]["bridge_safe"] is True


def test_metadata_safety_flags() -> None:
    report = build_report(
        _class_bundle("skill_path:100"),
        _skill_bundle(),
        {},
        {"classes": []},
        _source_skills(),
    )

    assert report["metadata"]["read_only"] is True
    assert report["metadata"]["experimental"] is True
    assert report["metadata"]["production_safe"] is False
    assert report["summary"]["production_consumed"] is False
