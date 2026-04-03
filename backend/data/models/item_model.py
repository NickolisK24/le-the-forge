"""J5 — Item Data Model"""

from dataclasses import dataclass, field

__all__ = ["ItemModel"]

_VALID_SLOTS = {
    "helm", "chest", "gloves", "boots", "belt", "ring", "amulet",
    "sword", "axe", "mace", "dagger", "sceptre", "wand", "staff",
    "bow", "spear", "shield", "quiver", "catalyst",
    "idol_small", "idol_large", "idol_grand", "idol_stout",
}


@dataclass(frozen=True)
class ItemModel:
    """
    Immutable representation of a base item definition.

    Attributes
    ----------
    item_id:
        Unique item identifier.
    slot_type:
        Equipment slot (e.g. ``"helm"``, ``"sword"``).
    implicit_stats:
        Dict mapping stat key → flat value for implicit modifiers.
    explicit_affixes:
        Ordered list of affix IDs that can appear on this item.
    """

    item_id: str
    slot_type: str
    implicit_stats: dict = field(default_factory=dict)
    explicit_affixes: tuple = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.item_id:
            raise ValueError("item_id must not be empty")
        if not self.slot_type:
            raise ValueError("slot_type must not be empty")
        if self.slot_type not in _VALID_SLOTS:
            raise ValueError(
                f"Invalid slot_type {self.slot_type!r}. Must be one of: {sorted(_VALID_SLOTS)}"
            )
        object.__setattr__(self, "implicit_stats", dict(self.implicit_stats))
        object.__setattr__(
            self, "explicit_affixes", tuple(str(a) for a in self.explicit_affixes)
        )

    def is_weapon(self) -> bool:
        return self.slot_type in {
            "sword", "axe", "mace", "dagger", "sceptre", "wand",
            "staff", "bow", "spear",
        }

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "slot_type": self.slot_type,
            "implicit_stats": dict(self.implicit_stats),
            "explicit_affixes": list(self.explicit_affixes),
        }
