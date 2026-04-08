"""
Gear Upgrade Ranker — Phase 7 Engine

For each gear slot, evaluates candidate items by simulating a swap:
  - Replace current item → recalculate stats → compute DPS and EHP delta
  - Estimate FP cost to craft the candidate item
  - Score efficiency = weighted_impact / fp_cost
  - Return ranked candidates per slot + overall top-10

Uses the existing stat_engine, combat_engine, defense_engine, and
affix_engine/efficiency_scorer for FP cost estimation.

Pure module — no DB, no HTTP.
"""

from __future__ import annotations

import time
from copy import copy as _copy
from dataclasses import dataclass, field
from typing import Optional

from app.engines.stat_engine import BuildStats, aggregate_stats
from app.engines.combat_engine import calculate_dps
from app.engines.defense_engine import calculate_ehp
from app.engines.efficiency_scorer import _fp_cost_for_tier
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


# ---------------------------------------------------------------------------
# Gear slot definitions
# ---------------------------------------------------------------------------

GEAR_SLOTS = [
    "helmet", "body", "gloves", "boots", "belt",
    "amulet", "ring1", "ring2", "relic",
    "weapon", "off_hand",
]

# Map display slot names to internal slot keys
_SLOT_ALIASES = {
    "helm": "helmet",
    "chest": "body",
    "body_armour": "body",
    "feet": "boots",
    "ring": "ring1",
}


def _normalize_slot(slot: str) -> str:
    return _SLOT_ALIASES.get(slot.lower(), slot.lower())


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class GearUpgradeCandidate:
    item_name: str
    base_type: str
    slot: str
    affixes: list[dict]
    dps_delta_pct: float
    ehp_delta_pct: float
    fp_cost: int
    efficiency_score: float
    rank: int = 0

    def to_dict(self) -> dict:
        return {
            "item_name": self.item_name,
            "base_type": self.base_type,
            "slot": self.slot,
            "affixes": self.affixes,
            "dps_delta_pct": round(self.dps_delta_pct, 1),
            "ehp_delta_pct": round(self.ehp_delta_pct, 1),
            "fp_cost": self.fp_cost,
            "efficiency_score": round(self.efficiency_score, 2),
            "rank": self.rank,
        }


@dataclass
class SlotUpgradeResult:
    slot: str
    candidates: list[GearUpgradeCandidate]

    def to_dict(self) -> dict:
        return {
            "slot": self.slot,
            "candidates": [c.to_dict() for c in self.candidates],
        }


@dataclass
class GearUpgradeResult:
    slots: list[SlotUpgradeResult]
    top_10_overall: list[GearUpgradeCandidate]
    execution_time: float = 0.0

    def to_dict(self) -> dict:
        return {
            "slots": [s.to_dict() for s in self.slots],
            "top_10_overall": [c.to_dict() for c in self.top_10_overall],
        }


# ---------------------------------------------------------------------------
# Candidate generation
# ---------------------------------------------------------------------------

