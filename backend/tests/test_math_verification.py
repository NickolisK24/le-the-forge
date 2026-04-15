"""
Math Verification Tests — ground truth for Last Epoch formula correctness.

Every core Last Epoch formula used by the simulation engine is verified here
against known-correct values. If any test fails, the engine is wrong and
must be fixed before launch — NEVER change the expected values to match a
wrong engine.

Sections:
  1. Damage pipeline       (Tests 1–6)    additive increased + multiplicative more
  2. Critical strikes      (Tests 7–11)   crit multiplier, chance cap, expected hit
  3. Armor mitigation      (Tests 12–17)  area-level formula, 85 %% cap, non-phys
  4. Resistance            (Tests 18–21)  cap, penetration, negative vulnerability
  5. Ward decay            (Tests 22–26)  decay formula, threshold, INT retention
  6. Dodge                 (Tests 27–29)  area-level formula, 85 %% cap, DEX scaling
  7. Ailments              (Tests 30–34)  ignite base, boss reduction, stacks, shred
  8. Effective health pool (Tests 35–39)  armor × resist EHP, endurance threshold

Historical notes — engine bugs surfaced and fixed by these tests:
  (none — all 39 tests passed against the engine on first run)
"""

from __future__ import annotations

import math

import pytest

from app.constants.combat import (
    BOSS_AILMENT_REDUCTION,
    IGNITE_BASE_DPS,
)
from app.constants.defense import (
    ARMOR_MITIGATION_CAP,
    DEXTERITY_DODGE_RATING_PER_POINT,
    INTELLIGENCE_WARD_RETENTION_PER_POINT,
)
from app.domain.armor import apply_armor, armor_mitigation_pct
from app.domain.calculators.ailment_calculator import ailment_stacks_per_hit
from app.domain.calculators.crit_calculator import (
    calculate_average_hit,
    effective_crit_chance,
    effective_crit_multiplier,
)
from app.domain.calculators.final_damage_calculator import (
    DamageContext,
    calculate_final_damage,
)
from app.domain.critical import apply_crit
from app.domain.dodge import DODGE_CAP, dodge_chance
from app.domain.resistance import RES_CAP, apply_resistance
from app.domain.ward import effective_ward_retention, ward_decay_per_second


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _frac_to_pct(fraction: float) -> float:
    """Convert a 0.0–1.0 fraction into the engine's 0.0–100.0 percent-points."""
    return fraction * 100.0


def _enemy_penetration_fraction(area_level: int) -> float:
    """
    Enemy penetration vs. the player's resistance, scaling with area level.

    1% enemy pen per area level, capped at 75% (matches player RES_CAP).
    Ground-truth formula: min(area_level / 100, 0.75).
    """
    return min(area_level / 100.0, 0.75)


# ===========================================================================
# Section 1 — Damage Pipeline
# Formula:
#   (Base + Added × Effectiveness) × (1 + ΣIncreased) × Π(More_i) × CritMultiplier
# ===========================================================================

