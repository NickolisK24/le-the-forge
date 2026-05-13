import json
from pathlib import Path

import pytest

from app.repositories.v2.skill_repository import V2SkillBundleError, V2SkillRepository
from scripts.report_v2_skill_tree_bundle import build_v2_skill_tree_bundles, validate_v2_skill_tree_records


def test_v2_skill_tree_bundle_generation(tmp_path):
    source, layout, classes = _write_sources(tmp_path)

    skill_bundle, tree_bundle, validation, unsupported = build_v2_skill_tree_bundles(source, layout, classes)

    assert skill_bundle["summary"]["skill_count"] == 2
    assert skill_bundle["summary"]["skill_with_tree_count"] == 1
    assert tree_bundle["summary"]["skill_tree_count"] == 1
    assert tree_bundle["summary"]["skill_node_count"] == 2
    assert tree_bundle["summary"]["layout_matched_node_count"] == 2
    assert validation["summary"]["error_count"] == 0
    assert unsupported["summary"]["unsupported_or_text_only_node_count"] == 1
    skill = skill_bundle["records"]["skills"][0]
    tree = tree_bundle["records"]["skill_trees"][0]
    nodes = tree_bundle["records"]["skill_nodes"]
    assert skill["canonical_id"] == "skill:fi9"
    assert skill["skill_tree_id"] == "skill_tree:fi9"
    assert tree["canonical_id"] == "skill_tree:fi9"
    assert nodes[0]["canonical_id"] == "skill_node:fi9:0"
    assert nodes[0]["position"] == {"x": 0.0, "y": 0.0}
    assert nodes[0]["special_behavior_classification"] == "partial_modifier"
    assert nodes[1]["special_behavior_classification"] == "unsupported_special_behavior"
    assert nodes[0]["stable_calculable"] is False


def test_v2_skill_validation_detects_duplicate_ids(tmp_path):
    skill_bundle, tree_bundle, _validation, _unsupported = _bundles(tmp_path)
    skills = skill_bundle["records"]["skills"]
    trees = tree_bundle["records"]["skill_trees"]
    nodes = tree_bundle["records"]["skill_nodes"]
    skills.append(dict(skills[0]))
    trees.append(dict(trees[0]))
    nodes.append(dict(nodes[0]))

    report = validate_v2_skill_tree_records(skills, trees, nodes, _class_mastery_bundle())

    assert report["summary"]["duplicate_skill_id_count"] == 1
    assert report["summary"]["duplicate_skill_tree_id_count"] == 1
    assert report["summary"]["duplicate_skill_node_id_count"] == 1
    with pytest.raises(V2SkillBundleError, match="Duplicate canonical_id"):
        V2SkillRepository("<skills>", "<trees>").load_payloads(skill_bundle, tree_bundle)


def test_v2_skill_validation_detects_missing_links(tmp_path):
    skill_bundle, tree_bundle, _validation, _unsupported = _bundles(tmp_path)
    skill_bundle["records"]["skills"][0]["skill_tree_id"] = "skill_tree:missing"
    tree_bundle["records"]["skill_trees"][0]["skill_id"] = "skill:missing"
    tree_bundle["records"]["skill_nodes"][0]["skill_tree_id"] = "skill_tree:missing"
    tree_bundle["records"]["skill_nodes"][1]["skill_id"] = "skill:missing"

    report = validate_v2_skill_tree_records(skill_bundle["records"]["skills"], tree_bundle["records"]["skill_trees"], tree_bundle["records"]["skill_nodes"], _class_mastery_bundle())

    assert report["summary"]["skill_tree_missing_skill_link_count"] == 1
    assert report["summary"]["skill_node_missing_tree_link_count"] == 1
    assert report["summary"]["skill_node_missing_skill_link_count"] == 1
    with pytest.raises(V2SkillBundleError, match="links missing tree"):
        V2SkillRepository("<skills>", "<trees>").load_payloads(skill_bundle, tree_bundle)


