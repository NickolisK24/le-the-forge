"""
Combat Simulator — deterministic time-based execution loop.

Orchestrates existing engines to simulate a full combat encounter:

    SkillExecutionEngine  →  EnemyDefenseEngine  →  accumulate damage

The loop advances in fixed ticks. At each tick, skills whose cooldown
has elapsed are cast in priority order. Damage is computed via the
existing engines — no math is duplicated here.

Mana integration: skills with mana_cost > 0 require sufficient mana
to cast. Insufficient mana skips the cast without triggering cooldown.
Mana regenerates every tick after the casting phase.

All state is deterministic: same inputs → same outputs, no randomness.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.combat.combat_scenario import CombatScenario, SkillRotationEntry
from app.domain.armor_shred import armor_shred_amount
from app.enemies.enemy_defense import EnemyDefenseEngine
from app.engines.stat_engine import BuildStats
from app.skills.skill_execution import SkillExecutionEngine
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


# ---------------------------------------------------------------------------
# Timeline event record
# ---------------------------------------------------------------------------

@dataclass
class TimelineEvent:
    """A single event in the combat timeline."""
    time: float
    skill_name: str
    damage_before_defense: float
    damage_after_defense: float
    mitigation_pct: float

    def to_dict(self) -> dict:
        return {
            "time": round(self.time, 3),
            "skill_name": self.skill_name,
            "damage_before_defense": round(self.damage_before_defense, 2),
            "damage_after_defense": round(self.damage_after_defense, 2),
            "mitigation_pct": round(self.mitigation_pct, 2),
        }


# ---------------------------------------------------------------------------
# Simulation result
# ---------------------------------------------------------------------------

@dataclass
class SimulationResult:
    """Output of a full combat simulation.

    Fields:
        total_damage:       Sum of all post-defense damage dealt.
        effective_dps:      total_damage / fight_duration.
        fight_duration:     Actual simulated duration in seconds.
        total_casts:        Total number of skill activations.
        skill_usage:        Per-skill cast counts.
        skill_damage:       Per-skill total damage dealt.
        timeline:           Ordered list of cast events (if captured).
        ticks_simulated:    Number of ticks advanced.
        raw_dps:            DPS before enemy defenses.
        total_mana_spent:   Total mana consumed across all casts.
        total_mana_regenerated: Total mana restored via regen.
        casts_skipped_oom:  Number of casts skipped due to insufficient mana.
    """
    total_damage: float
    effective_dps: float
    fight_duration: float
    total_casts: int
    skill_usage: dict[str, int] = field(default_factory=dict)
    skill_damage: dict[str, float] = field(default_factory=dict)
    timeline: list[TimelineEvent] = field(default_factory=list)
    ticks_simulated: int = 0
    raw_dps: float = 0.0
    ailment_dps: dict[str, float] = field(default_factory=dict)
    total_dps_with_ailments: float = 0.0
    total_mana_spent: float = 0.0
    total_mana_regenerated: float = 0.0
    casts_skipped_oom: int = 0

    def to_dict(self) -> dict:
        d = {
            "total_damage": round(self.total_damage, 2),
            "effective_dps": round(self.effective_dps, 2),
            "fight_duration": round(self.fight_duration, 3),
            "total_casts": self.total_casts,
            "skill_usage": dict(self.skill_usage),
            "skill_damage": {k: round(v, 2) for k, v in self.skill_damage.items()},
            "ticks_simulated": self.ticks_simulated,
            "raw_dps": round(self.raw_dps, 2),
        }
        if self.ailment_dps:
            d["ailment_dps"] = {k: round(v, 2) for k, v in self.ailment_dps.items()}
            d["total_dps_with_ailments"] = round(self.total_dps_with_ailments, 2)
        if self.total_mana_spent > 0 or self.total_mana_regenerated > 0:
            d["total_mana_spent"] = round(self.total_mana_spent, 2)
            d["total_mana_regenerated"] = round(self.total_mana_regenerated, 2)
            d["casts_skipped_oom"] = self.casts_skipped_oom
        return d


# ---------------------------------------------------------------------------
# Simulator
# ---------------------------------------------------------------------------

class CombatSimulator:
    """Deterministic combat loop: scenario + stats → SimulationResult.

    Usage::

        sim = CombatSimulator()
        result = sim.simulate(scenario, stats)
        print(result.effective_dps)
    """

    def __init__(self) -> None:
        self._skill_engine = SkillExecutionEngine()
        self._defense_engine = EnemyDefenseEngine()

    def simulate(
        self,
        scenario: CombatScenario,
        stats: BuildStats,
        capture_timeline: bool = False,
    ) -> SimulationResult:
        """Run a deterministic combat simulation.

        Args:
            scenario:         CombatScenario defining duration, enemy, rotation.
            stats:            Fully resolved BuildStats (read-only).
            capture_timeline: If True, record every cast event.

        Returns:
            SimulationResult with total damage, DPS, and per-skill breakdown.
        """
        duration = scenario.duration_seconds
        tick = scenario.tick_size
        rotation = sorted(scenario.rotation, key=lambda e: e.priority)

        # Create mana pool for this simulation run (fresh per run)
        mana_pool = scenario.create_mana_pool()
        mana_enabled = mana_pool is not None

        log.debug(
            "combat_sim.start",
            duration=duration,
            tick=tick,
            n_skills=len(rotation),
            mana_enabled=mana_enabled,
            max_mana=mana_pool.max_mana if mana_pool else 0,
        )

        # Pre-compute skill execution results (deterministic — same every cast)
        skill_results: dict[str, object] = {}
        defense_results: dict[str, object] = {}
        skill_mana_costs: dict[str, float] = {}

        for entry in rotation:
            key = entry.skill_name or id(entry)
            sr = self._skill_engine.execute(
                skill_def=entry.skill_def,
                stats=stats,
                level=entry.level,
                skill_mods=entry.skill_mods,
                skill_name=entry.skill_name,
            )
            skill_results[key] = sr
            skill_mana_costs[key] = entry.skill_def.mana_cost

            if scenario.enemy is not None:
                # Calculate steady-state armor shred from build stats.
                # Use total hits: skill's native hit_count × hits_per_cast
                # (hit_count from SkillStatDef, hits_per_cast from SkillModifiers)
                total_hits = entry.skill_def.hit_count * sr.hits_per_cast
                shred = armor_shred_amount(
                    stats.armour_shred_chance,
                    sr.casts_per_second,
                    total_hits,
                )
                dr = self._defense_engine.apply_defenses(
                    sr, scenario.enemy,
                    penetration=scenario.penetration or None,
                    armor_shred=shred,
                )
                defense_results[key] = dr
            else:
                defense_results[key] = None

        # Cooldown tracking: time remaining until each skill can cast again
        cooldowns: dict[str, float] = {}
        for entry in rotation:
            key = entry.skill_name or id(entry)
            cooldowns[key] = 0.0  # all ready at t=0

        # Simulation state
        total_damage = 0.0
        total_raw_damage = 0.0
        total_casts = 0
        total_mana_spent = 0.0
        total_mana_regenerated = 0.0
        casts_skipped_oom = 0
        skill_usage: dict[str, int] = {}
        skill_damage: dict[str, float] = {}
        timeline: list[TimelineEvent] = []

        elapsed = 0.0
        ticks = 0

        while elapsed < duration:
            # Check each skill in priority order
            for entry in rotation:
                key = entry.skill_name or id(entry)

                if cooldowns[key] > 1e-9:
                    continue  # still on cooldown

                # Mana check — skip cast if insufficient mana
                cost = skill_mana_costs[key]
                if mana_enabled and cost > 0:
                    if not mana_pool.can_afford(cost):
                        casts_skipped_oom += 1
                        continue  # skip — no cooldown triggered

                # Spend mana
                if mana_enabled and cost > 0:
                    mana_pool.spend(cost)
                    total_mana_spent += cost

                # Cast this skill
                sr = skill_results[key]
                dr = defense_results[key]

                if dr is not None:
                    damage = dr.damage_dealt
                    raw_damage = dr.damage_before
                    mit_pct = dr.mitigation_pct
                else:
                    damage = sr.average_hit
                    raw_damage = sr.average_hit
                    mit_pct = 0.0

                # Account for hits_per_cast
                damage *= sr.hits_per_cast
                raw_damage *= sr.hits_per_cast

                total_damage += damage
                total_raw_damage += raw_damage
                total_casts += 1
                skill_usage[key] = skill_usage.get(key, 0) + 1
                skill_damage[key] = skill_damage.get(key, 0.0) + damage

                if capture_timeline:
                    timeline.append(TimelineEvent(
                        time=elapsed,
                        skill_name=entry.skill_name,
                        damage_before_defense=raw_damage,
                        damage_after_defense=damage,
                        mitigation_pct=mit_pct,
                    ))

                # Set cooldown
                cooldowns[key] = entry.effective_interval

            # Advance time
            elapsed += tick
            ticks += 1

            # Reduce cooldowns
            for key in cooldowns:
                cooldowns[key] = max(0.0, cooldowns[key] - tick)

            # Mana regeneration (after casting phase, every tick)
            if mana_enabled:
                restored = mana_pool.regenerate(tick)
                total_mana_regenerated += restored

        fight_duration = elapsed
        effective_dps = total_damage / fight_duration if fight_duration > 0 else 0.0
        raw_dps = total_raw_damage / fight_duration if fight_duration > 0 else 0.0

        # Aggregate ailment DPS from all skills (steady-state, additive)
        agg_ailment_dps: dict[str, float] = {}
        for entry in rotation:
            key = entry.skill_name or id(entry)
            sr = skill_results[key]
            for atype, adps in sr.ailment_dps.items():
                agg_ailment_dps[atype] = agg_ailment_dps.get(atype, 0.0) + adps
        total_ailment_dps = sum(agg_ailment_dps.values())
        total_dps_with_ailments = effective_dps + total_ailment_dps

        log.debug(
            "combat_sim.done",
            total_damage=round(total_damage, 2),
            effective_dps=round(effective_dps, 2),
            ailment_dps=round(total_ailment_dps, 2),
            total_casts=total_casts,
            ticks=ticks,
            mana_spent=round(total_mana_spent, 2),
            mana_regenerated=round(total_mana_regenerated, 2),
            casts_skipped_oom=casts_skipped_oom,
        )

        return SimulationResult(
            total_damage=total_damage,
            effective_dps=effective_dps,
            fight_duration=fight_duration,
            total_casts=total_casts,
            skill_usage=skill_usage,
            skill_damage=skill_damage,
            ailment_dps=agg_ailment_dps,
            total_dps_with_ailments=total_dps_with_ailments,
            timeline=timeline if capture_timeline else [],
            ticks_simulated=ticks,
            raw_dps=raw_dps,
            total_mana_spent=total_mana_spent,
            total_mana_regenerated=total_mana_regenerated,
            casts_skipped_oom=casts_skipped_oom,
        )
