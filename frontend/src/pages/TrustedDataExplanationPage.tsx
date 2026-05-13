import { Link } from "react-router-dom";

import PageMeta from "@/components/PageMeta";
import { V2LimitationNotice } from "@/components/v2/V2LimitationNotice";
import { V2SupportBadge, V2TrustBadge } from "@/components/v2/V2TrustBadge";

const TRUST_SECTIONS = [
  {
    title: "What trusted data means",
    body:
      "Trusted data means EpochForge can trace where the data came from, validate its structure, and show its current support status. It does not mean the data is automatically safe for stat math.",
  },
  {
    title: "Generated data",
    body:
      "Generated means the record came from the v2 export and report pipeline instead of being typed by hand. The pipeline keeps source paths, identifiers, warnings, and validation evidence visible.",
  },
  {
    title: "Validation and provenance",
    body:
      "Validation checks the shape of the data. Provenance explains the source path or generated artifact behind it. These help users inspect the record and understand why EpochForge trusts its identity.",
  },
  {
    title: "Display-only data",
    body:
      "Display-only means the data can be shown for inspection, labels, ownership, and source context, but it is not used for damage, defense, crafting, or build output.",
  },
  {
    title: "Not planner-calculable",
    body:
      "Not planner-calculable means EpochForge will not use this data to change DPS, EHP, recommendations, or build output yet. The planner keeps using existing production calculation paths.",
  },
  {
    title: "Audit-only value normalization",
    body:
      "Audit-only means EpochForge can report whether values are source units, unknown, or otherwise blocked, but it is not safely converting those values into planner math yet.",
  },
  {
    title: "Unsupported mechanics",
    body:
      "Unsupported mechanics are shown instead of guessed. Seeing an unsupported mechanic is a warning that the data exists, not a claim that its gameplay behavior has been solved.",
  },
  {
    title: "Skill identity gaps",
    body:
      "Unresolved or ambiguous skill identity gaps stay visible. EpochForge does not bridge them from display names, nested evidence, or tooltip text.",
  },
  {
    title: "Safe today",
    body:
      "Today, users can rely on v2 trusted data for inspection, source context, support status, provenance, warnings, and debug visibility. It is useful for understanding what exists and what is blocked.",
  },
  {
    title: "Waiting for v3 mechanical intelligence",
    body:
      "v3 work is where value normalization contracts, operation semantics, golden mechanical baselines, and production planner remap decisions belong. v2.5 only makes the current trust state understandable.",
  },
];

export default function TrustedDataExplanationPage() {
  return (
    <div className="mx-auto max-w-6xl space-y-8 p-6">
      <PageMeta
        title="Trusted Data"
        description="Plain-language guide to EpochForge trusted data, display-only status, provenance, and planner calculation limits."
        path="/trusted-data"
      />

      <header className="border-b border-[#2a3050] pb-6">
        <p className="font-mono text-xs uppercase tracking-wide text-[#22d3ee]">
          Trusted Data / v2.5
        </p>
        <h1 className="mt-3 font-display text-3xl text-[#f5a623]">
          Understanding trusted data
        </h1>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-gray-300">
          EpochForge v2 trusted data makes source identity, validation, provenance, and support status visible. Some of that data is ready to display today, but none of it is used to change production planner calculations yet.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <V2TrustBadge status="generated_from_game_data" size="md" />
          <V2TrustBadge status="validated" size="md" />
          <V2TrustBadge status="provenance_available" size="md" />
          <V2SupportBadge status="display_only" size="md" />
          <V2SupportBadge status="not_planner_calculable" size="md" />
        </div>
      </header>

      <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded border border-[#2a3050] bg-[#10152a] p-5">
          <h2 className="text-base font-semibold text-gray-100">The short version</h2>
          <p className="mt-3 text-sm leading-6 text-gray-300">
            Trusted data can be real, sourced, and validated while still being unsafe for mechanical planner use. EpochForge shows that distinction directly so users can inspect data without assuming DPS, EHP, crafting, or build output has changed.
          </p>
          <p className="mt-3 text-sm leading-6 text-gray-300">
            If a record is display-only, audit-only, unsupported, or not planner-calculable, it remains visible for explanation and review. It does not power production stat math.
          </p>
        </div>

        <V2LimitationNotice
          codes={[
            "display_only",
            "audit_only_value_normalization",
            "not_planner_calculable",
            "unsupported_mechanics",
            "unresolved_skill_identity",
            "production_not_consuming_v2",
          ]}
          mode="full"
        />
      </section>

      <section className="grid gap-3 md:grid-cols-2">
        {TRUST_SECTIONS.map((section) => (
          <article key={section.title} className="rounded border border-[#2a3050] bg-[#10152a] p-4">
            <h2 className="text-sm font-semibold text-gray-100">{section.title}</h2>
            <p className="mt-2 text-sm leading-6 text-gray-300">{section.body}</p>
          </article>
        ))}
      </section>

      <section className="rounded border border-amber-400/20 bg-amber-500/5 p-5">
        <h2 className="text-base font-semibold text-amber-100">What this does not mean</h2>
        <ul className="mt-3 space-y-2 text-sm leading-6 text-amber-100/90">
          <li>Trusted data does not mean DPS or EHP is more accurate by itself.</li>
          <li>Validated structure does not mean unsupported mechanics are solved.</li>
          <li>Audit-only value normalization does not mean source-unit values are converted.</li>
          <li>Visible skill identity gaps do not mean bridges have been inferred.</li>
          <li>v2 debug visibility does not mean production planner consumption is enabled.</li>
        </ul>
      </section>

      <section className="rounded border border-[#2a3050] bg-[#10152a] p-5">
        <h2 className="text-base font-semibold text-gray-100">Where to inspect the data</h2>
        <p className="mt-2 text-sm leading-6 text-gray-300">
          Developer debug pages expose the current v2 trusted-data envelopes, warnings, provenance, and blocked reasons.
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link
            to="/debug/v2-stats-modifiers"
            className="rounded border border-[#2a3050] px-4 py-2 text-sm text-gray-200 no-underline hover:border-[#f5a623]"
          >
            Open stats/modifiers debug
          </Link>
          <Link
            to="/debug/forge-safe-affixes"
            className="rounded border border-[#2a3050] px-4 py-2 text-sm text-gray-200 no-underline hover:border-[#f5a623]"
          >
            Open affix debug
          </Link>
        </div>
      </section>
    </div>
  );
}
