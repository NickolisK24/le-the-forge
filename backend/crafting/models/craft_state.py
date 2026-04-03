from __future__ import annotations
from dataclasses import dataclass, field, asdict
import copy


@dataclass
class AffixState:
    affix_id: str
    current_tier: int
    max_tier: int
    locked: bool = False   # locked affixes can't be changed by runes


@dataclass
class CraftState:
    item_id: str
    item_name: str
    item_class: str           # "helm", "chest", "weapon", etc.
    forging_potential: int    # starts e.g. 50-100, decreases each craft
    instability: int          # starts 0, increases per craft
    affixes: list[AffixState] = field(default_factory=list)
    is_fractured: bool = False
    fracture_type: str | None = None   # "minor", "damaging", "destructive"
    craft_count: int = 0
    metadata: dict = field(default_factory=dict)

    def snapshot(self) -> dict:
        return asdict(self)

    def clone(self) -> CraftState:
        return copy.deepcopy(self)

    def serialize(self) -> dict:
        return self.snapshot()

    @classmethod
    def from_dict(cls, data: dict) -> CraftState:
        affixes = [AffixState(**a) for a in data.get("affixes", [])]
        return cls(
            item_id=data["item_id"],
            item_name=data["item_name"],
            item_class=data["item_class"],
            forging_potential=data["forging_potential"],
            instability=data["instability"],
            affixes=affixes,
            is_fractured=data.get("is_fractured", False),
            fracture_type=data.get("fracture_type"),
            craft_count=data.get("craft_count", 0),
            metadata=data.get("metadata", {}),
        )

    @property
    def affix_count(self) -> int:
        return len(self.affixes)

    @property
    def can_craft(self) -> bool:
        return not self.is_fractured and self.forging_potential > 0
