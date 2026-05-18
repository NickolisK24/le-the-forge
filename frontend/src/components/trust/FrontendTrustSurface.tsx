import type {
  FrontendTrustSurfaceData,
  TrustDiagnosticsSummaryData,
  TrustEvidencePanelData,
  TrustExplanationPanelData,
  TrustMetricSummaryData,
  TrustProvenanceLineageData,
  TrustStatusCardData,
  TrustSurfaceBadgeDefinition,
  TrustSurfaceSupportStatus,
} from "@/types/frontendTrustSurface";
import {
  getFrontendTrustSurfaceData,
  getSupportBadgeDefinition,
} from "@/lib/frontendTrustSurfaceData";

const badgeToneClasses: Record<TrustSurfaceBadgeDefinition["tone"], string> = {
  green: "border-emerald-400/40 bg-emerald-500/10 text-emerald-100",
  blue: "border-sky-400/40 bg-sky-500/10 text-sky-100",
  amber: "border-amber-400/40 bg-amber-500/10 text-amber-100",
  red: "border-rose-400/40 bg-rose-500/10 text-rose-100",
  purple: "border-violet-400/40 bg-violet-500/10 text-violet-100",
  gray: "border-gray-400/40 bg-gray-500/10 text-gray-100",
  slate: "border-slate-400/40 bg-slate-500/10 text-slate-100",
};

const diagnosticToneClasses: Record<TrustDiagnosticsSummaryData["state"], string> = {
  warning: "border-amber-400/30 bg-amber-500/10 text-amber-100",
  blocker: "border-rose-400/30 bg-rose-500/10 text-rose-100",
  unsupported: "border-violet-400/30 bg-violet-500/10 text-violet-100",
  gap: "border-sky-400/30 bg-sky-500/10 text-sky-100",
};

function ordered<T extends { deterministicOrder: number }>(items: readonly T[]): readonly T[] {
  return [...items].sort((left, right) => left.deterministicOrder - right.deterministicOrder);
}

export function SupportStatusBadge({
  status,
  className = "",
}: {
  status: TrustSurfaceSupportStatus;
  className?: string;
}) {
  const badge = getSupportBadgeDefinition(status);
  return (
    <span
      className={`inline-flex items-center rounded border px-2.5 py-1 text-xs font-semibold ${badgeToneClasses[badge.tone]} ${className}`}
      title={badge.description}
      data-read-only="true"
      data-descriptive-only="true"
    >
      {badge.label}
    </span>
  );
}

