import { useState, useEffect } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "@/store";
import { versionApi } from "@/lib/api";

import Sidebar, { SIDEBAR_WIDTH_COLLAPSED, SIDEBAR_WIDTH_EXPANDED } from "@/components/navigation/Sidebar";
import TopBar from "@/components/navigation/TopBar";
import GlobalSearch from "@/components/search/GlobalSearch";

const SIDEBAR_STORAGE_KEY = "forge_sidebar_open";

export default function AppLayout() {
  const { data: versionRes } = useQuery({
    queryKey: ["version"],
    queryFn: () => versionApi.get(),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
  const apiVersion = versionRes?.data;
  // Build-time fallback so the footer renders the version badge synchronously
  // on cold load before /api/version resolves. patch/season still come from the
  // API (they can change between releases without a frontend rebuild).
  const versionString = apiVersion?.version || __APP_VERSION__;

  const [sidebarOpen, setSidebarOpen] = useState<boolean>(() => {
    try {
      const stored = localStorage.getItem(SIDEBAR_STORAGE_KEY);
      return stored === null ? false : stored === "true";
    } catch {
      return false;
    }
  });

  const [searchOpen, setSearchOpen] = useState(false);

  // Sync sidebar state to localStorage when toggled from TopBar
  useEffect(() => {
    try {
      localStorage.setItem(SIDEBAR_STORAGE_KEY, String(sidebarOpen));
    } catch {
      // ignore
    }
  }, [sidebarOpen]);

  // Register Cmd/Ctrl+K globally
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen((v) => !v);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const sidebarWidth = sidebarOpen ? SIDEBAR_WIDTH_EXPANDED : SIDEBAR_WIDTH_COLLAPSED;

  return (
    <div className="h-screen bg-forge-bg text-forge-text font-body overflow-hidden flex">
      {/* Sidebar */}
      <Sidebar />

      {/* Main column */}
      <div
        className="flex flex-col flex-1 min-w-0 min-h-0 transition-all duration-200"
        style={{ marginLeft: 0 }}
      >
        {/* Top bar */}
        <TopBar
          onSearchOpen={() => setSearchOpen(true)}
          onSidebarToggle={() => setSidebarOpen((v) => !v)}
        />

        {/* Page content — single scroll container for the app shell. min-h-0
            lets this flex child actually shrink below its content size so that
            overflow-y-auto kicks in instead of pushing the footer off-screen. */}
        <main className="flex-1 min-h-0 overflow-y-auto overflow-x-hidden px-6 py-8">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>

        {/* Footer */}
        <footer className="border-t border-forge-border py-4 px-6 shrink-0">
          <div className="mx-auto max-w-7xl flex items-center justify-between">
            <span className="font-mono text-xs text-forge-dim">
              The Forge — Last Epoch Build Analyzer
            </span>
            <span className="font-mono text-xs text-forge-dim flex items-center gap-2">
              {versionString && versionString !== "0.0.0" && (
                <span className="text-forge-muted">v{versionString}</span>
              )}
              {apiVersion?.current_patch && (
                <>
                  <span className="text-forge-border">|</span>
                  <span title="Last Epoch patch" className="text-forge-amber/60">
                    patch {apiVersion.current_patch}
                  </span>
                </>
              )}
              {apiVersion?.current_season !== undefined && apiVersion?.current_season !== null && (
                <>
                  <span className="text-forge-border">|</span>
                  <span title="Last Epoch season" className="text-forge-cyan/60">
                    S{apiVersion.current_season}
                  </span>
                </>
              )}
            </span>
          </div>
        </footer>
      </div>

      {/* Global search modal */}
      <GlobalSearch isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
    </div>
  );
}

// Suppress unused import warnings — these are exported for consumers
export { SIDEBAR_WIDTH_COLLAPSED, SIDEBAR_WIDTH_EXPANDED };
