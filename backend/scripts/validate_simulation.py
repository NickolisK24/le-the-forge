"""
Deep Validation: Fight Simulation Correctness
=============================================

Runs controlled scenarios where the correct answer can be derived
analytically (pen-and-paper math), then compares simulation output
to that expectation tick-by-tick.

Run with:
    cd backend && python scripts/validate_simulation.py

Each scenario prints:
  - Per-tick event log (elapsed, active stacks, raw damage, modifiers, final)
  - Analytical expected value
  - Simulated value
  - PASS / FAIL with absolute and relative error

Exit code 0 = all scenarios pass.
"""

import sys
import os

# Allow running from the backend/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.domain.ailments import AilmentType, AilmentInstance, tick_ailments
from app.domain.ailment_stacking import apply_ailment_with_limit, STACK_LIMITS
from app.domain.timeline import BuffInstance, BuffType, TimelineEngine
from app.domain.status_interactions import (
    apply_interaction_multiplier,
    SHOCK_DAMAGE_BONUS_PER_STACK,
    IGNITE_SHOCK_MULTIPLIER_BONUS,
)
from app.domain.enemy_behavior import EnemyBehaviorProfile, simulate_enemy_behavior
from app.domain.fight_simulator import FightConfig, AilmentApplication, simulate_fight

# ─────────────────────────────────────────────────────────────────────────────
# Logging helpers
# ─────────────────────────────────────────────────────────────────────────────

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
SEP  = "─" * 72

def header(title: str) -> None:
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)

def log_tick(
    t: float,
    stacks: list[AilmentInstance],
    buffs: TimelineEngine,
    uptime: float,
    tick_dmg: float,
) -> None:
    stack_desc = ", ".join(
        f"{s.ailment_type.value}×{s.stack_count}[{s.duration:.3f}s @{s.damage_per_tick}dpt]"
        for s in stacks
    ) or "(none)"
    buff_desc = ", ".join(
        f"{b.buff_type.value}={b.value:+.0f}%[{b.duration:.3f}s]"
        for b in buffs.active_buffs
    ) or "(none)"
    print(
        f"  t={t:6.3f}s | {stack_desc:55s} | buffs={buff_desc:35s} "
        f"| uptime={uptime:.2f} | tick_dmg={tick_dmg:8.4f}"
    )

def verdict(label: str, expected: float, simulated: float, abs_tol: float = 0.5) -> bool:
    err = abs(simulated - expected)
    rel = err / expected if expected != 0 else err
    ok  = err <= abs_tol
    mark = PASS if ok else FAIL
    print(f"\n  {mark}  expected={expected:.4f}  simulated={simulated:.4f}  "
          f"err={err:.4f}  rel={rel:.2%}")
    return ok


# ─────────────────────────────────────────────────────────────────────────────
# Manual tick-by-tick tracer (mirrors CombatTimeline.advance but with logging)
# ─────────────────────────────────────────────────────────────────────────────

def trace_fight(
    ailments_init: list[tuple[AilmentType, float, float]],  # (type, dpt, dur)
    buffs_init: list[tuple[BuffType, float, float]],        # (type, value, dur)
    fight_duration: float,
    tick_size: float = 0.25,
    behavior: EnemyBehaviorProfile | None = None,
    cast_interval: float | None = None,
    recast_ailments: list[tuple[AilmentType, float, float]] | None = None,
) -> tuple[float, int]:
    """
    Manually simulate a fight with full per-tick logging.
    Returns (total_damage, ticks_run).
    """
    active: list[AilmentInstance] = []
    engine = TimelineEngine()
    total_damage = 0.0
    ticks = 0
    elapsed = 0.0
    next_cast = 0.0

    # Initial application
    for (atype, dpt, dur) in ailments_init:
        active = apply_ailment_with_limit(active, atype, dpt, dur)
    for (btype, val, dur) in buffs_init:
        engine.add_buff(BuffInstance(btype, val, dur))

    uptime = 1.0
    if behavior is not None:
        summary = simulate_enemy_behavior(behavior, fight_duration)
        uptime = summary.attack_uptime

    while elapsed < fight_duration:
        actual_tick = min(tick_size, fight_duration - elapsed)

        # Recast check
        if cast_interval is not None and elapsed >= next_cast and elapsed > 0:
            for (atype, dpt, dur) in (recast_ailments or ailments_init):
                active = apply_ailment_with_limit(active, atype, dpt, dur)
            next_cast += cast_interval

        # 1. Compute tick damage per stack (before expiry)
        tick_total = 0.0
        for inst in active:
            raw = inst.damage_per_tick * actual_tick
            boosted = apply_interaction_multiplier(raw, active, inst.ailment_type)
            dmg_bonus = engine.total_modifier(BuffType.DAMAGE_MULTIPLIER)
            boosted *= 1.0 + dmg_bonus / 100.0
            boosted *= uptime
            tick_total += boosted

        # Log this tick
        log_tick(elapsed, active, engine, uptime, tick_total)

        # 2. Expire ailments and advance buffs
        active, _ = tick_ailments(active, actual_tick)
        engine.tick(actual_tick)

        total_damage += tick_total
        elapsed      += actual_tick
        ticks        += 1

    return total_damage, ticks


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 1 — Single bleed, no interactions
# ─────────────────────────────────────────────────────────────────────────────

