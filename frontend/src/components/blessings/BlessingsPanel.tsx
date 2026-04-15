/**
 * BlessingsPanel — Monolith of Fate blessing selector.
 *
 * Renders one row per timeline (10 total).  Each row lets the player pick a
 * blessing definition, choose Normal vs Grand, set a rolled value, or clear
 * the selection.  Emits the resulting `SelectedBlessing[]` via `onChange`.
 *
 * No <form> tags — all interactions use onClick / onChange handlers so the
 * component can be embedded inside any larger planner UI without the risk
 * of submit bubbling.
 */

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { clsx } from "clsx";

import { refApi } from "@/lib/api";
import type {
  BlessingDefinition,
  BlessingTimeline,
  SelectedBlessing,
} from "@/types/blessings";
import { Badge, Panel, SectionLabel, Spinner } from "@/components/ui";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function defaultValueFor(def: BlessingDefinition, isGrand: boolean): number {
  return Number(isGrand ? def.grand_max : def.normal_max) || 0;
}

function findDef(
  timeline: BlessingTimeline,
  blessingId: string,
): BlessingDefinition | undefined {
  return timeline.blessings.find((b) => b.id === blessingId);
}

// ---------------------------------------------------------------------------
// Row
// ---------------------------------------------------------------------------

interface RowProps {
  timeline: BlessingTimeline;
  selection: SelectedBlessing | undefined;
  onChange: (next: SelectedBlessing | null) => void;
  readOnly: boolean;
}

