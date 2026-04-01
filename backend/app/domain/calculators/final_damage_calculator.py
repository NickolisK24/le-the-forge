"""
Final Damage Calculator — full hit-damage pipeline.

Pipeline: Base → Increased → More → Final

Consumers (combat_engine) call calculate_final_damage() with an already-built
effective_base (scaled skill damage + flat added gear damage) and receive the
final per-hit damage value ready for crit / attack-speed application.
"""

from app.domain.calculators.increased_damage_calculator import sum_increased_damage
from app.domain.calculators.more_multiplier_calculator import apply_more_multiplier
from app.domain.calculators.stat_calculator import apply_percent_bonus
from app.domain.skill import SkillStatDef
from app.engines.stat_engine import BuildStats


def calculate_final_damage(
    effective_base: float,
    stats: BuildStats,
    skill_def: SkillStatDef,
    extra_more_pct: float = 0.0,
) -> float:
    """
    Apply the full damage pipeline to effective_base.

    Args:
        effective_base:  Scaled skill base damage + flat added damage from gear.
        stats:           Aggregated build stats.
        skill_def:       Skill definition (scaling_stats, weapon flags, etc.).
        extra_more_pct:  Additional 'more' percent from the skill spec tree
                         (percent-point, 0.0 = no bonus).

    Returns:
        Final per-hit damage after increased and more modifiers.
    """
    increased = sum_increased_damage(stats, skill_def)
    after_increased = apply_percent_bonus(effective_base, increased)
    return apply_more_multiplier(after_increased, [stats.more_damage_pct, extra_more_pct])
