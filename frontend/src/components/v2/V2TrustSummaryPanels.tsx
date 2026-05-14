import type { V2ApiEnvelope } from "@/lib/v2ApiEnvelope";
import { getV2ProvenanceSummary, getV2WarningSummary } from "@/lib/v2TrustSummaries";

import { V2LimitationNotice } from "./V2LimitationNotice";
import { V2StatusBadgeGroup } from "./V2StatusBadgeGroup";

interface V2TrustSummaryPanelProps {
  response: V2ApiEnvelope | null;
}

export function V2ProvenanceSummaryPanel({ response }: V2TrustSummaryPanelProps) {
  const summary = getV2ProvenanceSummary(response);

  return (
    <div className="rounded border border-[#2a3050] bg-[#10152a] p-4">
      <h2 className="text-sm font-semibold text-gray-100">Provenance</h2>
      <p className="mt-2 text-xs text-gray-300">{summary.sourceLabel}</p>
      <p className="mt-2 break-all font-mono text-xs text-gray-300">{summary.sourcePath}</p>
      <p className="mt-2 text-xs text-gray-500">{summary.validationStatus}</p>
      <p className="mt-2 break-words font-mono text-xs text-gray-500">{summary.provenanceDetails}</p>
    </div>
  );
}

export function V2WarningSummaryPanel({ response }: V2TrustSummaryPanelProps) {
  const summary = getV2WarningSummary(response);

  return (
    <div className="mt-3 rounded border border-amber-400/20 bg-amber-500/5 p-3">
      <h3 className="text-xs font-semibold text-amber-100">Warnings and limitations</h3>
      <ul className="mt-2 space-y-1 text-xs text-amber-100/90">
        {summary.messages.map((message) => (
          <li key={message}>{message}</li>
        ))}
      </ul>
      <div className="mt-3">
        <V2LimitationNotice codes={summary.limitationCodes} />
      </div>
    </div>
  );
}

export function V2TrustSummaryPanels({ response }: V2TrustSummaryPanelProps) {
  return (
    <section className="grid gap-3 lg:grid-cols-3">
      <div className="rounded border border-[#2a3050] bg-[#10152a] p-4">
        <h2 className="text-sm font-semibold text-gray-100">Trust status</h2>
        <div className="mt-2">
          <V2StatusBadgeGroup response={response} />
        </div>
        <p className="mt-2 text-xs text-gray-500">Badges describe visibility and trust, not planner calculation support.</p>
      </div>
      <V2ProvenanceSummaryPanel response={response} />
      <div className="rounded border border-[#2a3050] bg-[#10152a] p-4">
        <h2 className="text-sm font-semibold text-gray-100">Warnings</h2>
        <V2WarningSummaryPanel response={response} />
      </div>
    </section>
  );
}
