/**
 * I15 — Target Config Panel
 *
 * Allows the user to add / remove / edit individual target specs
 * for the multi-target simulator when not using a template.
 */

import { Button } from "@/components/ui";

export interface TargetSpec {
  target_id:      string;
  max_health:     number;
  position_index: number;
}

interface Props {
  targets:  TargetSpec[];
  onChange: (targets: TargetSpec[]) => void;
}

const inputCls =
  "w-full rounded-sm border border-forge-border bg-forge-surface2 px-2 py-1.5 " +
  "font-body text-sm text-forge-text outline-none focus:border-forge-amber/60";
const labelCls =
  "block font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1";

function defaultTarget(idx: number): TargetSpec {
  return { target_id: `target_${idx + 1}`, max_health: 10000, position_index: idx };
}

export default function TargetConfigPanel({ targets, onChange }: Props) {
  function add() {
    onChange([...targets, defaultTarget(targets.length)]);
  }

  function remove(idx: number) {
    onChange(targets.filter((_, i) => i !== idx));
  }

  function update<K extends keyof TargetSpec>(idx: number, key: K, value: TargetSpec[K]) {
    onChange(targets.map((t, i) => i === idx ? { ...t, [key]: value } : t));
  }

  return (
    <div className="space-y-3">
      {targets.map((t, idx) => (
        <div
          key={idx}
          className="rounded border border-forge-border bg-forge-surface p-3 grid grid-cols-3 gap-3 items-end"
        >
          <div>
            <label className={labelCls}>Target ID</label>
            <input
              className={inputCls}
              value={t.target_id}
              onChange={e => update(idx, "target_id", e.target.value)}
            />
          </div>
          <div>
            <label className={labelCls}>Max Health</label>
            <input
              type="number"
              min={1}
              className={inputCls}
              value={t.max_health}
              onChange={e => update(idx, "max_health", Number(e.target.value))}
            />
          </div>
          <div className="flex gap-2 items-end">
            <div className="flex-1">
              <label className={labelCls}>Position</label>
              <input
                type="number"
                min={0}
                className={inputCls}
                value={t.position_index}
                onChange={e => update(idx, "position_index", Number(e.target.value))}
              />
            </div>
            <button
              type="button"
              onClick={() => remove(idx)}
              className="mb-px font-mono text-[10px] text-forge-dim hover:text-red-400 whitespace-nowrap"
            >
              × Remove
            </button>
          </div>
        </div>
      ))}

      {targets.length === 0 && (
        <p className="font-body text-sm text-forge-dim text-center py-3">
          No targets defined. Add at least one or choose a template.
        </p>
      )}

      <Button size="sm" variant="secondary" onClick={add}>
        + Add Target
      </Button>
    </div>
  );
}
