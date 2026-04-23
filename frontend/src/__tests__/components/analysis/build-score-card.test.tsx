/**
 * BuildScoreCard — phase 3 tests.
 *
 * Covers the five contract points from the phase-3 prompt:
 *   1. Letter-grade boundary transitions at 45, 60, 75, 90.
 *   2. Summary sentence logic across all four prompt branches.
 *   3. Pill color tier matches benchmark thresholds (weak/average/strong).
 *   4. Skeleton renders during pending with no previous result.
 *   5. Card is hidden when idle with no result.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";

import BuildScoreCard, {
  computeBuildRating,
  computeSummary,
  elementalResistancesAreTight,
  DPS_UPPER_BOUND,
  EHP_UPPER_BOUND,
} from "@/components/features/build-workspace/analysis/BuildScoreCard";
import type { BuildSimulationResult } from "@/lib/api";

// ---------------------------------------------------------------------------
// Fixture helpers
// ---------------------------------------------------------------------------

function makeResult(overrides: Partial<{
  dps: number;
  ehp: number;
  survivabilityScore: number;
  primarySkill: string;
  weaknesses: string[];
  topUpgradeLabel: string;
}> = {}): BuildSimulationResult {
  const dps = overrides.dps ?? 10_000;
  const ehp = overrides.ehp ?? 5_000;
  const surv = overrides.survivabilityScore ?? 60;
  return {
    primary_skill: overrides.primarySkill ?? "Fireball",
    skill_level: 20,
    stats: {},
    dps: {
      hit_damage: 0, average_hit: 0, dps: dps, effective_attack_speed: 1,
      crit_contribution_pct: 0, flat_damage_added: 0,
      bleed_dps: 0, ignite_dps: 0, poison_dps: 0, ailment_dps: 0,
      total_dps: dps,
    },
    monte_carlo: {
      mean_dps: dps, min_dps: dps, max_dps: dps, std_dev: 0,
      percentile_25: dps, percentile_75: dps, n_simulations: 100,
    },
    defense: {
      max_health: 1000, effective_hp: ehp,
      armor_reduction_pct: 0, avg_resistance: 0,
      fire_res: 0, cold_res: 0, lightning_res: 0, void_res: 0,
      necrotic_res: 0, physical_res: 0, poison_res: 0,
      dodge_chance_pct: 0, block_chance_pct: 0, block_mitigation_pct: 0,
      endurance_pct: 0, endurance_threshold_pct: 0,
      crit_avoidance_pct: 0, glancing_blow_pct: 0, stun_avoidance_pct: 0,
      ward_buffer: 0, total_ehp: ehp,
      ward_regen_per_second: 0, ward_decay_per_second: 0, net_ward_per_second: 0,
      leech_pct: 0, health_on_kill: 0, mana_on_kill: 0, ward_on_kill: 0,
      health_regen: 0, mana_regen: 0,
      survivability_score: surv, sustain_score: 0,
      weaknesses: overrides.weaknesses ?? [],
      strengths: [],
    },
    stat_upgrades: overrides.topUpgradeLabel
      ? [
          {
            stat: "spell_damage",
            label: overrides.topUpgradeLabel,
            dps_gain_pct: 10,
            ehp_gain_pct: 0,
          },
        ]
      : [],
    seed: null,
    dps_per_skill: [],
    combined_dps: dps,
  };
}

// ---------------------------------------------------------------------------
// 1. Letter grade boundaries
// ---------------------------------------------------------------------------

describe("computeBuildRating — letter grade boundaries", () => {
  // Efficiency × weights to reach each grade boundary exactly:
  //   score = dpsEff*40 + ehpEff*30 + survEff*30
  // A uniform efficiency U makes score = 100 * U. We use that to pin the
  // boundaries.

  function uniform(score: number) {
    const eff = score / 100;
    return computeBuildRating(
      eff * DPS_UPPER_BOUND,
      eff * EHP_UPPER_BOUND,
      eff * 100,
    );
  }

  it("90 → S", () => {
    expect(uniform(90).letter).toBe("S");
  });
  it("89 → A", () => {
    expect(uniform(89).letter).toBe("A");
  });

  it("75 → A", () => {
    expect(uniform(75).letter).toBe("A");
  });
  it("74 → B", () => {
    expect(uniform(74).letter).toBe("B");
  });

  it("60 → B", () => {
    expect(uniform(60).letter).toBe("B");
  });
  it("59 → C", () => {
    expect(uniform(59).letter).toBe("C");
  });

  it("45 → C", () => {
    expect(uniform(45).letter).toBe("C");
  });
  it("44 → D", () => {
    expect(uniform(44).letter).toBe("D");
  });

  it("0 → D", () => {
    expect(uniform(0).letter).toBe("D");
  });
  it("100 → S", () => {
    expect(uniform(100).letter).toBe("S");
  });

  it("clamps score to 0..100 even when raw values exceed bounds", () => {
    const r = computeBuildRating(
      DPS_UPPER_BOUND * 10,
      EHP_UPPER_BOUND * 10,
      999,
    );
    expect(r.score).toBeLessThanOrEqual(100);
    expect(r.score).toBeGreaterThanOrEqual(0);
    expect(r.letter).toBe("S");
  });

  it("handles non-finite inputs without NaN propagation", () => {
    const r = computeBuildRating(NaN, Infinity, -Infinity);
    expect(Number.isFinite(r.score)).toBe(true);
    expect(["S", "A", "B", "C", "D"]).toContain(r.letter);
  });
});

// ---------------------------------------------------------------------------
// 2. Summary sentence branches
// ---------------------------------------------------------------------------

describe("computeSummary — branch coverage", () => {
  it("branch 0: score < 20 emits the 'needs significant investment' message", () => {
    // uniform(10) gives a score of 10 — well below the branch-0 floor.
    const rating = computeBuildRating(
      0.1 * DPS_UPPER_BOUND,
      0.1 * EHP_UPPER_BOUND,
      10,
    );
    const s = computeSummary({
      rating,
      survivabilityScore: 10,
      weaknesses: ["Low Fire Resistance (5%)"],
      topUpgrade: null,
    });
    expect(s).toContain("significant investment");
    expect(s).toContain("Allocate skill points");
    // Crucially, it must NOT inherit the low-survivability branch even
    // though survivability is 10 — branch 0 runs first.
    expect(s).not.toContain("Low Fire Resistance");
    expect(s).not.toContain("Balanced");
  });

  it("branch 0 boundary: score 20 is NOT branch-0", () => {
    const rating = computeBuildRating(
      0.2 * DPS_UPPER_BOUND,
      0.2 * EHP_UPPER_BOUND,
      20,
    );
    const s = computeSummary({
      rating,
      survivabilityScore: 20,
      weaknesses: [],
      topUpgrade: null,
    });
    expect(s).not.toContain("significant investment");
  });

  it("branch 1: well-rounded when DPS efficiency >= 0.6 and survivability >= 75", () => {
    const rating = computeBuildRating(
      0.7 * DPS_UPPER_BOUND,
      0.7 * EHP_UPPER_BOUND,
      80,
    );
    const s = computeSummary({
      rating,
      survivabilityScore: 80,
      weaknesses: [],
      topUpgrade: null,
    });
    expect(s).toBe("Well-rounded build ready for endgame content.");
  });

  it("branch 1 boundary: survivability = 74 does NOT qualify as well-rounded", () => {
    const rating = computeBuildRating(
      0.7 * DPS_UPPER_BOUND,
      0.7 * EHP_UPPER_BOUND,
      74,
    );
    const s = computeSummary({
      rating,
      survivabilityScore: 74,
      weaknesses: [],
      topUpgrade: null,
    });
    expect(s).not.toBe("Well-rounded build ready for endgame content.");
  });

  it("branch 2: low survivability mentions the first weakness", () => {
    const rating = computeBuildRating(
      0.8 * DPS_UPPER_BOUND,
      0.8 * EHP_UPPER_BOUND,
      30,
    );
    const s = computeSummary({
      rating,
      survivabilityScore: 30,
      weaknesses: ["Low Fire Resistance (12%)"],
      topUpgrade: null,
    });
    expect(s).toContain("low survivability");
    expect(s).toContain("Low Fire Resistance (12%)");
  });

  it("branch 2 fallback: no weaknesses provided → generic resistance nudge", () => {
    const rating = computeBuildRating(
      0.8 * DPS_UPPER_BOUND,
      0.8 * EHP_UPPER_BOUND,
      10,
    );
    const s = computeSummary({
      rating,
      survivabilityScore: 10,
      weaknesses: ["", "   "], // empty-ish entries are skipped
      topUpgrade: null,
    });
    expect(s).toContain("low survivability");
    expect(s).toContain("weakest resistance");
  });

  it("branch 2 tight-spread: all elemental resistances within 5 % uses plural phrasing", () => {
    const rating = computeBuildRating(
      0.8 * DPS_UPPER_BOUND,
      0.8 * EHP_UPPER_BOUND,
      40,
    );
    const s = computeSummary({
      rating,
      survivabilityScore: 40,
      // Backend picked "Low Fire Resistance (42%)" as the weakest, but
      // every resistance is between 42 and 45 — a 3-point spread.
      weaknesses: ["Low Fire Resistance (42%)"],
      topUpgrade: null,
      elementalResistances: [42, 45, 43, 44, 42],
    });
    expect(s).toContain("elemental resistances");
    // Must NOT name the single resistance — tight spread means no real
    // weakest.
    expect(s).not.toContain("Fire Resistance");
  });

  it("branch 2 wide-spread: one genuinely low resistance is singled out", () => {
    const rating = computeBuildRating(
      0.8 * DPS_UPPER_BOUND,
      0.8 * EHP_UPPER_BOUND,
      40,
    );
    const s = computeSummary({
      rating,
      survivabilityScore: 40,
      weaknesses: ["Low Fire Resistance (20%)"],
      topUpgrade: null,
      // Fire is 20 while the others are in the 60s — spread = 45 > 5.
      elementalResistances: [20, 65, 60, 65, 60],
    });
    expect(s).toContain("Low Fire Resistance (20%)");
  });
});

describe("elementalResistancesAreTight", () => {
  it("returns true when max - min <= 5", () => {
    expect(elementalResistancesAreTight([40, 42, 45, 45, 43])).toBe(true);
    expect(elementalResistancesAreTight([70, 70, 70, 70, 70])).toBe(true);
    expect(elementalResistancesAreTight([60, 65])).toBe(true);
  });

  it("returns false when max - min > 5", () => {
    expect(elementalResistancesAreTight([40, 60, 60, 60, 60])).toBe(false);
    expect(elementalResistancesAreTight([-30, 70, 70, 70, 70])).toBe(false);
  });

  it("treats empty / single-entry lists as tight (no meaningful call-out)", () => {
    expect(elementalResistancesAreTight([])).toBe(true);
    expect(elementalResistancesAreTight([70])).toBe(true);
  });

  it("ignores NaN / Infinity entries when computing spread", () => {
    expect(elementalResistancesAreTight([70, NaN, 70, 70, 70])).toBe(true);
    expect(elementalResistancesAreTight([NaN, NaN])).toBe(true);
  });

  it("branch 3: weak DPS mentions the top stat upgrade label", () => {
    // High EHP + survivability, but DPS efficiency = 0.3 → below 0.6
    const rating = computeBuildRating(
      0.3 * DPS_UPPER_BOUND,
      0.9 * EHP_UPPER_BOUND,
      80,
    );
    const s = computeSummary({
      rating,
      survivabilityScore: 80,
      weaknesses: [],
      topUpgrade: {
        stat: "spell_damage",
        label: "increasing Spell Damage",
        dps_gain_pct: 12,
        ehp_gain_pct: 0,
      },
    });
    expect(s).toContain("improve damage output");
    expect(s).toContain("increasing Spell Damage");
  });

  it("branch 3 fallback: no upgrade provided → generic offense nudge", () => {
    const rating = computeBuildRating(
      0.3 * DPS_UPPER_BOUND,
      0.9 * EHP_UPPER_BOUND,
      80,
    );
    const s = computeSummary({
      rating,
      survivabilityScore: 80,
      weaknesses: [],
      topUpgrade: null,
    });
    expect(s).toContain("improve damage output");
    expect(s).toContain("offensive affixes");
  });

  it("branch 4: balanced-but-unremarkable fallback", () => {
    // DPS efficiency = 0.65, EHP efficiency = 0.5, survivability = 70:
    // not well-rounded (ehpEfficiency < 0.6), survivability > 50, DPS >= 0.6
    const rating = computeBuildRating(
      0.65 * DPS_UPPER_BOUND,
      0.5 * EHP_UPPER_BOUND,
      70,
    );
    const s = computeSummary({
      rating,
      survivabilityScore: 70,
      weaknesses: [],
      topUpgrade: null,
    });
    expect(s).toBe("Balanced build with room for refinement.");
  });
});

// ---------------------------------------------------------------------------
// 3. Stat pill color indicator
// ---------------------------------------------------------------------------

describe("BuildScoreCard — pill benchmark tiers", () => {
  it("renders weak-tier pills when DPS/EHP/Survivability are below weak thresholds", () => {
    const result = makeResult({
      dps: 100,
      ehp: 100,
      survivabilityScore: 10,
    });
    render(
      <BuildScoreCard
        result={result}
        status="success"
        characterClass="Mage"
        mastery="Sorcerer"
      />,
    );
    expect(screen.getAllByTestId("score-pill-weak").length).toBe(3);
  });

  it("renders average-tier pills at mid values", () => {
    const result = makeResult({
      dps: 10_000,
      ehp: 5_000,
      survivabilityScore: 60,
    });
    render(
      <BuildScoreCard
        result={result}
        status="success"
        characterClass="Mage"
        mastery="Sorcerer"
      />,
    );
    expect(screen.getAllByTestId("score-pill-average").length).toBe(3);
  });

  it("renders strong-tier pills at/above strong thresholds", () => {
    const result = makeResult({
      dps: 25_000,
      ehp: 10_000,
      survivabilityScore: 80,
    });
    render(
      <BuildScoreCard
        result={result}
        status="success"
        characterClass="Mage"
        mastery="Sorcerer"
      />,
    );
    expect(screen.getAllByTestId("score-pill-strong").length).toBe(3);
  });
});

// ---------------------------------------------------------------------------
// 4. Skeleton during pending-with-no-previous-result
// ---------------------------------------------------------------------------

describe("BuildScoreCard — pending skeleton", () => {
  it("renders the skeleton layout when status is pending and result is null", () => {
    render(
      <BuildScoreCard
        result={null}
        status="pending"
        characterClass="Mage"
        mastery="Sorcerer"
      />,
    );
    expect(screen.getByTestId("score-card-skeleton")).toBeInTheDocument();
    expect(screen.queryByTestId("build-score-card")).toBeNull();
  });

  it("renders the real card (not the skeleton) when pending AND a previous result is present", () => {
    // Phase 2 contract: preserve the prior result during pending.
    const result = makeResult({ primarySkill: "Fireball" });
    render(
      <BuildScoreCard
        result={result}
        status="pending"
        characterClass="Mage"
        mastery="Sorcerer"
      />,
    );
    expect(screen.getByTestId("build-score-card")).toBeInTheDocument();
    expect(screen.queryByTestId("score-card-skeleton")).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// 5. Idle with no result → hide the card
// ---------------------------------------------------------------------------

describe("BuildScoreCard — idle hiding", () => {
  it("renders nothing when status is idle and no result has ever landed", () => {
    const { container } = render(
      <BuildScoreCard
        result={null}
        status="idle"
        characterClass="Mage"
        mastery="Sorcerer"
      />,
    );
    expect(container).toBeEmptyDOMElement();
    expect(screen.queryByTestId("build-score-card")).toBeNull();
    expect(screen.queryByTestId("score-card-skeleton")).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// Bonus: Primary-skill change button behaviour
// ---------------------------------------------------------------------------

describe("BuildScoreCard — header + subtitle", () => {
  it('uses "Build Rating" as the card title, not the primary skill name', () => {
    const result = makeResult({ primarySkill: "Fireball" });
    render(
      <BuildScoreCard
        result={result}
        status="success"
        characterClass="Mage"
        mastery="Sorcerer"
      />,
    );
    expect(screen.getByTestId("score-card-title")).toHaveTextContent(/build rating/i);
    // The title does NOT duplicate the PrimarySkillBreakdown header.
    expect(screen.getByTestId("score-card-title")).not.toHaveTextContent(/fireball/i);
  });

  it('surfaces the primary skill as a subtitle "Analyzing {skill}"', () => {
    const result = makeResult({ primarySkill: "Fireball" });
    render(
      <BuildScoreCard
        result={result}
        status="success"
        characterClass="Mage"
        mastery="Sorcerer"
      />,
    );
    expect(screen.getByTestId("score-card-subtitle")).toHaveTextContent(/analyzing/i);
    expect(screen.getByTestId("score-card-subtitle")).toHaveTextContent(/fireball/i);
  });

  it('falls back to "No primary skill detected" subtitle when none is present', () => {
    const result = makeResult({ primarySkill: "" });
    render(
      <BuildScoreCard
        result={result}
        status="success"
        characterClass="Mage"
        mastery="Sorcerer"
      />,
    );
    expect(screen.getByTestId("score-card-subtitle")).toHaveTextContent(
      /no primary skill detected/i,
    );
  });
});

describe("BuildScoreCard — primary skill change button", () => {
  it('shows "Change" and triggers onOpenSkills when a primary skill is detected', () => {
    const onOpenSkills = vi.fn();
    const result = makeResult({ primarySkill: "Fireball" });
    render(
      <BuildScoreCard
        result={result}
        status="success"
        characterClass="Mage"
        mastery="Sorcerer"
        onOpenSkills={onOpenSkills}
      />,
    );
    const btn = screen.getByTestId("score-card-change-skill");
    expect(btn).toHaveTextContent(/change/i);
    fireEvent.click(btn);
    expect(onOpenSkills).toHaveBeenCalledTimes(1);
  });

  it('shows "Go to skills" when no primary skill is detected', () => {
    const onOpenSkills = vi.fn();
    const result = makeResult({ primarySkill: "" });
    render(
      <BuildScoreCard
        result={result}
        status="success"
        characterClass="Mage"
        mastery="Sorcerer"
        onOpenSkills={onOpenSkills}
      />,
    );
    const btn = screen.getByTestId("score-card-change-skill");
    expect(btn).toHaveTextContent(/go to skills/i);
  });
});
