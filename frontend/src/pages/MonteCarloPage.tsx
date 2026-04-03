/**
 * M19 — Monte Carlo Page
 *
 * Route: /monte-carlo
 *
 * Full-page Monte Carlo simulator. Generates mock results client-side using
 * a Box-Muller normal approximation, builds convergence data, and renders
 * the dashboard, distribution histogram, CI convergence chart, and build
 * comparison panel.
 */

import { useState, useCallback } from "react";

import MonteCarloDashboard, {
  type SimConfig,
  type MonteCarloSimResult,
} from "@/components/monte_carlo/MonteCarloDashboard";
import DistributionChart from "@/components/monte_carlo/DistributionChart";
import ConfidenceIntervalChart from "@/components/monte_carlo/ConfidenceIntervalChart";
import BuildComparisonPanel, {
  type BuildComparisonData,
} from "@/components/monte_carlo/BuildComparisonPanel";

// ---------------------------------------------------------------------------
// Simulation helpers
// ---------------------------------------------------------------------------

/** Box-Muller transform: returns a standard-normal random variate. */
function randNormal(): number {
  let u = 0, v = 0;
  while (u === 0) u = Math.random();
  while (v === 0) v = Math.random();
  return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
}

interface RunStats {
  mean: number;
  std: number;
  min: number;
  max: number;
  median: number;
  p5: number;
  p95: number;
  meanCrits: number;
  meanProcs: number;
  cv: number;
}

function runSim(config: SimConfig, nRuns: number): { samples: number[]; stats: RunStats; totalCrits: number; totalProcs: number } {
  const {
    base_damage,
    duration,
    crit_chance,
    crit_multiplier,
    proc_chance,
    proc_magnitude,
  } = config;

  const TICK_SIZE = 0.1;
  const ticks = Math.ceil(duration / TICK_SIZE);

  // Expected mean per tick (deterministic part)
  const tickMeanDmg =
    base_damage * (1 + crit_chance * (crit_multiplier - 1)) +
    proc_chance * proc_magnitude;

  // Standard deviation estimate: driven by variance from crits and procs
  const critVar = crit_chance * (1 - crit_chance) * Math.pow(base_damage * (crit_multiplier - 1), 2);
  const procVar = proc_chance * (1 - proc_chance) * Math.pow(proc_magnitude, 2);
  const tickStdDmg = Math.sqrt(critVar + procVar);

  const samples: number[] = [];
  let totalCrits = 0;
  let totalProcs = 0;

  for (let i = 0; i < nRuns; i++) {
    // Approximate run total as sum of 'ticks' iid random vars via CLT
    const runMean = tickMeanDmg * ticks;
    const runStd = tickStdDmg * Math.sqrt(ticks);
    const totalDmg = Math.max(0, runMean + runStd * randNormal());
    samples.push(totalDmg);

    // Estimate crit / proc counts for this run
    totalCrits += ticks * crit_chance;
    totalProcs += ticks * proc_chance;
  }

  // Compute stats
  const sorted = [...samples].sort((a, b) => a - b);
  const mean = samples.reduce((s, v) => s + v, 0) / nRuns;
  const variance = samples.reduce((s, v) => s + (v - mean) ** 2, 0) / nRuns;
  const std = Math.sqrt(variance);

  function pct(p: number): number {
    const idx = Math.min(Math.floor(p * nRuns), nRuns - 1);
    return sorted[idx];
  }

  return {
    samples,
    stats: {
      mean,
      std,
      min: sorted[0],
      max: sorted[nRuns - 1],
      median: pct(0.5),
      p5: pct(0.05),
      p95: pct(0.95),
      meanCrits: totalCrits / nRuns,
      meanProcs: totalProcs / nRuns,
      cv: mean > 0 ? std / mean : 0,
    },
    totalCrits,
    totalProcs,
  };
}

