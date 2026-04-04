"""
F2 — Build Variant Generator

Generates controlled mutations from a base BuildDefinition.
All randomness uses a seeded random.Random instance so the same
(base_build, config) pair always produces the same variant list.

Mutation types
--------------
affix_tier_bump   — increase or decrease an existing affix tier by 1
affix_swap        — replace a random gear affix with a different one
affix_add         — add a new affix to a random gear slot
passive_toggle    — add or remove one passive node ID
buff_toggle       — add or remove one preset buff
"""

from __future__ import annotations
import copy
import hashlib
import json
import random as _random_module
from typing import Callable

from builds.build_definition import BuildDefinition
from builds.gear_system      import GearItem, GearAffix
from builds.buff_system      import Buff
from optimization.models.optimization_config import OptimizationConfig

# ---------------------------------------------------------------------------
# Available affix pool (lazy-loaded)
# ---------------------------------------------------------------------------

_AFFIX_POOL: list[tuple[str, list[int]]] | None = None  # [(name, [tier_ints]), ...]


def _get_affix_pool() -> list[tuple[str, list[int]]]:
    global _AFFIX_POOL
    if _AFFIX_POOL is None:
        from app.game_data.game_data_loader import get_all_affixes
        pool = []
        for a in get_all_affixes():
            tiers = sorted(int(t["tier"]) for t in a.get("tiers", []) if "tier" in t)
            if tiers:
                pool.append((a["name"], tiers))
        _AFFIX_POOL = pool
    return _AFFIX_POOL


# ---------------------------------------------------------------------------
# Preset buffs available for buff_toggle mutations
# ---------------------------------------------------------------------------

_PRESET_BUFFS = [
    Buff("frenzy",      {"base_damage": 50.0},         duration=None),
    Buff("conviction",  {"crit_chance": 0.10},          duration=None),
    Buff("power_surge", {"spell_damage_pct": 30.0},     duration=10.0),
    Buff("exposure",    {"physical_damage_pct": 25.0},  duration=None),
]

# ---------------------------------------------------------------------------
# Individual mutation functions
# ---------------------------------------------------------------------------

def _affix_tier_bump(build: BuildDefinition, rng: _random_module.Random) -> tuple[BuildDefinition, str]:
    """Increase or decrease a random existing affix tier by 1."""
    items_with_affixes = [g for g in build.gear if g.affixes]
    if not items_with_affixes:
        return build, "no_op:no_affixed_gear"
    item  = rng.choice(items_with_affixes)
    affix = rng.choice(item.affixes)

    pool  = _get_affix_pool()
    pool_entry = next((p for p in pool if p[0] == affix.name), None)
    max_tier = max(pool_entry[1]) if pool_entry else 7
    min_tier = min(pool_entry[1]) if pool_entry else 1

    delta    = rng.choice([-1, 1])
    new_tier = max(min_tier, min(max_tier, affix.tier + delta))
    if new_tier == affix.tier:
        return build, "no_op:tier_at_boundary"

    new_affixes = [
        GearAffix(a.name, new_tier if a is affix else a.tier)
        for a in item.affixes
    ]
    new_item  = GearItem(slot=item.slot, affixes=new_affixes, rarity=item.rarity)
    b2 = copy.deepcopy(build)
    b2.add_gear(new_item)
    return b2, f"tier_bump:{item.slot}:{affix.name}:{affix.tier}→{new_tier}"


def _affix_swap(build: BuildDefinition, rng: _random_module.Random) -> tuple[BuildDefinition, str]:
    """Replace a random gear affix with a different one from the pool."""
    items_with_affixes = [g for g in build.gear if g.affixes]
    if not items_with_affixes:
        return build, "no_op:no_affixed_gear"
    pool = _get_affix_pool()
    if not pool:
        return build, "no_op:empty_affix_pool"

    item     = rng.choice(items_with_affixes)
    idx      = rng.randrange(len(item.affixes))
    new_name, new_tiers = rng.choice(pool)
    new_tier = rng.choice(new_tiers)
    old_name = item.affixes[idx].name

    new_affixes = list(item.affixes)
    new_affixes[idx] = GearAffix(new_name, new_tier)
    new_item = GearItem(slot=item.slot, affixes=new_affixes, rarity=item.rarity)
    b2 = copy.deepcopy(build)
    b2.add_gear(new_item)
    return b2, f"affix_swap:{item.slot}:{old_name}→{new_name}(T{new_tier})"


