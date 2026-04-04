"""
Passive Stat Aggregation (Step 88).

Aggregates passive tree nodes into a unified stat dictionary consumed by
the build assembly layer.

  PassiveNode          — a single node on the passive tree with a stat dict
  aggregate_passives   — sums all node stats into one flat totals dict

Rules:
- Stats with identical keys are summed (additive stacking)
- Negative stat values are accepted (represent penalties)
- Empty node lists return an empty dict
- Node stat values must be numeric (float/int)
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PassiveNode:
    """
    A single passive tree node.

    node_id  — unique identifier for the node
    name     — human-readable label
    stats    — mapping of stat_key -> value (e.g. {"fire_damage_pct": 10.0})
    """
    node_id: str
    name:    str
    stats:   dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Ensure stats values are numeric
        for key, val in self.stats.items():
            if not isinstance(val, (int, float)):
                raise ValueError(
                    f"PassiveNode '{self.node_id}': stat '{key}' must be numeric, got {type(val)}"
                )

    def __hash__(self) -> int:
        return hash(self.node_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PassiveNode):
            return NotImplemented
        return self.node_id == other.node_id


def aggregate_passives(nodes: list[PassiveNode]) -> dict[str, float]:
    """
    Sum all stat values across passive nodes into a single flat dict.

    Identical stat keys are added together (additive stacking).
    Returns an empty dict if *nodes* is empty.

    Example:
        nodes = [
            PassiveNode("n1", "Fire Mastery", {"fire_damage_pct": 10.0}),
            PassiveNode("n2", "Spell Power",  {"fire_damage_pct": 5.0, "spell_damage_pct": 8.0}),
        ]
        aggregate_passives(nodes)
        # -> {"fire_damage_pct": 15.0, "spell_damage_pct": 8.0}
    """
    totals: dict[str, float] = {}
    for node in nodes:
        for stat, value in node.stats.items():
            totals[stat] = totals.get(stat, 0.0) + value
    return totals
