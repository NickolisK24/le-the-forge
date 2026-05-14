import { Link } from "react-router-dom";

import PageMeta from "@/components/PageMeta";
import { V2LimitationNotice } from "@/components/v2/V2LimitationNotice";
import { V2SupportBadge, V2TrustBadge } from "@/components/v2/V2TrustBadge";

const READINESS_CARDS = [
  { label: "v2 Infrastructure", value: "Ready", tone: "ready" },
  { label: "Production Planner", value: "Not Ready", tone: "blocked" },
  { label: "Mechanical Remap", value: "Not Ready", tone: "blocked" },
  { label: "Planner-Calculable Records", value: "0", tone: "blocked" },
  { label: "Stable-Calculable Records", value: "0", tone: "blocked" },
  { label: "Value Normalization", value: "Audit Only", tone: "caution" },
  { label: "Skill Identity Bridge", value: "Unbridged", tone: "caution" },
  { label: "Golden Baselines", value: "Planned / Partial Scaffold", tone: "caution" },
  { label: "Experimental Adapter Mode", value: "Disabled by Default", tone: "caution" },
];

const BLOCKER_SECTIONS = [
  {
    title: "Value normalization blockers",
    body:
      "Mechanical readiness is blocked because source-unit and unknown value scales are visible but not proven safe for planner math. There are 6,248 source-unit values and 13,150 unknown value scales in the current dry-run summary.",
  },
  {
    title: "Operation semantics blockers",
    body:
      "Modifier operations must have deterministic semantics before they can affect stat aggregation. Unknown or conditional operation behavior remains diagnostic-only.",
  },
  {
    title: "Stat identity blockers",
    body:
      "Stat and modifier identities must resolve consistently before any adapter row can become a production calculation input.",
  },
  {
    title: "Skill identity blockers",
    body:
      "Skill identity gaps are shown honestly and are not bridged by guessing. The bridge remains unbridged until source evidence and policy make it safe.",
  },
  {
    title: "Unsupported/scripted/text-only blockers",
    body:
      "Unsupported, scripted, and text-only mechanics remain visible as limitations. They are not inferred from tooltip text or treated as solved behavior.",
  },
  {
    title: "Golden baseline requirements",
    body:
      "Golden baselines are required before any future remap can be trusted. Existing scaffold work identifies 7 safe-now fixtures and 6 blocked fixtures, but mechanical baselines are not complete.",
  },
];

const COMPLETED_ITEMS = [
  "Trusted bundles, provenance, support status, and warnings are visible.",
  "Debug pages explain audit-only and display-only status without changing planner output.",
  "Stats/modifiers are inspectable with blocked reasons and value scale counts.",
  "Planner adapter context is read-only and disabled by default.",
  "Support matrix and trusted-data copy explain what belongs to v2.5 versus v3.",
];

const V3_PROOF_ITEMS = [
  "Explicit value scale contracts for source-unit and unknown values.",
  "Operation semantics for additive, flat, increased, more, conditional, and scripted cases.",
  "Resolved stat identity coverage with blocked fallbacks for unknown identities.",
  "Skill identity bridge policy backed by source evidence, not names or tooltip text.",
  "Golden planner, crafting, passive, skill, item, and modifier output baselines.",
  "Dry-run comparison snapshots that explain accepted and blocked deltas before production remap.",
];

