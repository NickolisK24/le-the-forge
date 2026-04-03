/**
 * I15 — Multi-Target Simulator Page
 *
 * Route: /multi-target
 *
 * Allows users to:
 *   - Choose a target template (single_boss / elite_pack / mob_swarm)
 *     or configure custom targets
 *   - Set base_damage, distribution, selection_mode, tick_size, max_duration
 *   - Submit to POST /api/simulate/multi-target
 *   - View kill summary, metrics table, and damage chart (I16)
 */

import { useState, useCallback } from "react";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";

import { Button, Panel, SectionLabel, Spinner } from "@/components/ui";
import TargetConfigPanel, { type TargetSpec } from "@/components/TargetConfigPanel";
import MultiTargetChart from "@/components/MultiTargetChart";
import { simulateApi, type MultiTargetResult } from "@/lib/api";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const TEMPLATES = [
  { value: "",            label: "Custom targets" },
  { value: "single_boss", label: "Single Boss" },
  { value: "elite_pack",  label: "Elite Pack" },
  { value: "mob_swarm",   label: "Mob Swarm" },
];

const DISTRIBUTIONS = [
  { value: "full_aoe",      label: "Full AOE" },
  { value: "single_target", label: "Single Target" },
  { value: "split_damage",  label: "Split Damage" },
  { value: "splash",        label: "Splash" },
  { value: "chain",         label: "Chain" },
];

