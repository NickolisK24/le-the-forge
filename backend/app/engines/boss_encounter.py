"""
Boss Encounter Simulator — Phase 7 Engine

Simulates a build fighting a boss with multiple phases. Each phase has its own
health pool, resistance profile, armor, and optional mechanics (immunity windows,
damage reduction).

Pipeline:
    Build → stat_engine → per-phase combat_engine + defense_engine → phase results → summary

Supports enrage timers: if total TTK exceeds enrage_time, the result flags it.

Pure module — no DB, no HTTP.
"""

from __future__ import annotations

import time
from copy import copy as _copy
from dataclasses import dataclass, field
from typing import Optional

from app.engines.stat_engine import BuildStats
from app.engines.combat_engine import calculate_dps
from app.engines.defense_engine import calculate_defense
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


# ---------------------------------------------------------------------------
# Boss profile helpers
# ---------------------------------------------------------------------------

# Default phase when boss data has no explicit phases — treat the entire
# boss as a single-phase encounter.
_DEFAULT_PHASE = {
    "phase": 1,
    "health_threshold": 1.0,
    "resistances": None,  # inherit from boss top-level
    "armor": None,        # inherit from boss top-level
    "immunity": False,
    "damage_reduction": 0.0,
}


def _build_phases(boss: dict) -> list[dict]:
    """Normalize boss profile into a list of ordered phases.

    If the boss profile defines ``phases``, use them directly.
    Otherwise synthesize a single-phase encounter from top-level stats.
    """
    raw_phases = boss.get("phases")
    if raw_phases and isinstance(raw_phases, list) and len(raw_phases) > 0:
        phases = []
        for i, p in enumerate(raw_phases):
            phases.append({
                "phase": p.get("phase", i + 1),
                "health_threshold": float(p.get("health_threshold", 1.0)),
                "resistances": p.get("resistances") or boss.get("resistances", {}),
                "armor": p.get("armor") if p.get("armor") is not None else boss.get("armor", 0),
                "immunity": bool(p.get("immunity", False)),
                "damage_reduction": float(p.get("damage_reduction", 0.0)),
            })
        # Sort by health_threshold descending (phase 1 = full HP)
        phases.sort(key=lambda x: x["health_threshold"], reverse=True)
        return phases

    # Single-phase fallback
    return [{
        "phase": 1,
        "health_threshold": 1.0,
        "resistances": boss.get("resistances", {}),
        "armor": boss.get("armor", 0),
        "immunity": False,
        "damage_reduction": 0.0,
    }]


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class PhaseResult:
    phase: int
    health_threshold: float
    dps: float
    ttk_seconds: float
    survival_score: int
    mana_sustainable: bool
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "phase": self.phase,
            "health_threshold": self.health_threshold,
            "dps": round(self.dps),
            "ttk_seconds": round(self.ttk_seconds, 1),
            "survival_score": self.survival_score,
            "mana_sustainable": self.mana_sustainable,
            "warnings": self.warnings,
        }


@dataclass
class BossSummary:
    total_ttk_seconds: float
    can_kill_before_enrage: bool
    overall_survival_score: int
    weakest_phase: int

    def to_dict(self) -> dict:
        return {
            "total_ttk_seconds": round(self.total_ttk_seconds, 1),
            "can_kill_before_enrage": self.can_kill_before_enrage,
            "overall_survival_score": self.overall_survival_score,
            "weakest_phase": self.weakest_phase,
        }


@dataclass
class BossEncounterResult:
    boss_id: str
    boss_name: str
    corruption: int
    phases: list[PhaseResult]
    summary: BossSummary
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "boss_id": self.boss_id,
            "boss_name": self.boss_name,
            "corruption": self.corruption,
            "phases": [p.to_dict() for p in self.phases],
            "summary": self.summary.to_dict(),
            "warnings": self.warnings,
        }


# ---------------------------------------------------------------------------
# Per-phase DPS calculation
# ---------------------------------------------------------------------------