function BlessingRow({ timeline, selection, onChange, readOnly }: RowProps) {
  const selectedDef = selection ? findDef(timeline, selection.blessing_id) : undefined;
  const isGrand = selection?.is_grand ?? true;
  const value = selection?.value;

  const handlePick = (blessingId: string) => {
    if (!blessingId) {
      onChange(null);
      return;
    }
    const def = findDef(timeline, blessingId);
    if (!def) return;
    // Preserve the current Normal/Grand toggle if an option is already
    // selected, otherwise default to Grand (forge-amber).
    const nextGrand = selection?.is_grand ?? true;
    onChange({
      timeline_id: timeline.id,
      blessing_id: def.id,
      is_grand: nextGrand,
      value: defaultValueFor(def, nextGrand),
    });
  };

  const handleGrandToggle = (nextGrand: boolean) => {
    if (!selection || !selectedDef) return;
    onChange({
      ...selection,
      is_grand: nextGrand,
      value: defaultValueFor(selectedDef, nextGrand),
    });
  };

  const handleValueChange = (raw: string) => {
    if (!selection) return;
    const parsed = Number(raw);
    if (Number.isNaN(parsed)) return;
    onChange({ ...selection, value: parsed });
  };

  const handleClear = () => {
    onChange(null);
  };

  return (
    <div className="flex flex-col gap-2 py-3 border-b border-forge-border/60 last:border-b-0">
      {/* Header row — timeline + clear */}
      <div className="flex items-center justify-between gap-2 min-w-0">
        <div className="min-w-0">
          <span className="font-display text-sm text-forge-text truncate">
            {timeline.name}
          </span>
          <span className="ml-2 font-mono text-[10px] uppercase tracking-widest text-forge-dim">
            Lv {timeline.level}
          </span>
        </div>
        <button
          type="button"
          onClick={handleClear}
          disabled={readOnly || !selection}
          aria-label={`Clear blessing on ${timeline.name}`}
          className={clsx(
            "min-w-[44px] min-h-[44px] md:w-6 md:h-6 md:min-w-0 md:min-h-0 rounded-sm border border-forge-border bg-forge-surface2 shrink-0",
            "flex items-center justify-center text-forge-dim",
            "hover:text-forge-red hover:border-forge-red/60",
            "disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:text-forge-dim disabled:hover:border-forge-border",
            "transition-colors",
          )}
        >
          <span className="text-sm leading-none">×</span>
        </button>
      </div>

      {/* Blessing picker */}
      <select
        value={selection?.blessing_id ?? ""}
        disabled={readOnly}
        onChange={(e) => handlePick(e.target.value)}
        className={clsx(
          "w-full bg-forge-surface2 border border-forge-border rounded-sm",
          "px-2 py-1.5 text-sm text-forge-text font-body",
          "focus:outline-none focus:border-forge-cyan",
          "disabled:opacity-50 disabled:cursor-not-allowed",
        )}
      >
        <option value="">— No blessing —</option>
        {timeline.blessings.map((b) => (
          <option key={b.id} value={b.id}>
            {isGrand ? (b.grand_name || b.name) : b.name}
            {b.description ? ` — ${b.description}` : ""}
          </option>
        ))}
      </select>

      {/* Toggle + value — stacks vertically on mobile, side-by-side on md+ */}
      <div className="flex flex-col md:flex-row md:items-stretch gap-2 min-w-0">
        <div
          className={clsx(
            "flex rounded-sm border border-forge-border overflow-hidden bg-forge-surface2 flex-1",
            (!selection || readOnly) && "opacity-50",
          )}
        >
          <button
            type="button"
            disabled={readOnly || !selection}
            onClick={() => handleGrandToggle(false)}
            className={clsx(
              "flex-1 px-2 py-1 font-mono text-[11px] uppercase tracking-widest transition-colors min-h-[44px] md:min-h-0",
              !isGrand
                ? "bg-forge-cyan/15 text-forge-cyan"
                : "text-forge-dim hover:text-forge-text",
              "disabled:cursor-not-allowed",
            )}
          >
            Normal
          </button>
          <button
            type="button"
            disabled={readOnly || !selection}
            onClick={() => handleGrandToggle(true)}
            className={clsx(
              "flex-1 px-2 py-1 font-mono text-[11px] uppercase tracking-widest transition-colors min-h-[44px] md:min-h-0",
              isGrand
                ? "bg-forge-amber/20 text-forge-amber"
                : "text-forge-dim hover:text-forge-text",
              "disabled:cursor-not-allowed",
            )}
          >
            Grand
          </button>
        </div>
        <input
          type="number"
          inputMode="decimal"
          step="any"
          value={value ?? ""}
          disabled={readOnly || !selection}
          onChange={(e) => handleValueChange(e.target.value)}
          placeholder="—"
          className={clsx(
            "w-full md:w-24 bg-forge-surface2 border border-forge-border rounded-sm",
            "px-2 py-1 text-sm text-forge-text font-mono text-right min-h-[44px] md:min-h-0",
            "focus:outline-none focus:border-forge-cyan",
            "disabled:opacity-50 disabled:cursor-not-allowed",
          )}
        />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Panel
// ---------------------------------------------------------------------------

const TOTAL_TIMELINES = 10;

export interface BlessingsPanelProps {
  selectedBlessings: SelectedBlessing[];
  onChange: (next: SelectedBlessing[]) => void;
  readOnly?: boolean;
}

export function BlessingsPanel({
  selectedBlessings,
  onChange,
  readOnly = false,
}: BlessingsPanelProps) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["ref", "blessings"],
    queryFn: () => refApi.getBlessings(),
    staleTime: Infinity,
  });

  const timelines = useMemo<BlessingTimeline[]>(() => {
    const rows = data?.data ?? [];
    // Guarantee deterministic render order using `order` then `name`.
    return [...rows].sort(
      (a, b) => (a.order ?? 0) - (b.order ?? 0) || a.name.localeCompare(b.name),
    );
  }, [data]);

  const byTimeline = useMemo(() => {
    const m = new Map<string, SelectedBlessing>();
    for (const sel of selectedBlessings) m.set(sel.timeline_id, sel);
    return m;
  }, [selectedBlessings]);

  const filledCount = useMemo(
    () => selectedBlessings.filter((s) => !!s.blessing_id).length,
    [selectedBlessings],
  );

  const updateRow = (timelineId: string, next: SelectedBlessing | null) => {
    const without = selectedBlessings.filter((s) => s.timeline_id !== timelineId);
    onChange(next ? [...without, next] : without);
  };

  const header = (
    <Badge variant={filledCount > 0 ? "tier-a" : "default"}>
      Monolith Blessings {filledCount} / {TOTAL_TIMELINES}
    </Badge>
  );

  return (
    <Panel title="Monolith Blessings" action={header}>
      {isLoading && (
        <div className="flex items-center justify-center py-10">
          <Spinner />
        </div>
      )}

      {isError && (
        <div className="py-6 text-center">
          <p className="font-body text-sm text-forge-red">
            Failed to load blessings registry.
          </p>
        </div>
      )}

      {!isLoading && !isError && timelines.length === 0 && (
        <div className="py-6 text-center">
          <p className="font-body text-sm text-forge-muted">
            No blessing timelines available.
          </p>
        </div>
      )}

      {!isLoading && !isError && timelines.length > 0 && (
        <>
          <SectionLabel>
            Pick one blessing per timeline — Grand upgrades grant the maximum
            magnitude.
          </SectionLabel>
          <div className="flex flex-col">
            {timelines.map((t) => (
              <BlessingRow
                key={t.id}
                timeline={t}
                selection={byTimeline.get(t.id)}
                onChange={(next) => updateRow(t.id, next)}
                readOnly={readOnly}
              />
            ))}
          </div>
        </>
      )}
    </Panel>
  );
}

export default BlessingsPanel;
