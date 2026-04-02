"""
Conditional Trigger System (Step 55).

Allows effects to fire automatically when specific combat conditions are met.

  TriggerType    — the event that can fire a trigger (ON_CRIT, ON_HIT, etc.)
  TriggerEffect  — what happens when the trigger fires (APPLY_AILMENT, GAIN_BUFF)
  TriggerCondition — optional guard that must be true for the trigger to fire
  Trigger        — a complete trigger definition (type + condition + effect)
  TriggerContext — read-only snapshot of combat state passed to evaluation
  evaluate_triggers(triggers, context) — returns list of triggers that fired
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field


class TriggerType(enum.Enum):
    ON_HIT      = "on_hit"       # fires on every hit
    ON_CRIT     = "on_crit"      # fires only on critical strikes
    ON_KILL     = "on_kill"      # fires when an enemy dies
    ON_LOW_MANA = "on_low_mana"  # fires when current mana < threshold
    ON_CAST     = "on_cast"      # fires at the moment of skill activation


class TriggerEffect(enum.Enum):
    APPLY_BLEED     = "apply_bleed"
    APPLY_IGNITE    = "apply_ignite"
    APPLY_POISON    = "apply_poison"
    APPLY_SHOCK     = "apply_shock"
    GAIN_BUFF       = "gain_buff"
    RESTORE_MANA    = "restore_mana"


@dataclass(frozen=True)
class TriggerCondition:
    """
    An optional guard checked before a trigger fires.

    is_crit        — trigger only fires on a critical hit
    min_hit_damage — trigger only fires if the hit dealt at least this much damage
    mana_below_pct — trigger only fires if current mana < this % of max (0–100)
    chance_pct     — probability the trigger fires (0–100; 100 = always)
    """
    is_crit:        bool  = False
    min_hit_damage: float = 0.0
    mana_below_pct: float = 100.0   # 100 = no restriction
    chance_pct:     float = 100.0   # 100 = always fires when condition met


@dataclass(frozen=True)
class Trigger:
    """
    A complete trigger definition.

    trigger_type   — the event that can activate this trigger
    effect         — what happens when it fires
    condition      — additional guard (defaults: always fires)
    effect_value   — magnitude for the effect (e.g. mana restored, buff value)
    effect_duration — duration for buff/ailment effects in seconds
    source         — optional identifier for the skill/passive that owns this
    """
    trigger_type:    TriggerType
    effect:          TriggerEffect
    condition:       TriggerCondition = field(default_factory=TriggerCondition)
    effect_value:    float = 0.0
    effect_duration: float = 0.0
    source:          str   = ""


@dataclass(frozen=True)
class TriggerContext:
    """
    Read-only snapshot of the combat state at the moment of a combat event.

    is_crit        — whether the triggering hit was a critical strike
    hit_damage     — total damage dealt by the triggering hit (0 if not a hit event)
    current_mana   — current mana at the moment of evaluation
    max_mana       — maximum mana
    elapsed        — seconds elapsed in the fight
    """
    is_crit:      bool  = False
    hit_damage:   float = 0.0
    current_mana: float = 0.0
    max_mana:     float = 1.0    # > 0 to avoid division by zero
    elapsed:      float = 0.0

    @property
    def mana_pct(self) -> float:
        """Current mana as a percentage of max (0–100)."""
        return (self.current_mana / self.max_mana) * 100.0


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def _condition_met(trigger: Trigger, ctx: TriggerContext) -> bool:
    cond = trigger.condition

    # is_crit guard
    if cond.is_crit and not ctx.is_crit:
        return False

    # min_hit_damage guard
    if ctx.hit_damage < cond.min_hit_damage:
        return False

    # mana_below_pct guard (100.0 = no restriction — skip check entirely)
    if cond.mana_below_pct < 100.0 and ctx.mana_pct >= cond.mana_below_pct:
        return False

    return True


def _event_matches(trigger: Trigger, ctx: TriggerContext) -> bool:
    """Check that the trigger_type is appropriate for the context."""
    tt = trigger.trigger_type
    if tt is TriggerType.ON_CRIT and not ctx.is_crit:
        return False
    if tt is TriggerType.ON_LOW_MANA and ctx.mana_pct >= trigger.condition.mana_below_pct:
        return False
    return True


def evaluate_triggers(
    triggers: list[Trigger],
    context: TriggerContext,
    *,
    rng_roll: float | None = None,
) -> list[Trigger]:
    """
    Return the subset of ``triggers`` that fire given the current ``context``.

    For deterministic testing, pass ``rng_roll`` (0.0–100.0) to override
    the chance roll. When None, every trigger with chance_pct < 100 is
    treated as always firing (useful for unit tests; production code should
    pass a real roll).

    Order of checks per trigger:
      1. Event type matches context (e.g. ON_CRIT requires is_crit=True).
      2. Condition guards pass (is_crit, min_hit_damage, mana_below_pct).
      3. Chance roll succeeds.
    """
    fired: list[Trigger] = []

    for trigger in triggers:
        if not _event_matches(trigger, context):
            continue
        if not _condition_met(trigger, context):
            continue
        # Chance check
        roll = rng_roll if rng_roll is not None else 0.0
        if roll > trigger.condition.chance_pct:
            continue
        fired.append(trigger)

    return fired
