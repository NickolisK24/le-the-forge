/**
 * Client-side crafting math — mirrors app/services/craft_service.py.
 *
 * We replicate this on the frontend so the UI can show live risk
 * calculations as the user adjusts the instability slider,
 * without a round-trip to the backend for every input change.
 *
 * The backend is the authoritative source for persisted outcomes.
 * These are display-only calculations.
 */

import type {
  CraftAffix,
  OptimalPathStep,
  SimulationResult,
  StrategyComparison,
} from "@/types";

export const MAX_INSTABILITY = 80;
const SEAL_RISK_THRESHOLD = 0.20;
const TARGET_TIER = 4;
const PERFECT_ROLL_THRESHOLD = 0.95;

// ---------------------------------------------------------------------------
// FP costs
// ---------------------------------------------------------------------------

export const FP_COSTS: Record<string, number> = {
  add_affix: 4,
  upgrade_affix: 5,
  seal_affix: 8,
  unseal_affix: 2,
  remove_affix: 3,
};

export function fpCost(action: string): number {
  return FP_COSTS[action] ?? 4;
}

// ---------------------------------------------------------------------------
// Instability gain ranges (mirrors INSTABILITY_GAINS in craft_service.py)
// ---------------------------------------------------------------------------

const INSTABILITY_GAINS: Record<string, [number, number]> = {
  add_affix: [3, 7],
  upgrade_affix: [4, 10],
  seal_affix: [0, 0],
  unseal_affix: [1, 3],
  remove_affix: [2, 5],
};

/** Expected (mean) instability gain for an action, accounting for 5% perfect rolls. */
export function expectedInstabilityGain(action: string): number {
  const [lo, hi] = INSTABILITY_GAINS[action] ?? [3, 8];
  if (lo === hi) return lo;
  const normalMean = (lo + hi) / 2;
  return 0.05 * lo + 0.95 * normalMean;
}

// ---------------------------------------------------------------------------
// Risk calculation
// ---------------------------------------------------------------------------

/**
 * Returns fracture probability (0.0–1.0).
 * Each sealed affix reduces effective instability by 12.
 */
export function fractureRisk(instability: number, sealedCount = 0): number {
  const effective = Math.max(0, instability - sealedCount * 12);
  const base = Math.pow(effective / MAX_INSTABILITY, 2);
  return Math.min(base, 1.0);
}

/** Returns fracture risk as a 0–100 percentage, rounded to 1 decimal. */
export function fractureRiskPct(instability: number, sealedCount = 0): number {
  return Math.round(fractureRisk(instability, sealedCount) * 1000) / 10;
}

/** Returns success probability as 0–100 percentage. */
export function successPct(instability: number, sealedCount = 0): number {
  return Math.round((1 - fractureRisk(instability, sealedCount)) * 1000) / 10;
}

/** Risk colour classification for UI use. */
export type RiskLevel = "safe" | "moderate" | "dangerous" | "critical";

export function riskLevel(riskPct: number): RiskLevel {
  if (riskPct < 20) return "safe";
  if (riskPct < 45) return "moderate";
  if (riskPct < 70) return "dangerous";
  return "critical";
}

export const RISK_COLORS: Record<RiskLevel, string> = {
  safe: "#7cb87a",
  moderate: "#e8891a",
  dangerous: "#e05050",
  critical: "#cc2020",
};

// ---------------------------------------------------------------------------
// Optimal path search (mirrors optimal_path_search in craft_service.py)
// ---------------------------------------------------------------------------

