/**
 * buffManager.ts — Manages active buff/debuff state.
 *
 * Tracks active buffs with durations, stacking, and tick-based expiry.
 * Pure functions — returns new state instead of mutating.
 * Deterministic timing using integer millisecond math.
 */

import type { BuffDefinition, ActiveBuff } from "@/types/buff";
import type { AggregatedStat } from "@/types/passiveEffects";

// ---------------------------------------------------------------------------
// State type
// ---------------------------------------------------------------------------

export type BuffState = Map<string, ActiveBuff>;

/** Create an empty buff state. */
export function createBuffState(): BuffState {
  return new Map();
}

// ---------------------------------------------------------------------------
// Apply / Remove
// ---------------------------------------------------------------------------

/**
 * Apply a buff. If already active:
 *   - Refresh duration
 *   - Increment stacks (up to maxStacks)
 * Returns new state.
 */
export function applyBuff(
  state: BuffState,
  definition: BuffDefinition,
  now: number = Date.now(),
): BuffState {
  const next = new Map(state);
  const existing = next.get(definition.id);

  if (existing) {
    // Refresh duration and add stack
    next.set(definition.id, {
      ...existing,
      remainingSeconds: definition.durationSeconds,
      stacks: Math.min(existing.stacks + 1, definition.maxStacks),
    });
  } else {
    // New buff
    next.set(definition.id, {
      definition,
      remainingSeconds: definition.durationSeconds === 0 ? -1 : definition.durationSeconds,
      stacks: 1,
      appliedAt: now,
    });
  }

  return next;
}

/**
 * Remove a buff entirely (all stacks).
 * Returns new state.
 */
export function removeBuff(state: BuffState, buffId: string): BuffState {
  const next = new Map(state);
  next.delete(buffId);
  return next;
}

/**
 * Remove one stack of a buff. If stacks reach 0, remove entirely.
 */
export function removeBuffStack(state: BuffState, buffId: string): BuffState {
  const next = new Map(state);
  const existing = next.get(buffId);
  if (!existing) return state;

  if (existing.stacks <= 1) {
    next.delete(buffId);
  } else {
    next.set(buffId, { ...existing, stacks: existing.stacks - 1 });
  }

  return next;
}

// ---------------------------------------------------------------------------
// Tick (time progression)
// ---------------------------------------------------------------------------

/**
 * Advance buff timers by deltaSeconds.
 * Removes expired buffs. Permanent buffs (remainingSeconds === -1) are never expired.
 *
 * Uses integer math internally to avoid floating-point drift:
 *   - Converts to milliseconds, subtracts, converts back
 */
export function tickBuffs(state: BuffState, deltaSeconds: number): BuffState {
  if (deltaSeconds <= 0) return state;

  const next = new Map<string, ActiveBuff>();
  const deltaMs = Math.round(deltaSeconds * 1000);

  for (const [id, buff] of state) {
    // Permanent buffs never expire
    if (buff.remainingSeconds === -1) {
      next.set(id, buff);
      continue;
    }

    const remainingMs = Math.round(buff.remainingSeconds * 1000) - deltaMs;
    if (remainingMs <= 0) {
      // Expired — don't include in next state
      continue;
    }

    next.set(id, {
      ...buff,
      remainingSeconds: remainingMs / 1000,
    });
  }

  return next;
}

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

/** Get all active buffs as an array, sorted by appliedAt for determinism. */
export function getActiveBuffs(state: BuffState): ActiveBuff[] {
  return Array.from(state.values()).sort((a, b) => a.appliedAt - b.appliedAt);
}

/** Get only buffs (not debuffs). */
export function getBuffsOnly(state: BuffState): ActiveBuff[] {
  return getActiveBuffs(state).filter((b) => !b.definition.isDebuff);
}

/** Get only debuffs. */
export function getDebuffsOnly(state: BuffState): ActiveBuff[] {
  return getActiveBuffs(state).filter((b) => b.definition.isDebuff);
}

/** Check if a specific buff is active. */
export function isBuffActive(state: BuffState, buffId: string): boolean {
  return state.has(buffId);
}

/** Get active buff IDs. */
export function getActiveBuffIds(state: BuffState): string[] {
  return Array.from(state.keys());
}

// ---------------------------------------------------------------------------
// Stat aggregation from active buffs
// ---------------------------------------------------------------------------

/**
 * Aggregate stat modifiers from all active buffs.
 * Each modifier is multiplied by the buff's stack count.
 * Returns Map<statId, AggregatedStat> compatible with the merge pipeline.
 */
