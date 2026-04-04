# Gameplay Feature Expansion — Implementation Reference

All 10 steps implemented on branch `claude/add-backend-constants-RlGuT`.
Each step is fully tested; the test count is noted per step.

---

## Step 1 — Enemy Archetype System

**Files:** `backend/app/domain/enemy.py` · `backend/tests/test_enemy_archetypes.py` (22 tests)

### What it does
Models the four enemy tiers in Last Epoch: Training Dummy, Normal, Elite, and Boss.

### Logic
- `EnemyStats` is a **frozen dataclass** holding `health`, `armor`, `resistances`, and `status_effects`.
- A `capped_resistances` property applies `min(v, RES_CAP)` to every resistance value so the cap is enforced automatically without mutating raw data.
- `EnemyArchetype` is an **enum** whose `base_stats()` factory method returns a pre-tuned `EnemyStats` object per tier:
  - `TRAINING_DUMMY` → all zeros (no mitigation)
  - `NORMAL` → 1 000 HP / 200 armor / ~25% resistances
  - `ELITE` → 3 000 HP / 500 armor / ~40% resistances
  - `BOSS` → 10 000 HP / 1 000 armor / ~60% resistances
- Scaling invariant: boss > elite > normal > dummy for every stat.

---

## Step 2 — Ailment System Foundation

**Files:** `backend/app/domain/ailments.py` · `backend/tests/test_ailment_system.py` (24 tests)

### What it does
Provides the primitive building blocks for damage-over-time effects.

### Logic
- `AilmentType` enum: `BLEED`, `IGNITE`, `POISON`, `SHOCK`, `FROSTBITE`.
- `AilmentInstance` is a **frozen dataclass** — once created it cannot change. Fields: `ailment_type`, `damage_per_tick`, `duration`, `stack_count`.
- `apply_ailment(active, type, dpt, duration) → list` returns a **new list** with the instance appended. The original list is never mutated (functional pattern).
- `tick_ailments(active, delta) → (remaining, total_damage)`:
  - Subtracts `delta` from every instance's duration.
  - Removes instances whose new duration is `<= 0`.
  - Sums `damage_per_tick * delta` across all instances (before removal).
  - Returns a new list and a float — no mutation.

---

## Step 3 — Ailment Stacking Logic

**Files:** `backend/app/domain/ailment_stacking.py` · `backend/tests/test_ailment_stacking.py` (24 tests)

### What it does
Enforces Last Epoch stack caps and provides a DPS snapshot function.

### Logic
- `STACK_LIMITS` dict encodes per-type caps: bleed/poison cap at **8**, ignite/shock/frostbite cap at **1**.
- `enforce_stack_limit(active, type)` partitions the list into same-type and other-type stacks, then slices the same-type list to keep only the **most-recent** `limit` entries (front-trimmed). Other-type stacks are completely untouched.
- `apply_ailment_with_limit(active, type, dpt, dur)` is a convenience wrapper: calls `apply_ailment` then `enforce_stack_limit` in one call so callers never forget to enforce.
- `calculate_total_ailment_damage(active)` sums `damage_per_tick` across all active instances — an instantaneous DPS snapshot independent of remaining duration.

---

## Step 4 — Buff/Debuff Timeline Engine

**Files:** `backend/app/domain/timeline.py` · `backend/tests/test_timeline_engine.py` (28 tests)

### What it does
Tracks time-limited stat modifiers (buffs and debuffs) and expires them automatically.

### Logic
- `BuffType` enum: `DAMAGE_MULTIPLIER`, `ATTACK_SPEED`, `CAST_SPEED`, `MOVEMENT_SPEED`, `RESISTANCE_SHRED`, `DAMAGE_TAKEN`, `CRIT_CHANCE_BONUS`.
- `BuffInstance` is a **frozen dataclass** — value, duration, and source are immutable after construction.
- `TimelineEngine` is a **mutable class** wrapping a `list[BuffInstance]`:
  - `add_buff(buff)` — appends to internal list.
  - `tick(delta)` — rebuilds the list: for each buff, if `duration - delta > 0` a new `BuffInstance` with reduced duration is kept; otherwise it is expired. Returns the expired list for event hooks.
  - `total_modifier(type)` — sums `value` across matching active buffs (additive aggregation).
  - `has_any(type)` — O(n) existence check.
  - `active_buffs` property returns a **snapshot copy** so callers cannot accidentally mutate the internal list.
