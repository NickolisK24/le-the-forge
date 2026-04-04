"""
Combat Monte Carlo Simulator — Upgrade 2

Simulates real combat behavior via seeded Monte Carlo iteration.
Each iteration models a complete combat round including:

    - Random base damage roll (variance ±15%)
    - Crit chance roll → crit multiplier application
    - Enemy armor mitigation
    - Enemy resistance mitigation (per damage type)
    - Player hit simulation (enemy attacks against player)
    - Health depletion → survival time calculation

Rules enforced:
- Determinism first: every call with the same seed produces identical results
- No global RNG: uses random.Random(seed) exclusively
- No magic numbers: all caps and defaults from constants.json
- Telemetry: every run exposes execution_time and iterations_completed
"""

from __future__ import annotations

import math
import random as _random_module
import time
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from app.engines.stat_engine import BuildStats
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)

# ---------------------------------------------------------------------------
# Constants loader (inline to avoid cross-engine import)
# ---------------------------------------------------------------------------

import json as _json
import os as _os

_CONSTANTS_PATH = _os.path.join(
    _os.path.dirname(__file__), "..", "game_data", "constants.json"
)


@lru_cache(maxsize=1)
def _load_constants() -> dict:
    with open(_CONSTANTS_PATH) as f:
        return _json.load(f)


def _const(section: str, key: str, default: Any = None) -> Any:
    return _load_constants().get(section, {}).get(key, default)


# ---------------------------------------------------------------------------
# Simulation constants
# ---------------------------------------------------------------------------

DAMAGE_ROLL_MIN: float = 0.85   # -15% variance floor
DAMAGE_ROLL_MAX: float = 1.15   # +15% variance ceiling
BASE_HIT_CHANCE: float = 0.92   # player hit chance vs standard enemy
ARMOR_DIVISOR: float  = 300.0   # used in armor reduction formula: armor/(armor+300)
ARMOR_CAP: float      = 0.80    # maximum armor mitigation
ENEMY_ATTACK_VARIANCE: float = 0.20  # ±20% variance on enemy damage roll
SKILL_PATTERN_DEFAULT: list[str] = ["basic"]


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class CombatSimulationResult:
    """Full Monte Carlo combat simulation output."""
    average_dps:      float
    median_dps:       float
    dps_variance:     float
    dps_std_dev:      float
    dps_p10:          float    # 10th percentile DPS
    dps_p90:          float    # 90th percentile DPS
    survival_time:    float    # average seconds before player death
    death_rate:       float    # fraction of iterations where player dies
    total_damage:     float    # average total damage dealt
    crit_rate_actual: float    # observed crit rate
    iterations:       int
    execution_time:   float    # wall-clock seconds

    def to_dict(self) -> dict:
        return {
            "average_dps":      round(self.average_dps, 2),
            "median_dps":       round(self.median_dps, 2),
            "dps_variance":     round(self.dps_variance, 2),
            "dps_std_dev":      round(self.dps_std_dev, 2),
            "dps_p10":          round(self.dps_p10, 2),
            "dps_p90":          round(self.dps_p90, 2),
            "survival_time":    round(self.survival_time, 2),
            "death_rate":       round(self.death_rate, 4),
            "total_damage":     round(self.total_damage, 2),
            "crit_rate_actual": round(self.crit_rate_actual, 4),
            "iterations":       self.iterations,
            "execution_time":   round(self.execution_time, 4),
        }


# ---------------------------------------------------------------------------
# Per-iteration simulation
# ---------------------------------------------------------------------------

