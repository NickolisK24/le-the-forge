/**
 * E9 — Build Editor Page
 *
 * Full build definition editor integrated with encounter simulation.
 * Manages the complete build state and triggers the encounter-build API.
 */

import { useState, useCallback } from "react";
import toast from "react-hot-toast";

import SkillSelector  from "./SkillSelector";
import GearPanel      from "./GearPanel";
import PassivePanel   from "./PassivePanel";
import BuffPanel      from "./BuffPanel";
import ResultsPanel   from "./ResultsPanel";
import DamageChart    from "./DamageChart";

import { simulateBuild, TEMPLATE_LABELS } from "@/services/buildApi";
import type {
  BuildDefinition, EncounterOverride, EnemyTemplateOpt,
} from "@/services/buildApi";
import type { EncounterResult } from "@/services/encounterApi";

// ---------------------------------------------------------------------------
// Default state
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

const DEFAULT_ENCOUNTER: EncounterOverride = {
  enemy_template: "STANDARD_BOSS",
  fight_duration: 60.0,
  tick_size:      0.1,
  distribution:   "SINGLE",
};

const TEMPLATES = Object.keys(TEMPLATE_LABELS) as EnemyTemplateOpt[];

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function BuildEditorPage() {
  const [build,    setBuild]   = useState<BuildDefinition>(DEFAULT_BUILD);
  const [encounter, setEnc]   = useState<EncounterOverride>(DEFAULT_ENCOUNTER);
  const [result,   setResult] = useState<EncounterResult | null>(null);
  const [loading,  setLoading] = useState(false);

  const patchBuild    = useCallback((p: Partial<BuildDefinition>) =>
    setBuild((prev) => ({ ...prev, ...p })), []);
  const patchEnc      = useCallback((p: Partial<EncounterOverride>) =>
    setEnc((prev) => ({ ...prev, ...p })), []);

  const handleRun = useCallback(async () => {
    setLoading(true);
    try {
      const res = await simulateBuild({ build, encounter });
      setResult(res);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Simulation failed");
    } finally {
      setLoading(false);
    }
  }, [build, encounter]);

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="mb-1 text-2xl font-bold text-forge-text">Build Editor</h1>
      <p className="mb-6 text-sm text-forge-muted">
        Define your build — class, skills, gear, passives, and buffs — then simulate against
        a boss template.
      </p>

      {/* ---- Build inputs ---- */}
      <div className="space-y-6 rounded-lg border border-forge-border bg-forge-surface p-6">
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

      {/* ---- Encounter settings ---- */}
      <div className="mt-4 rounded-lg border border-forge-border bg-forge-surface p-6">
        <h3 className="mb-3 text-sm font-semibold text-forge-accent uppercase tracking-wider">
          Encounter
        </h3>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-forge-muted uppercase tracking-wide">Template</label>
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
            <label className="text-xs text-forge-muted uppercase tracking-wide">
              Fight Duration (s)
            </label>
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
            <label className="text-xs text-forge-muted uppercase tracking-wide">Tick Size (s)</label>
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
            <label className="text-xs text-forge-muted uppercase tracking-wide">Distribution</label>
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
          {loading ? "Simulating…" : "Run Simulation"}
        </button>
      </div>

      {/* ---- Results ---- */}
      {(result || loading) && (
        <div className="mt-6 space-y-6 rounded-lg border border-forge-border bg-forge-surface p-6">
          <ResultsPanel result={result} isLoading={loading} />
          {result && result.damage_per_tick.length > 0 && (
            <>
              <hr className="border-forge-border" />
              <DamageChart
                data={result.damage_per_tick}
                tickSize={encounter.tick_size ?? 0.1}
              />
            </>
          )}
        </div>
      )}
    </div>
  );
}
