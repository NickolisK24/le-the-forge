"""
Tests for validators — Upgrade 8

Covers: validate_build, validate_item, validate_affix_combination,
validate_stat_ranges, Violation, ValidationResult, all error codes.
"""

from __future__ import annotations

import pytest

from app.engines.validators import (
    validate_build,
    validate_item,
    validate_affix_combination,
    validate_stat_ranges,
    Violation,
    ValidationResult,
    VALID_SLOTS,
    VALID_CLASSES,
    VALID_MASTERIES,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _item(**kw) -> dict:
    base = {
        "slot_type": "helmet",
        "forging_potential": 10,
        "implicit_stats": {},
        "affixes": [],
        "sealed_affix": None,
    }
    base.update(kw)
    return base


def _build(**kw) -> dict:
    base = {
        "character_class": "Mage",
        "mastery": "Sorcerer",
        "passive_tree": [1, 2, 3],
        "gear": [],
        "primary_skill": "Fireball",
    }
    base.update(kw)
    return base


def _affix(name="Added Health", tier=1, affix_type="prefix") -> dict:
    return {"name": name, "tier": tier, "type": affix_type}


# ---------------------------------------------------------------------------
# 1. ValidationResult structure
# ---------------------------------------------------------------------------

class TestValidationResult:
    def test_default_valid_true(self):
        vr = ValidationResult(valid=True)
        assert vr.valid is True

    def test_add_error_sets_valid_false(self):
        vr = ValidationResult(valid=True)
        vr.add_error("CODE", "msg")
        assert vr.valid is False

    def test_add_error_appends_to_errors(self):
        vr = ValidationResult(valid=True)
        vr.add_error("CODE", "msg", "field")
        assert len(vr.errors) == 1

    def test_add_warning_does_not_set_valid_false(self):
        vr = ValidationResult(valid=True)
        vr.add_warning("CODE", "msg")
        assert vr.valid is True

    def test_add_warning_appends_to_warnings(self):
        vr = ValidationResult(valid=True)
        vr.add_warning("CODE", "msg")
        assert len(vr.warnings) == 1

    def test_merge_errors(self):
        vr1 = ValidationResult(valid=True)
        vr2 = ValidationResult(valid=False)
        vr2.add_error("E1", "err")
        vr1.merge(vr2)
        assert len(vr1.errors) == 1
        assert vr1.valid is False

    def test_merge_warnings(self):
        vr1 = ValidationResult(valid=True)
        vr2 = ValidationResult(valid=True)
        vr2.add_warning("W1", "warn")
        vr1.merge(vr2)
        assert len(vr1.warnings) == 1
        assert vr1.valid is True

    def test_to_dict_has_valid_key(self):
        vr = ValidationResult(valid=True)
        assert "valid" in vr.to_dict()

    def test_to_dict_has_errors_key(self):
        vr = ValidationResult(valid=True)
        assert "errors" in vr.to_dict()

    def test_to_dict_has_warnings_key(self):
        vr = ValidationResult(valid=True)
        assert "warnings" in vr.to_dict()

    def test_to_dict_valid_true(self):
        vr = ValidationResult(valid=True)
        assert vr.to_dict()["valid"] is True

    def test_multiple_errors(self):
        vr = ValidationResult(valid=True)
        vr.add_error("E1", "msg1")
        vr.add_error("E2", "msg2")
        assert len(vr.errors) == 2

    def test_multiple_warnings(self):
        vr = ValidationResult(valid=True)
        vr.add_warning("W1", "msg1")
        vr.add_warning("W2", "msg2")
        assert len(vr.warnings) == 2


# ---------------------------------------------------------------------------
# 2. Violation structure
# ---------------------------------------------------------------------------

class TestViolation:
    def test_violation_has_code(self):
        v = Violation("CODE", "msg", "field", "error")
        assert v.code == "CODE"

    def test_violation_has_message(self):
        v = Violation("CODE", "msg", "field", "error")
        assert v.message == "msg"

    def test_violation_has_field(self):
        v = Violation("CODE", "msg", "field.path", "warning")
        assert v.field == "field.path"

    def test_violation_has_severity(self):
        v = Violation("CODE", "msg", "field", "error")
        assert v.severity == "error"

    def test_to_dict_has_all_keys(self):
        v = Violation("CODE", "msg", "field", "warning")
        d = v.to_dict()
        assert {"code", "message", "field", "severity"} == set(d.keys())

    def test_to_dict_code_correct(self):
        v = Violation("SLOT_MISSING", "msg", "f", "error")
        assert v.to_dict()["code"] == "SLOT_MISSING"


# ---------------------------------------------------------------------------
# 3. validate_item() — valid items
# ---------------------------------------------------------------------------

class TestValidateItemValid:
    @pytest.mark.parametrize("slot", sorted(VALID_SLOTS))
    def test_valid_slots_pass(self, slot):
        r = validate_item(_item(slot_type=slot))
        # Slots validation passes
        slot_errors = [e for e in r.errors if e.code == "SLOT_INVALID"]
        assert len(slot_errors) == 0

    def test_empty_affixes_valid(self):
        r = validate_item(_item(affixes=[]))
        assert r.valid

    def test_valid_affix_tier(self):
        r = validate_item(_item(affixes=[_affix(tier=1)]))
        tier_errors = [e for e in r.errors if "TIER" in e.code]
        assert len(tier_errors) == 0

    def test_max_tier_valid(self):
        r = validate_item(_item(affixes=[_affix(tier=7)]))
        tier_errors = [e for e in r.errors if e.code == "TIER_ABOVE_MAX"]
        assert len(tier_errors) == 0

    def test_zero_fp_valid(self):
        r = validate_item(_item(forging_potential=0))
        fp_errors = [e for e in r.errors if e.code == "FP_NEGATIVE"]
        assert len(fp_errors) == 0

    def test_high_fp_valid(self):
        r = validate_item(_item(forging_potential=100))
        fp_errors = [e for e in r.errors if e.code == "FP_NEGATIVE"]
        assert len(fp_errors) == 0

    def test_numeric_implicit_stat_valid(self):
        r = validate_item(_item(implicit_stats={"health": 50.0}))
        impl_errors = [e for e in r.errors if e.code == "IMPLICIT_NOT_NUMERIC"]
        assert len(impl_errors) == 0

    def test_valid_sealed_affix_dict(self):
        r = validate_item(_item(sealed_affix={"name": "Added Health", "tier": 1}))
        seal_errors = [e for e in r.errors if e.code == "SEAL_INVALID"]
        assert len(seal_errors) == 0

    def test_null_sealed_affix_valid(self):
        r = validate_item(_item(sealed_affix=None))
        seal_errors = [e for e in r.errors if e.code == "SEAL_INVALID"]
        assert len(seal_errors) == 0


# ---------------------------------------------------------------------------
# 4. validate_item() — error cases
# ---------------------------------------------------------------------------

class TestValidateItemErrors:
    def test_missing_slot_is_error(self):
        item = {"forging_potential": 10, "affixes": []}
        r = validate_item(item)
        assert not r.valid
        assert any(e.code == "SLOT_MISSING" for e in r.errors)

    def test_invalid_slot_is_error(self):
        r = validate_item(_item(slot_type="invalid_slot_xyz"))
        assert not r.valid
        assert any(e.code == "SLOT_INVALID" for e in r.errors)

    def test_negative_fp_is_error(self):
        r = validate_item(_item(forging_potential=-1))
        assert not r.valid
        assert any(e.code == "FP_NEGATIVE" for e in r.errors)

    def test_tier_below_min_is_error(self):
        r = validate_item(_item(affixes=[_affix(tier=0)]))
        assert any(e.code == "TIER_BELOW_MIN" for e in r.errors)

    def test_tier_above_max_is_error(self):
        r = validate_item(_item(affixes=[_affix(tier=8)]))
        assert any(e.code == "TIER_ABOVE_MAX" for e in r.errors)

    def test_non_numeric_implicit_is_error(self):
        r = validate_item(_item(implicit_stats={"health": "50"}))
        assert any(e.code == "IMPLICIT_NOT_NUMERIC" for e in r.errors)

    def test_sealed_affix_not_dict_is_error(self):
        r = validate_item(_item(sealed_affix="not_a_dict"))
        assert any(e.code == "SEAL_INVALID" for e in r.errors)

    def test_prefix_overflow(self):
        prefixes = [_affix(f"Affix{i}", tier=1) for i in range(4)]
        r = validate_item({"slot_type": "helmet", "forging_potential": 10,
                           "prefixes": prefixes, "suffixes": []})
        assert any(e.code == "PREFIX_OVERFLOW" for e in r.errors)

    def test_suffix_overflow(self):
        suffixes = [_affix(f"SuffixAffix{i}", tier=1, affix_type="suffix") for i in range(4)]
        r = validate_item({"slot_type": "helmet", "forging_potential": 10,
                           "prefixes": [], "suffixes": suffixes})
        assert any(e.code == "SUFFIX_OVERFLOW" for e in r.errors)

    def test_missing_fp_adds_warning(self):
        item = {"slot_type": "helmet", "affixes": []}
        r = validate_item(item)
        assert any(w.code == "FP_MISSING" for w in r.warnings)

    @pytest.mark.parametrize("bad_slot", [
        "not_a_slot", "HELMET", "123", "chest_armor", "main_hand",
    ])
    def test_various_invalid_slots(self, bad_slot):
        r = validate_item(_item(slot_type=bad_slot))
        assert any(e.code == "SLOT_INVALID" for e in r.errors)

    @pytest.mark.parametrize("tier", [0, -1, -5, 8, 9, 10, 100])
    def test_invalid_tier_values(self, tier):
        r = validate_item(_item(affixes=[_affix(tier=tier)]))
        tier_errors = [e for e in r.errors if "TIER" in e.code]
        assert len(tier_errors) > 0


# ---------------------------------------------------------------------------
# 5. validate_item() — slot index in field path
# ---------------------------------------------------------------------------

class TestValidateItemSlotIndex:
    def test_slot_index_0_in_field_path(self):
        r = validate_item(_item(slot_type="bad_slot"), slot_index=0)
        slot_error = next(e for e in r.errors if e.code == "SLOT_INVALID")
        assert "gear[0]" in slot_error.field

    def test_slot_index_3_in_field_path(self):
        r = validate_item(_item(slot_type="bad_slot"), slot_index=3)
        slot_error = next(e for e in r.errors if e.code == "SLOT_INVALID")
        assert "gear[3]" in slot_error.field


# ---------------------------------------------------------------------------
# 6. validate_build() — valid builds
# ---------------------------------------------------------------------------

class TestValidateBuildValid:
    def test_minimal_valid_build(self):
        b = _build()
        r = validate_build(b)
        assert r.valid

    def test_empty_passive_tree_valid(self):
        r = validate_build(_build(passive_tree=[]))
        assert r.valid

    def test_empty_gear_valid(self):
        r = validate_build(_build(gear=[]))
        assert r.valid

    @pytest.mark.parametrize("char_class", sorted(VALID_CLASSES))
    def test_all_known_classes_valid(self, char_class):
        mastery = list(VALID_MASTERIES[char_class])[0] if char_class in VALID_MASTERIES else ""
        r = validate_build(_build(character_class=char_class, mastery=mastery))
        class_errors = [e for e in r.errors if "CLASS" in e.code]
        assert len(class_errors) == 0

    def test_passive_tree_as_ints_valid(self):
        r = validate_build(_build(passive_tree=[1, 2, 3]))
        assert r.valid

    def test_passive_tree_as_dicts_valid(self):
        r = validate_build(_build(passive_tree=[{"id": 1}, {"id": 2}]))
        assert r.valid

    def test_primary_skill_string_valid(self):
        r = validate_build(_build(primary_skill="Fireball"))
        assert r.valid


# ---------------------------------------------------------------------------
# 7. validate_build() — error cases
# ---------------------------------------------------------------------------

class TestValidateBuildErrors:
    def test_missing_class_is_error(self):
        b = _build()
        del b["character_class"]
        r = validate_build(b)
        assert not r.valid
        assert any(e.code == "CLASS_MISSING" for e in r.errors)

    def test_mastery_mismatch_is_error(self):
        r = validate_build(_build(character_class="Mage", mastery="Paladin"))
        assert any(e.code == "MASTERY_MISMATCH" for e in r.errors)

    def test_passive_tree_not_list_is_error(self):
        r = validate_build(_build(passive_tree="not a list"))
        assert any(e.code == "PASSIVE_NOT_LIST" for e in r.errors)

    def test_passive_tree_overflow_is_error(self):
        r = validate_build(_build(passive_tree=list(range(200))))
        assert any(e.code == "PASSIVE_OVERFLOW" for e in r.errors)

    def test_gear_not_list_is_error(self):
        r = validate_build(_build(gear="not a list"))
        assert any(e.code == "GEAR_NOT_LIST" for e in r.errors)

    def test_gear_item_not_dict_is_error(self):
        r = validate_build(_build(gear=["not a dict"]))
        assert any(e.code == "ITEM_NOT_DICT" for e in r.errors)

    def test_invalid_primary_skill_type_is_error(self):
        r = validate_build(_build(primary_skill=123))
        assert any(e.code == "SKILL_NOT_STRING" for e in r.errors)

    def test_unknown_class_is_warning(self):
        r = validate_build(_build(character_class="UnknownClass"))
        assert any(w.code == "CLASS_UNKNOWN" for w in r.warnings)

    def test_duplicate_gear_slot_is_warning(self):
        gear = [_item(slot_type="helmet"), _item(slot_type="helmet")]
        r = validate_build(_build(gear=gear))
        assert any(w.code == "SLOT_DUPLICATE" for w in r.warnings)

    def test_passive_node_dict_no_id_is_warning(self):
        r = validate_build(_build(passive_tree=[{"name": "test"}]))
        assert any(w.code == "NODE_NO_ID" for w in r.warnings)

    def test_passive_node_invalid_type_is_error(self):
        r = validate_build(_build(passive_tree=[3.14]))
        assert any(e.code == "NODE_INVALID_TYPE" for e in r.errors)

    @pytest.mark.parametrize("char_class,bad_mastery", [
        ("Mage", "Bladedancer"),
        ("Sentinel", "Lich"),
        ("Rogue", "Paladin"),
        ("Primalist", "Sorcerer"),
        ("Acolyte", "Forge Guard"),
    ])
    def test_mastery_mismatch_per_class(self, char_class, bad_mastery):
        r = validate_build(_build(character_class=char_class, mastery=bad_mastery))
        assert any(e.code == "MASTERY_MISMATCH" for e in r.errors)


# ---------------------------------------------------------------------------
# 8. validate_affix_combination()
# ---------------------------------------------------------------------------

class TestValidateAffixCombination:
    def test_empty_affixes_valid(self):
        r = validate_affix_combination([])
        assert r.valid

    def test_single_prefix_valid(self):
        r = validate_affix_combination([_affix()])
        assert r.valid

    def test_three_prefixes_valid(self):
        affixes = [_affix(f"Prefix{i}") for i in range(3)]
        r = validate_affix_combination(affixes)
        assert r.valid

    def test_three_suffixes_valid(self):
        affixes = [_affix(f"Suffix{i}", affix_type="suffix") for i in range(3)]
        r = validate_affix_combination(affixes)
        assert r.valid

    def test_duplicate_name_is_error(self):
        affixes = [_affix("Same Name"), _affix("Same Name")]
        r = validate_affix_combination(affixes)
        assert any(e.code == "AFFIX_DUPLICATE" for e in r.errors)

    def test_prefix_overflow_is_error(self):
        affixes = [_affix(f"Prefix{i}") for i in range(4)]
        r = validate_affix_combination(affixes)
        assert any(e.code == "PREFIX_OVERFLOW" for e in r.errors)

    def test_suffix_overflow_is_error(self):
        affixes = [_affix(f"Suffix{i}", affix_type="suffix") for i in range(4)]
        r = validate_affix_combination(affixes)
        assert any(e.code == "SUFFIX_OVERFLOW" for e in r.errors)

    def test_tier_below_min_is_error(self):
        r = validate_affix_combination([_affix(tier=0)])
        assert any(e.code == "TIER_BELOW_MIN" for e in r.errors)

    def test_tier_above_max_is_error(self):
        r = validate_affix_combination([_affix(tier=8)])
        assert any(e.code == "TIER_ABOVE_MAX" for e in r.errors)

    @pytest.mark.parametrize("tier", [1, 2, 3, 4, 5, 6, 7])
    def test_valid_tiers(self, tier):
        r = validate_affix_combination([_affix(tier=tier)])
        tier_errors = [e for e in r.errors if "TIER" in e.code]
        assert len(tier_errors) == 0

    @pytest.mark.parametrize("n_prefixes,n_suffixes,should_fail", [
        (0, 0, False), (1, 0, False), (3, 3, False),
        (4, 0, True), (0, 4, True), (4, 4, True),
    ])
    def test_prefix_suffix_combinations(self, n_prefixes, n_suffixes, should_fail):
        affixes = (
            [_affix(f"P{i}") for i in range(n_prefixes)] +
            [_affix(f"S{i}", affix_type="suffix") for i in range(n_suffixes)]
        )
        r = validate_affix_combination(affixes)
        has_overflow = any(e.code in ("PREFIX_OVERFLOW", "SUFFIX_OVERFLOW") for e in r.errors)
        assert has_overflow == should_fail


# ---------------------------------------------------------------------------
# 9. validate_stat_ranges()
# ---------------------------------------------------------------------------

class TestValidateStatRanges:
    def test_empty_stats_valid(self):
        r = validate_stat_ranges({})
        assert r.valid

    def test_positive_max_health_valid(self):
        r = validate_stat_ranges({"max_health": 500.0})
        assert r.valid

    def test_zero_max_health_valid(self):
        r = validate_stat_ranges({"max_health": 0.0})
        assert r.valid

    def test_negative_max_health_is_error(self):
        r = validate_stat_ranges({"max_health": -1.0})
        assert any(e.code == "STAT_NEGATIVE" for e in r.errors)

    @pytest.mark.parametrize("stat", [
        "max_health", "armour", "dodge_rating", "ward",
        "base_damage", "attack_speed", "crit_multiplier",
    ])
    def test_negative_non_negative_stats_error(self, stat):
        r = validate_stat_ranges({stat: -0.001})
        assert any(e.code == "STAT_NEGATIVE" for e in r.errors)

    @pytest.mark.parametrize("stat", [
        "max_health", "armour", "dodge_rating", "ward",
        "base_damage", "attack_speed", "crit_multiplier",
    ])
    def test_zero_non_negative_stats_valid(self, stat):
        r = validate_stat_ranges({stat: 0.0})
        non_neg_errors = [e for e in r.errors if e.code == "STAT_NEGATIVE" and e.field == stat]
        assert len(non_neg_errors) == 0

    def test_crit_chance_in_range_valid(self):
        r = validate_stat_ranges({"crit_chance": 0.5})
        assert r.valid

    def test_crit_chance_zero_valid(self):
        r = validate_stat_ranges({"crit_chance": 0.0})
        assert r.valid

    def test_crit_chance_one_valid(self):
        r = validate_stat_ranges({"crit_chance": 1.0})
        assert r.valid

    def test_crit_chance_above_1_is_error(self):
        r = validate_stat_ranges({"crit_chance": 1.5})
        assert any(e.code == "STAT_OUT_OF_RANGE" for e in r.errors)

    def test_crit_chance_negative_is_error(self):
        r = validate_stat_ranges({"crit_chance": -0.1})
        assert any(e.code == "STAT_OUT_OF_RANGE" for e in r.errors)

    @pytest.mark.parametrize("res", [
        "fire_res", "cold_res", "lightning_res", "void_res",
        "necrotic_res", "physical_res", "poison_res",
    ])
    def test_normal_resistance_valid(self, res):
        r = validate_stat_ranges({res: 50.0})
        res_warnings = [w for w in r.warnings if w.code == "RESISTANCE_EXTREME" and w.field == res]
        assert len(res_warnings) == 0

    @pytest.mark.parametrize("res", [
        "fire_res", "cold_res", "lightning_res", "void_res",
    ])
    def test_extreme_resistance_warning(self, res):
        r = validate_stat_ranges({res: 200.0})
        assert any(w.code == "RESISTANCE_EXTREME" and w.field == res for w in r.warnings)

    @pytest.mark.parametrize("res", [
        "fire_res", "cold_res", "lightning_res",
    ])
    def test_extreme_negative_resistance_warning(self, res):
        r = validate_stat_ranges({res: -200.0})
        assert any(w.code == "RESISTANCE_EXTREME" for w in r.warnings)

    def test_valid_full_stats_dict(self):
        stats = {
            "max_health": 1000.0,
            "armour": 500.0,
            "dodge_rating": 200.0,
            "crit_chance": 0.05,
            "crit_multiplier": 1.5,
            "fire_res": 50.0,
            "cold_res": 30.0,
        }
        r = validate_stat_ranges(stats)
        assert r.valid

    @pytest.mark.parametrize("crit", [0.0, 0.1, 0.25, 0.5, 0.75, 1.0])
    def test_crit_chance_range(self, crit):
        r = validate_stat_ranges({"crit_chance": crit})
        range_errors = [e for e in r.errors if e.code == "STAT_OUT_OF_RANGE"]
        assert len(range_errors) == 0


# ---------------------------------------------------------------------------
# 10. Error code completeness
# ---------------------------------------------------------------------------

class TestErrorCodes:
    def test_slot_missing_code(self):
        r = validate_item({"forging_potential": 10, "affixes": []})
        assert any(e.code == "SLOT_MISSING" for e in r.errors)

    def test_slot_invalid_code(self):
        r = validate_item(_item(slot_type="xyz"))
        assert any(e.code == "SLOT_INVALID" for e in r.errors)

    def test_fp_negative_code(self):
        r = validate_item(_item(forging_potential=-5))
        assert any(e.code == "FP_NEGATIVE" for e in r.errors)

    def test_tier_below_min_code(self):
        r = validate_item(_item(affixes=[_affix(tier=0)]))
        assert any(e.code == "TIER_BELOW_MIN" for e in r.errors)

    def test_tier_above_max_code(self):
        r = validate_item(_item(affixes=[_affix(tier=9)]))
        assert any(e.code == "TIER_ABOVE_MAX" for e in r.errors)

    def test_class_missing_code(self):
        b = _build()
        del b["character_class"]
        r = validate_build(b)
        assert any(e.code == "CLASS_MISSING" for e in r.errors)

    def test_mastery_mismatch_code(self):
        r = validate_build(_build(character_class="Mage", mastery="Paladin"))
        assert any(e.code == "MASTERY_MISMATCH" for e in r.errors)

    def test_passive_overflow_code(self):
        r = validate_build(_build(passive_tree=list(range(200))))
        assert any(e.code == "PASSIVE_OVERFLOW" for e in r.errors)

    def test_affix_duplicate_code(self):
        r = validate_affix_combination([_affix("Same"), _affix("Same")])
        assert any(e.code == "AFFIX_DUPLICATE" for e in r.errors)

    def test_stat_negative_code(self):
        r = validate_stat_ranges({"max_health": -1.0})
        assert any(e.code == "STAT_NEGATIVE" for e in r.errors)

    def test_stat_out_of_range_code(self):
        r = validate_stat_ranges({"crit_chance": 2.0})
        assert any(e.code == "STAT_OUT_OF_RANGE" for e in r.errors)

    def test_resistance_extreme_code(self):
        r = validate_stat_ranges({"fire_res": 999.0})
        assert any(w.code == "RESISTANCE_EXTREME" for w in r.warnings)


# ---------------------------------------------------------------------------
# 11. to_dict() serializable
# ---------------------------------------------------------------------------

class TestToDictSerializable:
    def test_validate_build_to_dict(self):
        import json
        r = validate_build(_build())
        json.dumps(r.to_dict())  # should not raise

    def test_validate_item_to_dict(self):
        import json
        r = validate_item(_item())
        json.dumps(r.to_dict())

    def test_validate_affix_combo_to_dict(self):
        import json
        r = validate_affix_combination([_affix()])
        json.dumps(r.to_dict())

    def test_validate_stat_ranges_to_dict(self):
        import json
        r = validate_stat_ranges({"max_health": 1000.0})
        json.dumps(r.to_dict())


# ---------------------------------------------------------------------------
# 12. Severity levels
# ---------------------------------------------------------------------------

class TestSeverity:
    def test_error_severity_string(self):
        vr = ValidationResult(valid=True)
        vr.add_error("CODE", "msg", "field")
        assert vr.errors[0].severity == "error"

    def test_warning_severity_string(self):
        vr = ValidationResult(valid=True)
        vr.add_warning("CODE", "msg", "field")
        assert vr.warnings[0].severity == "warning"

    def test_violations_in_to_dict(self):
        vr = ValidationResult(valid=True)
        vr.add_error("E1", "msg", "f")
        vr.add_warning("W1", "msg", "f")
        d = vr.to_dict()
        assert d["errors"][0]["severity"] == "error"
        assert d["warnings"][0]["severity"] == "warning"


# ---------------------------------------------------------------------------
# 13. VALID_SLOTS constant
# ---------------------------------------------------------------------------

class TestValidSlots:
    def test_valid_slots_nonempty(self):
        assert len(VALID_SLOTS) > 0

    def test_helmet_in_valid_slots(self):
        assert "helmet" in VALID_SLOTS

    def test_ring_in_valid_slots(self):
        assert "ring" in VALID_SLOTS

    def test_amulet_in_valid_slots(self):
        assert "amulet" in VALID_SLOTS

    def test_boots_in_valid_slots(self):
        assert "boots" in VALID_SLOTS

    @pytest.mark.parametrize("slot", ["helmet", "body", "gloves", "boots", "belt",
                                       "ring", "amulet", "relic"])
    def test_core_gear_slots_present(self, slot):
        assert slot in VALID_SLOTS


# ---------------------------------------------------------------------------
# 14. VALID_CLASSES constant
# ---------------------------------------------------------------------------

class TestValidClasses:
    @pytest.mark.parametrize("cls", ["Mage", "Sentinel", "Rogue", "Primalist", "Acolyte"])
    def test_core_classes_present(self, cls):
        assert cls in VALID_CLASSES

    def test_valid_classes_nonempty(self):
        assert len(VALID_CLASSES) > 0


# ---------------------------------------------------------------------------
# 15. Build validation integration
# ---------------------------------------------------------------------------

class TestBuildValidationIntegration:
    def test_valid_build_no_errors(self):
        b = _build()
        r = validate_build(b)
        assert len(r.errors) == 0

    def test_build_with_valid_gear(self):
        gear = [_item(slot_type="helmet"), _item(slot_type="boots")]
        r = validate_build(_build(gear=gear))
        assert r.valid

    def test_build_with_invalid_gear_item_fails(self):
        gear = [_item(slot_type="invalid_slot_xyz")]
        r = validate_build(_build(gear=gear))
        assert not r.valid

    def test_build_with_multiple_errors(self):
        b = {
            "character_class": "",
            "passive_tree": "not a list",
            "gear": "not a list",
        }
        r = validate_build(b)
        assert len(r.errors) >= 2

    def test_result_to_dict_valid_true_for_good_build(self):
        d = validate_build(_build()).to_dict()
        assert d["valid"] is True

    def test_result_to_dict_valid_false_for_bad_build(self):
        b = _build()
        del b["character_class"]
        d = validate_build(b).to_dict()
        assert d["valid"] is False
