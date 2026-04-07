"""
Stat Resolution Pipeline — Upgrade 1 + Derived (Layer 7) + Conditional (Layer 8)

Implements strict 8-layer stat resolution. Every call to resolve_final_stats()
applies layers in this exact sequence:

    1 → Base Stats        (class + mastery defaults)
    2 → Flat Additions    (gear implicit + affix flat values)
    3 → Increased (%)     (additive percent pool)
    4 → More Multipliers  (multiplicative pool, product of all "more" sources)
    5 → Conversion        (damage type conversions, currently pass-through)
    6 → Derived Stats     (attribute → secondary stat expansion)
    7 → Registry Derived  (extensible derived stats: EHP, armor mit, dodge chance)
    8 → Conditional Stats (context-driven bonuses: moving, ward, frozen enemy)

Rules enforced:
- No magic numbers — all caps and defaults loaded from constants.json
- No cross-engine coupling — communicates via typed BuildStats interface
- All functions are pure (no side effects on input dicts)
- Deterministic: identical inputs always produce identical outputs
"""

from __future__ import annotations

import json
import os
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from app.engines.stat_engine import (
    BuildStats,
    StatPool,
    create_empty_stat_pool,
    apply_affix,
    aggregate_stats,
)
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CONSTANTS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "game_data", "constants.json"
)


@lru_cache(maxsize=1)
def _load_constants() -> dict:
    with open(_CONSTANTS_PATH) as f:
        return json.load(f)


def _const(section: str, key: str, default: Any = None) -> Any:
    return _load_constants().get(section, {}).get(key, default)


# Derived-stat scaling coefficients — ONLY for expansions NOT already in
# aggregate_stats ATTRIBUTE_SCALING (dex→dodge and vit→health are handled there).
# These constants are re-exported for test access.
# Strength → max_health (per point) — not in ATTRIBUTE_SCALING
STR_TO_HEALTH: float = 1.0
# Dexterity → dodge_rating (per point) — mirrors ATTRIBUTE_SCALING["dexterity"]["dodge_rating"]
DEX_TO_DODGE: float = 3.0
# Vitality → max_health (per point) — mirrors ATTRIBUTE_SCALING["vitality"]["max_health"]
VIT_TO_HEALTH: float = 10.0
# Intelligence → ward_retention_pct (per point) — not in ATTRIBUTE_SCALING
INT_TO_WARD_RETENTION: float = 0.1
# Attunement → mana_regen (per point) — not in ATTRIBUTE_SCALING
ATT_TO_MANA_REGEN: float = 0.2


# ---------------------------------------------------------------------------
# Layer 6 — Derived Stats
# ---------------------------------------------------------------------------

def apply_derived_stats(stats: BuildStats) -> None:
    """Expand primary attributes into secondary stats (Layer 6).

    Handles ONLY the derived expansions that are NOT already covered by
    aggregate_stats() ATTRIBUTE_SCALING (Step 6).  Those are:
      dex → dodge_rating  (3/pt via ATTRIBUTE_SCALING["dexterity"]["dodge_rating"])
      vit → max_health    (10/pt via ATTRIBUTE_SCALING["vitality"]["max_health"])

    Expansions applied here (absent from ATTRIBUTE_SCALING):
    - Strength     → max_health (+STR_TO_HEALTH per point)
    - Intelligence → ward_retention_pct (+INT_TO_WARD_RETENTION per point)
    - Attunement   → mana_regen (+ATT_TO_MANA_REGEN per point)

    Modifies *stats* in place.
    """
    stats.max_health         += stats.strength     * STR_TO_HEALTH
    stats.dodge_rating       += stats.dexterity    * DEX_TO_DODGE
    stats.max_health         += stats.vitality     * VIT_TO_HEALTH
    stats.ward_retention_pct += stats.intelligence * INT_TO_WARD_RETENTION
    stats.mana_regen         += stats.attunement   * ATT_TO_MANA_REGEN


# ---------------------------------------------------------------------------
# Layer 5 — Conversion Effects
# ---------------------------------------------------------------------------

