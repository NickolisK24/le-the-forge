/**
 * Q24 — WeightConfigPanel
 *
 * Four weight sliders (Tier, Coverage, FP, Feasibility) with sum validation,
 * a Normalize button, preset shortcuts, and a small horizontal bar chart.
 */

import type { WeightConfig } from "@/pages/bis/BisSearchPage";

// ---------------------------------------------------------------------------
// Presets
// ---------------------------------------------------------------------------

const PRESETS: Record<string, WeightConfig> = {
  Balanced:          { tier: 0.4,  coverage: 0.3,  fp: 0.15, feasibility: 0.15 },
  "Tier Focused":    { tier: 0.7,  coverage: 0.2,  fp: 0.05, feasibility: 0.05 },
  "Coverage Focused":{ tier: 0.2,  coverage: 0.65, fp: 0.10, feasibility: 0.05 },
};

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface Props {
  weights: WeightConfig;
  onChange: (w: WeightConfig) => void;
}

// ---------------------------------------------------------------------------
// Slider row
// ---------------------------------------------------------------------------

function SliderRow({
  label,
  value,
  onChange,
  color,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  color: string;
}) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center justify-between">
        <label className="text-xs uppercase tracking-wide text-forge-muted">{label}</label>
        <span className="text-xs font-medium" style={{ color }}>{value.toFixed(2)}</span>
      </div>
      <input
        type="range"
        min={0} max={1} step={0.01}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full"
        style={{ accentColor: color }}
      />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Mini bar chart (pure CSS)
// ---------------------------------------------------------------------------

function WeightBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className="w-20 shrink-0 text-right text-xs text-forge-muted">{label}</span>
      <div className="relative flex-1 h-3 rounded-full bg-[#1a2040]">
        <div
          className="absolute inset-y-0 left-0 rounded-full transition-all"
          style={{ width: `${(value * 100).toFixed(1)}%`, backgroundColor: color }}
        />
      </div>
      <span className="w-8 text-xs text-forge-muted">{(value * 100).toFixed(0)}%</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function WeightConfigPanel({ weights, onChange }: Props) {
  const sum = +(weights.tier + weights.coverage + weights.fp + weights.feasibility).toFixed(4);
  const sumOk = Math.abs(sum - 1.0) < 0.001;

  function patch(key: keyof WeightConfig, value: number) {
    onChange({ ...weights, [key]: value });
  }

  function normalize() {
    if (sum === 0) return;
    onChange({
      tier:        +(weights.tier        / sum).toFixed(4),
      coverage:    +(weights.coverage    / sum).toFixed(4),
      fp:          +(weights.fp          / sum).toFixed(4),
      feasibility: +(weights.feasibility / sum).toFixed(4),
    });
  }

  return (
    <div className="rounded-lg border border-forge-border bg-forge-surface p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-forge-accent">
          Score Weights
        </h2>
        <button
          onClick={normalize}
          disabled={sumOk || sum === 0}
          className="rounded border border-forge-border px-2 py-0.5 text-xs text-forge-muted
            hover:border-[#f5a623] hover:text-[#f5a623] transition-colors
            disabled:cursor-not-allowed disabled:opacity-40"
        >
          Normalize
        </button>
      </div>

      {/* Sliders */}
      <div className="space-y-3">
        <SliderRow label="Tier"        value={weights.tier}        onChange={(v) => patch("tier",        v)} color="#f5a623" />
        <SliderRow label="Coverage"    value={weights.coverage}    onChange={(v) => patch("coverage",    v)} color="#22d3ee" />
        <SliderRow label="FP"          value={weights.fp}          onChange={(v) => patch("fp",          v)} color="#a78bfa" />
        <SliderRow label="Feasibility" value={weights.feasibility} onChange={(v) => patch("feasibility", v)} color="#34d399" />
      </div>

      {/* Sum indicator */}
      <div className="mt-3 flex items-center gap-2">
        <span className="text-xs text-forge-muted">Sum:</span>
        <span className={`text-xs font-medium ${sumOk ? "text-[#34d399]" : "text-[#f5a623]"}`}>
          {sum.toFixed(3)}
        </span>
        {!sumOk && (
          <span className="text-xs text-[#f5a623]">⚠ Weights don't sum to 1.0 (sum: {sum.toFixed(2)})</span>
        )}
      </div>

      {/* Presets */}
      <div className="mt-3 flex flex-wrap gap-1.5">
        {Object.entries(PRESETS).map(([name, preset]) => (
          <button
            key={name}
            onClick={() => onChange(preset)}
            className="rounded border border-forge-border px-2 py-0.5 text-xs text-forge-muted
              hover:border-[#f5a623] hover:text-[#f5a623] transition-colors"
          >
            {name}
          </button>
        ))}
      </div>

      {/* Mini bar chart */}
      <div className="mt-4 space-y-1.5">
        <WeightBar label="Tier"        value={weights.tier}        color="#f5a623" />
        <WeightBar label="Coverage"    value={weights.coverage}    color="#22d3ee" />
        <WeightBar label="FP"          value={weights.fp}          color="#a78bfa" />
        <WeightBar label="Feasibility" value={weights.feasibility} color="#34d399" />
      </div>
    </div>
  );
}
