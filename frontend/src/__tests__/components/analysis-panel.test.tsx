/**
 * AnalysisPanel — phase 2 tests.
 *
 * Covers:
 *  - Idle state renders the empty-state message.
 *  - Non-simulatable build always shows the empty-state message.
 *  - Pending state (no prior result) renders the skeleton.
 *  - Pending state with a prior result keeps the result visible and adds a
 *    subtle "Updating…" indicator.
 *  - Success state renders the SimulationDashboard.
 *  - Error state renders the error message and a retry button.
 *  - Retry button invokes runAnalysisNow (bypassing the debounce).
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";

// ---------------------------------------------------------------------------
// Mock the dashboard — it pulls in recharts which is heavy and we only need
// to verify it rendered.
// ---------------------------------------------------------------------------
vi.mock("@/components/features/build/SimulationDashboard", () => ({
  default: ({ result }: any) => (
    <div data-testid="mock-simulation-dashboard">
      primary={result?.primary_skill}
    </div>
  ),
}));

// Mock runAnalysisNow so tests can verify the retry path without firing
// actual HTTP calls. buildIsSimulatable is pure and exported from the same
// module; keep its real implementation.
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

const runAnalysisNowMock = runAnalysisNow as unknown as ReturnType<
  typeof vi.fn
>;

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

function fakeResult(tag = "Fireball") {
  return {
    primary_skill: tag,
    skill_level: 20,
    stats: {},
    dps: {},
    monte_carlo: {},
    defense: {},
    stat_upgrades: [],
    seed: null,
    dps_per_skill: [],
    combined_dps: 0,
  } as any;
}

beforeEach(() => {
  useBuildWorkspaceStore.getState().reset();
  runAnalysisNowMock.mockReset();
});

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("AnalysisPanel — idle state", () => {
  it("renders the empty-state message on /workspace/new with no data", () => {
    render(<AnalysisPanel />);
    expect(screen.getByTestId("analysis-idle")).toHaveTextContent(
      /edit your build to see analysis/i,
    );
    expect(screen.queryByTestId("mock-simulation-dashboard")).toBeNull();
  });

  it("renders the empty-state message when the build is simulatable but no request has fired", () => {
    seedSimulatableBuild();
    render(<AnalysisPanel />);
    expect(screen.getByTestId("analysis-idle")).toHaveTextContent(
      /edit your build to see analysis/i,
    );
  });

  it("renders the empty-state message when the build is not simulatable even if a prior result exists", () => {
    const s = useBuildWorkspaceStore.getState();
    seedSimulatableBuild();
    const id = s.requestAnalysis();
    s.setAnalysisResult(id, fakeResult());
    // Now drop the skill to make the build non-simulatable.
    s.setSkills([]);
    render(<AnalysisPanel />);
    expect(screen.getByTestId("analysis-idle")).toBeInTheDocument();
    expect(screen.queryByTestId("mock-simulation-dashboard")).toBeNull();
  });
});

describe("AnalysisPanel — pending state", () => {
  it("renders the skeleton when no previous result exists", () => {
    seedSimulatableBuild();
    useBuildWorkspaceStore.getState().requestAnalysis();
    render(<AnalysisPanel />);
    expect(screen.getByTestId("analysis-skeleton")).toBeInTheDocument();
    expect(screen.getByTestId("analysis-pending-indicator")).toBeInTheDocument();
  });

  it("keeps the previous result visible and shows a subtle indicator when a request is pending", () => {
    seedSimulatableBuild();
    const s = useBuildWorkspaceStore.getState();
    const id = s.requestAnalysis();
    s.setAnalysisResult(id, fakeResult("old"));
    // Kick off a new request — status moves to pending but result stays.
    s.requestAnalysis();
    render(<AnalysisPanel />);
    expect(screen.getByTestId("mock-simulation-dashboard")).toHaveTextContent(
      "primary=old",
    );
    expect(screen.getByTestId("analysis-pending-indicator")).toBeInTheDocument();
    // No skeleton because we have a previous result to show.
    expect(screen.queryByTestId("analysis-skeleton")).toBeNull();
  });
});

describe("AnalysisPanel — success state", () => {
  it("renders the SimulationDashboard with the returned result", () => {
    seedSimulatableBuild();
    const s = useBuildWorkspaceStore.getState();
    const id = s.requestAnalysis();
    s.setAnalysisResult(id, fakeResult("Fireball"));
    render(<AnalysisPanel />);
    expect(screen.getByTestId("mock-simulation-dashboard")).toHaveTextContent(
      "primary=Fireball",
    );
    expect(screen.queryByTestId("analysis-idle")).toBeNull();
    expect(screen.queryByTestId("analysis-pending-indicator")).toBeNull();
    expect(screen.queryByTestId("analysis-error")).toBeNull();
  });
});

describe("AnalysisPanel — error state", () => {
  it("renders the error message and a retry button", () => {
    seedSimulatableBuild();
    const s = useBuildWorkspaceStore.getState();
    const id = s.requestAnalysis();
    s.setAnalysisError(id, "Something broke");
    render(<AnalysisPanel />);
    expect(screen.getByTestId("analysis-error")).toHaveTextContent(
      "Something broke",
    );
    expect(screen.getByTestId("analysis-retry")).toBeInTheDocument();
  });

  it("retry button calls runAnalysisNow (bypassing the debounce)", () => {
    seedSimulatableBuild();
    const s = useBuildWorkspaceStore.getState();
    const id = s.requestAnalysis();
    s.setAnalysisError(id, "boom");
    render(<AnalysisPanel />);
    fireEvent.click(screen.getByTestId("analysis-retry"));
    expect(runAnalysisNowMock).toHaveBeenCalledTimes(1);
  });
});

describe("AnalysisPanel — layout stability", () => {
  it("the panel always carries a min-height class to reserve vertical space", () => {
    render(<AnalysisPanel />);
    const panel = screen.getByTestId("workspace-analysis-panel");
    expect(panel.className).toMatch(/min-h-\[520px\]/);
  });

  it("exposes the current status via data-analysis-status for styling hooks", () => {
    seedSimulatableBuild();
    useBuildWorkspaceStore.getState().requestAnalysis();
    render(<AnalysisPanel />);
    const panel = screen.getByTestId("workspace-analysis-panel");
    expect(panel.getAttribute("data-analysis-status")).toBe("pending");
  });
});
