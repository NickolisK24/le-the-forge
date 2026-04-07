"""
BuildState — mutable container that holds all build inputs and drives
end-to-end stat recomputation through the resolution pipeline.

Sits above the individual subsystems (equipment, passives, buffs) and
orchestrates the full recompute loop:

    Equipment → StatPool  ←  Passives  ←  Buffs
                   ↓
          stat_resolution_pipeline
                   ↓
              BuildStats

This is a pure domain model — no DB, no HTTP.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from app.domain.equipment_set import EquipmentSet
from app.domain.item import Item
from app.engines.stat_engine import BuildStats, StatPool, create_empty_stat_pool
from app.utils.logging import ForgeLogger
from builds.passive_system import PassiveSystem

if TYPE_CHECKING:
    from builds.buff_system import Buff

log = ForgeLogger(__name__)


@dataclass
class BuildState:
    """Full mutable build state with deterministic stat recomputation.

    Usage::

        state = BuildState(
            character_class="Mage",
            mastery="Sorcerer",
            equipment=gear_set,
        )
        state.recompute()
        print(state.resolved_stats.max_health)
    """

    character_class: str = "Sentinel"
    mastery: str = ""

    equipment: EquipmentSet = field(default_factory=EquipmentSet)
    passive_node_ids: set[int] = field(default_factory=set)
    passive_system: Optional[PassiveSystem] = None
    active_buffs: dict[str, "Buff"] = field(default_factory=dict)

    # Pre-resolved passive stats from passive_stat_resolver (optional).
    # When provided, these override the modulo-based fallback in aggregate_stats.
    passive_stats: Optional[dict] = None

    # Pipeline output — populated by recompute()
    resolved_stats: Optional[BuildStats] = None
    last_pool_snapshot: Optional[dict] = None

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def equip_item(self, item: Item) -> Item | None:
        """Equip an item and mark stats as stale."""
        self.resolved_stats = None
        return self.equipment.equip_item(item)

    def unequip(self, slot: str) -> Item | None:
        """Unequip a slot and mark stats as stale."""
        self.resolved_stats = None
        return self.equipment.unequip(slot)

    def add_passive(self, node_id: int) -> None:
        self.resolved_stats = None
        self.passive_node_ids.add(node_id)

    def remove_passive(self, node_id: int) -> None:
        self.resolved_stats = None
        self.passive_node_ids.discard(node_id)

    def add_buff(self, buff: "Buff") -> None:
        self.resolved_stats = None
        self.active_buffs[buff.buff_id] = buff

    def remove_buff(self, buff_id: str) -> None:
        self.resolved_stats = None
        self.active_buffs.pop(buff_id, None)

    # ------------------------------------------------------------------
    # Recompute pipeline
    # ------------------------------------------------------------------

    def recompute(self, capture_pool: bool = False) -> BuildStats:
        """Run the full stat resolution pipeline and cache the result.

        Execution order:
            1. Create empty StatPool
            2. Apply **equipment** stats → StatPool
            3. Apply **passive** stats → StatPool  (via PassiveSystem)
            4. Apply **buff** modifiers on final BuildStats
            5. Delegate to resolve_final_stats for full 6-layer resolution
               (class base → flat → increased → more → conversions → derived)
            6. Store final BuildStats

        Args:
            capture_pool: If True, snapshot the raw StatPool after
                          equipment + passives for debugging.

        Returns:
            The fully resolved BuildStats.
        """
        log.debug(
            "build_state.recompute.start",
            character_class=self.character_class,
            mastery=self.mastery,
            n_items=len(self.equipment),
            n_passives=len(self.passive_node_ids),
            n_buffs=len(self.active_buffs),
            has_passive_system=self.passive_system is not None,
        )

        # 1 — Fresh stat pool
        pool = create_empty_stat_pool()

        # 2 — Equipment contributes to the pool
        self.equipment.apply_to_stat_pool(pool)
        log.debug("build_state.recompute.equipment_done")

        # 3 — Passives contribute to the pool (if PassiveSystem available)
        if self.passive_system is not None:
            self.passive_system.apply_to_stat_pool(pool)
            log.debug(
                "build_state.recompute.passives_done",
                n_allocated=len(self.passive_system.get_allocated_ids()),
            )

        if capture_pool:
            self.last_pool_snapshot = pool.to_dict()

        # 4 — Collect gear affixes in the flat format that
        #     resolve_final_stats / aggregate_stats expects.
        gear_affixes = self._collect_gear_affixes_for_pipeline()

        # 5 — Build the dict that resolve_final_stats expects.
        #     Include node dicts so aggregate_stats can apply the modulo
        #     fallback for nodes that have metadata but no pre-resolved stats.
        node_dicts = self._collect_passive_node_dicts()

        build_dict: dict = {
            "character_class": self.character_class,
            "mastery": self.mastery,
            "passive_tree": node_dicts if node_dicts else sorted(self.passive_node_ids),
            "gear_affixes": gear_affixes,
        }
        if self.passive_stats:
            build_dict["passive_stats"] = self.passive_stats

        # 6 — Run the canonical 6-layer pipeline
        from app.engines.stat_resolution_pipeline import resolve_final_stats

        result = resolve_final_stats(build_dict, capture_snapshots=True)
        stats = result.stats
        log.debug("build_state.recompute.pipeline_done")

        # 7 — Apply buff modifiers on top (same logic as BuildStatsEngine)
        for buff in self.active_buffs.values():
            for stat_key, delta in buff.modifiers.items():
                if hasattr(stats, stat_key):
                    setattr(stats, stat_key, getattr(stats, stat_key) + delta)
        log.debug("build_state.recompute.buffs_done", n_buffs=len(self.active_buffs))

        self.resolved_stats = stats

        log.debug(
            "build_state.recompute.done",
            health=stats.max_health,
            base_damage=stats.base_damage,
            warnings=len(result.warnings),
        )
        return stats

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _collect_passive_node_dicts(self) -> list[dict]:
        """Return node dicts for all allocated passives (with metadata).

        If a PassiveSystem is attached, uses its registry to produce
        ``{"id": int, "type": str, "name": str}`` dicts that
        ``aggregate_stats`` needs for the modulo fallback.

        Returns an empty list if no PassiveSystem is set — in that case
        ``passive_tree`` falls back to a bare int list.
        """
        if self.passive_system is None:
            return []
        return self.passive_system.to_node_dicts()

    def _collect_gear_affixes_for_pipeline(self) -> list[dict]:
        """Flatten all equipped item affixes into the stat_engine format.

        This produces the ``[{"stat_key": ..., "value": ...}]`` format
        that aggregate_stats understands (format b: direct stat_key injection).
        We use format b because Item.affixes already have resolved values,
        so we bypass the affix-name → tier-midpoint lookup.
        """
        affixes: list[dict] = []
        for item in self.equipment.list_items():
            for affix in item.affixes:
                affixes.append({
                    "stat_key": affix.stat_key,
                    "value": affix.value,
                })
            for stat_key, value in item.implicit_stats.items():
                affixes.append({
                    "stat_key": stat_key,
                    "value": value,
                })
        return affixes

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        from dataclasses import asdict

        # Serialize passive nodes from the system if available
        passive_nodes_data: list[dict] = []
        if self.passive_system is not None:
            passive_nodes_data = self.passive_system.to_node_dicts()

        return {
            "character_class": self.character_class,
            "mastery": self.mastery,
            "equipment": self.equipment.to_dict(),
            "passive_node_ids": sorted(self.passive_node_ids),
            "passive_nodes": passive_nodes_data,
            "active_buffs": {
                bid: buff.to_dict()
                for bid, buff in self.active_buffs.items()
            },
            "resolved_stats": asdict(self.resolved_stats) if self.resolved_stats else None,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "BuildState":
        from builds.buff_system import Buff
        from builds.passive_system import PassiveNode

        equipment = EquipmentSet.from_dict(d.get("equipment", {}))
        buffs = {
            bid: Buff.from_dict(bd)
            for bid, bd in d.get("active_buffs", {}).items()
        }
        passive_node_ids = set(d.get("passive_node_ids", []))

        # Rebuild PassiveSystem from serialised node dicts if present
        passive_system: PassiveSystem | None = None
        raw_nodes = d.get("passive_nodes", [])
        if raw_nodes:
            nodes = [PassiveNode.from_dict(nd) for nd in raw_nodes]
            passive_system = PassiveSystem(nodes)
            for nid in passive_node_ids:
                try:
                    passive_system.allocate(nid)
                except ValueError:
                    pass  # skip dependency failures on deserialisation

        return cls(
            character_class=d.get("character_class", "Sentinel"),
            mastery=d.get("mastery", ""),
            equipment=equipment,
            passive_node_ids=passive_node_ids,
            passive_system=passive_system,
            active_buffs=buffs,
            passive_stats=d.get("passive_stats"),
        )
