/**
 * H18 — Conditional Builder Page
 *
 * Route: /conditional
 *
 * Allows users to:
 *   - Define a set of conditional modifiers
 *   - Configure the simulation state (HP %, elapsed time, buffs, statuses)
 *   - Submit to POST /api/simulate/conditional
 *   - View adjusted damage and which modifiers fired
 */

import { useState, useCallback } from "react";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";

import { Button, Panel, SectionLabel, Spinner } from "@/components/ui";
import ConditionEditor, {
  type ConditionDraft,
  type ConditionType,
  type ComparisonOperator,
} from "@/components/ConditionEditor";
import { simulateApi, type ConditionalResult } from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type ModifierType = "additive" | "multiplicative" | "override";

interface ModifierDraft {
  modifier_id:   string;
  stat_target:   string;
  value:         number;
  modifier_type: ModifierType;
  condition:     ConditionDraft;
}

interface SimStateDraft {
  player_health_pct:     number;
  target_health_pct:     number;
  elapsed_time:          number;
  active_buffs:          string;   // comma-separated
  active_status_effects: string;   // "shock:2,ignite:1"
}

// ---------------------------------------------------------------------------
// Defaults
// ---------------------------------------------------------------------------

function defaultCondition(): ConditionDraft {
  return {
    condition_id:        "",
    condition_type:      "target_health_pct",
    threshold_value:     0.5,
    comparison_operator: "lt",
    duration:            null,
  };
}

