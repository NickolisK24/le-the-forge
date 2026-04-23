/**
 * AnalysisPanel — phase 3 composition tests.
 *
 * Phase 2 tests verified state transitions (idle, pending, error, success)
 * against a mocked `SimulationDashboard`. Phase 3 replaces that single
 * render target with a vertical stack of purpose-built sub-components, so
 * these tests verify each expected sub-component mounts in the correct
 * state and that the idle / pending / error guards still work.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Mocks — slug-scoped leaf panels (heavy, use React Query). Replace with
// lightweight probes so tests stay hermetic. These are legacy components
// phase 3 reuses verbatim.
vi.mock("@/components/features/build/BossEncounterPanel", () => ({
  default: ({ slug }: { slug: string }) => (
    <div data-testid="mock-boss-panel">boss:{slug}</div>
  ),
}));
vi.mock("@/components/features/build/CorruptionScalingPanel", () => ({
  default: ({ slug }: { slug: string }) => (
    <div data-testid="mock-corruption-panel">corr:{slug}</div>
  ),
}));
vi.mock("@/components/features/build/GearUpgradePanel", () => ({
  default: ({ slug }: { slug: string }) => (
    <div data-testid="mock-gear-panel">gear:{slug}</div>
  ),
}));
vi.mock("@/components/features/build/StatUpgradePanel", () => ({
  default: () => <div data-testid="mock-stat-upgrade-panel" />,
}));
vi.mock("@/components/features/build/UpgradeCandidatesPanel", () => ({
  default: () => <div data-testid="mock-upgrade-candidates-panel" />,
}));

vi.mock("@/hooks/useDebouncedAnalysis", async () => {
  const actual = await vi.importActual<
    typeof import("@/hooks/useDebouncedAnalysis")
  >("@/hooks/useDebouncedAnalysis");
  return {
    ...actual,
    runAnalysisNow: vi.fn(),
  };
});

import { runAnalysisNow } from "@/hooks/useDebouncedAnalysis";
import AnalysisPanel from "@/components/features/build-workspace/AnalysisPanel";
import { useBuildWorkspaceStore } from "@/store";
import type { BuildSkill } from "@/types";

const runAnalysisNowMock = runAnalysisNow as unknown as ReturnType<typeof vi.fn>;

// ---------------------------------------------------------------------------
// React Query wrapper — required because the "What to improve next" section
// uses `useQuery` when a slug is present.
// ---------------------------------------------------------------------------

function renderPanel(props: Parameters<typeof AnalysisPanel>[0] = {}) {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={qc}>
      <AnalysisPanel {...props} />
    </QueryClientProvider>,
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function simulatableSkill(): BuildSkill {
  return {
    id: "s1",
    slot: 0,
    skill_name: "Fireball",
    points_allocated: 20,
    spec_tree: [],
  };
}

function seedSimulatableBuild() {
  const s = useBuildWorkspaceStore.getState();
  s.initializeEmpty();
  s.setMeta({ character_class: "Mage", mastery: "Sorcerer" });
  s.setSkills([simulatableSkill()]);
}

function seedSavedBuild(slug: string) {
  const s = useBuildWorkspaceStore.getState();
  s.initializeEmpty();
  s.setMeta({ character_class: "Mage", mastery: "Sorcerer" });
  s.setSkills([simulatableSkill()]);
  // Push a synthetic identity without going through initializeFromServer —
  // the full Build object is not necessary for these tests.
  useBuildWorkspaceStore.setState({
    identity: { id: "id-1", slug },
  });
}

function fakeResult(primary = "Fireball") {
  return {
    primary_skill: primary,
    skill_level: 20,
    stats: { crit_chance: 0.25 },
    dps: {
      hit_damage: 400, average_hit: 500, dps: 10_000,
      effective_attack_speed: 1.3, crit_contribution_pct: 20,
      flat_damage_added: 50, bleed_dps: 0, ignite_dps: 0,
      poison_dps: 0, ailment_dps: 0, total_dps: 10_000,
    },
    monte_carlo: {
      mean_dps: 10_000, min_dps: 9_000, max_dps: 11_000,
      std_dev: 500, percentile_25: 9_500, percentile_75: 10_500,
      n_simulations: 1_000,
    },
    defense: {
      max_health: 1_200, effective_hp: 5_000,
      armor_reduction_pct: 30, avg_resistance: 60,
      fire_res: 60, cold_res: 60, lightning_res: 60,
      void_res: 40, necrotic_res: 40, physical_res: 40, poison_res: 40,
      dodge_chance_pct: 0, block_chance_pct: 0, block_mitigation_pct: 0,
      endurance_pct: 20, endurance_threshold_pct: 20,
      crit_avoidance_pct: 0, glancing_blow_pct: 0, stun_avoidance_pct: 0,
      ward_buffer: 0, total_ehp: 5_000,
      ward_regen_per_second: 0, ward_decay_per_second: 0,
      net_ward_per_second: 0, leech_pct: 0, health_on_kill: 0,
      mana_on_kill: 0, ward_on_kill: 0, health_regen: 0, mana_regen: 0,
      survivability_score: 65, sustain_score: 50,
      weaknesses: [], strengths: [],
    },
    stat_upgrades: [],
    seed: null,
    dps_per_skill: [],
    combined_dps: 10_000,
  } as any;
}

beforeEach(() => {
  useBuildWorkspaceStore.getState().reset();
  runAnalysisNowMock.mockReset();
  window.localStorage.clear();
});

// ---------------------------------------------------------------------------
// Idle state
// ---------------------------------------------------------------------------

describe("AnalysisPanel — idle", () => {
  it("renders the phase-3 empty-state message on /workspace/new with no data", () => {
    renderPanel();
    expect(screen.getByTestId("analysis-idle")).toHaveTextContent(
      /select a class and specialize a skill/i,
    );
    expect(screen.queryByTestId("build-score-card")).toBeNull();
  });

  it("renders the idle message when simulatable but no request has fired yet", () => {
    seedSimulatableBuild();
    renderPanel();
    expect(screen.getByTestId("analysis-idle")).toHaveTextContent(
      /edit your build to see analysis/i,
    );
  });

  it("hides the panel body when not simulatable even if a prior result exists", () => {
    seedSimulatableBuild();
    const s = useBuildWorkspaceStore.getState();
    const id = s.requestAnalysis();
    s.setAnalysisResult(id, fakeResult());
    s.setSkills([]); // now non-simulatable
    renderPanel();
    expect(screen.getByTestId("analysis-idle")).toBeInTheDocument();
    expect(screen.queryByTestId("build-score-card")).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// Pending state
// ---------------------------------------------------------------------------

describe("AnalysisPanel — pending", () => {
  it("renders section skeletons + score-card skeleton when no prior result exists", () => {
    seedSimulatableBuild();
    useBuildWorkspaceStore.getState().requestAnalysis();
    renderPanel();
    expect(screen.getByTestId("score-card-skeleton")).toBeInTheDocument();
    expect(screen.getByTestId("analysis-skeleton-grid")).toBeInTheDocument();
    // No pending indicator because there's no prior result yet.
    expect(screen.queryByTestId("analysis-pending-indicator")).toBeNull();
  });

  it("keeps the result visible and shows the Updating… badge when a prior result exists", () => {
    seedSimulatableBuild();
    const s = useBuildWorkspaceStore.getState();
    const id = s.requestAnalysis();
    s.setAnalysisResult(id, fakeResult("old"));
    // Kick off a new request — status moves to pending but result stays.
    s.requestAnalysis();
    renderPanel();
    expect(screen.getByTestId("build-score-card")).toBeInTheDocument();
    expect(screen.getByTestId("analysis-pending-indicator")).toBeInTheDocument();
    expect(screen.queryByTestId("score-card-skeleton")).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// Success state — full composition
// ---------------------------------------------------------------------------

describe("AnalysisPanel — success composition", () => {
  it("renders the score card, offense + defense, primary skill, skills table, and accordion", () => {
    seedSimulatableBuild();
    const s = useBuildWorkspaceStore.getState();
    const id = s.requestAnalysis();
    s.setAnalysisResult(id, fakeResult());
    renderPanel();

    expect(screen.getByTestId("build-score-card")).toBeInTheDocument();
    expect(screen.getByTestId("offense-card")).toBeInTheDocument();
    expect(screen.getByTestId("defense-card")).toBeInTheDocument();
    expect(screen.getByTestId("primary-skill-breakdown")).toBeInTheDocument();
    expect(screen.getByTestId("skills-summary-table")).toBeInTheDocument();
    expect(screen.getByTestId("advanced-analysis-accordion")).toBeInTheDocument();
  });

  it("renders the advanced accordion collapsed by default", () => {
    seedSimulatableBuild();
    const s = useBuildWorkspaceStore.getState();
    const id = s.requestAnalysis();
    s.setAnalysisResult(id, fakeResult());
    renderPanel();
    expect(
      screen.getByTestId("advanced-analysis-accordion").getAttribute("data-open"),
    ).toBe("false");
  });

  it("omits the What-to-improve-next section on an unsaved build with no stat_upgrades", () => {
    seedSimulatableBuild();
    const s = useBuildWorkspaceStore.getState();
    const id = s.requestAnalysis();
    s.setAnalysisResult(id, fakeResult()); // stat_upgrades: []
    renderPanel();
    expect(screen.queryByTestId("improve-next-section")).toBeNull();
  });

  it("renders the fallback What-to-improve-next list on an unsaved build when stat_upgrades are present", () => {
    seedSimulatableBuild();
    const s = useBuildWorkspaceStore.getState();
    const id = s.requestAnalysis();
    const r = fakeResult();
    r.stat_upgrades = [
      { stat: "spell_damage", label: "Spell Damage", dps_gain_pct: 12, ehp_gain_pct: 0 },
      { stat: "crit_chance",  label: "Crit Chance",  dps_gain_pct: 9,  ehp_gain_pct: 0 },
    ];
    s.setAnalysisResult(id, r);
    renderPanel();
    const section = screen.getByTestId("improve-next-section");
    expect(section.getAttribute("data-mode")).toBe("fallback");
    expect(screen.getByTestId("improve-next-inline-list")).toBeInTheDocument();
    expect(section).toHaveTextContent(/Spell Damage/);
    expect(section).toHaveTextContent(/Crit Chance/);
  });

  it("includes the slug-scoped What-to-improve-next section when a slug is present", () => {
    seedSavedBuild("cool-build");
    const s = useBuildWorkspaceStore.getState();
    const id = s.requestAnalysis();
    s.setAnalysisResult(id, fakeResult());
    renderPanel();
    const section = screen.getByTestId("improve-next-section");
    expect(section.getAttribute("data-mode")).toBe("saved");
    expect(section).toHaveTextContent(/what to improve next/i);
    expect(section).toHaveTextContent(/per forge potential invested/i);
  });

  it("renders What-to-improve-next above the AdvancedAnalysisAccordion", () => {
    seedSavedBuild("cool-build");
    const s = useBuildWorkspaceStore.getState();
    const id = s.requestAnalysis();
    s.setAnalysisResult(id, fakeResult());
    renderPanel();
    const improve = screen.getByTestId("improve-next-section");
    const accordion = screen.getByTestId("advanced-analysis-accordion");
    // Document order: improve should come first.
    expect(
      improve.compareDocumentPosition(accordion) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
  });
});

// ---------------------------------------------------------------------------
// Error state (unchanged from phase 2)
// ---------------------------------------------------------------------------

describe("AnalysisPanel — error", () => {
  it("renders the error block and retry button", () => {
    seedSimulatableBuild();
    const s = useBuildWorkspaceStore.getState();
    const id = s.requestAnalysis();
    s.setAnalysisError(id, "Something broke");
    renderPanel();
    expect(screen.getByTestId("analysis-error")).toHaveTextContent(
      "Something broke",
    );
    const retry = screen.getByTestId("analysis-retry");
    fireEvent.click(retry);
    expect(runAnalysisNowMock).toHaveBeenCalledTimes(1);
  });
});

// ---------------------------------------------------------------------------
// Layout stability
// ---------------------------------------------------------------------------

describe("AnalysisPanel — layout stability", () => {
  it("keeps the min-h-[520px] class on the outer panel", () => {
    renderPanel();
    const panel = screen.getByTestId("workspace-analysis-panel");
    expect(panel.className).toMatch(/min-h-\[520px\]/);
  });

  it("exposes the analysis status via data-analysis-status", () => {
    seedSimulatableBuild();
    useBuildWorkspaceStore.getState().requestAnalysis();
    renderPanel();
    expect(
      screen.getByTestId("workspace-analysis-panel").getAttribute("data-analysis-status"),
    ).toBe("pending");
  });
});

// ---------------------------------------------------------------------------
// Skill-tab callback
// ---------------------------------------------------------------------------

describe("AnalysisPanel — onOpenSkills wiring", () => {
  it("forwards the callback to the BuildScoreCard change button", () => {
    seedSimulatableBuild();
    const s = useBuildWorkspaceStore.getState();
    const id = s.requestAnalysis();
    s.setAnalysisResult(id, fakeResult());
    const onOpenSkills = vi.fn();
    renderPanel({ onOpenSkills });
    fireEvent.click(screen.getByTestId("score-card-change-skill"));
    expect(onOpenSkills).toHaveBeenCalledTimes(1);
  });
});
