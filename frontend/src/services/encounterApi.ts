/**
 * D7 — Encounter simulation API client.
 *
 * Calls POST /api/simulate/encounter and returns typed results.
 */

import type { ApiResponse } from "@/types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

export type HitDistribution = "SINGLE" | "CLEAVE" | "SPLIT" | "CHAIN";
export type EnemyTemplate =
  | "TRAINING_DUMMY"
  | "STANDARD_BOSS"
  | "SHIELDED_BOSS"
  | "ADD_FIGHT"
  | "MOVEMENT_BOSS";

export interface EncounterRequest {
  base_damage: number;
  fight_duration: number;
  tick_size: number;
  enemy_template: EnemyTemplate;
  distribution: HitDistribution;
  crit_chance: number;
  crit_multiplier: number;
}

export interface EncounterResult {
  total_damage: number;
  dps: number;
  elapsed_time: number;
  ticks_simulated: number;
  all_enemies_dead: boolean;
  enemies_killed: number;
  total_casts: number;
  downtime_ticks: number;
  active_phase_id: string | null;
  damage_per_tick: number[];
}

export const TEMPLATE_LABELS: Record<EnemyTemplate, string> = {
  TRAINING_DUMMY: "Training Dummy",
  STANDARD_BOSS:  "Standard Boss",
  SHIELDED_BOSS:  "Shielded Boss",
  ADD_FIGHT:      "Add Fight",
  MOVEMENT_BOSS:  "Movement Boss",
};

export const DISTRIBUTION_LABELS: Record<HitDistribution, string> = {
  SINGLE: "Single Target",
  CLEAVE: "Cleave (Full AoE)",
  SPLIT:  "Split (Equal Share)",
  CHAIN:  "Chain (Falloff)",
};

export async function runSimulation(
  req: EncounterRequest,
  signal?: AbortSignal
): Promise<EncounterResult> {
  const res = await fetch(`${BASE_URL}/simulate/encounter`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
    signal,
  });

  if (!res.ok) {
    const body: ApiResponse<null> = await res.json().catch(() => ({
      data: null, meta: null, errors: [{ message: `HTTP ${res.status}` }],
    }));
    const msg = body.errors?.[0]?.message ?? `Request failed (${res.status})`;
    throw new Error(msg);
  }

  const body: ApiResponse<EncounterResult> = await res.json();
  if (!body.data) throw new Error("Empty response from server");
  return body.data;
}
