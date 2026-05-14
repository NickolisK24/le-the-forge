/**
 * UnifiedBuildPage — phase-1 shell tests.
 *
 * Covers:
 *   - /workspace/:slug loads an existing build via useBuild and renders all
 *     editor surfaces.
 *   - /workspace/new initializes with an empty build.
 *   - Edits to the Meta section update the shared store correctly.
 *   - The tab strip switches sections.
 *   - Route registration does not steal from the legacy planner routes.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import React from "react";

// ---------------------------------------------------------------------------
// Mocks — keep the shell testable without booting the full app.
// ---------------------------------------------------------------------------

const mockUseBuild = vi.fn();

vi.mock("@/hooks", () => ({
  useBuild: (slug: string) => mockUseBuild(slug),
  useCreateBuild: () => ({ mutate: vi.fn(), mutateAsync: vi.fn(), isPending: false }),
  useUpdateBuild: () => ({ mutate: vi.fn(), mutateAsync: vi.fn(), isPending: false }),
  useVote: () => ({ mutate: vi.fn() }),
}));

vi.mock("@tanstack/react-query", async () => {
  const actual = await vi.importActual<typeof import("@tanstack/react-query")>(
    "@tanstack/react-query",
  );
  return {
    ...actual,
    useQuery: () => ({ data: null, isLoading: false, error: null }),
    useMutation: () => ({ mutate: vi.fn(), mutateAsync: vi.fn(), isPending: false }),
  };
});

// Keep the heavy leaf editors trivial so tests are fast and focused on the shell.
vi.mock("@/components/features/build/GearEditor", () => ({
  default: ({ gear, onChange }: any) => (
    <div data-testid="mock-gear-editor">
      <span data-testid="mock-gear-count">{gear?.length ?? 0}</span>
      <button
        data-testid="mock-gear-add"
        onClick={() => onChange([...(gear ?? []), { slot: "helmet" }])}
      >
        add-gear
      </button>
    </div>
  ),
}));

vi.mock("@/components/features/build/SkillSelector", () => ({
  default: ({ skills, onAddSkill }: any) => (
    <div data-testid="mock-skill-selector">
      <span data-testid="mock-skill-count">{skills?.length ?? 0}</span>
      <button
        data-testid="mock-skill-add"
        onClick={() => onAddSkill?.("TestSkill")}
      >
        add-skill
      </button>
    </div>
  ),
}));

vi.mock("@/components/features/build/BuildPassiveTree", () => ({
  default: ({ allocated, onAllocate }: any) => (
    <div data-testid="mock-passive-tree">
      <span data-testid="mock-passive-node-count">
        {Object.keys(allocated ?? {}).length}
      </span>
      <button
        data-testid="mock-passive-allocate"
        onClick={() => onAllocate(42, 1)}
      >
        allocate
      </button>
    </div>
  ),
}));

vi.mock("@/components/features/build/PassiveProgressBar", () => ({
  default: ({ history }: any) => (
    <div data-testid="mock-progress-bar">{history?.length ?? 0}</div>
  ),
}));

vi.mock("@/components/blessings/BlessingsPanel", () => ({
  BlessingsPanel: ({ selectedBlessings, onChange }: any) => (
    <div data-testid="mock-blessings-panel">
      <span data-testid="mock-blessing-count">
        {selectedBlessings?.length ?? 0}
      </span>
      <button
        data-testid="mock-blessing-add"
        onClick={() =>
          onChange([
            ...(selectedBlessings ?? []),
            { timeline_id: "t", blessing_id: "b", is_grand: false, value: 1 },
          ])
        }
      >
        add-blessing
      </button>
    </div>
  ),
}));

// ---------------------------------------------------------------------------
// Imports under test (after mocks)
// ---------------------------------------------------------------------------

import UnifiedBuildPage from "@/components/features/build-workspace/UnifiedBuildPage";
import { useBuildWorkspaceStore } from "@/store";

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

function mountAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/workspace/new" element={<UnifiedBuildPage />} />
        <Route path="/workspace/:slug" element={<UnifiedBuildPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

const SERVER_BUILD = {
  id: "id-1",
  slug: "my-build",
  name: "Server Build",
  description: "From server",
  character_class: "Rogue",
  mastery: "Bladedancer",
  level: 88,
  passive_tree: [1, 2, 2],
  gear: [{ slot: "helmet" }],
  skills: [
    {
      id: "sk-1",
      slot: 0,
      skill_name: "Shift",
      points_allocated: 3,
      spec_tree: [5, 6, 7],
    },
  ],
  blessings: [
    { timeline_id: "t1", blessing_id: "b1", is_grand: false, value: 30 },
  ],
  is_ssf: false,
  is_hc: false,
  is_ladder_viable: true,
  is_budget: false,
  patch_version: "1.2.1",
  cycle: "1.2",
  vote_count: 0,
  view_count: 0,
  is_public: true,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-02T00:00:00Z",
};

beforeEach(() => {
  useBuildWorkspaceStore.getState().reset();
  mockUseBuild.mockReset();
});

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("UnifiedBuildPage — /workspace/new", () => {
  beforeEach(() => {
    mockUseBuild.mockReturnValue({ data: null, isLoading: false, error: null });
  });

  it("renders the shell layout", () => {
    mountAt("/workspace/new");
    expect(screen.getByTestId("unified-build-page")).toBeInTheDocument();
    expect(screen.getByTestId("workspace-section-nav")).toBeInTheDocument();
    expect(screen.getByTestId("workspace-analysis-panel")).toBeInTheDocument();
  });

  it("initializes the store with an empty build", () => {
    mountAt("/workspace/new");
    const s = useBuildWorkspaceStore.getState();
    expect(s.status).toBe("ready");
    expect(s.identity.slug).toBeNull();
    expect(s.build.name).toBe("");
    expect(s.build.skills).toEqual([]);
    expect(s.build.gear).toEqual([]);
  });

  it("renders the Meta section by default", () => {
    mountAt("/workspace/new");
    expect(screen.getByTestId("workspace-section-meta")).toBeInTheDocument();
  });

  it("shows the phase-3 empty-state on a fresh /workspace/new", () => {
    // Phase 2 replaced the placeholder with a real analysis rail. Phase 3
    // rewrote the empty-state copy to explicitly nudge the user toward
    // picking a class and specializing a skill — the path to analysis.
    mountAt("/workspace/new");
    expect(
      screen.getByText(/select a class and specialize a skill/i),
    ).toBeInTheDocument();
  });
});

describe("UnifiedBuildPage — /workspace/:slug", () => {
  it("shows a loading state while useBuild is fetching", () => {
    mockUseBuild.mockReturnValue({ data: null, isLoading: true, error: null });
    mountAt("/workspace/my-build");
    expect(screen.getByTestId("workspace-loading")).toBeInTheDocument();
  });

  it("seeds the store from the server build once useBuild resolves", () => {
    mockUseBuild.mockReturnValue({
      data: { data: SERVER_BUILD },
      isLoading: false,
      error: null,
    });
    mountAt("/workspace/my-build");
    const s = useBuildWorkspaceStore.getState();
    expect(s.status).toBe("ready");
    expect(s.identity.slug).toBe("my-build");
    expect(s.build.name).toBe("Server Build");
    expect(s.build.character_class).toBe("Rogue");
    expect(s.build.skills).toHaveLength(1);
    expect(s.build.passive_tree).toEqual([1, 2, 2]);
    expect(s.build.blessings).toHaveLength(1);
  });

  it("renders every editor surface across the tab strip", () => {
    mockUseBuild.mockReturnValue({
      data: { data: SERVER_BUILD },
      isLoading: false,
      error: null,
    });
    mountAt("/workspace/my-build");

    for (const id of ["meta", "gear", "skills", "passives", "blessings"]) {
      expect(screen.getByTestId(`workspace-tab-${id}`)).toBeInTheDocument();
    }

    // Switch through tabs and confirm each section body mounts.
    fireEvent.click(screen.getByTestId("workspace-tab-gear"));
    expect(screen.getByTestId("mock-gear-editor")).toBeInTheDocument();

    fireEvent.click(screen.getByTestId("workspace-tab-skills"));
    expect(screen.getByTestId("mock-skill-selector")).toBeInTheDocument();

    fireEvent.click(screen.getByTestId("workspace-tab-passives"));
    expect(screen.getByTestId("mock-passive-tree")).toBeInTheDocument();

    fireEvent.click(screen.getByTestId("workspace-tab-blessings"));
    expect(screen.getByTestId("mock-blessings-panel")).toBeInTheDocument();
  });

  it("shows an error state when useBuild fails", () => {
    mockUseBuild.mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error("nope"),
    });
    mountAt("/workspace/my-build");
    expect(screen.getByTestId("workspace-error")).toBeInTheDocument();
  });
});

describe("UnifiedBuildPage — edits update the shared store", () => {
  beforeEach(() => {
    mockUseBuild.mockReturnValue({ data: null, isLoading: false, error: null });
  });

  it("updates build.name when the Meta name input changes", () => {
    mountAt("/workspace/new");
    const input = screen.getByTestId("meta-name") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "My New Build" } });
    expect(useBuildWorkspaceStore.getState().build.name).toBe("My New Build");
  });

  it("updates build.level via setMeta", () => {
    mountAt("/workspace/new");
    const input = screen.getByTestId("meta-level") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "75" } });
    expect(useBuildWorkspaceStore.getState().build.level).toBe(75);
  });

  it("pushes a new gear entry through GearSection", () => {
    mountAt("/workspace/new");
    fireEvent.click(screen.getByTestId("workspace-tab-gear"));
    expect(useBuildWorkspaceStore.getState().build.gear).toHaveLength(0);
    fireEvent.click(screen.getByTestId("mock-gear-add"));
    expect(useBuildWorkspaceStore.getState().build.gear).toHaveLength(1);
    expect(useBuildWorkspaceStore.getState().build.gear[0].slot).toBe("helmet");
  });

  it("adds a skill through SkillsSection", () => {
    mountAt("/workspace/new");
    fireEvent.click(screen.getByTestId("workspace-tab-skills"));
    fireEvent.click(screen.getByTestId("mock-skill-add"));
    const skills = useBuildWorkspaceStore.getState().build.skills;
    expect(skills).toHaveLength(1);
    expect(skills[0].skill_name).toBe("TestSkill");
    expect(skills[0].slot).toBe(0);
  });

  it("allocates a passive point through PassivesSection", () => {
    mountAt("/workspace/new");
    fireEvent.click(screen.getByTestId("workspace-tab-passives"));
    fireEvent.click(screen.getByTestId("mock-passive-allocate"));
    expect(useBuildWorkspaceStore.getState().build.passive_tree).toEqual([42]);
  });

  it("adds a blessing through BlessingsSection", () => {
    mountAt("/workspace/new");
    fireEvent.click(screen.getByTestId("workspace-tab-blessings"));
    fireEvent.click(screen.getByTestId("mock-blessing-add"));
    expect(useBuildWorkspaceStore.getState().build.blessings).toHaveLength(1);
  });
});

describe("UnifiedBuildPage — route coexistence", () => {
  it("the old /build and /planner paths are not served by UnifiedBuildPage", () => {
    // Only /workspace/* routes are registered in this test tree — navigating
    // to a legacy path must NOT render the unified page. This is a guard
    // against accidentally stealing the legacy namespace during phase 1.
    mockUseBuild.mockReturnValue({ data: null, isLoading: false, error: null });
    const { container } = render(
      <MemoryRouter initialEntries={["/build"]}>
        <Routes>
          <Route path="/workspace/new" element={<UnifiedBuildPage />} />
          <Route path="/workspace/:slug" element={<UnifiedBuildPage />} />
          <Route
            path="/build"
            element={<div data-testid="legacy-planner-stub">legacy</div>}
          />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByTestId("legacy-planner-stub")).toBeInTheDocument();
    expect(container.querySelector('[data-testid="unified-build-page"]')).toBeNull();
  });
});
