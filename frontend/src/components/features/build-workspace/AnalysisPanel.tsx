/**
 * AnalysisPanel — placeholder for the real-time analysis rail.
 *
 * Phase 1: renders a static summary of the working build (class / mastery /
 * skill count) plus a "wired up in next phase" banner. It reads from the
 * store so that its presence in the layout is non-trivial — if the store
 * wiring breaks, this panel breaks first and loudly.
 *
 * Phase 2 will replace the body of this component with the real-time
 * analysis hook. The shell does not need to change.
 */

import { useBuildWorkspaceStore } from "@/store";

export default function AnalysisPanel() {
  const status = useBuildWorkspaceStore((s) => s.status);
  const build = useBuildWorkspaceStore((s) => s.build);
  const identity = useBuildWorkspaceStore((s) => s.identity);

  return (
    <aside
      data-testid="workspace-analysis-panel"
      className="rounded-lg border border-white/10 bg-black/30 p-4 text-sm"
    >
      <h2 className="mb-3 text-base font-semibold text-white">Analysis</h2>

      <dl className="space-y-2 text-white/80">
        <div className="flex justify-between">
          <dt className="text-white/60">Status</dt>
          <dd>{status}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-white/60">Slug</dt>
          <dd className="font-mono">{identity.slug ?? "—"}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-white/60">Class</dt>
          <dd>{build.character_class}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-white/60">Mastery</dt>
          <dd>{build.mastery || "—"}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-white/60">Level</dt>
          <dd>{build.level}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-white/60">Skills</dt>
          <dd>{build.skills.length} / 5</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-white/60">Passive points</dt>
          <dd>{build.passive_tree.length}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-white/60">Blessings</dt>
          <dd>{build.blessings.length}</dd>
        </div>
      </dl>

      <p className="mt-4 rounded border border-forge-cyan/30 bg-forge-cyan/5 p-2 text-xs text-forge-cyan/80">
        Analysis panel — wired up in next phase.
      </p>
    </aside>
  );
}
