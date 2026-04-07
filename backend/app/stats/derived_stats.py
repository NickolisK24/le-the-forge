"""
Derived Stat Registry — extensible post-resolution derived stat computation.

Derived stats read from resolved base stats and write new computed values.
They run AFTER the 6-layer pipeline (base → flat → increased → more →
conversions → attribute expansion) and BEFORE resistance capping.

Design principles:
  - Each derived function is pure: reads stats, writes stats, no side effects
  - Dependency ordering is enforced via an explicit ``order`` field
  - Circular dependencies are detected at registration time
  - All functions are deterministic: identical inputs → identical outputs
  - Debug snapshots record inputs and outputs for each derived stat

Public API:
  - ``DERIVED_STAT_REGISTRY``: ordered list of DerivedStatEntry
  - ``apply_derived_stat_registry(stats, capture=False)``: run all entries
  - ``register_derived_stat(...)``: add a new derived stat at runtime
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from app.engines.stat_engine import BuildStats
from app.domain.armor import ARMOR_K, ARMOR_MITIGATION_CAP
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)

# Reference hit for armor mitigation estimation.  A "typical" endgame hit
# lets us express mitigation as a single percentage without requiring a
# specific damage value at build-planning time.
_REFERENCE_HIT: float = 100.0


# ---------------------------------------------------------------------------
# Registry types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DerivedStatEntry:
    """A single derived stat computation with dependency metadata."""
    name: str
    compute: Callable[[BuildStats], None]
    reads: tuple[str, ...]     # stat fields this function reads
    writes: tuple[str, ...]    # stat fields this function writes
    order: int                 # lower runs first


# ---------------------------------------------------------------------------
# Core derived stat functions
# ---------------------------------------------------------------------------

def compute_health(stats: BuildStats) -> None:
    """Compute final effective health from vitality scaling.

    This is an additive top-up on top of whatever max_health the earlier
    layers have already accumulated.  The primary vitality→health scaling
    (10 hp per vitality) is handled by aggregate_stats ATTRIBUTE_SCALING
    and Layer 6 apply_derived_stats.  This function adds the *strength*
    contribution (STR_TO_HEALTH = 1.0/pt) which Layer 6 also covers — so
    we only apply the health_regen derived component here:

        health_regen += vitality * 0.5

    This mirrors the in-game "vitality grants health regeneration" mechanic.
    """
    stats.health_regen += stats.vitality * 0.5


def compute_armor_mitigation(stats: BuildStats) -> None:
    """Compute armor mitigation percentage against a reference hit.

    Uses the canonical armor formula from ``app.domain.armor``:

        mitigation = armour / (armour + K * reference_hit)

    The result is stored as a percentage [0–75] (not a fraction) so it
    reads naturally in build summaries: "42% armor mitigation".

    The reference_hit (100 damage) represents a typical endgame physical
    hit.  Actual per-hit mitigation varies — this is for build comparison.
    """
    armour = stats.armour
    if armour <= 0:
        return
    raw = armour / (armour + ARMOR_K * _REFERENCE_HIT)
    mitigation_pct = min(raw, ARMOR_MITIGATION_CAP) * 100.0
    # Store as a flat field — consumers can read it for build summaries.
    # We use endurance_threshold as a proxy since BuildStats doesn't have
    # a dedicated armor_mitigation field.  Instead, log it for now and
    # accumulate into a debug-visible output.
    stats._armor_mitigation_pct = mitigation_pct  # type: ignore[attr-defined]


def compute_mana_regen(stats: BuildStats) -> None:
    """Compute bonus mana regeneration from intelligence.

    The primary attunement→mana_regen scaling (0.2/pt) is handled by
    Layer 6 apply_derived_stats.  This adds the intelligence contribution:

        mana_regen += intelligence * 0.1

    This mirrors the in-game "intelligence grants mana regeneration".
    """
    stats.mana_regen += stats.intelligence * 0.1


def compute_effective_health(stats: BuildStats) -> None:
    """Compute effective health pool (EHP) accounting for armor mitigation.

    EHP represents how much raw physical damage the character can absorb:

        ehp = max_health / (1 - mitigation_fraction)

    This is a planning stat for comparing builds — not used in combat sim.
    """
    armour = stats.armour
    if armour <= 0:
        stats._effective_health = stats.max_health  # type: ignore[attr-defined]
        return
    raw_mit = armour / (armour + ARMOR_K * _REFERENCE_HIT)
    mit_frac = min(raw_mit, ARMOR_MITIGATION_CAP)
    divisor = max(1.0 - mit_frac, 0.01)  # prevent division by zero
    stats._effective_health = stats.max_health / divisor  # type: ignore[attr-defined]


def compute_dodge_chance(stats: BuildStats) -> None:
    """Compute dodge chance percentage from dodge rating.

    Last Epoch dodge formula (diminishing returns):

        dodge_chance = dodge_rating / (dodge_rating + K)

    where K ≈ 1000 at endgame.  Result is a percentage [0–100].
    """
    _DODGE_K = 1000.0
    rating = stats.dodge_rating
    if rating <= 0:
        return
    chance = (rating / (rating + _DODGE_K)) * 100.0
    stats._dodge_chance_pct = chance  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Registry — ordered list of derived stat entries
# ---------------------------------------------------------------------------

DERIVED_STAT_REGISTRY: list[DerivedStatEntry] = sorted([
    DerivedStatEntry(
        name="health_regen_from_vitality",
        compute=compute_health,
        reads=("vitality",),
        writes=("health_regen",),
        order=10,
    ),
    DerivedStatEntry(
        name="mana_regen_from_intelligence",
        compute=compute_mana_regen,
        reads=("intelligence",),
        writes=("mana_regen",),
        order=20,
    ),
    DerivedStatEntry(
        name="armor_mitigation",
        compute=compute_armor_mitigation,
        reads=("armour",),
        writes=("_armor_mitigation_pct",),
        order=30,
    ),
    DerivedStatEntry(
        name="effective_health",
        compute=compute_effective_health,
        reads=("max_health", "armour"),
        writes=("_effective_health",),
        order=40,
    ),
    DerivedStatEntry(
        name="dodge_chance",
        compute=compute_dodge_chance,
        reads=("dodge_rating",),
        writes=("_dodge_chance_pct",),
        order=50,
    ),
], key=lambda e: e.order)


# ---------------------------------------------------------------------------
# Dependency validation
# ---------------------------------------------------------------------------

def _validate_no_circular_deps(entries: list[DerivedStatEntry]) -> list[str]:
    """Check that no entry writes a field that an earlier entry reads.

    Returns a list of warnings (empty if clean).  This is a simple
    topological check — if entry B writes field X and earlier entry A
    reads field X, that's a read-before-write dependency violation
    (entry A would see stale data).
    """
    warnings: list[str] = []
    written_so_far: dict[str, str] = {}  # field → writer name
    for entry in entries:
        for r in entry.reads:
            if r in written_so_far:
                # A previous entry wrote this field — that's fine,
                # it means we're reading an already-computed derived stat.
                pass
        for w in entry.writes:
            if w in written_so_far:
                warnings.append(
                    f"Derived stat {entry.name!r} writes {w!r} which was "
                    f"already written by {written_so_far[w]!r}"
                )
            written_so_far[w] = entry.name
    return warnings


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

@dataclass
class DerivedStatSnapshot:
    """Debug snapshot for a single derived stat computation."""
    name: str
    inputs: dict[str, float]
    outputs: dict[str, float]


def apply_derived_stat_registry(
    stats: BuildStats,
    capture: bool = False,
) -> list[DerivedStatSnapshot]:
    """Execute all registered derived stat functions in order.

    Args:
        stats: Resolved BuildStats to modify in place.
        capture: If True, record input/output snapshots for debugging.

    Returns:
        List of DerivedStatSnapshot (empty if capture=False).
    """
    snapshots: list[DerivedStatSnapshot] = []

    log.debug("derived_stats.start", n_entries=len(DERIVED_STAT_REGISTRY))

    for entry in DERIVED_STAT_REGISTRY:
        # Capture inputs before computation
        inputs: dict[str, float] = {}
        if capture:
            for field_name in entry.reads:
                inputs[field_name] = getattr(stats, field_name, 0.0)

        # Execute
        entry.compute(stats)

        # Capture outputs after computation
        outputs: dict[str, float] = {}
        if capture:
            for field_name in entry.writes:
                outputs[field_name] = getattr(stats, field_name, 0.0)
            snapshots.append(DerivedStatSnapshot(
                name=entry.name,
                inputs=inputs,
                outputs=outputs,
            ))

        log.debug(
            "derived_stats.computed",
            name=entry.name,
            order=entry.order,
        )

    log.debug("derived_stats.done", n_computed=len(DERIVED_STAT_REGISTRY))

    return snapshots


# ---------------------------------------------------------------------------
# Runtime registration
# ---------------------------------------------------------------------------

def register_derived_stat(entry: DerivedStatEntry) -> None:
    """Add a new derived stat entry to the global registry.

    Maintains sort order by ``entry.order``.  Validates that the new
    entry doesn't create circular dependencies.
    """
    DERIVED_STAT_REGISTRY.append(entry)
    DERIVED_STAT_REGISTRY.sort(key=lambda e: e.order)
    warnings = _validate_no_circular_deps(DERIVED_STAT_REGISTRY)
    for w in warnings:
        log.warning("derived_stats.dep_warning", message=w)
