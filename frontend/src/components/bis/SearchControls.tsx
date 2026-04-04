/**
 * Q25 — SearchControls
 *
 * BIS search trigger panel: run button, max-candidates slider, estimated time,
 * indeterminate progress bar while searching.
 */

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface Props {
  onSearch: () => void;
  isSearching: boolean;
  disabled?: boolean;
  maxCandidates?: number;
  onMaxCandidatesChange?: (n: number) => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function SearchControls({
  onSearch,
  isSearching,
  disabled = false,
  maxCandidates = 200,
  onMaxCandidatesChange,
}: Props) {
  const estimatedSeconds = Math.max(1, Math.round(maxCandidates / 200));

  return (
    <div className="rounded-lg border border-forge-border bg-forge-surface p-4 space-y-4">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-forge-accent">
        Search Controls
      </h2>

      {/* Max candidates slider */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center justify-between">
          <label className="text-xs uppercase tracking-wide text-forge-muted">
            Max Candidates
          </label>
          <div className="flex items-center gap-2">
            <span className="text-xs text-forge-text">Evaluating up to {maxCandidates}</span>
            <span className="rounded-full bg-[#1a2040] px-2 py-0.5 text-xs text-[#22d3ee]">
              ~{estimatedSeconds}s
            </span>
          </div>
        </div>
        <input
          type="range"
          min={50}
          max={1000}
          step={50}
          value={maxCandidates}
          disabled={isSearching}
          onChange={(e) => onMaxCandidatesChange?.(Number(e.target.value))}
          className="w-full accent-[#f5a623] disabled:opacity-50"
        />
        <div className="flex justify-between text-xs text-forge-muted">
          <span>50</span>
          <span>1000</span>
        </div>
      </div>

      {/* Progress bar (indeterminate while searching) */}
      {isSearching && (
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-[#1a2040]">
          <div className="h-full animate-[indeterminate_1.5s_ease-in-out_infinite] rounded-full bg-[#f5a623]" />
        </div>
      )}

      {/* Buttons */}
      <div className="flex gap-2">
        <button
          onClick={onSearch}
          disabled={isSearching || disabled}
          className="flex flex-1 items-center justify-center gap-2 rounded bg-[#f5a623] px-4 py-2 text-sm
            font-semibold text-[#10152a] hover:brightness-110 active:brightness-90
            disabled:cursor-not-allowed disabled:opacity-50 transition-all"
        >
          {isSearching ? (
            <>
              <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-[#10152a]" />
              Searching...
            </>
          ) : (
            "Run BIS Search"
          )}
        </button>
      </div>

      {/* Estimated time note */}
      <p className="text-xs text-forge-muted">
        Estimated time: ~{estimatedSeconds}s for {maxCandidates} candidates
      </p>

      <style>{`
        @keyframes indeterminate {
          0%   { transform: translateX(-100%) scaleX(0.4); }
          50%  { transform: translateX(50%)   scaleX(0.6); }
          100% { transform: translateX(200%)  scaleX(0.4); }
        }
      `}</style>
    </div>
  );
}