export default function PreV3MechanicalReadinessPage() {
  return (
    <div className="mx-auto max-w-7xl space-y-6 p-6">
      <PageMeta
        title="Pre-v3 Mechanical Readiness"
        description="Readiness dashboard for the blockers that must be solved before trusted v2 data can affect planner math."
        path="/trusted-data/pre-v3-readiness"
      />

      <header className="border-b border-[#2a3050] pb-5">
        <p className="font-mono text-xs uppercase tracking-wide text-[#22d3ee]">
          Trusted Data / Pre-v3 Readiness
        </p>
        <h1 className="mt-2 font-display text-3xl text-[#f5a623]">
          Mechanical readiness before v3
        </h1>
        <p className="mt-3 max-w-4xl text-sm leading-6 text-gray-300">
          EpochForge can inspect this data today, but it will not use it to change build output yet. This dashboard summarizes what must be proven before trusted data can become mechanical planner input.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <V2TrustBadge status="validated" size="md" />
          <V2SupportBadge status="display_only" size="md" />
          <V2SupportBadge status="audit_only" size="md" />
          <V2SupportBadge status="not_planner_calculable" size="md" />
        </div>
      </header>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {READINESS_CARDS.map((card) => (
          <article key={card.label} className={`rounded border p-4 ${cardClass(card.tone)}`}>
            <div className="text-xs uppercase text-gray-500">{card.label}</div>
            <div className="mt-2 font-mono text-lg text-gray-100">{card.value}</div>
          </article>
        ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-[1fr_1fr]">
        <div className="rounded border border-[#2a3050] bg-[#10152a] p-4">
          <h2 className="text-base font-semibold text-gray-100">What is already complete</h2>
          <ul className="mt-3 space-y-2 text-sm leading-6 text-gray-300">
            {COMPLETED_ITEMS.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className="rounded border border-amber-400/20 bg-amber-500/5 p-4">
          <h2 className="text-base font-semibold text-amber-100">Current readiness decision</h2>
          <p className="mt-3 text-sm leading-6 text-amber-100/90">
            v2 infrastructure is ready. Production planner readiness is false. Mechanical remap readiness is false. Production consumed is false.
          </p>
          <p className="mt-2 text-sm leading-6 text-amber-100/90">
            Modifier rows inspected: 19,398. Blocked modifier records: 19,398. Planner-calculable and stable-calculable records remain 0.
          </p>
        </div>
      </section>

      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {BLOCKER_SECTIONS.map((section) => (
          <article key={section.title} className="rounded border border-[#2a3050] bg-[#10152a] p-4">
            <h2 className="text-sm font-semibold text-gray-100">{section.title}</h2>
            <p className="mt-2 text-sm leading-6 text-gray-300">{section.body}</p>
          </article>
        ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-[1fr_1fr]">
        <div className="rounded border border-[#2a3050] bg-[#10152a] p-4">
          <h2 className="text-base font-semibold text-gray-100">What v3 must prove</h2>
          <ul className="mt-3 space-y-2 text-sm leading-6 text-gray-300">
            {V3_PROOF_ITEMS.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <V2LimitationNotice
          codes={[
            "audit_only_value_normalization",
            "not_planner_calculable",
            "unresolved_skill_identity",
            "stable_calculable_unavailable",
            "production_not_consuming_v2",
          ]}
          mode="full"
        />
      </section>

      <section className="rounded border border-[#2a3050] bg-[#10152a] p-4">
        <h2 className="text-sm font-semibold text-gray-100">Related pages</h2>
        <div className="mt-3 flex flex-wrap gap-3">
          <Link className="rounded border border-[#2a3050] px-3 py-2 text-sm text-gray-200 no-underline hover:border-[#f5a623]" to="/trusted-data">
            Trusted data guide
          </Link>
          <Link className="rounded border border-[#2a3050] px-3 py-2 text-sm text-gray-200 no-underline hover:border-[#f5a623]" to="/trusted-data/support">
            Support matrix
          </Link>
          <Link className="rounded border border-[#2a3050] px-3 py-2 text-sm text-gray-200 no-underline hover:border-[#f5a623]" to="/debug/v2">
            v2 debug index
          </Link>
        </div>
      </section>
    </div>
  );
}

function cardClass(tone: string): string {
  if (tone === "ready") return "border-emerald-400/30 bg-emerald-500/10";
  if (tone === "blocked") return "border-red-400/30 bg-red-500/10";
  return "border-amber-400/20 bg-amber-500/5";
}
