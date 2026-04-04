interface ProgressIndicatorProps {
  value: number;
  total?: number;
  label?: string;
  showEta?: boolean;
  startTime?: number;
  variant?: "amber" | "cyan" | "green";
}

const VARIANT_STYLES = {
  amber: {
    fill:  "bg-forge-amber",
    track: "bg-forge-amber/15",
    text:  "text-forge-amber",
  },
  cyan: {
    fill:  "bg-forge-cyan",
    track: "bg-forge-cyan/15",
    text:  "text-forge-cyan",
  },
  green: {
    fill:  "bg-forge-green",
    track: "bg-forge-green/15",
    text:  "text-forge-green",
  },
} as const;

function formatEta(ms: number): string {
  if (ms < 1000) return "<1s";
  const s = Math.round(ms / 1000);
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  const rem = s % 60;
  return rem > 0 ? `${m}m ${rem}s` : `${m}m`;
}

export function ProgressIndicator({
  value,
  total,
  label,
  showEta = false,
  startTime,
  variant = "amber",
}: ProgressIndicatorProps) {
  const styles = VARIANT_STYLES[variant];
  const clamped = Math.min(Math.max(value, 0), 100);

  let eta: string | null = null;
  if (showEta && startTime && clamped > 0 && clamped < 100) {
    const elapsed = Date.now() - startTime;
    const totalEstimate = elapsed / (clamped / 100);
    const remaining = totalEstimate - elapsed;
    eta = formatEta(remaining);
  }

  return (
    <div className="w-full">
      {(label || eta || total !== undefined) && (
        <div className="flex items-center justify-between font-mono text-[11px] uppercase tracking-widest mb-1.5">
          <span className="text-forge-dim">{label}</span>
          <div className="flex items-center gap-3">
            {total !== undefined && (
              <span className="text-forge-muted">
                {Math.round((clamped / 100) * total)}/{total}
              </span>
            )}
            {eta && (
              <span className={styles.text}>
                ETA {eta}
              </span>
            )}
            <span className={styles.text}>{clamped.toFixed(0)}%</span>
          </div>
        </div>
      )}

      <div className={`h-2 rounded-full overflow-hidden ${styles.track}`}>
        <div
          className={`h-full rounded-full transition-all duration-300 ${styles.fill}`}
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}

export function IndeterminateProgress({ label }: { label?: string }) {
  return (
    <div className="w-full">
      {label && (
        <div className="font-mono text-[11px] uppercase tracking-widest text-forge-dim mb-1.5">
          {label}
        </div>
      )}
      <div className="h-2 rounded-full overflow-hidden bg-forge-amber/15 relative">
        <div
          className="absolute h-full rounded-full bg-forge-amber"
          style={{
            width: "40%",
            animation: "forge-indeterminate 1.4s cubic-bezier(0.65,0.815,0.735,0.395) infinite",
          }}
        />
      </div>
      <style>{`
        @keyframes forge-indeterminate {
          0%   { left: -40%; }
          100% { left: 100%; }
        }
      `}</style>
    </div>
  );
}
