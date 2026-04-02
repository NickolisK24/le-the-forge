/**
 * F11 — Optimization Progress Bar
 *
 * Shows a progress bar and variant count during a running optimization.
 */

interface Props {
  total:     number;
  completed: number;
  failed:    number;
}

export default function OptimizationProgress({ total, completed, failed }: Props) {
  const fraction = total > 0 ? completed / total : 0;
  const pct = Math.round(fraction * 100);

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs text-forge-muted">
        <span>Simulating variants…</span>
        <span>
          {completed} / {total}
          {failed > 0 && (
            <span className="ml-2 text-red-400">({failed} failed)</span>
          )}
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-forge-border">
        <div
          className="h-full rounded-full bg-forge-accent transition-all duration-200"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
