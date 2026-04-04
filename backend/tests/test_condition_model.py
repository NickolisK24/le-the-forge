"""H1 — Condition Model tests."""
import pytest
from conditions.models.condition import Condition, VALID_TYPES, VALID_OPERATORS


class TestConditionCreation:
    def test_valid_health_condition(self):
        c = Condition("low_hp", "target_health_pct", threshold_value=0.5, comparison_operator="lt")
        assert c.condition_id == "low_hp"
        assert c.condition_type == "target_health_pct"
        assert c.threshold_value == 0.5

    def test_valid_buff_condition(self):
        c = Condition("my_buff", "buff_active")
        assert c.condition_type == "buff_active"
        assert c.threshold_value is None

    def test_valid_status_condition(self):
        c = Condition("shocked", "status_present")
        assert c.condition_type == "status_present"

    def test_valid_time_condition(self):
        c = Condition("after_10s", "time_elapsed", threshold_value=10.0, comparison_operator="ge")
        assert c.threshold_value == 10.0

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError, match="Invalid condition_type"):
            Condition("x", "unknown_type", threshold_value=0.5)

    def test_numeric_type_without_threshold_raises(self):
        with pytest.raises(ValueError, match="requires threshold_value"):
            Condition("x", "target_health_pct")

    def test_invalid_operator_raises(self):
        with pytest.raises(ValueError, match="Invalid comparison_operator"):
            Condition("x", "target_health_pct", threshold_value=0.5, comparison_operator="??")

    def test_zero_duration_raises(self):
        with pytest.raises(ValueError, match="duration must be"):
            Condition("x", "buff_active", duration=0.0)

    def test_negative_duration_raises(self):
        with pytest.raises(ValueError, match="duration must be"):
            Condition("x", "buff_active", duration=-1.0)


class TestThresholdComparison:
    def _cond(self, op: str, threshold: float = 0.5):
        return Condition("c", "target_health_pct", threshold_value=threshold, comparison_operator=op)

    def test_lt(self):
        c = self._cond("lt", 0.5)
        assert c.evaluate_numeric(0.4) is True
        assert c.evaluate_numeric(0.5) is False

    def test_le(self):
        c = self._cond("le", 0.5)
        assert c.evaluate_numeric(0.5) is True
        assert c.evaluate_numeric(0.6) is False

    def test_eq(self):
        c = self._cond("eq", 1.0)
        assert c.evaluate_numeric(1.0) is True
        assert c.evaluate_numeric(0.9) is False

    def test_ge(self):
        c = self._cond("ge", 0.5)
        assert c.evaluate_numeric(0.5) is True
        assert c.evaluate_numeric(0.4) is False

    def test_gt(self):
        c = self._cond("gt", 0.5)
        assert c.evaluate_numeric(0.6) is True
        assert c.evaluate_numeric(0.5) is False


class TestConditionSerialization:
    def test_round_trip(self):
        c = Condition("t", "time_elapsed", threshold_value=5.0, comparison_operator="gt", duration=2.0)
        assert Condition.from_dict(c.to_dict()) == c

    def test_buff_round_trip(self):
        c = Condition("my_buff", "buff_active")
        assert Condition.from_dict(c.to_dict()) == c