def test_v2_skill_validation_requires_provenance_and_support_status(tmp_path):
    skill_bundle, tree_bundle, _validation, _unsupported = _bundles(tmp_path)
    skill_bundle["records"]["skills"][0]["provenance"] = {}
    tree_bundle["records"]["skill_nodes"][0].pop("support_status")

    report = validate_v2_skill_tree_records(skill_bundle["records"]["skills"], tree_bundle["records"]["skill_trees"], tree_bundle["records"]["skill_nodes"], _class_mastery_bundle())

    assert report["summary"]["missing_provenance_count"] == 1
    assert report["summary"]["missing_support_status_count"] == 1
    with pytest.raises(V2SkillBundleError, match="missing provenance"):
        V2SkillRepository("<skills>", "<trees>").load_payloads(skill_bundle, tree_bundle)


def test_v2_skill_repository_lookup_and_debug(tmp_path):
    skill_bundle, tree_bundle, _validation, _unsupported = _bundles(tmp_path)
    repository = V2SkillRepository("<skills>", "<trees>").load_payloads(skill_bundle, tree_bundle)

    assert repository.count_skills() == 2
    assert repository.count_trees() == 1
    assert repository.count_nodes() == 2
    assert repository.get_skill("skill:fi9")["display_name"] == "Fireball"
    assert repository.get_tree("skill_tree:fi9")["display_name"] == "Fireball Skill Tree"
    assert repository.get_tree_by_skill("skill:fi9")["canonical_id"] == "skill_tree:fi9"
    assert repository.get_node("skill_node:fi9:2")["display_name"] == "Special Fire"
    assert repository.get_nodes_by_tree("skill_tree:fi9")[0]["canonical_id"] == "skill_node:fi9:0"
    assert repository.filter_skills(query="fire")[0]["canonical_id"] == "skill:fi9"
    assert repository.debug_summary()["production_consumer"] is False


def test_v2_skill_routes(app, tmp_path):
    skill_bundle, tree_bundle, _validation, _unsupported = _bundles(tmp_path)
    skill_path = tmp_path / "v2_skill_bundle.json"
    tree_path = tmp_path / "v2_skill_tree_bundle.json"
    skill_path.write_text(json.dumps(skill_bundle), encoding="utf-8")
    tree_path.write_text(json.dumps(tree_bundle), encoding="utf-8")
    app.config["V2_SKILL_BUNDLE_PATH"] = str(skill_path)
    app.config["V2_SKILL_TREE_BUNDLE_PATH"] = str(tree_path)
    client = app.test_client()

    skills = client.get("/experimental/v2/skills?q=fire")
    assert skills.status_code == 200
    assert skills.get_json()["records"][0]["canonical_id"] == "skill:fi9"

    skill = client.get("/experimental/v2/skills/skill:fi9")
    assert skill.status_code == 200
    assert skill.get_json()["record"]["display_name"] == "Fireball"

    tree_by_skill = client.get("/experimental/v2/skills/skill:fi9/tree")
    assert tree_by_skill.status_code == 200
    assert tree_by_skill.get_json()["record"]["canonical_id"] == "skill_tree:fi9"

    tree = client.get("/experimental/v2/skills/trees/skill_tree:fi9")
    assert tree.status_code == 200
    assert tree.get_json()["nodes"][0]["canonical_id"] == "skill_node:fi9:0"

    node = client.get("/experimental/v2/skills/trees/skill_tree:fi9/nodes/skill_node:fi9:2")
    assert node.status_code == 200
    assert node.get_json()["record"]["special_behavior_classification"] == "unsupported_special_behavior"

    debug = client.get("/experimental/v2/skills/debug")
    assert debug.status_code == 200
    assert debug.get_json()["debug_summary"]["production_safe"] is False


def test_v2_skill_bundle_is_not_referenced_by_production_modules():
    root = Path(__file__).resolve().parents[2]
    allowed = {
        root / "backend" / "app" / "routes" / "experimental.py",
        root / "backend" / "app" / "repositories" / "v2" / "skill_repository.py",
        root / "backend" / "app" / "repositories" / "v2" / "__init__.py",
        root / "backend" / "scripts" / "report_v2_skill_tree_bundle.py",
        Path(__file__).resolve(),
    }
    needles = ("v2_skill_bundle.json", "v2_skill_tree_bundle.json", "V2SkillRepository")
    offenders: list[str] = []
    for path in (root / "backend" / "app").rglob("*.py"):
        if path in allowed or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if any(needle in text for needle in needles):
            offenders.append(str(path.relative_to(root)))

    assert offenders == []


