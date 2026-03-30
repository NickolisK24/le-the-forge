/**
 * MetaSnapshotPage — live meta tracker for The Forge community builds.
 *
 * Consumes GET /api/builds/meta/snapshot (120s server cache).
 * Displays:
 *   1. Summary strip — total builds, most played class, top mastery
 *   2. Class distribution bar chart
 *   3. S-tier builds list
 */

import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { buildsApi } from "@/lib/api";
import type { MetaSnapshot, MetaSnapshotEntry, STierBuild } from "@/lib/api";
import { Panel, Spinner, ErrorMessage } from "@/components/ui";
import { CLASS_COLORS } from "@/lib/gameData";

// ---------------------------------------------------------------------------
// Class distribution bar chart panel
// ---------------------------------------------------------------------------

function ClassDistributionPanel({ distribution }: { distribution: MetaSnapshotEntry[] }) {
  const total = distribution.reduce((sum, d) => sum + d.count, 0) || 1;

  return (
    <Panel title="Class Distribution">
      <div className="space-y-3">
        {distribution.map((d) => {
          const pct = Math.round((d.count / total) * 100);
          const color = CLASS_COLORS[d.class as keyof typeof CLASS_COLORS] ?? "#8890b8";
          return (
            <div key={d.class}>
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
            </div>
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
// S-tier builds list panel
// ---------------------------------------------------------------------------

function STierBuildsPanel({ builds }: { builds: STierBuild[] }) {
  return (
    <Panel title="S-Tier Builds">
      {builds.length === 0 ? (
        <p className="font-mono text-[10px] text-forge-dim italic text-center py-4">
          No S-tier builds yet
        </p>
      ) : (
        <div className="divide-y divide-forge-border/20">
          {builds.map((b, i) => (
            <Link
              key={b.id}
              to={`/build/${b.slug}`}
              className="flex items-center gap-3 py-2.5 group no-underline"
            >
              <span className="font-display text-sm font-bold text-forge-amber w-5 text-center">
                {i + 1}
              </span>
              <div className="flex-1 min-w-0">
                <div className="font-body text-sm text-forge-text group-hover:text-forge-amber transition-colors truncate">
                  {b.name}
                </div>
                <div className="font-mono text-[10px] text-forge-dim">{b.mastery}</div>
              </div>
              <span className="font-mono text-[10px] text-yellow-400 bg-yellow-500/10 border border-yellow-500/20 px-2 py-0.5 rounded shrink-0">
                S
              </span>
            </Link>
          ))}
        </div>
      )}
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Summary strip
// ---------------------------------------------------------------------------

function SummaryStrip({ data }: { data: MetaSnapshot }) {
  return (
    <div className="grid grid-cols-3 gap-4 rounded border border-forge-border bg-forge-surface2 px-6 py-4">
      <div className="text-center">
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-muted mb-1">
          Total Builds
        </div>
        <div className="font-display text-3xl font-bold text-forge-amber">
          {data.total_builds.toLocaleString()}
        </div>
      </div>
      <div className="text-center">
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-muted mb-1">
          Most Played Class
        </div>
        <div
          className="font-display text-2xl font-bold"
          style={{
            color: CLASS_COLORS[data.most_played_class as keyof typeof CLASS_COLORS] ?? "#f0a020",
          }}
        >
          {data.most_played_class}
        </div>
      </div>
      <div className="text-center">
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-muted mb-1">
          Top Mastery
        </div>
        <div className="font-display text-2xl font-bold text-forge-cyan">
          {data.top_mastery}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page root
// ---------------------------------------------------------------------------

export default function MetaSnapshotPage() {
  const { data: res, isLoading, isError } = useQuery({
    queryKey: ["meta-snapshot"],
    queryFn: () => buildsApi.metaSnapshot(),
    staleTime: 2 * 60 * 1000, // 2 min — matches server cache TTL
    retry: 1,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <Spinner size={32} />
      </div>
    );
  }

  if (isError || !res?.data) {
    return (
      <div className="mx-auto max-w-2xl py-16">
        <ErrorMessage message="Failed to load meta snapshot. Please try again." />
      </div>
    );
  }

  const data = res.data;

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 space-y-6">
      {/* Page header */}
      <div>
        <h1 className="font-display text-2xl font-bold text-forge-amber tracking-wide">
          Meta Snapshot
        </h1>
        <p className="font-body text-sm text-forge-muted mt-1">
          Live aggregate stats from all public community builds. Updated every 2 minutes.
        </p>
      </div>

      {/* Summary numbers */}
      <SummaryStrip data={data} />

      {/* Class distribution + S-tier builds side by side */}
      <div className="grid grid-cols-2 gap-4">
        <ClassDistributionPanel distribution={data.class_distribution} />
        <STierBuildsPanel builds={data.s_tier_builds} />
      </div>
    </div>
  );
}
