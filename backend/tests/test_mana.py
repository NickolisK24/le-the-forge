"""
Tests for Mana Resource System (Step 54).

Validates:
  - ManaPool construction and validation
  - can_afford, spend, regenerate, restore_full
  - InsufficientManaError raised when mana depleted
  - Regeneration caps at max_mana
  - Casting fails then succeeds after regen
"""

import pytest
from app.domain.mana import ManaPool, InsufficientManaError


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestManaPoolConstruction:
    def test_basic_construction(self):
        pool = ManaPool(max_mana=100.0, current_mana=100.0, mana_regeneration_rate=5.0)
        assert pool.max_mana == pytest.approx(100.0)
        assert pool.current_mana == pytest.approx(100.0)
        assert pool.mana_regeneration_rate == pytest.approx(5.0)

    def test_regen_rate_defaults_to_zero(self):
        pool = ManaPool(max_mana=100.0, current_mana=50.0)
        assert pool.mana_regeneration_rate == pytest.approx(0.0)

    def test_zero_max_mana_raises(self):
        with pytest.raises(ValueError, match="max_mana"):
            ManaPool(max_mana=0.0, current_mana=0.0)

    def test_negative_max_mana_raises(self):
        with pytest.raises(ValueError, match="max_mana"):
            ManaPool(max_mana=-10.0, current_mana=0.0)

    def test_negative_current_mana_raises(self):
        with pytest.raises(ValueError, match="current_mana"):
            ManaPool(max_mana=100.0, current_mana=-1.0)

    def test_current_exceeds_max_raises(self):
        with pytest.raises(ValueError, match="current_mana"):
            ManaPool(max_mana=50.0, current_mana=100.0)

    def test_negative_regen_rate_raises(self):
        with pytest.raises(ValueError, match="mana_regeneration_rate"):
            ManaPool(max_mana=100.0, current_mana=50.0, mana_regeneration_rate=-1.0)


# ---------------------------------------------------------------------------
# can_afford
# ---------------------------------------------------------------------------

class TestCanAfford:
    def test_affordable_cost(self):
        pool = ManaPool(max_mana=100.0, current_mana=50.0)
        assert pool.can_afford(50.0) is True

    def test_exact_cost_affordable(self):
        pool = ManaPool(max_mana=100.0, current_mana=30.0)
        assert pool.can_afford(30.0) is True

    def test_over_budget_not_affordable(self):
        pool = ManaPool(max_mana=100.0, current_mana=20.0)
        assert pool.can_afford(21.0) is False

    def test_zero_cost_always_affordable(self):
        pool = ManaPool(max_mana=100.0, current_mana=0.0)
        assert pool.can_afford(0.0) is True


# ---------------------------------------------------------------------------
# spend
# ---------------------------------------------------------------------------

class TestSpend:
    def test_spend_reduces_current(self):
        pool = ManaPool(max_mana=100.0, current_mana=80.0)
        pool.spend(30.0)
        assert pool.current_mana == pytest.approx(50.0)

    def test_spend_to_zero(self):
        pool = ManaPool(max_mana=100.0, current_mana=50.0)
        pool.spend(50.0)
        assert pool.current_mana == pytest.approx(0.0)
        assert pool.is_empty is True

    def test_spend_more_than_available_raises(self):
        pool = ManaPool(max_mana=100.0, current_mana=20.0)
        with pytest.raises(InsufficientManaError):
            pool.spend(30.0)

    def test_spend_exact_amount(self):
        pool = ManaPool(max_mana=100.0, current_mana=40.0)
        pool.spend(40.0)
        assert pool.current_mana == pytest.approx(0.0)

    def test_spend_negative_raises(self):
        pool = ManaPool(max_mana=100.0, current_mana=100.0)
        with pytest.raises(ValueError, match="cost"):
            pool.spend(-10.0)

    def test_insufficient_mana_message(self):
        pool = ManaPool(max_mana=100.0, current_mana=10.0)
        with pytest.raises(InsufficientManaError, match="20"):
            pool.spend(20.0)


