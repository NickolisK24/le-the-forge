/**
 * F10 — Optimizer Page
 *
 * UI for build optimization:
 *   1. Configure base build (class, mastery, skill, gear, passives, buffs)
 *   2. Configure OptimizationConfig (metric, variant count, depth, seed)
 *   3. Configure encounter settings
 *   4. Run → show ranked results + comparison panel
 */

import { useState, useCallback } from "react";
import toast from "react-hot-toast";

import SkillSelector  from "../encounter/SkillSelector";
import GearPanel      from "../encounter/GearPanel";
import PassivePanel   from "../encounter/PassivePanel";
import BuffPanel      from "../encounter/BuffPanel";

import OptimizationProgress       from "./OptimizationProgress";
import OptimizationResultsTable   from "./OptimizationResultsTable";
import VariantComparisonPanel     from "./VariantComparisonPanel";

import {
  runOptimization,
  METRIC_LABELS,
  type OptimizationConfig,
  type OptimizeBuildResponse,
} from "@/services/optimizerApi";
import { TEMPLATE_LABELS }       from "@/services/buildApi";
import type { BuildDefinition, EncounterOverride, EnemyTemplateOpt } from "@/services/buildApi";

// ---------------------------------------------------------------------------
// Defaults
// ---------------------------------------------------------------------------

const DEFAULT_BUILD: BuildDefinition = {
  character_class: "Acolyte",
  mastery:         "Lich",
  skill_id:        "Rip Blood",
  skill_level:     20,
  gear:            [],
  passive_ids:     [],
  buffs:           [],
};

const DEFAULT_CONFIG: OptimizationConfig = {
  target_metric:  "dps",
  max_variants:   50,
  mutation_depth: 2,
  constraints:    {},
  random_seed:    42,
};

const DEFAULT_ENCOUNTER: EncounterOverride = {
  enemy_template: "STANDARD_BOSS",
  fight_duration: 60.0,
  tick_size:      0.1,
  distribution:   "SINGLE",
};

