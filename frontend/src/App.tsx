import { BrowserRouter, Routes, Route, Navigate, useLocation, useSearchParams } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import toast from "react-hot-toast";
import { lazy, Suspense, useEffect } from "react";

import { useAuthStore } from "@/store";
import { authApi, setToken } from "@/lib/api";

import ErrorBoundary from "@/components/ErrorBoundary";
import AppLayout from "@/components/layout/AppLayout";
import HomePage from "@/components/features/HomePage";
import BuildsPage from "@/components/features/builds/BuildsPage";
import BuildPlannerPage from "@/components/features/build/BuildPlannerPage";
import CraftSimulatorPage from "@/components/features/craft/CraftSimulatorPage";
import AuthCallbackPage from "@/components/features/AuthCallbackPage";
import UserProfilePage from "@/components/features/UserProfilePage";
import NotFoundPage from "@/components/features/NotFoundPage";
import AffixEditorPage from "@/components/features/affixes/AffixEditorPage";

import BuildComparisonPage from "@/components/features/builds/BuildComparisonPage";
import ReportPage from "@/components/features/builds/ReportPage";
import PassiveTreePage from "@/pages/PassiveTreePage";
import MetaSnapshotPage from "@/components/features/builds/MetaSnapshotPage";
import BuildEditorPage from "@/components/features/encounter/BuildEditorPage";
import SimulationPage from "@/pages/simulation/SimulationPage";
import OptimizerPage from "@/components/features/optimizer/OptimizerPage";
import RotationBuilderPage from "@/pages/RotationBuilderPage";
import ConditionalBuilderPage from "@/pages/ConditionalBuilderPage";
import MultiTargetSimulatorPage from "@/pages/MultiTargetSimulatorPage";
import DataManagerPage from "@/pages/DataManagerPage";
import MonteCarloPage from "@/pages/MonteCarloPage";
import CraftingPage from "@/pages/crafting/CraftingPage";
// Removed: SharedBuildPage (mock data), BuildLibraryPage (mock data)
// Removed: UserBuildDashboard (mock data with wrong class names)
// Removed: IntegrationDebugPage, BuildWorkspace (stub), BisWorkspace (duplicate)
import BisSearchPage from "@/pages/bis/BisSearchPage";
import CraftingWorkspace from "@/pages/crafting/CraftingWorkspace";
import DashboardPage from "@/pages/DashboardPage";
import ClassesPage from "@/pages/classes/ClassesPage";

// ---------------------------------------------------------------------------
// Debug pages — lazy-loaded, only registered in development builds.
// In production these routes simply don't exist, so /debug, /viz-debug, etc.
// correctly fall through to the NotFoundPage catch-all.
// ---------------------------------------------------------------------------
const IS_DEV = import.meta.env.DEV;

const MovementDebugPage = lazy(() => import("@/pages/movement/MovementDebugPage"));
const VisualizationDebugPage = lazy(() => import("@/pages/debug/VisualizationDebugPage"));
const CraftDebugPage = lazy(() => import("@/pages/debug/CraftDebugPage"));
const BackendDebugDashboard = lazy(() => import("@/pages/debug/BackendDebugDashboard"));
const DataFlowHarness = lazy(() => import("@/pages/debug/DataFlowHarness"));

// ---------------------------------------------------------------------------
// Route alias redirect — preserves the current location's search string so
// bookmarks like /planner?class=Acolyte still deliver the query param to the
// canonical /build route.
// ---------------------------------------------------------------------------
function AliasRedirect({ to }: { to: string }) {
  const loc = useLocation();
  return <Navigate to={{ pathname: to, search: loc.search }} replace />;
}

// ---------------------------------------------------------------------------
// Suspense fallback for lazy-loaded routes
// ---------------------------------------------------------------------------
function PageLoader() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-2 border-forge-cyan border-t-transparent" />
    </div>
  );
}

// ---------------------------------------------------------------------------
// React Query client
// ---------------------------------------------------------------------------
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Boot: attempt to restore session from URL token (OAuth callback)
// or from a previously stored token.
function AuthBootstrapper({ children }: { children: React.ReactNode }) {
  const { login, logout } = useAuthStore();

  useEffect(() => {
    const stored = sessionStorage.getItem("forge_token");
    if (!stored) {
      useAuthStore.setState({ isLoading: false });
      return;
    }

    const controller = new AbortController();
    setToken(stored);
    authApi.me(controller.signal).then((res) => {
      if (controller.signal.aborted) return;
      if (res.data) {
        login(stored, res.data);
      } else {
        sessionStorage.removeItem("forge_token");
        setToken(null);
        logout();
      }
    });

    return () => controller.abort();
  }, []);

  return <>{children}</>;
}

const AUTH_FAIL_MESSAGES: Record<string, string> = {
  discord_unreachable: "Could not reach Discord. Please try again.",
  discord_timeout: "Discord login timed out. Please try again.",
  token_exchange: "Discord login failed. Please try again.",
  profile_fetch: "Could not fetch your Discord profile. Please try again.",
  no_code: "Discord login was cancelled.",
  no_access_token: "Discord did not return an access token. Please try again.",
};