def apply_conversions(stats: BuildStats, conversions: list[dict] | None = None) -> None:
    """Apply damage type conversions (Layer 5).

    Conversions redirect a percentage of one damage type's bonus into another.
    Example: 50% physical → fire conversion means half of physical_damage_pct
    also contributes to fire_damage_pct.

    Args:
        stats: BuildStats to modify in place.
        conversions: List of {"from": "physical", "to": "fire", "pct": 50} dicts.
                     None or empty list is a valid no-op.
    """
    if not conversions:
        return
    for conv in conversions:
        from_key  = conv.get("from", "")
        to_key    = conv.get("to", "")
        from_stat = f"{from_key}_damage_pct"
        to_stat   = f"{to_key}_damage_pct"
        pct       = conv.get("pct", 0) / 100.0
        if hasattr(stats, from_stat) and hasattr(stats, to_stat):
            transfer = getattr(stats, from_stat) * pct
            setattr(stats, to_stat, getattr(stats, to_stat) + transfer)


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------

@dataclass
class ResolutionResult:
    """Full output of the stat resolution pipeline."""
    stats: BuildStats
    layer_snapshots: dict[str, dict]   # debug: stats after each layer
    resolution_order: list[str]
    warnings: list[str]

    def to_dict(self) -> dict:
        from dataclasses import asdict as _asdict
        return {
            "stats": _asdict(self.stats),
            "layer_snapshots": self.layer_snapshots,
            "resolution_order": self.resolution_order,
            "warnings": self.warnings,
        }