function defaultModifier(idx: number): ModifierDraft {
  return {
    modifier_id:   `mod_${idx + 1}`,
    stat_target:   "spell_damage_pct",
    value:         20,
    modifier_type: "additive",
    condition:     { ...defaultCondition(), condition_id: `cond_${idx + 1}` },
  };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function parseStatusEffects(raw: string): Record<string, number> {
  const out: Record<string, number> = {};
  for (const part of raw.split(",").map(s => s.trim()).filter(Boolean)) {
    const [id, n] = part.split(":").map(s => s.trim());
    if (id) out[id] = parseInt(n ?? "1", 10) || 1;
  }
  return out;
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

const inputCls =
  "w-full rounded-sm border border-forge-border bg-forge-surface2 px-3 py-2 " +
  "font-body text-sm text-forge-text outline-none focus:border-forge-amber/60";
const labelCls =
  "block font-mono text-[11px] uppercase tracking-widest text-forge-dim mb-1";

function ModifierCard({
  mod, idx, onChange, onRemove,
}: {
  mod:      ModifierDraft;
  idx:      number;
  onChange: (m: ModifierDraft) => void;
  onRemove: () => void;
}) {
  function set<K extends keyof ModifierDraft>(k: K, v: ModifierDraft[K]) {
    onChange({ ...mod, [k]: v });
  }

  return (
    <div className="rounded border border-forge-border bg-forge-surface p-4 space-y-3">
      <div className="flex items-center justify-between">
        <span className="font-mono text-xs text-forge-amber">Modifier {idx + 1}</span>
        <button
          type="button"
          onClick={onRemove}
          className="font-mono text-[10px] text-forge-dim hover:text-red-400"
        >
          × Remove
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelCls}>Modifier ID</label>
          <input className={inputCls} value={mod.modifier_id}
            onChange={e => set("modifier_id", e.target.value)} />
        </div>
        <div>
          <label className={labelCls}>Stat Target</label>
          <input className={inputCls} value={mod.stat_target}
            placeholder="e.g. spell_damage_pct"
            onChange={e => set("stat_target", e.target.value)} />
        </div>
        <div>
          <label className={labelCls}>Value</label>
          <input type="number" className={inputCls} value={mod.value}
            onChange={e => set("value", Number(e.target.value))} />
        </div>
        <div>
          <label className={labelCls}>Modifier Type</label>
          <select className={inputCls} value={mod.modifier_type}
            onChange={e => set("modifier_type", e.target.value as ModifierType)}>
            <option value="additive">Additive</option>
            <option value="multiplicative">Multiplicative</option>
            <option value="override">Override</option>
          </select>
        </div>
      </div>

      <div>
        <SectionLabel>Condition</SectionLabel>
        <ConditionEditor value={mod.condition} onChange={c => set("condition", c)} />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function ConditionalBuilderPage() {
  const [baseDamage, setBaseDamage] = useState<number>(1000);
  const [modifiers, setModifiers]   = useState<ModifierDraft[]>([defaultModifier(0)]);
  const [simState, setSimState]     = useState<SimStateDraft>({
    player_health_pct:     1.0,
    target_health_pct:     0.4,
    elapsed_time:          5.0,
    active_buffs:          "",
    active_status_effects: "",
  });
  const [result, setResult] = useState<ConditionalResult | null>(null);

  function setSimField<K extends keyof SimStateDraft>(k: K, v: SimStateDraft[K]) {
    setSimState(s => ({ ...s, [k]: v }));
  }

  const mutation = useMutation({
    mutationFn: async () => {
      const payload = {
        base_damage: baseDamage,
        state: {
          player_health_pct:     simState.player_health_pct,
          target_health_pct:     simState.target_health_pct,
          elapsed_time:          simState.elapsed_time,
          active_buffs:          simState.active_buffs.split(",").map(s => s.trim()).filter(Boolean),
          active_status_effects: parseStatusEffects(simState.active_status_effects),
        },
        modifiers: modifiers.map(m => ({
          modifier_id:   m.modifier_id,
          stat_target:   m.stat_target,
          value:         m.value,
          modifier_type: m.modifier_type,
          condition: {
            condition_id:        m.condition.condition_id,
            condition_type:      m.condition.condition_type,
            threshold_value:     m.condition.threshold_value,
            comparison_operator: m.condition.comparison_operator,
            duration:            m.condition.duration,
          },
        })),
      };
      const res = await simulateApi.conditional(payload);
      return res;
    },
    onSuccess: data => {
      setResult(data.data!);
    },
    onError: (err: Error) => {
      toast.error(err.message || "Simulation failed");
    },
  });

  const addModifier = useCallback(() => {
    setModifiers(ms => [...ms, defaultModifier(ms.length)]);
  }, []);

  const removeModifier = useCallback((idx: number) => {
    setModifiers(ms => ms.filter((_, i) => i !== idx));
  }, []);

  const updateModifier = useCallback((idx: number, m: ModifierDraft) => {
    setModifiers(ms => ms.map((x, i) => i === idx ? m : x));
  }, []);

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <h1 className="font-display text-2xl text-forge-text">Conditional Builder</h1>
      <p className="font-body text-sm text-forge-dim">
        Define conditional modifiers and simulate their effect on a damage value based on
        fight state (HP, buffs, statuses, elapsed time).
      </p>

      {/* Base damage */}
      <Panel>
        <SectionLabel>Base Damage</SectionLabel>
        <input
          type="number"
          min={0}
          className={inputCls}
          value={baseDamage}
          onChange={e => setBaseDamage(Number(e.target.value))}
        />
      </Panel>

      {/* Simulation state */}
      <Panel>
        <SectionLabel>Simulation State</SectionLabel>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={labelCls}>Player HP % (0–1)</label>
            <input type="number" min={0} max={1} step={0.05} className={inputCls}
              value={simState.player_health_pct}
              onChange={e => setSimField("player_health_pct", Number(e.target.value))} />
          </div>
          <div>
            <label className={labelCls}>Target HP % (0–1)</label>
            <input type="number" min={0} max={1} step={0.05} className={inputCls}
              value={simState.target_health_pct}
              onChange={e => setSimField("target_health_pct", Number(e.target.value))} />
          </div>
          <div>
            <label className={labelCls}>Elapsed Time (s)</label>
            <input type="number" min={0} step={0.5} className={inputCls}
              value={simState.elapsed_time}
              onChange={e => setSimField("elapsed_time", Number(e.target.value))} />
          </div>
          <div>
            <label className={labelCls}>Active Buffs (comma-separated)</label>
            <input className={inputCls} value={simState.active_buffs}
              placeholder="power_surge, haste"
              onChange={e => setSimField("active_buffs", e.target.value)} />
          </div>
          <div className="col-span-2">
            <label className={labelCls}>Status Effects (id:stacks, e.g. shock:2,ignite:1)</label>
            <input className={inputCls} value={simState.active_status_effects}
              placeholder="shock:2, ignite:1"
              onChange={e => setSimField("active_status_effects", e.target.value)} />
          </div>
        </div>
      </Panel>

      {/* Modifiers */}
      <Panel>
        <div className="flex items-center justify-between mb-3">
          <SectionLabel>Conditional Modifiers</SectionLabel>
          <Button size="sm" variant="secondary" onClick={addModifier}>+ Add Modifier</Button>
        </div>
        <div className="space-y-4">
          {modifiers.map((mod, idx) => (
            <ModifierCard
              key={idx}
              mod={mod}
              idx={idx}
              onChange={m => updateModifier(idx, m)}
              onRemove={() => removeModifier(idx)}
            />
          ))}
          {modifiers.length === 0 && (
            <p className="font-body text-sm text-forge-dim text-center py-4">
              No modifiers. Click "+ Add Modifier" to begin.
            </p>
          )}
        </div>
      </Panel>

      {/* Submit */}
      <div className="flex justify-end">
        <Button
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending}
        >
          {mutation.isPending ? <Spinner size={16} /> : "Simulate"}
        </Button>
      </div>

      {/* Result */}
      {result && (
        <Panel>
          <SectionLabel>Result</SectionLabel>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">Base</div>
              <div className="font-display text-2xl text-forge-text">{result.base_damage.toLocaleString()}</div>
            </div>
            <div className="text-center">
              <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">Adjusted</div>
              <div className="font-display text-2xl text-forge-amber">{result.adjusted_damage.toLocaleString()}</div>
            </div>
            <div className="text-center">
              <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">Multiplier</div>
              <div className="font-display text-2xl text-forge-text">{result.damage_multiplier.toFixed(2)}×</div>
            </div>
          </div>

          {result.active_modifier_ids.length > 0 && (
            <div className="mb-3">
              <div className={labelCls}>Active Modifiers</div>
              <div className="flex flex-wrap gap-2">
                {result.active_modifier_ids.map(id => (
                  <span key={id} className="rounded bg-forge-amber/20 px-2 py-0.5 font-mono text-xs text-forge-amber">
                    {id}
                  </span>
                ))}
              </div>
            </div>
          )}

          {Object.keys(result.stat_deltas).length > 0 && (
            <div>
              <div className={labelCls}>Stat Deltas</div>
              <div className="rounded border border-forge-border bg-forge-surface2 p-2 font-mono text-xs text-forge-text space-y-1">
                {Object.entries(result.stat_deltas).map(([stat, val]) => (
                  <div key={stat} className="flex justify-between">
                    <span className="text-forge-dim">{stat}</span>
                    <span className={val >= 0 ? "text-green-400" : "text-red-400"}>
                      {val >= 0 ? "+" : ""}{val.toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Panel>
      )}
    </div>
  );
}
