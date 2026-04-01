"""
Final Damage Calculator — full hit-damage pipeline.

Pipeline: Base → Increased → More → Final

DamageContext captures the three stage values so callers pass a single
structured object instead of loose arguments. Build one with
DamageContext.from_build(), then hand it to calculate_final_damage().
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.calculators.increased_damage_calculator import sum_increased_damage
from app.domain.calculators.more_multiplier_calculator import apply_more_multiplier
from app.domain.calculators.stat_calculator import apply_percent_bonus
from app.domain.skill import SkillStatDef
from app.engines.stat_engine import BuildStats


@dataclass
class DamageContext:
    """
    Carries the pre-computed value for each pipeline stage.

    base_damage:      Effective base — scaled skill damage + flat gear damage.
    increased_damage: Sum of all additive increased% sources (percent-point).
    more_damage:      Each multiplicative 'more' source (percent-point list).
    """
    base_damage: float
    increased_damage: float
    more_damage: list[float] = field(default_factory=list)

    @classmethod
    def from_build(
        cls,
        effective_base: float,
        stats: BuildStats,
        skill_def: SkillStatDef,
        extra_more_pct: float = 0.0,
    ) -> DamageContext:
        """
        Compute all three stage values from build inputs.

        extra_more_pct: additional 'more' from the skill spec tree (percent-point).
        """
        return cls(
            base_damage=effective_base,
            increased_damage=sum_increased_damage(stats, skill_def),
            more_damage=[stats.more_damage_pct, extra_more_pct],
        )


def calculate_final_damage(ctx: DamageContext) -> float:
    """
    Apply the full pipeline to the values stored in ctx.

    Returns final per-hit damage, ready for crit and attack-speed application.
    """
    after_increased = apply_percent_bonus(ctx.base_damage, ctx.increased_damage)
    return apply_more_multiplier(after_increased, ctx.more_damage)
