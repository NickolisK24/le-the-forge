import { Link } from "react-router-dom";

export const TRUST_SURFACE_ROUTE = "/trusted-data/frontend-trust";

export function TrustSurfaceEntryCallout() {
  return (
    <section
      className="rounded border border-[#2a3050] bg-[#10152a] p-5"
      data-testid="trust-surface-entry-callout"
      data-read-only="true"
      data-descriptive-only="true"
    >
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="max-w-3xl">
          <p className="font-mono text-xs uppercase tracking-wide text-[#22d3ee]">
            Read-only trust surface
          </p>
          <h2 className="mt-2 text-base font-semibold text-gray-100">
            View trust visibility
          </h2>
          <p className="mt-2 text-sm leading-6 text-gray-300">
            See support status, evidence, provenance, lineage, report metadata,
            fallback visibility, and fail-visible diagnostics in one descriptive
            surface. It stays read-only and does not enable planner authority or
            operational behavior.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {[
              "report-backed visibility",
              "fallback visible",
              "fail-visible diagnostics",
              "descriptive-only",
            ].map((label) => (
              <span
                key={label}
                className="rounded border border-[#33415f] px-2 py-1 font-mono text-[11px] uppercase text-gray-300"
              >
                {label}
              </span>
            ))}
          </div>
        </div>
        <Link
          to={TRUST_SURFACE_ROUTE}
          className="inline-flex w-fit rounded border border-[#2a3050] px-4 py-2 text-sm text-gray-200 no-underline hover:border-[#f5a623]"
        >
          View trust visibility
        </Link>
      </div>
    </section>
  );
}
