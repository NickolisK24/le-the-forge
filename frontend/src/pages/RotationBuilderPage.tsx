/**
 * G13 — Rotation Builder Page
 *
 * UI for building a skill rotation, configuring skills/GCD/encounter,
 * and viewing the resulting timeline and damage metrics.
 */

import { useState, useCallback } from "react";
import toast from "react-hot-toast";

import CooldownTimeline    from "@/components/CooldownTimeline";
import RotationResultsPanel from "@/components/RotationResultsPanel";
import {
  runRotation,
  type SkillDefinition,
  type RotationStep,
  type RotationResult,
} from "@/services/rotationApi";

// ---------------------------------------------------------------------------
// Defaults
// ---------------------------------------------------------------------------

const DEFAULT_SKILLS: SkillDefinition[] = [
  { skill_id: "Rip Blood",  base_damage: 150.0, cast_time: 0.0, cooldown: 1.0 },
  { skill_id: "Bone Curse", base_damage: 100.0, cast_time: 0.5, cooldown: 2.0 },
];

const DEFAULT_STEPS: RotationStep[] = [
  { skill_id: "Rip Blood",  priority: 0 },
  { skill_id: "Bone Curse", priority: 1 },
];

const TEMPLATES = [
  "TRAINING_DUMMY", "STANDARD_BOSS", "SHIELDED_BOSS", "ADD_FIGHT", "MOVEMENT_BOSS",
];

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function SkillRow({
  skill,
  onChange,
  onRemove,
  disabled,
}: {
  skill:    SkillDefinition;
  onChange: (s: SkillDefinition) => void;
  onRemove: () => void;
  disabled: boolean;
}) {
  const num = (field: keyof SkillDefinition, val: string) => {
    const v = parseFloat(val);
    if (!isNaN(v) && v >= 0) onChange({ ...skill, [field]: v });
  };

  return (
    <div className="grid grid-cols-5 gap-2 items-center">
      <input
        value={skill.skill_id}
        disabled={disabled}
        onChange={(e) => onChange({ ...skill, skill_id: e.target.value })}
        placeholder="Skill ID"
        className="col-span-1 rounded border border-forge-border bg-forge-input px-2 py-1.5 text-sm text-forge-text focus:border-forge-accent focus:outline-none disabled:opacity-50"
      />
      {(["base_damage", "cast_time", "cooldown"] as const).map((f) => (
        <input
          key={f}
          type="number"
          min={0}
          step={f === "base_damage" ? 10 : 0.1}
          value={skill[f] ?? 0}
          disabled={disabled}
          onChange={(e) => num(f, e.target.value)}
          placeholder={f.replace(/_/g, " ")}
          className="rounded border border-forge-border bg-forge-input px-2 py-1.5 text-sm text-forge-text focus:border-forge-accent focus:outline-none disabled:opacity-50"
        />
      ))}
      <button
        onClick={onRemove}
        disabled={disabled}
        className="rounded border border-red-700/50 px-2 py-1.5 text-xs text-red-400 hover:bg-red-900/20 disabled:opacity-50"
      >
        Remove
      </button>
    </div>
  );
}

