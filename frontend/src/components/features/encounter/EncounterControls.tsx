/**
 * D6 — Encounter Controls
 *
 * Captures encounter-specific parameters: template, fight duration, distribution.
 */

import type { EncounterRequest, EnemyTemplate, HitDistribution } from "@/services/encounterApi";
import { TEMPLATE_LABELS, DISTRIBUTION_LABELS } from "@/services/encounterApi";

type EncounterFields = Pick<
  EncounterRequest,
  "enemy_template" | "fight_duration" | "tick_size" | "distribution"
>;

interface Props {
  values: EncounterFields;
  onChange: (patch: Partial<EncounterFields>) => void;
  disabled?: boolean;
}

const TEMPLATES = Object.keys(TEMPLATE_LABELS) as EnemyTemplate[];
const DISTRIBUTIONS = Object.keys(DISTRIBUTION_LABELS) as HitDistribution[];

export default function EncounterControls({ values, onChange, disabled }: Props) {
  return (
    <section>
      <h3 className="mb-3 text-sm font-semibold text-forge-accent uppercase tracking-wider">
        Encounter Setup
      </h3>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Template */}
        <div className="flex flex-col gap-1">
          <label className="text-xs text-forge-muted uppercase tracking-wide">Template</label>
          <select
            value={values.enemy_template}
            disabled={disabled}
            onChange={(e) => onChange({ enemy_template: e.target.value as EnemyTemplate })}
            className="
              w-full rounded border border-forge-border bg-forge-input
              px-3 py-2 text-sm text-forge-text
              focus:border-forge-accent focus:outline-none
              disabled:opacity-50
            "
          >
            {TEMPLATES.map((t) => (
              <option key={t} value={t}>
                {TEMPLATE_LABELS[t]}
              </option>
            ))}
          </select>
        </div>

        {/* Distribution */}
        <div className="flex flex-col gap-1">
          <label className="text-xs text-forge-muted uppercase tracking-wide">Distribution</label>
          <select
            value={values.distribution}
            disabled={disabled}
            onChange={(e) => onChange({ distribution: e.target.value as HitDistribution })}
            className="
              w-full rounded border border-forge-border bg-forge-input
              px-3 py-2 text-sm text-forge-text
              focus:border-forge-accent focus:outline-none
              disabled:opacity-50
            "
          >
            {DISTRIBUTIONS.map((d) => (
              <option key={d} value={d}>
                {DISTRIBUTION_LABELS[d]}
              </option>
            ))}
          </select>
        </div>

        {/* Fight Duration */}
        <div className="flex flex-col gap-1">
          <label className="text-xs text-forge-muted uppercase tracking-wide">
            Fight Duration (s)
          </label>
          <input
            type="number"
            min={1}
            max={3600}
            step={1}
            value={values.fight_duration}
            disabled={disabled}
            onChange={(e) => {
              const v = parseFloat(e.target.value);
              if (!isNaN(v) && v >= 1 && v <= 3600) onChange({ fight_duration: v });
            }}
            className="
              w-full rounded border border-forge-border bg-forge-input
              px-3 py-2 text-sm text-forge-text
              focus:border-forge-accent focus:outline-none
              disabled:opacity-50
            "
          />
        </div>

        {/* Tick Size */}
        <div className="flex flex-col gap-1">
          <label className="text-xs text-forge-muted uppercase tracking-wide">
            Tick Size (s)
          </label>
          <input
            type="number"
            min={0.01}
            max={10}
            step={0.01}
            value={values.tick_size}
            disabled={disabled}
            onChange={(e) => {
              const v = parseFloat(e.target.value);
              if (!isNaN(v) && v >= 0.01 && v <= 10) onChange({ tick_size: v });
            }}
            className="
              w-full rounded border border-forge-border bg-forge-input
              px-3 py-2 text-sm text-forge-text
              focus:border-forge-accent focus:outline-none
              disabled:opacity-50
            "
          />
        </div>
      </div>
    </section>
  );
}