def scenario_1() -> bool:
    header("Scenario 1: Single bleed, no interactions")
    print("  Setup: 1 bleed stack @ 80 dpt, 4s duration, 4s fight, tick=0.25s")
    print("  Expected: 80 dpt × 4s = 320 total damage\n")

    dpt = 80.0
    dur = 4.0
    fight = 4.0
    tick = 0.25

    total, ticks = trace_fight(
        ailments_init=[(AilmentType.BLEED, dpt, dur)],
        buffs_init=[],
        fight_duration=fight,
        tick_size=tick,
    )

    expected = dpt * fight   # 320
    return verdict("Scenario 1", expected, total, abs_tol=dpt * tick)


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 2 — Two bleed stacks, independent timers
# ─────────────────────────────────────────────────────────────────────────────

def scenario_2() -> bool:
    header("Scenario 2: Two bleed stacks with different durations")
    print("  Setup: stack A @ 50 dpt / 2s, stack B @ 30 dpt / 4s, 4s fight, tick=0.25s")
    print("  Expected: (50+30)×2s + 30×2s = 160 + 60 = 220 total damage\n")

    fight = 4.0
    tick  = 0.25

    active: list[AilmentInstance] = []
    active = apply_ailment_with_limit(active, AilmentType.BLEED, 50.0, 2.0)
    active = apply_ailment_with_limit(active, AilmentType.BLEED, 30.0, 4.0)

    engine = TimelineEngine()
    total_damage = 0.0
    elapsed = 0.0

    while elapsed < fight:
        actual_tick = min(tick, fight - elapsed)
        tick_total = 0.0
        for inst in active:
            raw = inst.damage_per_tick * actual_tick
            boosted = apply_interaction_multiplier(raw, active, inst.ailment_type)
            tick_total += boosted
        log_tick(elapsed, active, engine, 1.0, tick_total)
        active, _ = tick_ailments(active, actual_tick)
        engine.tick(actual_tick)
        total_damage += tick_total
        elapsed += actual_tick

    expected = (50.0 + 30.0) * 2.0 + 30.0 * 2.0   # 220
    return verdict("Scenario 2", expected, total_damage, abs_tol=50.0 * tick)


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 3 — Shock amplifies bleed (additive bonus)
# ─────────────────────────────────────────────────────────────────────────────

def scenario_3() -> bool:
    bonus = SHOCK_DAMAGE_BONUS_PER_STACK   # 20%
    header("Scenario 3: Shock (1 stack) amplifies bleed")
    print(f"  Setup: 1 bleed @ 100 dpt / 4s + 1 shock @ 0 dpt / 4s, 4s fight")
    print(f"  Shock adds +{bonus:.0f}% to all damage (target=None)")
    print(f"  Expected bleed: 100 × 4 × (1 + {bonus/100:.2f}) = {100*4*(1+bonus/100):.1f}")
    print(f"  Expected shock: 0 (dpt=0, though it also gets the bonus)")
    expected_bleed = 100.0 * 4.0 * (1.0 + bonus / 100.0)
    print(f"  Expected total: {expected_bleed:.1f}\n")

    total, _ = trace_fight(
        ailments_init=[
            (AilmentType.BLEED, 100.0, 4.0),
            (AilmentType.SHOCK, 0.0,   4.0),
        ],
        buffs_init=[],
        fight_duration=4.0,
        tick_size=0.25,
    )

    return verdict("Scenario 3", expected_bleed, total, abs_tol=100.0 * 0.25 * (1 + bonus/100))


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 4 — Shock + Ignite synergy (multiplicative)
# ─────────────────────────────────────────────────────────────────────────────