# ---------------------------------------------------------------------------
# regenerate
# ---------------------------------------------------------------------------

class TestRegenerate:
    def test_regen_restores_mana(self):
        pool = ManaPool(max_mana=100.0, current_mana=50.0, mana_regeneration_rate=10.0)
        pool.regenerate(2.0)
        assert pool.current_mana == pytest.approx(70.0)

    def test_regen_caps_at_max(self):
        pool = ManaPool(max_mana=100.0, current_mana=95.0, mana_regeneration_rate=10.0)
        pool.regenerate(2.0)
        assert pool.current_mana == pytest.approx(100.0)
        assert pool.is_full is True

    def test_regen_returns_amount_restored(self):
        pool = ManaPool(max_mana=100.0, current_mana=50.0, mana_regeneration_rate=10.0)
        restored = pool.regenerate(3.0)
        assert restored == pytest.approx(30.0)

    def test_regen_capped_return_value(self):
        pool = ManaPool(max_mana=100.0, current_mana=95.0, mana_regeneration_rate=10.0)
        restored = pool.regenerate(2.0)
        assert restored == pytest.approx(5.0)   # capped at remaining headroom

    def test_zero_regen_rate_restores_nothing(self):
        pool = ManaPool(max_mana=100.0, current_mana=50.0, mana_regeneration_rate=0.0)
        pool.regenerate(10.0)
        assert pool.current_mana == pytest.approx(50.0)

    def test_regen_at_full_returns_zero(self):
        pool = ManaPool(max_mana=100.0, current_mana=100.0, mana_regeneration_rate=10.0)
        restored = pool.regenerate(5.0)
        assert restored == pytest.approx(0.0)

    def test_negative_delta_raises(self):
        pool = ManaPool(max_mana=100.0, current_mana=50.0, mana_regeneration_rate=10.0)
        with pytest.raises(ValueError, match="delta"):
            pool.regenerate(-1.0)


# ---------------------------------------------------------------------------
# restore_full
# ---------------------------------------------------------------------------

class TestRestoreFull:
    def test_restores_to_max(self):
        pool = ManaPool(max_mana=100.0, current_mana=10.0)
        pool.restore_full()
        assert pool.current_mana == pytest.approx(100.0)
        assert pool.is_full is True

    def test_restore_full_from_empty(self):
        pool = ManaPool(max_mana=80.0, current_mana=0.0)
        pool.restore_full()
        assert pool.current_mana == pytest.approx(80.0)


# ---------------------------------------------------------------------------
# Integration — cast, deplete, regen, cast again
# ---------------------------------------------------------------------------

class TestManaCycle:
    def test_cast_fails_then_succeeds_after_regen(self):
        pool = ManaPool(max_mana=100.0, current_mana=20.0, mana_regeneration_rate=10.0)
        # Can't cast 30-mana skill
        assert pool.can_afford(30.0) is False
        with pytest.raises(InsufficientManaError):
            pool.spend(30.0)
        # Regen 1s → 30 mana
        pool.regenerate(1.0)
        assert pool.can_afford(30.0) is True
        pool.spend(30.0)
        assert pool.current_mana == pytest.approx(0.0)

    def test_sustained_casting_depletes_mana(self):
        pool = ManaPool(max_mana=100.0, current_mana=100.0, mana_regeneration_rate=5.0)
        # Each cast: spend 30, regen 1s (5 mana) → net −25 per cycle
        # 100 → 75 → 50 → 25 (after 3 cycles); 4th spend of 30 fails
        for _ in range(3):
            pool.spend(30.0)
            pool.regenerate(1.0)
        assert pool.current_mana == pytest.approx(25.0)
        with pytest.raises(InsufficientManaError):
            pool.spend(30.0)
