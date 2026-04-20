"""
E6 — Passive System

Manages passive node allocation for a build.
Tracks dependency chains and prevents circular allocations.
Emits stat modifiers from allocated nodes into a StatPool.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.engines.stat_engine import StatPool


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

    def apply_to_stat_pool(self, pool: "StatPool") -> None:
        """Emit stat modifiers from all allocated nodes into *pool*.

        For each allocated node that has metadata in the registry, the
        node bonus is computed using the same logic as
        ``stat_engine._get_node_bonus`` and routed into the correct
        StatPool bucket (flat / increased / more).

        Nodes without registry metadata are skipped — their stats are
        handled by aggregate_stats via the modulo fallback or by
        pre-resolved passive_stats from the DB resolver.

        DEPRECATED:
            This method and ``_get_node_stat_bonus`` below still rely on
            the CLASS_STAT_CYCLES modulo heuristic, which fabricates stat
            values from node_id rather than reading game data. It is
            retained because ``BuildState.recompute`` (exercised by
            tests/test_equipment_pipeline.py) constructs PassiveSystem
            instances without attaching the real PassiveNode rows. New
            production paths should pre-resolve stats via
            ``app.services.passive_stat_resolver.resolve_passive_stats``
            and pass the result through ``aggregate_stats(passive_stats=…)``.
        """
        from app.utils.logging import ForgeLogger
        log = ForgeLogger(__name__)

        for node_id in sorted(self._allocated):
            node = self._registry.get(node_id)
            if node is None:
                continue
            bonus = self._get_node_stat_bonus(node)
            for stat_key, value in bonus.items():
                if value == 0:
                    continue
                if stat_key.endswith("_pct"):
                    pool.add_increased(stat_key, value)
                elif stat_key.startswith("more_") or stat_key == "more_damage_multiplier":
                    pool.add_more(stat_key, value)
                else:
                    pool.add_flat(stat_key, value)
                log.debug(
                    "passive.emit",
                    node_id=node_id,
                    node_name=node.name,
                    stat_key=stat_key,
                    value=value,
                )

    @staticmethod
    def _get_node_stat_bonus(node: PassiveNode) -> dict[str, float]:
        """Compute the stat bonus dict for a single passive node.

        Mirrors ``stat_engine._get_node_bonus`` logic:
        - Mastery-gate nodes produce nothing.
        - Keystone nodes use the KEYSTONE_BONUSES lookup.
        - Minor/notable nodes use the CORE_STAT_CYCLE modulo heuristic,
          with notables getting 3× the base amount.
        """
        from app.engines.stat_engine import (
            CLASS_STAT_CYCLES,
            CORE_STAT_CYCLE,
            KEYSTONE_BONUSES,
            NOTABLE_MULTIPLIER,
        )

        if node.node_type == "mastery-gate":
            return {}
        if node.node_type == "keystone":
            return dict(KEYSTONE_BONUSES.get(node.name, {
                "spell_damage_pct": 10,
                "max_health": 50,
            }))
        cycle = CORE_STAT_CYCLE  # default; class-aware lookup in stat_engine
        stat_key, base_amount = cycle[node.node_id % len(cycle)]
        amount = base_amount * NOTABLE_MULTIPLIER if node.node_type == "notable" else base_amount
        return {stat_key: float(amount)}

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
