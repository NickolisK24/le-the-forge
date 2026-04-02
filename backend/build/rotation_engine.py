"""
Multi-Skill Rotation Modeling (Step 93).

Simulates real gameplay rotations at the build layer. Takes a prioritized
list of skills and a fight duration, then produces a timeline of casts and
per-skill execution statistics.

  RotationSkill   — a skill entry with cooldown, mana cost, and priority
  CastEvent       — a recorded cast: which skill fired at what time
  RotationResult  — simulation output: cast timeline and aggregated stats
  BuildRotation   — engine that simulates the full rotation timeline

Scheduling rules (same as FullCombatLoop rotation logic):
  - Skills fire in priority order (lower number = higher priority)
  - A skill is ready when cooldown_remaining <= 0 and mana >= cost
  - After casting, cooldown_remaining is reset to skill.cooldown
  - Mana regenerates at mana_regen_rate per second each tick
  - Mana is floored at 0 and capped at max_mana
  - Tick size defaults to 0.05s for fine-grained rotation accuracy
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RotationSkill:
    """
    A skill slot in the build rotation.

    name       — unique skill identifier
    cooldown   — seconds between casts (0 = spam)
    mana_cost  — mana required per cast
    priority   — lower number = higher priority (1 is highest)
    base_damage — damage per cast (before build scaling)
    """
    name:        str
    cooldown:    float = 0.0
    mana_cost:   float = 0.0
    priority:    int   = 1
    base_damage: float = 0.0

    def __post_init__(self) -> None:
        if self.cooldown < 0:
            raise ValueError(f"RotationSkill '{self.name}': cooldown must be >= 0")
        if self.mana_cost < 0:
            raise ValueError(f"RotationSkill '{self.name}': mana_cost must be >= 0")
        if self.priority < 1:
            raise ValueError(f"RotationSkill '{self.name}': priority must be >= 1")


@dataclass
class CastEvent:
    """A single skill cast recorded in the rotation timeline."""
    time:       float   # simulation time of cast (seconds)
    skill_name: str
    damage:     float   # damage dealt by this cast


@dataclass
class RotationResult:
    """
    Output of a BuildRotation simulation.

    timeline         — ordered list of CastEvents
    casts_per_skill  — {skill_name: cast_count}
    damage_per_skill — {skill_name: total_damage}
    total_damage     — sum of all hit damage
    total_casts      — total number of casts
    fight_duration   — actual simulated duration (seconds)
    mana_floor       — minimum mana observed (>= 0)
    """
    timeline:         list[CastEvent]
    casts_per_skill:  dict[str, int]
    damage_per_skill: dict[str, float]
    total_damage:     float
    total_casts:      int
    fight_duration:   float
    mana_floor:       float


class BuildRotation:
    """
    Tick-based rotation simulator.

    Simulates the cast schedule for a prioritized skill list over a fight
    duration, tracking cooldowns and mana.

    Usage:
        engine = BuildRotation(skills, fight_duration=60.0, max_mana=200.0,
                               mana_regen_rate=20.0)
        result = engine.run()
    """

    def __init__(
        self,
        skills:           list[RotationSkill],
        fight_duration:   float = 30.0,
        max_mana:         float = 200.0,
        mana_regen_rate:  float = 10.0,
        tick_size:        float = 0.05,
    ) -> None:
        if not skills:
            raise ValueError("BuildRotation requires at least one skill")
        if fight_duration <= 0:
            raise ValueError("fight_duration must be > 0")
        if tick_size <= 0:
            raise ValueError("tick_size must be > 0")

        # Sort once by priority (stable: ties keep list order)
        self._skills        = sorted(skills, key=lambda s: s.priority)
        self._duration      = fight_duration
        self._max_mana      = max_mana
        self._regen_rate    = mana_regen_rate
        self._tick          = tick_size

    def run(self) -> RotationResult:
        """Simulate the rotation and return a RotationResult."""
        mana       = self._max_mana
        mana_floor = mana
        time       = 0.0
        cooldowns  = {s.name: 0.0 for s in self._skills}

        timeline:         list[CastEvent]       = []
        casts_per_skill:  dict[str, int]        = {s.name: 0 for s in self._skills}
        damage_per_skill: dict[str, float]      = {s.name: 0.0 for s in self._skills}

        while time < self._duration:
            # 1. Regenerate mana
            mana = min(self._max_mana, mana + self._regen_rate * self._tick)

            # 2. Select and cast the highest-priority ready skill
            for skill in self._skills:
                if cooldowns[skill.name] <= 0.0 and mana >= skill.mana_cost:
                    mana -= skill.mana_cost
                    cooldowns[skill.name] = skill.cooldown
                    timeline.append(CastEvent(
                        time=round(time, 10),
                        skill_name=skill.name,
                        damage=skill.base_damage,
                    ))
                    casts_per_skill[skill.name]  += 1
                    damage_per_skill[skill.name] += skill.base_damage
                    break   # only one cast per tick

            # 3. Track mana floor
            mana_floor = min(mana_floor, mana)

            # 4. Tick cooldowns
            for name in cooldowns:
                if cooldowns[name] > 0.0:
                    cooldowns[name] = max(0.0, cooldowns[name] - self._tick)

            time += self._tick

        total_damage = sum(damage_per_skill.values())
        total_casts  = sum(casts_per_skill.values())

        return RotationResult(
            timeline=timeline,
            casts_per_skill=casts_per_skill,
            damage_per_skill=damage_per_skill,
            total_damage=total_damage,
            total_casts=total_casts,
            fight_duration=self._duration,
            mana_floor=max(0.0, mana_floor),
        )
