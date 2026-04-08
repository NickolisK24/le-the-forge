/**
 * Client-side crafting math — mirrors app/services/craft_service.py.
 *
 * We replicate this on the frontend so the UI can show live FP cost
 * calculations as the user adjusts crafting parameters,
 * without a round-trip to the backend for every input change.
 *
 * The backend is the authoritative source for persisted outcomes.
 * These are display-only calculations.
 */

import type {
  CraftAffix,
  OptimalPathStep,
  SimulationResult,
  LocalSimulationResult,
  StrategyComparison,
} from "@/types";

export type RiskLevel = "safe" | "moderate" | "dangerous" | "critical";

export const TARGET_TIER = 5;

export const FP_COSTS: Record<string, number> = {
  upgrade_affix: 4,
  seal_affix: 8,
};

export function fpCost(action: string): number {
  return FP_COSTS[action] ?? 4;
}

// ---------------------------------------------------------------------------
// Optimal path search (mirrors optimal_path_search in craft_service.py)
// ---------------------------------------------------------------------------

export function optimalPath(
  affixes: CraftAffix[],
  forgePotential = 28,
): OptimalPathStep[] {
  const steps: OptimalPathStep[] = [];
  let fp = forgePotential;
  const current = affixes.map((a) => ({ ...a }));
  let sealedCount = current.filter((a) => a.sealed).length;

  const toUpgrade = current.filter((a) => !a.sealed && a.tier < TARGET_TIER);

  // Sort affixes by current tier (lowest first) to prioritize upgrading weaker affixes
  toUpgrade.sort((a, b) => a.tier - b.tier);

  for (const targetAffix of toUpgrade) {
    // Upgrade target affix step by step to TARGET_TIER
    while (targetAffix.tier < TARGET_TIER && fp >= FP_COSTS.upgrade_affix) {
      targetAffix.tier = Math.min(TARGET_TIER, targetAffix.tier + 1);

      steps.push({
        action: "upgrade_affix",
        affix: `${targetAffix.name} → T${targetAffix.tier}`,
        risk_pct: 0,
        cumulative_survival_pct: 100.0,
        sealed_count_at_step: sealedCount,
        note: `Upgrade to T${targetAffix.tier} — ${fp - FP_COSTS.upgrade_affix} FP remaining`,
      });

      fp -= FP_COSTS.upgrade_affix;
    }
  }

  // If we still have FP and unsealed affixes, consider sealing some for future upgrades
  const unsealedAffixes = current.filter((a) => !a.sealed);
  if (fp >= FP_COSTS.seal_affix && unsealedAffixes.length > 0) {
    // Seal the highest tier affix to preserve gains
    const toSeal = unsealedAffixes.reduce((best, a) =>
      a.tier > best.tier ? a : best
    );

    steps.push({
      action: "seal_affix",
      affix: toSeal.name,
      risk_pct: 0,
      cumulative_survival_pct: 100.0,
      sealed_count_at_step: sealedCount,
      note: `Seal "${toSeal.name}" (T${toSeal.tier}) — preserves current gains`,
    });

    toSeal.sealed = true;
    sealedCount++;
    fp -= FP_COSTS.seal_affix;
  }

  return steps;
}

// ---------------------------------------------------------------------------
// Monte Carlo simulation (mirrors simulate_sequence in craft_service.py)
// ---------------------------------------------------------------------------

interface SimStep {
  action: string;
  sealed_count_at_step: number;
}

