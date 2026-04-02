"""
Encounter Stability Tests (Step 110).

Validates long-run correctness, memory growth bounds, and numerical
stability across extreme damage scales and fight durations.
"""

import tracemalloc

import pytest

from encounter.enemy import EncounterEnemy
from encounter.multi_target import HitDistribution, MultiHitConfig
from encounter.state_machine import EncounterConfig, EncounterMachine


def _hit(dist=HitDistribution.SINGLE):
    return MultiHitConfig(distribution=dist, rng_hit=0.0, rng_crit=99.0)


def _immortal(name: str = "d") -> EncounterEnemy:
    """Enemy with near-infinite health that won't die during tests."""
    return EncounterEnemy(
        max_health=1e12, current_health=1e12, armor=0.0, name=name
    )


class TestExtendedFights:
    """Correctness properties hold over very long fights."""

    def test_damage_accounting_extended(self):
        """total_damage == sum(damage_per_tick) over a 600-second fight."""
        cfg = EncounterConfig(
            enemies=[_immortal()],
            fight_duration=600.0,
            tick_size=0.1,
            base_damage=100.0,
            hit_config=_hit(),
        )
        r = EncounterMachine(cfg).run()
        assert r.total_damage == pytest.approx(sum(r.damage_per_tick), rel=1e-9)

    def test_ticks_match_damage_list_extended(self):
        """len(damage_per_tick) == ticks_simulated over a long fight."""
        cfg = EncounterConfig(
            enemies=[_immortal()],
            fight_duration=300.0,
            tick_size=0.1,
            base_damage=50.0,
            hit_config=_hit(),
        )
        r = EncounterMachine(cfg).run()
        assert len(r.damage_per_tick) == r.ticks_simulated

    def test_no_negative_damage_extended(self):
        """No tick ever records negative damage."""
        cfg = EncounterConfig(
            enemies=[_immortal()],
            fight_duration=60.0,
            tick_size=0.1,
            base_damage=200.0,
            hit_config=_hit(),
        )
        r = EncounterMachine(cfg).run()
        assert all(d >= 0.0 for d in r.damage_per_tick)

    def test_elapsed_time_bounded(self):
        """elapsed_time never exceeds fight_duration by more than one tick."""
        cfg = EncounterConfig(
            enemies=[_immortal()],
            fight_duration=120.0,
            tick_size=0.1,
            base_damage=100.0,
            hit_config=_hit(),
        )
        r = EncounterMachine(cfg).run()
        assert r.elapsed_time <= cfg.fight_duration + cfg.tick_size + 1e-9


class TestMemoryGrowth:
    """Repeated runs must not accumulate unbounded memory."""

    def test_50_long_runs_memory_growth(self):
        """50 × 600-second fights grow heap by < 1 MB."""
        tracemalloc.start()
        snap_before = tracemalloc.take_snapshot()

        for _ in range(50):
            cfg = EncounterConfig(
                enemies=[_immortal()],
                fight_duration=600.0,
                tick_size=0.1,
                base_damage=100.0,
                hit_config=_hit(),
            )
            EncounterMachine(cfg).run()

        snap_after = tracemalloc.take_snapshot()
        tracemalloc.stop()

        stats = snap_after.compare_to(snap_before, "lineno")
        growth_bytes = sum(s.size_diff for s in stats)
        assert growth_bytes < 1024 * 1024, (
            f"Memory grew {growth_bytes / 1024:.1f} KB over 50 long runs (limit 1 MB)"
        )

    def test_100_short_runs_memory_growth(self):
        """100 × 10-second fights grow heap by < 512 KB."""
        tracemalloc.start()
        snap_before = tracemalloc.take_snapshot()

        for _ in range(100):
            cfg = EncounterConfig(
                enemies=[_immortal()],
                fight_duration=10.0,
                tick_size=0.1,
                base_damage=100.0,
                hit_config=_hit(),
            )
            EncounterMachine(cfg).run()

        snap_after = tracemalloc.take_snapshot()
        tracemalloc.stop()

        stats = snap_after.compare_to(snap_before, "lineno")
        growth_bytes = sum(s.size_diff for s in stats)
        assert growth_bytes < 512 * 1024, (
            f"Memory grew {growth_bytes / 1024:.1f} KB over 100 short runs (limit 512 KB)"
        )


class TestNumericalStability:
    """Damage pipeline stays accurate across extreme input magnitudes."""

    @pytest.mark.parametrize("base_damage", [0.001, 1.0, 1_000.0, 1_000_000.0])
    def test_damage_ratio_stable(self, base_damage):
        """total_damage / (base_damage × ticks) ≈ 1.0 across all scales."""
        cfg = EncounterConfig(
            enemies=[_immortal()],
            fight_duration=10.0,
            tick_size=0.1,
            base_damage=base_damage,
            hit_config=_hit(),
        )
        r = EncounterMachine(cfg).run()
        expected = base_damage * r.ticks_simulated
        assert r.total_damage == pytest.approx(expected, rel=1e-6)

    def test_very_high_armor_no_negative_damage(self):
        """Extreme armor (1 000 000) never produces negative health dealt."""
        enemy = EncounterEnemy(
            max_health=1e12, current_health=1e12, armor=1_000_000.0, name="tank"
        )
        cfg = EncounterConfig(
            enemies=[enemy],
            fight_duration=10.0,
            tick_size=0.1,
            base_damage=1000.0,
            hit_config=_hit(),
        )
        r = EncounterMachine(cfg).run()
        assert all(d >= 0.0 for d in r.damage_per_tick)

    def test_tiny_tick_size_accounting(self):
        """0.01-tick fights still satisfy damage-sum invariant."""
        cfg = EncounterConfig(
            enemies=[_immortal()],
            fight_duration=5.0,
            tick_size=0.01,
            base_damage=100.0,
            hit_config=_hit(),
        )
        r = EncounterMachine(cfg).run()
        assert r.total_damage == pytest.approx(sum(r.damage_per_tick), rel=1e-9)
        assert len(r.damage_per_tick) == r.ticks_simulated

    def test_max_health_boundary_not_exceeded(self):
        """After a full run with lethal damage, current_health >= 0."""
        enemy = EncounterEnemy(
            max_health=100.0, current_health=100.0, armor=0.0, name="fragile"
        )
        cfg = EncounterConfig(
            enemies=[enemy],
            fight_duration=60.0,
            tick_size=0.1,
            base_damage=1_000_000.0,
            hit_config=_hit(),
            stop_on_all_dead=True,
        )
        EncounterMachine(cfg).run()
        assert enemy.current_health >= 0.0
