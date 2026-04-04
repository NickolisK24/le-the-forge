/**
 * PassiveTreeControls — class/mastery selectors, point counters, and reset.
 *
 * Renders above the PassiveTreeRenderer and drives the tree data fetch
 * by surfacing the selected class and mastery back to the parent page.
 */

import { Button } from "@/components/ui";
import { MASTERIES } from "@/lib/gameData";
import { BASE_CLASSES } from "@constants";
import type { CharacterClass } from "@/types";

const CLASSES: CharacterClass[] = [...BASE_CLASSES] as CharacterClass[];

// Cap for base-class passive section (game rule: ~20 base points available)
const BASE_POINT_CAP = 20;

interface Props {
  selectedClass: CharacterClass | null;
  selectedMastery: string;
  onClassChange: (cls: CharacterClass | null) => void;
  onMasteryChange: (mastery: string) => void;
  basePointsSpent: number;
  masteryPointsSpent: number;
  onReset: () => void;
}

export default function PassiveTreeControls({
  selectedClass,
  selectedMastery,
  onClassChange,
  onMasteryChange,
  basePointsSpent,
  masteryPointsSpent,
  onReset,
}: Props) {
  const masteries = selectedClass ? (MASTERIES[selectedClass] ?? []) : [];
  const hasAllocations = basePointsSpent > 0 || masteryPointsSpent > 0;

  return (
    <div className="flex flex-wrap items-end gap-4 rounded border border-forge-border bg-forge-surface p-3">
      {/* Class selector */}
      <div className="flex flex-col gap-1">
        <label className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
          Class
        </label>
        <select
          value={selectedClass ?? ""}
          onChange={(e) => {
            const val = e.target.value as CharacterClass | "";
            onClassChange(val || null);
            onMasteryChange("__base__");
          }}
          className="min-w-[148px] rounded-sm border border-forge-border bg-forge-surface2 px-3 py-1.5 font-body text-sm text-forge-text outline-none focus:border-forge-cyan/50"
        >
          <option value="">Select class…</option>
          {CLASSES.map((cls) => (
            <option key={cls} value={cls}>
              {cls}
            </option>
          ))}
        </select>
      </div>

      {/* Mastery selector — only when a class is chosen */}
      {selectedClass && (
        <div className="flex flex-col gap-1">
          <label className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
            Mastery
          </label>
          <select
            value={selectedMastery}
            onChange={(e) => onMasteryChange(e.target.value)}
            className="min-w-[164px] rounded-sm border border-forge-border bg-forge-surface2 px-3 py-1.5 font-body text-sm text-forge-text outline-none focus:border-forge-cyan/50"
          >
            <option value="__base__">Base class</option>
            {masteries.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Spacer */}
      <div className="flex-1" />

      {/* Points counters */}
      {selectedClass && (
        <div className="flex items-center gap-5 font-mono text-xs">
          <div className="flex flex-col items-center gap-0.5">
            <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
              Base pts
            </span>
            <span
              className={
                basePointsSpent > 0 ? "font-bold text-forge-amber" : "text-forge-dim"
              }
            >
              {basePointsSpent}
              <span className="text-forge-dim"> / {BASE_POINT_CAP}</span>
            </span>
          </div>

          {selectedMastery && selectedMastery !== "__base__" && (
            <div className="flex flex-col items-center gap-0.5">
              <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
                Mastery pts
              </span>
              <span
                className={
                  masteryPointsSpent > 0
                    ? "font-bold text-forge-cyan"
                    : "text-forge-dim"
                }
              >
                {masteryPointsSpent}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Reset */}
      <Button
        variant="outline"
        size="sm"
        onClick={onReset}
        disabled={!hasAllocations}
      >
        Reset
      </Button>
    </div>
  );
}
