/**
 * G13 — Rotation API client.
 *
 * Calls POST /api/simulate/rotation and returns typed results.
 */

import type { ApiResponse } from "@/types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

// ---------------------------------------------------------------------------
// Request types
// ---------------------------------------------------------------------------

export interface SkillDefinition {
  skill_id:      string;
  base_damage?:  number;
  cast_time?:    number;
  cooldown?:     number;
  resource_cost?: number;
  tags?:         string[];
}

export interface RotationStep {
  skill_id:          string;
  delay_after_cast?: number;
  priority?:         number;
  repeat_count?:     number;
}

export interface RotationDefinition {
  rotation_id?: string;
  steps:        RotationStep[];
  loop?:        boolean;
}

export interface RotationEncounterOverride {
  enemy_template?: string;
  fight_duration?: number;
  tick_size?:      number;
  distribution?:   "SINGLE" | "CLEAVE" | "SPLIT" | "CHAIN";
  crit_chance?:    number;
  crit_multiplier?: number;
}

export interface RotationRequest {
  rotation:   RotationDefinition;
  skills:     SkillDefinition[];
  duration?:  number;
  gcd?:       number;
  encounter?: RotationEncounterOverride;
}

// ---------------------------------------------------------------------------
// Response types
// ---------------------------------------------------------------------------

export interface CastDetail {
  skill_id:    string;
  cast_at:     number;
  resolves_at: number;
  damage:      number;
}

export interface RotationMetrics {
  total_damage:      number;
  total_casts:       number;
  duration_used:     number;
  dps:               number;
  uptime_fraction:   number;
  idle_time:         number;
  efficiency:        number;
  cast_counts:       Record<string, number>;
  damage_by_skill:   Record<string, number>;
  avg_cast_interval: number;
}

export interface RotationResult {
  total_damage:     number;
  dps:              number;
  total_casts:      number;
  rotation_metrics: RotationMetrics;
  cast_results:     CastDetail[];
}

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------

export async function runRotation(
  req: RotationRequest,
  signal?: AbortSignal
): Promise<RotationResult> {
  const res = await fetch(`${BASE_URL}/simulate/rotation`, {
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

  const body: ApiResponse<RotationResult> = await res.json();
  if (!body.data) throw new Error("Empty response from server");
  return body.data;
}