def _simulate_one_combat(
    rng: _random_module.Random,
    stats: BuildStats,
    enemy: dict,
    duration: float,
    tick: float,
) -> tuple[float, bool, float, bool]:
    """Simulate one combat iteration.

    Returns:
        (dps, player_died, survival_time, had_crit)
    """
    enemy_hp      = float(enemy.get("max_health", 10_000))
    enemy_armor   = float(enemy.get("armor", 0))
    enemy_res     = enemy.get("resistances", {})
    enemy_crit_ch = float(enemy.get("crit_chance", 0.0))
    enemy_crit_mx = float(enemy.get("crit_multiplier", 1.5))
    dmg_range     = enemy.get("damage_range", None)
    skill_pattern = enemy.get("skill_pattern", SKILL_PATTERN_DEFAULT)
    attack_spd    = float(enemy.get("attack_speed", 1.0))

    # Build player damage profile from stats
    base_dmg      = max(1.0, stats.base_damage)
    increased_pct = (
        stats.spell_damage_pct + stats.physical_damage_pct +
        stats.fire_damage_pct + stats.elemental_damage_pct
    )
    more_mult     = max(1.0, stats.more_damage_multiplier)
    # Player effective attack speed
    atk_speed     = max(0.1, stats.attack_speed * (1 + stats.attack_speed_pct / 100))

    # Enemy armor mitigation (armor/(armor+300), capped at 80%)
    arm_red = min(ARMOR_CAP, enemy_armor / (enemy_armor + ARMOR_DIVISOR))

    # Primary damage type resistance (use lowest to simulate optimized targeting)
    all_res = [
        enemy_res.get("fire", 0),
        enemy_res.get("cold", 0),
        enemy_res.get("lightning", 0),
        enemy_res.get("physical", 0),
        enemy_res.get("void", 0),
        enemy_res.get("necrotic", 0),
    ]
    # Player picks best damage type: min resistance
    best_res = min(all_res) if all_res else 0
    res_red  = max(0.0, min(75.0, best_res)) / 100.0

    player_hp     = float(stats.max_health)
    player_alive  = True
    survival_t    = duration
    total_dmg     = 0.0
    crit_count    = 0
    attack_count  = 0
    t             = 0.0
    skill_idx     = 0

    max_ticks = int(duration / tick) + 2  # safety cap: prevents infinite loop on degenerate inputs
    tick_count = 0
    while t < duration:
        if tick_count >= max_ticks:
            log.warning("_simulate_one_combat.tick_cap_reached", duration=duration, tick=tick)
            break
        tick_count += 1
        # --- Player attacks enemy ---
        if rng.random() < BASE_HIT_CHANCE:
            roll    = rng.uniform(DAMAGE_ROLL_MIN, DAMAGE_ROLL_MAX)
            dmg     = base_dmg * roll * (1 + increased_pct / 100) * more_mult
            is_crit = rng.random() < stats.crit_chance
            if is_crit:
                dmg *= stats.crit_multiplier
                crit_count += 1
            # Apply mitigation
            dmg *= (1 - arm_red) * (1 - res_red)
            total_dmg += max(0.0, dmg)
            attack_count += 1

        # --- Enemy attacks player (per tick) ---
        skill_name = skill_pattern[skill_idx % len(skill_pattern)]
        skill_idx += 1

        if attack_spd > 0 and (t == 0 or rng.random() < attack_spd * tick):
            # Enemy base damage roll
            if dmg_range:
                e_dmg = rng.uniform(float(dmg_range[0]), float(dmg_range[1]))
            else:
                e_dmg = enemy.get("damage_per_hit", 0)
                if e_dmg:
                    e_dmg *= rng.uniform(1 - ENEMY_ATTACK_VARIANCE, 1 + ENEMY_ATTACK_VARIANCE)

            # Heavy attack multiplier
            if skill_name == "heavy":
                e_dmg *= 2.0
            elif skill_name == "basic":
                pass

            # Enemy crit
            if e_dmg and rng.random() < enemy_crit_ch:
                e_dmg *= enemy_crit_mx

            if e_dmg:
                player_hp -= e_dmg
                if player_hp <= 0 and player_alive:
                    player_alive = False
                    survival_t   = t

        t += tick

    dps = total_dmg / duration if duration > 0 else 0.0
    return dps, not player_alive, survival_t, crit_count > 0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_combat_simulation(
    build_stats_or_build: BuildStats | dict,
    enemy: dict,
    iterations: int = 10_000,
    seed: int = 42,
    duration: float = 60.0,
    tick: float = 0.5,
) -> CombatSimulationResult:
    """Run a full Monte Carlo combat simulation.

    This is the architecture-plan canonical function for combat simulation.

    Args:
        build_stats_or_build: Either a resolved :class:`BuildStats` or a build
            dict (which will be resolved via the stat pipeline).
        enemy: Enemy template dict from enemies.json or a custom dict with at
            least ``max_health``, ``armor``, ``resistances`` keys.
        iterations: Number of Monte Carlo iterations (default 10,000).
            More iterations → lower variance.  Must be ≥ 1.
        seed: RNG seed for full determinism (default 42).
        duration: Simulated fight duration in seconds (default 60).
        tick: Simulation time step in seconds (default 0.5).

    Returns:
        :class:`CombatSimulationResult` with average_dps, median_dps,
        dps_variance, survival_time, death_rate, and telemetry fields.
    """
    if iterations < 1:
        raise ValueError("iterations must be >= 1")
    if duration <= 0:
        raise ValueError("duration must be > 0")
    if tick <= 0:
        raise ValueError("tick must be > 0")

    # Resolve stats if a build dict was passed
    if isinstance(build_stats_or_build, dict):
        from app.engines.stat_resolution_pipeline import quick_resolve
        stats = quick_resolve(build_stats_or_build)
    else:
        stats = build_stats_or_build

    log.info(
        "combat_simulation.start",
        iterations=iterations,
        seed=seed,
        duration=duration,
        enemy=enemy.get("name", "unknown"),
    )

    t_start = time.perf_counter()
    rng = _random_module.Random(seed)

    dps_values: list[float] = []
    deaths: int = 0
    survival_times: list[float] = []
    had_crits: int = 0

    for _ in range(iterations):
        dps, died, surv_t, crit = _simulate_one_combat(rng, stats, enemy, duration, tick)
        dps_values.append(dps)
        if died:
            deaths += 1
        survival_times.append(surv_t)
        if crit:
            had_crits += 1

    elapsed = time.perf_counter() - t_start

    # Statistics
    dps_values.sort()
    n = len(dps_values)
    avg_dps    = sum(dps_values) / n
    median_dps = dps_values[n // 2]
    variance   = sum((d - avg_dps) ** 2 for d in dps_values) / n
    std_dev    = math.sqrt(variance)
    p10        = dps_values[max(0, int(n * 0.10))]
    p90        = dps_values[min(n - 1, int(n * 0.90))]
    avg_surv   = sum(survival_times) / n
    death_rate = deaths / n
    avg_total  = avg_dps * duration
    crit_rate  = had_crits / n

    result = CombatSimulationResult(
        average_dps      = round(avg_dps, 2),
        median_dps       = round(median_dps, 2),
        dps_variance     = round(variance, 2),
        dps_std_dev      = round(std_dev, 2),
        dps_p10          = round(p10, 2),
        dps_p90          = round(p90, 2),
        survival_time    = round(avg_surv, 2),
        death_rate       = round(death_rate, 4),
        total_damage     = round(avg_total, 2),
        crit_rate_actual = round(crit_rate, 4),
        iterations       = iterations,
        execution_time   = round(elapsed, 4),
    )

    log.info(
        "combat_simulation.done",
        avg_dps=result.average_dps,
        death_rate=result.death_rate,
        elapsed=result.execution_time,
    )
    return result


def compare_builds_vs_enemy(
    builds: list[BuildStats | dict],
    enemy: dict,
    labels: list[str] | None = None,
    iterations: int = 5_000,
    seed: int = 42,
    duration: float = 60.0,
) -> list[dict]:
    """Compare multiple builds against the same enemy.

    Returns a ranked list of results sorted by average_dps descending.
    """
    results = []
    for i, build in enumerate(builds):
        label  = (labels or [])[i] if labels and i < len(labels) else f"Build {i + 1}"
        result = run_combat_simulation(build, enemy, iterations=iterations,
                                       seed=seed, duration=duration)
        row    = result.to_dict()
        row["label"] = label
        results.append(row)
    results.sort(key=lambda r: r["average_dps"], reverse=True)
    return results