def _generate_candidates_for_slot(
    slot: str,
    character_class: str,
    primary_damage_type: str | None = None,
) -> list[dict]:
    """Generate candidate affix combos for a slot from the affix registry.

    Returns a list of candidate item dicts with synthesized affixes.
    """
    try:
        from flask import current_app
        pipeline = current_app.extensions.get("game_data")
        if not pipeline:
            return []
        all_affixes = [a.to_dict() for a in pipeline.affixes]
    except RuntimeError:
        return []

    # Filter affixes applicable to this slot
    slot_affixes = [
        a for a in all_affixes
        if slot in (a.get("applicable_to") or [])
        or _normalize_slot(slot) in (a.get("applicable_to") or [])
    ]

    if not slot_affixes:
        return []

    # Score affixes by relevance to the build's damage type
    offense_affixes = []
    defense_affixes = []
    for a in slot_affixes:
        tags = a.get("tags", [])
        stat_key = a.get("stat_key", "")
        if any(t in tags for t in ["damage", "critical", "attack_speed"]) or "damage" in stat_key:
            offense_affixes.append(a)
        else:
            defense_affixes.append(a)

    # Generate a few candidate items with different affix combos
    candidates = []
    # Top offense affixes
    for affix in offense_affixes[:5]:
        name = affix.get("name", "Unknown")
        tiers = affix.get("tiers", [])
        best_tier = tiers[-1] if tiers else {"tier": 1, "min": 0, "max": 0}
        candidates.append({
            "item_name": f"{name} {slot.title()}",
            "base_type": f"Base {slot.title()}",
            "slot": slot,
            "affixes": [{"name": name, "tier": best_tier.get("tier", 1)}],
        })

    # Top defense affixes
    for affix in defense_affixes[:3]:
        name = affix.get("name", "Unknown")
        tiers = affix.get("tiers", [])
        best_tier = tiers[-1] if tiers else {"tier": 1, "min": 0, "max": 0}
        candidates.append({
            "item_name": f"{name} {slot.title()}",
            "base_type": f"Base {slot.title()}",
            "slot": slot,
            "affixes": [{"name": name, "tier": best_tier.get("tier", 1)}],
        })

    return candidates[:8]  # cap per slot


# ---------------------------------------------------------------------------
# Core evaluation
# ---------------------------------------------------------------------------

