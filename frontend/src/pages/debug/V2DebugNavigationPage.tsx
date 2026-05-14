import { Link } from "react-router-dom";

import PageMeta from "@/components/PageMeta";
import { V2LimitationNotice } from "@/components/v2/V2LimitationNotice";
import { V2SupportBadge } from "@/components/v2/V2TrustBadge";

const DEBUG_LINKS = [
  {
    title: "Support Matrix",
    path: "/trusted-data/support",
    label: "User-facing guide",
    description: "Compact support overview for trusted-data domains and planner calculation limits.",
    statuses: ["Display Only", "Not Planner-Calculable"],
  },
  {
    title: "Trusted Data Explanation",
    path: "/trusted-data",
    label: "User-facing guide",
    description: "Plain-language meaning for trust, provenance, display-only data, and planner limits.",
    statuses: ["Display Only", "Not Planner-Calculable"],
  },
  {
    title: "Stats / Modifiers",
    path: "/debug/v2-stats-modifiers",
    label: "Read-only debug",
    description: "Registry counts, blocked reasons, value scale status, and planner adapter status.",
    statuses: ["Audit Only", "Not Planner-Calculable"],
  },
  {
    title: "Forge-Safe Affixes",
    path: "/debug/forge-safe-affixes",
    label: "Read-only debug",
    description: "Affix metadata, support summaries, provenance, and modifier visibility.",
    statuses: ["Display Only", "Partial Support"],
  },
  {
    title: "Items",
    path: "/debug/v2-items",
    label: "Read-only debug",
    description: "Item/base trusted-data envelopes, provenance, and display metadata.",
    statuses: ["Display Only", "Partial Support"],
  },
  {
    title: "Uniques / Sets",
    path: "/debug/v2-unique-sets",
    label: "Read-only debug",
    description: "Unique and set records with unsupported mechanics kept visible.",
    statuses: ["Display Only", "Unsupported Visible"],
  },
  {
    title: "Idols",
    path: "/debug/v2-idols",
    label: "Read-only debug",
    description: "Idol base and affix metadata for inspection without planner calculation use.",
    statuses: ["Display Only", "Audit Only"],
  },
  {
    title: "Classes / Masteries",
    path: "/debug/v2-classes",
    label: "Read-only debug",
    description: "Class and mastery metadata with provenance and support context.",
    statuses: ["Display Only"],
  },
  {
    title: "Passives",
    path: "/debug/v2-passives",
    label: "Read-only debug",
    description: "Passive identity and tree metadata while passive effects remain non-calculating.",
    statuses: ["Identity Only", "Not Planner-Calculable"],
  },
  {
    title: "Skills",
    path: "/debug/v2-skills",
    label: "Read-only debug",
    description: "Skill identity and tree metadata with unresolved identity gaps left visible.",
    statuses: ["Identity Only", "Unbridged"],
  },
];

export default function V2DebugNavigationPage() {
  return (
    <div className="mx-auto max-w-6xl space-y-6 p-6">
      <PageMeta
        title="v2 Debug Navigation"
        description="Read-only trusted-data debug and report navigation for EpochForge v2 and v2.5 surfaces."
        path="/debug/v2"
      />

      <header className="border-b border-[#2a3050] pb-5">
        <p className="font-mono text-xs uppercase tracking-wide text-[#22d3ee]">
          Debug / Trusted Data
        </p>
        <h1 className="mt-2 font-display text-2xl text-[#f5a623]">
          v2 trusted-data debug pages
        </h1>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-gray-300">
          These pages are read-only inspection surfaces for trusted-data status, provenance, warnings, and blocked reasons. They do not power production planner calculations.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <V2SupportBadge status="experimental" size="md" />
          <V2SupportBadge status="display_only" size="md" />
          <V2SupportBadge status="not_planner_calculable" size="md" />
        </div>
      </header>

      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {DEBUG_LINKS.map((link) => (
          <Link
            key={link.path}
            to={link.path}
            className="rounded border border-[#2a3050] bg-[#10152a] p-4 text-gray-200 no-underline transition hover:border-[#f5a623]"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="text-sm font-semibold text-gray-100">{link.title}</h2>
                <p className="mt-1 font-mono text-[11px] uppercase text-[#22d3ee]">{link.label}</p>
              </div>
              <span className="text-sm text-[#f5a623]">Open</span>
            </div>
            <p className="mt-3 text-sm leading-6 text-gray-300">{link.description}</p>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {link.statuses.map((status) => (
                <span key={status} className="rounded border border-[#2a3050] px-1.5 py-0.5 text-[10px] text-gray-300">
                  {status}
                </span>
              ))}
            </div>
          </Link>
        ))}
      </section>

      <section className="grid gap-3 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded border border-[#2a3050] bg-[#10152a] p-4">
          <h2 className="text-sm font-semibold text-gray-100">Route notes</h2>
          <p className="mt-2 text-sm leading-6 text-gray-300">
            The canonical affix debug page is <span className="font-mono text-gray-100">/debug/forge-safe-affixes</span>. The legacy shorthand <span className="font-mono text-gray-100">/debug/v2-affixes</span> redirects there.
          </p>
        </div>
        <V2LimitationNotice
          codes={[
            "experimental_only",
            "display_only",
            "not_planner_calculable",
            "production_not_consuming_v2",
          ]}
          mode="full"
        />
      </section>
    </div>
  );
}
