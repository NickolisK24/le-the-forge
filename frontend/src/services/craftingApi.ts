/**
 * Crafting API service — connects the Crafting Lab UI to the backend engine.
 *
 * Uses the shared API client for auth token injection and error handling.
 * Primary endpoint: POST /api/craft/predict (stateless optimizer)
 */

import { apiPost } from "@/lib/api";

// ---------------------------------------------------------------------------
// Request types
// ---------------------------------------------------------------------------

export interface CraftAffixTarget {
  affix_id: string;
  affix_name: string;
  current_tier: number;
  target_tier: number;
}

export interface CraftPredictRequest {
  forge_potential: number;
  affixes: CraftAffixTarget[];
  n_simulations?: number;
}

// ---------------------------------------------------------------------------
// Response types
// ---------------------------------------------------------------------------

export interface CraftPathStep {
  action: string;
  affix_name?: string;
  target_tier?: number;
  sealed_count_at_step: number;
}

export interface CraftSimulationResult {
  completion_chance: number;
  step_survival_curve: number[];
  n_simulations: number;
  seed: number | null;
}

export interface StrategyComparison {
  name: string;
  completion_chance: number;
  mean_fp_cost: number;
  steps: number;
}

export interface CraftPredictResponse {
  optimal_path: CraftPathStep[];
  simulation_result: CraftSimulationResult;
  strategy_comparison: StrategyComparison[];
}

// ---------------------------------------------------------------------------
// API calls
// ---------------------------------------------------------------------------

export async function predictCrafting(
  req: CraftPredictRequest,
): Promise<CraftPredictResponse> {
  const res = await apiPost<CraftPredictResponse>("/craft/predict", {
    forge_potential: req.forge_potential,
    affixes: req.affixes.map((a) => ({
      affix_name: a.affix_name,
      current_tier: a.current_tier,
      target_tier: a.target_tier,
    })),
    n_simulations: req.n_simulations ?? 10_000,
  });

  if (res.errors) {
    throw new Error(res.errors[0]?.message ?? "Craft prediction failed");
  }
  if (!res.data) {
    throw new Error("Empty response from craft prediction");
  }
  return res.data;
}
