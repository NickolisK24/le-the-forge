"""
Conditional Stat Phase — Layer 8 of the stat resolution pipeline.

Evaluates ConditionalModifiers against a RuntimeContext and applies
their stat deltas to the already-resolved BuildStats.

This layer runs AFTER all base stat math (layers 1–7) so that
conditional bonuses stack on top of the fully resolved character sheet.

Architecture:
  - Reuses existing ConditionalModifierEngine for evaluation
  - RuntimeContext bridges build-planning flags to SimulationState
  - Stat deltas from the engine are applied directly to BuildStats
  - Debug snapshots record each condition check and its outcome
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.engines.stat_engine import BuildStats
from app.stats.runtime_context import RuntimeContext, DEFAULT_CONTEXT
from app.utils.logging import ForgeLogger
from conditions.models.condition import Condition
from modifiers.models.conditional_modifier import ConditionalModifier
from modifiers.conditional_modifier_engine import ConditionalModifierEngine

log = ForgeLogger(__name__)


# ---------------------------------------------------------------------------
# Debug snapshot
# ---------------------------------------------------------------------------

@dataclass
class ConditionalStatSnapshot:
    """Debug record for Layer 8 conditional stat evaluation."""
    context: dict
    evaluated: list[dict] = field(default_factory=list)
    active_ids: list[str] = field(default_factory=list)
    stat_deltas: dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Core evaluation
# ---------------------------------------------------------------------------

_ENGINE = ConditionalModifierEngine()


def apply_conditional_stats(
    stats: BuildStats,
    modifiers: list[ConditionalModifier],
    context: RuntimeContext | None = None,
    capture: bool = False,
) -> Optional[ConditionalStatSnapshot]:
    """Evaluate conditional modifiers and apply active deltas to *stats*.

    Args:
        stats: Fully resolved BuildStats (after layers 1–7).
        modifiers: List of ConditionalModifiers to evaluate.
        context: RuntimeContext describing assumed conditions.
                 Defaults to DEFAULT_CONTEXT (no conditions active).
        capture: If True, return a debug snapshot.

    Returns:
        ConditionalStatSnapshot if capture=True, else None.
    """
    if not modifiers:
        log.debug("conditional_stats.skip", reason="no modifiers")
        return ConditionalStatSnapshot(context={}) if capture else None

    ctx = context or DEFAULT_CONTEXT
    sim_state = ctx.to_simulation_state(
        max_health=max(stats.max_health, 1.0),
    )

    log.debug(
        "conditional_stats.start",
        n_modifiers=len(modifiers),
        n_buffs=len(sim_state.active_buffs),
        n_statuses=len(sim_state.active_status_effects),
    )

    # Evaluate which modifiers are active
    active = _ENGINE.active_modifiers(modifiers, sim_state)
    # Compute aggregated stat deltas
    deltas = _ENGINE.evaluate(modifiers, sim_state)

    log.debug(
        "conditional_stats.evaluated",
        n_active=len(active),
        n_deltas=len(deltas),
    )

    # Apply deltas to BuildStats
    for stat_key, delta in deltas.items():
        if hasattr(stats, stat_key):
            current = getattr(stats, stat_key)
            setattr(stats, stat_key, current + delta)
            log.debug(
                "conditional_stats.apply",
                stat=stat_key,
                delta=delta,
                new_value=current + delta,
            )
        else:
            log.debug(
                "conditional_stats.skip_field",
                stat=stat_key,
                reason="not a BuildStats field",
            )

    log.debug("conditional_stats.done", n_applied=len(deltas))

    if capture:
        snapshot = ConditionalStatSnapshot(
            context=ctx.to_dict(),
            evaluated=[
                {
                    "modifier_id": m.modifier_id,
                    "stat_target": m.stat_target,
                    "value": m.value,
                    "modifier_type": m.modifier_type,
                    "condition_id": m.condition.condition_id,
                    "active": m in active,
                }
                for m in modifiers
            ],
            active_ids=[m.modifier_id for m in active],
            stat_deltas=dict(deltas),
        )
        return snapshot

    return None


# ---------------------------------------------------------------------------
# Convenience builders for common conditional modifiers
# ---------------------------------------------------------------------------

def moving_bonus(stat_key: str, value: float, modifier_id: str = "") -> ConditionalModifier:
    """Create a modifier that activates while moving."""
    return ConditionalModifier(
        modifier_id=modifier_id or f"moving_{stat_key}",
        stat_target=stat_key,
        value=value,
        modifier_type="additive",
        condition=Condition(
            condition_id="is_moving",
            condition_type="buff_active",
        ),
    )


def ward_bonus(stat_key: str, value: float, modifier_id: str = "") -> ConditionalModifier:
    """Create a modifier that activates while player has ward."""
    return ConditionalModifier(
        modifier_id=modifier_id or f"ward_{stat_key}",
        stat_target=stat_key,
        value=value,
        modifier_type="additive",
        condition=Condition(
            condition_id="has_ward",
            condition_type="buff_active",
        ),
    )


def frozen_enemy_bonus(stat_key: str, value: float, modifier_id: str = "") -> ConditionalModifier:
    """Create a modifier that activates when enemy is frozen."""
    return ConditionalModifier(
        modifier_id=modifier_id or f"frozen_{stat_key}",
        stat_target=stat_key,
        value=value,
        modifier_type="additive",
        condition=Condition(
            condition_id="frozen",
            condition_type="status_present",
        ),
    )


def boss_bonus(stat_key: str, value: float, modifier_id: str = "") -> ConditionalModifier:
    """Create a modifier that activates against bosses."""
    return ConditionalModifier(
        modifier_id=modifier_id or f"boss_{stat_key}",
        stat_target=stat_key,
        value=value,
        modifier_type="additive",
        condition=Condition(
            condition_id="against_boss",
            condition_type="buff_active",
        ),
    )


def low_health_bonus(
    stat_key: str,
    value: float,
    threshold: float = 0.35,
    modifier_id: str = "",
) -> ConditionalModifier:
    """Create a modifier that activates when player health is below threshold."""
    return ConditionalModifier(
        modifier_id=modifier_id or f"low_hp_{stat_key}",
        stat_target=stat_key,
        value=value,
        modifier_type="additive",
        condition=Condition(
            condition_id="low_health",
            condition_type="player_health_pct",
            threshold_value=threshold,
            comparison_operator="le",
        ),
    )
