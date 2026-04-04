"""
FP Engine Tests — validates core FP system behavior.

Run with:  python -m pytest backend/tests/test_fp_engine.py -v
       or: cd backend && python -m pytest tests/test_fp_engine.py -v
"""

import sys
import os

# Allow running from repo root or backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from unittest.mock import patch

from app.engines.fp_engine import (
    roll_fp_cost,
    fp_cost_range,
    expected_fp_cost,
    consume_fp,
    log_fp_event,
    apply_fp,
    load_fp_rules,
    roll_base_fp,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_item(fp: int = 20) -> dict:
    return {"forge_potential": fp, "history": []}


# ---------------------------------------------------------------------------
# Test 1 — Basic FP Roll stays in range
# ---------------------------------------------------------------------------

class TestFpRollRange:
    def test_upgrade_stays_in_range(self):
        lo, hi = fp_cost_range("upgrade_affix")
        for _ in range(50):
            cost = roll_fp_cost("upgrade_affix")
            assert lo <= cost <= hi, f"Expected {lo}–{hi}, got {cost}"

    def test_seal_stays_in_range(self):
        lo, hi = fp_cost_range("seal_affix")
        for _ in range(50):
            cost = roll_fp_cost("seal_affix")
            assert lo <= cost <= hi, f"Expected {lo}–{hi}, got {cost}"

    def test_remove_stays_in_range(self):
        lo, hi = fp_cost_range("remove_affix")
        for _ in range(50):
            cost = roll_fp_cost("remove_affix")
            assert lo <= cost <= hi, f"Expected {lo}–{hi}, got {cost}"

    def test_add_affix_stays_in_range(self):
        lo, hi = fp_cost_range("add_affix")
        for _ in range(50):
            cost = roll_fp_cost("add_affix")
            assert lo <= cost <= hi

    def test_unseal_stays_in_range(self):
        lo, hi = fp_cost_range("unseal_affix")
        for _ in range(50):
            cost = roll_fp_cost("unseal_affix")
            assert lo <= cost <= hi

    def test_unknown_action_raises(self):
        with pytest.raises(ValueError, match="Unknown action type"):
            roll_fp_cost("invalid_action")


# ---------------------------------------------------------------------------
# Test 2 — FP Depletion blocks crafting
# ---------------------------------------------------------------------------

class TestFpDepletion:
    def test_craft_until_zero(self):
        item = make_item(fp=10)
        attempts = 0
        while item["forge_potential"] > 0:
            result = apply_fp(item, "upgrade_affix")
            attempts += 1
            if not result["success"]:
                break
            assert item["forge_potential"] >= 0
            if attempts > 100:
                break  # safety

        # Eventually FP should run out
        lo, hi = fp_cost_range("upgrade_affix")
        # After max hi steps at min 1 each, FP should be 0
        assert item["forge_potential"] >= 0

    def test_blocked_when_depleted(self):
        item = make_item(fp=0)
        result = apply_fp(item, "upgrade_affix")
        assert result["success"] is False
        assert "Not enough" in result["reason"]
        assert item["forge_potential"] == 0  # unchanged


# ---------------------------------------------------------------------------
# Test 3 — Exact FP match succeeds
# ---------------------------------------------------------------------------

class TestExactFpMatch:
    def test_exact_match_succeeds(self):
        lo, _ = fp_cost_range("upgrade_affix")
        item = make_item(fp=lo)
        # Force a roll of exactly lo
        with patch("app.engines.fp_engine.random.randint", return_value=lo):
            result = apply_fp(item, "upgrade_affix")
        assert result["success"] is True
        assert item["forge_potential"] == 0

    def test_fp_becomes_zero_is_valid(self):
        lo, _ = fp_cost_range("seal_affix")
        item = make_item(fp=lo)
        with patch("app.engines.fp_engine.random.randint", return_value=lo):
            result = apply_fp(item, "seal_affix")
        assert result["success"] is True
        assert item["forge_potential"] == 0


# ---------------------------------------------------------------------------
# Test 4 — Over-cost is blocked without removing FP
# ---------------------------------------------------------------------------

class TestOverCostPrevention:
    def test_high_roll_blocked(self):
        _, hi = fp_cost_range("seal_affix")
        item = make_item(fp=hi - 1)  # one less than max cost
        with patch("app.engines.fp_engine.random.randint", return_value=hi):
            result = apply_fp(item, "seal_affix")
        assert result["success"] is False
        assert item["forge_potential"] == hi - 1  # unchanged — no FP was removed

    def test_fp_zero_always_blocked(self):
        for action in ["upgrade_affix", "add_affix", "seal_affix", "remove_affix"]:
            item = make_item(fp=0)
            result = apply_fp(item, action)
            assert result["success"] is False
            assert item["forge_potential"] == 0


# ---------------------------------------------------------------------------
# Test 5 — History logging
# ---------------------------------------------------------------------------

class TestHistoryLogging:
    def test_event_logged_on_success(self):
        lo, _ = fp_cost_range("upgrade_affix")
        item = make_item(fp=lo + 5)
        with patch("app.engines.fp_engine.random.randint", return_value=lo):
            apply_fp(item, "upgrade_affix")
        assert len(item["history"]) == 1
        event = item["history"][0]
        assert event["action"] == "upgrade_affix"
        assert event["fp_cost"] == lo
        assert event["remaining_fp"] == item["forge_potential"]

    def test_no_log_on_failure(self):
        item = make_item(fp=0)
        apply_fp(item, "upgrade_affix")
        assert len(item["history"]) == 0

    def test_multiple_events_logged_in_order(self):
        lo, _ = fp_cost_range("add_affix")
        item = make_item(fp=lo * 3)
        with patch("app.engines.fp_engine.random.randint", return_value=lo):
            apply_fp(item, "add_affix")
            apply_fp(item, "add_affix")
        assert len(item["history"]) == 2
        assert item["history"][0]["remaining_fp"] > item["history"][1]["remaining_fp"]


# ---------------------------------------------------------------------------
# Test 6 — Rules file integrity
# ---------------------------------------------------------------------------

class TestRulesFile:
    def test_all_actions_present(self):
        rules = load_fp_rules()
        required = {"upgrade_affix", "add_affix", "seal_affix", "unseal_affix", "remove_affix"}
        assert required.issubset(rules["fp_costs"].keys())

    def test_min_less_than_max(self):
        rules = load_fp_rules()
        for action, costs in rules["fp_costs"].items():
            assert costs["min"] <= costs["max"], f"{action}: min > max"
            assert costs["min"] >= 1, f"{action}: min < 1"

    def test_base_fp_ranges_valid(self):
        rules = load_fp_rules()
        for slot, fp in rules["base_item_fp"].items():
            assert fp["min"] >= 1
            assert fp["min"] <= fp["max"]

    def test_roll_base_fp_in_range(self):
        for slot in ["helmet", "gloves", "wand", "default"]:
            fp = roll_base_fp(slot)
            rules = load_fp_rules()
            base = rules["base_item_fp"].get(slot, rules["base_item_fp"]["default"])
            assert base["min"] <= fp <= base["max"]
