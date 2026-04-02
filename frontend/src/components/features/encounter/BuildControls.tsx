/**
 * D5 — Build Controls
 *
 * Captures build-specific parameters: base damage, crit chance, crit multiplier.
 */

import type { EncounterRequest } from "@/services/encounterApi";

type BuildFields = Pick<EncounterRequest, "base_damage" | "crit_chance" | "crit_multiplier">;

interface Props {
  values: BuildFields;
  onChange: (patch: Partial<BuildFields>) => void;
  disabled?: boolean;
}

function NumericInput({
  label,
  value,
  min,
  max,
  step,
  disabled,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  disabled?: boolean;
  onChange: (v: number) => void;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs text-forge-muted uppercase tracking-wide">{label}</label>
      <input
        type="number"
        min={min}
        max={max}
        step={step}
        value={value}
        disabled={disabled}
        onChange={(e) => {
          const v = parseFloat(e.target.value);
          if (!isNaN(v) && v >= min && v <= max) onChange(v);
        }}
        className="
          w-full rounded border border-forge-border bg-forge-input
          px-3 py-2 text-sm text-forge-text
          focus:border-forge-accent focus:outline-none
          disabled:opacity-50
        "
      />
    </div>
  );
}

export default function BuildControls({ values, onChange, disabled }: Props) {
  return (
    <section>
      <h3 className="mb-3 text-sm font-semibold text-forge-accent uppercase tracking-wider">
        Build Stats
      </h3>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <NumericInput
          label="Base Damage"
          value={values.base_damage}
          min={1}
          max={1_000_000}
          step={10}
          disabled={disabled}
          onChange={(v) => onChange({ base_damage: v })}
        />
        <NumericInput
          label="Crit Chance (0–1)"
          value={values.crit_chance}
          min={0}
          max={1}
          step={0.01}
          disabled={disabled}
          onChange={(v) => onChange({ crit_chance: v })}
        />
        <NumericInput
          label="Crit Multiplier"
          value={values.crit_multiplier}
          min={1}
          max={20}
          step={0.1}
          disabled={disabled}
          onChange={(v) => onChange({ crit_multiplier: v })}
        />
      </div>
    </section>
  );
}
