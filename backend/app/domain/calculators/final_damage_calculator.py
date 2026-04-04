"""
Final Damage Calculator — full hit-damage pipeline.

Pipeline: Base → Increased → More → Final

DamageContext captures the three stage values so callers pass a single
structured object instead of loose arguments. Build one with
DamageContext.from_build(), then hand it to calculate_final_damage().

DamageResult is the output: total hit damage plus a per-type breakdown
populated when the caller provides the scaled dict from scale_skill_damage().
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.calculators.damage_type_router import DamageType
from app.domain.calculators.increased_damage_calculator import sum_increased_damage
from app.domain.calculators.more_multiplier_calculator import apply_more_multiplier
from app.domain.calculators.stat_calculator import apply_percent_bonus
from app.domain.skill import SkillStatDef
from app.engines.stat_engine import BuildStats
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


@dataclass
class DamageResult:
    """
    Output of the full hit-damage pipeline.

    total:          Combined hit damage across all types.
    damage_by_type: Per-type breakdown; proportional to each type's share of
                    base damage. Empty when no scaled dict was provided.
    """
    total: float
    damage_by_type: dict[DamageType, float] = field(default_factory=dict)


@dataclass
class DamageContext:
    """
    Carries the pre-computed value for each pipeline stage.

    base_damage:      Effective base — scaled skill damage + flat gear damage.
    increased_damage: Sum of all additive increased% sources (percent-point).
    more_damage:      Each multiplicative 'more' source (percent-point list).
    scaled:           Per-type base damage from scale_skill_damage(); used to
                      populate DamageResult.damage_by_type. Empty by default.
    """
    base_damage: float
    increased_damage: float
    more_damage: list[float] = field(default_factory=list)
    scaled: dict[DamageType, float] = field(default_factory=dict)

    @classmethod
    def from_build(
        cls,
        effective_base: float,
        stats: BuildStats,
        skill_def: SkillStatDef,
        extra_more_pct: float = 0.0,
        *,
        scaled: dict[DamageType, float] | None = None,
    ) -> DamageContext:
        """
        Compute all three stage values from build inputs.

        extra_more_pct: additional 'more' from the skill spec tree (percent-point).
        scaled:         per-type base damage from scale_skill_damage(); pass to
                        get a populated damage_by_type in the result.
        """
        return cls(
            base_damage=effective_base,
            increased_damage=sum_increased_damage(stats, skill_def),
            more_damage=[stats.more_damage_pct, extra_more_pct],
            scaled=scaled or {},
        )


def calculate_final_damage(ctx: DamageContext, *, debug: bool = False) -> DamageResult:
    """
    Apply the full pipeline to the values stored in ctx.

    Returns a DamageResult with:
      total          — final per-hit damage, ready for crit and attack-speed application
      damage_by_type — per-type split proportional to ctx.scaled; empty if not provided

    Pass debug=True to emit a structured trace log of each pipeline stage.
    """
    after_increased = apply_percent_bonus(ctx.base_damage, ctx.increased_damage)
    total = apply_more_multiplier(after_increased, ctx.more_damage)

    # Per-type breakdown: each type's hit damage is proportional to its share
    # of the pre-pipeline base damage (same multipliers apply to every type).
    if ctx.scaled:
        scaled_total = sum(ctx.scaled.values())
        damage_by_type: dict[DamageType, float] = (
            {dt: total * (v / scaled_total) for dt, v in ctx.scaled.items()}
            if scaled_total > 0 else {}
        )
    else:
        damage_by_type = {}

    if debug:
        log.debug(
            "damage_pipeline",
            base=round(ctx.base_damage, 2),
            increased_pct=ctx.increased_damage,
            after_increased=round(after_increased, 2),
            more_values=ctx.more_damage,
            final=round(total, 2),
            damage_by_type={dt.value: round(v, 2) for dt, v in damage_by_type.items()},
        )

    return DamageResult(total=total, damage_by_type=damage_by_type)
