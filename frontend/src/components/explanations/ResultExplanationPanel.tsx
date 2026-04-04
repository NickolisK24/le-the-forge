/**
 * UI+4 — Result Explanation Panel
 * Show stat contributions and percent breakdown from gear, skills, and passives.
 */

import React from "react";
import { ComputedStats, StatSource } from "../../hooks/useLiveStats";

export interface StatContribution {
  source: string;
  sourceType: "gear" | "skill" | "passive" | "base";
  stat: string;
  value: number;
  percentage: number;
}

export interface ExplanationData {
  stat: string;
  displayName: string;
  total: number;
  contributions: StatContribution[];
}

interface ResultExplanationPanelProps {
  stats: ComputedStats;
  source: StatSource;
  /** Which stats to show explanations for. Defaults to main stats. */
  visibleStats?: string[];
  className?: string;
}

const STAT_LABELS: Record<string, string> = {
  totalDps:              "Total DPS",
  effectiveCritChance:   "Crit Chance",
  effectiveCritMultiplier: "Crit Multiplier",
  totalArmor:            "Armor",
  manaPool:              "Mana Pool",
  castSpeed:             "Cast Speed",
  movementSpeed:         "Movement Speed",
};

const DEFAULT_VISIBLE = Object.keys(STAT_LABELS);

function formatValue(stat: string, value: number): string {
  if (stat === "effectiveCritChance") return `${(value * 100).toFixed(1)}%`;
  if (stat === "effectiveCritMultiplier") return `${value.toFixed(2)}x`;
  if (stat === "castSpeed" || stat === "movementSpeed") return `${value.toFixed(2)}x`;
  return String(Math.round(value));
}

function buildExplanations(
  stats: ComputedStats,
  source: StatSource,
  visibleStats: string[]
): ExplanationData[] {
  return visibleStats
    .filter((s) => s in STAT_LABELS)
    .map((stat) => {
      const total = stats[stat as keyof ComputedStats] as number;
      const contributions: StatContribution[] = [];

      // Base contribution
      const baseValues: Record<string, number> = {
        totalDps: 100,
        effectiveCritChance: 0.05,
        effectiveCritMultiplier: 1.5,
        totalArmor: 0,
        manaPool: 200,
        castSpeed: 1.0,
        movementSpeed: 1.0,
      };
      const base = baseValues[stat] ?? 0;
      if (base !== 0) {
        contributions.push({
          source: "Base",
          sourceType: "base",
          stat,
          value: base,
          percentage: total > 0 ? Math.round((base / total) * 100) : 0,
        });
      }

      // Skill contributions
      if (source.skills.length > 0 && stat === "totalDps") {
        const val = source.skills.length * 10;
        contributions.push({
          source: `Skills (×${source.skills.length})`,
          sourceType: "skill",
          stat,
          value: val,
          percentage: total > 0 ? Math.round((val / total) * 100) : 0,
        });
      }

      // Passive contributions
      if (source.passives.length > 0 && stat === "totalDps") {
        const val = source.passives.reduce((s, id) => s + (id % 10), 0);
        if (val > 0) {
          contributions.push({
            source: `Passives (×${source.passives.length})`,
            sourceType: "passive",
            stat,
            value: val,
            percentage: total > 0 ? Math.round((val / total) * 100) : 0,
          });
        }
      }

      // Gear contributions from raw stats
      const rawMap: Record<string, string> = {
        totalDps: "damage",
        totalArmor: "armor",
        manaPool: "mana",
      };
      const rawKey = rawMap[stat];
      if (rawKey && stats.raw[rawKey]) {
        const val = stats.raw[rawKey];
        contributions.push({
          source: "Gear",
          sourceType: "gear",
          stat,
          value: val,
          percentage: total > 0 ? Math.round((val / total) * 100) : 0,
        });
      }

      return {
        stat,
        displayName: STAT_LABELS[stat] ?? stat,
        total,
        contributions,
      };
    });
}

const SOURCE_COLORS: Record<string, string> = {
  base:    "text-gray-400",
  gear:    "text-amber-400",
  skill:   "text-cyan-400",
  passive: "text-purple-400",
};

export function ResultExplanationPanel({
  stats,
  source,
  visibleStats = DEFAULT_VISIBLE,
  className = "",
}: ResultExplanationPanelProps): React.JSX.Element {
  const explanations = buildExplanations(stats, source, visibleStats);

  return (
    <div
      className={`rounded-lg bg-[#0d1117] border border-[#2d3748] p-4 space-y-4 ${className}`}
      role="region"
      aria-label="Stat Breakdown"
    >
      <h3 className="text-sm font-semibold text-[#f0a020] uppercase tracking-wider">
        Stat Breakdown
      </h3>

      {explanations.map((exp) => (
        <div key={exp.stat} className="space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400">{exp.displayName}</span>
            <span className="text-sm font-mono font-semibold text-white">
              {formatValue(exp.stat, exp.total)}
            </span>
          </div>

          {exp.contributions.length > 0 && (
            <div className="space-y-0.5 pl-2 border-l border-[#2d3748]">
              {exp.contributions.map((c, i) => (
                <div key={i} className="flex items-center justify-between text-xs">
                  <span className={SOURCE_COLORS[c.sourceType] ?? "text-gray-500"}>
                    {c.source}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400 font-mono">
                      {formatValue(exp.stat, c.value)}
                    </span>
                    <span className="text-gray-600 w-10 text-right">{c.percentage}%</span>
                  </div>
                </div>
              ))}

              {/* Contribution bar */}
              <div className="flex gap-0.5 h-1 mt-1 rounded overflow-hidden">
                {exp.contributions.map((c, i) => (
                  <div
                    key={i}
                    style={{ width: `${c.percentage}%` }}
                    className={`h-full ${
                      c.sourceType === "gear" ? "bg-amber-500" :
                      c.sourceType === "skill" ? "bg-cyan-500" :
                      c.sourceType === "passive" ? "bg-purple-500" :
                      "bg-gray-600"
                    }`}
                    title={`${c.source}: ${c.percentage}%`}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