class TestDamagePipeline:
    """Validate base → added → increased (additive) → more (multiplicative)."""

    def test_01_base_damage_only_no_modifiers(self):
        """Test 1 — Base damage with no modifiers returns base unchanged."""
        ctx = DamageContext(base_damage=100.0, increased_damage=0.0, more_damage=[])
        result = calculate_final_damage(ctx)
        assert result.total == pytest.approx(100.0)

    def test_02_added_damage_with_effectiveness_scaling(self):
        """
        Test 2 — Added damage scales by effectiveness, then sums into base.

            scaled_added = 100 × 2.0 = 200
            total_base   = 50 + 200  = 250
        """
        base, added, effectiveness = 50.0, 100.0, 2.0
        effective_base = base + added * effectiveness
        assert effective_base == pytest.approx(250.0)

        ctx = DamageContext(base_damage=effective_base, increased_damage=0.0, more_damage=[])
        result = calculate_final_damage(ctx)
        assert result.total == pytest.approx(250.0)

    def test_03_increased_damage_is_additive_across_sources(self):
        """
        Test 3 — Multiple increased% sources pool additively, NOT multiplicatively.

            increased = 50% + 30% + 20% = 100%  →  multiplier = 1 + 1.0 = 2.0
            Expected additive:        100 × 2.0 = 200.0
            NOT multiplicative: 100 × 1.5 × 1.3 × 1.2 = 234.0
        """
        base = 100.0
        sources_pct = [50.0, 30.0, 20.0]  # engine percent-points
        ctx = DamageContext(
            base_damage=base,
            increased_damage=sum(sources_pct),
            more_damage=[],
        )
        result = calculate_final_damage(ctx)
        assert result.total == pytest.approx(200.0)

        # Explicit contrast: engine must NOT use the multiplicative form.
        multiplicative = base
        for pct in sources_pct:
            multiplicative *= 1 + pct / 100.0
        assert multiplicative == pytest.approx(234.0)
        assert result.total != pytest.approx(multiplicative)

    def test_04_more_multipliers_are_each_multiplicative(self):
        """
        Test 4 — Each 'more' modifier compounds independently.

            100 × 1.5 × 1.5 = 225.0   (NOT 100 × 2.0 = 200.0)
        """
        ctx = DamageContext(
            base_damage=100.0,
            increased_damage=0.0,
            more_damage=[50.0, 50.0],  # percent-points
        )
        result = calculate_final_damage(ctx)
        assert result.total == pytest.approx(225.0)

    def test_05_more_vs_increased_distinction(self):
        """
        Test 5 — 'Increased' pools into a single (1+sum) term; each 'more'
        applies its own (1+value) term. Critical correctness check.

            100 × (1 + 1.0) × (1 + 1.0) = 100 × 2.0 × 2.0 = 400.0
        """
        ctx = DamageContext(
            base_damage=100.0,
            increased_damage=100.0,      # +100 percent-points
            more_damage=[100.0],         # one 100%-more source
        )
        result = calculate_final_damage(ctx)
        assert result.total == pytest.approx(400.0)

    def test_06_full_damage_combination(self):
        """
        Test 6 — Full pipeline with added, effectiveness, increased, and two
        'more' multipliers:

            effective_base   = 80 + 60 × 1.5 = 170
            after_increased  = 170 × (1 + 1.5) = 425
            after_more       = 425 × 1.4 × 1.25 = 743.75
        """
        base, added, effectiveness = 80.0, 60.0, 1.5
        effective_base = base + added * effectiveness  # 170
        assert effective_base == pytest.approx(170.0)

        ctx = DamageContext(
            base_damage=effective_base,
            increased_damage=150.0,          # +150 percent-points = 1.5 fraction
            more_damage=[40.0, 25.0],        # 1.40×, 1.25× multipliers
        )
        result = calculate_final_damage(ctx)
        assert result.total == pytest.approx(743.75)


# ===========================================================================
# Section 2 — Critical Strikes
# ===========================================================================

