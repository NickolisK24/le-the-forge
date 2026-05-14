import { Link } from "react-router-dom";

import PageMeta from "@/components/PageMeta";
import { V2LimitationNotice } from "@/components/v2/V2LimitationNotice";
import { V2SupportBadge, V2TrustBadge } from "@/components/v2/V2TrustBadge";

const SUPPORT_ROWS = [
  {
    domain: "Items / item bases",
    status: "Display metadata",
    safeToday: "Names, categories, requirements, source paths, and provenance can be shown for inspection.",
    displayOnly: "Item/base metadata and implicit references stay display-only.",
    blockers: "Implicit and modifier values are not planner-calculable.",
    nextTrack: "v2.5 UX",
  },
  {
    domain: "Affixes",
    status: "Display / provenance",
    safeToday: "Affix identities, tier summaries, applicability, warnings, and provenance can be inspected.",
    displayOnly: "Tier and modifier links are visible as provenance, not stat math.",
    blockers: "Modifier values remain blocked by audit-only value normalization.",
    nextTrack: "v3 mechanics",
  },
  {
    domain: "Unique/set items",
    status: "Partial / unsupported visible",
    safeToday: "Records, names, support status, and unsupported mechanics can be shown honestly.",
    displayOnly: "Unsupported or scripted mechanics stay visible for review.",
    blockers: "Unsupported mechanics are not inferred from text.",
    nextTrack: "v3 mechanics",
  },
  {
    domain: "Idols",
    status: "Display metadata",
    safeToday: "Idol shape, identity, source context, and affix provenance can be inspected.",
    displayOnly: "Idol metadata is visible without changing planner math.",
    blockers: "Source-unit values and altar-specific behavior remain blocked.",
    nextTrack: "v3 mechanics",
  },
  {
    domain: "Classes/masteries",
    status: "Trusted metadata",
    safeToday: "Class and mastery identities can be shown with source context.",
    displayOnly: "Ownership and label metadata are display-safe.",
    blockers: "Skill ownership gaps still limit mechanical use.",
    nextTrack: "v2.5 UX",
  },
  {
    domain: "Passive trees",
    status: "Identity only",
    safeToday: "Passive tree identity, class/mastery ownership, and source paths can be inspected.",
    displayOnly: "Tree and node identity are visible without applying passive effects.",
    blockers: "Passive effects are not planner-calculable yet.",
    nextTrack: "v3 mechanics",
  },
  {
    domain: "Skills / skill trees",
    status: "Identity only",
    safeToday: "Skill identity and tree metadata can be inspected while identity gaps remain visible.",
    displayOnly: "Skill tree links are provenance and identity information only.",
    blockers: "Unresolved and ambiguous skill identity refs are unbridged.",
    nextTrack: "v3 mechanics",
  },
  {
    domain: "Stats",
    status: "Audit / registry",
    safeToday: "Stat registry entries can be counted and inspected for debug context.",
    displayOnly: "Stat identities are shown for audit and report navigation.",
    blockers: "Stat identity gaps and unsupported mechanics remain blocked.",
    nextTrack: "v3 mechanics",
  },
  {
    domain: "Modifiers",
    status: "Audit only",
    safeToday: "Modifier rows, operation distribution, value scale status, and blocked reasons can be inspected.",
    displayOnly: "Modifier values are visible for audit/debug only.",
    blockers: "Value normalization is audit-only; source-unit and unknown scales remain blocked.",
    nextTrack: "v3 mechanics",
  },
  {
    domain: "Planner adapter",
    status: "Read-only disabled",
    safeToday: "The adapter can explain visible records, blocked reasons, and baseline readiness.",
    displayOnly: "Adapter context is diagnostic-only and disabled by default.",
    blockers: "Planner-calculable and stable-calculable counts remain 0.",
    nextTrack: "future patch-resilience",
  },
];