- Negative `value` is supported for debuffs (e.g. `DAMAGE_TAKEN = -20` means the enemy takes 20% less).

---

## Step 5 — Resistance Shred Mechanics

**Files:** `backend/app/domain/resistance_shred.py` · `backend/tests/test_resistance_shred.py` (25 tests)

### What it does
Models resistance shred — a debuff that reduces an enemy's resistance and can push it **negative** (vulnerability), unlike penetration which floors at zero.

### Logic

| Mechanic | Penetration | Shred |
|----------|------------|-------|
| Applied per | Hit | Debuff on enemy |
| Can go negative | No (floors at 0) | Yes (clamped at −RES_CAP) |

- `apply_resistance_shred(resistances, shred_map)`:
  - For each type in `shred_map`: `eff = max(-RES_CAP, base - shred)`.
  - Types absent from `resistances` start at 0.0.
  - Returns a **new dict** — original is never mutated.
- `shred_damage_multiplier(base_resistance, shred)`:
  - `eff = max(-RES_CAP, base - shred)`
  - `multiplier = 1.0 - eff / 100.0`
  - Result `> 1.0` when `eff < 0` (enemy is vulnerable and takes more damage).
  - Maximum vulnerability: `eff = -75` → `multiplier = 1.75`.
- `effective_shredded_resistance(resistances, shred_map, damage_type)` — single-type convenience wrapper.

---

## Step 6 — Multi-Hit Skill Support

**Files:** `backend/app/domain/skill.py` (extended) · `backend/tests/test_multi_hit_skill.py` (21 tests)

### What it does
Extends `SkillStatDef` so skills that fire multiple projectiles or hit multiple times per cast are modelled correctly.

### Logic
- Two new fields added to the frozen `SkillStatDef` dataclass:
  - `hit_count: int = 1` — number of discrete hits per cast activation.
  - `hit_interval: float = 0.0` — seconds between hits within one cast (0 = simultaneous). Used by timeline scheduling; does **not** affect steady-state DPS.
- `from_dict` parses both fields from JSON with safe defaults.
- `calculate_multi_hit_dps(skill, per_hit_damage)`:
  ```
  total_damage_per_cast = per_hit_damage × hit_count
  dps = total_damage_per_cast × attack_speed
  ```
  Raises `ValueError` if `hit_count < 1` or `attack_speed <= 0`.
- `hit_interval` intentionally excluded from the DPS formula — it controls *when* each hit lands within a cast window, not *how many* casts occur per second.

---

## Step 7 — Status Effect Interaction System

**Files:** `backend/app/domain/status_interactions.py` · `backend/tests/test_status_interactions.py` (26 tests)

### What it does
Models synergies between co-active ailments (e.g. shocked enemies take more ignite damage).

### Logic
Three interaction rules, evaluated by `evaluate_status_interactions(active)`:

| Trigger | Target | Effect | Type |
|---------|--------|--------|------|
| Shock (N stacks) | All damage (`target=None`) | +`N × 20%` damage taken | Additive % |
| Frostbite (N stacks) | Frostbite damage | +`N × 25%` cold damage | Additive % |
| Shock + Ignite | Ignite only | `× (1 + N × 0.10)` ignite damage | Multiplicative |

- `InteractionResult` is a **frozen dataclass** with `source`, `target`, `bonus_percent`, `multiplier`, `description`.
- `target = None` means the bonus applies to all ailment types.
- `apply_interaction_multiplier(base, active, ailment_type)`:
  - Collects all interactions where `target is None` or `target is ailment_type`.
  - Sums additive bonuses first, then multiplies all multipliers:
    ```
    damage = base × (1 + Σ bonus_percent / 100) × Π multipliers
    ```

---

## Step 8 — Enemy Behavior Profiles

**Files:** `backend/app/domain/enemy_behavior.py` · `backend/tests/test_enemy_behavior.py` (28 tests)

### What it does
Models the attack/move/stun cycle of an enemy so simulations can account for downtime when the enemy is not attackable.

### Logic
- `EnemyBehaviorProfile` (frozen dataclass): `attack_duration`, `move_duration`, `stun_duration`, `is_stationary`.
  - `__post_init__` validates all durations are non-negative.
  - `cycle_duration` property: sum of all phases (move phase omitted when `is_stationary=True`).
  - `attack_uptime` property: `attack_duration / cycle_duration`.
