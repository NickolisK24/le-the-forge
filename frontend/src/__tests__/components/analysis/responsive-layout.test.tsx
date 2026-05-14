/**
 * Responsive layout contract for the phase-3 analysis composition.
 *
 * These tests pin the Tailwind breakpoint classnames rather than actually
 * resizing the viewport — jsdom does not evaluate CSS — so they catch
 * regressions where someone accidentally drops a `grid-cols-*` or
 * `min-h-[44px]` guard without having to spin up a browser. Combined with
 * the project-owner's manual 375 px pass documented in phase-3 notes §7,
 * this gives reasonable coverage.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";

// Minimal mocks so the analysis subtree mounts without pulling in slug-
// scoped panels.
vi.mock("@/components/features/build/BossEncounterPanel", () => ({
  default: () => <div data-testid="mock-boss-panel" />,
}));
vi.mock("@/components/features/build/CorruptionScalingPanel", () => ({
  default: () => <div data-testid="mock-corruption-panel" />,
}));
vi.mock("@/components/features/build/GearUpgradePanel", () => ({
  default: () => <div data-testid="mock-gear-panel" />,
}));

import BuildScoreCard from "@/components/features/build-workspace/analysis/BuildScoreCard";
import SkillsSummaryTable from "@/components/features/build-workspace/analysis/SkillsSummaryTable";
import AdvancedAnalysisAccordion from "@/components/features/build-workspace/analysis/AdvancedAnalysisAccordion";
import PrimarySkillBreakdown from "@/components/features/build-workspace/analysis/PrimarySkillBreakdown";

import type { BuildSimulationResult } from "@/lib/api";

function mkResult(): BuildSimulationResult {
  return {
    primary_skill: "Fireball",
    skill_level: 20,
    stats: {},
    dps: {
      hit_damage: 100, average_hit: 120, dps: 10_000,
      effective_attack_speed: 1.2, crit_contribution_pct: 20,
      flat_damage_added: 0, bleed_dps: 0, ignite_dps: 0,
      poison_dps: 0, ailment_dps: 0, total_dps: 10_000,
    },
    monte_carlo: {
      mean_dps: 10_000, min_dps: 0, max_dps: 0, std_dev: 0,
      percentile_25: 0, percentile_75: 0, n_simulations: 0,
    },
    defense: {
      max_health: 1_000, effective_hp: 5_000, armor_reduction_pct: 20,
      avg_resistance: 55, fire_res: 0, cold_res: 0, lightning_res: 0,
      void_res: 0, necrotic_res: 0, physical_res: 0, poison_res: 0,
      dodge_chance_pct: 0, block_chance_pct: 0, block_mitigation_pct: 0,
      endurance_pct: 0, endurance_threshold_pct: 0,
      crit_avoidance_pct: 0, glancing_blow_pct: 0, stun_avoidance_pct: 0,
      ward_buffer: 0, total_ehp: 5_000, ward_regen_per_second: 0,
      ward_decay_per_second: 0, net_ward_per_second: 0,
      leech_pct: 0, health_on_kill: 0, mana_on_kill: 0, ward_on_kill: 0,
      health_regen: 0, mana_regen: 0,
      survivability_score: 60, sustain_score: 50,
      weaknesses: [], strengths: [],
    },
    stat_upgrades: [],
    seed: null,
    dps_per_skill: [],
    combined_dps: 10_000,
  };
}

// ---------------------------------------------------------------------------
// Score-card: pills must stack vertically on mobile.
// ---------------------------------------------------------------------------

describe("BuildScoreCard — mobile layout", () => {
  it("pills use a single-column grid at base width and 3-col at sm+", () => {
    render(
      <BuildScoreCard
        result={mkResult()}
        status="success"
        characterClass="Mage"
        mastery="Sorcerer"
      />,
    );
    // The pills live in the second flex child of the card. Match by tier
    // testids and climb to the grid parent.
    const pill = screen.getAllByTestId("score-pill-average")[0];
    const grid = pill.parentElement!;
    expect(grid.className).toMatch(/grid-cols-1/);
    expect(grid.className).toMatch(/sm:grid-cols-3/);
  });

  it("change-skill button has at least a 44 px mobile tap target", () => {
    render(
      <BuildScoreCard
        result={mkResult()}
        status="success"
        characterClass="Mage"
        mastery="Sorcerer"
        onOpenSkills={() => {}}
      />,
    );
    const btn = screen.getByTestId("score-card-change-skill");
    expect(btn.className).toMatch(/min-h-\[44px\]/);
  });
});

// ---------------------------------------------------------------------------
// Skills summary table — horizontally scrollable on mobile.
// ---------------------------------------------------------------------------

describe("SkillsSummaryTable — mobile layout", () => {
  it("wraps the table in an overflow-x container with a minimum width", () => {
    render(
      <SkillsSummaryTable
        skills={[
          { slot: 0, skill_name: "Fireball", points_allocated: 0 },
        ]}
        dpsPerSkill={[]}
        primaryDps={null}
        primarySkillName=""
      />,
    );
    const table = screen.getByRole("table");
    expect(table.className).toMatch(/min-w-\[480px\]/);
    const scroll = table.parentElement!;
    expect(scroll.className).toMatch(/overflow-x-auto/);
  });

  it("row content provides at least a 44 px tap target on mobile", () => {
    render(
      <SkillsSummaryTable
        skills={[
          { slot: 0, skill_name: "Fireball", points_allocated: 0 },
        ]}
        dpsPerSkill={[]}
        primaryDps={null}
        primarySkillName=""
      />,
    );
    // First cell body carries the min-h guard; rows are clickable so any
    // 44 px-tall child in the row is a sufficient target on mobile.
    const row = screen.getByTestId("skills-row-0");
    const tallChild = row.querySelector("[class*='min-h-[44px]']");
    expect(tallChild).not.toBeNull();
    // And the row is still clickable to expand.
    fireEvent.click(row);
    expect(screen.getByTestId("skills-row-0-detail")).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// Advanced accordion — header wraps on narrow widths + 44 px tap target.
// ---------------------------------------------------------------------------

describe("AdvancedAnalysisAccordion — mobile layout", () => {
  it("header wraps cleanly and carries a 44 px tap target", () => {
    render(<AdvancedAnalysisAccordion slug="my-build" />);
    const toggle = screen.getByTestId("advanced-analysis-toggle");
    expect(toggle.className).toMatch(/min-h-\[44px\]/);
    const title = toggle.querySelector("span");
    expect(title?.className).toMatch(/whitespace-normal/);
    expect(title?.className).toMatch(/break-words/);
  });
});

// ---------------------------------------------------------------------------
// Primary-skill breakdown — Change button is at least 44 px.
// ---------------------------------------------------------------------------

describe("PrimarySkillBreakdown — mobile layout", () => {
  it('the Change button is at least 44 px tall on mobile', () => {
    render(
      <PrimarySkillBreakdown
        skillName="Fireball"
        dps={mkResult().dps}
        onOpenSkills={() => {}}
      />,
    );
    const btn = screen.getByTestId("primary-skill-change");
    expect(btn.className).toMatch(/min-h-\[44px\]/);
  });
});