export default function TrustedDataSupportMatrixPage() {
  return (
    <div className="mx-auto max-w-7xl space-y-6 p-6">
      <PageMeta
        title="Trusted Data Support Matrix"
        description="User-facing support matrix for EpochForge trusted data domains and planner calculation limits."
        path="/trusted-data/support"
      />

      <header className="border-b border-[#2a3050] pb-5">
        <p className="font-mono text-xs uppercase tracking-wide text-[#22d3ee]">
          Trusted Data / Support Matrix
        </p>
        <h1 className="mt-2 font-display text-3xl text-[#f5a623]">
          What EpochForge can safely show today
        </h1>
        <p className="mt-3 max-w-4xl text-sm leading-6 text-gray-300">
          This matrix separates trusted visibility from planner calculation support. v2 data can be sourced, validated, and useful for inspection while still being blocked from DPS, EHP, crafting, and build output.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <V2TrustBadge status="validated" size="md" />
          <V2TrustBadge status="provenance_available" size="md" />
          <V2SupportBadge status="display_only" size="md" />
          <V2SupportBadge status="audit_only" size="md" />
          <V2SupportBadge status="not_planner_calculable" size="md" />
        </div>
      </header>

      <section className="rounded border border-amber-400/20 bg-amber-500/5 p-4">
        <h2 className="text-sm font-semibold text-amber-100">Global planner safety status</h2>
        <p className="mt-2 text-sm leading-6 text-amber-100/90">
          Production planner consumption is false. Planner-calculable count is 0. Stable-calculable count is 0. Value normalization is audit-only. Skill identity bridge status is unbridged.
        </p>
      </section>

      <section className="overflow-hidden rounded border border-[#2a3050]">
        <div className="grid grid-cols-[1fr_1fr_1.5fr_1.5fr_1.5fr_1fr] bg-[#10152a] text-xs font-semibold uppercase text-gray-400">
          <div className="border-r border-[#2a3050] p-3">Domain</div>
          <div className="border-r border-[#2a3050] p-3">Status</div>
          <div className="border-r border-[#2a3050] p-3">Safe today</div>
          <div className="border-r border-[#2a3050] p-3">Display-only use</div>
          <div className="border-r border-[#2a3050] p-3">Primary blockers</div>
          <div className="p-3">Next track</div>
        </div>
        {SUPPORT_ROWS.map((row) => (
          <article key={row.domain} className="grid grid-cols-[1fr_1fr_1.5fr_1.5fr_1.5fr_1fr] border-t border-[#2a3050] bg-[#0f172a] text-sm text-gray-300">
            <div className="border-r border-[#2a3050] p-3 font-semibold text-gray-100">{row.domain}</div>
            <div className="border-r border-[#2a3050] p-3">{row.status}</div>
            <div className="border-r border-[#2a3050] p-3 leading-6">{row.safeToday}</div>
            <div className="border-r border-[#2a3050] p-3 leading-6">{row.displayOnly}</div>
            <div className="border-r border-[#2a3050] p-3 leading-6">{row.blockers}</div>
            <div className="p-3 font-mono text-xs text-[#22d3ee]">{row.nextTrack}</div>
          </article>
        ))}
      </section>

      <section className="grid gap-3 lg:grid-cols-[1fr_1fr]">
        <V2LimitationNotice
          codes={[
            "display_only",
            "audit_only_value_normalization",
            "not_planner_calculable",
            "unresolved_skill_identity",
            "production_not_consuming_v2",
          ]}
          mode="full"
        />
        <div className="rounded border border-[#2a3050] bg-[#10152a] p-4">
          <h2 className="text-sm font-semibold text-gray-100">Related pages</h2>
          <div className="mt-3 flex flex-wrap gap-3">
            <Link className="rounded border border-[#2a3050] px-3 py-2 text-sm text-gray-200 no-underline hover:border-[#f5a623]" to="/trusted-data">
              Trusted data guide
            </Link>
            <Link className="rounded border border-[#2a3050] px-3 py-2 text-sm text-gray-200 no-underline hover:border-[#f5a623]" to="/debug/v2">
              v2 debug index
            </Link>
            <Link className="rounded border border-[#2a3050] px-3 py-2 text-sm text-gray-200 no-underline hover:border-[#f5a623]" to="/debug/v2-stats-modifiers">
              Stats/modifiers debug
            </Link>
            <Link className="rounded border border-[#2a3050] px-3 py-2 text-sm text-gray-200 no-underline hover:border-[#f5a623]" to="/trusted-data/pre-v3-readiness">
              Pre-v3 readiness
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