function StepRow({
  step,
  onChange,
  onRemove,
  disabled,
}: {
  step:     RotationStep;
  onChange: (s: RotationStep) => void;
  onRemove: () => void;
  disabled: boolean;
}) {
  return (
    <div className="grid grid-cols-4 gap-2 items-center">
      <input
        value={step.skill_id}
        disabled={disabled}
        onChange={(e) => onChange({ ...step, skill_id: e.target.value })}
        placeholder="Skill ID"
        className="rounded border border-forge-border bg-forge-input px-2 py-1.5 text-sm text-forge-text focus:border-forge-accent focus:outline-none disabled:opacity-50"
      />
      <input
        type="number" min={0} step={1}
        value={step.priority ?? 0}
        disabled={disabled}
        onChange={(e) => {
          const v = parseInt(e.target.value, 10);
          if (!isNaN(v)) onChange({ ...step, priority: v });
        }}
        placeholder="Priority"
        className="rounded border border-forge-border bg-forge-input px-2 py-1.5 text-sm text-forge-text focus:border-forge-accent focus:outline-none disabled:opacity-50"
      />
      <input
        type="number" min={0} step={0.1}
        value={step.delay_after_cast ?? 0}
        disabled={disabled}
        onChange={(e) => {
          const v = parseFloat(e.target.value);
          if (!isNaN(v) && v >= 0) onChange({ ...step, delay_after_cast: v });
        }}
        placeholder="Delay (s)"
        className="rounded border border-forge-border bg-forge-input px-2 py-1.5 text-sm text-forge-text focus:border-forge-accent focus:outline-none disabled:opacity-50"
      />
      <button
        onClick={onRemove}
        disabled={disabled}
        className="rounded border border-red-700/50 px-2 py-1.5 text-xs text-red-400 hover:bg-red-900/20 disabled:opacity-50"
      >
        Remove
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function RotationBuilderPage() {
  const [skills,   setSkills]   = useState<SkillDefinition[]>(DEFAULT_SKILLS);
  const [steps,    setSteps]    = useState<RotationStep[]>(DEFAULT_STEPS);
  const [duration, setDuration] = useState(30.0);
  const [gcd,      setGcd]      = useState(0.0);
  const [template, setTemplate] = useState("STANDARD_BOSS");
  const [loading,  setLoading]  = useState(false);
  const [result,   setResult]   = useState<RotationResult | null>(null);

  const addSkill = () =>
    setSkills((prev) => [...prev, { skill_id: "", base_damage: 100.0, cooldown: 1.0 }]);

  const addStep = () =>
    setSteps((prev) => [...prev, { skill_id: "", priority: prev.length }]);

  const handleRun = useCallback(async () => {
    const hasEmpty = steps.some((s) => !s.skill_id.trim()) ||
                     skills.some((s) => !s.skill_id.trim());
    if (hasEmpty) {
      toast.error("All skill IDs must be non-empty.");
      return;
    }
    setLoading(true);
    try {
      const res = await runRotation({
        rotation:  { steps, loop: true },
        skills,
        duration,
        gcd,
        encounter: { enemy_template: template, fight_duration: duration, distribution: "SINGLE", crit_chance: 0.0 },
      });
      setResult(res);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Simulation failed");
    } finally {
      setLoading(false);
    }
  }, [skills, steps, duration, gcd, template]);

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="mb-1 text-2xl font-bold text-forge-text">Rotation Builder</h1>
      <p className="mb-6 text-sm text-forge-muted">
        Build a skill rotation, set cooldowns and priorities, then simulate against a boss template.
      </p>

      {/* Skills */}
      <div className="rounded-lg border border-forge-border bg-forge-surface p-6">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-forge-accent">Skills</h2>
          <div className="grid grid-cols-5 gap-2 text-xs uppercase tracking-wide text-forge-muted">
            <span>ID</span><span>Base Dmg</span><span>Cast (s)</span><span>CD (s)</span><span />
          </div>
        </div>
        <div className="space-y-2">
          {skills.map((s, i) => (
            <SkillRow
              key={i}
              skill={s}
              onChange={(ns) => setSkills((prev) => prev.map((x, j) => j === i ? ns : x))}
              onRemove={() => setSkills((prev) => prev.filter((_, j) => j !== i))}
              disabled={loading}
            />
          ))}
        </div>
        <button
          onClick={addSkill}
          disabled={loading}
          className="mt-3 rounded border border-forge-border px-3 py-1.5 text-xs text-forge-muted hover:border-forge-accent hover:text-forge-accent disabled:opacity-50"
        >
          + Add Skill
        </button>
      </div>

      {/* Rotation Steps */}
      <div className="mt-4 rounded-lg border border-forge-border bg-forge-surface p-6">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-forge-accent">Rotation</h2>
          <div className="grid grid-cols-4 gap-2 text-xs uppercase tracking-wide text-forge-muted">
            <span>Skill ID</span><span>Priority</span><span>Delay (s)</span><span />
          </div>
        </div>
        <div className="space-y-2">
          {steps.map((s, i) => (
            <StepRow
              key={i}
              step={s}
              onChange={(ns) => setSteps((prev) => prev.map((x, j) => j === i ? ns : x))}
              onRemove={() => setSteps((prev) => prev.filter((_, j) => j !== i))}
              disabled={loading}
            />
          ))}
        </div>
        <button
          onClick={addStep}
          disabled={loading}
          className="mt-3 rounded border border-forge-border px-3 py-1.5 text-xs text-forge-muted hover:border-forge-accent hover:text-forge-accent disabled:opacity-50"
        >
          + Add Step
        </button>
      </div>

      {/* Sim Settings */}
      <div className="mt-4 grid grid-cols-2 gap-4 rounded-lg border border-forge-border bg-forge-surface p-6 sm:grid-cols-4">
        <div className="flex flex-col gap-1">
          <label className="text-xs uppercase tracking-wide text-forge-muted">Duration (s)</label>
          <input type="number" min={1} max={3600} step={1} value={duration} disabled={loading}
            onChange={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v) && v >= 1) setDuration(v); }}
            className="rounded border border-forge-border bg-forge-input px-3 py-2 text-sm text-forge-text focus:border-forge-accent focus:outline-none disabled:opacity-50" />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs uppercase tracking-wide text-forge-muted">GCD (s)</label>
          <input type="number" min={0} max={10} step={0.1} value={gcd} disabled={loading}
            onChange={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v) && v >= 0) setGcd(v); }}
            className="rounded border border-forge-border bg-forge-input px-3 py-2 text-sm text-forge-text focus:border-forge-accent focus:outline-none disabled:opacity-50" />
        </div>
        <div className="flex flex-col gap-1 sm:col-span-2">
          <label className="text-xs uppercase tracking-wide text-forge-muted">Template</label>
          <select value={template} disabled={loading}
            onChange={(e) => setTemplate(e.target.value)}
            className="rounded border border-forge-border bg-forge-input px-3 py-2 text-sm text-forge-text focus:border-forge-accent focus:outline-none disabled:opacity-50">
            {TEMPLATES.map((t) => <option key={t} value={t}>{t.replace(/_/g, " ")}</option>)}
          </select>
        </div>
      </div>

      {/* Run */}
      <div className="mt-4 flex justify-end">
        <button
          onClick={handleRun}
          disabled={loading || steps.length === 0 || skills.length === 0}
          className="rounded bg-forge-accent px-6 py-2 text-sm font-semibold text-forge-bg hover:brightness-110 active:brightness-90 disabled:cursor-not-allowed disabled:opacity-50 transition-all"
        >
          {loading ? "Simulating…" : "Run Rotation"}
        </button>
      </div>

      {/* Results */}
      {(result || loading) && (
        <div className="mt-6 space-y-6 rounded-lg border border-forge-border bg-forge-surface p-6">
          <RotationResultsPanel result={result} isLoading={loading} />
          {result && result.cast_results.length > 0 && (
            <>
              <hr className="border-forge-border" />
              <div>
                <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-forge-accent">
                  Cast Timeline
                </h3>
                <CooldownTimeline castResults={result.cast_results} duration={duration} />
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