function SectionHeading({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-wide text-[#22d3ee]">{eyebrow}</p>
      <h2 className="mt-2 text-xl font-semibold text-gray-100">{title}</h2>
    </div>
  );
}

export function TrustStatusCard({ card }: { card: TrustStatusCardData }) {
  return (
    <article
      className="rounded border border-[#2a3050] bg-[#10152a] p-4"
      data-read-only={card.readOnly}
      data-descriptive-only={card.descriptiveOnly}
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <h3 className="text-sm font-semibold text-gray-100">{card.title}</h3>
        <SupportStatusBadge status={card.status} />
      </div>
      <p className="mt-3 text-sm leading-6 text-gray-300">{card.summary}</p>
      <p className="mt-3 rounded border border-amber-400/20 bg-amber-500/5 p-3 text-xs leading-5 text-amber-100">
        {card.limitation}
      </p>
    </article>
  );
}

export function ExplainabilityPanel({ panel }: { panel: TrustExplanationPanelData }) {
  return (
    <details
      className="rounded border border-[#2a3050] bg-[#10152a] p-4"
      data-read-only={panel.readOnly}
      data-descriptive-only={panel.descriptiveOnly}
    >
      <summary className="cursor-pointer text-sm font-semibold text-gray-100">
        {panel.title}
      </summary>
      <p className="mt-3 text-sm leading-6 text-gray-300">{panel.summary}</p>
      <ul className="mt-3 space-y-2 text-sm leading-6 text-gray-300">
        {panel.details.map((detail) => (
          <li key={detail}>{detail}</li>
        ))}
      </ul>
    </details>
  );
}

export function EvidencePanel({ panel }: { panel: TrustEvidencePanelData }) {
  return (
    <article
      className="rounded border border-[#2a3050] bg-[#10152a] p-4"
      data-read-only={panel.readOnly}
      data-descriptive-only={panel.descriptiveOnly}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-semibold text-gray-100">{panel.title}</h3>
        <span className="rounded border border-[#33415f] px-2 py-1 font-mono text-[11px] uppercase text-gray-300">
          {panel.group.replace("_", " ")}
        </span>
      </div>
      <div className="mt-4 space-y-3">
        {panel.items.map((item) => (
          <div
            key={item.id}
            className="rounded border border-[#24304f] bg-[#0c1124] p-3"
            data-read-only={item.readOnly}
            data-descriptive-only={item.descriptiveOnly}
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm font-medium text-gray-100">{item.label}</p>
              <span className="rounded border border-[#33415f] px-2 py-1 font-mono text-[11px] uppercase text-gray-300">
                {item.freshness}
              </span>
            </div>
            <dl className="mt-3 grid gap-2 text-xs leading-5 text-gray-300">
              <div>
                <dt className="font-semibold text-gray-100">Source</dt>
                <dd>{item.source}</dd>
              </div>
              <div>
                <dt className="font-semibold text-gray-100">Provenance</dt>
                <dd>{item.provenance}</dd>
              </div>
              <div>
                <dt className="font-semibold text-gray-100">Lineage</dt>
                <dd>{item.lineage}</dd>
              </div>
            </dl>
          </div>
        ))}
      </div>
    </article>
  );
}

export function ProvenanceLineagePanel({ panel }: { panel: TrustProvenanceLineageData }) {
  return (
    <article
      className="rounded border border-[#2a3050] bg-[#10152a] p-4"
      data-read-only={panel.readOnly}
      data-descriptive-only={panel.descriptiveOnly}
    >
      <h3 className="text-sm font-semibold text-gray-100">{panel.title}</h3>
      <dl className="mt-3 grid gap-2 text-xs leading-5 text-gray-300">
        <div>
          <dt className="font-semibold text-gray-100">Source reference</dt>
          <dd>{panel.sourceReference}</dd>
        </div>
        <div>
          <dt className="font-semibold text-gray-100">Evidence origin</dt>
          <dd>{panel.evidenceOrigin}</dd>
        </div>
        <div className="grid gap-2 sm:grid-cols-2">
          <div>
            <dt className="font-semibold text-gray-100">Provenance state</dt>
            <dd>{panel.provenanceState}</dd>
          </div>
          <div>
            <dt className="font-semibold text-gray-100">Lineage state</dt>
            <dd>{panel.lineageState}</dd>
          </div>
        </div>
        <div>
          <dt className="font-semibold text-gray-100">Visibility note</dt>
          <dd>{panel.visibilityNote}</dd>
        </div>
      </dl>
    </article>
  );
}

export function CoverageConfidenceSummary({ summary }: { summary: TrustMetricSummaryData }) {
  return (
    <article
      className="rounded border border-[#2a3050] bg-[#10152a] p-4"
      data-read-only={summary.readOnly}
      data-descriptive-only={summary.descriptiveOnly}
    >
      <h3 className="text-sm font-semibold text-gray-100">{summary.label}</h3>
      <p className="mt-2 font-mono text-xs uppercase text-[#22d3ee]">{summary.state}</p>
      <p className="mt-3 text-sm leading-6 text-gray-300">{summary.visibilityNote}</p>
    </article>
  );
}

export function DiagnosticsSummary({ summary }: { summary: TrustDiagnosticsSummaryData }) {
  return (
    <article
      className={`rounded border p-4 ${diagnosticToneClasses[summary.state]}`}
      data-read-only={summary.readOnly}
      data-descriptive-only={summary.descriptiveOnly}
    >
      <p className="font-mono text-xs uppercase">{summary.state}</p>
      <h3 className="mt-2 text-sm font-semibold">{summary.label}</h3>
      <p className="mt-2 text-sm leading-6">{summary.message}</p>
    </article>
  );
}

export function FrontendTrustSurface({
  data = getFrontendTrustSurfaceData(),
}: {
  data?: FrontendTrustSurfaceData;
}) {
  return (
    <div className="space-y-8">
      <section className="rounded border border-[#2a3050] bg-[#10152a] p-5">
        <p className="font-mono text-xs uppercase tracking-wide text-[#22d3ee]">
          {data.phaseId}
        </p>
        <h1 className="mt-3 font-display text-3xl text-[#f5a623]">
          Frontend trust surface foundations
        </h1>
        <p className="mt-3 max-w-4xl text-sm leading-6 text-gray-300">
          These surfaces expose public trust visibility as read-only, descriptive-only
          frontend context. They keep limitations, unsupported states, missing evidence,
          stale provenance, incomplete coverage, and diagnostics visible.
        </p>
        <p className="mt-4 rounded border border-amber-400/20 bg-amber-500/5 p-3 text-sm leading-6 text-amber-100">
          {data.nonAuthorityStatement}
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {data.repositoryRemains.map((guarantee) => (
            <span
              key={guarantee}
              className="rounded border border-[#33415f] px-2.5 py-1 font-mono text-[11px] uppercase text-gray-200"
            >
              {guarantee}
            </span>
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <SectionHeading eyebrow="Trust status cards" title="State visibility" />
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {ordered(data.trustStatusCards).map((card) => (
            <TrustStatusCard key={card.id} card={card} />
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <SectionHeading eyebrow="Support status badges" title="Deterministic labels" />
        <div className="rounded border border-[#2a3050] bg-[#10152a] p-4">
          <div className="flex flex-wrap gap-2">
            {data.supportBadges.map((badge) => (
              <SupportStatusBadge key={badge.status} status={badge.status} />
            ))}
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <SectionHeading eyebrow="Explainability panels" title="Read-only explanations" />
        <div className="grid gap-4 md:grid-cols-2">
          {ordered(data.explainabilityPanels).map((panel) => (
            <ExplainabilityPanel key={panel.id} panel={panel} />
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <SectionHeading eyebrow="Evidence panels" title="Grouped public evidence" />
        <div className="grid gap-4 lg:grid-cols-2">
          {ordered(data.evidencePanels).map((panel) => (
            <EvidencePanel key={panel.id} panel={panel} />
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <SectionHeading eyebrow="Provenance and lineage" title="Source continuity" />
        <div className="grid gap-4 md:grid-cols-2">
          {ordered(data.provenanceLineagePanels).map((panel) => (
            <ProvenanceLineagePanel key={panel.id} panel={panel} />
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <SectionHeading eyebrow="Coverage and confidence" title="Non-scoring summaries" />
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[...ordered(data.coverageSummaries), ...ordered(data.confidenceSummaries)].map(
            (summary) => (
              <CoverageConfidenceSummary key={summary.id} summary={summary} />
            ),
          )}
        </div>
      </section>

      <section className="space-y-4">
        <SectionHeading eyebrow="Diagnostics summaries" title="Fail-visible diagnostics" />
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {ordered(data.diagnosticsSummaries).map((summary) => (
            <DiagnosticsSummary key={summary.id} summary={summary} />
          ))}
        </div>
      </section>
    </div>
  );
}
