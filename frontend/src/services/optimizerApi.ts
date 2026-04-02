/**
 * F10 — Optimizer API client.
 *
 * Calls POST /api/optimize/build and returns typed optimization results.
 */

import type { ApiResponse } from "@/types";
import type { BuildDefinition, EncounterOverride } from "@/services/buildApi";
import type { EncounterResult } from "@/services/encounterApi";

const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

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
  signal?: AbortSignal
): Promise<OptimizeBuildResponse> {
  const res = await fetch(`${BASE_URL}/optimize/build`, {
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

  const body: ApiResponse<OptimizeBuildResponse> = await res.json();
  if (!body.data) throw new Error("Empty response from server");
  return body.data;
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
