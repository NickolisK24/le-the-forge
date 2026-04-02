"""
Damage Type Conversion System (Step 58).

Converts a portion of one damage type into another before resistance
calculations are applied. This mirrors the "X% of Physical converted to
Fire" mechanic found in Last Epoch.

  ConversionRule   — a single conversion: source → target at some percentage
  apply_conversions(damage_map, rules) → dict[DamageType, float]
      Pure function; transforms damage amounts and returns a new map.

Rules:
- Conversion is applied to the *original* source amount (not the already-
  converted remainder), so rule ordering does not matter.
- Total conversion out of any single source type is capped at 100%.
  If multiple rules convert the same source and their percentages sum
  above 100, each is scaled down proportionally.
- Converted damage is *added* to the target type; unconverted damage
  remains in the source type.
- Negative percentages are rejected (ValueError).
- Percentages above 100 per rule are clamped (treated as 100).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.calculators.damage_type_router import DamageType


@dataclass(frozen=True)
class ConversionRule:
    """
    Convert ``conversion_pct`` % of ``source`` damage into ``target`` damage.

    source         — damage type being converted away
    target         — damage type receiving the converted amount
    conversion_pct — percentage to convert (0–100)
    """
    source:         DamageType
    target:         DamageType
    conversion_pct: float

    def __post_init__(self) -> None:
        if self.conversion_pct < 0:
            raise ValueError(
                f"conversion_pct must be >= 0, got {self.conversion_pct}"
            )
        if self.source is self.target:
            raise ValueError(
                f"source and target must differ, got {self.source}"
            )


def apply_conversions(
    damage_map: dict[DamageType, float],
    rules: list[ConversionRule],
) -> dict[DamageType, float]:
    """
    Apply conversion rules to *damage_map* and return a new damage map.

    ``damage_map`` maps DamageType → raw damage amount (before resistance).
    Types not present in the map are treated as 0 damage.

    Conversion is computed from the *original* source amounts, so the
    order of rules does not affect the result. Total conversion from any
    one source is capped at 100% (rules scaled proportionally if needed).

    Returns a new dict; the input is not mutated.
    """
    result: dict[DamageType, float] = dict(damage_map)

    # Group rules by source type
    from collections import defaultdict
    rules_by_source: dict[DamageType, list[ConversionRule]] = defaultdict(list)
    for rule in rules:
        rules_by_source[rule.source].append(rule)

    for source, source_rules in rules_by_source.items():
        original_amount = damage_map.get(source, 0.0)
        if original_amount <= 0.0:
            continue

        # Cap each rule at 100%, then scale total if it exceeds 100%
        capped_pcts = [min(100.0, r.conversion_pct) for r in source_rules]
        total_pct = sum(capped_pcts)

        if total_pct > 100.0:
            # Scale down proportionally so total = 100%
            scale = 100.0 / total_pct
            capped_pcts = [p * scale for p in capped_pcts]
            total_pct = 100.0

        # Apply each conversion
        for rule, pct in zip(source_rules, capped_pcts):
            converted_amount = original_amount * (pct / 100.0)
            result[rule.source] = result.get(rule.source, 0.0) - converted_amount
            result[rule.target] = result.get(rule.target, 0.0) + converted_amount

    # Remove zero/negative entries to keep the map clean
    return {dt: amt for dt, amt in result.items() if amt > 0.0}
