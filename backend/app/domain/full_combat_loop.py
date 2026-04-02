"""
Full Combat Loop Stabilization (Step 60).

Integrates all combat systems from Steps 51–59 into a single cohesive
simulation loop:

  Step 51 — Ailment damage scaling        (scale_ailment_damage)
  Step 52 — Skill cooldowns               (CooldownManager)
  Step 53 — Speed scaling                 (effective_cast_interval)
  Step 54 — Mana resource                 (ManaPool)
  Step 55 — Conditional triggers          (evaluate_triggers)
  Step 56 — Buff duration scaling         (apply_buff_duration)
  Step 57 — Multi-skill rotation          (RotationEngine)
  Step 58 — Damage type conversion        (apply_conversions)
  Step 59 — Ailment duration scaling      (scale_ailment_duration)

Public API:
  SkillSpec         — full description of a skill in the simulation
  SimConfig         — configuration for a full combat simulation
  SimResult         — output: damage, DPS, mana/cooldown histories
  FullCombatLoop    — the simulator class; call run() for a full fight
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.ailment_duration_scaling import scale_ailment_duration
from app.domain.ailment_scaling import scale_ailment_damage
from app.domain.ailments import AilmentInstance, AilmentType, tick_ailments
from app.domain.ailment_stacking import apply_ailment_with_limit
from app.domain.buff_duration_scaling import apply_buff_duration
from app.domain.calculators.damage_type_router import DamageType
from app.domain.cooldown import CooldownManager
from app.domain.damage_conversion import ConversionRule, apply_conversions
from app.domain.mana import ManaPool
from app.domain.rotation import RotationEngine, SkillEntry
from app.domain.speed_scaling import effective_cast_interval
from app.domain.timeline import BuffInstance, BuffType, TimelineEngine
from app.domain.triggers import (
    Trigger,
    TriggerContext,
    TriggerEffect,
    evaluate_triggers,
)


# ---------------------------------------------------------------------------
# Configuration types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SkillSpec:
    """
    Full description of one skill in the rotation.

    name             — unique skill identifier
    mana_cost        — mana per cast
    cooldown         — base cooldown (seconds)
    priority         — rotation priority (lower = higher priority)
    base_damage      — direct hit damage before stats
    cast_speed_pct   — cast speed bonus for this skill
    ailment_type     — ailment applied on hit (or None)
    ailment_base_dmg — ailment damage per tick
    ailment_duration — base ailment duration in seconds
    on_hit_triggers  — list of Trigger objects that can fire on hit
    """
    name:             str
    mana_cost:        float         = 0.0
    cooldown:         float         = 0.0
    priority:         int           = 1
    base_damage:      float         = 0.0
    cast_speed_pct:   float         = 0.0
    ailment_type:     AilmentType | None = None
    ailment_base_dmg: float         = 0.0
    ailment_duration: float         = 0.0
    on_hit_triggers:  tuple[Trigger, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SimConfig:
    """
    Configuration for a full combat simulation.

    tick_size           — simulation time step (seconds)
    fight_duration      — total simulated fight length (seconds)
    max_mana            — starting / maximum mana
    mana_regen_rate     — mana per second regenerated
    ailment_damage_pct  — increased damage for all ailments (additive %)
    ailment_duration_pct— increased duration for all ailments (additive %)
    buff_duration_pct   — increased duration for all buffs (additive %)
    conversion_rules    — list of DamageType conversion rules
    skills              — ordered list of SkillSpec definitions
    """
    tick_size:            float = 0.1
    fight_duration:       float = 30.0
    max_mana:             float = 200.0
    mana_regen_rate:      float = 10.0
    ailment_damage_pct:   float = 0.0
    ailment_duration_pct: float = 0.0
    buff_duration_pct:    float = 0.0
    conversion_rules:     tuple[ConversionRule, ...] = field(default_factory=tuple)
    skills:               tuple[SkillSpec, ...] = field(default_factory=tuple)


@dataclass
class SimResult:
    """
    Output of a full combat simulation.

    total_damage        — total damage dealt (hit + ailments)
    fight_duration      — actual elapsed time simulated
    average_dps         — total_damage / fight_duration
    ticks_simulated     — total tick count
    mana_floor          — minimum mana observed during the fight (>= 0)
    cooldown_floor      — minimum cooldown_remaining observed across all skills
    hit_damage_total    — total direct hit damage
    ailment_damage_total— total ailment (DoT) damage
    casts_per_skill     — number of times each skill was cast
    """
    total_damage:         float
    fight_duration:       float
    average_dps:          float
    ticks_simulated:      int
    mana_floor:           float
    cooldown_floor:       float
    hit_damage_total:     float
    ailment_damage_total: float
    casts_per_skill:      dict[str, int]


# ---------------------------------------------------------------------------
# Simulator
# ---------------------------------------------------------------------------

class FullCombatLoop:
    """
    Tick-based simulator integrating all Step 51–59 subsystems.

    Tick ordering (COMPUTE FIRST — see combat_timeline.py docstring):
      1. Regenerate mana.
      2. Select skill via RotationEngine; cast if ready.
         a. Spend mana (skipped if unaffordable — engine handles fallback).
         b. Trigger cooldown.
         c. Apply damage conversions to hit.
         d. Evaluate on_hit triggers; apply resulting ailments/buffs.
      3. Tick active ailments; accumulate scaled DoT damage.
      4. Tick buff timeline.
    """

    def __init__(self, config: SimConfig) -> None:
        self._cfg = config
        self._tick_size = config.tick_size

        # Subsystem initialisation
        self._mana = ManaPool(
            max_mana=config.max_mana,
            current_mana=config.max_mana,
            mana_regeneration_rate=config.mana_regen_rate,
        )
        self._rotation  = RotationEngine()
        self._cooldowns = CooldownManager()
        self._buffs     = TimelineEngine()
        self._ailments: list[AilmentInstance] = []

        # Register skills
        for spec in config.skills:
            self._rotation.add(SkillEntry(
                name=spec.name,
                mana_cost=spec.mana_cost,
                cooldown=spec.cooldown,
                priority=spec.priority,
            ))
            self._cooldowns.register(spec.name, spec.cooldown)

        # Skill spec lookup
        self._specs: dict[str, SkillSpec] = {s.name: s for s in config.skills}

        # Metrics
        self._total_damage     = 0.0
        self._hit_damage       = 0.0
        self._ailment_damage   = 0.0
        self._ticks            = 0
        self._elapsed          = 0.0
        self._mana_floor       = config.max_mana
        self._cd_floor         = 0.0
        self._casts: dict[str, int] = {s.name: 0 for s in config.skills}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _cast_skill(self, spec: SkillSpec) -> None:
        """Execute one cast of *spec*."""
        self._mana.spend(spec.mana_cost)
        # Start cooldown in both trackers so they stay in sync
        self._cooldowns.trigger(spec.name)
        self._rotation.trigger(spec.name)

        # Compute hit damage with conversion
        if spec.base_damage > 0:
            raw_map: dict[DamageType, float] = {DamageType.PHYSICAL: spec.base_damage}
            converted = apply_conversions(raw_map, list(self._cfg.conversion_rules))
            hit_dmg = sum(converted.values())
            # Apply DAMAGE_MULTIPLIER buff
            bonus = self._buffs.total_modifier(BuffType.DAMAGE_MULTIPLIER)
            hit_dmg *= 1.0 + bonus / 100.0
            self._hit_damage    += hit_dmg
            self._total_damage  += hit_dmg

        # Apply ailment if configured
        if spec.ailment_type is not None and spec.ailment_base_dmg > 0:
            # Scale ailment damage by stats
            from app.engines.stat_engine import BuildStats  # local import
            stats = BuildStats(ailment_damage_pct=self._cfg.ailment_damage_pct)
            scaled_dmg = scale_ailment_damage(
                spec.ailment_base_dmg, spec.ailment_type, stats
            )
            scaled_dur = scale_ailment_duration(
                spec.ailment_duration, self._cfg.ailment_duration_pct
            )
            self._ailments = apply_ailment_with_limit(
                self._ailments,
                spec.ailment_type,
                scaled_dmg,
                scaled_dur,
            )

        # Evaluate on-hit triggers
        ctx = TriggerContext(
            is_crit=False,
            hit_damage=spec.base_damage,
            current_mana=self._mana.current_mana,
            max_mana=self._mana.max_mana,
        )
        fired = evaluate_triggers(list(spec.on_hit_triggers), ctx)
        for trigger in fired:
            self._handle_trigger(trigger)

        self._casts[spec.name] += 1

    def _handle_trigger(self, trigger: Trigger) -> None:
        """Apply a fired trigger's effect."""
        if trigger.effect is TriggerEffect.RESTORE_MANA:
            restored = min(
                trigger.effect_value,
                self._mana.max_mana - self._mana.current_mana,
            )
            self._mana.current_mana += restored
        elif trigger.effect is TriggerEffect.GAIN_BUFF:
            raw_buff = BuffInstance(
                buff_type=BuffType.DAMAGE_MULTIPLIER,
                value=trigger.effect_value,
                duration=trigger.effect_duration,
                source=trigger.source,
            )
            scaled_buff = apply_buff_duration(raw_buff, self._cfg.buff_duration_pct)
            self._buffs.add_buff(scaled_buff)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> SimResult:
        """Run the full simulation and return a SimResult."""
        remaining = self._cfg.fight_duration

        while remaining > 0.0:
            actual_tick = min(self._tick_size, remaining)

            # 1. Regenerate mana
            self._mana.regenerate(actual_tick)
            self._mana_floor = min(self._mana_floor, self._mana.current_mana)

            # 2. Skill rotation — advance cooldown timers then select
            self._rotation.tick(actual_tick)
            self._cooldowns.tick(actual_tick)

            # Track cooldown floor
            for cd_val in self._rotation.cooldowns.values():
                self._cd_floor = min(self._cd_floor, cd_val)

            skill_entry = self._rotation.next_skill(self._mana.current_mana)
            if skill_entry is not None:
                spec = self._specs[skill_entry.name]
                self._cast_skill(spec)

            # 3. Tick ailments — scaled DoT damage
            remaining_ailments, _ = tick_ailments(self._ailments, actual_tick)
            for inst in self._ailments:
                from app.engines.stat_engine import BuildStats  # local import
                stats = BuildStats(ailment_damage_pct=self._cfg.ailment_damage_pct)
                raw_dot = inst.damage_per_tick * actual_tick
                # scale_ailment_damage scales by stat multiplier on the *rate*
                # but ailment_scaling expects base_damage not per-tick-rate,
                # so we compute the multiplier directly
                increased = self._cfg.ailment_damage_pct
                dot_dmg = raw_dot * (1.0 + increased / 100.0)
                # Apply DAMAGE_MULTIPLIER buff on top
                bonus = self._buffs.total_modifier(BuffType.DAMAGE_MULTIPLIER)
                dot_dmg *= 1.0 + bonus / 100.0
                self._ailment_damage  += dot_dmg
                self._total_damage    += dot_dmg
            self._ailments = remaining_ailments

            # 4. Advance buff timeline
            self._buffs.tick(actual_tick)

            self._elapsed += actual_tick
            self._ticks   += 1
            remaining     -= actual_tick

        duration = self._elapsed
        avg_dps = self._total_damage / duration if duration > 0 else 0.0
        return SimResult(
            total_damage=self._total_damage,
            fight_duration=duration,
            average_dps=avg_dps,
            ticks_simulated=self._ticks,
            mana_floor=self._mana_floor,
            cooldown_floor=self._cd_floor,
            hit_damage_total=self._hit_damage,
            ailment_damage_total=self._ailment_damage,
            casts_per_skill=dict(self._casts),
        )