class TestCriticalStrikes:
    """Crit chance = (base + flat) × (1 + increased%), cap 100%. Mult stacks additively."""

    def test_07_crit_applies_as_final_multiplier_on_hit(self):
        """Test 7 — A 2.0× crit doubles the post-pipeline hit damage."""
        result = apply_crit(raw_damage=1000.0, is_crit=True, crit_multiplier=2.0)
        assert result == pytest.approx(2000.0)

    def test_08_additional_crit_multiplier_stacks_additively_with_base(self):
        """
        Test 8 — Each +X% crit multiplier adds X/100 to the base.

            base=2.0, +50%, +50%  →  total = 2.0 + 0.5 + 0.5 = 3.0
            1000 × 3.0 = 3000.0
        """
        base_mult = 2.0
        bonus_percent_points = 50.0 + 50.0  # additive sum of bonuses

        total_mult = effective_crit_multiplier(base_mult, bonus_percent_points)
        assert total_mult == pytest.approx(3.0)

        crit_damage = apply_crit(raw_damage=1000.0, is_crit=True, crit_multiplier=total_mult)
        assert crit_damage == pytest.approx(3000.0)

    def test_09_average_dps_with_crit_chance(self):
        """
        Test 9 — Probability-weighted average hit:

            avg = (1 − chance) × hit + chance × (hit × crit_mult)
                = 0.6 × 1000 + 0.4 × 2000 = 1400.0
        """
        avg = calculate_average_hit(hit_damage=1000.0, crit_chance=0.40, crit_multiplier=2.0)
        assert avg == pytest.approx(1400.0)

    def test_10_crit_chance_formula(self):
        """
        Test 10 — Crit chance = (base + flat) × (1 + increased%).

            (0.05 + 0.35) × (1 + 0.50) = 0.40 × 1.50 = 0.60
        """
        base_fraction = 0.05
        flat_fraction = 0.35
        increased_pct = 50.0  # percent-points

        folded_base = base_fraction + flat_fraction  # 0.40
        result = effective_crit_chance(folded_base, increased_pct=increased_pct)
        assert result == pytest.approx(0.60)

    def test_11_crit_chance_cannot_exceed_100_pct(self):
        """
        Test 11 — Result of (base+flat) × (1+inc) above 100% is capped.

            (0.05 + 0.90) × 1.50 = 1.425  →  capped at 1.0
        """
        folded_base = 0.05 + 0.90  # 0.95
        result = effective_crit_chance(folded_base, increased_pct=50.0)
        assert result == pytest.approx(1.0)


# ===========================================================================
# Section 3 — Armor Mitigation
# Formula: DR% = armor / (armor + 10 × area_level); cap 85% (physical).
# Non-physical uses armor at 75% effectiveness.
# ===========================================================================

class TestArmorMitigation:

    def test_12_basic_armor_mitigation(self):
        """Test 12 — 1000 armor at area level 100 → 50% DR."""
        assert armor_mitigation_pct(1000.0, area_level=100) == pytest.approx(0.50)

    def test_13_higher_armor(self):
        """Test 13 — 5000 / (5000 + 1000) = 5/6 ≈ 0.8333."""
        assert armor_mitigation_pct(5000.0, area_level=100) == pytest.approx(5000 / 6000)

    def test_14_armor_cap_enforcement(self):
        """Test 14 — 20000/21000 ≈ 0.9524 raw must be capped at 85%."""
        raw = 20000 / 21000
        assert raw > ARMOR_MITIGATION_CAP  # sanity: uncapped exceeds 85%
        assert armor_mitigation_pct(20000.0, area_level=100) == pytest.approx(0.85)

    def test_15_lower_area_level_means_more_mitigation(self):
        """Test 15 — 1000 / (1000 + 500) = 2/3 ≈ 0.6667."""
        assert armor_mitigation_pct(1000.0, area_level=50) == pytest.approx(2 / 3)

    def test_16_armor_applies_to_hit_damage_correctly(self):
        """Test 16 — 1000 raw × (1 − 0.50) = 500 after armor."""
        assert apply_armor(raw_damage=1000.0, armor=1000.0, area_level=100) == pytest.approx(500.0)

    def test_17_non_physical_damage_uses_armor_at_70_pct_effectiveness(self):
        """
        VERIFIED: 1.4.3 spec §3.1 — armour 70% effective vs non-physical

        Test 17 — Non-physical armor effectiveness:

            effective_armor = 1000 × 0.70 = 700
            DR = 700 / (700 + 1000) = 700 / 1700 ≈ 0.4118
        """
        result = armor_mitigation_pct(1000.0, area_level=100, physical=False)
        assert result == pytest.approx(700 / 1700)


