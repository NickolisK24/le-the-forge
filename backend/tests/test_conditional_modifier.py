"""H3 — Conditional Modifier Model tests."""
import pytest
from conditions.models.condition import Condition
from modifiers.models.conditional_modifier import ConditionalModifier


def _condition(ctype="buff_active", cid="test_buff"):
    return Condition(cid, ctype)


def _modifier(**kwargs) -> ConditionalModifier:
    defaults = dict(
        modifier_id="m1",
        stat_target="spell_damage_pct",
        value=20.0,
        modifier_type="additive",
        condition=_condition(),
    )
    defaults.update(kwargs)
    return ConditionalModifier(**defaults)


class TestModifierCreation:
    def test_valid_additive(self):
        m = _modifier(modifier_type="additive")
        assert m.modifier_id == "m1"
        assert m.value == 20.0

    def test_valid_multiplicative(self):
        m = _modifier(modifier_type="multiplicative")
        assert m.modifier_type == "multiplicative"

    def test_valid_override(self):
        m = _modifier(modifier_type="override")
        assert m.modifier_type == "override"

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError, match="Invalid modifier_type"):
            _modifier(modifier_type="unknown")

    def test_empty_id_raises(self):
        with pytest.raises(ValueError, match="modifier_id"):
            _modifier(modifier_id="")

    def test_empty_stat_target_raises(self):
        with pytest.raises(ValueError, match="stat_target"):
            _modifier(stat_target="")


class TestConditionLinking:
    def test_condition_attached(self):
        cond = Condition("low_hp", "target_health_pct", threshold_value=0.5, comparison_operator="lt")
        m = _modifier(condition=cond)
        assert m.condition.condition_id == "low_hp"


class TestSerialization:
    def test_round_trip(self):
        cond = Condition("shock", "status_present")
        m = ConditionalModifier("m2", "crit_chance", 10.0, "additive", cond)
        assert ConditionalModifier.from_dict(m.to_dict()) == m