export function optimalPath(
  instability: number,
  affixes: CraftAffix[],
  forgePotential = 28,
): OptimalPathStep[] {
  const steps: OptimalPathStep[] = [];
  let inst = instability;
  let fp = forgePotential;
  const current = affixes.map((a) => ({ ...a }));
  let sealedCount = current.filter((a) => a.sealed).length;
  let cumulativeSurvival = 1.0;

  const toUpgrade = current.filter((a) => !a.sealed && a.tier < TARGET_TIER);

  for (const targetAffix of toUpgrade) {
    // Check if we should seal something before working on this affix
    const preRisk = fractureRisk(inst, sealedCount);

    if (preRisk > SEAL_RISK_THRESHOLD) {
      const candidates = current.filter(
        (a) => !a.sealed && a.name !== targetAffix.name,
      );
      if (candidates.length > 0 && fp >= FP_COSTS.seal_affix) {
        const toSeal = candidates.reduce((best, a) =>
          a.tier > best.tier ? a : best,
        );
        steps.push({
          action: "seal_affix",
          affix: toSeal.name,
          risk_pct: 0,
          cumulative_survival_pct: Math.round(cumulativeSurvival * 1000) / 10,
          sealed_count_at_step: sealedCount,
          note: `Seal "${toSeal.name}" (T${toSeal.tier}) — risk at ${fractureRiskPct(inst, sealedCount).toFixed(1)}%, drops to ${fractureRiskPct(inst, sealedCount + 1).toFixed(1)}% after seal`,
        });
        toSeal.sealed = true;
        sealedCount++;
        fp -= FP_COSTS.seal_affix;
      }
    }

    // Upgrade target affix step by step to TARGET_TIER
    while (targetAffix.tier < TARGET_TIER && fp >= FP_COSTS.upgrade_affix) {
      let currentRisk = fractureRisk(inst, sealedCount);

      // Re-check threshold mid-sequence
      if (currentRisk > SEAL_RISK_THRESHOLD) {
        const candidates = current.filter(
          (a) => !a.sealed && a.name !== targetAffix.name,
        );
        if (candidates.length > 0 && fp >= FP_COSTS.seal_affix) {
          const toSeal = candidates.reduce((best, a) =>
            a.tier > best.tier ? a : best,
          );
          steps.push({
            action: "seal_affix",
            affix: toSeal.name,
            risk_pct: 0,
            cumulative_survival_pct: Math.round(cumulativeSurvival * 1000) / 10,
            sealed_count_at_step: sealedCount,
            note: `Seal "${toSeal.name}" — instability climbing, protect T${toSeal.tier} gains`,
          });
          toSeal.sealed = true;
          sealedCount++;
          fp -= FP_COSTS.seal_affix;
          currentRisk = fractureRisk(inst, sealedCount);
        }
      }

      // Upgrade step
      cumulativeSurvival *= 1.0 - currentRisk;
      targetAffix.tier = Math.min(5, targetAffix.tier + 1);

      steps.push({
        action: "upgrade_affix",
        affix: `${targetAffix.name} → T${targetAffix.tier}`,
        risk_pct: Math.round(currentRisk * 1000) / 10,
        cumulative_survival_pct: Math.round(cumulativeSurvival * 1000) / 10,
        sealed_count_at_step: sealedCount,
        note: `Upgrade to T${targetAffix.tier} — ${(currentRisk * 100).toFixed(1)}% fracture risk at this step`,
      });

      inst = Math.min(MAX_INSTABILITY, inst + expectedInstabilityGain("upgrade_affix"));
      fp -= FP_COSTS.upgrade_affix;
    }
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
  instability: number,
  forgePotential: number,
  proposedSteps: SimStep[],
  nSimulations = 3_000,
): SimulationResult {
  const n = nSimulations;
  const fractureAtStep = new Array<number>(proposedSteps.length).fill(0);
  let survivedAll = 0;
  const finalInstabilities: number[] = [];

  for (let i = 0; i < n; i++) {
    let inst = instability;
    let fp = forgePotential;
    let fractured = false;

    for (let si = 0; si < proposedSteps.length; si++) {
      const step = proposedSteps[si];
      const cost = FP_COSTS[step.action] ?? 4;

      if (fp < cost) break;

      const risk = fractureRisk(inst, step.sealed_count_at_step);
      const roll = Math.random();

      if (roll < risk) {
        fractureAtStep[si]++;
        fractured = true;
        break;
      }

      const [lo, hi] = INSTABILITY_GAINS[step.action] ?? [3, 8];
      let gain: number;
      if (lo === hi) {
        gain = lo;
      } else if (roll > PERFECT_ROLL_THRESHOLD) {
        gain = lo;
      } else {
        gain = lo + Math.floor(Math.random() * (hi - lo + 1));
      }

      inst = Math.min(MAX_INSTABILITY, inst + gain);
      fp -= cost;
    }

    if (!fractured) {
      survivedAll++;
      finalInstabilities.push(inst);
    }
  }

  // Cumulative survival curve
  let cumulativeFractures = 0;
  const stepSurvival = fractureAtStep.map((count) => {
    cumulativeFractures += count;
    return Math.round((1 - cumulativeFractures / n) * 10_000) / 10_000;
  });

  const totalFractures = fractureAtStep.reduce((a, b) => a + b, 0);
  const sorted = [...finalInstabilities].sort((a, b) => a - b);
  const medianInst =
    sorted.length > 0 ? sorted[Math.floor(sorted.length / 2)] : instability;

  return {
    brick_chance: Math.round((totalFractures / n) * 10_000) / 10_000,
    perfect_item_chance: Math.round((survivedAll / n) * 10_000) / 10_000,
    step_survival_curve: stepSurvival,
    step_fracture_rates: fractureAtStep.map(
      (f) => Math.round((f / n) * 10_000) / 10_000,
    ),
    median_instability: medianInst,
    n_simulations: n,
  };
}

// ---------------------------------------------------------------------------
// Strategy comparison (mirrors compare_strategies in craft_service.py)
// ---------------------------------------------------------------------------

export function compareStrategies(
  instability: number,
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
  const balancedRaw = optimalPath(instability, affixes, forgePotential);
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
      description: "Upgrade without sealing — high risk, no FP spent on seals",
      steps: aggressiveSteps,
    },
    {
      name: "Balanced",
      description: "Seal strategically when fracture risk exceeds 20%",
      steps: balancedSteps,
    },
    {
      name: "Conservative",
      description: "Seal all affixes before any upgrade — maximum protection",
      steps: conservativeSteps,
    },
  ];

  return defs.map(({ name, description, steps }) => {
    if (steps.length === 0) {
      return {
        name,
        description,
        brick_chance: 0,
        perfect_item_chance: 1,
        expected_steps: 0,
        expected_fp_cost: 0,
      };
    }
    const sim = simulateSequence(instability, forgePotential, steps, 2_000);
    const fpTotal = steps.reduce((sum, s) => sum + (FP_COSTS[s.action] ?? 4), 0);
    return {
      name,
      description,
      brick_chance: sim.brick_chance,
      perfect_item_chance: sim.perfect_item_chance,
      expected_steps: steps.length,
      expected_fp_cost: fpTotal,
    };
  });
}

// ---------------------------------------------------------------------------
// Formatting helpers
// ---------------------------------------------------------------------------

export function formatRiskPct(pct: number): string {
  return `${pct.toFixed(1)}%`;
}

export function instabilityColor(instability: number): string {
  if (instability < 30) return "#7cb87a";
  if (instability < 55) return "#e8891a";
  return "#e05050";
}

export function tierLabel(tier: number): string {
  return `T${tier}`;
}