def scenario_4() -> bool:
    shock_add  = SHOCK_DAMAGE_BONUS_PER_STACK / 100.0   # 0.20
    ignite_mul = 1.0 + IGNITE_SHOCK_MULTIPLIER_BONUS    # 1.10

    header("Scenario 4: Shock + Ignite synergy")
    print(f"  Setup: ignite @ 200 dpt / 4s + shock @ 0 dpt / 4s, 4s fight")
    print(f"  Ignite gets: shock additive (+{shock_add*100:.0f}%) × synergy mult (×{ignite_mul:.2f})")
    expected_ignite = 200.0 * 4.0 * (1.0 + shock_add) * ignite_mul
    print(f"  Expected: 200 × 4 × {1+shock_add:.2f} × {ignite_mul:.2f} = {expected_ignite:.4f}\n")

    total, _ = trace_fight(
        ailments_init=[
            (AilmentType.IGNITE, 200.0, 4.0),
            (AilmentType.SHOCK,  0.0,   4.0),
        ],
        buffs_init=[],
        fight_duration=4.0,
        tick_size=0.25,
    )

    return verdict("Scenario 4", expected_ignite, total, abs_tol=200.0 * 0.25 * (1+shock_add) * ignite_mul)


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 5 — DAMAGE_MULTIPLIER buff doubles damage, expires at 2s
# ─────────────────────────────────────────────────────────────────────────────

def scenario_5() -> bool:
    header("Scenario 5: DAMAGE_MULTIPLIER buff (+100%) expires at 2s")
    print("  Setup: bleed @ 60 dpt / 4s, buff +100% for 2s, 4s fight, tick=0.25s")
    print("  First 2s:  60 × 2 × (1+1.00) = 240")
    print("  Second 2s: 60 × 2 × (1+0.00) =  120")
    print("  Expected total: 360\n")

    total, _ = trace_fight(
        ailments_init=[(AilmentType.BLEED, 60.0, 4.0)],
        buffs_init=[(BuffType.DAMAGE_MULTIPLIER, 100.0, 2.0)],
        fight_duration=4.0,
        tick_size=0.25,
    )

    # Tolerance: 1 tick at full buff (60*0.25*2=30) + 1 tick at no buff (60*0.25=15)
    return verdict("Scenario 5", 360.0, total, abs_tol=30.0)


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 6 — Enemy behavior: 50% uptime
# ─────────────────────────────────────────────────────────────────────────────

def scenario_6() -> bool:
    header("Scenario 6: Enemy behavior — 50% attack uptime")
    print("  Setup: bleed @ 100 dpt / 8s, fight=8s, profile: 1s attack / 1s move, tick=0.25s")
    print("  Uptime = 0.50  →  expected total = 100 × 8 × 0.50 = 400\n")

    profile = EnemyBehaviorProfile(attack_duration=1.0, move_duration=1.0)
    total, _ = trace_fight(
        ailments_init=[(AilmentType.BLEED, 100.0, 8.0)],
        buffs_init=[],
        fight_duration=8.0,
        tick_size=0.25,
        behavior=profile,
    )

    return verdict("Scenario 6", 400.0, total, abs_tol=100.0 * 0.25 * 0.5)


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 7 — Ignite stack limit (cap = 1)
# ─────────────────────────────────────────────────────────────────────────────

def scenario_7() -> bool:
    header("Scenario 7: Ignite stack limit (cap = 1, oldest dropped)")
    limit = STACK_LIMITS[AilmentType.IGNITE]
    print(f"  STACK_LIMITS[IGNITE] = {limit}")
    print("  Apply 3 ignite stacks (100, 150, 200 dpt), each 4s, then 4s fight")
    print("  Only the most-recent (200 dpt) should survive after limit enforcement")
    print("  Expected: 200 × 4 = 800\n")

    active: list[AilmentInstance] = []
    for dpt in [100.0, 150.0, 200.0]:
        active = apply_ailment_with_limit(active, AilmentType.IGNITE, dpt, 4.0)

    ignites = [i for i in active if i.ailment_type is AilmentType.IGNITE]
    print(f"  After enforcement: {len(ignites)} ignite stack(s), dpt={[i.damage_per_tick for i in ignites]}")

    engine = TimelineEngine()
    total_damage = 0.0
    elapsed = 0.0
    fight = 4.0
    tick  = 0.25

    while elapsed < fight:
        actual_tick = min(tick, fight - elapsed)
        tick_total = 0.0
        for inst in active:
            raw = inst.damage_per_tick * actual_tick
            boosted = apply_interaction_multiplier(raw, active, inst.ailment_type)
            tick_total += boosted
        log_tick(elapsed, active, engine, 1.0, tick_total)
        active, _ = tick_ailments(active, actual_tick)
        engine.tick(actual_tick)
        total_damage += tick_total
        elapsed += actual_tick

    expected = 200.0 * fight
    return verdict("Scenario 7", expected, total_damage, abs_tol=200.0 * tick)


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 8 — Full fight via simulate_fight() with repeated casts
# ─────────────────────────────────────────────────────────────────────────────

