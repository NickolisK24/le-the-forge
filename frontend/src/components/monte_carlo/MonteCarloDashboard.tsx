/**
 * M15 — Monte Carlo Dashboard
 *
 * Config form on the left, summary statistics on the right.
 * Calls onRun with the current SimConfig when the user clicks Run.
 */

import { useState } from "react";
import { Button, Panel, SectionLabel } from "@/components/ui";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface SimConfig {
  n_runs: number;
  crit_chance: number;
  crit_multiplier: number;
  base_damage: number;
  proc_chance: number;
  proc_magnitude: number;
  duration: number;
}

export interface MonteCarloSimResult {
  mean_damage: number;
  std_damage: number;
  min_damage: number;
  max_damage: number;
  median_damage: number;
  percentile_5: number;
  percentile_95: number;
  mean_crits: number;
  mean_procs: number;
  n_runs: number;
  cv: number;
  reliability_score: number;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const DEFAULT_CONFIG: SimConfig = {
  n_runs: 1000,
  crit_chance: 0.25,
  crit_multiplier: 2.0,
  base_damage: 500,
  proc_chance: 0.15,
  proc_magnitude: 1200,
  duration: 60,
};

const inputCls =
  "w-full rounded-sm border border-forge-border bg-forge-surface2 px-3 py-2 " +
  "font-body text-sm text-forge-text outline-none focus:border-forge-amber/60";

const labelCls =
  "block font-mono text-[11px] uppercase tracking-widest text-forge-dim mb-1";

function fmt(n: number, decimals = 0): string {
  return n.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function reliabilityColor(score: number): string {
  if (score >= 0.8) return "text-green-400";
  if (score >= 0.6) return "text-forge-amber";
  return "text-red-400";
}

function StatRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-forge-border/40 last:border-0">
      <span className="font-mono text-xs text-forge-dim">{label}</span>
      <span className="font-mono text-xs text-forge-text">{value}</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface Props {
  result: MonteCarloSimResult | null;
  isRunning: boolean;
  onRun: (config: SimConfig) => void;
}

export default function MonteCarloDashboard({ result, isRunning, onRun }: Props) {
  const [config, setConfig] = useState<SimConfig>(DEFAULT_CONFIG);

  function set<K extends keyof SimConfig>(key: K, value: SimConfig[K]) {
    setConfig((prev) => ({ ...prev, [key]: value }));
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* ---- Config form ---- */}
      <Panel>
        <SectionLabel>Simulation Config</SectionLabel>
        <div className="space-y-4">

          {/* n_runs slider */}
          <div>
            <label className={labelCls}>
              Runs&nbsp;
              <span className="text-forge-amber">{config.n_runs.toLocaleString()}</span>
            </label>
            <input
              type="range"
              min={100}
              max={10000}
              step={100}
              value={config.n_runs}
              onChange={(e) => set("n_runs", Number(e.target.value))}
              className="w-full accent-amber-400"
            />
            <div className="flex justify-between font-mono text-[10px] text-forge-dim mt-0.5">
              <span>100</span><span>10 000</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={labelCls}>Crit Chance (0–1)</label>
              <input
                type="number"
                min={0}
                max={1}
                step={0.01}
                className={inputCls}
                value={config.crit_chance}
                onChange={(e) => set("crit_chance", Number(e.target.value))}
              />
            </div>
            <div>
              <label className={labelCls}>Crit Multiplier (1–5)</label>
              <input
                type="number"
                min={1}
                max={5}
                step={0.1}
                className={inputCls}
                value={config.crit_multiplier}
                onChange={(e) => set("crit_multiplier", Number(e.target.value))}
              />
            </div>
            <div>
              <label className={labelCls}>Base Damage</label>
              <input
                type="number"
                min={1}
                className={inputCls}
                value={config.base_damage}
                onChange={(e) => set("base_damage", Number(e.target.value))}
              />
            </div>
            <div>
              <label className={labelCls}>Duration (s)</label>
              <input
                type="number"
                min={1}
                className={inputCls}
                value={config.duration}
                onChange={(e) => set("duration", Number(e.target.value))}
              />
            </div>
            <div>
              <label className={labelCls}>Proc Chance (0–1)</label>
              <input
                type="number"
                min={0}
                max={1}
                step={0.01}
                className={inputCls}
                value={config.proc_chance}
                onChange={(e) => set("proc_chance", Number(e.target.value))}
              />
            </div>
            <div>
              <label className={labelCls}>Proc Magnitude</label>
              <input
                type="number"
                min={0}
                className={inputCls}
                value={config.proc_magnitude}
                onChange={(e) => set("proc_magnitude", Number(e.target.value))}
              />
            </div>
          </div>

          <Button
            onClick={() => onRun(config)}
            disabled={isRunning}
            className="w-full mt-2"
          >
            {isRunning ? "Simulating..." : "Run Simulation"}
          </Button>
        </div>
      </Panel>

      {/* ---- Summary stats ---- */}
      <Panel>
        <SectionLabel>Results</SectionLabel>
        {result ? (
          <div className="space-y-0.5">
            <StatRow label="Runs"           value={result.n_runs.toLocaleString()} />
            <StatRow label="Mean Damage"    value={fmt(result.mean_damage, 2)} />
            <StatRow label="Median Damage"  value={fmt(result.median_damage, 2)} />
            <StatRow label="Std Dev"        value={fmt(result.std_damage, 2)} />
            <StatRow label="Min"            value={fmt(result.min_damage, 2)} />
            <StatRow label="Max"            value={fmt(result.max_damage, 2)} />
            <StatRow label="P5"             value={fmt(result.percentile_5, 2)} />
            <StatRow label="P95"            value={fmt(result.percentile_95, 2)} />
            <StatRow label="CV"             value={result.cv.toFixed(4)} />
            <StatRow label="Mean Crits"     value={fmt(result.mean_crits, 2)} />
            <StatRow label="Mean Procs"     value={fmt(result.mean_procs, 2)} />
            {/* Reliability score with colour */}
            <div className="flex items-center justify-between py-1.5">
              <span className="font-mono text-xs text-forge-dim">Reliability Score</span>
              <span className={`font-mono text-xs font-bold ${reliabilityColor(result.reliability_score)}`}>
                {result.reliability_score.toFixed(3)}
                {result.reliability_score >= 0.8 ? " (high)" : result.reliability_score >= 0.6 ? " (moderate)" : " (low)"}
              </span>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-48 text-forge-dim font-mono text-sm">
            {isRunning ? "Running simulation…" : "Configure and run a simulation to see results."}
          </div>
        )}
      </Panel>
    </div>
  );
}