function buildDistribution(samples: number[], nBins = 40) {
  const min = Math.min(...samples);
  const max = Math.max(...samples);
  const binWidth = (max - min) / nBins || 1;
  const counts = new Array(nBins).fill(0);

  for (const v of samples) {
    const idx = Math.min(Math.floor((v - min) / binWidth), nBins - 1);
    counts[idx]++;
  }

  return counts.map((count, i) => ({
    bin_start: min + i * binWidth,
    bin_end: min + (i + 1) * binWidth,
    count,
    frequency: count / samples.length,
  }));
}

function buildConvergence(config: SimConfig): { n_runs: number; mean: number; lower: number; upper: number }[] {
  const checkpoints = [10, 50, 100, 250, 500, config.n_runs].filter(
    (v, i, a) => v <= config.n_runs && a.indexOf(v) === i
  );

  return checkpoints.map((n) => {
    const { stats } = runSim(config, n);
    // 95% CI for the mean: mean ± 1.96 * std / sqrt(n)
    const se = stats.std / Math.sqrt(n);
    return {
      n_runs: n,
      mean: stats.mean,
      lower: stats.mean - 1.96 * se,
      upper: stats.mean + 1.96 * se,
    };
  });
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

const DEFAULT_CONFIG: SimConfig = {
  n_runs: 1000,
  crit_chance: 0.25,
  crit_multiplier: 2.0,
  base_damage: 500,
  proc_chance: 0.15,
  proc_magnitude: 1200,
  duration: 60,
};

export default function MonteCarloPage() {
  const [result,          setResult]          = useState<MonteCarloSimResult | null>(null);
  const [isRunning,       setIsRunning]       = useState(false);
  const [distribution,    setDistribution]    = useState<ReturnType<typeof buildDistribution>>([]);
  const [convergenceData, setConvergenceData] = useState<{ n_runs: number; mean: number; lower: number; upper: number }[]>([]);
  // Build comparison is always null / placeholder for this phase
  const comparisonData: BuildComparisonData | null = null;

  const runSimulation = useCallback(async (config: SimConfig) => {
    setIsRunning(true);

    // Yield to the browser so the "Simulating…" text renders before the heavy loop
    await new Promise<void>((resolve) => setTimeout(resolve, 0));

    try {
      const { samples, stats } = runSim(config, config.n_runs);

      const simResult: MonteCarloSimResult = {
        mean_damage:     stats.mean,
        std_damage:      stats.std,
        min_damage:      stats.min,
        max_damage:      stats.max,
        median_damage:   stats.median,
        percentile_5:    stats.p5,
        percentile_95:   stats.p95,
        mean_crits:      stats.meanCrits,
        mean_procs:      stats.meanProcs,
        n_runs:          config.n_runs,
        cv:              stats.cv,
        // Reliability: higher n_runs and lower CV → higher score
        reliability_score: Math.min(1, (config.n_runs / 10000) * 0.5 + (1 - Math.min(stats.cv, 1)) * 0.5),
      };

      setResult(simResult);
      setDistribution(buildDistribution(samples));
      setConvergenceData(buildConvergence(config));
    } finally {
      setIsRunning(false);
    }
  }, []);

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-6">
      <div>
        <h1 className="font-display text-2xl text-forge-text">Monte Carlo Simulator</h1>
        <p className="font-body text-sm text-forge-dim mt-1">
          Stochastic damage simulation — characterise build consistency, variance,
          and expected output across thousands of randomised fight runs.
        </p>
      </div>

      {/* Dashboard: config + summary stats */}
      <MonteCarloDashboard
        result={result}
        isRunning={isRunning}
        onRun={runSimulation}
      />

      {/* Charts row — only shown once we have results */}
      {result && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DistributionChart
            distribution={distribution}
            mean={result.mean_damage}
            percentile_5={result.percentile_5}
            percentile_95={result.percentile_95}
          />
          <ConfidenceIntervalChart intervals={convergenceData} />
        </div>
      )}

      {/* Build comparison (always placeholder in Phase M) */}
      <BuildComparisonPanel comparison={comparisonData} />
    </div>
  );
}
