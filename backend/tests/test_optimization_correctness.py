"""
Tests for the three correctness fixes to the optimization / combat pipeline:

  1. ``_normalize_skill_name`` — imported builds carry skill names in
     snake_case / CamelCase; SKILL_STATS is keyed by title-case-with-spaces.
     Without normalization ``_get_skill_def`` returns ``None`` and the
     optimizer silently ranks against zero DPS.

  2. ``_applicable_damage_stat_keys`` — the upgrade advisor used to test
     every ``*_damage_pct`` bucket for every skill, so a pure-physical
     melee build would surface "fire_damage_pct" and "necrotic_damage_pct"
     as 0% rows that polluted the top-N ranking.

  3. ``sum_flat_damage`` — previously summed every weapon-style flat
     damage field (e.g. ``added_melee_fire`` for a physical/void skill),
     inflating base damage with types the skill couldn't actually deal.

These tests construct ``BuildStats`` and ``SkillStatDef`` objects
directly and hit the hardcoded SKILL_STATS fallback in
``_get_skill_def`` — no Flask app context required.
"""
from __future__ import annotations

import pytest

from app.engines.optimization_engine import (
    _normalize_skill_name,
    _applicable_damage_stat_keys,
    get_stat_upgrades,
)
from app.engines.stat_engine import BuildStats
from app.domain.skill import SkillStatDef
from app.domain.calculators.damage_type_router import DamageType
from app.domain.calculators.skill_calculator import sum_flat_damage


# ---------------------------------------------------------------------------
# Section 1 — _normalize_skill_name
# ---------------------------------------------------------------------------

class TestNormalizeSkillName:
    """Verify every casing LE Tools / Maxroll / manual entry can produce
    lands on the canonical SKILL_STATS key form."""

    def test_snake_case(self):
        assert _normalize_skill_name("shadow_cascade") == "Shadow Cascade"

    def test_lowercase_with_spaces(self):
        assert _normalize_skill_name("shadow cascade") == "Shadow Cascade"

    def test_camel_case(self):
        assert _normalize_skill_name("ShadowCascade") == "Shadow Cascade"

    def test_already_canonical(self):
        assert _normalize_skill_name("Shadow Cascade") == "Shadow Cascade"

    def test_single_word_lowercase(self):
        assert _normalize_skill_name("fireball") == "Fireball"

    def test_dancing_strikes_snake_case(self):
        assert _normalize_skill_name("dancing_strikes") == "Dancing Strikes"

    def test_synchronized_strike_snake_case(self):
        assert _normalize_skill_name("synchronized_strike") == "Synchronized Strike"

    def test_empty_string(self):
        # Early return — empty in, empty out (don't blow up on missing data).
        assert _normalize_skill_name("") == ""


# ---------------------------------------------------------------------------
# Section 2 — _applicable_damage_stat_keys
# ---------------------------------------------------------------------------

class TestApplicableDamageStatKeys:
    """The filter that decides which ``*_damage_pct`` buckets the upgrade
    advisor should even bother testing for a given skill."""

    def test_shadow_cascade_includes_physical_void_melee(self):
        keys = _applicable_damage_stat_keys("Shadow Cascade")
        assert keys is not None
        assert "physical_damage_pct" in keys
        assert "void_damage_pct" in keys
        assert "melee_damage_pct" in keys

    def test_shadow_cascade_excludes_unrelated_types(self):
        keys = _applicable_damage_stat_keys("Shadow Cascade")
        assert keys is not None
        assert "necrotic_damage_pct" not in keys
        assert "fire_damage_pct" not in keys
        assert "cold_damage_pct" not in keys
        assert "spell_damage_pct" not in keys

    def test_fireball_includes_fire_and_spell(self):
        keys = _applicable_damage_stat_keys("Fireball")
        assert keys is not None
        assert "fire_damage_pct" in keys
        assert "spell_damage_pct" in keys

    def test_fireball_excludes_physical(self):
        keys = _applicable_damage_stat_keys("Fireball")
        assert keys is not None
        assert "physical_damage_pct" not in keys

    def test_unknown_skill_returns_none(self):
        # ``None`` means "skill not in registry — don't filter anything".
        # Callers fall back to testing every increment rather than silently
        # dropping all of them.
        assert _applicable_damage_stat_keys("NonexistentSkillFoo") is None


# ---------------------------------------------------------------------------
# Section 3 — get_stat_upgrades recommendations
# ---------------------------------------------------------------------------

def _bladedancer_shadow_cascade_stats() -> BuildStats:
    """A plausible end-game Bladedancer running Shadow Cascade.

    High physical + melee scaling (primary), moderate void (Shadow Cascade's
    secondary channel), high crit. necrotic_damage_pct=0 so the advisor has
    a strong incentive to rank it — but under the new filter it should be
    excluded outright.
    """
    return BuildStats(
        base_damage=110,
        attack_speed=1.3,
        crit_chance=0.55,
        crit_multiplier=2.8,
        physical_damage_pct=180,
        void_damage_pct=60,
        melee_damage_pct=120,
        necrotic_damage_pct=0,
        fire_damage_pct=0,
        cold_damage_pct=0,
        spell_damage_pct=0,
        crit_chance_pct=35,
        crit_multiplier_pct=80,
        attack_speed_pct=30,
        max_health=2400,
        armour=800,
    )


