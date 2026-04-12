/**
 * BuildsPage — community build browser.
 *
 * Filterable by class, mastery, sort order, and tags. Paginated with Next/Prev.
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { clsx } from "clsx";

import { Button, Badge, Spinner, EmptyState, ErrorMessage } from "@/components/ui";
import PageMeta from "@/components/PageMeta";
import { useBuilds, useVote } from "@/hooks";
import { useAuthStore } from "@/store";
import { CLASS_COLORS, MASTERIES } from "@/lib/gameData";
import { BASE_CLASSES } from "@constants";
import type { BuildListItem, BuildFilters, CharacterClass, BuildTier } from "@/types";

// ---------------------------------------------------------------------------
// Filter state type
// ---------------------------------------------------------------------------

type ActiveFilters = BuildFilters & { page: number };

const SORT_OPTIONS = [
  { value: "votes", label: "Top Voted"    },
  { value: "new",   label: "Newest"       },
  { value: "tier",  label: "By Tier"      },
  { value: "views", label: "Most Viewed"  },
] as const;

const CLASSES: CharacterClass[] = [...BASE_CLASSES] as CharacterClass[];

const TIER_COLORS: Record<BuildTier, string> = {
  S: "#f5d060",
  A: "#3dca74",
  B: "#f0a020",
  C: "#8890b8",
};

// ---------------------------------------------------------------------------
// Build card
// ---------------------------------------------------------------------------

function BuildCard({
  build,
  isCompareSelected,
  onCompareToggle,
}: {
  build: BuildListItem;
  isCompareSelected: boolean;
  onCompareToggle: (slug: string) => void;
}) {
  const { user } = useAuthStore();
  const vote = useVote();

  const tierColor = TIER_COLORS[build.tier ?? "C"];
  const classColor = CLASS_COLORS[build.character_class] ?? "#8890b8";
  // Hide the C tier for unrated builds — only show a tier badge when
  // the backend has assigned one explicitly (i.e. there is simulation data).
  const hasRating = Boolean(build.tier);

  function handleVote(dir: 1 | -1) {
    if (!user) return;
    vote.mutate({ slug: build.slug, direction: dir });
  }

  return (
    <div className="bg-forge-surface border border-forge-border rounded transition-all duration-200 hover:border-forge-border-hot group"
      style={{ boxShadow: "0 2px 12px rgba(0,0,0,0.3)" }}
    >
      <div className="flex items-stretch">
        {/* Vote column */}
        <div className="flex flex-col items-center justify-center gap-1.5 px-4 py-4 border-r border-forge-border/50 min-w-[52px]">
          <button
            onClick={() => handleVote(1)}
            disabled={!user || vote.isPending}
            className="font-mono text-sm text-forge-dim hover:text-forge-amber disabled:opacity-30 disabled:cursor-default bg-transparent border-none cursor-pointer leading-none transition-colors"
          >▲</button>
          <span className="font-mono text-sm font-bold text-forge-amber tabular-nums">
            {build.vote_count}
          </span>
          <button
            onClick={() => handleVote(-1)}
            disabled={!user || vote.isPending}
            className="font-mono text-sm text-forge-dim hover:text-forge-red disabled:opacity-30 disabled:cursor-default bg-transparent border-none cursor-pointer leading-none transition-colors"
          >▼</button>
        </div>

        {/* Main content */}
        <div className="flex-1 min-w-0 px-5 py-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <Link
                to={`/build/${build.slug}`}
                className="font-display text-base font-semibold text-forge-text hover:text-forge-amber transition-colors no-underline block truncate"
              >
                {build.name}
              </Link>

              <p className="font-body text-sm text-forge-muted mt-1 line-clamp-1 leading-relaxed">
                {build.description?.trim() || (
                  <span className="italic text-forge-dim">No description provided</span>
                )}
              </p>

              <div className="flex flex-wrap items-center gap-2 mt-2.5">
                <span
                  className="font-mono text-xs uppercase tracking-widest px-2 py-0.5 border rounded-sm"
                  style={{ color: classColor, borderColor: `${classColor}50`, background: `${classColor}10` }}
                >
                  {build.character_class}
                </span>
                <span className="font-mono text-xs text-forge-muted border border-forge-border px-2 py-0.5 rounded-sm">
                  {build.mastery}
                </span>
                {build.is_ssf && <Badge variant="ssf">SSF</Badge>}
                {build.is_hc && <Badge variant="hc">HC</Badge>}
                {build.is_ladder_viable && <Badge variant="ladder">Ladder</Badge>}
                {build.is_budget && <Badge variant="budget">Budget</Badge>}
              </div>
            </div>

            {/* Tier + meta */}
            <div className="flex flex-col items-end gap-2 flex-shrink-0">
              {hasRating ? (
                <span
                  className="font-display text-2xl font-bold leading-none"
                  style={{ color: tierColor, textShadow: `0 0 12px ${tierColor}60` }}
                  title={`Tier ${build.tier}`}
                >
                  {build.tier}
                </span>
              ) : (
                <span
                  className="font-mono text-[10px] uppercase tracking-widest text-forge-dim border border-forge-border/60 rounded-sm px-1.5 py-0.5"
                  title="No simulation data yet — run a simulation to assign a tier."
                >
                  Unrated
                </span>
              )}
              {build.author && (
                <span className="font-mono text-[10px] text-forge-dim">
                  by {build.author.username}
                </span>
              )}
              <button
                onClick={() => onCompareToggle(build.slug)}
                title={isCompareSelected ? "Remove from comparison" : "Add to comparison"}
                className={clsx(
                  "font-mono text-[10px] uppercase tracking-widest px-2 py-1 border rounded-sm cursor-pointer transition-all",
                  isCompareSelected
                    ? "border-forge-cyan text-forge-cyan bg-forge-cyan/12"
                    : "border-forge-border text-forge-dim hover:border-forge-cyan/60 hover:text-forge-cyan"
                )}
              >
                {isCompareSelected ? "✓ Compare" : "+ Compare"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Filter chip
// ---------------------------------------------------------------------------

function FilterChip({
  label, active, onClick,
}: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        "font-mono text-xs uppercase tracking-widest px-3 py-1.5 border rounded-sm cursor-pointer transition-all",
        active
          ? "border-forge-amber text-forge-amber bg-forge-amber/12"
          : "border-forge-border text-forge-dim hover:border-forge-border-hot hover:text-forge-muted"
      )}
    >
      {label}
    </button>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export default function BuildsPage() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [filters, setFilters] = useState<ActiveFilters>({ sort: "votes", page: 1 });
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [compareSelection, setCompareSelection] = useState<string[]>([]);

  const { data: res, isLoading, isError, refetch } = useBuilds({ ...filters, q: search || undefined });
  const builds = res?.data ?? [];
  const meta = res?.meta;

  function toggleCompare(slug: string) {
    setCompareSelection((prev) => {
      if (prev.includes(slug)) return prev.filter((s) => s !== slug);
      if (prev.length >= 2) return [prev[1], slug]; // drop oldest, add new
      return [...prev, slug];
    });
  }

  function goCompare() {
    if (compareSelection.length === 2) {
      navigate(`/compare?a=${compareSelection[0]}&b=${compareSelection[1]}`);
    }
  }

  function setFilter<K extends keyof BuildFilters>(key: K, value: BuildFilters[K] | undefined) {
    setFilters((f) => {
      const next = { ...f, [key]: value, page: 1 };
      if (value === undefined) delete next[key];
      return next;
    });
  }

  function toggleClass(cls: CharacterClass) {
    setFilter("character_class", filters.character_class === cls ? undefined : cls);
  }

  function toggleSort(sort: BuildFilters["sort"]) {
    setFilter("sort", sort);
  }

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSearch(searchInput);
    setFilters((f) => ({ ...f, page: 1 }));
  }

  function clearFilters() {
    setFilters({ sort: "votes", page: 1 });
    setSearch("");
    setSearchInput("");
  }

  const hasActiveFilters = Boolean(
    filters.character_class || filters.mastery || filters.tier ||
    filters.is_ssf || filters.is_hc || filters.is_ladder_viable !== undefined ||
    search
  );

  const masteryOptions = filters.character_class
    ? MASTERIES[filters.character_class] ?? []
    : [];

  return (
    <div>
      <PageMeta
        title="Community Builds"
        description="Browse, vote, and compare Last Epoch community builds. Filter by class, mastery, tier, and playstyle."
        path="/builds"
      />
      {/* Page header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display text-4xl font-bold text-forge-amber tracking-wider"
            style={{ textShadow: "0 0 30px rgba(240,160,32,0.30)" }}
          >
            Community Builds
          </h1>
          <p className="font-body text-base text-forge-muted mt-1.5">
            {meta ? `${meta.total.toLocaleString()} builds available` : "Browse and vote on community builds"}
          </p>
        </div>
        <div className="flex gap-2">
          <Link to="/build">
            <Button variant="primary" size="sm">+ New Build</Button>
          </Link>
          <Link to="/build?import=true">
            <Button variant="outline" size="sm">↑ Import Build</Button>
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-forge-surface border border-forge-border rounded p-5 mb-6 flex flex-col gap-4">
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search builds…"
            className="flex-1 bg-forge-surface2 border border-forge-border text-forge-text font-body text-sm px-3 py-2 rounded-sm outline-none focus:border-forge-cyan/50 placeholder:text-forge-dim"
          />
          <Button type="submit" variant="outline" size="sm">Search</Button>
          {hasActiveFilters && (
            <Button type="button" variant="ghost" size="sm" onClick={clearFilters}>
              Clear
            </Button>
          )}
        </form>

        {/* Sort */}
        <div className="flex flex-wrap items-center gap-3">
          <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim w-10">Sort</span>
          <div className="flex flex-wrap gap-1.5">
            {SORT_OPTIONS.map((opt) => (
              <FilterChip
                key={opt.value}
                label={opt.label}
                active={filters.sort === opt.value}
                onClick={() => toggleSort(opt.value)}
              />
            ))}
          </div>
        </div>

        {/* Class filter */}
        <div className="flex flex-wrap items-center gap-3">
          <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim w-10">Class</span>
          <div className="flex flex-wrap gap-1.5">
            {CLASSES.map((cls) => (
              <button
                key={cls}
                onClick={() => toggleClass(cls)}
                className={clsx(
                  "font-mono text-xs uppercase tracking-widest px-3 py-1.5 border rounded-sm cursor-pointer transition-all",
                  filters.character_class === cls
                    ? "border-current"
                    : "border-forge-border text-forge-dim hover:border-forge-border-hot hover:text-forge-muted"
                )}
                style={filters.character_class === cls ? {
                  color: CLASS_COLORS[cls],
                  borderColor: CLASS_COLORS[cls],
                  background: `${CLASS_COLORS[cls]}18`,
                } : undefined}
              >
                {cls}
              </button>
            ))}
          </div>
        </div>

        {/* Mastery filter */}
        {masteryOptions.length > 0 && (
          <div className="flex flex-wrap items-center gap-3">
            <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim w-10">Mastery</span>
            <div className="flex flex-wrap gap-1.5">
              {masteryOptions.map((m) => (
                <FilterChip
                  key={m}
                  label={m}
                  active={filters.mastery === m}
                  onClick={() => setFilter("mastery", filters.mastery === m ? undefined : m)}
                />
              ))}
            </div>
          </div>
        )}

        {/* Tag filters */}
        <div className="flex flex-wrap items-center gap-3">
          <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim w-10">Tags</span>
          <div className="flex flex-wrap gap-1.5">
            <FilterChip
              label="SSF"
              active={Boolean(filters.is_ssf)}
              onClick={() => setFilter("is_ssf", filters.is_ssf ? undefined : true)}
            />
            <FilterChip
              label="HC"
              active={Boolean(filters.is_hc)}
              onClick={() => setFilter("is_hc", filters.is_hc ? undefined : true)}
            />
            <FilterChip
              label="Ladder"
              active={filters.is_ladder_viable === true}
              onClick={() => setFilter("is_ladder_viable", filters.is_ladder_viable === true ? undefined : true)}
            />
            <FilterChip
              label="Budget"
              active={Boolean(filters.is_budget)}
              onClick={() => setFilter("is_budget", filters.is_budget ? undefined : true)}
            />
          </div>
        </div>
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="flex justify-center py-16">
          <Spinner size={32} />
        </div>
      ) : isError ? (
        <ErrorMessage
          title="Could not load builds"
          message="Check your connection and try again."
          onRetry={refetch}
        />
      ) : builds.length === 0 ? (
        <EmptyState
          title="No builds found"
          description={hasActiveFilters ? "Try adjusting your filters." : "Be the first to share a build."}
          action={
            <div className="flex gap-2 justify-center">
              {hasActiveFilters && (
                <Button variant="ghost" size="sm" onClick={clearFilters}>Clear Filters</Button>
              )}
              <Link to="/build">
                <Button variant="primary" size="sm">Create Build</Button>
              </Link>
            </div>
          }
        />
      ) : (
        <>
          <div className="flex flex-col gap-2.5">
            {builds.map((build) => (
              <BuildCard
                key={build.id}
                build={build}
                isCompareSelected={compareSelection.includes(build.slug)}
                onCompareToggle={toggleCompare}
              />
            ))}
          </div>

          {/* Pagination */}
          {meta && meta.pages > 1 && (
            <div className="flex items-center justify-center gap-4 mt-8">
              <Button
                variant="outline"
                size="sm"
                disabled={!meta.has_prev}
                onClick={() => setFilters((f) => ({ ...f, page: f.page - 1 }))}
              >
                ← Previous
              </Button>
              <span className="font-mono text-sm text-forge-muted">
                Page {meta.page} of {meta.pages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={!meta.has_next}
                onClick={() => setFilters((f) => ({ ...f, page: f.page + 1 }))}
              >
                Next →
              </Button>
            </div>
          )}

          {!user && (
            <p className="font-mono text-xs text-forge-dim/60 text-center mt-5">
              Sign in to vote on builds.
            </p>
          )}
        </>
      )}

      {/* Sticky compare bar */}
      {compareSelection.length > 0 && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 flex items-center gap-4 bg-forge-surface2 border border-forge-cyan/40 rounded shadow-2xl px-5 py-3"
          style={{ boxShadow: "0 0 24px rgba(0,212,245,0.20)" }}
        >
          <span className="font-mono text-sm text-forge-cyan">
            {compareSelection.length === 1
              ? "1 build selected — select one more"
              : "2 builds selected"}
          </span>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCompareSelection([])}
            >
              Clear
            </Button>
            {compareSelection.length === 2 && (
              <Button variant="ghost" size="sm" onClick={goCompare}>
                Compare →
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