function AuthErrorHandler() {
  const [params, setParams] = useSearchParams();

  useEffect(() => {
    const failed = params.get("auth");
    const reason = params.get("reason") ?? "";
    if (failed !== "failed") return;

    // Only surface the toast if the user actually initiated a login attempt
    // (flag set when clicking Sign In). Prevents spurious errors on cold page
    // loads when credentials aren't configured or stale URL params linger.
    const attempted = sessionStorage.getItem("forge_login_attempted") === "1";
    sessionStorage.removeItem("forge_login_attempted");

    // Clear the URL params regardless so reloads don't re-fire the toast.
    params.delete("auth");
    params.delete("reason");
    setParams(params, { replace: true });

    if (!attempted) return;

    const msg = AUTH_FAIL_MESSAGES[reason] ?? "Login failed. Please try again.";

    if (IS_DEV && reason === "discord_unreachable") {
      // In dev, offer a bypass link since Discord may be unreachable in local environments
      toast.error(
        (t) => (
          <span>
            {msg}{" "}
            <a
              href="/api/auth/dev-login"
              style={{ color: "#f5a623", textDecoration: "underline", cursor: "pointer" }}
              onClick={() => toast.dismiss(t.id)}
            >
              Dev login
            </a>
          </span>
        ),
        { duration: 12000 }
      );
    } else {
      toast.error(msg, { duration: 6000 });
    }
  }, []);

  return null;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ErrorBoundary>
          <Toaster
            position="bottom-right"
            toastOptions={{
              style: {
                background: "#10152a",
                color: "#c8d0e0",
                border: "1px solid #2a3050",
                fontFamily: "var(--font-body, sans-serif)",
                fontSize: "14px",
              },
              error: {
                iconTheme: { primary: "#ef4444", secondary: "#10152a" },
              },
              success: {
                iconTheme: { primary: "#f5a623", secondary: "#10152a" },
              },
            }}
          />
          <AuthBootstrapper>
            <AuthErrorHandler />
            <Routes>
              {/* OAuth callback — no layout wrapper */}
              <Route path="/auth/callback" element={<AuthCallbackPage />} />

              {/* Main app shell */}
              <Route element={<AppLayout />}>
                <Route index element={<DashboardPage />} />
                <Route path="/home" element={<HomePage />} />
                <Route path="/builds" element={<BuildsPage />} />
                <Route path="/build" element={<BuildPlannerPage />} />
                <Route path="/build/:slug" element={<BuildPlannerPage />} />
                <Route path="/craft" element={<CraftSimulatorPage />} />
                <Route path="/craft/:slug" element={<CraftSimulatorPage />} />
                <Route path="/affixes" element={<AffixEditorPage />} />
                <Route path="/passives" element={<PassiveTreePage />} />
                <Route path="/compare" element={<BuildComparisonPage />} />
                <Route path="/report/:slug" element={<ReportPage />} />
                <Route path="/meta" element={<MetaSnapshotPage />} />
                <Route path="/encounter" element={<SimulationPage />} />
                <Route path="/build-editor" element={<BuildEditorPage />} />
                <Route path="/optimizer" element={<OptimizerPage />} />
                <Route path="/rotation" element={<RotationBuilderPage />} />
                <Route path="/conditional" element={<ConditionalBuilderPage />} />
                <Route path="/multi-target" element={<MultiTargetSimulatorPage />} />
                <Route path="/data-manager" element={<DataManagerPage />} />
                <Route path="/monte-carlo" element={<MonteCarloPage />} />
                <Route path="/crafting" element={<CraftingPage />} />
                <Route path="/classes" element={<ClassesPage />} />
                <Route path="/bis-search" element={<BisSearchPage />} />
                <Route path="/crafting-workspace" element={<CraftingWorkspace />} />
                <Route path="/profile" element={<UserProfilePage />} />

                {/* Route aliases — redirect legacy/external URL patterns to their
                    canonical paths. `replace` ensures the alias doesn't pollute
                    browser history. Query strings are preserved (e.g. so
                    /planner?class=Acolyte still reaches the planner with the
                    param intact). */}
                <Route path="/simulation" element={<AliasRedirect to="/encounter" />} />
                <Route path="/passive-tree" element={<AliasRedirect to="/passives" />} />
                <Route path="/planner" element={<AliasRedirect to="/build" />} />

                {/* Debug routes — only available in development builds */}
                {IS_DEV && (
                  <>
                    <Route path="/movement-debug" element={<Suspense fallback={<PageLoader />}><MovementDebugPage /></Suspense>} />
                    <Route path="/viz-debug" element={<Suspense fallback={<PageLoader />}><VisualizationDebugPage /></Suspense>} />
                    <Route path="/craft-debug" element={<Suspense fallback={<PageLoader />}><CraftDebugPage /></Suspense>} />
                    <Route path="/debug" element={<Suspense fallback={<PageLoader />}><BackendDebugDashboard /></Suspense>} />
                    <Route path="/data-flow" element={<Suspense fallback={<PageLoader />}><DataFlowHarness /></Suspense>} />
                  </>
                )}

                <Route path="*" element={<NotFoundPage />} />
              </Route>
            </Routes>
          </AuthBootstrapper>
        </ErrorBoundary>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