const SELECTION_MODES = [
  { value: "all_targets",    label: "All Targets" },
  { value: "nearest",        label: "Nearest" },
  { value: "random",         label: "Random" },
  { value: "lowest_health",  label: "Lowest Health" },
  { value: "highest_health", label: "Highest Health" },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const inputCls =
  "w-full rounded-sm border border-forge-border bg-forge-surface2 px-3 py-2 " +
  "font-body text-sm text-forge-text outline-none focus:border-forge-amber/60";
const labelCls =
  "block font-mono text-[11px] uppercase tracking-widest text-forge-dim mb-1";

function fmt(n: number | null | undefined): string {
  if (n == null) return "—";
  return n.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function MultiTargetSimulatorPage() {
  const [template,      setTemplate]      = useState<string>("");
  const [targets,       setTargets]       = useState<TargetSpec[]>([
    { target_id: "target_1", max_health: 10000, position_index: 0 },
    { target_id: "target_2", max_health: 8000,  position_index: 1 },
  ]);
  const [baseDamage,    setBaseDamage]    = useState<number>(500);
  const [distribution,  setDistribution]  = useState<string>("full_aoe");
  const [selectionMode, setSelectionMode] = useState<string>("all_targets");
  const [tickSize,      setTickSize]      = useState<number>(0.1);
  const [maxDuration,   setMaxDuration]   = useState<number>(60);
  const [result,        setResult]        = useState<MultiTargetResult | null>(null);

  const mutation = useMutation({
    mutationFn: async () => {
      const payload: Record<string, unknown> = {
        base_damage:    baseDamage,
        distribution,
        selection_mode: selectionMode,
        tick_size:      tickSize,
        max_duration:   maxDuration,
      };

      if (template) {
        payload.template = template;
      } else {
        payload.targets = targets;
      }

      const res = await simulateApi.multiTarget(payload);
      if (res.errors) {
        throw new Error(res.errors[0]?.message ?? "Simulation failed");
      }
      return res.data!;
    },
    onSuccess: data => {
      setResult(data);
    },
    onError: (err: Error) => {
      toast.error(err.message || "Simulation failed");
    },
  });

  const handleSubmit = useCallback(() => {
    if (!template && targets.length === 0) {
      toast.error("Add at least one target or select a template.");
      return;
    }
    mutation.mutate();
  }, [template, targets, mutation]);

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <h1 className="font-display text-2xl text-forge-text">Multi-Target Simulator</h1>
      <p className="font-body text-sm text-forge-dim">
        Simulate AOE, chain, splash, or single-target damage against multiple enemies.
        Choose a preset template or configure targets manually.
      </p>

      {/* Simulation parameters */}
      <Panel>
        <SectionLabel>Simulation Parameters</SectionLabel>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Base Damage (per second)</label>
            <input
              type="number"
              min={1}
              className={inputCls}
              value={baseDamage}
              onChange={e => setBaseDamage(Number(e.target.value))}
            />
          </div>
          <div>
            <label className={labelCls}>Distribution</label>
            <select
              className={inputCls}
              value={distribution}
              onChange={e => setDistribution(e.target.value)}
            >
              {DISTRIBUTIONS.map(d => (
                <option key={d.value} value={d.value}>{d.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Selection Mode</label>
            <select
              className={inputCls}
              value={selectionMode}
              onChange={e => setSelectionMode(e.target.value)}
            >
              {SELECTION_MODES.map(s => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Tick Size (s)</label>
            <input
              type="number"
              min={0.01}
              max={1}
              step={0.01}
              className={inputCls}
              value={tickSize}
              onChange={e => setTickSize(Number(e.target.value))}
            />
          </div>
          <div>
            <label className={labelCls}>Max Duration (s)</label>
            <input
              type="number"
              min={1}
              max={300}
              className={inputCls}
              value={maxDuration}
              onChange={e => setMaxDuration(Number(e.target.value))}
            />
          </div>
        </div>
      </Panel>

      {/* Template or custom targets */}
      <Panel>
        <SectionLabel>Targets</SectionLabel>
        <div className="mb-4">
          <label className={labelCls}>Template</label>
          <select
            className={inputCls}
            value={template}
            onChange={e => setTemplate(e.target.value)}
          >
            {TEMPLATES.map(t => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
          {template && (
            <p className="mt-1.5 font-mono text-[11px] text-forge-dim">
              Using preset template — custom target list below is ignored.
            </p>
          )}
        </div>

        {!template && (
          <TargetConfigPanel targets={targets} onChange={setTargets} />
        )}
      </Panel>

      {/* Submit */}
      <div className="flex justify-end">
        <Button onClick={handleSubmit} disabled={mutation.isPending}>
          {mutation.isPending ? <Spinner size="sm" /> : "Run Simulation"}
        </Button>
      </div>

      {/* Results */}
      {result && (
        <>
          {/* Summary banner */}
          <Panel>
            <SectionLabel>Summary</SectionLabel>
            <div className="grid grid-cols-3 gap-4 mb-2">
              <div className="text-center">
                <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">
                  Cleared
                </div>
                <div className={`font-display text-2xl ${result.cleared ? "text-green-400" : "text-red-400"}`}>
                  {result.cleared ? "Yes" : "No"}
                </div>
              </div>
              <div className="text-center">
                <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">
                  Time to Clear
                </div>
                <div className="font-display text-2xl text-forge-amber">
                  {result.time_to_clear != null ? `${result.time_to_clear.toFixed(2)}s` : "—"}
                </div>
              </div>
              <div className="text-center">
                <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">
                  Total Kills
                </div>
                <div className="font-display text-2xl text-forge-text">
                  {result.total_kills}
                </div>
              </div>
            </div>
          </Panel>

          {/* Per-target metrics */}
          <Panel>
            <SectionLabel>Per-Target Metrics</SectionLabel>
            <div className="overflow-x-auto">
              <table className="w-full font-mono text-xs text-forge-text">
                <thead>
                  <tr className="border-b border-forge-border text-forge-dim">
                    <th className="py-2 text-left">Target</th>
                    <th className="py-2 text-right">Total Damage</th>
                    <th className="py-2 text-right">Overkill</th>
                    <th className="py-2 text-right">Kill Time</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.keys(result.metrics.damage_per_target).map(tid => (
                    <tr key={tid} className="border-b border-forge-border/40">
                      <td className="py-1.5 text-forge-amber">{tid}</td>
                      <td className="py-1.5 text-right">
                        {fmt(result.metrics.damage_per_target[tid])}
                      </td>
                      <td className="py-1.5 text-right text-forge-dim">
                        {fmt(result.metrics.overkill_waste[tid] ?? 0)}
                      </td>
                      <td className="py-1.5 text-right">
                        {result.metrics.kill_times[tid] != null
                          ? `${result.metrics.kill_times[tid].toFixed(2)}s`
                          : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>

          {/* Damage chart */}
          <Panel>
            <MultiTargetChart events={result.damage_events} />
          </Panel>
        </>
      )}
    </div>
  );
}