export function aggregateBuffStats(state: BuffState): Map<string, AggregatedStat> {
  const stats = new Map<string, AggregatedStat>();

  for (const buff of state.values()) {
    for (const mod of buff.definition.modifiers) {
      if (!mod.statId || !Number.isFinite(mod.value)) continue;

      const scaled = mod.value * buff.stacks;
      if (!Number.isFinite(scaled)) continue;

      let entry = stats.get(mod.statId);
      if (!entry) {
        entry = { statId: mod.statId, flat: 0, percent: 0 };
        stats.set(mod.statId, entry);
      }

      if (mod.type === "flat") {
        entry.flat += scaled;
      } else {
        entry.percent += scaled;
      }
    }
  }

  return stats;
}

// ---------------------------------------------------------------------------
// Validation tests
// ---------------------------------------------------------------------------

export interface BuffTestResult {
  name: string;
  passed: boolean;
  details: string;
}

export function runBuffTests(): BuffTestResult[] {
  const results: BuffTestResult[] = [];
  const EXAMPLE_BUFFS = _getTestBuffs();

  // Test 1: Apply buff appears in active list
  {
    let state = createBuffState();
    state = applyBuff(state, EXAMPLE_BUFFS.berserk, 1000);
    const active = getActiveBuffs(state);
    const passed = active.length === 1 && active[0].definition.id === "berserk";
    results.push({ name: "Apply buff appears in active list", passed, details: passed ? "OK" : `Got ${active.length} buffs` });
  }

  // Test 2: Tick duration expires buff
  {
    let state = createBuffState();
    state = applyBuff(state, EXAMPLE_BUFFS.berserk, 1000); // 8s duration
    state = tickBuffs(state, 9); // 9 seconds later
    const active = getActiveBuffs(state);
    const passed = active.length === 0;
    results.push({ name: "Tick duration expires buff", passed, details: passed ? "OK" : `${active.length} buffs remain` });
  }

  // Test 3: Stacking buff increments
  {
    let state = createBuffState();
    state = applyBuff(state, EXAMPLE_BUFFS.frenzy, 1000);
    state = applyBuff(state, EXAMPLE_BUFFS.frenzy, 1001);
    state = applyBuff(state, EXAMPLE_BUFFS.frenzy, 1002);
    const buff = state.get("frenzy");
    const passed = buff !== undefined && buff.stacks === 3;
    results.push({ name: "Stacking buff increments", passed, details: passed ? `OK (${buff?.stacks} stacks)` : `Got ${buff?.stacks} stacks` });
  }

  // Test 4: Max stacks capped
  {
    let state = createBuffState();
    for (let i = 0; i < 10; i++) state = applyBuff(state, EXAMPLE_BUFFS.frenzy, 1000 + i);
    const buff = state.get("frenzy");
    const passed = buff !== undefined && buff.stacks === 5; // maxStacks=5
    results.push({ name: "Max stacks capped at 5", passed, details: passed ? "OK" : `Got ${buff?.stacks}` });
  }

  // Test 5: Remove buff clears it
  {
    let state = createBuffState();
    state = applyBuff(state, EXAMPLE_BUFFS.berserk, 1000);
    state = removeBuff(state, "berserk");
    const passed = !state.has("berserk");
    results.push({ name: "Remove buff clears it", passed, details: passed ? "OK" : "Still present" });
  }

  // Test 6: Permanent buff never expires
  {
    const permBuff: BuffDefinition = { ...EXAMPLE_BUFFS.berserk, id: "perm", durationSeconds: 0 };
    let state = createBuffState();
    state = applyBuff(state, permBuff, 1000);
    state = tickBuffs(state, 999);
    const passed = state.has("perm");
    results.push({ name: "Permanent buff never expires", passed, details: passed ? "OK" : "Expired" });
  }

  return results;
}

/** Inline test buff definitions to avoid require() in browser. */
function _getTestBuffs(): Record<string, BuffDefinition> {
  return {
    berserk: {
      id: "berserk", name: "Berserk",
      modifiers: [{ statId: "Damage", type: "percent", value: 30 }, { statId: "Attack Speed", type: "percent", value: 15 }],
      durationSeconds: 8, maxStacks: 1, tags: ["melee"], isDebuff: false,
    },
    frenzy: {
      id: "frenzy", name: "Frenzy",
      modifiers: [{ statId: "Attack Speed", type: "percent", value: 5 }],
      durationSeconds: 4, maxStacks: 5, tags: ["stackable"], isDebuff: false,
    },
  };
}
