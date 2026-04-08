/**
 * F10 — Optimizer API client.
 *
 * Calls POST /api/optimize/build and returns typed optimization results.
 */

import { apiPost } from "@/lib/api";
import type { BuildDefinition, EncounterOverride } from "@/services/buildApi";
import type { EncounterResult } from "@/services/encounterApi";

// ---------------------------------------------------------------------------
// Request / Response types
// ---------------------------------------------------------------------------

export type OptimizationMetric = "dps" | "total_damage" | "ttk" | "uptime" | "composite";

export interface OptimizationConfig {
  target_metric:  OptimizationMetric;
  max_variants:   number;   // 1–1000
  mutation_depth: number;   // 1–10
  constraints:    Record<string, number | string>;
  random_seed:    number;
}

export interface OptimizeBuildRequest {
  build:      BuildDefinition;
  config?:    Partial<OptimizationConfig>;
  encounter?: EncounterOverride;
  top_n?:     number;
}

export interface OptimizationResultItem {
  rank:              number;
  score:             number;
  mutations_applied: string[];
  build_variant:     BuildDefinition;
  simulation_output: EncounterResult;
}

export interface OptimizeBuildResponse {
  results:                     OptimizationResultItem[];
  total_variants_generated:    number;
  variants_passed_constraints: number;
  variants_simulated:          number;
  variants_failed_simulation:  number;
}

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------

export async function runOptimization(
  req: OptimizeBuildRequest,
): Promise<OptimizeBuildResponse> {
  const res = await apiPost<OptimizeBuildResponse>("/optimize/build", req);
  if (res.errors) {
    throw new Error(res.errors[0]?.message ?? "Optimization failed");
  }
  if (!res.data) throw new Error("Empty response from server");
  return res.data;
}

// ---------------------------------------------------------------------------
// Display helpers
// ---------------------------------------------------------------------------

export const METRIC_LABELS: Record<OptimizationMetric, string> = {
  dps:          "DPS",
  total_damage: "Total Damage",
  ttk:          "Time to Kill",
  uptime:       "Uptime",
  composite:    "Composite",
};
