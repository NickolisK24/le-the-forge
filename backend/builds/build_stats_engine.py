"""
E3 — Build Stats Engine

Converts a BuildDefinition into numeric BuildStats by delegating to
app.engines.stat_engine.aggregate_stats().

Also supports compiling from BuildState (the new equipment-set-aware
domain model) via compile_from_state().

The game data loader uses a module-level fallback pipeline, so this
works both inside and outside a Flask application context.
"""

from __future__ import annotations
from dataclasses import asdict
from typing import TYPE_CHECKING

from builds.build_definition import BuildDefinition
from builds.passive_system   import PassiveNode

if TYPE_CHECKING:
    from app.domain.build_state import BuildState
    from app.engines.stat_engine import BuildStats


class BuildStatsEngine:
    """
    Stateless compiler: BuildDefinition → BuildStats.

    Usage
    -----
    engine = BuildStatsEngine()
    stats  = engine.compile(build)
    params = engine.to_encounter_params(build)
    """

    def compile(
        self,
        build: BuildDefinition,
        passive_nodes: list[PassiveNode] | None = None,
    ):
        """
        Compile a BuildDefinition into a BuildStats object.

        passive_nodes:
            Optional list of PassiveNode objects used for node-type lookups
            in stat_engine.  When omitted (or empty), passive bonuses fall back
            to the modulo heuristic inside stat_engine.

        Returns
        -------
        BuildStats (from app.engines.stat_engine)
        """
        from app.engines.stat_engine import aggregate_stats

        node_dicts = [n.to_dict() for n in (passive_nodes or [])]

        # Flatten all gear affixes (each item → list of {"name": str, "tier": int})
        gear_affixes = build.all_gear_affixes()

        # Base stats from class + mastery + passives + gear
        stats = aggregate_stats(
            character_class=build.character_class,
            mastery=build.mastery,
            allocated_node_ids=build.passive_ids,
            nodes=node_dicts,
            gear_affixes=gear_affixes,
        )

        # Apply buff modifiers on top of base stats
        for buff in build.buffs:
            for stat_key, delta in buff.modifiers.items():
                if hasattr(stats, stat_key):
                    setattr(stats, stat_key, getattr(stats, stat_key) + delta)

        return stats

    def to_encounter_params(
        self,
        build: BuildDefinition,
        passive_nodes: list[PassiveNode] | None = None,
    ) -> dict:
        """
        Return a dict of kwargs suitable for run_encounter_simulation().

        Effective base_damage = raw base_damage scaled by the combined additive
        percent damage pool (spell + elemental + physical + more_damage).
        This mirrors how the skill engine applies damage modifiers.
        """
        stats = self.compile(build, passive_nodes)

        # Combine additive increased damage pools (additive with each other)
        total_increased_pct = (
            stats.spell_damage_pct
            + stats.physical_damage_pct
            + stats.elemental_damage_pct
            + stats.more_damage_pct
        )
        effective_damage = stats.base_damage * (1.0 + total_increased_pct / 100.0)

        return {
            "base_damage":     effective_damage,
            "crit_chance":     stats.crit_chance,
            "crit_multiplier": stats.crit_multiplier,
        }

    # ------------------------------------------------------------------
    # BuildState integration (equipment-set-aware path)
    # ------------------------------------------------------------------

    def compile_from_state(self, state: "BuildState") -> "BuildStats":
        """Compile stats from a BuildState using its recompute pipeline.

        This delegates to BuildState.recompute() which runs the full
        6-layer resolution pipeline with equipment, passives, and buffs.
        """
        return state.recompute()
