/**
 * DashboardPage — The Forge landing page.
 *
 * Replaces the raw backend-debug dashboard that used to live at `/`.
 * Presents:
 *   - Hero section with Season + Patch badge and two CTA buttons
 *   - Stats row: community builds, skills, affixes counts
 *   - Meta snapshot: top 5 classes bar chart, top 5 skills
 *   - 2×3 quick links grid
 */
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui";
import PageMeta from "@/components/PageMeta";
import { useBuilds } from "@/hooks";
import { metaApi, refApi, versionApi } from "@/lib/api";
import { CLASS_COLORS } from "@/lib/gameData";
import type { CharacterClass } from "@/types";

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

function useVersion() {
  return useQuery({
    queryKey: ["version"],
    queryFn: () => versionApi.get(),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}

function useMetaSnapshot() {
  return useQuery({
    queryKey: ["meta", "snapshot"],
    queryFn: () => metaApi.snapshot(),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}

function useSkillsCount() {
  return useQuery({
    queryKey: ["ref", "skills", "count"],
    queryFn: () => refApi.skills(),
    staleTime: Infinity,
    retry: false,
  });
}

function useAffixesCount() {
  return useQuery({
    queryKey: ["ref", "affixes", "count"],
    queryFn: () => refApi.affixes(),
    staleTime: Infinity,
    retry: false,
  });
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StatCard({
  label,
  value,
  color,
  loading,
}: {
  label: string;
  value: string | number;
  color: string;
  loading?: boolean;
}) {
  return (
    <div
      className="bg-forge-surface border border-forge-border rounded p-6 text-center"
      style={{ background: "linear-gradient(135deg, #0c0f1c 0%, #10152a 100%)" }}
    >
      <span
        className="font-display text-4xl font-bold block mb-2 tabular-nums"
        style={{ color, textShadow: `0 0 20px ${color}50` }}
      >
        {loading ? "—" : value}
      </span>
      <span className="font-mono text-xs uppercase tracking-widest text-forge-muted">
        {label}
      </span>
    </div>
  );
}

function QuickLinkCard({
  to,
  title,
  description,
  accent,
  icon,
}: {
  to: string;
  title: string;
  description: string;
  accent: string;
  icon: string;
}) {
  return (
    <Link to={to} className="block no-underline group">
      <div
        className="h-full bg-forge-surface border border-forge-border rounded p-5 transition-all duration-200 relative overflow-hidden
          hover:border-forge-border-hot hover:-translate-y-0.5"
        style={{ background: "linear-gradient(135deg, #0c0f1c 0%, #10152a 100%)" }}
      >
        <div
          className="absolute top-0 left-0 right-0 h-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
          style={{ background: `linear-gradient(90deg, transparent, ${accent}, transparent)` }}
        />
        <div className="flex items-center gap-3 mb-2">
          <span
            className="text-2xl"
            style={{ filter: `drop-shadow(0 0 8px ${accent}60)` }}
          >
            {icon}
          </span>
          <span className="font-display text-base font-semibold text-forge-text tracking-wider">
            {title}
          </span>
        </div>
        <p className="font-body text-sm text-forge-muted leading-relaxed">
          {description}
        </p>
      </div>
    </Link>
  );
}

const QUICK_LINKS = [
  { to: "/build",      title: "Build Planner",    description: "Plan a full build with passives, skills, and gear.", accent: "#f0a020", icon: "⚔" },
  { to: "/craft",      title: "Crafting Lab",     description: "Plan crafts with FP cost simulation.",                accent: "#e06030", icon: "🔥" },
  { to: "/builds",     title: "Community Builds", description: "Browse, vote, and compare community builds.",         accent: "#00d4f5", icon: "⚡" },
  { to: "/bis-search", title: "BIS Search",       description: "Find the optimal gear combination across all slots.", accent: "#22d3ee", icon: "🎯" },
  { to: "/encounter",  title: "Simulation",       description: "Simulate encounter DPS against boss templates.",      accent: "#b870ff", icon: "📊" },
  { to: "/meta",       title: "Meta Snapshot",    description: "Class distribution, popular skills and affixes.",      accent: "#3dca74", icon: "🧭" },
];

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export default function DashboardPage() {
  const { data: versionRes } = useVersion();
  const { data: buildsRes } = useBuilds({ sort: "votes" });
  const { data: metaRes, isLoading: metaLoading } = useMetaSnapshot();
  const { data: skillsRes, isLoading: skillsLoading } = useSkillsCount();
  const { data: affixesRes, isLoading: affixesLoading } = useAffixesCount();

  const version = versionRes?.data;
  const meta = metaRes?.data ?? null;
  const buildsTotal = buildsRes?.meta?.total ?? 0;

  // refApi.skills returns Record<string, SkillDef[]> keyed by class,
  // so total skills = sum of lengths.
  const skillsTotal = (() => {
    const payload = skillsRes?.data;
    if (!payload) return 0;
    if (Array.isArray(payload)) return payload.length;
    if (typeof payload === "object") {
      return Object.values(payload as Record<string, unknown>).reduce<number>(
        (sum, list) => sum + (Array.isArray(list) ? list.length : 0),
        0
      );
    }
    return 0;
  })();

  const affixesTotal = (() => {
    const payload = affixesRes?.data;
    if (Array.isArray(payload)) return payload.length;
    return 0;
  })();

  // Show up to 5 classes with at least one public build. The backend's
  // class_distribution only includes classes that have builds (group-by),
  // but we still filter defensively in case that changes.
  const topClasses = (meta?.class_distribution ?? [])
    .filter((d) => d.count > 0)
    .slice(0, 5);
  const topSkills = (meta?.popular_skills ?? []).slice(0, 5);
  const classTotal = topClasses.reduce((s, d) => s + d.count, 0) || 1;
  const skillMax = topSkills.reduce((m, s) => Math.max(m, s.usage_count), 0) || 1;

  const patchLabel = version?.current_patch ?? "1.4.3";
  const seasonLabel = version?.current_season ?? 4;

  return (
    <div>
      <PageMeta
        title="Dashboard"
        description="The Forge — your Last Epoch command center. Browse community builds, explore the meta, and plan your next character."
        path="/"
      />
      {/* Hero */}
      <section className="pt-12 pb-10 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-forge-amber/40 bg-forge-amber/10 px-4 py-1.5 font-mono text-[10px] uppercase tracking-[0.28em] text-forge-amber mb-6">
          <span>Season {seasonLabel}</span>
          <span className="text-forge-amber/50">·</span>
          <span>Patch {patchLabel}</span>
        </div>

        <h1 className="font-display text-7xl font-bold leading-none tracking-tight text-forge-text">
          The{" "}
          <span
            className="text-forge-amber"
            style={{ textShadow: "0 0 40px rgba(240,160,32,0.50), 0 0 80px rgba(240,160,32,0.20)" }}
          >
            Forge
          </span>
        </h1>

        <p className="font-body text-xl font-light text-forge-muted mt-6 max-w-2xl mx-auto leading-relaxed">
          Last Epoch Build Intelligence.
          <br />
          <span className="text-forge-dim text-base">
            Simulate. Craft. Optimize.
          </span>
        </p>

        <div className="flex gap-4 justify-center mt-8">
          <Link to="/build">
            <Button variant="primary" size="md">Start Planning</Button>
          </Link>
          <Link to="/builds">
            <Button variant="ghost" size="md">Browse Community Builds</Button>
          </Link>
        </div>
      </section>

      {/* Stats row */}
      <section className="mb-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatCard
            label="Community Builds"
            value={buildsTotal.toLocaleString()}
            color="#f0a020"
          />
          <StatCard
            label="Skills Catalogued"
            value={skillsTotal.toLocaleString()}
            color="#00d4f5"
            loading={skillsLoading}
          />
          <StatCard
            label="Affixes Indexed"
            value={affixesTotal.toLocaleString()}
            color="#3dca74"
            loading={affixesLoading}
          />
        </div>
      </section>

      {/* Meta snapshot */}
      <section className="mb-10 grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Top classes */}
        <div className="rounded border border-forge-border bg-forge-surface p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-mono text-xs uppercase tracking-widest text-forge-muted">
              Top Classes
            </h2>
            <Link
              to="/meta"
              className="font-mono text-[10px] uppercase tracking-widest text-forge-dim hover:text-forge-amber no-underline transition-colors"
            >
              View full meta →
            </Link>
          </div>
          {metaLoading ? (
            <p className="font-mono text-xs text-forge-dim">Loading…</p>
          ) : topClasses.length === 0 ? (
            <p className="font-mono text-xs text-forge-dim">No builds yet.</p>
          ) : (
            <div className="space-y-3">
              {topClasses.map((d) => {
                const pct = Math.round((d.count / classTotal) * 100);
                const color = CLASS_COLORS[d.class as CharacterClass] ?? "#8890b8";
                return (
                  <div key={d.class}>
                    <div className="flex justify-between font-mono text-xs mb-1">
                      <span style={{ color }}>{d.class}</span>
                      <span className="text-forge-muted">
                        {d.count} <span className="text-forge-dim">({pct}%)</span>
                      </span>
                    </div>
                    <div className="h-2 rounded-full bg-forge-surface2 overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{ width: `${pct}%`, backgroundColor: color }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Top skills */}
        <div className="rounded border border-forge-border bg-forge-surface p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-mono text-xs uppercase tracking-widest text-forge-muted">
              Popular Skills
            </h2>
            <Link
              to="/meta"
              className="font-mono text-[10px] uppercase tracking-widest text-forge-dim hover:text-forge-amber no-underline transition-colors"
            >
              View full meta →
            </Link>
          </div>
          {metaLoading ? (
            <p className="font-mono text-xs text-forge-dim">Loading…</p>
          ) : topSkills.length === 0 ? (
            <p className="font-mono text-xs text-forge-dim">No skills recorded yet.</p>
          ) : (
            <div className="space-y-2.5">
              {topSkills.map((s) => {
                const pct = Math.round((s.usage_count / skillMax) * 100);
                return (
                  <div key={s.skill_name}>
                    <div className="flex justify-between font-mono text-xs mb-1">
                      <span className="text-forge-text truncate pr-2">{s.skill_name}</span>
                      <span className="text-forge-muted tabular-nums">{s.usage_count}</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-forge-surface2 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-forge-amber/70 transition-all duration-700"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </section>

      {/* Quick links grid */}
      <section className="mb-12">
        <div className="font-mono text-xs uppercase tracking-[0.28em] text-forge-dim text-center mb-6">
          Jump In
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {QUICK_LINKS.map((q) => (
            <QuickLinkCard key={q.to} {...q} />
          ))}
        </div>
      </section>
    </div>
  );
}