def _bundles(tmp_path: Path) -> tuple[dict, dict, dict, dict]:
    source, layout, classes = _write_sources(tmp_path)
    return build_v2_skill_tree_bundles(source, layout, classes)


def _write_sources(tmp_path: Path) -> tuple[Path, Path, Path]:
    source = tmp_path / "skills_with_trees.json"
    layout = tmp_path / "skill-tree-layout.json"
    classes = tmp_path / "v2_class_mastery_bundle.json"
    source.write_text(json.dumps(_source_skills()), encoding="utf-8")
    layout.write_text(json.dumps(_layout_skills()), encoding="utf-8")
    classes.write_text(json.dumps(_class_mastery_bundle()), encoding="utf-8")
    return source, layout, classes


def _source_skills() -> dict:
    return {
        "meta": {"source": "test"},
        "skills": [
            {
                "id": "fi9",
                "name": "Fireball",
                "description": "Cast a fireball.",
                "lore": "",
                "altText": "",
                "tagsDecoded": ["Fire", "Spell"],
                "conversionDamageTagsDecoded": [],
                "manaCost": 3,
                "minimumManaCost": 0,
                "channelCost": 0,
                "freeWhenOutOfMana": False,
                "useDelay": 0,
                "useDuration": 1,
                "minimumUseDuration": 0,
                "channelTimeLimit": 0,
                "channelled": False,
                "instantCast": False,
                "speedScaler": 1,
                "speedMultiplier": 1,
                "maxCharges": 1,
                "chargesPerSecond": 0,
                "sharedCooldown": False,
                "cannotResetCooldown": False,
                "requireWeaponType": False,
                "permittedWeaponTypes": [],
                "requiresShield": False,
                "requiresDualWield": False,
                "attributeScaling": [{"attribute": "Intelligence", "stats": []}],
                "damageSources": [{"kind": "hit"}],
                "damageSourceStatus": "serialized",
                "mutatorHints": [],
                "summonedActors": [],
                "damageSourceNotes": [],
                "hasTree": True,
                "skillTree": {
                    "sourceId": "fi9",
                    "className": "FireballTree",
                    "ability": "Fireball",
                    "nodes": [
                        {
                            "id": 0,
                            "name": "Fireball",
                            "description": "",
                            "maxPoints": 0,
                            "masteryRequirement": 0,
                            "stats": [{"statName": "Damage", "value": "+5%", "property": 0}],
                            "requirements": [],
                            "effectHints": [{"classification": "stat_modifier_serialized", "statName": "Damage", "value": "+5%", "property": 0}],
                        },
                        {
                            "id": 2,
                            "name": "Special Fire",
                            "description": "Special behavior.",
                            "maxPoints": 1,
                            "masteryRequirement": 0,
                            "stats": [{"statName": "Special", "value": "", "property": 54}],
                            "requirements": [{"nodeId": 0, "requirement": 0}],
                            "effectHints": [{"classification": "unsafe_to_infer", "statName": "Special", "value": "", "property": 54}],
                        },
                    ],
                },
            },
            {
                "id": "utility",
                "name": "Utility",
                "description": "",
                "tagsDecoded": [],
                "conversionDamageTagsDecoded": [],
                "attributeScaling": [],
                "damageSources": [],
                "damageSourceStatus": "none",
                "mutatorHints": [],
                "summonedActors": [],
                "damageSourceNotes": [],
                "hasTree": False,
            },
        ],
    }


def _layout_skills() -> dict:
    return {
        "fi9": {
            "children": [
                {"rect": [0, 0, 84, 84], "icon": "root", "nodeSize": 0, "treeId": "fi9", "nodeId": 0},
                {"rect": [120, 80, 60, 60], "icon": "special", "nodeSize": 2, "treeId": "fi9", "nodeId": 2},
            ]
        }
    }


def _class_mastery_bundle() -> dict:
    return {
        "records": {
            "classes": [{"canonical_id": "class:mage", "display_name": "Mage", "skill_ids": ["skill_path:123"]}],
            "masteries": [{"canonical_id": "mastery:mage:sorcerer", "display_name": "Sorcerer", "class_id": "class:mage", "skill_ids": []}],
        }
    }
