"""
Gear Stat Integration (Step 89).

Merges gear-based affix stats from equipped items into the build stat pool.

Uses the existing Item / Affix model from app.domain.item.

  aggregate_gear(items) -> dict[str, float]
      Sums all affix values across all items. Identical stat_keys stack
      additively, matching the passive aggregator convention.

Rules:
- All affix values are accumulated additively per stat_key
- Sealed affixes are included (they are still active modifiers)
- Empty item lists or items with no affixes return an empty dict
- affix.value must be numeric; non-numeric values raise ValueError
"""

from __future__ import annotations

from app.domain.item import Affix, Item


def aggregate_gear(items: list[Item]) -> dict[str, float]:
    """
    Sum all affix values across *items* into a single flat stat dict.

    Affixes with identical stat_key values are accumulated additively.
    Returns an empty dict if *items* is empty or no affixes are present.

    Example:
        items = [
            Item(slot="amulet", ..., affixes=[
                Affix(name="Fire Damage", stat_key="fire_damage_pct", value=12.0),
                Affix(name="Crit Chance", stat_key="crit_chance_pct",  value=5.0),
            ]),
            Item(slot="ring", ..., affixes=[
                Affix(name="Fire Damage", stat_key="fire_damage_pct", value=8.0),
            ]),
        ]
        aggregate_gear(items)
        # -> {"fire_damage_pct": 20.0, "crit_chance_pct": 5.0}
    """
    totals: dict[str, float] = {}
    for item in items:
        for affix in item.affixes:
            if not isinstance(affix.value, (int, float)):
                raise ValueError(
                    f"Item '{item.slot}' affix '{affix.stat_key}': "
                    f"value must be numeric, got {type(affix.value)}"
                )
            totals[affix.stat_key] = totals.get(affix.stat_key, 0.0) + affix.value
    return totals