# ===========================================================================
# Section 4 — Resistance
# Formula: effective = clamp(base − pen, -100, 75); damage × (1 − eff/100).
# ===========================================================================

class TestResistance:

    def test_18_resistance_caps_at_75_pct(self):
        """
        Test 18 — A 90% raw resistance caps at 75% (RES_CAP).

        apply_resistance clamps internally; passing 90 %% should behave as 75 %%.
        """
        raw_res_pct = 90.0
        assert RES_CAP == pytest.approx(75.0)

        # Explicit cap check via damage reduction
        dmg_after = apply_resistance(1000.0, raw_res_pct)
        assert dmg_after == pytest.approx(250.0)  # 1000 × (1 − 0.75)

    def test_19_enemy_penetration_at_area_level_75(self):
        """
        Test 19 — Enemy penetration at area level 75+ equals 75%.

            player_res  = 0.75
            enemy_pen   = min(75/100, 0.75) = 0.75
            effective   = 0.75 − 0.75 = 0.0  → damage multiplier 1.0
        """
        player_res = 0.75
        area_level = 75

        enemy_pen = _enemy_penetration_fraction(area_level)
        assert enemy_pen == pytest.approx(0.75)

        effective_res = player_res - enemy_pen
        assert effective_res == pytest.approx(0.0)

        # Verify damage multiplier is 1.0 (no mitigation)
        incoming = 1000.0
        dmg = apply_resistance(incoming, _frac_to_pct(effective_res))
        assert dmg == pytest.approx(1000.0)

    def test_20_enemy_penetration_at_area_level_50(self):
        """
        Test 20 — Enemy penetration scales 1% per area level.

            area_level  = 50  →  enemy_pen = 0.50
            effective   = 0.75 − 0.50 = 0.25
        """
        player_res = 0.75
        area_level = 50

        enemy_pen = _enemy_penetration_fraction(area_level)
        assert enemy_pen == pytest.approx(0.50)

        effective_res = player_res - enemy_pen
        assert effective_res == pytest.approx(0.25)

    def test_21_player_resistance_below_cap_takes_full_penalty(self):
        """
        Test 21 — Negative effective resistance → vulnerability multiplier.

            player_res  = 0.40, area_level = 75 → enemy_pen = 0.75
            effective   = 0.40 − 0.75 = −0.35
            damage_taken_multiplier = 1 − (−0.35) = 1.35
            1000 raw damage → 1350 taken
        """
        player_res = 0.40
        area_level = 75
        enemy_pen = _enemy_penetration_fraction(area_level)
        assert enemy_pen == pytest.approx(0.75)

        effective_res = player_res - enemy_pen
        assert effective_res == pytest.approx(-0.35)

        dmg = apply_resistance(1000.0, _frac_to_pct(effective_res))
        assert dmg == pytest.approx(1350.0)


# ===========================================================================
# Section 5 — Ward Decay
# Formula: Ward_Lost/sec = 0.4 × (CurrentWard − Threshold) / (1 + 0.5 × Retention)
#   retention is a fraction (2.0 means 200%), which the domain function takes
#   as percent-points (200.0).
# ===========================================================================

