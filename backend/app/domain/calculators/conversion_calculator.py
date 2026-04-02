"""
Conversion Calculator — percentage-based damage type conversion pipeline.

Conversion rules (Last Epoch):
- A conversion moves X% of a source type's base damage to a target type.
- Converted damage is fully the new type: it loses source bonuses and gains
  target bonuses when increased-damage routing runs.
- Multiple conversions from the same source and the same priority tier are
  additive; their total is capped at 100%. If the sum exceeds 100%, each is
  scaled proportionally so the source is never over-converted.
- Conversion runs on the scaled base dict (output of scale_skill_damage)
  before increased damage is applied.

Priority ordering:
- Each DamageConversion carries an integer priority (default 0).
  Higher value = runs first.
- apply_conversions processes tiers from highest priority to lowest.
  Each tier sees the full output of all earlier (higher-priority) tiers.
- This makes chaining explicit and deterministic:
    phys→fire (priority=1), fire→cold (priority=0)
    → 100 phys becomes 100 fire (tier 1), then 100 fire becomes 100 cold (tier 0)
- Conversions within the same priority tier and the same source are grouped
  and capped together. Ordering between different source types in the same
  tier is unspecified — avoid same-tier chains.

Other rules:
- Self-conversions (source == target) are ignored.
- Zero-percent entries are ignored.
- Types whose value reaches zero are omitted from the result.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Sequence

from app.domain.calculators.damage_type_router import DamageType


@dataclass(frozen=True)
class DamageConversion:
    """A single percentage-based conversion from one damage type to another."""

    source: DamageType
    target: DamageType
    pct: float       # 0.0–100.0
    priority: int = 0  # Higher value runs first; controls chaining order


def apply_conversions(
    scaled: dict[DamageType, float],
    conversions: Sequence[DamageConversion],
) -> dict[DamageType, float]:
    """
    Apply percentage-based damage conversions to a scaled damage dict.

    Algorithm:
    1. Filter out self-conversions and zero-pct entries.
    2. Collect all unique priority values; sort descending (highest first).
    3. For each priority tier:
       a. Group conversions by source type.
       b. For each source, sum all outgoing pct values.
       c. If total > 100%, scale each down proportionally (sum → 100%).
       d. Move converted amounts from source to each target.
       Each tier mutates the running result so the next tier sees the output.
    4. Return the final result, omitting types with zero remaining damage.

    ``scaled`` is not modified; a new dict is returned.
    """
    if not conversions:
        return dict(scaled)

    valid = [c for c in conversions if c.source != c.target and c.pct > 0]
    if not valid:
        return dict(scaled)

    result = dict(scaled)

    # Process tiers from highest priority to lowest
    for priority in sorted({c.priority for c in valid}, reverse=True):
        tier = [c for c in valid if c.priority == priority]

        # Group by source within this tier
        from_source: dict[DamageType, list[tuple[DamageType, float]]] = defaultdict(list)
        for conv in tier:
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

            # Compute all amounts first, then subtract the total once.
            # A single subtraction preserves the remainder more accurately
            # than N accumulated subtractions when pct is a repeating fraction.
            amounts = [(target, source_amount * pct / 100.0) for target, pct in targets]
            total_converted = sum(a for _, a in amounts)
            result[source] -= total_converted
            for target, amount in amounts:
                result[target] = result.get(target, 0.0) + amount

    # 1e-12 tolerance: drop fully-converted types and float underflow negatives
    # without discarding legitimate fractional remainders near (but above) zero.
    return {dt: v for dt, v in result.items() if v > 1e-12}
