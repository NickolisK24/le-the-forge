import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect } from "react";

import { useAuthStore } from "@/store";
import { authApi, setToken } from "@/lib/api";

import AppLayout from "@/components/layout/AppLayout";
import HomePage from "@/components/features/HomePage";
import BuildsPage from "@/components/features/builds/BuildsPage";
import BuildPlannerPage from "@/components/features/build/BuildPlannerPage";
import CraftSimulatorPage from "@/components/features/craft/CraftSimulatorPage";
import AuthCallbackPage from "@/components/features/AuthCallbackPage";
import UserProfilePage from "@/components/features/UserProfilePage";

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
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </AuthBootstrapper>
      </BrowserRouter>
    </QueryClientProvider>
  );
}