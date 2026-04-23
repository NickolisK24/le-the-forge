/**
 * UnifiedBuildPage — phase 1 shell for the consolidated build workspace.
 *
 * Composes the existing editor components against the `useBuildWorkspaceStore`
 * Zustand slice. Renders a two-column layout: section-tabs + editor area on
 * the left, an analysis placeholder on the right.
 *
 * Routes (declared in App.tsx):
 *   /workspace/new        — initializes the store with an empty build
 *   /workspace/:slug      — fetches the build via useBuild() and initializes
 *                           the store from the server object
 *
 * The legacy `/build`, `/build/:slug`, `/planner`, and `/build-editor` routes
 * are untouched. See docs/unified-planner-design.md for architectural notes.
 */

import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { useBuild } from "@/hooks";
import { useDebouncedAnalysis } from "@/hooks/useDebouncedAnalysis";
import { useBuildWorkspaceStore } from "@/store";

import AnalysisPanel from "./AnalysisPanel";
import MetaSection from "./sections/MetaSection";
import GearSection from "./sections/GearSection";
import SkillsSection from "./sections/SkillsSection";
import PassivesSection from "./sections/PassivesSection";
import BlessingsSection from "./sections/BlessingsSection";

// ---------------------------------------------------------------------------
// Section registry — drives the tab strip and the rendered body.
// ---------------------------------------------------------------------------

type SectionId = "meta" | "gear" | "skills" | "passives" | "blessings";

const SECTIONS: ReadonlyArray<{ id: SectionId; label: string }> = [
  { id: "meta", label: "Details" },
  { id: "gear", label: "Gear" },
  { id: "skills", label: "Skills" },
  { id: "passives", label: "Passives" },
  { id: "blessings", label: "Blessings" },
];

function SectionBody({ id }: { id: SectionId }) {
  switch (id) {
    case "meta":
      return <MetaSection />;
    case "gear":
      return <GearSection />;
    case "skills":
      return <SkillsSection />;
    case "passives":
      return <PassivesSection />;
    case "blessings":
      return <BlessingsSection />;
  }
}

// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------

export default function UnifiedBuildPage() {
  const { slug } = useParams<{ slug?: string }>();
  const isNew = !slug || slug === "new";

  const { data, isLoading, error } = useBuild(isNew ? "" : slug ?? "");

  const initializeFromServer = useBuildWorkspaceStore(
    (s) => s.initializeFromServer,
  );
  const initializeEmpty = useBuildWorkspaceStore((s) => s.initializeEmpty);
  const setLoading = useBuildWorkspaceStore((s) => s.setLoading);
  const reset = useBuildWorkspaceStore((s) => s.reset);
  const status = useBuildWorkspaceStore((s) => s.status);

  const [activeSection, setActiveSection] = useState<SectionId>("meta");

  // Phase 2 — real-time analysis. Mount the hook once at the page level so
  // a single HTTP dispatcher watches every surface. Per-section mounting
  // would duplicate the request.
  useDebouncedAnalysis();

  // Initialize / reinitialize the store when the route changes.
  useEffect(() => {
    if (isNew) {
      initializeEmpty();
      return;
    }
    if (isLoading) {
      setLoading();
      return;
    }
    const build = data?.data;
    if (build) {
      initializeFromServer(build);
    }
  }, [isNew, isLoading, data, initializeEmpty, initializeFromServer, setLoading]);

  // Reset on unmount so a later route change starts from a clean slate.
  useEffect(() => {
    return () => {
      reset();
    };
  }, [reset]);

  if (!isNew && error) {
    return (
      <div className="p-6 text-red-400" data-testid="workspace-error">
        Failed to load build.
      </div>
    );
  }

  if (!isNew && status === "loading") {
    return (
      <div className="p-6 text-white/60" data-testid="workspace-loading">
        Loading build…
      </div>
    );
  }

  return (
    <div
      data-testid="unified-build-page"
      className="flex flex-col gap-4 p-4 lg:flex-row"
    >
      <main className="flex-1 space-y-4">
        <nav
          data-testid="workspace-section-nav"
          className="flex flex-wrap gap-1 border-b border-white/10 pb-2"
          role="tablist"
        >
          {SECTIONS.map((s) => (
            <button
              key={s.id}
              type="button"
              role="tab"
              aria-selected={activeSection === s.id}
              data-testid={`workspace-tab-${s.id}`}
              onClick={() => setActiveSection(s.id)}
              className={
                activeSection === s.id
                  ? "rounded-t border-b-2 border-forge-cyan px-3 py-1.5 text-sm font-semibold text-white"
                  : "rounded-t px-3 py-1.5 text-sm text-white/60 hover:text-white"
              }
            >
              {s.label}
            </button>
          ))}
        </nav>

        <div data-testid="workspace-section-body">
          <SectionBody id={activeSection} />
        </div>
      </main>

      <div className="w-full lg:w-80 lg:flex-none">
        <AnalysisPanel />
      </div>
    </div>
  );
}