def _affix_add(build: BuildDefinition, rng: _random_module.Random) -> tuple[BuildDefinition, str]:
    """Add a new affix to a random gear slot (max 6 affixes per item)."""
    from builds.gear_system import VALID_SLOTS
    pool = _get_affix_pool()
    if not pool:
        return build, "no_op:empty_affix_pool"

    slot = rng.choice(list(VALID_SLOTS))
    item = build.get_gear(slot) or GearItem(slot=slot)
    if len(item.affixes) >= 6:
        return build, "no_op:slot_full"

    new_name, new_tiers = rng.choice(pool)
    new_tier = rng.choice(new_tiers)
    new_affixes = list(item.affixes) + [GearAffix(new_name, new_tier)]
    new_item = GearItem(slot=slot, affixes=new_affixes, rarity=item.rarity)
    b2 = copy.deepcopy(build)
    b2.add_gear(new_item)
    return b2, f"affix_add:{slot}:{new_name}(T{new_tier})"


def _passive_toggle(build: BuildDefinition, rng: _random_module.Random) -> tuple[BuildDefinition, str]:
    """Add or remove a passive node ID."""
    b2 = copy.deepcopy(build)
    if b2.passive_ids and rng.random() < 0.5:
        nid = rng.choice(b2.passive_ids)
        b2.remove_passive(nid)
        return b2, f"passive_remove:{nid}"
    else:
        nid = rng.randint(1, 500)
        b2.add_passive(nid)
        return b2, f"passive_add:{nid}"


def _buff_toggle(build: BuildDefinition, rng: _random_module.Random) -> tuple[BuildDefinition, str]:
    """Add or remove a preset buff."""
    b2 = copy.deepcopy(build)
    active_ids = {b.buff_id for b in b2.buffs}
    preset = rng.choice(_PRESET_BUFFS)
    if preset.buff_id in active_ids:
        b2.remove_buff(preset.buff_id)
        return b2, f"buff_remove:{preset.buff_id}"
    else:
        b2.add_buff(copy.deepcopy(preset))
        return b2, f"buff_add:{preset.buff_id}"


_MUTATION_FUNCTIONS: list[Callable] = [
    _affix_tier_bump,
    _affix_swap,
    _affix_add,
    _passive_toggle,
    _buff_toggle,
]


# ---------------------------------------------------------------------------
# Build fingerprint (for uniqueness checking)
# ---------------------------------------------------------------------------

def _fingerprint(build: BuildDefinition) -> str:
    d = build.to_dict()
    # Remove metadata (name/version doesn't affect simulation)
    d.pop("metadata", None)
    return hashlib.md5(
        json.dumps(d, sort_keys=True, default=str).encode()
    ).hexdigest()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class VariantGenerator:
    """
    Generates up to `config.max_variants` unique mutated variants of a base build.

    Each variant is produced by applying `config.mutation_depth` independent
    mutations chosen at random.  The seeded RNG ensures reproducibility.
    """

    def __init__(self, config: OptimizationConfig) -> None:
        self._config = config

    def generate(self, base_build: BuildDefinition) -> list[tuple[BuildDefinition, list[str]]]:
        """
        Return a list of (variant, mutations_applied) tuples.

        The base build itself is NOT included.  Duplicate variants (identical
        fingerprint) are silently skipped.  Always-failing mutations are treated
        as no-ops and still consume a mutation slot.

        Returns at most config.max_variants variants.
        """
        rng   = _random_module.Random(self._config.random_seed)
        seen  = {_fingerprint(base_build)}
        variants: list[tuple[BuildDefinition, list[str]]] = []

        # Allow up to 3× max_variants attempts to fill the quota
        max_attempts = self._config.max_variants * 3
        attempts = 0

        while len(variants) < self._config.max_variants and attempts < max_attempts:
            attempts += 1
            candidate = base_build
            applied: list[str] = []

            for _ in range(self._config.mutation_depth):
                fn = rng.choice(_MUTATION_FUNCTIONS)
                candidate, label = fn(candidate, rng)
                applied.append(label)

            fp = _fingerprint(candidate)
            if fp not in seen:
                seen.add(fp)
                variants.append((candidate, applied))

        return variants
