"""
Skill Execution Engine — computes damage output for a skill using resolved
BuildStats.

This is the simulation entry point: given a fully resolved character sheet
(BuildStats) and a skill (SkillStatDef + SkillSpec + SkillModifiers), produce
a SkillExecutionResult containing per-hit damage, average hit, DPS, crit
breakdown, and per-type damage split.

Architecture:
  - Consumes BuildStats (read-only — never modifies stats)
  - Delegates to existing calculators (skill, damage, crit, speed)
  - Deterministic: identical inputs → identical outputs
  - No DB, no HTTP, no Flask context

Pipeline:
  1. Scale skill base damage by level
  2. Add flat gear damage
  3. Compute increased % damage pool
  4. Apply "more" multipliers
  5. Compute per-hit damage (DamageResult)
  6. Compute effective crit chance and multiplier
  7. Compute average hit (crit-weighted)
  8. Compute effective attack/cast speed
  9. Compute DPS (average_hit × hits_per_cast × casts_per_sec)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.domain.calculators.crit_calculator import (
    calculate_average_hit,
    crit_contribution_pct,
    effective_crit_chance,
    effective_crit_multiplier,
)
from app.domain.calculators.damage_type_router import DamageType
from app.domain.calculators.final_damage_calculator import (
    DamageContext,
    DamageResult,
    calculate_final_damage,
)
from app.domain.calculators.skill_calculator import (
    hits_per_cast,
    scale_skill_damage,
    sum_flat_damage,
)
from app.domain.calculators.ailment_calculator import calc_ailment_dps
from app.domain.calculators.speed_calculator import effective_attack_speed
from app.domain.skill import SkillStatDef, SkillSpec, calculate_multi_hit_dps
from app.domain.skill_modifiers import SkillModifiers
from app.engines.stat_engine import BuildStats
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class SkillExecutionResult:
    """Complete output of a single skill execution computation.

    Fields:
        hit_damage:        Raw per-hit damage (before crit averaging).
        average_hit:       Crit-weighted per-hit damage.
        dps:               Sustained damage per second.
        crit_chance:       Effective crit chance (0.0–0.95).
        crit_multiplier:   Effective crit multiplier (e.g. 2.0).
        crit_contribution: Percentage of average hit from crits.
        casts_per_second:  Effective attack/cast speed.
        hits_per_cast:     Total hits per cast activation.
        damage_by_type:    Per-type damage breakdown (from DamageResult).
        skill_name:        Name of the skill (informational).
        debug:             Optional debug trace dict.
    """
    hit_damage: float
    average_hit: float
    dps: float
    crit_chance: float
    crit_multiplier: float
    crit_contribution: int
    casts_per_second: float
    hits_per_cast: int
    damage_by_type: dict[str, float] = field(default_factory=dict)
    ailment_dps: dict[str, float] = field(default_factory=dict)
    total_dps: float = 0.0  # hit DPS + ailment DPS combined
    skill_name: str = ""
    debug: Optional[dict] = None

    def to_dict(self) -> dict:
        d = {
            "skill_name": self.skill_name,
            "hit_damage": round(self.hit_damage, 2),
            "average_hit": round(self.average_hit, 2),
            "dps": round(self.dps, 2),
            "crit_chance": round(self.crit_chance, 4),
            "crit_multiplier": round(self.crit_multiplier, 4),
            "crit_contribution": self.crit_contribution,
            "casts_per_second": round(self.casts_per_second, 4),
            "hits_per_cast": self.hits_per_cast,
            "damage_by_type": {k: round(v, 2) for k, v in self.damage_by_type.items()},
        }
        if self.ailment_dps:
            d["ailment_dps"] = {k: round(v, 2) for k, v in self.ailment_dps.items()}
            d["total_dps"] = round(self.total_dps, 2)
        return d


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class SkillExecutionEngine:
    """Stateless engine: (SkillStatDef + SkillModifiers + BuildStats) → SkillExecutionResult.

    Usage::

        engine = SkillExecutionEngine()
        result = engine.execute(skill_def, stats, level=20, skill_mods=sm)
        print(result.dps)
    """

    def execute(
        self,
        skill_def: SkillStatDef,
        stats: BuildStats,
        level: int = 1,
        skill_mods: SkillModifiers | None = None,
        skill_name: str = "",
        capture_debug: bool = False,
    ) -> SkillExecutionResult:
        """Execute a skill against resolved BuildStats and return damage output.

        Args:
            skill_def:     Skill template (from SkillRegistry or manual).
            stats:         Fully resolved BuildStats (read-only).
            level:         Skill level (1–20).
            skill_mods:    Per-skill spec-tree modifiers. Defaults to empty.
            skill_name:    Optional name for labeling the result.
            capture_debug: If True, attach a debug trace dict.

        Returns:
            SkillExecutionResult with all damage metrics.
        """
        sm = skill_mods or SkillModifiers()
        debug_trace: dict = {} if capture_debug else None  # type: ignore[assignment]

        log.debug(
            "skill_execution.start",
            skill=skill_name,
            level=level,
            base_damage=skill_def.base_damage,
        )

        # 1 — Scale base damage by level
        scaled = scale_skill_damage(
            skill_def.base_damage,
            skill_def.level_scaling,
            level,
            skill_def.damage_types,
        )
        scaled_total = sum(scaled.values()) if scaled else (
            skill_def.base_damage * (1 + skill_def.level_scaling * (level - 1))
        )

        # 2 — Add flat gear damage
        flat_added = sum_flat_damage(stats, skill_def)
        effective_base = scaled_total + flat_added

        if capture_debug:
            debug_trace["scaled_total"] = round(scaled_total, 2)
            debug_trace["flat_added"] = round(flat_added, 2)
            debug_trace["effective_base"] = round(effective_base, 2)

        # 3–4 — Build DamageContext and compute final per-hit damage
        ctx = DamageContext.from_build(
            effective_base,
            stats,
            skill_def,
            extra_more_pct=sm.more_damage_pct,
            scaled=scaled or None,
        )
        dmg_result: DamageResult = calculate_final_damage(ctx, debug=capture_debug)
        hit_damage = dmg_result.total

        if capture_debug:
            debug_trace["increased_damage_pct"] = ctx.increased_damage
            debug_trace["more_damage_sources"] = ctx.more_damage
            debug_trace["hit_damage"] = round(hit_damage, 2)

        # 5 — Effective crit chance and multiplier (build + skill mods)
        crit_ch = effective_crit_chance(stats.crit_chance, sm.crit_chance_pct)
        crit_mul = effective_crit_multiplier(stats.crit_multiplier, sm.crit_multiplier_pct)

        # 6 — Average hit (crit-weighted)
        avg_hit = calculate_average_hit(hit_damage, crit_ch, crit_mul)
        crit_pct = crit_contribution_pct(hit_damage, crit_ch, crit_mul, avg_hit)

        if capture_debug:
            debug_trace["crit_chance"] = round(crit_ch, 4)
            debug_trace["crit_multiplier"] = round(crit_mul, 4)
            debug_trace["average_hit"] = round(avg_hit, 2)

        # 7 — Effective attack/cast speed
        casts_per_sec = effective_attack_speed(skill_def, stats, sm)

        # 8 — Hits per cast (base + spec-tree additions)
        total_hits = hits_per_cast(sm.added_hits_per_cast)

        # 9 — Hit DPS
        dps = avg_hit * total_hits * casts_per_sec

        # 10 — Ailment DPS (bleed, ignite, poison from proc chance + scaling)
        bleed, ignite, poison = calc_ailment_dps(hit_damage, casts_per_sec, stats)
        ailment_dps: dict[str, float] = {}
        if bleed > 0:
            ailment_dps["bleed"] = float(bleed)
        if ignite > 0:
            ailment_dps["ignite"] = float(ignite)
        if poison > 0:
            ailment_dps["poison"] = float(poison)
        total_ailment_dps = sum(ailment_dps.values())
        total_dps = dps + total_ailment_dps

        if capture_debug:
            debug_trace["casts_per_second"] = round(casts_per_sec, 4)
            debug_trace["hits_per_cast"] = total_hits
            debug_trace["dps"] = round(dps, 2)
            debug_trace["ailment_dps"] = {k: round(v, 2) for k, v in ailment_dps.items()}
            debug_trace["total_dps"] = round(total_dps, 2)

        # Per-type breakdown (convert DamageType enum → string keys)
        damage_by_type = {
            dt.value: v for dt, v in dmg_result.damage_by_type.items()
        }

        log.debug(
            "skill_execution.done",
            skill=skill_name,
            hit_damage=round(hit_damage, 2),
            dps=round(dps, 2),
            ailment_dps=round(total_ailment_dps, 2),
        )

        return SkillExecutionResult(
            hit_damage=hit_damage,
            average_hit=avg_hit,
            dps=dps,
            crit_chance=crit_ch,
            crit_multiplier=crit_mul,
            crit_contribution=crit_pct,
            casts_per_second=casts_per_sec,
            hits_per_cast=total_hits,
            damage_by_type=damage_by_type,
            ailment_dps=ailment_dps,
            total_dps=total_dps,
            skill_name=skill_name,
            debug=debug_trace,
        )

    def execute_from_spec(
        self,
        skill_spec: SkillSpec,
        skill_def: SkillStatDef,
        stats: BuildStats,
        skill_mods: SkillModifiers | None = None,
        capture_debug: bool = False,
    ) -> SkillExecutionResult:
        """Convenience: execute using a SkillSpec (includes name and level)."""
        return self.execute(
            skill_def=skill_def,
            stats=stats,
            level=skill_spec.level,
            skill_mods=skill_mods,
            skill_name=skill_spec.skill_name,
            capture_debug=capture_debug,
        )
