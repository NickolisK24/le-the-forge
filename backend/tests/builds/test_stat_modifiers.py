"""
E2 — Tests for StatModifierEngine and FinalModifierStack.
"""

import pytest
from builds.stat_modifiers import StatModifier, StatModifierEngine, FinalModifierStack, ModifierType


class TestStatModifier:
    def test_creates_flat_modifier(self):
        m = StatModifier("base_damage", 50.0, ModifierType.FLAT)
        assert m.stat_key == "base_damage"
        assert m.value == 50.0
        assert m.modifier_type == ModifierType.FLAT

    def test_creates_percent_modifier(self):
        m = StatModifier("spell_damage_pct", 20.0, ModifierType.PERCENT)
        assert m.modifier_type == ModifierType.PERCENT

    def test_default_type_is_flat(self):
        m = StatModifier("base_damage", 10.0)
        assert m.modifier_type == ModifierType.FLAT

    def test_roundtrip(self):
        m = StatModifier("crit_chance", 0.05, ModifierType.FLAT)
        m2 = StatModifier.from_dict(m.to_dict())
        assert m2.stat_key == m.stat_key
        assert m2.value == m.value
        assert m2.modifier_type == m.modifier_type


class TestStatModifierEngine:
    def test_empty_stack_has_no_modifiers(self):
        eng = StatModifierEngine()
        stack = eng.compute()
        assert stack.flat == {}
        assert stack.percent == {}

    def test_flat_stacking(self):
        eng = StatModifierEngine()
        eng.add_modifier(StatModifier("base_damage", 100.0))
        eng.add_modifier(StatModifier("base_damage", 50.0))
        stack = eng.compute()
        assert stack.flat["base_damage"] == 150.0

    def test_percent_stacking(self):
        eng = StatModifierEngine()
        eng.add_modifier(StatModifier("spell_damage_pct", 20.0, ModifierType.PERCENT))
        eng.add_modifier(StatModifier("spell_damage_pct", 15.0, ModifierType.PERCENT))
        stack = eng.compute()
        assert stack.percent["spell_damage_pct"] == 35.0

    def test_mixed_stacking_does_not_cross_contaminate(self):
        eng = StatModifierEngine()
        eng.add_modifier(StatModifier("base_damage", 100.0, ModifierType.FLAT))
        eng.add_modifier(StatModifier("base_damage", 20.0,  ModifierType.PERCENT))
        stack = eng.compute()
        assert stack.flat["base_damage"] == 100.0
        assert stack.percent["base_damage"] == 20.0

    def test_negative_modifiers_safe(self):
        eng = StatModifierEngine()
        eng.add_modifier(StatModifier("base_damage", 100.0))
        eng.add_modifier(StatModifier("base_damage", -30.0))
        stack = eng.compute()
        assert stack.flat["base_damage"] == 70.0

    def test_stacking_is_deterministic(self):
        mods = [StatModifier(f"stat_{i}", float(i)) for i in range(20)]
        eng = StatModifierEngine()
        eng.add_modifiers(mods)
        s1 = eng.compute()
        s2 = eng.compute()
        assert s1.flat == s2.flat

    def test_reset_clears_modifiers(self):
        eng = StatModifierEngine()
        eng.add_modifier(StatModifier("base_damage", 100.0))
        assert len(eng) == 1
        eng.reset()
        assert len(eng) == 0
        assert eng.compute().flat == {}


class TestFinalModifierStack:
    def test_apply_to_dict_flat(self):
        stack = FinalModifierStack(flat={"base_damage": 200.0})
        result = stack.apply_to({"base_damage": 100.0})
        assert result["base_damage"] == 300.0

    def test_apply_to_dict_percent(self):
        stack = FinalModifierStack(percent={"base_damage": 50.0})
        result = stack.apply_to({"base_damage": 100.0})
        assert result["base_damage"] == 150.0

    def test_apply_to_missing_key_defaults_to_zero(self):
        stack = FinalModifierStack(flat={"new_stat": 5.0})
        result = stack.apply_to({})
        assert result["new_stat"] == 5.0
