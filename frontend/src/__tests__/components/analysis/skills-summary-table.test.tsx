/**
 * SkillsSummaryTable — phase 3 tests.
 *
 * Covers:
 *   - Renders all 5 skill rows.
 *   - Classification badges resolve correctly for each category.
 *   - Expanding a row collapses any previously expanded row.
 *   - Clicking an expanded row's header collapses it.
 */

import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";

import SkillsSummaryTable, {
  classifySkill,
} from "@/components/features/build-workspace/analysis/SkillsSummaryTable";
import type { BuildSkill } from "@/types";
import type { SkillDpsEntry, DPSResult } from "@/lib/api";

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

function skill(
  slot: number,
  skill_name: string,
  points_allocated = 0,
): BuildSkill {
  return {
    id: `draft-${slot}`,
    slot,
    skill_name,
    points_allocated,
    spec_tree: [],
  };
}

function dpsEntry(
  slot: number,
  skill_name: string,
  total_dps: number,
  is_primary = false,
): SkillDpsEntry {
  return {
    skill_name,
    skill_level: 20,
    slot,
    dps: total_dps,
    total_dps,
    is_primary,
  };
}

const NULL_DPS = null as DPSResult | null;

// ---------------------------------------------------------------------------
// classifySkill pure function
// ---------------------------------------------------------------------------

describe("classifySkill", () => {
  it("classifies known minions as minion", () => {
    expect(classifySkill("Summon Wraith")).toBe("minion");
    expect(classifySkill("Thorn Totem")).toBe("minion");
  });

  it("classifies known utilities as utility", () => {
    expect(classifySkill("Teleport")).toBe("utility");
    expect(classifySkill("Flame Ward")).toBe("utility");
  });

  it('defaults unknown skills to "damage"', () => {
    expect(classifySkill("Fireball")).toBe("damage");
    expect(classifySkill("Dancing Strikes")).toBe("damage");
  });

  it('treats zero-DPS damage entries as utility (engine hint)', () => {
    const entry = dpsEntry(0, "Made Up Skill", 0);
    expect(classifySkill("Made Up Skill", entry)).toBe("utility");
  });
});

// ---------------------------------------------------------------------------
// Renders all rows
// ---------------------------------------------------------------------------

describe("SkillsSummaryTable — row rendering", () => {
  it("renders a row for each of the 5 skill slots", () => {
    const skills: BuildSkill[] = [
      skill(0, "Fireball", 5),
      skill(1, "Teleport", 0),
      skill(2, "Summon Wraith", 3),
      skill(3, "Meteor", 2),
      skill(4, "Flame Ward", 0),
    ];
    render(
      <SkillsSummaryTable
        skills={skills}
        dpsPerSkill={[dpsEntry(0, "Fireball", 12_000, true)]}
        primaryDps={NULL_DPS}
        primarySkillName="Fireball"
      />,
    );
    for (let i = 0; i < 5; i++) {
      expect(screen.getByTestId(`skills-row-${i}`)).toBeInTheDocument();
    }
  });

  it("renders an empty-state message when no skills are slotted", () => {
    render(
      <SkillsSummaryTable
        skills={[]}
        dpsPerSkill={[]}
        primaryDps={NULL_DPS}
        primarySkillName=""
      />,
    );
    expect(
      screen.getByText(/no skills slotted/i),
    ).toBeInTheDocument();
  });

  it("applies correct classification badge for damage / utility / minion", () => {
    const skills: BuildSkill[] = [
      skill(0, "Fireball"),
      skill(1, "Teleport"),
      skill(2, "Summon Wraith"),
    ];
    render(
      <SkillsSummaryTable
        skills={skills}
        dpsPerSkill={[]}
        primaryDps={NULL_DPS}
        primarySkillName=""
      />,
    );
    expect(
      screen.getByTestId("skills-row-0-badge").textContent?.toLowerCase(),
    ).toContain("damage");
    expect(
      screen.getByTestId("skills-row-1-badge").textContent?.toLowerCase(),
    ).toContain("utility");
    expect(
      screen.getByTestId("skills-row-2-badge").textContent?.toLowerCase(),
    ).toContain("minion");
  });

  it("marks the primary skill row with the primary badge", () => {
    render(
      <SkillsSummaryTable
        skills={[skill(0, "Fireball"), skill(1, "Meteor")]}
        dpsPerSkill={[dpsEntry(0, "Fireball", 12_000, true)]}
        primaryDps={NULL_DPS}
        primarySkillName="Fireball"
      />,
    );
    expect(screen.getByTestId("skills-row-0-primary")).toBeInTheDocument();
    expect(screen.queryByTestId("skills-row-1-primary")).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// Row expansion (accordion-style single-expanded invariant)
// ---------------------------------------------------------------------------

describe("SkillsSummaryTable — row expansion", () => {
  function renderThree() {
    render(
      <SkillsSummaryTable
        skills={[
          skill(0, "Fireball"),
          skill(1, "Meteor"),
          skill(2, "Teleport"),
        ]}
        dpsPerSkill={[dpsEntry(0, "Fireball", 9_000, true)]}
        primaryDps={NULL_DPS}
        primarySkillName="Fireball"
      />,
    );
  }

  it("no row is expanded on first mount", () => {
    renderThree();
    expect(screen.queryByTestId("skills-row-0-detail")).toBeNull();
    expect(screen.queryByTestId("skills-row-1-detail")).toBeNull();
  });

  it("clicking a row expands it", () => {
    renderThree();
    fireEvent.click(screen.getByTestId("skills-row-0"));
    expect(screen.getByTestId("skills-row-0-detail")).toBeInTheDocument();
  });

  it("clicking a second row collapses the first and expands the second", () => {
    renderThree();
    fireEvent.click(screen.getByTestId("skills-row-0"));
    expect(screen.getByTestId("skills-row-0-detail")).toBeInTheDocument();

    fireEvent.click(screen.getByTestId("skills-row-1"));
    expect(screen.queryByTestId("skills-row-0-detail")).toBeNull();
    expect(screen.getByTestId("skills-row-1-detail")).toBeInTheDocument();
  });

  it("clicking an expanded row's header collapses it", () => {
    renderThree();
    fireEvent.click(screen.getByTestId("skills-row-0"));
    expect(screen.getByTestId("skills-row-0-detail")).toBeInTheDocument();
    fireEvent.click(screen.getByTestId("skills-row-0"));
    expect(screen.queryByTestId("skills-row-0-detail")).toBeNull();
  });
});