def scenario_8() -> bool:
    header("Scenario 8: simulate_fight() — bleed, cast every 2s, 6s fight")
    print("  Cast at t=0, t=2, t=4 → 3 casts of bleed @ 50 dpt / 3s")
    print()
    print("  Damage windows (each cast contributes 50×3=150, but they overlap):")
    print("    Cast 0:  t=0..3   → 50 dpt for 3s = 150")
    print("    Cast 1:  t=2..5   → 50 dpt for 3s = 150, overlapping cast 0 from t=2..3 (100 dpt)")
    print("    Cast 2:  t=4..6   → 50 dpt for 2s = 100  (fight ends at t=6)")
    print()
    print("  Analytical:")
    print("    t=0..2:  1 stack × 50 × 2s = 100")
    print("    t=2..3:  2 stacks × 50 × 1s = 100  (cast 0 still alive, cast 1 applied)")
    print("    t=3..4:  1 stack × 50 × 1s = 50   (cast 0 expires)")
    print("    t=4..5:  2 stacks × 50 × 1s = 100  (cast 1 still alive, cast 2 applied)")
    print("    t=5..6:  1 stack × 50 × 1s = 50   (cast 1 expires)")
    print("    Total = 100+100+50+100+50 = 400\n")

    cfg = FightConfig(
        fight_duration=6.0,
        cast_interval=2.0,
        ailments=(AilmentApplication(AilmentType.BLEED, 50.0, 3.0),),
        tick_size=0.25,
    )
    result = simulate_fight(cfg)

    print(f"  simulate_fight() total_casts = {result.total_casts}")
    print(f"  fight_duration = {result.combat_result.fight_duration:.3f}s")
    print(f"  avg_dps        = {result.combat_result.average_dps:.4f}")
    print(f"  damage_by_type = {result.combat_result.damage_by_ailment}")

    expected = 400.0
    return verdict("Scenario 8", expected, result.combat_result.total_damage, abs_tol=50.0 * 0.25)


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 9 — Poison with 8-stack cap saturating
# ─────────────────────────────────────────────────────────────────────────────

def scenario_9() -> bool:
    cap = STACK_LIMITS[AilmentType.POISON]
    header(f"Scenario 9: Poison stack cap ({cap} stacks)")
    print(f"  Apply {cap+2} poison stacks of 10 dpt, all 4s duration")
    print(f"  Only the {cap} most-recent survive → effective 80 dpt total")
    print(f"  Fight=4s, tick=0.25s → expected = 80 × 4 = 320\n")

    active: list[AilmentInstance] = []
    for i in range(cap + 2):
        active = apply_ailment_with_limit(active, AilmentType.POISON, 10.0, 4.0)

    poisons = [i for i in active if i.ailment_type is AilmentType.POISON]
    print(f"  Active poison stacks: {len(poisons)} (expected {cap})")
    assert len(poisons) == cap, f"WRONG stack count: {len(poisons)}"

    engine = TimelineEngine()
    total_damage = 0.0
    elapsed = 0.0
    fight = 4.0
    tick  = 0.25

    while elapsed < fight:
        actual_tick = min(tick, fight - elapsed)
        tick_total = sum(i.damage_per_tick * actual_tick for i in active)
        log_tick(elapsed, active, engine, 1.0, tick_total)
        active, _ = tick_ailments(active, actual_tick)
        engine.tick(actual_tick)
        total_damage += tick_total
        elapsed += actual_tick

    expected = cap * 10.0 * fight
    return verdict("Scenario 9", expected, total_damage, abs_tol=cap * 10.0 * tick)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    scenarios = [
        scenario_1,
        scenario_2,
        scenario_3,
        scenario_4,
        scenario_5,
        scenario_6,
        scenario_7,
        scenario_8,
        scenario_9,
    ]

    results = []
    for fn in scenarios:
        try:
            ok = fn()
            results.append(ok)
        except Exception as exc:
            print(f"\n  \033[31mERROR\033[0m  {fn.__name__}: {exc}")
            results.append(False)

    passed = sum(results)
    total  = len(results)

    print(f"\n{SEP}")
    print(f"  Results: {passed}/{total} scenarios passed")
    print(SEP)

    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