const TEMPLATES = Object.keys(TEMPLATE_LABELS) as EnemyTemplateOpt[];
const METRICS   = Object.keys(METRIC_LABELS) as (keyof typeof METRIC_LABELS)[];

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function OptimizerPage() {
  const [build,    setBuild]    = useState<BuildDefinition>(DEFAULT_BUILD);
  const [config,   setConfig]   = useState<OptimizationConfig>(DEFAULT_CONFIG);
  const [encounter, setEnc]     = useState<EncounterOverride>(DEFAULT_ENCOUNTER);

  const [loading,  setLoading]  = useState(false);
  const [response, setResponse] = useState<OptimizeBuildResponse | null>(null);
  const [selectedRank, setSelectedRank] = useState<number | null>(null);

  const patchBuild    = useCallback((p: Partial<BuildDefinition>) =>
    setBuild((prev) => ({ ...prev, ...p })), []);
  const patchConfig   = useCallback((p: Partial<OptimizationConfig>) =>
    setConfig((prev) => ({ ...prev, ...p })), []);
  const patchEnc      = useCallback((p: Partial<EncounterOverride>) =>
    setEnc((prev) => ({ ...prev, ...p })), []);

  const handleRun = useCallback(async () => {
    setLoading(true);
    setResponse(null);
    setSelectedRank(null);
    try {
      const res = await runOptimization({ build, config, encounter });
      setResponse(res);
      if (res.results.length > 0) setSelectedRank(res.results[0].rank);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Optimization failed");
    } finally {
      setLoading(false);
    }
  }, [build, config, encounter]);

  const selectedResult = response?.results.find((r) => r.rank === selectedRank) ?? null;
  const bestResult     = response?.results[0] ?? null;

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="mb-1 text-2xl font-bold text-forge-text">Build Optimizer</h1>
      <p className="mb-6 text-sm text-forge-muted">
        Automatically generate and rank build variants to find the highest-scoring mutations.
      </p>

      {/* ---- Build inputs ---- */}
      <div className="space-y-6 rounded-lg border border-forge-border bg-forge-surface p-6">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-forge-accent">
          Base Build
        </h2>

        <SkillSelector
          values={build}
          onChange={(p) => patchBuild(p as Partial<BuildDefinition>)}
          disabled={loading}
        />
        <hr className="border-forge-border" />
        <GearPanel
          gear={build.gear}
          onChange={(gear) => patchBuild({ gear })}
          disabled={loading}
        />
        <hr className="border-forge-border" />
        <PassivePanel
          passiveIds={build.passive_ids}
          onChange={(ids) => patchBuild({ passive_ids: ids })}
          disabled={loading}
        />
        <hr className="border-forge-border" />
        <BuffPanel
          buffs={build.buffs}
          onChange={(buffs) => patchBuild({ buffs })}
          disabled={loading}
        />
      </div>

      {/* ---- Optimization config ---- */}
      <div className="mt-4 rounded-lg border border-forge-border bg-forge-surface p-6">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-forge-accent">
          Optimization Settings
        </h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {/* Metric */}
          <div className="flex flex-col gap-1">
            <label className="text-xs uppercase tracking-wide text-forge-muted">Metric</label>
            <select
              value={config.target_metric}
              disabled={loading}
              onChange={(e) => patchConfig({ target_metric: e.target.value as OptimizationConfig["target_metric"] })}
              className="
                w-full rounded border border-forge-border bg-forge-input
                px-3 py-2 text-sm text-forge-text
                focus:border-forge-accent focus:outline-none disabled:opacity-50
              "
            >
              {METRICS.map((m) => (
                <option key={m} value={m}>{METRIC_LABELS[m]}</option>
              ))}
            </select>
          </div>

          {/* Max variants */}
          <div className="flex flex-col gap-1">
            <label className="text-xs uppercase tracking-wide text-forge-muted">Max Variants</label>
            <input
              type="number" min={1} max={1000} step={1}
              value={config.max_variants}
              disabled={loading}
              onChange={(e) => {
                const v = parseInt(e.target.value, 10);
                if (!isNaN(v) && v >= 1 && v <= 1000) patchConfig({ max_variants: v });
              }}
              className="
                w-full rounded border border-forge-border bg-forge-input
                px-3 py-2 text-sm text-forge-text
                focus:border-forge-accent focus:outline-none disabled:opacity-50
              "
            />
          </div>

          {/* Mutation depth */}
          <div className="flex flex-col gap-1">
            <label className="text-xs uppercase tracking-wide text-forge-muted">Mutation Depth</label>
            <input
              type="number" min={1} max={10} step={1}
              value={config.mutation_depth}
              disabled={loading}
              onChange={(e) => {
                const v = parseInt(e.target.value, 10);
                if (!isNaN(v) && v >= 1 && v <= 10) patchConfig({ mutation_depth: v });
              }}
              className="
                w-full rounded border border-forge-border bg-forge-input
                px-3 py-2 text-sm text-forge-text
                focus:border-forge-accent focus:outline-none disabled:opacity-50
              "
            />
          </div>

          {/* Seed */}
          <div className="flex flex-col gap-1">
            <label className="text-xs uppercase tracking-wide text-forge-muted">RNG Seed</label>
            <input
              type="number"
              value={config.random_seed}
              disabled={loading}
              onChange={(e) => {
                const v = parseInt(e.target.value, 10);
                if (!isNaN(v)) patchConfig({ random_seed: v });
              }}
              className="
                w-full rounded border border-forge-border bg-forge-input
                px-3 py-2 text-sm text-forge-text
                focus:border-forge-accent focus:outline-none disabled:opacity-50
              "
            />
          </div>
        </div>
      </div>

      {/* ---- Encounter settings ---- */}
      <div className="mt-4 rounded-lg border border-forge-border bg-forge-surface p-6">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-forge-accent">
          Encounter
        </h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="flex flex-col gap-1">
            <label className="text-xs uppercase tracking-wide text-forge-muted">Template</label>
            <select
              value={encounter.enemy_template}
              disabled={loading}
              onChange={(e) => patchEnc({ enemy_template: e.target.value as EnemyTemplateOpt })}
              className="
                w-full rounded border border-forge-border bg-forge-input
                px-3 py-2 text-sm text-forge-text
                focus:border-forge-accent focus:outline-none disabled:opacity-50
              "
            >
              {TEMPLATES.map((t) => (
                <option key={t} value={t}>{TEMPLATE_LABELS[t]}</option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs uppercase tracking-wide text-forge-muted">Duration (s)</label>
            <input
              type="number" min={1} max={3600} step={1}
              value={encounter.fight_duration}
              disabled={loading}
              onChange={(e) => {
                const v = parseFloat(e.target.value);
                if (!isNaN(v) && v >= 1) patchEnc({ fight_duration: v });
              }}
              className="
                w-full rounded border border-forge-border bg-forge-input
                px-3 py-2 text-sm text-forge-text
                focus:border-forge-accent focus:outline-none disabled:opacity-50
              "
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs uppercase tracking-wide text-forge-muted">Tick Size (s)</label>
            <input
              type="number" min={0.01} max={10} step={0.01}
              value={encounter.tick_size}
              disabled={loading}
              onChange={(e) => {
                const v = parseFloat(e.target.value);
                if (!isNaN(v) && v >= 0.01) patchEnc({ tick_size: v });
              }}
              className="
                w-full rounded border border-forge-border bg-forge-input
                px-3 py-2 text-sm text-forge-text
                focus:border-forge-accent focus:outline-none disabled:opacity-50
              "
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs uppercase tracking-wide text-forge-muted">Distribution</label>
            <select
              value={encounter.distribution}
              disabled={loading}
              onChange={(e) => patchEnc({
                distribution: e.target.value as EncounterOverride["distribution"],
              })}
              className="
                w-full rounded border border-forge-border bg-forge-input
                px-3 py-2 text-sm text-forge-text
                focus:border-forge-accent focus:outline-none disabled:opacity-50
              "
            >
              {(["SINGLE", "CLEAVE", "SPLIT", "CHAIN"] as const).map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* ---- Run button ---- */}
      <div className="mt-4 flex justify-end">
        <button
          onClick={handleRun}
          disabled={loading}
          className="
            rounded bg-forge-accent px-6 py-2 text-sm font-semibold text-forge-bg
            hover:brightness-110 active:brightness-90
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-all
          "
        >
          {loading ? "Optimizing…" : "Run Optimizer"}
        </button>
      </div>

      {/* ---- Progress (while loading) ---- */}
      {loading && (
        <div className="mt-4 rounded-lg border border-forge-border bg-forge-surface p-4">
          <OptimizationProgress
            total={config.max_variants}
            completed={0}
            failed={0}
          />
        </div>
      )}

      {/* ---- Results ---- */}
      {response && !loading && (
        <div className="mt-6 space-y-4">
          {/* Summary stats */}
          <div className="flex flex-wrap gap-6 rounded-lg border border-forge-border bg-forge-surface px-6 py-4 text-sm">
            <div>
              <span className="text-forge-muted">Generated: </span>
              <span className="font-semibold text-forge-text">{response.total_variants_generated}</span>
            </div>
            <div>
              <span className="text-forge-muted">Passed constraints: </span>
              <span className="font-semibold text-forge-text">{response.variants_passed_constraints}</span>
            </div>
            <div>
              <span className="text-forge-muted">Simulated: </span>
              <span className="font-semibold text-forge-text">{response.variants_simulated}</span>
            </div>
            {response.variants_failed_simulation > 0 && (
              <div>
                <span className="text-forge-muted">Failed: </span>
                <span className="font-semibold text-red-400">{response.variants_failed_simulation}</span>
              </div>
            )}
          </div>

          {/* Ranked table */}
          <div className="rounded-lg border border-forge-border bg-forge-surface p-6">
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-forge-accent">
              Rankings — {METRIC_LABELS[config.target_metric as keyof typeof METRIC_LABELS] ?? config.target_metric}
            </h2>
            <OptimizationResultsTable
              results={response.results}
              metric={METRIC_LABELS[config.target_metric as keyof typeof METRIC_LABELS] ?? config.target_metric}
              selectedRank={selectedRank}
              onSelectRank={setSelectedRank}
            />
          </div>

          {/* Comparison panel — only when a non-#1 row is selected */}
          {bestResult && selectedResult && selectedResult.rank !== bestResult.rank && (
            <div className="rounded-lg border border-forge-border bg-forge-surface p-6">
              <VariantComparisonPanel base={bestResult} compared={selectedResult} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
