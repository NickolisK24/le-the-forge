"""
E6 — Passive System

Manages passive node allocation for a build.
Tracks dependency chains and prevents circular allocations.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class PassiveNode:
    """
    A passive tree node with optional dependency requirements.

    dependencies: list of node_ids that must be allocated first.
    node_type: "minor" | "notable" | "keystone"
    """
    node_id:      int
    name:         str  = ""
    node_type:    str  = "minor"
    dependencies: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Compatible with stat_engine.aggregate_stats nodes format."""
        return {"id": self.node_id, "type": self.node_type, "name": self.name}

    @classmethod
    def from_dict(cls, d: dict) -> "PassiveNode":
        return cls(
            node_id=d["id"],
            name=d.get("name", ""),
            node_type=d.get("type", "minor"),
            dependencies=d.get("dependencies", []),
        )


class PassiveSystem:
    """
    Tracks which passive nodes are allocated in a build.

    Dependency validation prevents allocating a node whose prerequisite
    nodes are not yet allocated.  Circular dependency detection prevents
    infinite loops in the dependency graph.
    """

    def __init__(self, nodes: list[PassiveNode] | None = None) -> None:
        # Registry of all known nodes by id
        self._registry: dict[int, PassiveNode] = {}
        self._allocated: set[int] = set()
        for n in (nodes or []):
            self._registry[n.node_id] = n

    def register(self, node: PassiveNode) -> None:
        """Add a node to the registry without allocating it."""
        # Temporarily include the incoming node so the cycle check can see it
        candidate_reg = {**self._registry, node.node_id: node}
        if self._has_circular_dependency(node.node_id, node.dependencies, set(), candidate_reg):
            raise ValueError(
                f"Circular dependency detected for node {node.node_id}"
            )
        self._registry[node.node_id] = node

    def allocate(self, node_id: int) -> None:
        """Allocate a node, raising if its dependencies are not met."""
        node = self._registry.get(node_id)
        if node is None:
            # Unknown node — allow allocation without dependency check
            self._allocated.add(node_id)
            return
        missing = [d for d in node.dependencies if d not in self._allocated]
        if missing:
            raise ValueError(
                f"Cannot allocate node {node_id}: missing dependencies {missing}"
            )
        self._allocated.add(node_id)

    def deallocate(self, node_id: int) -> None:
        """Remove a node from the allocated set."""
        self._allocated.discard(node_id)

    def is_allocated(self, node_id: int) -> bool:
        return node_id in self._allocated

    def get_allocated_ids(self) -> list[int]:
        return sorted(self._allocated)

    def to_node_dicts(self) -> list[dict]:
        """
        Return all REGISTERED nodes in the stat_engine-compatible format.
        Only registered nodes can supply stat_engine node bonuses.
        """
        return [n.to_dict() for n in self._registry.values()]

    def _has_circular_dependency(
        self,
        node_id: int,
        deps: list[int],
        visiting: set[int],
        registry: dict[int, "PassiveNode"] | None = None,
    ) -> bool:
        reg = registry if registry is not None else self._registry
        if node_id in visiting:
            return True
        visiting = visiting | {node_id}
        for dep in deps:
            dep_node = reg.get(dep)
            if dep_node is None:
                continue
            if self._has_circular_dependency(dep, dep_node.dependencies, visiting, reg):
                return True
        return False
