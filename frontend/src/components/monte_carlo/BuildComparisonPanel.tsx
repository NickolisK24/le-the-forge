/**
 * M18 — Build Comparison Panel
 *
 * Displays two build cards side by side, a winner badge, delta statistics,
 * effect size interpretation, and a "Build A wins X%" progress bar.
 * Shows a placeholder when comparison data is null.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface BuildComparisonData {
  build_a_mean: number;
  build_b_mean: number;
  delta_mean: number;
  delta_pct: number;
  winner: "A" | "B" | "tie";
  a_is_better_pct: number;
  effect_size: number;
}

interface Props {
  comparison: BuildComparisonData | null;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function fmtDmg(v: number): string {
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(2)}M`;
  if (v >= 1_000) return `${(v / 1_000).toFixed(1)}k`;
  return v.toFixed(1);
}

function effectLabel(d: number): string {
  const abs = Math.abs(d);
  if (abs < 0.2) return "negligible";
  if (abs < 0.5) return "small";
  if (abs < 0.8) return "medium";
  return "large";
}

function winnerBadgeClasses(winner: "A" | "B" | "tie"): string {
  if (winner === "A") return "bg-green-500/20 border-green-500/60 text-green-400";
  if (winner === "B") return "bg-blue-500/20 border-blue-500/60 text-blue-400";
  return "bg-forge-border/30 border-forge-border text-forge-dim";
}

function winnerLabel(winner: "A" | "B" | "tie"): string {
  if (winner === "A") return "Build A Wins";
  if (winner === "B") return "Build B Wins";
  return "Tie";
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function BuildComparisonPanel({ comparison }: Props) {
  if (!comparison) {
    return (
      <div className="rounded border border-forge-border bg-forge-surface p-8 flex items-center justify-center">
        <p className="font-mono text-sm text-forge-dim">
          Run two builds to compare
        </p>
      </div>
    );
  }

  const {
    build_a_mean,
    build_b_mean,
    delta_mean,
    delta_pct,
    winner,
    a_is_better_pct,
    effect_size,
  } = comparison;

  const deltaPositive = delta_pct >= 0;
  const deltaCls = deltaPositive ? "text-green-400" : "text-red-400";
  const deltaSign = deltaPositive ? "+" : "";

  const bWinsPct = 100 - a_is_better_pct;

  return (
    <div className="rounded border border-forge-border bg-forge-surface p-4 space-y-5">
      <div className="font-mono text-[11px] uppercase tracking-widest text-forge-cyan/70">
        Build Comparison
      </div>

      {/* Build cards */}
      <div className="grid grid-cols-2 gap-4">
        {/* Build A */}
        <div className={`rounded border p-4 text-center ${winner === "A" ? "border-green-500/50 bg-green-500/5" : "border-forge-border bg-forge-surface2"}`}>
          <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">Build A</div>
          <div className="font-display text-2xl text-forge-amber">{fmtDmg(build_a_mean)}</div>
          <div className="font-mono text-[10px] text-forge-dim mt-0.5">mean damage</div>
        </div>
        {/* Build B */}
        <div className={`rounded border p-4 text-center ${winner === "B" ? "border-blue-500/50 bg-blue-500/5" : "border-forge-border bg-forge-surface2"}`}>
          <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">Build B</div>
          <div className="font-display text-2xl text-forge-cyan">{fmtDmg(build_b_mean)}</div>
          <div className="font-mono text-[10px] text-forge-dim mt-0.5">mean damage</div>
        </div>
      </div>

      {/* Winner badge + delta */}
      <div className="flex items-center gap-4 flex-wrap">
        <span
          className={`inline-block font-mono text-xs uppercase tracking-widest px-3 py-1 rounded border ${winnerBadgeClasses(winner)}`}
        >
          {winnerLabel(winner)}
        </span>
        <span className={`font-mono text-sm font-bold ${deltaCls}`}>
          {deltaSign}{delta_pct.toFixed(2)}%
        </span>
        <span className="font-mono text-xs text-forge-dim">
          ({deltaSign}{fmtDmg(delta_mean)} mean damage)
        </span>
      </div>

      {/* Effect size */}
      <div className="flex items-center gap-3">
        <span className="font-mono text-xs text-forge-dim">Effect size (Cohen's d):</span>
        <span className="font-mono text-xs text-forge-text font-bold">
          {effect_size.toFixed(3)}
        </span>
        <span className="font-mono text-[11px] text-forge-dim italic">
          ({effectLabel(effect_size)})
        </span>
      </div>

      {/* Build A wins % progress bar */}
      <div>
        <div className="flex justify-between font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1.5">
          <span>Build A wins {a_is_better_pct.toFixed(1)}% of runs</span>
          <span>Build B wins {bWinsPct.toFixed(1)}%</span>
        </div>
        <div className="h-3 rounded-full overflow-hidden bg-blue-500/20 relative">
          <div
            className="h-full rounded-full bg-green-500/70 transition-all duration-500"
            style={{ width: `${Math.min(a_is_better_pct, 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
}
