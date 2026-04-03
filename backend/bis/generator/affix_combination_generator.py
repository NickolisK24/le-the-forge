from __future__ import annotations

from dataclasses import dataclass, field
import itertools


AVAILABLE_AFFIXES: list[str] = [
    "max_life",
    "flat_fire_damage",
    "crit_chance",
    "cast_speed",
    "resistances",
    "armour",
    "spell_damage",
    "attack_speed",
    "mana",
    "dodge_rating",
    "endurance",
    "ward",
]


@dataclass
class AffixCombo:
    affixes: list[str]  # list of affix_ids
    size: int


class AffixCombinationGenerator:
    def __init__(self, available: list[str] | None = None):
        self._available = available or AVAILABLE_AFFIXES

    def generate(
        self,
        n: int,
        required: list[str] | None = None,
        excluded: list[str] | None = None,
    ) -> list[AffixCombo]:
        # Generates all combinations of n affixes from available pool.
        # Mandatory affixes always included; fill remaining slots from pool.
        required = required or []
        excluded = set(excluded or [])
        pool = [a for a in self._available if a not in excluded and a not in required]
        remaining = n - len(required)
        if remaining < 0:
            return [AffixCombo(required[:n], n)]
        combos: list[AffixCombo] = []
        for extra in itertools.combinations(pool, max(0, remaining)):
            combos.append(AffixCombo(list(required) + list(extra), n))
        return combos

    def generate_with_sizes(
        self,
        min_n: int,
        max_n: int,
        required: list[str] | None = None,
    ) -> list[AffixCombo]:
        results: list[AffixCombo] = []
        for n in range(min_n, max_n + 1):
            results.extend(self.generate(n, required))
        return results
