"""
Proc Chain System (Step 68).

Allows chained trigger effects — when a trigger fires, its output can
itself be a trigger event that evaluates another set of effects. This
models "on-hit → apply bleed → on-bleed-apply → gain buff" chains.

Design decisions:
  - Chains are depth-limited (MAX_CHAIN_DEPTH) to prevent infinite loops
  - Each link in a chain is a ProcLink: an event type + list of effects
  - Chains are resolved eagerly (depth-first) within a single call

  ProcEvent       — what event was raised (maps to TriggerType)
  ProcLink        — one node in the chain: event → effects list
  ProcChain       — ordered list of ProcLinks
  resolve_chain(chain, initial_event, context, rng_roll) -> list[ProcResult]
      Returns all effects that fired, with their depth.

Public API:
    MAX_CHAIN_DEPTH = 5
    ProcEvent
    ProcLink(event, effects, next_event=None)
    ProcResult(effect, depth)
    resolve_chain(chain, initial_event, context, *, rng_roll=None) -> list[ProcResult]
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field

from app.domain.triggers import (
    Trigger,
    TriggerContext,
    TriggerType,
    evaluate_triggers,
)

MAX_CHAIN_DEPTH: int = 5


class ProcEvent(enum.Enum):
    """Events that can trigger a proc chain link."""
    ON_HIT      = TriggerType.ON_HIT.value
    ON_CRIT     = TriggerType.ON_CRIT.value
    ON_KILL     = TriggerType.ON_KILL.value
    ON_CAST     = TriggerType.ON_CAST.value
    ON_LOW_MANA = TriggerType.ON_LOW_MANA.value
    ON_PROC     = "on_proc"   # fires when any previous link fires


@dataclass(frozen=True)
class ProcLink:
    """
    One node in a proc chain.

    event      — which event activates this link
    triggers   — Trigger objects evaluated when the event fires
    next_event — optional event raised when any trigger in this link fires,
                 used to continue the chain to the next link
    """
    event:      ProcEvent
    triggers:   tuple[Trigger, ...] = field(default_factory=tuple)
    next_event: ProcEvent | None = None


@dataclass(frozen=True)
class ProcResult:
    """One fired effect within a chain."""
    trigger: Trigger
    depth:   int


def resolve_chain(
    chain: list[ProcLink],
    initial_event: ProcEvent,
    context: TriggerContext,
    *,
    rng_roll: float | None = None,
) -> list[ProcResult]:
    """
    Resolve a proc chain starting from *initial_event*.

    Walks the chain depth-first:
    1. Find links whose .event matches the current event.
    2. Evaluate each matching link's triggers against *context*.
    3. If any trigger fires AND the link has a next_event, raise that event
       at depth+1 (up to MAX_CHAIN_DEPTH).

    Returns a flat list of ProcResult in the order they fired.
    Depth starts at 0 for the initial event.
    """
    results: list[ProcResult] = []
    _resolve(chain, initial_event, context, rng_roll, depth=0, results=results)
    return results


def _resolve(
    chain: list[ProcLink],
    event: ProcEvent,
    context: TriggerContext,
    rng_roll: float | None,
    depth: int,
    results: list[ProcResult],
) -> None:
    if depth > MAX_CHAIN_DEPTH:
        return

    for link in chain:
        if link.event is not event:
            continue

        # Build a TriggerType-compatible context by mapping ProcEvent → TriggerType
        trigger_type = _proc_event_to_trigger_type(event)
        matching_triggers = [
            t for t in link.triggers if t.trigger_type is trigger_type
        ] if trigger_type is not None else list(link.triggers)

        fired = evaluate_triggers(matching_triggers, context, rng_roll=rng_roll)

        for t in fired:
            results.append(ProcResult(trigger=t, depth=depth))

        # If any trigger fired and this link chains to another event, recurse
        if fired and link.next_event is not None:
            _resolve(chain, link.next_event, context, rng_roll, depth + 1, results)


def _proc_event_to_trigger_type(event: ProcEvent) -> TriggerType | None:
    """Map ProcEvent to TriggerType for evaluate_triggers compatibility."""
    mapping = {
        ProcEvent.ON_HIT:      TriggerType.ON_HIT,
        ProcEvent.ON_CRIT:     TriggerType.ON_CRIT,
        ProcEvent.ON_KILL:     TriggerType.ON_KILL,
        ProcEvent.ON_CAST:     TriggerType.ON_CAST,
        ProcEvent.ON_LOW_MANA: TriggerType.ON_LOW_MANA,
    }
    return mapping.get(event)
