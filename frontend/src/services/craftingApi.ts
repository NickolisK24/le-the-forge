/**
 * Crafting API service — connects the Crafting Lab UI to the backend engine.
 *
 * Primary endpoint: POST /api/craft/predict (stateless optimizer)
 *   - Takes: forge_potential, affixes (target list), n_simulations
 *   - Returns: optimal_path, simulation_result, strategy_comparison
 */

const BASE = import.meta.env.VITE_API_URL ?? "/api";

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
  const res = await fetch(`${BASE}/craft/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      forge_potential: req.forge_potential,
      affixes: req.affixes.map((a) => ({
        affix_name: a.affix_name,
        current_tier: a.current_tier,
        target_tier: a.target_tier,
      })),
      n_simulations: req.n_simulations ?? 10_000,
    }),
  });

  const json = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(
      json.errors?.[0]?.message ?? json.error ?? `Craft prediction failed (${res.status})`,
    );
  }

  return json.data ?? json;
}
