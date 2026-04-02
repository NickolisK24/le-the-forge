"""
Conversion Calculator — percentage-based damage type conversion pipeline.

Conversion rules (Last Epoch):
- A conversion moves X% of a source type's base damage to a target type.
- Converted damage is fully the new type: it loses source bonuses and gains
  target bonuses when increased-damage routing runs.
- Multiple conversions from the same source are additive; their total is
  capped at 100%. If the sum exceeds 100%, each is scaled proportionally so
  the source is never over-converted.
- Conversion runs on the scaled base dict (output of scale_skill_damage)
  before increased damage is applied.
- No chained conversion: A→B then B→C is not re-applied. B stays B.
- Self-conversions (source == target) and zero-percent entries are ignored.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Sequence

from app.domain.calculators.damage_type_router import DamageType


@dataclass(frozen=True)
class DamageConversion:
    """A single percentage-based conversion from one damage type to another."""

    source: DamageType
    target: DamageType
    pct: float  # 0.0–100.0


def apply_conversions(
    scaled: dict[DamageType, float],
    conversions: Sequence[DamageConversion],
) -> dict[DamageType, float]:
    """
    Apply percentage-based damage conversions to a scaled damage dict.

    Algorithm:
    1. Group conversions by source type.
    2. For each source, sum all outgoing pct values.
    3. If total > 100%, scale each entry down proportionally (sum becomes 100%).
    4. Move the converted amounts from source to each target.

    Returns a new dict; ``scaled`` is not modified.
    Types whose value reaches zero after conversion are omitted from the result.
    """
    if not conversions:
        return dict(scaled)

    result = dict(scaled)

    # Group valid conversions by source
    from_source: dict[DamageType, list[tuple[DamageType, float]]] = defaultdict(list)
    for conv in conversions:
        if conv.source != conv.target and conv.pct > 0:
            from_source[conv.source].append((conv.target, conv.pct))

    for source, targets in from_source.items():
        if source not in result:
            continue
        source_amount = result[source]
        if source_amount <= 0:
            continue

        total_pct = sum(p for _, p in targets)
        if total_pct > 100.0:
            # Scale proportionally so no source is over-converted
            factor = 100.0 / total_pct
            targets = [(t, p * factor) for t, p in targets]

        for target, pct in targets:
            amount = source_amount * pct / 100.0
            result[source] -= amount
            result[target] = result.get(target, 0.0) + amount

    # Drop exhausted entries (also catches any float underflow negatives)
    return {dt: v for dt, v in result.items() if v > 0}