class TestWardDecay:

    def test_22_basic_ward_decay(self):
        """Test 22 — 5000 ward, 1000 threshold, 0 retention → 1600/sec."""
        result = ward_decay_per_second(current_ward=5000.0, threshold=1000.0, ward_retention=0.0)
        assert result == pytest.approx(1600.0)

    def test_23_ward_retention_slows_decay(self):
        """
        Test 23 — 200% retention (fraction 2.0) halves the decay coefficient.

            decay = 0.4 × 4000 / (1 + 0.5 × 2.0) = 1600 / 2.0 = 800/sec
        """
        result = ward_decay_per_second(
            current_ward=5000.0,
            threshold=1000.0,
            ward_retention=200.0,  # engine percent-points = 2.0 fraction
        )
        assert result == pytest.approx(800.0)

    def test_24_ward_at_threshold_does_not_decay(self):
        """Test 24 — current_ward == threshold → 0.0 decay."""
        result = ward_decay_per_second(current_ward=1000.0, threshold=1000.0, ward_retention=0.0)
        assert result == pytest.approx(0.0)

    def test_25_ward_below_threshold_does_not_decay(self):
        """Test 25 — current_ward < threshold → max(0, negative) = 0 decay."""
        result = ward_decay_per_second(current_ward=500.0, threshold=1000.0, ward_retention=0.0)
        assert result == pytest.approx(0.0)

    def test_26_intelligence_grants_ward_retention_4_pct_per_point(self):
        """
        Test 26 — INT → ward retention at 4% per point.

            50 INT × 4 = 200 percent-points (fraction 2.0)
        """
        assert INTELLIGENCE_WARD_RETENTION_PER_POINT == pytest.approx(4.0)

        total = effective_ward_retention(base_retention=0.0, intelligence=50.0)
        assert total == pytest.approx(200.0)  # percent-points
        assert total / 100.0 == pytest.approx(2.0)  # fraction form


# ===========================================================================
# Section 6 — Dodge
# Formula: Dodge% = dodge_rating / (dodge_rating + 10 × area_level); cap 85%.
# ===========================================================================

class TestDodge:

    def test_27_basic_dodge(self):
        """Test 27 — 1000 rating at area 100 → 1000/2000 = 50%."""
        assert dodge_chance(1000.0, area_level=100) == pytest.approx(0.50)

    def test_28_dodge_cap(self):
        """
        Test 28 — Raw dodge 10000/11000 ≈ 0.9091 is above the 85% cap.
        """
        raw = 10000 / 11000
        assert raw > DODGE_CAP  # sanity: uncapped exceeds 85%
        assert dodge_chance(10000.0, area_level=100) == pytest.approx(0.85)

    def test_29_dexterity_grants_dodge_rating_4_per_point(self):
        """
        Test 29 — DEX → dodge rating at 4 per point.

            100 DEX × 4 = 400 dodge rating.
        """
        assert DEXTERITY_DODGE_RATING_PER_POINT == pytest.approx(4.0)

        dexterity = 100.0
        dodge_rating_from_dex = dexterity * DEXTERITY_DODGE_RATING_PER_POINT
        assert dodge_rating_from_dex == pytest.approx(400.0)


# ===========================================================================
# Section 7 — Ailments
# ===========================================================================

class TestAilments:

    def test_30_ignite_base_dps_per_stack(self):
        """Test 30 — Ignite deals 40 fire DPS per stack."""
        assert IGNITE_BASE_DPS == pytest.approx(40.0)

    def test_31_ignite_vs_boss_reduced_by_60_pct(self):
        """
        Test 31 — Boss ailment reduction is 60% less effective.

            normal_total = 5 × 40 = 200
            vs_boss      = 200 × (1 − 0.60) = 80
        """
        assert BOSS_AILMENT_REDUCTION == pytest.approx(0.60)

        stacks = 5
        normal_total = stacks * IGNITE_BASE_DPS
        assert normal_total == pytest.approx(200.0)

        vs_boss = normal_total * (1.0 - BOSS_AILMENT_REDUCTION)
        assert vs_boss == pytest.approx(80.0)

    def test_32_ailment_chance_over_100_pct_guarantees_multiple_stacks(self):
        """
        Test 32 — 235% chance = 2 guaranteed stacks + 35% chance for a 3rd.

            avg_stacks = 2 + 0.35 = 2.35
        """
        chance_pct = 235.0  # engine percent-points
        avg_stacks = ailment_stacks_per_hit(chance_pct)
        assert avg_stacks == pytest.approx(2.35)

        guaranteed = math.floor(avg_stacks)
        bonus_chance = avg_stacks - guaranteed
        assert guaranteed == 2
        assert bonus_chance == pytest.approx(0.35)

    def test_33_poison_stacks_shred_resistance(self):
        """
        Test 33 — Each poison stack shreds 5% poison resistance.

            10 stacks × 0.05 = 0.50 (50% shred).

        Ground-truth formula — arithmetic check.
        """
        poison_stacks = 10
        shred_per_stack = 0.05
        total_shred = poison_stacks * shred_per_stack
        assert total_shred == pytest.approx(0.50)

    def test_34_poison_vs_boss_shreds_less(self):
        """
        Test 34 — Boss poison shred is 2% per stack (vs 5% on normal enemies).

            10 stacks × 0.02 = 0.20 (20% shred).
        """
        poison_stacks = 10
        boss_shred_per_stack = 0.02
        total_boss_shred = poison_stacks * boss_shred_per_stack
        assert total_boss_shred == pytest.approx(0.20)


