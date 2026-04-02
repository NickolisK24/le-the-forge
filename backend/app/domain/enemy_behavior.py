"""
Enemy Behavior Profiles (Step 8).

Models how an enemy spends time during combat — moving, attacking, and
being stunned — so downstream simulations can account for downtime when
computing effective DPS exposure.

  EnemyBehaviorProfile — frozen dataclass encoding an enemy's action cadence
  simulate_enemy_behavior() — project behavior over a given fight duration,
                               returning phase timings
  BehaviorSummary      — aggregated result of the simulation
"""

from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EnemyBehaviorProfile:
    """
    Parameterises how an enemy alternates between phases each cycle.

    attack_duration  — seconds enemy spends attacking per cycle
    move_duration    — seconds enemy spends repositioning per cycle
    stun_duration    — seconds enemy is stunned per cycle (0 = never stunned)
    is_stationary    — if True, enemy never enters the move phase

    One cycle = attack_duration + move_duration + stun_duration seconds.
    During attack phase the enemy is vulnerable and deals damage.
    During move/stun phases the enemy is still vulnerable but deals no damage.
    """
    attack_duration: float
    move_duration:   float
    stun_duration:   float = 0.0
    is_stationary:   bool  = False

    def __post_init__(self) -> None:
        if self.attack_duration < 0:
            raise ValueError(f"attack_duration must be >= 0, got {self.attack_duration}")
        if self.move_duration < 0:
            raise ValueError(f"move_duration must be >= 0, got {self.move_duration}")
        if self.stun_duration < 0:
            raise ValueError(f"stun_duration must be >= 0, got {self.stun_duration}")

    @property
    def cycle_duration(self) -> float:
        """Total seconds for one complete behavior cycle."""
        if self.is_stationary:
            return self.attack_duration + self.stun_duration
        return self.attack_duration + self.move_duration + self.stun_duration

    @property
    def attack_uptime(self) -> float:
        """Fraction of cycle time spent attacking (0.0–1.0)."""
        cycle = self.cycle_duration
        if cycle <= 0:
            return 0.0
        return self.attack_duration / cycle


# ---------------------------------------------------------------------------
# Simulation result
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BehaviorSummary:
    """
    Aggregated behavior timing over a simulated fight.

    total_duration  — total fight time in seconds (as requested)
    attack_time     — seconds enemy spends attacking
    move_time       — seconds enemy spends moving
    stun_time       — seconds enemy spends stunned
    attack_uptime   — fraction of total_duration spent attacking
    full_cycles     — number of complete behavior cycles
    partial_cycle   — remaining seconds in the last partial cycle
    """
    total_duration: float
    attack_time:    float
    move_time:      float
    stun_time:      float
    attack_uptime:  float
    full_cycles:    int
    partial_cycle:  float


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

def simulate_enemy_behavior(
    profile: EnemyBehaviorProfile,
    fight_duration: float,
) -> BehaviorSummary:
    """
    Project enemy behavior over ``fight_duration`` seconds.

    Phases within each cycle proceed in order: attack → move → stun.
    The last cycle may be partial.

    Raises ValueError if fight_duration < 0.
    """
    if fight_duration < 0:
        raise ValueError(f"fight_duration must be >= 0, got {fight_duration}")

    cycle = profile.cycle_duration
    if cycle <= 0:
        # Degenerate profile — enemy does nothing
        return BehaviorSummary(
            total_duration=fight_duration,
            attack_time=0.0,
            move_time=0.0,
            stun_time=0.0,
            attack_uptime=0.0,
            full_cycles=0,
            partial_cycle=fight_duration,
        )

    full_cycles = int(fight_duration / cycle)
    partial = fight_duration - full_cycles * cycle

    # Full cycles
    attack_time = full_cycles * profile.attack_duration
    move_time   = full_cycles * (0.0 if profile.is_stationary else profile.move_duration)
    stun_time   = full_cycles * profile.stun_duration

    # Partial cycle: phases fill in order — attack first, then move, then stun
    phases: list[tuple[str, float]] = [("attack", profile.attack_duration)]
    if not profile.is_stationary:
        phases.append(("move", profile.move_duration))
    phases.append(("stun", profile.stun_duration))

    remaining = partial
    for phase_name, phase_dur in phases:
        consumed = min(remaining, phase_dur)
        if phase_name == "attack":
            attack_time += consumed
        elif phase_name == "move":
            move_time += consumed
        elif phase_name == "stun":
            stun_time += consumed
        remaining -= consumed
        if remaining <= 0:
            break

    uptime = attack_time / fight_duration if fight_duration > 0 else 0.0

    return BehaviorSummary(
        total_duration=fight_duration,
        attack_time=attack_time,
        move_time=move_time,
        stun_time=stun_time,
        attack_uptime=uptime,
        full_cycles=full_cycles,
        partial_cycle=partial,
    )
