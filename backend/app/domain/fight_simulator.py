"""
Realistic Fight Simulation (Step 10).

simulate_fight() is the top-level entry point that orchestrates a complete
simulated combat encounter:

  1. Builds a CombatTimeline from the provided configuration.
  2. Applies an initial set of ailments and buffs.
  3. Re-applies ailments at the configured cast interval (simulating
     the player repeatedly using their skill).
  4. Returns a FightResult containing the full CombatResult plus metadata.

Public API:
  FightConfig     — parameters describing the skill being used and the fight
  FightResult     — final outcome with CombatResult + metadata
  simulate_fight() — execute the simulation
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.ailments import AilmentType
from app.domain.timeline import BuffInstance
from app.domain.enemy_behavior import EnemyBehaviorProfile
from app.domain.combat_timeline import CombatTimeline, CombatResult


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AilmentApplication:
    """
    Describes one type of ailment applied per cast.

    ailment_type    — which ailment is applied
    damage_per_tick — damage per second per stack
    duration        — how long each stack lasts
    stacks_per_cast — how many new stacks are applied each cast (default 1)
    """
    ailment_type:    AilmentType
    damage_per_tick: float
    duration:        float
    stacks_per_cast: int = 1


@dataclass(frozen=True)
class FightConfig:
    """
    Full configuration for a fight simulation.

    fight_duration    — total fight length in seconds
    cast_interval     — seconds between skill uses (re-application of ailments)
    ailments          — ailment types applied on each cast
    initial_buffs     — buffs/debuffs active at fight start
    behavior_profile  — optional enemy behavior (None = always attackable)
    tick_size         — simulation step in seconds (default 0.1)
    """
    fight_duration:   float
    cast_interval:    float
    ailments:         tuple[AilmentApplication, ...] = ()
    initial_buffs:    tuple[BuffInstance, ...] = ()
    behavior_profile: EnemyBehaviorProfile | None = None
    tick_size:        float = 0.1

    def __post_init__(self) -> None:
        if self.fight_duration < 0:
            raise ValueError(f"fight_duration must be >= 0, got {self.fight_duration}")
        if self.cast_interval <= 0:
            raise ValueError(f"cast_interval must be > 0, got {self.cast_interval}")
        if self.tick_size <= 0:
            raise ValueError(f"tick_size must be > 0, got {self.tick_size}")


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FightResult:
    """
    Full outcome of a simulated fight.

    combat_result  — damage/DPS breakdown from the CombatTimeline
    total_casts    — number of skill activations during the fight
    config         — the FightConfig that produced this result
    """
    combat_result: CombatResult
    total_casts:   int
    config:        FightConfig


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

def simulate_fight(config: FightConfig) -> FightResult:
    """
    Run a full fight simulation according to ``config``.

    The fight proceeds as follows:
      - At t=0, initial buffs are applied and first cast happens.
      - Every ``cast_interval`` seconds thereafter, another cast happens.
      - Each cast applies all configured ailments (stacks_per_cast times each).
      - The timeline advances between casts in cast_interval steps.
      - A final advance covers any remaining time after the last cast.

    Returns a FightResult summarising damage, DPS, and cast count.
    """
    timeline = CombatTimeline(
        tick_size=config.tick_size,
        behavior_profile=config.behavior_profile,
    )

    # Apply initial buffs
    for buff in config.initial_buffs:
        timeline.add_buff(buff)

    cast_count = 0
    elapsed    = 0.0

    while elapsed < config.fight_duration:
        # Perform a cast
        for application in config.ailments:
            for _ in range(application.stacks_per_cast):
                timeline.apply_ailment(
                    application.ailment_type,
                    application.damage_per_tick,
                    application.duration,
                )
        cast_count += 1

        # Advance to next cast or end of fight
        next_event = min(elapsed + config.cast_interval, config.fight_duration)
        advance_by = next_event - elapsed
        if advance_by > 0:
            timeline.advance(advance_by)
        elapsed = next_event

    result = FightResult(
        combat_result=timeline.get_result(),
        total_casts=cast_count,
        config=config,
    )
    return result
