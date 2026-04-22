/**
 * AnalysisPanel — real-time analysis rail for the unified workspace (phase 2).
 *
 * Replaces the phase-1 placeholder. Reads analysis state from
 * `useBuildWorkspaceStore` and renders one of four visual states:
 *
 *   idle    — build is not yet simulatable. Empty-state message.
 *   pending — a request is in flight. Keeps the previous result (if any)
 *             visible with a subtle indicator so rapid edits do not flicker.
 *   success — renders the SimulationDashboard for the most recent result.
 *   error   — renders the error message and a retry button.
 *
 * The `useDebouncedAnalysis` hook is mounted once by `UnifiedBuildPage` and
 * handles the HTTP dispatch. The retry button goes through
 * `runAnalysisNow()` to bypass the 400 ms debounce.
 *
 * See docs/unified-planner-phase2-notes.md §4 for why SimulationDashboard is
 * reused verbatim — this phase does not redesign the analysis presentation.
 */

import { useBuildWorkspaceStore } from "@/store";
import { runAnalysisNow } from "@/hooks/useDebouncedAnalysis";
import { buildIsSimulatable } from "@/hooks/useDebouncedAnalysis";
import SimulationDashboard from "@/components/features/build/SimulationDashboard";

// Fixed minimum height reserves vertical space so state transitions do not
// reflow adjacent editor surfaces. The value is large enough to absorb a
// typical SimulationDashboard without clipping and small enough that the
// empty-state message still reads as intentional.
const PANEL_MIN_HEIGHT = "min-h-[520px]";

export default function AnalysisPanel() {
  const status = useBuildWorkspaceStore((s) => s.analysisStatus);
  const result = useBuildWorkspaceStore((s) => s.analysisResult);
  const error = useBuildWorkspaceStore((s) => s.analysisError);
  const build = useBuildWorkspaceStore((s) => s.build);

  const simulatable = buildIsSimulatable(build);

  return (
    <aside
      data-testid="workspace-analysis-panel"
      data-analysis-status={status}
      className={`relative rounded-lg border border-white/10 bg-black/30 p-4 ${PANEL_MIN_HEIGHT}`}
    >
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-base font-semibold text-white">Analysis</h2>
        {status === "pending" && (
          <span
            data-testid="analysis-pending-indicator"
            className="flex items-center gap-1.5 text-xs text-white/60"
            aria-live="polite"
          >
            <span
              className="inline-block h-2 w-2 animate-pulse rounded-full bg-forge-cyan"
              aria-hidden="true"
            />
            Updating…
          </span>
        )}
      </div>

      {!simulatable && (
        <IdlePanel
          message={
            status === "error"
              ? // Fall through to the error branch below.
                ""
              : "Edit your build to see analysis."
          }
        />
      )}

      {simulatable && status === "idle" && (
        <IdlePanel message="Edit your build to see analysis." />
      )}

      {simulatable && status === "error" && (
        <ErrorPanel message={error ?? "Analysis failed"} />
      )}

      {/* Success and pending (with a prior result) render the dashboard.
          Pending without a prior result shows the skeleton below. */}
      {simulatable && result && status !== "error" && (
        <div data-testid="analysis-dashboard">
          <SimulationDashboard result={result} />
        </div>
      )}

      {simulatable && !result && status === "pending" && <PendingSkeleton />}
    </aside>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function IdlePanel({ message }: { message: string }) {
  if (!message) return null;
  return (
    <div
      data-testid="analysis-idle"
      className="flex h-full min-h-[440px] flex-col items-center justify-center text-center text-sm text-white/50"
    >
      <p>{message}</p>
    </div>
  );
}

function ErrorPanel({ message }: { message: string }) {
  return (
    <div
      data-testid="analysis-error"
      className="flex h-full min-h-[440px] flex-col items-center justify-center gap-3 text-center text-sm"
    >
      <p className="text-red-400" role="alert">
        {message}
      </p>
      <button
        type="button"
        data-testid="analysis-retry"
        onClick={() => runAnalysisNow()}
        className="rounded border border-forge-cyan/40 bg-forge-cyan/10 px-3 py-1.5 text-forge-cyan hover:bg-forge-cyan/20"
      >
        Retry
      </button>
    </div>
  );
}

function PendingSkeleton() {
  // Static skeleton that reserves roughly the same vertical space the
  // SimulationDashboard occupies. Prevents the content jumping when the
  // first successful result arrives.
  return (
    <div
      data-testid="analysis-skeleton"
      className="space-y-3"
      aria-hidden="true"
    >
      <div className="h-14 rounded border border-white/5 bg-white/5" />
      <div className="grid grid-cols-2 gap-3">
        <div className="h-28 rounded border border-white/5 bg-white/5" />
        <div className="h-28 rounded border border-white/5 bg-white/5" />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="h-28 rounded border border-white/5 bg-white/5" />
        <div className="h-28 rounded border border-white/5 bg-white/5" />
      </div>
      <div className="h-24 rounded border border-white/5 bg-white/5" />
    </div>
  );
}
