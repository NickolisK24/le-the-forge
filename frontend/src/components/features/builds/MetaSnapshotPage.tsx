/**
 * MetaSnapshotPage — full meta analytics page for The Forge community builds.
 *
 * Displays:
 *   1. Summary strip — total builds, most played class, top mastery
 *   2. Class distribution bar chart (clicking filters mastery below)
 *   3. Mastery breakdown bar chart
 *   4. Popular skills — horizontal bar chart
 *   5. Popular affixes — horizontal bar chart
 *   6. Trending builds — card grid
 *   7. Last updated footer
 */

import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { metaApi } from "@/lib/api";
import { Panel, Spinner, ErrorMessage } from "@/components/ui";
import { CLASS_COLORS } from "@/lib/gameData";
import type { FullMetaSnapshot, TrendingBuild, ClassDistEntry, MasteryDistEntry } from "@/types";

const C = {
  amber: "#f0a020",
  cyan: "#22d3ee",
  green: "#4ade80",
  dim: "#5a6080",
};

const TIER_COLORS: Record<string, string> = {
  S: "#f5d060",
  A: "#3dca74",
  B: "#f0a020",
  C: "#8890b8",
};

// ---------------------------------------------------------------------------
// Class Distribution
// ---------------------------------------------------------------------------

function ClassDistributionPanel({
  distribution,
  selectedClass,
  onSelect,
}: {
  distribution: ClassDistEntry[];
  selectedClass: string | null;
  onSelect: (cls: string | null) => void;
}) {
  const total = distribution.reduce((sum, d) => sum + d.count, 0) || 1;

  return (
    <Panel title="Class Distribution">
      <div className="space-y-3">
        {distribution.map((d) => {
          const pct = Math.round((d.count / total) * 100);
          const color = CLASS_COLORS[d.class as keyof typeof CLASS_COLORS] ?? "#8890b8";
          const isSelected = selectedClass === d.class;
          return (
            <button
              key={d.class}
              onClick={() => onSelect(isSelected ? null : d.class)}
              className="w-full text-left bg-transparent border-none cursor-pointer p-0"
              style={{ opacity: selectedClass && !isSelected ? 0.5 : 1, transition: "opacity 0.2s" }}
            >
              <div className="flex justify-between font-mono text-xs mb-1">
                <span style={{ color }}>{d.class}</span>
                <span className="text-forge-muted">
                  {d.count} <span className="text-forge-dim">({pct}%)</span>
                </span>
              </div>
              <div className="h-2 rounded-full bg-forge-surface3 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{ width: `${pct}%`, backgroundColor: color }}
                />
              </div>
            </button>
          );
        })}
        {distribution.length === 0 && (
          <p className="font-mono text-[10px] text-forge-dim italic text-center py-4">
            No public builds yet
          </p>
        )}
      </div>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Mastery Breakdown
// ---------------------------------------------------------------------------

function MasteryBreakdownPanel({
  masteries,
  className: cls,
}: {
  masteries: MasteryDistEntry[];
  className: string;
}) {
  const max = Math.max(...masteries.map((m) => m.count), 1);
  const color = CLASS_COLORS[cls as keyof typeof CLASS_COLORS] ?? "#8890b8";

  return (
    <Panel title={`${cls} Masteries`}>
      <div className="space-y-3">
        {masteries.map((m) => {
          const pct = Math.round((m.count / max) * 100);
          return (
            <div key={m.mastery}>
              <div className="flex justify-between font-mono text-xs mb-1">
                <span className="text-forge-text">{m.mastery}</span>
                <span className="text-forge-muted">{m.count} ({m.percentage}%)</span>
              </div>
              <div className="h-2 rounded-full bg-forge-surface3 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${pct}%`, backgroundColor: color, opacity: 0.8 }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Popular Skills
// ---------------------------------------------------------------------------

function PopularSkillsPanel({ skills }: { skills: Array<{ skill_name: string; usage_count: number }> }) {
  const max = Math.max(...skills.map((s) => s.usage_count), 1);

  return (
    <Panel title="Popular Skills">
      {skills.length === 0 ? (
        <p className="font-mono text-[10px] text-forge-dim italic text-center py-4">No data</p>
      ) : (
        <div className="space-y-2">
          {skills.map((s, i) => (
            <div key={s.skill_name} className="flex items-center gap-3">
              <span className="font-mono text-xs text-forge-dim w-4 text-right shrink-0">{i + 1}</span>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between font-mono text-xs mb-0.5">
                  <span className="text-forge-text truncate">{s.skill_name}</span>
                  <span className="text-forge-muted shrink-0 ml-2">{s.usage_count}</span>
                </div>
                <div className="h-1.5 rounded-full bg-forge-surface3 overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${(s.usage_count / max) * 100}%`,
                      backgroundColor: C.amber,
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Popular Affixes
// ---------------------------------------------------------------------------

function PopularAffixesPanel({ affixes }: { affixes: Array<{ affix_name: string; usage_count: number }> }) {
  const max = Math.max(...affixes.map((a) => a.usage_count), 1);

  return (
    <Panel title="Popular Affixes">
      {affixes.length === 0 ? (
        <p className="font-mono text-[10px] text-forge-dim italic text-center py-4">No data</p>
      ) : (
        <div className="space-y-2">
          {affixes.map((a, i) => (
            <div key={a.affix_name} className="flex items-center gap-3">
              <span className="font-mono text-xs text-forge-dim w-4 text-right shrink-0">{i + 1}</span>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between font-mono text-xs mb-0.5">
                  <span className="text-forge-text truncate">{a.affix_name}</span>
                  <span className="text-forge-muted shrink-0 ml-2">{a.usage_count}</span>
                </div>
                <div className="h-1.5 rounded-full bg-forge-surface3 overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${(a.usage_count / max) * 100}%`,
                      backgroundColor: C.cyan,
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Trending Builds
// ---------------------------------------------------------------------------

function TrendingBuildsSection({ builds }: { builds: TrendingBuild[] }) {
  if (builds.length === 0) {
    return (
      <Panel title="Trending Builds">
        <p className="font-mono text-[10px] text-forge-dim italic text-center py-4">
          No trending builds yet (minimum 10 views required)
        </p>
      </Panel>
    );
  }

  return (
    <div>
      <div className="font-display text-lg font-bold text-forge-amber tracking-wider mb-3">
        Trending Builds
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {builds.map((b) => {
          const classColor = CLASS_COLORS[b.character_class as keyof typeof CLASS_COLORS] ?? "#8890b8";
          const tierColor = TIER_COLORS[b.tier ?? "C"] ?? "#8890b8";
          return (
            <Link
              key={b.id}
              to={`/build/${b.slug}`}
              className="rounded border border-forge-border bg-forge-surface p-4 no-underline group hover:border-forge-amber/30 transition-colors"
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="font-body text-sm font-medium text-forge-text group-hover:text-forge-amber transition-colors line-clamp-1">
                  {b.name}
                </div>
                {b.tier && (
                  <span
                    className="font-display text-sm font-bold shrink-0"
                    style={{ color: tierColor }}
                  >
                    {b.tier}
                  </span>
                )}
              </div>
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <span
                  className="font-mono text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded-sm border"
                  style={{ color: classColor, borderColor: `${classColor}40`, background: `${classColor}08` }}
                >
                  {b.mastery}
                </span>
              </div>
              <div className="flex items-center justify-between font-mono text-[10px] text-forge-dim">
                <span>{b.author ?? "Anonymous"}</span>
                <div className="flex items-center gap-3">
                  <span>{b.view_count} views</span>
                  <span style={{ color: C.green }}>{b.trending_score.toFixed(1)}/d</span>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Summary strip
// ---------------------------------------------------------------------------

function SummaryStrip({ data }: { data: FullMetaSnapshot }) {
  const total = data.class_distribution.reduce((sum, d) => sum + d.count, 0);
  const mostPlayed = data.class_distribution[0]?.class ?? "N/A";
  // Find most popular mastery across all classes
  let topMastery = "N/A";
  let topMasteryCount = 0;
  for (const entries of Object.values(data.mastery_distribution)) {
    for (const m of entries) {
      if (m.count > topMasteryCount) {
        topMasteryCount = m.count;
        topMastery = m.mastery;
      }
    }
  }

  return (
    <div className="grid grid-cols-3 gap-4 rounded border border-forge-border bg-forge-surface2 px-6 py-4">
      <div className="text-center">
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-muted mb-1">
          Total Builds
        </div>
        <div className="font-display text-3xl font-bold text-forge-amber">
          {total.toLocaleString()}
        </div>
      </div>
      <div className="text-center">
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-muted mb-1">
          Most Played Class
        </div>
        <div
          className="font-display text-2xl font-bold"
          style={{
            color: CLASS_COLORS[mostPlayed as keyof typeof CLASS_COLORS] ?? C.amber,
          }}
        >
          {mostPlayed}
        </div>
      </div>
      <div className="text-center">
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-muted mb-1">
          Top Mastery
        </div>
        <div className="font-display text-2xl font-bold text-forge-cyan">
          {topMastery}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page root
// ---------------------------------------------------------------------------

export default function MetaSnapshotPage() {
  const [selectedClass, setSelectedClass] = useState<string | null>(null);

  const { data: snapshotRes, isLoading: snapshotLoading, isError: snapshotError } = useQuery({
    queryKey: ["meta", "snapshot"],
    queryFn: () => metaApi.snapshot(),
    staleTime: 2 * 60 * 1000,
    retry: 1,
  });

  const { data: trendingRes, isLoading: trendingLoading, isError: trendingError } = useQuery({
    queryKey: ["meta", "trending"],
    queryFn: () => metaApi.trending(),
    staleTime: 2 * 60 * 1000,
    retry: 1,
  });

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 space-y-6">
      {/* Page header */}
      <div>
        <h1 className="font-display text-2xl font-bold text-forge-amber tracking-wide">
          Meta Snapshot
        </h1>
        <p className="font-body text-sm text-forge-muted mt-1">
          Live aggregate stats from all public community builds. Data refreshes every 6 hours.
        </p>
      </div>

      {/* Snapshot sections */}
      {snapshotLoading && (
        <div className="flex items-center justify-center py-32">
          <Spinner size={32} />
        </div>
      )}

      {snapshotError && (
        <div className="mx-auto max-w-2xl py-16">
          <ErrorMessage message="Failed to load meta snapshot. Please try again." />
        </div>
      )}

      {snapshotRes?.data && (
        <>
          {/* Summary numbers */}
          <SummaryStrip data={snapshotRes.data} />

          {/* Class distribution + mastery breakdown side by side */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ClassDistributionPanel
              distribution={snapshotRes.data.class_distribution}
              selectedClass={selectedClass}
              onSelect={setSelectedClass}
            />
            {selectedClass && snapshotRes.data.mastery_distribution[selectedClass] ? (
              <MasteryBreakdownPanel
                masteries={snapshotRes.data.mastery_distribution[selectedClass]}
                className={selectedClass}
              />
            ) : (
              <Panel title="Mastery Breakdown">
                <p className="font-mono text-[10px] text-forge-dim italic text-center py-8">
                  Click a class to see mastery breakdown
                </p>
              </Panel>
            )}
          </div>

          {/* Popular skills + affixes side by side */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <PopularSkillsPanel skills={snapshotRes.data.popular_skills} />
            <PopularAffixesPanel affixes={snapshotRes.data.popular_affixes} />
          </div>
        </>
      )}

      {/* Trending builds */}
      {trendingLoading && (
        <div className="flex justify-center py-8">
          <Spinner size={24} />
        </div>
      )}

      {trendingError && (
        <ErrorMessage message="Failed to load trending builds." />
      )}

      {trendingRes?.data && (
        <TrendingBuildsSection builds={trendingRes.data} />
      )}

      {/* Footer */}
      {snapshotRes?.data && (
        <div className="text-center font-mono text-[10px] text-forge-dim py-4 border-t border-forge-border/30">
          Last updated: {new Date(snapshotRes.data.last_updated).toLocaleString()}
          {" | "}Patch {snapshotRes.data.current_patch}
          {" | "}Data refreshes every 6 hours
        </div>
      )}
    </div>
  );
}
