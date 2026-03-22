import { useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { clsx } from "clsx";

import { Panel, Button, Badge, Spinner, EmptyState, ConfirmModal } from "@/components/ui";
import {
  useProfile, useProfileBuilds,
  useProfileSessions, useDeleteBuild,
} from "@/hooks";
import { useAuthStore } from "@/store";
import { CLASS_COLORS } from "@/lib/gameData";
import type { CharacterClass } from "@/types";

// ---------------------------------------------------------------------------
// Stat card
// ---------------------------------------------------------------------------

function StatCard({ label, value, color }: { label: string; value: number | string; color?: string }) {
  const c = color ?? "#f0a020";
  return (
    <div className="bg-forge-surface border border-forge-border rounded p-6 text-center"
      style={{ background: "linear-gradient(135deg, #0c0f1c 0%, #10152a 100%)" }}
    >
      <span
        className="font-display text-4xl font-bold block mb-2"
        style={{ color: c, textShadow: `0 0 20px ${c}50` }}
      >
        {value}
      </span>
      <span className="font-mono text-xs uppercase tracking-widest text-forge-muted">
        {label}
      </span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Tabs
// ---------------------------------------------------------------------------

type Tab = "overview" | "builds" | "sessions";

// ---------------------------------------------------------------------------
// Builds tab
// ---------------------------------------------------------------------------

function BuildsTab() {
  const [page, setPage] = useState(1);
  const { data: res, isLoading } = useProfileBuilds(page);
  const deleteBuild = useDeleteBuild();
  const [deleteTarget, setDeleteTarget] = useState<{ slug: string; name: string } | null>(null);

  const builds = res?.data ?? [];
  const meta = res?.meta;

  async function handleDelete() {
    if (!deleteTarget) return;
    await deleteBuild.mutateAsync(deleteTarget.slug);
    setDeleteTarget(null);
  }

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size={28} /></div>;

  return (
    <div>
      {deleteTarget && (
        <ConfirmModal
          title="Delete Build"
          message={`Are you sure you want to delete "${deleteTarget.name}"?`}
          confirmLabel="Delete Build"
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
          isPending={deleteBuild.isPending}
        />
      )}

      {builds.length === 0 ? (
        <EmptyState
          title="No builds yet"
          description="Head to the Build Planner to create your first build."
          action={<Link to="/build"><Button variant="ghost" size="sm">Create Build</Button></Link>}
        />
      ) : (
        <div className="flex flex-col gap-2.5">
          {builds.map((build: any) => (
            <div
              key={build.id}
              className="bg-forge-surface border border-forge-border rounded px-5 py-4 hover:border-forge-border-hot transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <Link
                    to={`/build/${build.slug}`}
                    className="font-display text-base font-semibold text-forge-text hover:text-forge-amber transition-colors no-underline block truncate"
                  >
                    {build.name}
                  </Link>
                  <div className="flex flex-wrap gap-2 mt-2">
                    <span
                      className="font-mono text-xs uppercase tracking-widest px-2 py-0.5 border rounded-sm"
                      style={{
                        color: CLASS_COLORS[build.character_class as CharacterClass] ?? "#eceef8",
                        borderColor: `${CLASS_COLORS[build.character_class as CharacterClass] ?? "#4a5480"}50`,
                        background: `${CLASS_COLORS[build.character_class as CharacterClass] ?? "#4a5480"}12`,
                      }}
                    >
                      {build.character_class}
                    </span>
                    <span className="font-mono text-xs text-forge-muted border border-forge-border px-2 py-0.5 rounded-sm">
                      {build.mastery}
                    </span>
                    {build.is_ssf && <Badge variant="ssf">SSF</Badge>}
                    {build.is_hc && <Badge variant="hc">HC</Badge>}
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <Link to={`/build/${build.slug}`}>
                    <button className="font-mono text-xs uppercase tracking-widest text-forge-muted hover:text-forge-amber border border-forge-border hover:border-forge-amber rounded-sm px-3 py-1.5 bg-transparent cursor-pointer transition-colors">
                      View
                    </button>
                  </Link>
                  <button
                    onClick={() => setDeleteTarget({ slug: build.slug, name: build.name })}
                    className="font-mono text-xs uppercase tracking-widest text-forge-dim hover:text-forge-red border border-forge-border/50 hover:border-forge-red/40 rounded-sm px-3 py-1.5 bg-transparent cursor-pointer transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {meta && meta.pages > 1 && (
        <div className="flex justify-center gap-3 mt-5">
          <Button variant="outline" size="sm" disabled={!meta.has_prev} onClick={() => setPage(p => p - 1)}>Previous</Button>
          <span className="font-mono text-sm text-forge-muted self-center">{meta.page} / {meta.pages}</span>
          <Button variant="outline" size="sm" disabled={!meta.has_next} onClick={() => setPage(p => p + 1)}>Next</Button>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sessions tab
// ---------------------------------------------------------------------------

function SessionsTab() {
  const [page, setPage] = useState(1);
  const { data: res, isLoading } = useProfileSessions(page);

  const sessions = res?.data ?? [];
  const meta = res?.meta;

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size={28} /></div>;

  return (
    <div>
      {sessions.length === 0 ? (
        <EmptyState
          title="No craft sessions yet"
          description="Head to the Craft Simulator to start planning your crafts."
          action={<Link to="/craft"><Button variant="ghost" size="sm">Open Simulator</Button></Link>}
        />
      ) : (
        <div className="flex flex-col gap-2.5">
          {sessions.map((session: any) => (
            <Link key={session.id} to={`/craft/${session.slug}`} className="no-underline">
              <div className="bg-forge-surface border border-forge-border rounded px-5 py-4 hover:border-forge-border-hot transition-colors">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="font-display text-base font-semibold text-forge-text">
                      {session.item_name ?? session.item_type}
                    </div>
                    <div className="flex items-center gap-4 mt-1.5">
                      <span className="font-mono text-xs text-forge-muted">{session.item_type}</span>
                      <span className="font-mono text-xs text-forge-dim">
                        {session.step_count} actions
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 flex-shrink-0">
                    <div
                      className="font-display text-sm font-bold"
                      style={{ color: "#3dca74" }}
                    >
                      {session.forge_potential} FP
                    </div>
                    <div className="font-mono text-xs uppercase tracking-widest text-forge-muted border border-forge-border rounded-sm px-3 py-1.5 hover:border-forge-amber hover:text-forge-amber transition-colors">
                      Resume →
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {meta && meta.pages > 1 && (
        <div className="flex justify-center gap-3 mt-5">
          <Button variant="outline" size="sm" disabled={!meta.has_prev} onClick={() => setPage(p => p - 1)}>Previous</Button>
          <span className="font-mono text-sm text-forge-muted self-center">{meta.page} / {meta.pages}</span>
          <Button variant="outline" size="sm" disabled={!meta.has_next} onClick={() => setPage(p => p + 1)}>Next</Button>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Overview tab
// ---------------------------------------------------------------------------

function OverviewTab({ profileData }: { profileData: any }) {
  const recentBuilds = profileData.recent_builds ?? [];
  const recentSessions = profileData.recent_sessions ?? [];

  return (
    <div className="grid gap-5" style={{ gridTemplateColumns: "1fr 1fr" }}>
      {/* Recent Builds */}
      <Panel title="Recent Builds" action={
        <Link to="/build" className="font-mono text-xs uppercase tracking-widest text-forge-dim hover:text-forge-amber no-underline transition-colors">+ New</Link>
      }>
        {recentBuilds.length === 0 ? (
          <p className="font-body text-sm italic text-forge-dim">No builds yet.</p>
        ) : recentBuilds.map((b: any) => (
          <Link key={b.id} to={`/build/${b.slug}`} className="no-underline block">
            <div className="flex items-center justify-between py-2.5 border-b border-forge-border/40 last:border-b-0 hover:bg-forge-surface2 rounded-sm px-2 transition-colors">
              <div>
                <div className="font-body text-sm text-forge-text truncate max-w-[160px]">{b.name}</div>
                <div className="font-mono text-xs text-forge-dim mt-0.5">{b.mastery}</div>
              </div>
              <span
                className="font-mono text-xs px-2 py-0.5 border rounded-sm"
                style={{
                  color: CLASS_COLORS[b.character_class as CharacterClass] ?? "#8890b8",
                  borderColor: `${CLASS_COLORS[b.character_class as CharacterClass] ?? "#4a5480"}50`,
                  background: `${CLASS_COLORS[b.character_class as CharacterClass] ?? "#4a5480"}12`,
                }}
              >
                {b.character_class}
              </span>
            </div>
          </Link>
        ))}
      </Panel>

      {/* Recent Sessions */}
      <Panel title="Recent Crafts" action={
        <Link to="/craft" className="font-mono text-xs uppercase tracking-widest text-forge-dim hover:text-forge-amber no-underline transition-colors">+ New</Link>
      }>
        {recentSessions.length === 0 ? (
          <p className="font-body text-sm italic text-forge-dim">No sessions yet.</p>
        ) : recentSessions.map((s: any) => (
          <Link key={s.id} to={`/craft/${s.slug}`} className="no-underline block">
            <div className="flex items-center justify-between py-2.5 border-b border-forge-border/40 last:border-b-0 hover:bg-forge-surface2 rounded-sm px-2 transition-colors">
              <div>
                <div className="font-body text-sm text-forge-text truncate max-w-[160px]">
                  {s.item_name ?? s.item_type}
                </div>
                <div className="font-mono text-xs text-forge-dim mt-0.5">{s.item_type}</div>
              </div>
              <span
                className="font-mono text-xs font-semibold"
                style={{ color: "#3dca74" }}
              >
                {s.forge_potential} FP
              </span>
            </div>
          </Link>
        ))}
      </Panel>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Profile Page
// ---------------------------------------------------------------------------

export default function UserProfilePage() {
  const { user } = useAuthStore();
  const { data: profileRes, isLoading } = useProfile();
  const [tab, setTab] = useState<Tab>("overview");

  if (!user) return <Navigate to="/" replace />;

  if (isLoading) {
    return <div className="flex items-center justify-center py-24"><Spinner size={32} /></div>;
  }

  const profile = profileRes?.data;
  if (!profile) return null;

  const stats = profile.stats;

  const TABS: { id: Tab; label: string; count?: number }[] = [
    { id: "overview",  label: "Overview" },
    { id: "builds",    label: "Builds",         count: stats.total_builds   },
    { id: "sessions",  label: "Craft Sessions",  count: stats.total_sessions },
  ];

  return (
    <div>
      {/* Profile header */}
      <div className="flex items-center gap-6 mb-10 p-6 bg-forge-surface border border-forge-border rounded"
        style={{ background: "linear-gradient(135deg, #0c0f1c 0%, #10152a 100%)" }}
      >
        {user.avatar_url ? (
          <img
            src={user.avatar_url}
            alt={user.username}
            className="w-20 h-20 rounded-full border-2 border-forge-border"
            style={{ boxShadow: "0 0 20px rgba(240,160,32,0.20)" }}
          />
        ) : (
          <div
            className="w-20 h-20 rounded-full border-2 border-forge-amber/40 bg-forge-surface2 flex items-center justify-center"
            style={{ boxShadow: "0 0 20px rgba(240,160,32,0.20)" }}
          >
            <span className="font-display text-3xl font-bold text-forge-amber">
              {user.username[0].toUpperCase()}
            </span>
          </div>
        )}
        <div>
          <h1
            className="font-display text-4xl font-bold text-forge-amber tracking-wider mb-1.5"
            style={{ textShadow: "0 0 24px rgba(240,160,32,0.35)" }}
          >
            {user.username}
          </h1>
          <div className="font-mono text-xs uppercase tracking-widest text-forge-dim">
            Member since {new Date(profile.user.created_at).toLocaleDateString("en-US", { month: "long", year: "numeric" })}
          </div>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <StatCard label="Builds Created" value={stats.total_builds} />
        <StatCard label="Craft Sessions" value={stats.total_sessions} color="#00d4f5" />
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 mb-6 border-b border-forge-border pb-0">
        {TABS.map(({ id, label, count }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={clsx(
              "font-mono text-xs uppercase tracking-widest px-5 py-3 border-b-2 -mb-px bg-transparent cursor-pointer transition-all",
              tab === id
                ? "border-forge-amber text-forge-amber"
                : "border-transparent text-forge-muted hover:text-forge-text"
            )}
          >
            {label}
            {count !== undefined && count > 0 && (
              <span className={clsx(
                "ml-2 font-mono text-[10px] px-1.5 py-0.5 rounded-sm",
                tab === id ? "bg-forge-amber/15 text-forge-amber" : "bg-forge-surface2 text-forge-dim"
              )}>{count}</span>
            )}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {tab === "overview"  && <OverviewTab profileData={profile} />}
      {tab === "builds"    && <BuildsTab />}
      {tab === "sessions"  && <SessionsTab />}
    </div>
  );
}
