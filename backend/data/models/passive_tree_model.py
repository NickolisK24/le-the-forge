"""J7 — Passive Tree Node Model"""

from dataclasses import dataclass, field

__all__ = ["PassiveTreeModel"]


@dataclass(frozen=True)
class PassiveTreeModel:
    """
    Immutable representation of a passive tree node.

    Attributes
    ----------
    node_id:
        Unique node identifier.
    stat_modifiers:
        Dict mapping stat key → modifier value granted by this node.
    dependencies:
        Tuple of node IDs that must be allocated before this node can be taken.
    """

    node_id: str
    stat_modifiers: dict = field(default_factory=dict)
    dependencies: tuple = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id must not be empty")
        object.__setattr__(self, "stat_modifiers", dict(self.stat_modifiers))
        object.__setattr__(
            self, "dependencies", tuple(str(d) for d in self.dependencies)
        )

    def is_root(self) -> bool:
        """Return True if this node has no dependencies."""
        return len(self.dependencies) == 0

    def grants_stat(self, stat_key: str) -> bool:
        """Return True if this node modifies *stat_key*."""
        return stat_key in self.stat_modifiers

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "stat_modifiers": dict(self.stat_modifiers),
            "dependencies": list(self.dependencies),
        }
