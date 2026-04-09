/**
 * BuildComparisonPage — side-by-side comparison of two builds.
 *
 * URL: /compare?a=<slug>&b=<slug>
 * Both slugs are set by BuildsPage when user selects 2 builds to compare.
 */

import { useSearchParams, Link } from "react-router-dom";
import { clsx } from "clsx";

import { Button, Badge, Spinner, ErrorMessage, Panel, SectionLabel } from "@/components/ui";
import { useBuild } from "@/hooks";
import { CLASS_COLORS } from "@/lib/gameData";
import type { Build, BuildTier, CharacterClass } from "@/types";
import SimulationComparison from "./SimulationComparison";

const TIER_COLORS: Record<BuildTier, string> = {
  S: "#f5d060",
  A: "#3dca74",
  B: "#f0a020",
  C: "#8890b8",
};

// ---------------------------------------------------------------------------
// Stat comparison row
// ---------------------------------------------------------------------------

function CompareRow({
  label,
  a,
  b,
  highlight = "high",
  format,
}: {
  label: string;
  a: number | string | null | undefined;
  b: number | string | null | undefined;
  /** "high" = higher is better, "low" = lower is better, "none" = no winner */
  highlight?: "high" | "low" | "none";
  format?: (v: number) => string;
}) {
  const aNum = typeof a === "number" ? a : null;
  const bNum = typeof b === "number" ? b : null;

  let aWins = false;
  let bWins = false;
  if (aNum !== null && bNum !== null && aNum !== bNum) {
    if (highlight === "high") { aWins = aNum > bNum; bWins = bNum > aNum; }
    if (highlight === "low")  { aWins = aNum < bNum; bWins = bNum < aNum; }
  }

  const fmt = (v: number | string | null | undefined) => {
    if (v === null || v === undefined) return "—";
    if (typeof v === "number" && format) return format(v);
    return String(v);
  };

  return (
    <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-2 py-2 border-b border-forge-border/40 last:border-b-0">
      <div
        className={clsx(
          "font-mono text-sm text-right tabular-nums",
          aWins ? "text-forge-green font-bold" : bWins ? "text-forge-muted" : "text-forge-text"
        )}
      >
        {aWins && <span className="mr-1 text-forge-green">▲</span>}
        {fmt(a)}
      </div>
      <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim text-center px-3 w-40 shrink-0">
        {label}
      </div>
      <div
        className={clsx(
          "font-mono text-sm text-left tabular-nums",
          bWins ? "text-forge-green font-bold" : aWins ? "text-forge-muted" : "text-forge-text"
        )}
      >
        {fmt(b)}
        {bWins && <span className="ml-1 text-forge-green">▲</span>}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Build header card
// ---------------------------------------------------------------------------

function BuildHeader({ build, side }: { build: Build; side: "A" | "B" }) {
  const classColor = CLASS_COLORS[build.character_class as CharacterClass] ?? "#8890b8";
  const tierColor = TIER_COLORS[build.tier ?? "C"];

  return (
    <div className="rounded border border-forge-border bg-forge-surface overflow-hidden">
      <div
        className="h-1.5 w-full"
        style={{ background: classColor, boxShadow: `0 0 12px ${classColor}60` }}
      />
      <div className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-1">
              Build {side}
            </div>
            <Link
              to={`/build/${build.slug}`}
              className="font-display text-xl font-bold text-forge-text hover:text-forge-amber transition-colors no-underline line-clamp-2"
            >
              {build.name}
            </Link>
          </div>
          <span
            className="font-display text-3xl font-bold flex-shrink-0 mt-1"
            style={{ color: tierColor, textShadow: `0 0 12px ${tierColor}60` }}
          >
            {build.tier ?? "C"}
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-2 mt-3">
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

        {build.author && (
          <div className="font-mono text-[11px] text-forge-dim mt-3">
            by {build.author.username}
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Skills comparison
// ---------------------------------------------------------------------------

function SkillsCompare({ a, b }: { a: Build; b: Build }) {
  const maxSkills = Math.max(a.skills.length, b.skills.length, 1);
  const rows = Array.from({ length: maxSkills }, (_, i) => ({
    a: a.skills[i],
    b: b.skills[i],
  }));

  return (
    <Panel title="Skills">
      <div className="space-y-2">
        {rows.map((row, i) => (
          <div key={i} className="grid grid-cols-[1fr_auto_1fr] items-center gap-2 py-1.5 border-b border-forge-border/40 last:border-b-0">
            <div className="text-right">
              {row.a ? (
                <div>
                  <span className="font-body text-sm text-forge-text">{row.a.skill_name}</span>
                  <span className="font-mono text-[11px] text-forge-dim ml-2">{row.a.points_allocated}pts</span>
                </div>
              ) : (
                <span className="font-mono text-xs text-forge-dim">—</span>
              )}
            </div>
            <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim text-center w-16 shrink-0">
              Slot {i + 1}
            </div>
            <div>
              {row.b ? (
                <div>
                  <span className="font-body text-sm text-forge-text">{row.b.skill_name}</span>
                  <span className="font-mono text-[11px] text-forge-dim ml-2">{row.b.points_allocated}pts</span>
                </div>
              ) : (
                <span className="font-mono text-xs text-forge-dim">—</span>
              )}
            </div>
          </div>
        ))}
        {a.skills.length === 0 && b.skills.length === 0 && (
          <p className="font-mono text-xs text-forge-dim text-center py-4">No skills configured</p>
        )}
      </div>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Gear comparison
// ---------------------------------------------------------------------------

const GEAR_SLOTS = [
  "head", "chest", "hands", "feet", "belt",
  "ring1", "ring2", "amulet", "weapon", "offhand",
] as const;

function GearCompare({ a, b }: { a: Build; b: Build }) {
  const aGear = Object.fromEntries((a.gear ?? []).map((g: any) => [g.slot, g]));
  const bGear = Object.fromEntries((b.gear ?? []).map((g: any) => [g.slot, g]));

  const filledSlots = GEAR_SLOTS.filter(
    (slot) => aGear[slot] || bGear[slot]
  );

  if (filledSlots.length === 0) {
    return (
      <Panel title="Gear">
        <p className="font-mono text-xs text-forge-dim text-center py-4">No gear configured</p>
      </Panel>
    );
  }

  return (
    <Panel title="Gear">
      <div className="space-y-2">
        {filledSlots.map((slot) => {
          const ga = aGear[slot];
          const gb = bGear[slot];
          return (
            <div key={slot} className="grid grid-cols-[1fr_auto_1fr] items-start gap-2 py-1.5 border-b border-forge-border/40 last:border-b-0">
              <div className="text-right min-w-0">
                {ga ? (
                  <div>
                    <div className="font-body text-sm text-forge-text truncate">{ga.item_name || "—"}</div>
                    {ga.rarity && (
                      <div className="font-mono text-[11px] text-forge-muted">{ga.rarity}</div>
                    )}
                  </div>
                ) : <span className="font-mono text-xs text-forge-dim">—</span>}
              </div>
              <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim text-center w-20 shrink-0 pt-0.5">
                {slot}
              </div>
              <div className="min-w-0">
                {gb ? (
                  <div>
                    <div className="font-body text-sm text-forge-text truncate">{gb.item_name || "—"}</div>
                    {gb.rarity && (
                      <div className="font-mono text-[11px] text-forge-muted">{gb.rarity}</div>
                    )}
                  </div>
                ) : <span className="font-mono text-xs text-forge-dim">—</span>}
              </div>
            </div>
          );
        })}
      </div>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Main comparison page
// ---------------------------------------------------------------------------

function CompareSkeleton() {
  return (
    <div className="flex justify-center py-24">
      <Spinner size={32} />
    </div>
  );
}

function SelectBuildPrompt() {
  return (
    <div className="text-center py-20">
      <div className="font-display text-2xl font-bold text-forge-amber mb-3 tracking-wider">
        Select Builds to Compare
      </div>
      <p className="font-body text-forge-muted mb-8">
        Go to the Builds page and click <strong className="text-forge-text">Compare</strong> on two builds.
      </p>
      <Link to="/builds">
        <Button variant="primary">Browse Builds</Button>
      </Link>
    </div>
  );
}

export default function BuildComparisonPage() {
  const [params] = useSearchParams();
  const slugA = params.get("a") ?? "";
  const slugB = params.get("b") ?? "";

  const { data: resA, isLoading: loadingA, isError: errA, refetch: refetchA } = useBuild(slugA);
  const { data: resB, isLoading: loadingB, isError: errB, refetch: refetchB } = useBuild(slugB);

  if (!slugA || !slugB) return <SelectBuildPrompt />;
  if (loadingA || loadingB) return <CompareSkeleton />;

  if (errA || errB || !resA?.data || !resB?.data) {
    return (
      <ErrorMessage
        title="Could not load builds"
        message="One or both builds could not be found."
        onRetry={() => { refetchA(); refetchB(); }}
      />
    );
  }

  const a = resA.data;
  const b = resB.data;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1
            className="font-display text-4xl font-bold text-forge-amber tracking-wider"
            style={{ textShadow: "0 0 30px rgba(240,160,32,0.30)" }}
          >
            Compare Builds
          </h1>
          <p className="font-body text-base text-forge-muted mt-1.5">
            Side-by-side build analysis
          </p>
        </div>
        <Link to="/builds">
          <Button variant="ghost" size="sm">← Back to Builds</Button>
        </Link>
      </div>

      {/* Build headers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <BuildHeader build={a} side="A" />
        <BuildHeader build={b} side="B" />
      </div>

      {/* Stats comparison */}
      <Panel title="Overview" className="mb-6">
        <CompareRow label="Level" a={a.level} b={b.level} highlight="high" />
        <CompareRow label="Votes" a={a.vote_count} b={b.vote_count} highlight="high" />
        <CompareRow label="Views" a={a.view_count} b={b.view_count} highlight="none" />
        <CompareRow label="Passive Nodes" a={a.passive_tree?.length ?? 0} b={b.passive_tree?.length ?? 0} highlight="none" />
        <CompareRow label="Skills" a={a.skills.length} b={b.skills.length} highlight="none" />
        <CompareRow label="Gear Slots Filled" a={a.gear?.length ?? 0} b={b.gear?.length ?? 0} highlight="high" />
        <CompareRow label="Patch" a={a.patch_version || "—"} b={b.patch_version || "—"} highlight="none" />
      </Panel>

      {/* Flags comparison */}
      <Panel title="Build Flags" className="mb-6">
        <CompareRow
          label="SSF"
          a={a.is_ssf ? "Yes" : "No"}
          b={b.is_ssf ? "Yes" : "No"}
          highlight="none"
        />
        <CompareRow
          label="Hardcore"
          a={a.is_hc ? "Yes" : "No"}
          b={b.is_hc ? "Yes" : "No"}
          highlight="none"
        />
        <CompareRow
          label="Ladder Viable"
          a={a.is_ladder_viable ? "Yes" : "No"}
          b={b.is_ladder_viable ? "Yes" : "No"}
          highlight="none"
        />
        <CompareRow
          label="Budget"
          a={a.is_budget ? "Yes" : "No"}
          b={b.is_budget ? "Yes" : "No"}
          highlight="none"
        />
      </Panel>

      {/* Skills */}
      <div className="mb-6">
        <SkillsCompare a={a} b={b} />
      </div>

      {/* Gear */}
      <div className="mb-6">
        <GearCompare a={a} b={b} />
      </div>

      {/* Descriptions */}
      {(a.description || b.description) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Panel title={`${a.name} — Notes`}>
            <p className="font-body text-sm text-forge-muted leading-relaxed">
              {a.description || <span className="text-forge-dim italic">No description.</span>}
            </p>
          </Panel>
          <Panel title={`${b.name} — Notes`}>
            <p className="font-body text-sm text-forge-muted leading-relaxed">
              {b.description || <span className="text-forge-dim italic">No description.</span>}
            </p>
          </Panel>
        </div>
      )}

      {/* Simulation Comparison */}
      <SimulationComparison slugA={a.slug} slugB={b.slug} />

      {/* Full view links */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
        <Link to={`/build/${a.slug}`}>
          <Button variant="outline" className="w-full">View Full Build: {a.name}</Button>
        </Link>
        <Link to={`/build/${b.slug}`}>
          <Button variant="outline" className="w-full">View Full Build: {b.name}</Button>
        </Link>
      </div>
    </div>
  );
}
