import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
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
  const { login, logout, setUser } = useAuthStore();

  useEffect(() => {
    // Check for token in URL (OAuth callback handled in AuthCallbackPage)
    // Fall back to fetching /api/auth/me if a token was already set
    const stored = sessionStorage.getItem("forge_token");
    if (stored) {
      setToken(stored);
      authApi.me().then((res) => {
        if (res.data) {
          login(stored, res.data);
        } else {
          sessionStorage.removeItem("forge_token");
          logout();
        }
      });
    } else {
      useAuthStore.setState({ isLoading: false });
    }
  }, []);

  return <>{children}</>;
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