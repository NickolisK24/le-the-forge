"""
Enemy Defense Engine — applies enemy resistances, armor, and dodge to
incoming skill damage.

This system runs AFTER skill damage is computed (SkillExecutionResult)
and produces a DefensedDamageResult showing how much damage survives
enemy defenses.

Architecture:
  - Consumes SkillExecutionResult (read-only — never modifies it)
  - Reuses existing domain math: resistance.py, armor.py, dodge.py,
    penetration.py
  - Deterministic: no randomness; dodge uses expected-value math
  - Pure logic: no DB, no HTTP, no Flask context

Pipeline:
  1. Compute per-type damage from SkillExecutionResult
  2. Apply resistance reduction per damage type
  3. Apply armor mitigation to physical component
  4. Apply dodge chance as expected-value multiplier
  5. Return DefensedDamageResult
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.domain.armor import armor_mitigation_pct, apply_armor
from app.domain.dodge import dodge_chance
from app.domain.enemy import EnemyInstance, EnemyArchetype, EnemyStats, EnemyProfile
from app.domain.resistance import apply_resistance, RES_CAP
from app.skills.skill_execution import SkillExecutionResult
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class DefensedDamageResult:
    """Output of enemy defense application.

    Fields:
        damage_dealt:       Final damage after all enemy defenses.
        damage_mitigated:   Total damage absorbed by defenses.
        damage_before:      Original damage (from SkillExecutionResult).
        mitigation_pct:     Overall percentage of damage mitigated.
        effective_dps:      DPS after defenses (damage_dealt * speed * hits).
        resistance_reduction: Per-type damage lost to resistances.
        armor_reduction:    Damage lost to armor (physical only).
        dodge_reduction:    Damage lost to dodge (expected value).
        dodge_chance:       Enemy's effective dodge chance.
        per_type_damage:    Per-type damage after resistances.
        debug:              Optional debug trace.
    """
    damage_dealt: float
    damage_mitigated: float
    damage_before: float
    mitigation_pct: float
    effective_dps: float
    resistance_reduction: float
    armor_reduction: float
    dodge_reduction: float
    dodge_chance_pct: float
    per_type_damage: dict[str, float] = field(default_factory=dict)
    debug: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "damage_dealt": round(self.damage_dealt, 2),
            "damage_mitigated": round(self.damage_mitigated, 2),
            "damage_before": round(self.damage_before, 2),
            "mitigation_pct": round(self.mitigation_pct, 2),
            "effective_dps": round(self.effective_dps, 2),
            "resistance_reduction": round(self.resistance_reduction, 2),
            "armor_reduction": round(self.armor_reduction, 2),
            "dodge_reduction": round(self.dodge_reduction, 2),
            "dodge_chance_pct": round(self.dodge_chance_pct, 4),
            "per_type_damage": {k: round(v, 2) for k, v in self.per_type_damage.items()},
        }


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class EnemyDefenseEngine:
    """Stateless engine: (SkillExecutionResult + EnemyInstance) → DefensedDamageResult.

    Usage::

        engine = EnemyDefenseEngine()
        enemy = EnemyInstance.from_archetype(EnemyArchetype.BOSS)
        result = engine.apply_defenses(skill_result, enemy)
        print(result.damage_dealt)
    """

    def apply_defenses(
        self,
        skill_result: SkillExecutionResult,
        enemy: EnemyInstance,
        penetration: dict[str, float] | None = None,
        capture_debug: bool = False,
    ) -> DefensedDamageResult:
        """Apply enemy defenses to skill damage and return post-defense result.

        Args:
            skill_result:  Output from SkillExecutionEngine.execute().
            enemy:         EnemyInstance with resistances, armor, shred state.
            penetration:   Per-type penetration values from BuildStats
                           (e.g. {"fire": 15.0, "physical": 10.0}).
            capture_debug: If True, attach a debug trace dict.

        Returns:
            DefensedDamageResult with final damage after all defenses.
        """
        pen = penetration or {}
        debug_trace: dict = {} if capture_debug else None  # type: ignore[assignment]
        incoming = skill_result.average_hit

        log.debug(
            "enemy_defense.start",
            incoming=round(incoming, 2),
            enemy_armor=enemy.armor,
        )

        # ------------------------------------------------------------------
        # 1 — Per-type damage split
        # ------------------------------------------------------------------
        # If skill_result has per-type breakdown, use it.
        # Otherwise treat all damage as untyped (no resistance applied).
        damage_by_type = dict(skill_result.damage_by_type)  # copy

        if not damage_by_type:
            # Untyped damage — no resistance to apply, but armor may still apply
            damage_by_type = {"untyped": incoming}

        # Scale per-type values so they sum to average_hit
        # (skill_result.damage_by_type is based on hit_damage, not average_hit)
        if skill_result.hit_damage > 0 and skill_result.damage_by_type:
            scale = incoming / skill_result.hit_damage
            damage_by_type = {k: v * scale for k, v in damage_by_type.items()}

        if capture_debug:
            debug_trace["damage_by_type_before"] = {
                k: round(v, 2) for k, v in damage_by_type.items()
            }

        # ------------------------------------------------------------------
        # 2 — Apply resistance reduction per damage type
        # ------------------------------------------------------------------
        total_res_reduction = 0.0
        after_resistance: dict[str, float] = {}

        for dmg_type, dmg_value in damage_by_type.items():
            if dmg_type == "untyped":
                after_resistance[dmg_type] = dmg_value
                continue

            eff_res = enemy.effective_resistance(
                dmg_type,
                penetration=pen.get(dmg_type, 0.0),
            )
            reduced = apply_resistance(dmg_value, eff_res)
            res_lost = dmg_value - reduced
            total_res_reduction += res_lost
            after_resistance[dmg_type] = reduced

            if capture_debug:
                debug_trace.setdefault("resistance_detail", {})[dmg_type] = {
                    "effective_res": round(eff_res, 2),
                    "before": round(dmg_value, 2),
                    "after": round(reduced, 2),
                }

        log.debug(
            "enemy_defense.resistance_done",
            total_res_reduction=round(total_res_reduction, 2),
        )

        # ------------------------------------------------------------------
        # 3 — Apply armor mitigation to physical component
        # ------------------------------------------------------------------
        total_armor_reduction = 0.0
        after_armor: dict[str, float] = {}

        for dmg_type, dmg_value in after_resistance.items():
            if dmg_type == "physical":
                mitigated = apply_armor(dmg_value, float(enemy.armor))
                armor_lost = dmg_value - mitigated
                total_armor_reduction += armor_lost
                after_armor[dmg_type] = mitigated
            else:
                after_armor[dmg_type] = dmg_value

        if capture_debug:
            debug_trace["armor_mitigation"] = {
                "enemy_armor": enemy.armor,
                "physical_before": round(after_resistance.get("physical", 0.0), 2),
                "physical_after": round(after_armor.get("physical", 0.0), 2),
                "armor_reduction": round(total_armor_reduction, 2),
            }

        log.debug(
            "enemy_defense.armor_done",
            armor_reduction=round(total_armor_reduction, 2),
        )

        # ------------------------------------------------------------------
        # 4 — Compute post-armor total
        # ------------------------------------------------------------------
        post_defense_hit = sum(after_armor.values())

        # ------------------------------------------------------------------
        # 5 — Apply dodge as expected-value multiplier
        # ------------------------------------------------------------------
        # Enemy dodge rating is not currently modeled in EnemyStats,
        # so dodge_chance is 0 unless explicitly provided. This keeps
        # the engine ready for future extension.
        enemy_dodge = 0.0  # placeholder — EnemyStats has no dodge_rating field
        dodge_ch = dodge_chance(enemy_dodge)
        dodge_reduction = post_defense_hit * dodge_ch
        final_damage = post_defense_hit * (1.0 - dodge_ch)

        if capture_debug:
            debug_trace["dodge"] = {
                "dodge_chance": round(dodge_ch, 4),
                "dodge_reduction": round(dodge_reduction, 2),
            }

        # ------------------------------------------------------------------
        # 6 — Compute effective DPS
        # ------------------------------------------------------------------
        if incoming > 0:
            defense_multiplier = final_damage / incoming
        else:
            defense_multiplier = 1.0
        effective_dps = skill_result.dps * defense_multiplier

        # ------------------------------------------------------------------
        # 7 — Mitigation summary
        # ------------------------------------------------------------------
        total_mitigated = incoming - final_damage
        mitigation_pct = (total_mitigated / incoming * 100.0) if incoming > 0 else 0.0

        log.debug(
            "enemy_defense.done",
            final_damage=round(final_damage, 2),
            mitigation_pct=round(mitigation_pct, 2),
            effective_dps=round(effective_dps, 2),
        )

        return DefensedDamageResult(
            damage_dealt=final_damage,
            damage_mitigated=total_mitigated,
            damage_before=incoming,
            mitigation_pct=mitigation_pct,
            effective_dps=effective_dps,
            resistance_reduction=total_res_reduction,
            armor_reduction=total_armor_reduction,
            dodge_reduction=dodge_reduction,
            dodge_chance_pct=dodge_ch * 100.0,
            per_type_damage={k: v for k, v in after_armor.items() if v > 0},
            debug=debug_trace,
        )

    def apply_defenses_from_profile(
        self,
        skill_result: SkillExecutionResult,
        profile: EnemyProfile,
        penetration: dict[str, float] | None = None,
        capture_debug: bool = False,
    ) -> DefensedDamageResult:
        """Convenience: apply defenses using an EnemyProfile directly."""
        stats = EnemyStats(
            health=profile.health,
            armor=profile.armor,
            resistances=dict(profile.resistances),
        )
        enemy = EnemyInstance.from_stats(stats)
        return self.apply_defenses(skill_result, enemy, penetration, capture_debug)

    def apply_defenses_from_archetype(
        self,
        skill_result: SkillExecutionResult,
        archetype: EnemyArchetype,
        penetration: dict[str, float] | None = None,
        capture_debug: bool = False,
    ) -> DefensedDamageResult:
        """Convenience: apply defenses using an EnemyArchetype."""
        enemy = EnemyInstance.from_archetype(archetype)
        return self.apply_defenses(skill_result, enemy, penetration, capture_debug)
