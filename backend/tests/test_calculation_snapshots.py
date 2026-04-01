"""
Calculation Snapshot Tests — detect stat-math regression drift.

Each snapshot captures the FULL output of a known build configuration so
that any change to a calculator function, pipeline stage, or stacking
formula immediately produces a diff against these expected values.

Snapshot anatomy
────────────────
  PIPELINE_SNAPSHOTS — intermediate DamageContext values (base, increased,
                        more, hit_damage) tested in isolation from the engine.
  DPS_SNAPSHOTS      — full DPSResult from calculate_dps(), including crit,
                       attack speed, ailment DPS.

Adding a new snapshot
─────────────────────
  1. Define build stats and expected result in the SNAPSHOTS dicts below.
  2. Derive expected values by hand or from a trusted run, then document
     the derivation as inline comments.
  3. The test asserts field-by-field so failures name the exact drifted value.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.engines.stat_engine import BuildStats
from app.engines.combat_engine import SKILL_STATS, calculate_dps
from app.domain.skill_modifiers import SkillModifiers
from app.domain.calculators.final_damage_calculator import DamageContext, calculate_final_damage
from app.domain.calculators.stat_calculator import combine_additive_percents
from app.constants.combat import BASE_CRIT_CHANCE, BASE_CRIT_MULTIPLIER


# ---------------------------------------------------------------------------
# Shared skill definitions (from SKILL_STATS — never changes in these tests)
# ---------------------------------------------------------------------------
#   Fireball: base=110, level_scaling=0.12, attack_speed=1.2,
#             scaling_stats=["spell_damage_pct", "fire_damage_pct"], is_spell=True
#
#   At level 20: scaled_base = 110 × (1 + 0.12 × 19) = 110 × 3.28 = 360.8

_FIREBALL = SKILL_STATS["Fireball"]


# ---------------------------------------------------------------------------
# Pipeline snapshots — intermediate DamageContext values
# ---------------------------------------------------------------------------

# Derivation key:
#   effective_base = scaled_base + flat_added (no flat damage in these builds)
#   increased_pct  = sum_increased_damage(stats, skill_def)
#                  = combine(spell_pct, fire_pct) [+ elemental if fire present]
#   hit_damage     = effective_base × (1 + increased_pct/100)
#                    × product(1 + m/100 for m in more_damage)

PIPELINE_SNAPSHOTS = [
    {
        "name": "no_bonuses",
        # All stats at 0; base damage unchanged by modifiers.
        # effective_base = 360.8
        # increased_pct  = combine(0, 0) = 0.0
        # after_increased = 360.8 × 1.0 = 360.8
        # more            = [0.0, 0.0] → × 1.0 × 1.0
        # hit_damage      = 360.8
        "stats": BuildStats(),
        "expected_base": 360.8,
        "expected_increased_pct": 0.0,
        "expected_hit_damage": 360.8,
    },
    {
        "name": "increased_only",
        # spell_damage_pct=100, fire_damage_pct=50, elemental=0
        # increased_pct  = combine(100, 50) + combine(0) = 150.0
        # after_increased = 360.8 × 2.5 = 902.0
        # more            = [0.0, 0.0] → no change
        # hit_damage      = 902.0
        "stats": BuildStats(spell_damage_pct=100.0, fire_damage_pct=50.0),
        "expected_base": 360.8,
        "expected_increased_pct": 150.0,
        "expected_hit_damage": 902.0,
    },
    {
        "name": "increased_with_elemental",
        # spell=100, fire=50, elemental=30 → elemental applies because fire ∈ ELEMENTAL_DAMAGE_INCREASED
        # increased_pct  = combine(100, 50) = 150 → + elemental(30) = 180.0
        # after_increased = 360.8 × 2.8 = 1010.24
        # hit_damage      = 1010.24
        "stats": BuildStats(spell_damage_pct=100.0, fire_damage_pct=50.0, elemental_damage_pct=30.0),
        "expected_base": 360.8,
        "expected_increased_pct": 180.0,
        "expected_hit_damage": 1010.24,
    },
    {
        "name": "more_only",
        # No increased bonuses; 50% more source from stats
        # increased_pct  = 0.0
        # after_increased = 360.8
        # more            = [50.0, 0.0] → × 1.5
        # hit_damage      = 360.8 × 1.5 = 541.2
        "stats": BuildStats(more_damage_pct=50.0),
        "expected_base": 360.8,
        "expected_increased_pct": 0.0,
        "expected_hit_damage": 541.2,
    },
    {
        "name": "increased_and_more",
        # spell=100, fire=50 → increased=150; more_damage_pct=50%
        # after_increased = 360.8 × 2.5 = 902.0
        # hit_damage      = 902.0 × 1.5 = 1353.0
        "stats": BuildStats(spell_damage_pct=100.0, fire_damage_pct=50.0, more_damage_pct=50.0),
        "expected_base": 360.8,
        "expected_increased_pct": 150.0,
        "expected_hit_damage": 1353.0,
    },
    {
        "name": "skill_modifier_more",
        # Stats: no more; SkillModifiers provides extra_more_pct=40%
        # more_damage = [0.0, 40.0] → × 1.0 × 1.4
        # after_increased = 360.8 × 2.5 = 902.0
        # hit_damage      = 902.0 × 1.4 = 1262.8
        "stats": BuildStats(spell_damage_pct=100.0, fire_damage_pct=50.0),
        "extra_more_pct": 40.0,
        "expected_base": 360.8,
        "expected_increased_pct": 150.0,
        "expected_hit_damage": 1262.8,
    },
]


# ---------------------------------------------------------------------------
# Full DPS snapshots — complete DPSResult field assertions
# ---------------------------------------------------------------------------

# All builds use Fireball level 20.  Derivation inline per snapshot.

DPS_SNAPSHOTS = [
    {
        "name": "minimal_baseline",
        # spell=100, fire=50, crit_chance=0.05, crit_mult=2.0, cast_speed=0
        #
        # hit_damage       = 902.0            (from pipeline snapshot above)
        # effective_crit_c = min(0.75, 0.05)  = 0.05
        # effective_crit_m = 2.0
        # non_crit         = 0.95 × 902.0     = 856.9
        # crit_hit         = 0.05 × 902.0 × 2 = 90.2
        # average_hit      = 856.9 + 90.2     = 947.1
        # effective_as     = 1.2 × (1 + 0)   = 1.2   (spell → cast_speed path)
        # hit_dps          = 947.1 × 1.2      = 1136.52
        # crit_contrib     = (90.2×1.2)/1136.52×100 = 9.52 → 10
        "stats": BuildStats(
            spell_damage_pct=100.0,
            fire_damage_pct=50.0,
            crit_chance=BASE_CRIT_CHANCE,
            crit_multiplier=BASE_CRIT_MULTIPLIER,
        ),
        "skill_modifiers": None,
        "expected": {
            "hit_damage": 902,
            "average_hit": 947,
            "dps": 1137,
            "effective_attack_speed": 1.2,
            "crit_contribution_pct": 10,
            "flat_damage_added": 0,
            "total_dps": 1137,
        },
    },
    {
        "name": "with_cast_speed_and_more",
        # spell=150, fire=80, elemental=20 → increased=250
        # more_damage_pct=50, cast_speed=30
        # crit_chance=0.10, crit_mult=2.5
        #
        # scaled_base      = 360.8
        # after_increased  = 360.8 × 3.5     = 1262.8
        # hit_damage       = 1262.8 × 1.5    = 1894.2
        # non_crit         = 0.90 × 1894.2   = 1704.78
        # crit_hit         = 0.10 × 1894.2 × 2.5 = 473.55
        # average_hit      = 1704.78 + 473.55 = 2178.33
        # cast_speed_bonus = 30/100           = 0.30
        # effective_as     = 1.2 × 1.3       = 1.56
        # hit_dps          = 2178.33 × 1.56  = 3398.19
        # crit_contrib     = (473.55×1.56)/3398.19×100 = 21.74 → 22
        "stats": BuildStats(
            spell_damage_pct=150.0,
            fire_damage_pct=80.0,
            elemental_damage_pct=20.0,
            more_damage_pct=50.0,
            crit_chance=0.10,
            crit_multiplier=2.5,
            cast_speed=30.0,
        ),
        "skill_modifiers": None,
        "expected": {
            "hit_damage": 1894,
            "average_hit": 2178,
            "dps": 3398,
            "effective_attack_speed": 1.56,
            "crit_contribution_pct": 22,
            "flat_damage_added": 0,
            "total_dps": 3398,
        },
    },
    {
        "name": "with_skill_modifier_more",
        # Base stats same as minimal_baseline; SkillModifiers adds 40% more.
        #
        # more_damage = [0.0, 40.0] → × 1.0 × 1.4
        # after_increased = 902.0
        # hit_damage      = 902.0 × 1.4 = 1262.8
        # non_crit        = 0.95 × 1262.8 = 1199.66
        # crit_hit        = 0.05 × 1262.8 × 2.0 = 126.28
        # average_hit     = 1199.66 + 126.28 = 1325.94
        # effective_as    = 1.2
        # hit_dps         = 1325.94 × 1.2 = 1591.13
        # crit_contrib    = (126.28×1.2)/1591.13×100 = 9.52 → 10
        "stats": BuildStats(
            spell_damage_pct=100.0,
            fire_damage_pct=50.0,
            crit_chance=BASE_CRIT_CHANCE,
            crit_multiplier=BASE_CRIT_MULTIPLIER,
        ),
        "skill_modifiers": SkillModifiers(more_damage_pct=40.0),
        "expected": {
            "hit_damage": 1263,
            "average_hit": 1326,
            "dps": 1591,
            "effective_attack_speed": 1.2,
            "crit_contribution_pct": 10,
            "flat_damage_added": 0,
            "total_dps": 1591,
        },
    },
]


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------

class TestPipelineSnapshots(unittest.TestCase):
    """Snapshot each DamageContext stage value to detect pipeline drift."""

    def _assert_snapshot(self, snap: dict) -> None:
        stats = snap["stats"]
        extra_more = snap.get("extra_more_pct", 0.0)
        scaled_base = _FIREBALL.base_damage * (1 + _FIREBALL.level_scaling * 19)

        ctx = DamageContext.from_build(scaled_base, stats, _FIREBALL, extra_more)
        hit = calculate_final_damage(ctx)

        name = snap["name"]
        self.assertAlmostEqual(
            ctx.base_damage, snap["expected_base"], places=4,
            msg=f"[{name}] base_damage drift",
        )
        self.assertAlmostEqual(
            ctx.increased_damage, snap["expected_increased_pct"], places=4,
            msg=f"[{name}] increased_pct drift",
        )
        self.assertAlmostEqual(
            hit, snap["expected_hit_damage"], places=4,
            msg=f"[{name}] hit_damage drift",
        )

    def test_no_bonuses(self):
        self._assert_snapshot(PIPELINE_SNAPSHOTS[0])

    def test_increased_only(self):
        self._assert_snapshot(PIPELINE_SNAPSHOTS[1])

    def test_increased_with_elemental(self):
        self._assert_snapshot(PIPELINE_SNAPSHOTS[2])

    def test_more_only(self):
        self._assert_snapshot(PIPELINE_SNAPSHOTS[3])

    def test_increased_and_more(self):
        self._assert_snapshot(PIPELINE_SNAPSHOTS[4])

    def test_skill_modifier_more(self):
        self._assert_snapshot(PIPELINE_SNAPSHOTS[5])


class TestDPSSnapshots(unittest.TestCase):
    """Snapshot full DPSResult fields to detect downstream engine drift."""

    def _assert_dps_snapshot(self, snap: dict) -> None:
        result = calculate_dps(
            snap["stats"],
            "Fireball",
            skill_level=20,
            skill_modifiers=snap["skill_modifiers"],
        )
        expected = snap["expected"]
        name = snap["name"]
        for field, expected_value in expected.items():
            actual = getattr(result, field)
            if isinstance(expected_value, float):
                self.assertAlmostEqual(
                    actual, expected_value, places=4,
                    msg=f"[{name}] {field}: expected {expected_value}, got {actual}",
                )
            else:
                self.assertEqual(
                    actual, expected_value,
                    msg=f"[{name}] {field}: expected {expected_value}, got {actual}",
                )

    def test_minimal_baseline(self):
        self._assert_dps_snapshot(DPS_SNAPSHOTS[0])

    def test_with_cast_speed_and_more(self):
        self._assert_dps_snapshot(DPS_SNAPSHOTS[1])

    def test_with_skill_modifier_more(self):
        self._assert_dps_snapshot(DPS_SNAPSHOTS[2])


if __name__ == "__main__":
    unittest.main()
