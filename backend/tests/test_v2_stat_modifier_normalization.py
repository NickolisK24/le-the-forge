import json
from pathlib import Path

from app.normalization.v2 import V2ModifierRegistry, V2StatRegistry, classify_operation
from app.normalization.v2.modifier_policy import is_stable_modifier_eligible
from scripts.report_v2_stat_modifier_normalization import build_v2_stat_modifier_reports, validate_modifier_records


def test_v2_stat_modifier_report_generation_collects_stats_and_blocks_source_units():
    reports = build_v2_stat_modifier_reports(_payloads(), _skill_identity_report())

    modifier_summary = reports["modifier_registry"]["summary"]
    stat_summary = reports["stat_registry"]["summary"]

    assert modifier_summary["modifier_count"] >= 4
    assert stat_summary["stat_count"] >= 3
    assert modifier_summary["stable_calculable_count"] == 0
    assert modifier_summary["value_scale_status_counts"]["source_units"] >= 2
    assert modifier_summary["blocked_reason_counts"]["value_scale_not_planner_normalized"] == modifier_summary["modifier_count"]
    assert modifier_summary["blocked_reason_counts"]["source_identity_not_resolved"] >= 1
    assert reports["validation_report"]["summary"]["error_count"] == 0


def test_v2_modifier_validation_detects_duplicate_modifier_ids():
    reports = build_v2_stat_modifier_reports(_payloads(), _skill_identity_report())
    modifiers = reports["modifier_registry"]["records"]["modifiers"]
    stats = reports["stat_registry"]["records"]["stats"]
    modifiers.append(dict(modifiers[0]))

    validation = validate_modifier_records(modifiers, stats, {"unresolved_reference_count": 0, "ambiguous_reference_count": 0})

    assert validation["summary"]["duplicate_canonical_modifier_id_count"] == 1
    assert validation["summary"]["error_count"] == 1


def test_v2_operation_classification_keeps_unknown_unknown():
    assert classify_operation(modifier_type="ADDED") == "flat"
    assert classify_operation(property_path="INCREASED.Damage.Fire") == "increased"
    assert classify_operation(stat_label="unstructured serialized hint") == "unknown"


def test_v2_stable_policy_blocks_unsafe_records():
    stable_record = {
        "support_status": "trusted",
        "trust_level": "generated_from_game_data",
        "stat_id": "stat:health",
        "operation": "flat",
        "value_scale_status": "planner_normalized",
        "source_identity_status": "resolved",
        "source_record_status": "modifier_row",
        "special_behavior_classification": "trusted_modifier",
        "provenance": {"source_path": "source.json"},
    }
    assert is_stable_modifier_eligible(stable_record) == (True, [])

    unsafe = dict(stable_record, value_scale_status="source_units", source_identity_status="partially_unresolved")
    stable, reasons = is_stable_modifier_eligible(unsafe)
    assert stable is False
    assert "value_scale_not_planner_normalized" in reasons
    assert "source_identity_not_resolved" in reasons


def test_v2_stat_and_modifier_registry_loaders_and_routes(app, tmp_path):
    reports = build_v2_stat_modifier_reports(_payloads(), _skill_identity_report())
    stat_path = tmp_path / "v2_stat_registry.json"
    modifier_path = tmp_path / "v2_modifier_registry.json"
    stat_path.write_text(json.dumps(reports["stat_registry"]), encoding="utf-8")
    modifier_path.write_text(json.dumps(reports["modifier_registry"]), encoding="utf-8")

    stat_registry = V2StatRegistry(stat_path).load()
    modifier_registry = V2ModifierRegistry(modifier_path).load()
    assert stat_registry.count() == reports["stat_registry"]["summary"]["stat_count"]
    assert modifier_registry.count() == reports["modifier_registry"]["summary"]["modifier_count"]

    app.config["V2_STAT_REGISTRY_PATH"] = str(stat_path)
    app.config["V2_MODIFIER_REGISTRY_PATH"] = str(modifier_path)
    client = app.test_client()

    stats = client.get("/experimental/v2/stats?q=health")
    assert stats.status_code == 200
    stat_id = stats.get_json()["records"][0]["canonical_stat_id"]
    stat_detail = client.get(f"/experimental/v2/stats/{stat_id}")
    assert stat_detail.status_code == 200

    modifiers = client.get("/experimental/v2/modifiers?source_type=affix")
    assert modifiers.status_code == 200
    modifier_id = modifiers.get_json()["records"][0]["canonical_modifier_id"]
    modifier_detail = client.get(f"/experimental/v2/modifiers/{modifier_id}")
    assert modifier_detail.status_code == 200
    debug = client.get("/experimental/v2/modifiers/debug")
    assert debug.status_code == 200
    assert debug.get_json()["debug_summary"]["modifiers"]["production_safe"] is False


