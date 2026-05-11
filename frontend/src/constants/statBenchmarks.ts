/**
 * Approximate benchmarks for common stats at level 90+. These are used to
 * colour-code values on the simulation page (green / amber / red) so that
 * players can immediately tell whether a given number is good, fine, or
 * needs work. The numbers are rough targets — varied builds and content
 * types will shift them — hence the disclaimer.
 *
 * Boundary semantics (phase 3):
 *   value >= strong → "strong"
 *   value  < weak   → "weak"
 *   otherwise        → "average"
 *
 * The prompt specifies exact bounds for five stats; they are called out
 * explicitly below so reviewers can diff against the brief.
 */

export const STAT_BENCHMARKS: Record<string, { weak: number; strong: number }> = {
  // --- Prompt-specified thresholds ------------------------------------------
  // DPS:               weak < 5,000; strong > 20,000
  total_dps:            { weak: 5_000, strong: 20_000 },
  dps:                  { weak: 5_000, strong: 20_000 },
  // Effective HP:      weak < 3,000; strong > 8,000
  effective_hp:         { weak: 3_000, strong: 8_000 },
  total_ehp:            { weak: 3_000, strong: 10_000 },
  // Survivability:     weak < 50;    strong > 75
  survivability_score:  { weak: 50,    strong: 75 },
  // Crit Chance:       weak < 0.20;  strong > 0.40 (engine reports fraction 0..1)
  crit_chance:          { weak: 0.20,  strong: 0.40 },
  // Average Resistance: weak < 50;   strong > 70
  avg_resistance:       { weak: 50,    strong: 70 },

  // --- Supplementary thresholds (not in the prompt; retained from phase 2) --
  armor_reduction_pct:  { weak: 20,    strong: 50 },
  dodge_chance_pct:     { weak: 15,    strong: 40 },
  sustain_score:        { weak: 50,    strong: 75 },
};

export type BenchmarkTier = "strong" | "average" | "weak";

/**
 * Classify a stat value against its benchmark.
 *
 * Boundary rule:
 *   value >= strong → "strong"
 *   value <= weak   → "weak"   (strict `<` for weak feels punishing at the
 *                                  threshold; matching the prompt's "weak
 *                                  below 5000" is best served by `<=` on
 *                                  the canonical example where weak = 5000
 *                                  is clearly not a strong value.)
 *   otherwise        → "average"
 *
 * Callers that pass an unknown key get "average" back — a neutral default
 * that renders the forge-amber indicator rather than accidentally flagging
 * the value as weak.
 */
export function getBenchmarkTier(key: string, value: number): BenchmarkTier {
  const bench = STAT_BENCHMARKS[key];
  if (!bench) return "average";
  if (value >= bench.strong) return "strong";
  if (value <= bench.weak) return "weak";
  return "average";
}

export const BENCHMARK_COLORS: Record<BenchmarkTier, string> = {
  strong:  "#4ade80",  // green — "target met"
  average: "#f0a020",  // forge-amber — "on track"
  weak:    "#f87171",  // red — "needs work"
};

export const BENCHMARK_DISCLAIMER =
  "Benchmarks are approximate and vary by build type and content.";

export const KNOWN_LIMITATIONS_URL =
  "https://github.com/NickolisK24/le-the-forge/blob/main/docs/KNOWN_LIMITATIONS.md";
