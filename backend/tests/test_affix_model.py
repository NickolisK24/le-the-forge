"""J6 — Tests for affix_model.py"""

import pytest
from data.models.affix_model import AffixModel


class TestAffixCreation:
    def test_basic_creation(self):
        a = AffixModel(affix_id="fire_res_t1", stat_type="fire_resistance", min_value=10, max_value=20)
        assert a.affix_id == "fire_res_t1"
        assert a.midpoint == 15.0

    def test_equal_min_max_allowed(self):
        a = AffixModel("x", "stat", 10, 10)
        assert a.min_value == a.max_value

    def test_to_dict(self):
        a = AffixModel("a1", "cold_res", 5, 15)
        d = a.to_dict()
        assert d["affix_id"] == "a1"
        assert d["min_value"] == 5


class TestRangeValidation:
    def test_min_greater_than_max_raises(self):
        with pytest.raises(ValueError, match="min_value"):
            AffixModel("x", "s", min_value=50, max_value=10)

    def test_empty_affix_id_raises(self):
        with pytest.raises(ValueError, match="affix_id"):
            AffixModel("", "s", 1, 5)

    def test_midpoint_calculation(self):
        a = AffixModel("x", "s", min_value=0, max_value=100)
        assert a.midpoint == 50.0
