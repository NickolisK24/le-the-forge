/**
 * AllSkillsSummary — compact table of every slotted skill with its role
 * and DPS contribution. Clicking a row expands it to show extra detail.
 *
 * Skill type classification runs on the client against a small hardcoded
 * set (matches backend/app/skills/skill_classifier.py). DPS entries with
 * zero total_dps automatically classify as Utility if not in any explicit
 * list.
 */

import { Fragment, useState } from "react";
import { clsx } from "clsx";
import { Panel, Badge } from "@/components/ui";
import type { SkillDpsEntry } from "@/lib/api";
import { statLabel } from "@/constants/statLabels";

// ---------------------------------------------------------------------------
// Client-side classifier (mirror of backend skill_classifier.py)
// ---------------------------------------------------------------------------

type SkillType = "damage" | "utility" | "minion";

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

function classifySkill(name: string, dpsEntry?: SkillDpsEntry): SkillType {
  if (MINION_NAMES.has(name)) return "minion";
  if (UTILITY_NAMES.has(name)) return "utility";
  // Fallback: zero DPS entries with no classification default to utility.
  if (dpsEntry && dpsEntry.total_dps <= 0) return "utility";
  return "damage";
}

// ---------------------------------------------------------------------------
// Formatting
// ---------------------------------------------------------------------------

function fmt(n: number): string {
  if (!Number.isFinite(n)) return "—";
  if (Math.abs(n) >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (Math.abs(n) >= 1_000)     return `${(n / 1_000).toFixed(1)}K`;
  return String(Math.round(n));
}

const TYPE_COLORS: Record<SkillType, string> = {
  damage:  "text-forge-amber border-forge-amber/40 bg-forge-amber/8",
  utility: "text-forge-cyan border-forge-cyan/40 bg-forge-cyan/8",
  minion:  "text-forge-purple border-forge-purple/40 bg-forge-purple/8",
};

// ---------------------------------------------------------------------------
// Row
// ---------------------------------------------------------------------------

interface SkillRow {
  slot: number;
  skill_name: string;
  skill_level: number;
  type: SkillType;
  dpsEntry?: SkillDpsEntry;
  points_allocated?: number;
  is_primary?: boolean;
}

function DpsCell({ row }: { row: SkillRow }) {
  if (row.type === "utility") {
    return <span className="font-body text-xs italic text-forge-cyan">Utility</span>;
  }
  if (row.type === "minion") {
    return <span className="font-body text-xs italic text-forge-purple">Minion</span>;
  }
  if (!row.dpsEntry) {
    return <span className="font-mono text-xs text-forge-dim">—</span>;
  }
  return (
    <span className="font-mono text-xs text-forge-text tabular-nums">
      {fmt(row.dpsEntry.total_dps)}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Root
// ---------------------------------------------------------------------------

interface AllSkillsSummaryProps {
  skills: Array<{
    slot: number;
    skill_name: string;
    points_allocated: number;
  }>;
  dpsPerSkill: SkillDpsEntry[];
}

export default function AllSkillsSummary({
  skills, dpsPerSkill,
}: AllSkillsSummaryProps) {
  const [openSlot, setOpenSlot] = useState<number | null>(null);

  if (skills.length === 0) {
    return (
      <Panel title="All Skills">
        <p className="font-body text-sm text-forge-dim italic text-center py-6">
          No skills slotted.
        </p>
      </Panel>
    );
  }

  const rows: SkillRow[] = skills.map((s) => {
    const dpsEntry = dpsPerSkill.find((d) => d.slot === s.slot);
    return {
      slot: s.slot,
      skill_name: s.skill_name,
      skill_level: dpsEntry?.skill_level ?? 0,
      type: classifySkill(s.skill_name, dpsEntry),
      dpsEntry,
      points_allocated: s.points_allocated,
      is_primary: dpsEntry?.is_primary ?? false,
    };
  });

  return (
    <Panel title="All Skills">
      <div className="overflow-x-auto -mx-4 px-4">
        <table className="w-full min-w-[480px] text-left">
          <thead>
            <tr className="border-b border-forge-border">
              <th className="font-mono text-[10px] uppercase tracking-widest text-forge-dim py-2 pr-3">
                Skill
              </th>
              <th className="font-mono text-[10px] uppercase tracking-widest text-forge-dim py-2 pr-3">
                Type
              </th>
              <th className="font-mono text-[10px] uppercase tracking-widest text-forge-dim py-2 pr-3">
                DPS / Role
              </th>
              <th className="font-mono text-[10px] uppercase tracking-widest text-forge-dim py-2 text-right">
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
                    onClick={() => setOpenSlot(isOpen ? null : row.slot)}
                    className={clsx(
                      "border-b border-forge-border/40 cursor-pointer transition-colors",
                      isOpen
                        ? "bg-forge-surface2"
                        : "hover:bg-forge-surface2/50",
                    )}
                  >
                    <td className="py-2 pr-3">
                      <div className="flex items-center gap-2">
                        <span
                          aria-hidden="true"
                          className="font-mono text-[10px] text-forge-dim transition-transform"
                          style={{ transform: isOpen ? "rotate(90deg)" : "rotate(0deg)" }}
                        >
                          ▶
                        </span>
                        <span className="font-body text-sm text-forge-text">
                          {row.skill_name}
                        </span>
                        {row.is_primary && <Badge variant="tier-a">Primary</Badge>}
                      </div>
                    </td>
                    <td className="py-2 pr-3">
                      <span
                        className={clsx(
                          "inline-block font-mono text-[10px] uppercase tracking-widest px-2 py-0.5 rounded-sm border",
                          TYPE_COLORS[row.type],
                        )}
                      >
                        {row.type}
                      </span>
                    </td>
                    <td className="py-2 pr-3">
                      <DpsCell row={row} />
                    </td>
                    <td className="py-2 text-right font-mono text-xs text-forge-muted tabular-nums">
                      {row.points_allocated ?? 0}
                    </td>
                  </tr>
                  {isOpen && (
                    <tr className="border-b border-forge-border/40 bg-forge-surface2/30">
                      <td colSpan={4} className="px-4 py-3">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                          <DetailCell label="Slot" value={`#${row.slot + 1}`} />
                          <DetailCell
                            label="Skill Level"
                            value={row.skill_level > 0 ? String(row.skill_level) : "—"}
                          />
                          <DetailCell
                            label={statLabel("hit_dps")}
                            value={row.dpsEntry ? fmt(row.dpsEntry.dps) : "—"}
                          />
                          <DetailCell
                            label={statLabel("total_dps")}
                            value={row.dpsEntry ? fmt(row.dpsEntry.total_dps) : "—"}
                          />
                        </div>
                        {row.type !== "damage" && (
                          <p className="mt-2 font-body text-[11px] text-forge-dim italic">
                            {row.type === "utility"
                              ? "Utility skill — provides movement, buffs, or control."
                              : "Minion skill — damage comes from summoned entities."}
                          </p>
                        )}
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}

function DetailCell({ label, value }: { label: string; value: string }) {
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