def _phase_dps(
    stats: BuildStats,
    phase: dict,
    primary_skill: str,
    skill_level: int,
) -> float:
    """Calculate effective DPS against a phase's defenses."""
    if phase.get("immunity"):
        return 0.0

    resistances = phase.get("resistances", {})
    armor = float(phase.get("armor", 0))
    damage_reduction = float(phase.get("damage_reduction", 0.0))

    # Get raw DPS from combat engine
    dps_result = calculate_dps(stats, primary_skill, skill_level)
    raw_dps = float(dps_result.total_dps)

    # Apply enemy armor mitigation: armor / (armor + 1000)
    armor_mit = armor / (armor + 1000.0) if armor > 0 else 0.0
    armor_factor = 1.0 - min(0.80, armor_mit)

    # Apply resistance — use lowest resistance (build targets weakest)
    res_values = [
        float(resistances.get("fire", 0)),
        float(resistances.get("cold", 0)),
        float(resistances.get("lightning", 0)),
        float(resistances.get("physical", 0)),
        float(resistances.get("void", 0)),
        float(resistances.get("necrotic", 0)),
    ]
    best_res = min(res_values) if res_values else 0.0
    res_factor = 1.0 - min(75.0, max(0.0, best_res)) / 100.0

    # Apply phase-specific damage reduction
    dr_factor = 1.0 - min(1.0, max(0.0, damage_reduction / 100.0))

    return raw_dps * armor_factor * res_factor * dr_factor


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def simulate_boss_encounter(
    stats: BuildStats,
    boss: dict,
    primary_skill: str,
    skill_level: int = 20,
    corruption: int = 0,
    health_multiplier: float = 1.0,
    damage_multiplier: float = 1.0,
) -> BossEncounterResult:
    """Run a full boss encounter simulation across all phases.

    Args:
        stats: Fully resolved BuildStats.
        boss: Boss profile dict from enemy_profiles.json or enhanced with phases.
        primary_skill: Build's primary damage skill.
        skill_level: Level of the primary skill.
        corruption: Corruption level (0-500). Scales enemy HP and damage.
        health_multiplier: Additional multiplier for boss HP (from corruption).
        damage_multiplier: Additional multiplier for boss damage (from corruption).

    Returns:
        BossEncounterResult with per-phase results and overall summary.
    """
    t_start = time.perf_counter()

    boss_id = boss.get("id", "unknown")
    boss_name = boss.get("name", "Unknown Boss")
    boss_hp = float(boss.get("health", 100_000)) * health_multiplier
    enrage_time = boss.get("enrage_time")  # seconds, or None

    phases = _build_phases(boss)
    warnings: list[str] = []

    # Detect missing fields
    if not boss.get("resistances"):
        warnings.append("Boss has no resistance data — using 0 for all")
    if not boss.get("armor") and boss.get("armor") != 0:
        warnings.append("Boss has no armor data — using 0")

    # Calculate defense/survival against the boss
    defense = calculate_defense(stats)
    base_survival_score = defense.survivability_score

    # Adjust survival score for enemy damage multiplier
    if damage_multiplier > 1.0:
        # Higher boss damage reduces survivability
        survival_adj = max(0, int(base_survival_score / damage_multiplier))
    else:
        survival_adj = base_survival_score

    # Mana sustainability check
    mana_regen = getattr(stats, 'mana_regen', 0.0)
    mana_sustainable = mana_regen >= 5.0  # basic threshold

    # Simulate each phase
    phase_results: list[PhaseResult] = []
    total_ttk = 0.0
    weakest_phase = 1
    min_survival = 999

    for i, phase in enumerate(phases):
        phase_warnings: list[str] = []

        if phase.get("immunity"):
            # Immunity phase — no damage, fixed duration
            immunity_duration = float(phase.get("immunity_duration", 5.0))
            phase_results.append(PhaseResult(
                phase=phase["phase"],
                health_threshold=phase["health_threshold"],
                dps=0,
                ttk_seconds=immunity_duration,
                survival_score=survival_adj,
                mana_sustainable=mana_sustainable,
                warnings=["Immunity phase — zero damage window"],
            ))
            total_ttk += immunity_duration
            continue

        # Calculate DPS against this phase's defenses
        dps = _phase_dps(stats, phase, primary_skill, skill_level)

        # Calculate HP for this phase
        if i + 1 < len(phases):
            next_threshold = phases[i + 1]["health_threshold"]
        else:
            next_threshold = 0.0
        phase_hp = boss_hp * (phase["health_threshold"] - next_threshold)

        # TTK for this phase
        if dps > 0:
            ttk = phase_hp / dps
        else:
            ttk = float("inf")
            phase_warnings.append("Zero DPS in this phase")

        # Phase-specific survival score (some phases may be harder)
        phase_survival = survival_adj
        if phase.get("damage_reduction", 0) > 0:
            phase_warnings.append(
                f"Boss has {phase['damage_reduction']}% damage reduction in this phase"
            )

        if phase_survival < min_survival:
            min_survival = phase_survival
            weakest_phase = phase["phase"]

        phase_results.append(PhaseResult(
            phase=phase["phase"],
            health_threshold=phase["health_threshold"],
            dps=dps,
            ttk_seconds=ttk,
            survival_score=phase_survival,
            mana_sustainable=mana_sustainable,
            warnings=phase_warnings,
        ))
        total_ttk += ttk

    # Enrage check
    can_kill = True
    if enrage_time is not None:
        enrage_time = float(enrage_time)
        if total_ttk > enrage_time:
            can_kill = False
            warnings.append(
                f"Build cannot kill boss before enrage ({round(total_ttk, 1)}s > {enrage_time}s)"
            )

    overall_survival = min(
        pr.survival_score for pr in phase_results
    ) if phase_results else 0

    elapsed = time.perf_counter() - t_start
    log.info(
        "boss_encounter.done",
        boss_id=boss_id,
        corruption=corruption,
        total_ttk=round(total_ttk, 1),
        enrage=can_kill,
        elapsed=round(elapsed, 4),
    )

    return BossEncounterResult(
        boss_id=boss_id,
        boss_name=boss_name,
        corruption=corruption,
        phases=phase_results,
        summary=BossSummary(
            total_ttk_seconds=total_ttk,
            can_kill_before_enrage=can_kill,
            overall_survival_score=overall_survival,
            weakest_phase=weakest_phase,
        ),
        warnings=warnings,
    )
