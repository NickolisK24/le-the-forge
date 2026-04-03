/**
 * H18 — ConditionEditor
 *
 * Allows building a single Condition object:
 *   - condition_type selector
 *   - threshold_value input (for numeric types)
 *   - comparison_operator selector (for numeric types)
 */

import { useId } from "react";

export type ConditionType =
  | "target_health_pct"
  | "player_health_pct"
  | "time_elapsed"
  | "buff_active"
  | "status_present";

export type ComparisonOperator = "lt" | "le" | "eq" | "ge" | "gt";

export interface ConditionDraft {
  condition_id:        string;
  condition_type:      ConditionType;
  threshold_value:     number | null;
  comparison_operator: ComparisonOperator;
  duration:            number | null;
}

interface Props {
  value:    ConditionDraft;
  onChange: (v: ConditionDraft) => void;
}

const NUMERIC_TYPES: ConditionType[] = [
  "target_health_pct",
  "player_health_pct",
  "time_elapsed",
];

const TYPE_LABELS: Record<ConditionType, string> = {
  target_health_pct: "Target HP %",
  player_health_pct: "Player HP %",
  time_elapsed:      "Time Elapsed (s)",
  buff_active:       "Buff Active",
  status_present:    "Status Present",
};

const OP_LABELS: Record<ComparisonOperator, string> = {
  lt: "< (less than)",
  le: "≤ (less or equal)",
  eq: "= (equal)",
  ge: "≥ (greater or equal)",
  gt: "> (greater than)",
};

const inputCls =
  "w-full rounded-sm border border-forge-border bg-forge-surface2 px-3 py-2 " +
  "font-body text-sm text-forge-text outline-none focus:border-forge-amber/60";
const labelCls =
  "block font-mono text-[11px] uppercase tracking-widest text-forge-dim mb-1";

export default function ConditionEditor({ value, onChange }: Props) {
  const uid = useId();
  const isNumeric = NUMERIC_TYPES.includes(value.condition_type);

  function set<K extends keyof ConditionDraft>(k: K, v: ConditionDraft[K]) {
    onChange({ ...value, [k]: v });
  }

  return (
    <div className="space-y-3 rounded border border-forge-border bg-forge-surface p-3">
      {/* Condition ID */}
      <div>
        <label htmlFor={uid + "-cid"} className={labelCls}>Condition ID</label>
        <input
          id={uid + "-cid"}
          className={inputCls}
          value={value.condition_id}
          onChange={e => set("condition_id", e.target.value)}
          placeholder="e.g. low_hp"
        />
      </div>

      {/* Type */}
      <div>
        <label htmlFor={uid + "-type"} className={labelCls}>Type</label>
        <select
          id={uid + "-type"}
          className={inputCls}
          value={value.condition_type}
          onChange={e => {
            const ct = e.target.value as ConditionType;
            const needsThreshold = NUMERIC_TYPES.includes(ct);
            onChange({
              ...value,
              condition_type:  ct,
              threshold_value: needsThreshold ? (value.threshold_value ?? 0.5) : null,
            });
          }}
        >
          {(Object.keys(TYPE_LABELS) as ConditionType[]).map(t => (
            <option key={t} value={t}>{TYPE_LABELS[t]}</option>
          ))}
        </select>
      </div>

      {/* Numeric controls */}
      {isNumeric && (
        <>
          <div>
            <label htmlFor={uid + "-op"} className={labelCls}>Comparison</label>
            <select
              id={uid + "-op"}
              className={inputCls}
              value={value.comparison_operator}
              onChange={e => set("comparison_operator", e.target.value as ComparisonOperator)}
            >
              {(Object.keys(OP_LABELS) as ComparisonOperator[]).map(op => (
                <option key={op} value={op}>{OP_LABELS[op]}</option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor={uid + "-thresh"} className={labelCls}>
              Threshold{value.condition_type !== "time_elapsed" ? " (0.0 – 1.0)" : " (seconds)"}
            </label>
            <input
              id={uid + "-thresh"}
              type="number"
              step={value.condition_type === "time_elapsed" ? "1" : "0.05"}
              min={0}
              max={value.condition_type === "time_elapsed" ? undefined : 1}
              className={inputCls}
              value={value.threshold_value ?? ""}
              onChange={e => set("threshold_value", Number(e.target.value))}
            />
          </div>
        </>
      )}

      {/* Duration (optional, for time-windowed conditions) */}
      <div>
        <label htmlFor={uid + "-dur"} className={labelCls}>
          Duration (s) <span className="normal-case text-forge-dim/60">optional</span>
        </label>
        <input
          id={uid + "-dur"}
          type="number"
          step="0.5"
          min={0}
          className={inputCls}
          value={value.duration ?? ""}
          placeholder="leave blank for permanent"
          onChange={e => {
            const v = e.target.value;
            set("duration", v === "" ? null : Number(v));
          }}
        />
      </div>
    </div>
  );
}