def test_v2_modifier_registries_are_not_referenced_by_production_modules():
    root = Path(__file__).resolve().parents[2]
    allowed = {
        root / "backend" / "app" / "routes" / "experimental.py",
        root / "backend" / "app" / "normalization" / "v2" / "modifier_registry.py",
        root / "backend" / "app" / "normalization" / "v2" / "stat_registry.py",
        root / "backend" / "app" / "normalization" / "v2" / "__init__.py",
        root / "backend" / "scripts" / "report_v2_stat_modifier_normalization.py",
        Path(__file__).resolve(),
    }
    needles = ("v2_modifier_registry.json", "v2_stat_registry.json", "V2ModifierRegistry", "V2StatRegistry")
    offenders: list[str] = []
    for path in (root / "backend" / "app").rglob("*.py"):
        if path in allowed or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if any(needle in text for needle in needles):
            offenders.append(str(path.relative_to(root)))

    assert offenders == []


def _payloads() -> dict:
    provenance = {
        "source_path": "test.json",
        "source_id": "source",
        "source_type": "generated_from_game_data",
        "extraction_method": "test",
    }
    return {
        "affix": {
            "records": {
                "affixes": [
                    {
                        "canonical_id": "affix:equipment:1",
                        "display_name": "Health",
                        "support_status": "partial",
                        "trust_level": "generated_from_game_data",
                        "provenance": provenance,
                        "modifier_references": [{"modifier_id": "source:1", "property": "Health", "property_path": "ADDED.Health"}],
                        "tier_ranges": [{"min_value": 1, "max_value": 2, "value_scale": "source_units"}],
                    }
                ]
            }
        },
        "item_implicit": {"records": {"implicits": []}},
        "unique": {
            "records": {
                "uniques": [
                    {
                        "canonical_id": "unique:1",
                        "display_name": "Unique",
                        "support_status": "partial",
                        "trust_level": "generated_from_game_data",
                        "provenance": provenance,
                        "modifier_rows": [{"modifier_id": "unique:1:0", "modifier_type": "INCREASED", "property": "Damage", "property_path": "INCREASED.Damage.Fire", "value_min": 0.1, "value_max": 0.2, "provenance": provenance}],
                    }
                ]
            }
        },
        "set": {"records": {"set_items": [], "set_bonuses": []}},
        "idol": {"records": {"idols": []}},
        "idol_affix": {"records": {"idol_affixes": []}},
        "passive": {
            "records": {
                "passive_nodes": [
                    {
                        "canonical_id": "passive_node:test:1",
                        "display_name": "Passive",
                        "support_status": "partial",
                        "trust_level": "generated_from_game_data",
                        "special_behavior_classification": "partial_modifier",
                        "provenance": provenance,
                        "modifier_rows": [{"row_id": "passive:1", "stat_name": "Intelligence", "value": "+1", "provenance": provenance}],
                    }
                ]
            }
        },
        "skill": {
            "records": {
                "skills": [
                    {
                        "canonical_id": "skill:test",
                        "display_name": "Skill",
                        "support_status": "partial",
                        "trust_level": "generated_from_game_data",
                        "special_behavior_classification": "scripted_runtime_behavior",
                        "provenance": provenance,
                        "cost": {"mana": 3},
                        "cooldown": {},
                        "cast_data": {},
                    }
                ]
            }
        },
        "skill_tree": {"records": {"skill_nodes": []}},
    }


def _skill_identity_report() -> dict:
    return {
        "summary": {
            "top_level_path_match_count": 60,
            "unresolved_reference_count": 2,
            "ambiguous_match_count": 1,
        }
    }
