/**
 * Benchmark classification test.
 *
 * Verifies the exact boundary behaviour of `getBenchmarkTier()` at the
 * thresholds the phase-3 prompt specifies. Off-by-one bugs here are easy
 * to introduce and invisible in visual review, so we pin them down.
 */

import { describe, it, expect } from "vitest";
import {
  STAT_BENCHMARKS,
  BENCHMARK_COLORS,
  BENCHMARK_DISCLAIMER,
  getBenchmarkTier,
} from "@/constants/statBenchmarks";

describe("STAT_BENCHMARKS — prompt-specified thresholds", () => {
  it("uses the exact DPS thresholds (weak 5000 / strong 20000)", () => {
    expect(STAT_BENCHMARKS.total_dps).toEqual({ weak: 5_000, strong: 20_000 });
    expect(STAT_BENCHMARKS.dps).toEqual({ weak: 5_000, strong: 20_000 });
  });

  it("uses the exact EHP thresholds (weak 3000 / strong 8000)", () => {
    expect(STAT_BENCHMARKS.effective_hp).toEqual({ weak: 3_000, strong: 8_000 });
  });

  it("uses the exact survivability thresholds (weak 50 / strong 75)", () => {
    expect(STAT_BENCHMARKS.survivability_score).toEqual({ weak: 50, strong: 75 });
  });

  it("uses the exact crit-chance thresholds (weak 0.20 / strong 0.40, fraction)", () => {
    expect(STAT_BENCHMARKS.crit_chance).toEqual({ weak: 0.2, strong: 0.4 });
  });

  it("uses the exact average-resistance thresholds (weak 50 / strong 70)", () => {
    expect(STAT_BENCHMARKS.avg_resistance).toEqual({ weak: 50, strong: 70 });
  });
});

describe("getBenchmarkTier — DPS boundary values", () => {
  it("classifies weak at and below the weak threshold", () => {
    expect(getBenchmarkTier("total_dps", 0)).toBe("weak");
    expect(getBenchmarkTier("total_dps", 4_999)).toBe("weak");
    expect(getBenchmarkTier("total_dps", 5_000)).toBe("weak");
  });

  it("classifies average between thresholds (exclusive of each)", () => {
    expect(getBenchmarkTier("total_dps", 5_001)).toBe("average");
    expect(getBenchmarkTier("total_dps", 12_000)).toBe("average");
    expect(getBenchmarkTier("total_dps", 19_999)).toBe("average");
  });

  it("classifies strong at and above the strong threshold", () => {
    expect(getBenchmarkTier("total_dps", 20_000)).toBe("strong");
    expect(getBenchmarkTier("total_dps", 50_000)).toBe("strong");
  });
});

describe("getBenchmarkTier — EHP boundary values", () => {
  it("classifies 3,000 as weak and 3,001 as average", () => {
    expect(getBenchmarkTier("effective_hp", 3_000)).toBe("weak");
    expect(getBenchmarkTier("effective_hp", 3_001)).toBe("average");
  });

  it("classifies 8,000 as strong", () => {
    expect(getBenchmarkTier("effective_hp", 8_000)).toBe("strong");
    expect(getBenchmarkTier("effective_hp", 7_999)).toBe("average");
  });
});

describe("getBenchmarkTier — survivability boundary values", () => {
  it("classifies 50 as weak and 51 as average", () => {
    expect(getBenchmarkTier("survivability_score", 50)).toBe("weak");
    expect(getBenchmarkTier("survivability_score", 51)).toBe("average");
  });

  it("classifies 75 as strong", () => {
    expect(getBenchmarkTier("survivability_score", 75)).toBe("strong");
    expect(getBenchmarkTier("survivability_score", 74)).toBe("average");
  });
});

describe("getBenchmarkTier — crit chance (fraction input)", () => {
  it("classifies 0.20 as weak, 0.21 as average, 0.40 as strong", () => {
    expect(getBenchmarkTier("crit_chance", 0.2)).toBe("weak");
    expect(getBenchmarkTier("crit_chance", 0.21)).toBe("average");
    expect(getBenchmarkTier("crit_chance", 0.4)).toBe("strong");
  });
});

describe("getBenchmarkTier — unknown keys", () => {
  it('returns "average" for any key missing from the benchmark table', () => {
    expect(getBenchmarkTier("no_such_stat", 0)).toBe("average");
    expect(getBenchmarkTier("no_such_stat", 1_000_000)).toBe("average");
  });
});

describe("BENCHMARK_COLORS and disclaimer", () => {
  it("defines a hex color for each tier", () => {
    expect(BENCHMARK_COLORS.strong).toMatch(/^#[0-9a-f]{6}$/i);
    expect(BENCHMARK_COLORS.average).toMatch(/^#[0-9a-f]{6}$/i);
    expect(BENCHMARK_COLORS.weak).toMatch(/^#[0-9a-f]{6}$/i);
  });

  it("ships the approximate-benchmarks disclaimer string", () => {
    expect(BENCHMARK_DISCLAIMER).toContain("approximate");
    expect(BENCHMARK_DISCLAIMER).toContain("build type");
  });
});
