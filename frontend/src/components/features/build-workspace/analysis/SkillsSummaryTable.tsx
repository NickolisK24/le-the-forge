/**
 * SkillsSummaryTable — compact 5-row table of the build's skills.
 *
 * Columns (prompt §6):
 *   - Skill name
 *   - Classification badge: Damage / Utility / Minion
 *   - DPS (for damage skills) or the classification label
 *   - Points invested
 *
 * Clicking a row expands that row inline to show the primary-skill
 * breakdown for that skill. Only one row may be expanded at a time.
 *
 * Classification mirrors `backend/app/skills/skill_classifier.py` so the
 * badge lines up with the backend's primary-skill detection logic. When
 * `SkillDpsEntry` data is unavailable (stateless endpoint) the DPS cell
 * falls back to an em-dash.
 */

import { Fragment, useState } from "react";
import type { BuildSkill } from "@/types";
import type { DPSResult, SkillDpsEntry } from "@/lib/api";
import { statLabel } from "@/constants/statLabels";

import { fmtNumber, fmtPerSecond } from "./format";

// ---------------------------------------------------------------------------
// Classifier (mirror of backend skill_classifier.py)
// ---------------------------------------------------------------------------

export type SkillType = "damage" | "utility" | "minion";

const UTILITY_NAMES = new Set<string>([
  "Shift", "Lunge", "Teleport", "Evade", "Dive", "Fury Leap",
  "Shield Rush", "Transplant", "Volatile Reversal", "Flame Rush",
  "Rampage", "Reap",
  "Focus", "Dark Quiver", "Fire Shield", "Holy Aura", "Roar",
  "Symbols of Hope", "Thorn Shield", "Eterra's Blessing",
  "Warcry", "Rebuke", "Smoke Bomb", "Flame Ward",
  "Human Form", "Swarmblade Form", "Werebear Form", "Spriggan Form",
  "Reaper Form",
  "Mark for Death", "Mark For Death", "Ring of Shields", "Ring Of Shields",
  "Arcane Ascendance", "Decoy", "Detonate Decoy", "Create Shadow",
  "Banner Rush", "Ice Ward", "Frost Wall", "Glyph of Dominion",
  "Falconry", "Firebrand", "Static", "Rune Bolt",
  "Black Hole", "Ice Barrage", "Flame Reave",
]);

const MINION_NAMES = new Set<string>([
  "Summon Bear", "Summon Bone Golem", "Summon Raptor", "Summon Sabertooth",
  "Summon Skeletal Mage", "Summon Skeleton", "Summon Volatile Zombie",
  "Summon Wolf", "Summon Wraith", "Summon Scorpion", "Summon Spriggan",
  "Summon Cryomancer", "Summon Death Knight", "Summon Forged Weapon",
  "Summon Frenzy Totem", "Summon Healing Totem", "Summon Hive",
  "Summon Pyromancer", "Summon Skeleton Rogue", "Summon Squirrel",
  "Summon Storm Crows", "Summon Storm Totem", "Summon Thorn Totem",
  "Summon Vine", "Summon Vines",
  "Assemble Abomination", "Manifest Armor",
  "Thorn Totem", "Ballista",
  "Falcon Strikes", "Aerial Assault", "Dive Bomb",
]);

export function classifySkill(name: string, dpsEntry?: SkillDpsEntry): SkillType {
  if (MINION_NAMES.has(name)) return "minion";
  if (UTILITY_NAMES.has(name)) return "utility";
  if (dpsEntry && dpsEntry.total_dps <= 0) return "utility";
  return "damage";
}

// ---------------------------------------------------------------------------
// Badge styling
// ---------------------------------------------------------------------------

const TYPE_STYLES: Record<SkillType, string> = {
  damage:  "text-forge-amber border-forge-amber/50 bg-forge-amber/10",
  utility: "text-forge-cyan border-forge-cyan/50 bg-forge-cyan/10",
  minion:  "text-forge-purple border-forge-purple/50 bg-forge-purple/10",
};