export function simulateSequence(
  forgePotential: number,
  proposedSteps: SimStep[],
  nSimulations = 3_000,
): LocalSimulationResult {
  const n = nSimulations;
  const fpConsumed: number[] = [];
  const stepsCompleted: number[] = [];

  for (let sim = 0; sim < n; sim++) {
    let fp = forgePotential;
    let steps = 0;

    for (const step of proposedSteps) {
      const cost = FP_COSTS[step.action as keyof typeof FP_COSTS] ?? 0;
      if (fp < cost) {
        break; // Can't afford this step
      }
      fp -= cost;
      steps++;
    }

    fpConsumed.push(forgePotential - fp);
    stepsCompleted.push(steps);
  }

  // Calculate percentiles
  const sortedFp = [...fpConsumed].sort((a, b) => a - b);
  const sortedSteps = [...stepsCompleted].sort((a, b) => a - b);

  const completedCount = stepsCompleted.filter((s) => s >= proposedSteps.length).length;

  return {
    fp_consumed: {
      p25: sortedFp[Math.floor(sortedFp.length * 0.25)],
      p50: sortedFp[Math.floor(sortedFp.length * 0.5)],
      p75: sortedFp[Math.floor(sortedFp.length * 0.75)],
    },
    steps_completed: {
      p25: sortedSteps[Math.floor(sortedSteps.length * 0.25)],
      p50: sortedSteps[Math.floor(sortedSteps.length * 0.5)],
      p75: sortedSteps[Math.floor(sortedSteps.length * 0.75)],
    },
    completion_rate: n > 0 ? completedCount / n : 0,
    n_simulations: n,
  };
}

// ---------------------------------------------------------------------------
// Strategy comparison (mirrors compare_strategies in craft_service.py)
// ---------------------------------------------------------------------------

export function compareStrategies(
  affixes: CraftAffix[],
  forgePotential: number,
): StrategyComparison[] {
  const unsealed = affixes.filter((a) => !a.sealed && a.tier < TARGET_TIER);
  const existingSealedCount = affixes.filter((a) => a.sealed).length;

  // Strategy 1: Aggressive — upgrade without sealing
  const aggressiveSteps: SimStep[] = [];
  for (const affix of unsealed) {
    for (let t = affix.tier; t < TARGET_TIER; t++) {
      aggressiveSteps.push({
        action: "upgrade_affix",
        sealed_count_at_step: existingSealedCount,
      });
    }
  }

  // Strategy 2: Balanced — uses optimalPath
  const balancedRaw = optimalPath(affixes, forgePotential);
  const balancedSteps: SimStep[] = balancedRaw.map((s) => ({
    action: s.action,
    sealed_count_at_step: s.sealed_count_at_step,
  }));

  // Strategy 3: Conservative — seal everything first, then upgrade
  const conservativeSteps: SimStep[] = [];
  let consSealedCount = existingSealedCount;
  for (const _affix of unsealed) {
    conservativeSteps.push({
      action: "seal_affix",
      sealed_count_at_step: consSealedCount,
    });
    consSealedCount++;
  }
  for (const affix of unsealed) {
    for (let t = affix.tier; t < TARGET_TIER; t++) {
      conservativeSteps.push({
        action: "upgrade_affix",
        sealed_count_at_step: consSealedCount,
      });
    }
  }

  const defs: Array<{ name: string; description: string; steps: SimStep[] }> = [
    {
      name: "Aggressive",
      description: "Upgrade without sealing — maximizes tier gains with available FP",
      steps: aggressiveSteps,
    },
    {
      name: "Balanced",
      description: "Strategic sealing to preserve high-tier gains when FP runs low",
      steps: balancedSteps,
    },
    {
      name: "Conservative",
      description: "Seal all affixes before upgrading — preserves all current gains",
      steps: conservativeSteps,
    },
  ];

  return defs.map(({ name, description, steps }) => {
    if (steps.length === 0) {
      return {
        name,
        description,
        completion_chance: 0,
        expected_steps: 0,
        expected_fp_cost: 0,
      };
    }
    const sim = simulateSequence(forgePotential, steps, 2_000);
    const fpTotal = steps.reduce((sum, s) => sum + (FP_COSTS[s.action as keyof typeof FP_COSTS] ?? 0), 0);
    return {
      name,
      description,
      completion_chance: sim.completion_rate,
      expected_steps: steps.length,
      expected_fp_cost: fpTotal,
    };
  });
}

// ---------------------------------------------------------------------------
// Formatting helpers
// ---------------------------------------------------------------------------

export function tierLabel(tier: number): string {
  return `T${tier}`;
}
