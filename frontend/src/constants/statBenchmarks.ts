/**
 * Approximate benchmarks for common stats at level 90+. These are used to
 * colour-code values on the simulation page (green / amber / red) so that
 * players can immediately tell whether a given number is good, fine, or
 * needs work. The numbers are rough targets — varied builds and content
 * types will shift them — hence the disclaimer.
 */

export const STAT_BENCHMARKS: Record<string, { weak: number; strong: number }> = {
  total_dps:            { weak: 5_000, strong: 20_000 },
  dps:                  { weak: 5_000, strong: 20_000 },
  effective_hp:         { weak: 3_000, strong: 8_000 },
  total_ehp:            { weak: 3_000, strong: 10_000 },
  survivability_score:  { weak: 50,    strong: 75 },
  crit_chance:          { weak: 0.20,  strong: 0.40 },
  avg_resistance:       { weak: 50,    strong: 70 },
  armor_mitigation_pct: { weak: 20,    strong: 50 },
  dodge_chance_pct:     { weak: 15,    strong: 40 },
};

export type BenchmarkTier = "strong" | "average" | "weak";

export function getBenchmarkTier(key: string, value: number): BenchmarkTier {
  const bench = STAT_BENCHMARKS[key];
  if (!bench) return "average";
  if (value >= bench.strong) return "strong";
  if (value <= bench.weak) return "weak";
  return "average";
}

export const BENCHMARK_COLORS: Record<BenchmarkTier, string> = {
  strong:  "#4ade80",  // green
  average: "#f0a020",  // forge-amber
  weak:    "#f87171",  // red
};

export const BENCHMARK_DISCLAIMER =
  "Benchmarks are approximate and vary by build type and content.";
