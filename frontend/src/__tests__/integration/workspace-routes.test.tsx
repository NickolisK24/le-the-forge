/**
 * Router-wiring test for phase-1 consolidation.
 *
 * Verifies that registering the new /workspace/* routes did NOT steal from
 * the legacy /build, /build/:slug, /planner, or /build-editor routes. The
 * legacy planner and encounter editor remain reachable exactly as before.
 *
 * We mock heavy page components to trivial stubs so we can assert which
 * component the router picks for a given URL without booting the whole app.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import React from "react";

// ---------------------------------------------------------------------------
// Stub every top-level page component — we only care about routing here.
// ---------------------------------------------------------------------------

vi.mock("@/components/features/build/BuildPlannerPage", () => ({
  default: () => <div data-testid="stub-legacy-planner">legacy-planner</div>,
}));

vi.mock("@/components/features/build-workspace/UnifiedBuildPage", () => ({
  default: () => <div data-testid="stub-unified-page">unified-page</div>,
}));

vi.mock("@/components/features/encounter/BuildEditorPage", () => ({
  default: () => <div data-testid="stub-encounter-editor">encounter</div>,
}));

// Other pages reachable at the routes we don't test — stub them all as noops
// so App.tsx compiles without side-effects from their imports.
vi.mock("@/components/features/HomePage", () => ({ default: () => null }));
vi.mock("@/components/features/builds/BuildsPage", () => ({ default: () => null }));
vi.mock("@/components/features/craft/CraftSimulatorPage", () => ({ default: () => null }));
vi.mock("@/components/features/AuthCallbackPage", () => ({ default: () => null }));
vi.mock("@/components/features/UserProfilePage", () => ({ default: () => null }));
vi.mock("@/components/features/NotFoundPage", () => ({
  default: () => <div data-testid="stub-not-found">not-found</div>,
}));
vi.mock("@/components/features/affixes/AffixEditorPage", () => ({ default: () => null }));
vi.mock("@/components/features/builds/BuildComparisonPage", () => ({ default: () => null }));
vi.mock("@/components/features/builds/ReportPage", () => ({ default: () => null }));
vi.mock("@/pages/PassiveTreePage", () => ({ default: () => null }));
vi.mock("@/components/features/builds/MetaSnapshotPage", () => ({ default: () => null }));
vi.mock("@/pages/simulation/SimulationPage", () => ({ default: () => null }));
vi.mock("@/components/features/optimizer/OptimizerPage", () => ({ default: () => null }));
vi.mock("@/pages/RotationBuilderPage", () => ({ default: () => null }));
vi.mock("@/pages/ConditionalBuilderPage", () => ({ default: () => null }));
vi.mock("@/pages/MultiTargetSimulatorPage", () => ({ default: () => null }));
vi.mock("@/pages/DataManagerPage", () => ({ default: () => null }));
vi.mock("@/pages/MonteCarloPage", () => ({ default: () => null }));
vi.mock("@/pages/crafting/CraftingPage", () => ({ default: () => null }));
vi.mock("@/pages/bis/BisSearchPage", () => ({ default: () => null }));
vi.mock("@/pages/crafting/CraftingWorkspace", () => ({ default: () => null }));
vi.mock("@/pages/DashboardPage", () => ({ default: () => null }));
vi.mock("@/pages/classes/ClassesPage", () => ({ default: () => null }));
vi.mock("@/components/layout/AppLayout", () => {
  const { Outlet } = require("react-router-dom");
  return { default: () => <Outlet /> };
});
vi.mock("@/components/ErrorBoundary", () => ({
  default: ({ children }: any) => <>{children}</>,
}));

// The auth bootstrapper + API calls fire on mount — suppress them.
vi.mock("@/store", () => ({
  useAuthStore: Object.assign(
    () => ({
      user: null,
      token: null,
      isLoading: false,
      setUser: vi.fn(),
      setToken: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
    }),
    {
      // Zustand `getState` convenience — some bootstrappers use it.
      getState: () => ({
        user: null,
        token: null,
        isLoading: false,
        setUser: vi.fn(),
        setToken: vi.fn(),
        login: vi.fn(),
        logout: vi.fn(),
      }),
      setState: vi.fn(),
    },
  ),
}));

vi.mock("@/lib/api", () => ({
  authApi: { me: vi.fn().mockResolvedValue({ data: null }) },
  setToken: vi.fn(),
}));

// ---------------------------------------------------------------------------
// Helper: drive the BrowserRouter inside App by mutating window.location
// before render. jsdom allows pushState so the browser router picks it up.
// ---------------------------------------------------------------------------

async function renderAppAt(path: string) {
  window.history.pushState({}, "", path);
  const { default: App } = await import("@/App");
  return render(<App />);
}

beforeEach(() => {
  cleanup();
  // Reset the URL bar between tests.
  window.history.replaceState({}, "", "/");
  vi.resetModules();
});

describe("Phase-1 router wiring: legacy routes still reach legacy pages", () => {
  it("/build renders the legacy planner", async () => {
    await renderAppAt("/build");
    expect(screen.getByTestId("stub-legacy-planner")).toBeInTheDocument();
    expect(screen.queryByTestId("stub-unified-page")).toBeNull();
  });

  it("/build/:slug renders the legacy planner", async () => {
    await renderAppAt("/build/some-saved-build");
    expect(screen.getByTestId("stub-legacy-planner")).toBeInTheDocument();
    expect(screen.queryByTestId("stub-unified-page")).toBeNull();
  });

  it("/planner redirects to /build and renders the legacy planner", async () => {
    await renderAppAt("/planner");
    expect(screen.getByTestId("stub-legacy-planner")).toBeInTheDocument();
  });

  it("/build-editor renders the encounter editor, not the unified page", async () => {
    await renderAppAt("/build-editor");
    expect(screen.getByTestId("stub-encounter-editor")).toBeInTheDocument();
    expect(screen.queryByTestId("stub-unified-page")).toBeNull();
  });
});

describe("Phase-1 router wiring: new /workspace/* routes render UnifiedBuildPage", () => {
  it("/workspace/new renders the unified page", async () => {
    await renderAppAt("/workspace/new");
    expect(screen.getByTestId("stub-unified-page")).toBeInTheDocument();
    expect(screen.queryByTestId("stub-legacy-planner")).toBeNull();
  });

  it("/workspace/:slug renders the unified page", async () => {
    await renderAppAt("/workspace/my-build");
    expect(screen.getByTestId("stub-unified-page")).toBeInTheDocument();
    expect(screen.queryByTestId("stub-legacy-planner")).toBeNull();
  });
});
