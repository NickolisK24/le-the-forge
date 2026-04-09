/**
 * ReportPage — shareable read-only build summary.
 *
 * Route: /report/:slug
 * Sets OpenGraph meta tags for Discord unfurling.
 */

import { useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { reportApi } from "@/lib/api";
import { Panel, Spinner, ErrorMessage, Button } from "@/components/ui";
import { CLASS_COLORS } from "@/lib/gameData";
import type { BuildReport, CharacterClass } from "@/types";

const TIER_COLORS: Record<string, string> = {
  S: "#f5d060",
  A: "#3dca74",
  B: "#f0a020",
  C: "#8890b8",
};

function useDocumentMeta(report: BuildReport | null | undefined) {
  useEffect(() => {
    if (!report) return;

    document.title = report.og_title;

    const setMeta = (property: string, content: string) => {
      let tag = document.querySelector(`meta[property="${property}"]`);
      if (!tag) {
        tag = document.createElement("meta");
        tag.setAttribute("property", property);
        document.head.appendChild(tag);
      }
      tag.setAttribute("content", content);
    };

    setMeta("og:title", report.og_title);
    setMeta("og:description", report.og_description);
    setMeta("og:url", report.og_url);
    setMeta("og:type", "website");

    return () => {
      document.title = "The Forge";
    };
  }, [report]);
}

function StatSummaryCard({ stats }: { stats: Record<string, number> }) {
  const keyStats = [
    ["base_damage", "Base Damage"],
    ["attack_speed", "Attack Speed"],
    ["crit_chance", "Crit Chance"],
    ["crit_multiplier", "Crit Multiplier"],
    ["max_health", "Max Health"],
    ["armour", "Armour"],
    ["dodge_rating", "Dodge Rating"],
  ] as const;

  return (
    <Panel title="Stat Summary">
      <div className="grid grid-cols-2 gap-x-6 gap-y-1">
        {keyStats.map(([key, label]) => {
          const val = stats[key];
          if (val === undefined || val === 0) return null;
          return (
            <div key={key} className="flex justify-between py-1 border-b border-forge-border/20">
              <span className="font-mono text-xs text-forge-muted">{label}</span>
              <span className="font-mono text-xs text-forge-text tabular-nums">
                {typeof val === "number" ? val.toLocaleString(undefined, { maximumFractionDigits: 1 }) : val}
              </span>
            </div>
          );
        })}
      </div>
    </Panel>
  );
}

function DPSSummaryCard({ dps }: { dps: BuildReport["dps_summary"] }) {
  return (
    <Panel title="DPS Summary">
      <div className="space-y-1">
        {[
          ["Total DPS", dps.total_dps],
          ["Raw DPS", dps.raw_dps],
          ["Hit Damage", dps.hit_damage],
          ["Average Hit", dps.average_hit],
          ["Crit Contribution", `${dps.crit_contribution_pct.toFixed(1)}%`],
          ["Ailment DPS", dps.ailment_dps],
        ].map(([label, val]) => (
          <div key={label as string} className="flex justify-between py-1 border-b border-forge-border/20">
            <span className="font-mono text-xs text-forge-muted">{label}</span>
            <span className="font-mono text-xs text-forge-text tabular-nums">
              {typeof val === "number" ? val.toLocaleString(undefined, { maximumFractionDigits: 0 }) : val}
            </span>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function EHPSummaryCard({ ehp }: { ehp: BuildReport["ehp_summary"] }) {
  return (
    <Panel title="EHP Summary">
      <div className="space-y-1">
        {[
          ["Effective HP", ehp.effective_hp],
          ["Max Health", ehp.max_health],
          ["Armor Reduction", `${ehp.armor_reduction_pct.toFixed(1)}%`],
          ["Avg Resistance", `${ehp.avg_resistance.toFixed(1)}%`],
          ["Survivability", `${ehp.survivability_score}/100`],
          ["Dodge Chance", `${ehp.dodge_chance_pct.toFixed(1)}%`],
          ["Block Chance", `${ehp.block_chance_pct.toFixed(1)}%`],
        ].map(([label, val]) => (
          <div key={label as string} className="flex justify-between py-1 border-b border-forge-border/20">
            <span className="font-mono text-xs text-forge-muted">{label}</span>
            <span className="font-mono text-xs text-forge-text tabular-nums">
              {typeof val === "number" ? val.toLocaleString(undefined, { maximumFractionDigits: 0 }) : val}
            </span>
          </div>
        ))}
      </div>
    </Panel>
  );
}

export default function ReportPage() {
  const { slug } = useParams<{ slug: string }>();

  const { data: res, isLoading, isError } = useQuery({
    queryKey: ["report", slug],
    queryFn: () => reportApi.get(slug!),
    enabled: Boolean(slug),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  const report = res?.data ?? null;
  useDocumentMeta(report);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <Spinner size={32} />
      </div>
    );
  }

  if (isError || !report) {
    return (
      <div className="mx-auto max-w-2xl py-16">
        <ErrorMessage
          title="Build not found"
          message="This build doesn't exist or is private."
        />
      </div>
    );
  }

  const { identity } = report;
  const classColor = CLASS_COLORS[identity.character_class as CharacterClass] ?? "#8890b8";

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 space-y-6">
      {/* Header */}
      <div className="rounded border border-forge-border bg-forge-surface overflow-hidden">
        <div className="h-1.5 w-full" style={{ background: classColor, boxShadow: `0 0 12px ${classColor}60` }} />
        <div className="p-6">
          <h1 className="font-display text-2xl font-bold text-forge-text mb-2">{identity.name}</h1>
          <div className="flex flex-wrap items-center gap-2">
            <span
              className="font-mono text-xs uppercase tracking-widest px-2 py-0.5 border rounded-sm"
              style={{ color: classColor, borderColor: `${classColor}50`, background: `${classColor}10` }}
            >
              {identity.character_class}
            </span>
            <span className="font-mono text-xs text-forge-muted border border-forge-border px-2 py-0.5 rounded-sm">
              {identity.mastery}
            </span>
            <span className="font-mono text-xs text-forge-dim">
              Lv. {identity.level} | Patch {identity.patch_version}
            </span>
          </div>
          {identity.author && (
            <div className="font-mono text-[11px] text-forge-dim mt-2">
              by {identity.author}
            </div>
          )}
        </div>
      </div>

      {/* Stat summary */}
      <StatSummaryCard stats={report.stat_summary} />

      {/* DPS + EHP side by side */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <DPSSummaryCard dps={report.dps_summary} />
        <EHPSummaryCard ehp={report.ehp_summary} />
      </div>

      {/* Top 3 upgrades */}
      {report.top_upgrades.length > 0 && (
        <Panel title="Top Upgrade Recommendations">
          <div className="space-y-2">
            {report.top_upgrades.map((u, i) => (
              <div key={i} className="flex items-start gap-3 py-2 border-b border-forge-border/20 last:border-b-0">
                <span className="font-display text-sm font-bold text-forge-amber w-5 text-center shrink-0">
                  {i + 1}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="font-body text-sm text-forge-text">{u.label}</div>
                  <div className="font-mono text-[10px] text-forge-dim">
                    DPS: +{u.dps_gain_pct.toFixed(1)}% | EHP: +{u.ehp_gain_pct.toFixed(1)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      )}

      {/* Skills */}
      <Panel title="Skills">
        {report.skills.length === 0 ? (
          <p className="font-mono text-xs text-forge-dim text-center py-4">No skills configured</p>
        ) : (
          <div className="space-y-1">
            {report.skills.map((s) => (
              <div key={s.slot} className="flex justify-between py-1.5 border-b border-forge-border/20 last:border-b-0">
                <span className="font-body text-sm text-forge-text">{s.skill_name}</span>
                <span className="font-mono text-[11px] text-forge-dim">
                  {s.points_allocated}pts | {s.node_count} nodes
                </span>
              </div>
            ))}
          </div>
        )}
      </Panel>

      {/* Gear */}
      <Panel title="Gear">
        {report.gear.length === 0 ? (
          <p className="font-mono text-xs text-forge-dim text-center py-4">No gear configured</p>
        ) : (
          <div className="space-y-1">
            {report.gear.map((g, i) => (
              <div key={i} className="flex justify-between py-1.5 border-b border-forge-border/20 last:border-b-0">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim w-16">
                    {g.slot}
                  </span>
                  <span className="font-body text-sm text-forge-text">
                    {g.item_name || "Empty"}
                  </span>
                </div>
                <div className="font-mono text-[11px] text-forge-dim">
                  {g.rarity && <span className="mr-2">{g.rarity}</span>}
                  {g.affix_count > 0 && <span>{g.affix_count} affixes</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </Panel>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-forge-border/30">
        <span className="font-mono text-[10px] text-forge-dim">
          Generated {new Date(report.generated_at).toLocaleString()}
        </span>
        <Link to={`/build/${identity.slug}`}>
          <Button variant="primary" size="sm">Plan this build</Button>
        </Link>
      </div>
    </div>
  );
}
