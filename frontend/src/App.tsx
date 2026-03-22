import { BrowserRouter, Routes, Route, useSearchParams } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import toast from "react-hot-toast";
import { useEffect } from "react";

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

const IS_DEV = import.meta.env.DEV;

function AuthErrorHandler() {
  const [params, setParams] = useSearchParams();

  useEffect(() => {
    const failed = params.get("auth");
    const reason = params.get("reason") ?? "";
    if (failed === "failed") {
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

      params.delete("auth");
      params.delete("reason");
      setParams(params, { replace: true });
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
                <Route index element={<HomePage />} />
                <Route path="/builds" element={<BuildsPage />} />
                <Route path="/build" element={<BuildPlannerPage />} />
                <Route path="/build/:slug" element={<BuildPlannerPage />} />
                <Route path="/craft" element={<CraftSimulatorPage />} />
                <Route path="/craft/:slug" element={<CraftSimulatorPage />} />
                <Route path="/affixes" element={<AffixEditorPage />} />
                <Route path="/profile" element={<UserProfilePage />} />
                <Route path="*" element={<NotFoundPage />} />
              </Route>
            </Routes>
          </AuthBootstrapper>
        </ErrorBoundary>
      </BrowserRouter>
    </QueryClientProvider>
  );
}