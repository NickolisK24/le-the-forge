/**
 * UI+3 — Live Stat Update Engine
 * Instantly recalculate derived stats when gear, skills, or passives change.
 * Target: < 50ms from change to updated result.
 */

import { useState, useEffect, useRef, useCallback } from "react";

export interface StatSource {
  gear: Record<string, unknown>;
  skills: string[];
  passives: number[];
  level?: number;
}

export interface ComputedStats {
  totalDps: number;
  effectiveCritChance: number;
  effectiveCritMultiplier: number;
  totalArmor: number;
  totalResistances: Record<string, number>;
  manaPool: number;
  castSpeed: number;
  movementSpeed: number;
  raw: Record<string, number>;
}

export interface LiveStatsResult {
  stats: ComputedStats;
  isCalculating: boolean;
  latencyMs: number;
  version: number;
}

const DEFAULT_STATS: ComputedStats = {
  totalDps: 0,
  effectiveCritChance: 0,
  effectiveCritMultiplier: 1.5,
  totalArmor: 0,
  totalResistances: {},
  manaPool: 200,
  castSpeed: 1.0,
  movementSpeed: 1.0,
  raw: {},
};

/** Derive numeric stat values from a gear slot map. */
function extractGearStats(gear: Record<string, unknown>): Record<string, number> {
  const stats: Record<string, number> = {};
  for (const slot of Object.values(gear)) {
    if (slot && typeof slot === "object") {
      const affixes = (slot as Record<string, unknown>).affixes;
      if (Array.isArray(affixes)) {
        for (const affix of affixes) {
          if (affix && typeof affix === "object") {
            const a = affix as Record<string, unknown>;
            const key = String(a.stat ?? a.type ?? "");
            const val = Number(a.value ?? a.tier ?? 0);
            if (key) stats[key] = (stats[key] ?? 0) + val;
          }
        }
      }
    }
  }
  return stats;
}

/** Fast synchronous stat computation. Runs in < 1ms for typical builds. */
function computeStats(source: StatSource): ComputedStats {
  const gearStats = extractGearStats(source.gear);

  const baseDps = 100;
  const skillBonus = source.skills.length * 10;
  const passiveBonus = source.passives.reduce((sum, id) => sum + (id % 10), 0);
  const damageBonus = gearStats["spell_damage"] ?? gearStats["damage"] ?? 0;

  const totalDps = baseDps + skillBonus + passiveBonus + damageBonus;

  const baseCrit = 0.05;
  const critBonus = (gearStats["crit_chance"] ?? 0) / 100;
  const effectiveCritChance = Math.min(1, baseCrit + critBonus);

  const baseCritMult = 1.5;
  const critMultBonus = (gearStats["crit_multiplier"] ?? 0) / 100;
  const effectiveCritMultiplier = baseCritMult + critMultBonus;

  const baseArmor = 0;
  const armorBonus = gearStats["armor"] ?? 0;
  const totalArmor = baseArmor + armorBonus;

  const resistanceTypes = ["fire", "cold", "lightning", "void", "poison"];
  const totalResistances: Record<string, number> = {};
  for (const res of resistanceTypes) {
    const val = gearStats[`${res}_resistance`] ?? gearStats[res] ?? 0;
    if (val !== 0) totalResistances[res] = val;
  }

  const baseMana = 200;
  const manaBonus = gearStats["mana"] ?? 0;
  const manaPool = baseMana + manaBonus;

  const castSpeed = 1.0 + (gearStats["cast_speed"] ?? 0) / 100;
  const movementSpeed = 1.0 + (gearStats["movement_speed"] ?? 0) / 100;

  return {
    totalDps: Math.round(totalDps),
    effectiveCritChance: Math.round(effectiveCritChance * 1000) / 1000,
    effectiveCritMultiplier: Math.round(effectiveCritMultiplier * 100) / 100,
    totalArmor: Math.round(totalArmor),
    totalResistances,
    manaPool: Math.round(manaPool),
    castSpeed: Math.round(castSpeed * 100) / 100,
    movementSpeed: Math.round(movementSpeed * 100) / 100,
    raw: gearStats,
  };
}

/**
 * Live stat hook. Recomputes stats synchronously on every source change.
 * Uses a debounce only when `debounceMs > 0`.
 */
export function useLiveStats(
  source: StatSource,
  options: { debounceMs?: number; enabled?: boolean } = {}
): LiveStatsResult {
  const { debounceMs = 0, enabled = true } = options;

  const [result, setResult] = useState<LiveStatsResult>(() => ({
    stats: computeStats(source),
    isCalculating: false,
    latencyMs: 0,
    version: 0,
  }));

  const versionRef = useRef(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const recalculate = useCallback(
    (src: StatSource) => {
      if (!enabled) return;
      const start = performance.now();
      const stats = computeStats(src);
      const latencyMs = performance.now() - start;
      versionRef.current += 1;
      setResult({ stats, isCalculating: false, latencyMs, version: versionRef.current });
    },
    [enabled]
  );

  useEffect(() => {
    if (!enabled) return;

    if (debounceMs > 0) {
      setResult((prev) => ({ ...prev, isCalculating: true }));
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => recalculate(source), debounceMs);
      return () => {
        if (timerRef.current) clearTimeout(timerRef.current);
      };
    }

    recalculate(source);
    return undefined;
  }, [JSON.stringify(source), debounceMs, enabled, recalculate]);

  return result;
}
