/**
 * OffenseCard + DefenseCard — phase 3 tests.
 *
 * Covers:
 *   - Ailment DPS row only appears for builds with meaningful ailment DPS.
 *   - Color indicators match benchmark thresholds.
 *   - Number formatting behaves on representative inputs.
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";

import OffenseCard from "@/components/features/build-workspace/analysis/OffenseCard";
import DefenseCard from "@/components/features/build-workspace/analysis/DefenseCard";
import {
  fmtNumber,
  fmtPct,
  fmtPctFromFraction,
  fmtPerSecond,
} from "@/components/features/build-workspace/analysis/format";
import type { DPSResult, DefenseResult } from "@/lib/api";

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

function makeDps(overrides: Partial<DPSResult> = {}): DPSResult {
  return {
    hit_damage: 100,
    average_hit: 120,
    dps: 5_000,
    effective_attack_speed: 1.5,
    crit_contribution_pct: 15,
    flat_damage_added: 20,
    bleed_dps: 0,
    ignite_dps: 0,
    poison_dps: 0,
    ailment_dps: 0,
    total_dps: 5_000,
    ...overrides,
  };
}

function makeDef(overrides: Partial<DefenseResult> = {}): DefenseResult {
  return {
    max_health: 1_200,
    effective_hp: 4_500,
    armor_reduction_pct: 25,
    avg_resistance: 55,
    fire_res: 60, cold_res: 60, lightning_res: 60, void_res: 40,
    necrotic_res: 40, physical_res: 40, poison_res: 40,
    dodge_chance_pct: 0, block_chance_pct: 0, block_mitigation_pct: 0,
    endurance_pct: 20, endurance_threshold_pct: 20,
    crit_avoidance_pct: 0, glancing_blow_pct: 0, stun_avoidance_pct: 0,
    ward_buffer: 0, total_ehp: 4_500,
    ward_regen_per_second: 0, ward_decay_per_second: 0, net_ward_per_second: 0,
    leech_pct: 0, health_on_kill: 0, mana_on_kill: 0, ward_on_kill: 0,
    health_regen: 0, mana_regen: 0,
    survivability_score: 55,
    sustain_score: 40,
    weaknesses: [],
    strengths: [],
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// 1. Ailment DPS row visibility
// ---------------------------------------------------------------------------

describe("OffenseCard — ailment row visibility", () => {
  it("does not render the ailment row when ailment_dps is 0", () => {
    render(<OffenseCard dps={makeDps({ ailment_dps: 0 })} stats={{}} />);
    expect(screen.queryByTestId("offense-row-ailment-dps")).toBeNull();
  });

  it("does not render the ailment row when ailment_dps is noise (<=1)", () => {
    render(<OffenseCard dps={makeDps({ ailment_dps: 0.7 })} stats={{}} />);
    expect(screen.queryByTestId("offense-row-ailment-dps")).toBeNull();
  });

  it("does not render the ailment row when ailment_dps is below 1 % of total", () => {
    render(
      <OffenseCard
        dps={makeDps({ ailment_dps: 50, total_dps: 100_000 })}
        stats={{}}
      />,
    );
    expect(screen.queryByTestId("offense-row-ailment-dps")).toBeNull();
  });

  it("does render the ailment row when ailment_dps is meaningful", () => {
    render(
      <OffenseCard
        dps={makeDps({ ailment_dps: 800, total_dps: 6_000 })}
        stats={{}}
      />,
    );
    expect(screen.getByTestId("offense-row-ailment-dps")).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// 2. Benchmark color indicators
// ---------------------------------------------------------------------------

describe("OffenseCard — benchmark tiers", () => {
  it('marks weak total DPS with data-tier="weak"', () => {
    render(<OffenseCard dps={makeDps({ total_dps: 1_000 })} stats={{}} />);
    expect(
      screen.getByTestId("offense-row-total-dps").getAttribute("data-tier"),
    ).toBe("weak");
  });

  it('marks average total DPS with data-tier="average"', () => {
    render(<OffenseCard dps={makeDps({ total_dps: 10_000 })} stats={{}} />);
    expect(
      screen.getByTestId("offense-row-total-dps").getAttribute("data-tier"),
    ).toBe("average");
  });

  it('marks strong total DPS with data-tier="strong"', () => {
    render(<OffenseCard dps={makeDps({ total_dps: 30_000 })} stats={{}} />);
    expect(
      screen.getByTestId("offense-row-total-dps").getAttribute("data-tier"),
    ).toBe("strong");
  });

  it("marks crit chance tier based on fraction input", () => {
    render(
      <OffenseCard dps={makeDps({})} stats={{ crit_chance: 0.5 }} />,
    );
    expect(
      screen.getByTestId("offense-row-crit-chance").getAttribute("data-tier"),
    ).toBe("strong");
  });
});

describe("DefenseCard — benchmark tiers", () => {
  it("marks weak effective_hp", () => {
    render(<DefenseCard defense={makeDef({ effective_hp: 1_000 })} />);
    expect(
      screen.getByTestId("defense-row-effective-hp").getAttribute("data-tier"),
    ).toBe("weak");
  });

  it("marks strong effective_hp", () => {
    render(<DefenseCard defense={makeDef({ effective_hp: 12_000 })} />);
    expect(
      screen.getByTestId("defense-row-effective-hp").getAttribute("data-tier"),
    ).toBe("strong");
  });

  it("marks weak avg_resistance", () => {
    render(<DefenseCard defense={makeDef({ avg_resistance: 40 })} />);
    expect(
      screen
        .getByTestId("defense-row-avg-resistance")
        .getAttribute("data-tier"),
    ).toBe("weak");
  });

  it("marks strong avg_resistance", () => {
    render(<DefenseCard defense={makeDef({ avg_resistance: 75 })} />);
    expect(
      screen
        .getByTestId("defense-row-avg-resistance")
        .getAttribute("data-tier"),
    ).toBe("strong");
  });

  it("renders the survivability progress bar", () => {
    render(<DefenseCard defense={makeDef({ survivability_score: 72 })} />);
    expect(screen.getByTestId("defense-row-survivability-bar")).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// 3. Number formatting
// ---------------------------------------------------------------------------

describe("format helpers", () => {
  it("adds thousands separators for medium numbers", () => {
    expect(fmtNumber(1_234)).toBe("1.2K");
    expect(fmtNumber(999)).toBe("999");
    expect(fmtNumber(1_500_000)).toBe("1.5M");
  });

  it("returns em-dash for missing / non-finite numbers", () => {
    expect(fmtNumber(null)).toBe("—");
    expect(fmtNumber(undefined)).toBe("—");
    expect(fmtNumber(NaN)).toBe("—");
    expect(fmtNumber(Infinity)).toBe("—");
  });

  it("renders percentages with one decimal", () => {
    expect(fmtPct(12.345)).toBe("12.3%");
    expect(fmtPct(0)).toBe("0.0%");
  });

  it("expands 0..1 fractions into percent strings", () => {
    expect(fmtPctFromFraction(0.25)).toBe("25.0%");
    expect(fmtPctFromFraction(1)).toBe("100.0%");
  });

  it("renders per-second speeds with two decimals", () => {
    expect(fmtPerSecond(1.234)).toBe("1.23/s");
    expect(fmtPerSecond(2)).toBe("2.00/s");
  });
});
