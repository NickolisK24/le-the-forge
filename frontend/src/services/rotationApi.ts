/**
 * G13 — Rotation API client.
 *
 * Calls POST /api/simulate/rotation and returns typed results.
 */

import { apiPost } from "@/lib/api";

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
): Promise<RotationResult> {
  const res = await apiPost<RotationResult>("/simulate/rotation", req);
  if (res.errors) {
    throw new Error(res.errors[0]?.message ?? "Rotation simulation failed");
  }
  if (!res.data) throw new Error("Empty response from server");
  return res.data;
}