def _evaluate_candidate(
    stats: BuildStats,
    candidate: dict,
    current_gear_affixes: list[dict],
    slot_idx: int,
    base_dps: float,
    base_ehp: float,
    primary_skill: str,
    skill_level: int,
    character_class: str,
    mastery: str,
    allocated_node_ids: list,
    nodes: list,
    all_gear: list[dict],
    passive_stats: dict | None,
    offense_weight: float = 0.6,
    defense_weight: float = 0.4,
) -> GearUpgradeCandidate | None:
    """Evaluate a single gear candidate by simulating the swap."""
    candidate_affixes = candidate.get("affixes", [])
    if not candidate_affixes:
        return None

    # Build modified gear list with candidate swapped in
    modified_gear = list(all_gear)
    if slot_idx < len(modified_gear):
        modified_gear[slot_idx] = candidate
    else:
        modified_gear.append(candidate)

    # Flatten all gear affixes from modified gear
    new_gear_affixes = []
    for slot_item in modified_gear:
        for affix in (slot_item.get("affixes") or []):
            new_gear_affixes.append(affix)

    # Re-aggregate stats with new gear
    new_stats = aggregate_stats(
        character_class=character_class,
        mastery=mastery,
        allocated_node_ids=allocated_node_ids,
        nodes=nodes,
        gear_affixes=new_gear_affixes,
        passive_stats=passive_stats,
    )

    new_dps = calculate_dps(new_stats, primary_skill, skill_level).dps
    new_ehp = calculate_ehp(new_stats)

    dps_delta = ((new_dps - base_dps) / base_dps * 100) if base_dps > 0 else 0.0
    ehp_delta = ((new_ehp - base_ehp) / base_ehp * 100) if base_ehp > 0 else 0.0

    # FP cost: sum of tier costs for all affixes
    fp_cost = sum(_fp_cost_for_tier(a.get("tier", 1)) for a in candidate_affixes)
    fp_cost = max(1, fp_cost)

    weighted_impact = dps_delta * offense_weight + ehp_delta * defense_weight
    efficiency = weighted_impact / fp_cost if fp_cost > 0 else weighted_impact

    return GearUpgradeCandidate(
        item_name=candidate.get("item_name", "Unknown Item"),
        base_type=candidate.get("base_type", "Unknown"),
        slot=candidate.get("slot", "unknown"),
        affixes=candidate_affixes,
        dps_delta_pct=dps_delta,
        ehp_delta_pct=ehp_delta,
        fp_cost=fp_cost,
        efficiency_score=efficiency,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def rank_gear_upgrades(
    stats: BuildStats,
    build: dict,
    primary_skill: str,
    skill_level: int = 20,
    slot_filter: str | None = None,
    candidate_items: list[dict] | None = None,
    top_n_per_slot: int = 5,
    top_n_overall: int = 10,
) -> GearUpgradeResult:
    """Rank gear upgrades for a build across all (or filtered) slots.

    Args:
        stats: Fully resolved BuildStats.
        build: Build dict with character_class, mastery, passive_tree, gear.
        primary_skill: Primary damage skill.
        skill_level: Skill level.
        slot_filter: If set, only evaluate this slot.
        candidate_items: External candidate list. If None, auto-generate.
        top_n_per_slot: Max candidates per slot.
        top_n_overall: Max candidates in the overall ranking.

    Returns:
        GearUpgradeResult with per-slot rankings and overall top-10.
    """
    t_start = time.perf_counter()

    character_class = build.get("character_class", "Sentinel")
    mastery = build.get("mastery", "")
    gear = build.get("gear") or []
    passive_tree = build.get("passive_tree") or []
    passive_stats = build.get("passive_stats")
    nodes = build.get("nodes") or []

    # Flatten current gear affixes
    current_affixes = []
    for slot_item in gear:
        for affix in (slot_item.get("affixes") or []):
            current_affixes.append(affix)

    # Baseline DPS and EHP
    base_dps = float(calculate_dps(stats, primary_skill, skill_level).dps)
    base_ehp = float(calculate_ehp(stats))

    # Determine which slots to evaluate
    if slot_filter:
        norm = _normalize_slot(slot_filter)
        slots_to_eval = [norm]
    else:
        slots_to_eval = GEAR_SLOTS

    # Build a slot-index map from existing gear
    slot_index_map: dict[str, int] = {}
    for i, item in enumerate(gear):
        s = _normalize_slot(item.get("slot", f"slot_{i}"))
        slot_index_map[s] = i

    slot_results: list[SlotUpgradeResult] = []
    all_candidates: list[GearUpgradeCandidate] = []

    for slot in slots_to_eval:
        # Get candidates for this slot
        if candidate_items:
            slot_candidates = [c for c in candidate_items if _normalize_slot(c.get("slot", "")) == slot]
        else:
            slot_candidates = _generate_candidates_for_slot(
                slot, character_class,
                primary_damage_type=None,
            )

        if not slot_candidates:
            continue

        slot_idx = slot_index_map.get(slot, len(gear))
        evaluated: list[GearUpgradeCandidate] = []

        for candidate in slot_candidates:
            result = _evaluate_candidate(
                stats=stats,
                candidate=candidate,
                current_gear_affixes=current_affixes,
                slot_idx=slot_idx,
                base_dps=base_dps,
                base_ehp=base_ehp,
                primary_skill=primary_skill,
                skill_level=skill_level,
                character_class=character_class,
                mastery=mastery,
                allocated_node_ids=passive_tree,
                nodes=nodes,
                all_gear=gear,
                passive_stats=passive_stats,
            )
            if result is not None:
                evaluated.append(result)

        # Sort by efficiency
        evaluated.sort(key=lambda c: c.efficiency_score, reverse=True)
        top = evaluated[:top_n_per_slot]
        for i, c in enumerate(top):
            c.rank = i + 1

        slot_results.append(SlotUpgradeResult(slot=slot, candidates=top))
        all_candidates.extend(top)

    # Overall top-10
    all_candidates.sort(key=lambda c: c.efficiency_score, reverse=True)
    top_overall = all_candidates[:top_n_overall]
    for i, c in enumerate(top_overall):
        c.rank = i + 1

    elapsed = time.perf_counter() - t_start
    log.info(
        "gear_upgrade_ranker.done",
        slots=len(slot_results),
        total_candidates=len(all_candidates),
        elapsed=round(elapsed, 4),
    )

    return GearUpgradeResult(
        slots=slot_results,
        top_10_overall=top_overall,
        execution_time=elapsed,
    )
