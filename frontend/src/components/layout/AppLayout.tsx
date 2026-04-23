import { useState, useEffect } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { versionApi } from "@/lib/api";

import Sidebar, { SIDEBAR_WIDTH_COLLAPSED, SIDEBAR_WIDTH_EXPANDED } from "@/components/navigation/Sidebar";
import TopBar from "@/components/navigation/TopBar";
import GlobalSearch from "@/components/search/GlobalSearch";

export default function AppLayout() {
  const location = useLocation();
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

  // Mobile drawer state (transient — doesn't persist across reloads).
  // Desktop sidebar expand/collapse persistence is owned by Sidebar itself.
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const [searchOpen, setSearchOpen] = useState(false);

  // Auto-close the mobile drawer whenever the route changes so that tapping a
  // nav item navigates AND dismisses the drawer in one gesture.
  useEffect(() => {
    setMobileSidebarOpen(false);
  }, [location.pathname]);

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

  // Routes that opt out of the default `max-w-7xl` content cap. The unified
  // build workspace is a two-column editor + analysis layout that needs the
  // full main-column width to avoid truncating the analysis rail on wide
  // displays. Keeping the opt-out here (rather than inside UnifiedBuildPage
  // with a CSS break-out trick) is what lets the sidebar resize without the
  // page overlapping into it — the page only ever occupies the main column's
  // own width, whatever that happens to be.
  const isFullWidthRoute = location.pathname.startsWith("/workspace");
  const contentWrapperClass = isFullWidthRoute
    ? "w-full"
    : "mx-auto max-w-7xl";

  return (
    <div className="h-screen bg-forge-bg text-forge-text font-body overflow-hidden flex">
      {/* Sidebar — fixed drawer on mobile, in-flow on md+ */}
      <Sidebar
        mobileOpen={mobileSidebarOpen}
        onMobileNavigate={() => setMobileSidebarOpen(false)}
      />

      {/* Mobile drawer backdrop — clicking dismisses the drawer */}
      {mobileSidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={() => setMobileSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Main column */}
      <div className="flex flex-col flex-1 min-w-0 min-h-0">
        {/* Top bar */}
        <TopBar
          onSearchOpen={() => setSearchOpen(true)}
          onSidebarToggle={() => setMobileSidebarOpen((v) => !v)}
        />

        {/* Page content — single scroll container for the app shell. min-h-0
            lets this flex child actually shrink below its content size so that
            overflow-y-auto kicks in instead of pushing the footer off-screen. */}
        <main className="flex-1 min-h-0 overflow-y-auto overflow-x-hidden px-4 py-6 md:px-6 md:py-8">
          <div className={contentWrapperClass}>
            <Outlet />
          </div>
        </main>

        {/* Footer */}
        <footer className="border-t border-forge-border py-4 px-6 shrink-0">
          <div className="mx-auto max-w-7xl flex items-center justify-between">
            <span className="font-mono text-xs text-forge-dim flex items-center gap-2">
              <span>The Forge — Last Epoch Build Analyzer</span>
              <span className="text-forge-border">|</span>
              <a
                href="https://github.com/NickolisK24/le-the-forge/blob/main/docs/KNOWN_LIMITATIONS.md"
                target="_blank"
                rel="noopener noreferrer"
                className="text-forge-dim hover:text-forge-amber underline decoration-dotted underline-offset-2"
                title="Public-facing disclosure of verified, approximate, and incomplete systems"
              >
                known limitations
              </a>
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