const TYPE_LABELS: Record<SkillType, string> = {
  damage:  "Damage",
  utility: "Utility",
  minion:  "Minion",
};

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface SkillsSummaryTableProps {
  /** The build's skill loadout — reads from the workspace store. */
  skills: Array<
    Pick<BuildSkill, "slot" | "skill_name" | "points_allocated">
  >;
  /** Per-skill DPS entries from the engine, if available. */
  dpsPerSkill: SkillDpsEntry[];
  /** The primary skill's full DPS breakdown, used for the expanded row. */
  primaryDps: DPSResult | null;
  /** Auto-detected primary skill name from the analysis result. */
  primarySkillName: string;
}

// ---------------------------------------------------------------------------
// Internal row model
// ---------------------------------------------------------------------------

interface Row {
  slot: number;
  skill_name: string;
  type: SkillType;
  dpsEntry?: SkillDpsEntry;
  points_allocated: number;
  is_primary: boolean;
}

function buildRows(
  skills: SkillsSummaryTableProps["skills"],
  dpsPerSkill: SkillDpsEntry[],
  primarySkillName: string,
): Row[] {
  const byName = (name: string) => dpsPerSkill.find((d) => d.skill_name === name);
  const bySlot = (slot: number) => dpsPerSkill.find((d) => d.slot === slot);
  return skills.map((s) => {
    const entry = bySlot(s.slot) ?? byName(s.skill_name);
    return {
      slot: s.slot,
      skill_name: s.skill_name,
      type: classifySkill(s.skill_name, entry),
      dpsEntry: entry,
      points_allocated: s.points_allocated ?? 0,
      is_primary:
        (entry?.is_primary ?? false) ||
        (!!s.skill_name && s.skill_name === primarySkillName),
    };
  });
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function SkillsSummaryTable({
  skills,
  dpsPerSkill,
  primaryDps,
  primarySkillName,
}: SkillsSummaryTableProps) {
  const [openSlot, setOpenSlot] = useState<number | null>(null);

  if (skills.length === 0) {
    return (
      <section
        data-testid="skills-summary-table"
        className="rounded border border-forge-border bg-forge-surface overflow-hidden"
      >
        <header className="flex items-center justify-between border-b border-forge-border bg-forge-surface2 px-4 py-3">
          <span className="font-mono text-xs uppercase tracking-widest text-forge-cyan">
            All Skills
          </span>
        </header>
        <p className="p-4 font-body text-sm italic text-forge-dim text-center">
          No skills slotted — select one on the Skills tab to see analysis.
        </p>
      </section>
    );
  }

  const rows = buildRows(skills, dpsPerSkill, primarySkillName);

  return (
    <section
      data-testid="skills-summary-table"
      className="rounded border border-forge-border bg-forge-surface overflow-hidden min-w-0"
    >
      <header className="flex items-center justify-between border-b border-forge-border bg-forge-surface2 px-4 py-3">
        <span className="font-mono text-xs uppercase tracking-widest text-forge-cyan">
          All Skills
        </span>
      </header>
      {/* Mobile: allow horizontal scroll so the table never truncates. */}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[480px] text-left">
          <thead>
            <tr className="border-b border-forge-border">
              <th className="font-mono text-[10px] uppercase tracking-widest text-forge-dim px-4 py-2">
                Skill
              </th>
              <th className="font-mono text-[10px] uppercase tracking-widest text-forge-dim px-3 py-2">
                Role
              </th>
              <th className="font-mono text-[10px] uppercase tracking-widest text-forge-dim px-3 py-2">
                DPS / Role
              </th>
              <th className="font-mono text-[10px] uppercase tracking-widest text-forge-dim px-4 py-2 text-right">
                Points
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const isOpen = openSlot === row.slot;
              return (
                <Fragment key={row.slot}>
                  <tr
                    data-testid={`skills-row-${row.slot}`}
                    data-classification={row.type}
                    data-is-primary={row.is_primary}
                    onClick={() => setOpenSlot(isOpen ? null : row.slot)}
                    className={
                      "border-b border-forge-border/40 cursor-pointer transition-colors " +
                      (isOpen ? "bg-forge-surface2" : "hover:bg-forge-surface2/50")
                    }
                  >
                    <td className="px-4 py-2">
                      <div className="flex items-center gap-2 min-h-[44px] sm:min-h-0">
                        <span
                          aria-hidden="true"
                          className="font-mono text-[10px] text-forge-dim transition-transform"
                          style={{ transform: isOpen ? "rotate(90deg)" : "rotate(0deg)" }}
                        >
                          ▶
                        </span>
                        <span className="font-body text-sm text-forge-text truncate">
                          {row.skill_name || <span className="italic text-forge-dim">empty slot</span>}
                        </span>
                        {row.is_primary && (
                          <span
                            data-testid={`skills-row-${row.slot}-primary`}
                            className="font-mono text-[9px] uppercase tracking-widest px-2 py-0.5 rounded-sm border border-forge-amber/60 text-forge-amber"
                          >
                            Primary
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-3 py-2">
                      <span
                        data-testid={`skills-row-${row.slot}-badge`}
                        className={
                          "inline-block font-mono text-[10px] uppercase tracking-widest px-2 py-0.5 rounded-sm border " +
                          TYPE_STYLES[row.type]
                        }
                      >
                        {TYPE_LABELS[row.type]}
                      </span>
                    </td>
                    <td className="px-3 py-2">
                      {row.type === "damage" ? (
                        <span className="font-mono text-xs text-forge-text tabular-nums">
                          {row.dpsEntry ? fmtNumber(row.dpsEntry.total_dps) : "—"}
                        </span>
                      ) : row.type === "utility" ? (
                        <span className="font-body text-xs italic text-forge-cyan">
                          Utility
                        </span>
                      ) : (
                        <span className="font-body text-xs italic text-forge-purple">
                          Minion
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-2 text-right font-mono text-xs text-forge-muted tabular-nums">
                      {row.points_allocated}
                    </td>
                  </tr>
                  {isOpen && (
                    <tr
                      data-testid={`skills-row-${row.slot}-detail`}
                      className="border-b border-forge-border/40 bg-forge-surface2/40"
                    >
                      <td colSpan={4} className="px-4 py-3">
                        <ExpandedDetail row={row} primaryDps={primaryDps} primaryName={primarySkillName} />
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// Expanded-row detail. Reuses the four-stat grid from PrimarySkillBreakdown
// to keep the presentation consistent.
// ---------------------------------------------------------------------------

function ExpandedDetail({
  row,
  primaryDps,
  primaryName,
}: {
  row: Row;
  primaryDps: DPSResult | null;
  primaryName: string;
}) {
  const entry = row.dpsEntry;

  // If this row is the primary skill and we have the full DPSResult, use it
  // — it has the richer values (hit_damage, average_hit, attack speed, total)
  // than the per-skill SkillDpsEntry which only has dps / total_dps.
  const isPrimary = row.skill_name && row.skill_name === primaryName;
  const showFull = isPrimary && primaryDps;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <Cell label="Slot" value={`#${row.slot + 1}`} />
      <Cell
        label="Skill Level"
        value={entry?.skill_level ? String(entry.skill_level) : "—"}
      />
      {showFull ? (
        <>
          <Cell
            label={statLabel("effective_attack_speed")}
            value={fmtPerSecond(primaryDps!.effective_attack_speed)}
          />
          <Cell
            label={statLabel("total_dps")}
            value={fmtNumber(primaryDps!.total_dps ?? primaryDps!.dps ?? 0)}
          />
        </>
      ) : (
        <>
          <Cell
            label={statLabel("hit_dps")}
            value={entry ? fmtNumber(entry.dps) : "—"}
          />
          <Cell
            label={statLabel("total_dps")}
            value={entry ? fmtNumber(entry.total_dps) : "—"}
          />
        </>
      )}
      {row.type !== "damage" && (
        <p className="col-span-2 md:col-span-4 mt-1 font-body text-[11px] italic text-forge-dim">
          {row.type === "utility"
            ? "Utility skill — provides movement, buffs, or control."
            : "Minion skill — damage comes from summoned entities."}
        </p>
      )}
    </div>
  );
}

function Cell({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0">
      <div className="font-mono text-[9px] uppercase tracking-widest text-forge-dim">
        {label}
      </div>
      <div className="font-mono text-xs text-forge-text tabular-nums truncate">
        {value}
      </div>
    </div>
  );
}