class TestGetStatUpgradesFiltersDamageTypes:
    """Verify the advisor no longer surfaces damage buckets Shadow Cascade
    cannot scale with."""

    def test_necrotic_damage_pct_excluded_from_top_5(self):
        stats = _bladedancer_shadow_cascade_stats()
        upgrades = get_stat_upgrades(stats, "Shadow Cascade", skill_level=20, top_n=5)
        stat_keys = {u.stat for u in upgrades}
        assert "necrotic_damage_pct" not in stat_keys

    def test_unrelated_damage_types_excluded_from_top_5(self):
        stats = _bladedancer_shadow_cascade_stats()
        upgrades = get_stat_upgrades(stats, "Shadow Cascade", skill_level=20, top_n=5)
        stat_keys = {u.stat for u in upgrades}
        assert "fire_damage_pct" not in stat_keys
        assert "cold_damage_pct" not in stat_keys
        assert "spell_damage_pct" not in stat_keys

    def test_applicable_offense_stat_surfaces_in_top_5(self):
        """At least one obviously-relevant stat should rank — if none do,
        either the filter over-restricted or the ranking is broken."""
        stats = _bladedancer_shadow_cascade_stats()
        upgrades = get_stat_upgrades(stats, "Shadow Cascade", skill_level=20, top_n=5)
        stat_keys = {u.stat for u in upgrades}
        expected_any = {
            "physical_damage_pct",
            "void_damage_pct",
            "melee_damage_pct",
            "crit_multiplier_pct",
            "crit_chance_pct",
            "attack_speed_pct",
        }
        assert stat_keys & expected_any, (
            f"none of {expected_any} appeared in top-5 stat keys {stat_keys}"
        )

    def test_snake_case_skill_name_matches_canonical(self):
        """``shadow_cascade`` and ``Shadow Cascade`` must produce identical
        output — the normalization step is the whole point of the fix."""
        stats = _bladedancer_shadow_cascade_stats()
        snake = get_stat_upgrades(stats, "shadow_cascade", skill_level=20, top_n=5)
        canonical = get_stat_upgrades(stats, "Shadow Cascade", skill_level=20, top_n=5)
        assert [u.stat for u in snake] == [u.stat for u in canonical]


# ---------------------------------------------------------------------------
# Section 4 — sum_flat_damage type-gating
# ---------------------------------------------------------------------------

def _shadow_cascade_def() -> SkillStatDef:
    """Stand-in SkillStatDef matching Shadow Cascade's damage profile.

    Constructed directly rather than looked up via SKILL_STATS so the test
    doesn't depend on any registry mutation elsewhere in the suite.
    """
    return SkillStatDef(
        base_damage=120,
        level_scaling=0.13,
        attack_speed=1.6,
        scaling_stats=("physical_damage_pct", "void_damage_pct"),
        data_version="test",
        is_melee=True,
        damage_types=(DamageType.PHYSICAL, DamageType.VOID),
    )


def _empty_types_melee_def() -> SkillStatDef:
    """Tag-only skill def — triggers the legacy broad-sum fallback."""
    return SkillStatDef(
        base_damage=0,
        level_scaling=0,
        attack_speed=1.0,
        scaling_stats=(),
        data_version="test",
        is_melee=True,
        damage_types=(),
    )


class TestSumFlatDamageTypeGating:
    """Shadow Cascade (physical/void melee) must not absorb added_melee_fire,
    added_melee_necrotic, etc. — those fields are for fire / necrotic melee
    skills like Forge Strike or a hypothetical necrotic warpath."""

    def test_physical_only_contributes(self):
        stats = BuildStats(added_melee_physical=50.0)
        assert sum_flat_damage(stats, _shadow_cascade_def()) == 50.0

    def test_void_only_contributes(self):
        stats = BuildStats(added_melee_void=30.0)
        assert sum_flat_damage(stats, _shadow_cascade_def()) == 30.0

    def test_necrotic_ignored_for_physical_void_skill(self):
        # Necrotic is not in Shadow Cascade's damage_types — must not bleed
        # into its flat total.
        stats = BuildStats(added_melee_necrotic=25.0)
        assert sum_flat_damage(stats, _shadow_cascade_def()) == 0.0

    def test_mixed_flats_only_matching_types_count(self):
        # 35 physical + 18 void = 53. necrotic=12 and fire=8 are dropped.
        stats = BuildStats(
            added_melee_physical=35.0,
            added_melee_void=18.0,
            added_melee_necrotic=12.0,
            added_melee_fire=8.0,
        )
        assert sum_flat_damage(stats, _shadow_cascade_def()) == 53.0

    def test_empty_damage_types_fallback_broad_sum(self):
        # Empty damage_types ⇒ legacy behaviour: sum every flat field for
        # the matching weapon style. Preserves correctness for unmigrated
        # tag-only skills like Rip Blood.
        stats = BuildStats(
            added_melee_physical=20.0,
            added_melee_necrotic=10.0,
        )
        assert sum_flat_damage(stats, _empty_types_melee_def()) == 30.0