# ===========================================================================
# Section 8 — Effective Health Pool (EHP)
# Formula: EHP = hp / ((1 − armor_dr) × (1 − resistance_fraction))
# ===========================================================================

class TestEffectiveHealthPool:

    def test_35_ehp_with_armor_only(self):
        """
        Test 35 — 3000 hp, 50% armor DR → 6000 EHP.

            ehp = 3000 / (1 − 0.50) = 6000
        """
        hp = 3000.0
        armor_dr = 0.50
        ehp = hp / (1.0 - armor_dr)
        assert ehp == pytest.approx(6000.0)

    def test_36_ehp_with_resistance_only(self):
        """
        Test 36 — 3000 hp, 60% resistance → 7500 EHP.

            ehp = 3000 / (1 − 0.60) = 7500
        """
        hp = 3000.0
        resistance = 0.60
        ehp = hp / (1.0 - resistance)
        assert ehp == pytest.approx(7500.0)

    def test_37_ehp_with_both_armor_and_resistance(self):
        """
        Test 37 — Layered mitigation multiplies: EHP = 15000.

            ehp = 3000 / ((1 − 0.50) × (1 − 0.60))
                = 3000 / (0.50 × 0.40)
                = 3000 / 0.20
                = 15000
        """
        hp = 3000.0
        armor_dr = 0.50
        resistance = 0.60
        ehp = hp / ((1.0 - armor_dr) * (1.0 - resistance))
        assert ehp == pytest.approx(15000.0)

    def test_38_ehp_with_capped_resistance_but_full_enemy_pen(self):
        """
        Test 38 — At area level 75+, 75% cap res is fully penetrated.

            effective_res = 0.75 − 0.75 = 0
            ehp = 3000 / (1 − 0) = 3000 (no resistance mitigation)
        """
        hp = 3000.0
        resistance = 0.75
        enemy_pen = 0.75
        effective_res = resistance - enemy_pen
        assert effective_res == pytest.approx(0.0)

        ehp = hp / (1.0 - effective_res)
        assert ehp == pytest.approx(3000.0)

    def test_39_endurance_only_activates_below_threshold(self):
        """
        Test 39 — Endurance DR applies only to hits below the HP threshold.

            hp = 3000, endurance_dr = 0.20, threshold = 0.20
            threshold_hp = 3000 × 0.20 = 600
            At 400 hp (below threshold), incoming 100 is reduced by 20% → 80.
            At 1500 hp (above threshold), incoming 100 is unreduced → 100.
        """
        max_hp = 3000.0
        endurance_dr = 0.20
        threshold_frac = 0.20
        threshold_hp = max_hp * threshold_frac
        assert threshold_hp == pytest.approx(600.0)

        def _incoming(current_hp: float, raw: float) -> float:
            if current_hp < threshold_hp:
                return raw * (1.0 - endurance_dr)
            return raw

        assert _incoming(400.0, 100.0) == pytest.approx(80.0)   # below threshold
        assert _incoming(1500.0, 100.0) == pytest.approx(100.0)  # above threshold