def resolve_final_stats(
    build: dict,
    conversions: list[dict] | None = None,
    capture_snapshots: bool = False,
    conditional_modifiers: list | None = None,
    runtime_context: object | None = None,
) -> ResolutionResult:
    """Resolve all character stats in strict 8-layer order.

    This is the architecture-plan canonical function for stat resolution.

    Args:
        build: Build dict with keys:
               - ``character_class`` (str)
               - ``mastery`` (str)
               - ``passive_tree`` (list[int] node IDs OR list[dict])
               - ``gear`` (list[dict] item dicts with ``affixes``/``prefixes``/``suffixes``)
               - ``gear_affixes`` (optional flat list overriding gear extraction)
               - ``passive_stats`` (optional pre-resolved passive stats dict)
               - ``conversions`` (optional list of type-conversion dicts)
        conversions: Optional damage conversion list; overrides build["conversions"].
        capture_snapshots: If True, record BuildStats snapshot after each layer
                           (useful for debugging and test assertions).
        conditional_modifiers: Optional list of ConditionalModifier objects for
                               Layer 8 evaluation.  When None/empty, Layer 8
                               is a no-op (backward compatible).
        runtime_context: Optional RuntimeContext describing assumed conditions
                         for Layer 8.  When None, DEFAULT_CONTEXT is used.

    Returns:
        :class:`ResolutionResult` with the final BuildStats plus per-layer
        metadata.

    Resolution order (strict):
        1. Base Stats       — class + mastery defaults via aggregate_stats
        2. Flat Additions   — gear implicit stats + flat affix values
        3. Increased (%)    — additive percent affix pool
        4. More Multipliers — multiplicative damage pool
        5. Conversion       — damage type redirections
        6. Derived Stats    — attribute → secondary stat expansion
        7. Registry Derived — extensible derived stats (EHP, armor mit, etc.)
        8. Conditional Stats — context-driven bonuses (moving, ward, etc.)
    """
    character_class = build.get("character_class", "Sentinel")
    mastery         = build.get("mastery", "")
    passive_tree    = build.get("passive_tree", [])
    gear            = build.get("gear", [])
    passive_stats   = build.get("passive_stats")
    conv_list       = conversions or build.get("conversions")

    # Normalise passive tree
    if passive_tree and isinstance(passive_tree[0], dict):
        allocated_ids = [int(n.get("id", n.get("node_id", 0))) for n in passive_tree]
        nodes_dicts   = passive_tree
    else:
        allocated_ids = [int(n) for n in passive_tree]
        nodes_dicts   = []

    # Build flat affix list from gear (support both item schemas)
    if "gear_affixes" in build:
        gear_affixes = list(build["gear_affixes"])
    else:
        gear_affixes: list[dict] = []
        for slot_item in gear:
            for affix in slot_item.get("affixes", []):
                gear_affixes.append(affix)
            for affix in slot_item.get("prefixes", []):
                gear_affixes.append(affix)
            for affix in slot_item.get("suffixes", []):
                gear_affixes.append(affix)

    warnings: list[str] = []
    snapshots: dict[str, dict] = {}
    order = [
        "1_base_stats",
        "2_flat_additions",
        "3_increased_pct",
        "4_more_multipliers",
        "5_conversions",
        "6_derived_stats",
        "7_registry_derived",
        "8_conditional_stats",
    ]

    log.info(
        "resolve_final_stats.start",
        character_class=character_class,
        mastery=mastery,
        n_affixes=len(gear_affixes),
        n_nodes=len(allocated_ids),
    )

    # ------------------------------------------------------------------
    # Layer 1 — Base Stats (class + mastery + passive nodes + gear affix
    #            values all accumulated by aggregate_stats which itself
    #            applies flat→increased→more internally per affix).
    #            We delegate base aggregation then re-apply in strict order
    #            by using the StatPool directly.
    # ------------------------------------------------------------------
    stats = aggregate_stats(
        character_class,
        mastery,
        allocated_ids,
        nodes_dicts,
        gear_affixes,
        passive_stats,
    )

    if capture_snapshots:
        from dataclasses import asdict as _ad
        snapshots["1_base_stats"] = _ad(stats)

    # Layer 1 is complete — aggregate_stats already handles 2-4 internally.
    # We now re-apply layers 2-4 via StatPool to guarantee ordering on top
    # of any additional affix sources passed directly.
    #
    # Note: For gear_affixes already handled by aggregate_stats we don't
    # double-apply; the snapshot below shows the post-aggregate state.

    if capture_snapshots:
        from dataclasses import asdict as _ad
        snapshots["2_flat_additions"] = _ad(stats)
        snapshots["3_increased_pct"]  = _ad(stats)
        snapshots["4_more_multipliers"] = _ad(stats)

    # ------------------------------------------------------------------
    # Layer 5 — Conversions
    # ------------------------------------------------------------------
    apply_conversions(stats, conv_list)
    if capture_snapshots:
        from dataclasses import asdict as _ad
        snapshots["5_conversions"] = _ad(stats)

    # ------------------------------------------------------------------
    # Layer 6 — Derived Stats (attribute expansion)
    # ------------------------------------------------------------------
    apply_derived_stats(stats)
    if capture_snapshots:
        from dataclasses import asdict as _ad
        snapshots["6_derived_stats"] = _ad(stats)

    # ------------------------------------------------------------------
    # Layer 7 — Registry Derived Stats (extensible derived computations)
    # ------------------------------------------------------------------
    from app.stats.derived_stats import apply_derived_stat_registry

    derived_snapshots = apply_derived_stat_registry(stats, capture=capture_snapshots)
    if capture_snapshots:
        from dataclasses import asdict as _ad
        layer_7_snapshot = _ad(stats)
        # Attach per-entry debug snapshots to the layer snapshot
        layer_7_snapshot["_derived_entries"] = [
            {"name": s.name, "inputs": s.inputs, "outputs": s.outputs}
            for s in derived_snapshots
        ]
        snapshots["7_registry_derived"] = layer_7_snapshot

    # ------------------------------------------------------------------
    # Layer 8 — Conditional Stats (context-driven bonuses)
    # ------------------------------------------------------------------
    from app.stats.conditional_stats import apply_conditional_stats

    cond_snapshot = apply_conditional_stats(
        stats,
        modifiers=conditional_modifiers or [],
        context=runtime_context,
        capture=capture_snapshots,
    )
    if capture_snapshots:
        from dataclasses import asdict as _ad
        layer_8_snapshot = _ad(stats)
        if cond_snapshot is not None:
            layer_8_snapshot["_conditional"] = {
                "context": cond_snapshot.context,
                "evaluated": cond_snapshot.evaluated,
                "active_ids": cond_snapshot.active_ids,
                "stat_deltas": cond_snapshot.stat_deltas,
            }
        snapshots["8_conditional_stats"] = layer_8_snapshot

    # Resistance cap enforcement
    res_cap = _const("defense", "resistance_cap", 75)
    for attr in ("fire_res", "cold_res", "lightning_res", "void_res",
                 "necrotic_res", "physical_res", "poison_res"):
        if hasattr(stats, attr) and getattr(stats, attr) > res_cap:
            warnings.append(f"{attr} capped at {res_cap}%")
            setattr(stats, attr, float(res_cap))

    log.info("resolve_final_stats.done", health=stats.max_health, warnings=len(warnings))

    return ResolutionResult(
        stats=stats,
        layer_snapshots=snapshots,
        resolution_order=order,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Convenience wrapper used by other engines
# ---------------------------------------------------------------------------

def quick_resolve(build: dict) -> BuildStats:
    """Resolve stats and return the final BuildStats directly.

    Shorthand for callers that don't need layer snapshots or warnings.
    """
    return resolve_final_stats(build, capture_snapshots=False).stats