- `simulate_enemy_behavior(profile, fight_duration) → BehaviorSummary`:
  - `full_cycles = floor(fight_duration / cycle_duration)`.
  - `partial = fight_duration mod cycle_duration`.
  - Partial cycle distributes remaining time through phases **in order**: attack → move → stun (each phase consumes up to its full duration, then the next phase begins).
  - Returns `BehaviorSummary` (frozen) with `attack_time`, `move_time`, `stun_time`, `attack_uptime`, `full_cycles`, `partial_cycle`.
  - Invariant: `attack_time + move_time + stun_time == fight_duration`.

---

## Step 9 — Combat Timeline Integration

**Files:** `backend/app/domain/combat_timeline.py` · `backend/tests/test_combat_timeline.py` (22 tests)

### What it does
The integration layer — ties together ailments, buffs, status interactions, and enemy behavior into a single tick-based simulator.

### Logic
- `CombatTimeline(tick_size, behavior_profile)` is the stateful manager.
- Per-tick pipeline inside `advance(duration)`:
  1. **Tick ailments** — call `tick_ailments(active, delta)` to get the surviving list and the raw per-instance damage.
  2. **Status interactions** — for each active instance, call `apply_interaction_multiplier(raw, active, type)` to apply shock/frostbite/synergy bonuses.
  3. **Damage multiplier buff** — query `buff_engine.total_modifier(DAMAGE_MULTIPLIER)` and scale by `(1 + bonus/100)`.
  4. **Behavior uptime** — if a `BehaviorProfile` is set, compute `attack_uptime` for the full advance window via `simulate_enemy_behavior` and multiply each tick's damage by that fraction.
  5. **Tick buffs** — `buff_engine.tick(delta)` expires any elapsed buffs.
- `apply_ailment(type, dpt, dur)` delegates to `apply_ailment_with_limit` (stack limits automatically enforced).
- `get_result() → CombatResult` (frozen): `total_damage`, `fight_duration`, `average_dps`, `ticks_simulated`, `damage_by_ailment` (keyed by ailment value string).
- **Float accumulation note**: `tick_size=0.1` is not exactly representable in binary float; tests use `abs` tolerances (±1 tick of damage) or exact-power-of-2 tick sizes (0.25) to avoid spurious failures.

---

## Step 10 — Realistic Fight Simulation

**Files:** `backend/app/domain/fight_simulator.py` · `backend/tests/test_fight_simulator.py` (25 tests)

### What it does
The top-level public entry point: runs a full encounter from configuration to result.

### Logic
- `AilmentApplication` (frozen): `ailment_type`, `damage_per_tick`, `duration`, `stacks_per_cast` (default 1).
- `FightConfig` (frozen): `fight_duration`, `cast_interval`, `ailments`, `initial_buffs`, `behavior_profile`, `tick_size`. Validated in `__post_init__`.
- `simulate_fight(config) → FightResult`:
  1. Construct a `CombatTimeline` from `tick_size` and `behavior_profile`.
  2. Apply all `initial_buffs` to the timeline.
  3. Loop while `elapsed < fight_duration`:
     - **Cast**: for each `AilmentApplication`, call `timeline.apply_ailment` `stacks_per_cast` times.
     - **Advance**: call `timeline.advance(min(cast_interval, remaining))`.
  4. Return `FightResult(combat_result, total_casts, config)`.
- The cast loop naturally handles the boundary: at `t = fight_duration` the while condition fails, so no damage is computed after the fight ends.
- `FightResult` is **frozen** and stores the originating `FightConfig` for reproducibility.

---

## Test Coverage Summary

| Step | Module | Tests |
|------|--------|------:|
| 1 | `enemy.py` | 22 |
| 2 | `ailments.py` | 24 |
| 3 | `ailment_stacking.py` | 24 |
| 4 | `timeline.py` | 28 |
| 5 | `resistance_shred.py` | 25 |
| 6 | `skill.py` (multi-hit) | 21 |
| 7 | `status_interactions.py` | 26 |
| 8 | `enemy_behavior.py` | 28 |
| 9 | `combat_timeline.py` | 22 |
| 10 | `fight_simulator.py` | 25 |
| **Total** | | **245** |
