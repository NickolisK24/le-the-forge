/**
 * PrimarySkillBreakdown — phase 3 tests.
 *
 * Covers:
 *   - Renders each of the four per-skill stats.
 *   - Contribution bar renders when segments are computable.
 *   - Fallback "not available" note renders when neither total DPS nor
 *     crit contribution is present.
 *   - "Change" button calls onOpenSkills.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";

import PrimarySkillBreakdown, {
  computeContributionSegments,
} from "@/components/features/build-workspace/analysis/PrimarySkillBreakdown";
import type { DPSResult } from "@/lib/api";

function makeDps(overrides: Partial<DPSResult> = {}): DPSResult {
  return {
    hit_damage: 320,
    average_hit: 400,
    dps: 8_000,
    effective_attack_speed: 1.3,
    crit_contribution_pct: 20,
    flat_damage_added: 40,
    bleed_dps: 0,
    ignite_dps: 0,
    poison_dps: 0,
    ailment_dps: 0,
    total_dps: 8_000,
    ...overrides,
  };
}

describe("computeContributionSegments", () => {
  it("returns three segments summing to 100 % when dps > 0", () => {
    const segs = computeContributionSegments(makeDps({ crit_contribution_pct: 20 }))!;
    expect(segs).toHaveLength(3);
    const sum = segs.reduce((a, s) => a + s.pct, 0);
    expect(Math.abs(sum - 100)).toBeLessThan(0.01);
  });

  it("returns null when both total DPS and crit contribution are zero", () => {
    expect(
      computeContributionSegments(
        makeDps({ total_dps: 0, dps: 0, crit_contribution_pct: 0 }),
      ),
    ).toBeNull();
  });

  it("clamps crit contribution above 100 %", () => {
    const segs = computeContributionSegments(
      makeDps({ crit_contribution_pct: 150 }),
    )!;
    expect(segs[1].pct).toBe(100);
  });
});

describe("PrimarySkillBreakdown — render", () => {
  it("renders the four stat cells with formatted values", () => {
    render(
      <PrimarySkillBreakdown
        skillName="Fireball"
        dps={makeDps({
          hit_damage: 1_500,
          average_hit: 2_000,
          effective_attack_speed: 1.25,
          total_dps: 12_345,
        })}
      />,
    );
    expect(screen.getByTestId("primary-skill-hit-damage")).toHaveTextContent("1.5K");
    expect(screen.getByTestId("primary-skill-average-hit")).toHaveTextContent("2.0K");
    expect(screen.getByTestId("primary-skill-attack-speed")).toHaveTextContent("1.25/s");
    expect(screen.getByTestId("primary-skill-total-dps")).toHaveTextContent("12.3K");
  });

  it("renders the contribution bar when segments are available", () => {
    render(
      <PrimarySkillBreakdown
        skillName="Fireball"
        dps={makeDps({ crit_contribution_pct: 25, total_dps: 9_000 })}
      />,
    );
    expect(screen.getByTestId("primary-skill-contribution-bar")).toBeInTheDocument();
    expect(screen.queryByTestId("primary-skill-no-breakdown")).toBeNull();
  });

  it("renders the fallback note when no contribution can be computed", () => {
    render(
      <PrimarySkillBreakdown
        skillName="Fireball"
        dps={makeDps({ total_dps: 0, dps: 0, crit_contribution_pct: 0 })}
      />,
    );
    expect(screen.getByTestId("primary-skill-no-breakdown")).toBeInTheDocument();
    expect(screen.queryByTestId("primary-skill-contribution-bar")).toBeNull();
  });

  it("renders a placeholder dash when skillName is empty", () => {
    render(<PrimarySkillBreakdown skillName="" dps={makeDps()} />);
    expect(
      screen.getByTestId("primary-skill-breakdown").querySelector("header"),
    ).toHaveTextContent("—");
  });
});

describe("PrimarySkillBreakdown — change button", () => {
  it('invokes onOpenSkills when "Change" is clicked', () => {
    const onOpenSkills = vi.fn();
    render(
      <PrimarySkillBreakdown
        skillName="Fireball"
        dps={makeDps()}
        onOpenSkills={onOpenSkills}
      />,
    );
    fireEvent.click(screen.getByTestId("primary-skill-change"));
    expect(onOpenSkills).toHaveBeenCalledTimes(1);
  });

  it("hides the button when no callback is supplied", () => {
    render(<PrimarySkillBreakdown skillName="Fireball" dps={makeDps()} />);
    expect(screen.queryByTestId("primary-skill-change")).toBeNull();
  });
});
