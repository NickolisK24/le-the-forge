import { Link } from "react-router-dom";

import PageMeta from "@/components/PageMeta";
import { FrontendTrustSurface } from "@/components/trust/FrontendTrustSurface";

export default function FrontendTrustSurfaceFoundationsPage() {
  return (
    <div className="mx-auto max-w-7xl space-y-8 p-6">
      <PageMeta
        title="Frontend Trust Surfaces"
        description="Read-only deterministic frontend trust surfaces for public support, evidence, provenance, lineage, coverage, confidence, and diagnostics visibility."
        path="/trusted-data/frontend-trust"
      />

      <nav
        className="rounded border border-[#2a3050] bg-[#10152a] p-4 text-sm"
        aria-label="Trust surface related views"
      >
        <p className="mb-3 text-sm leading-6 text-gray-300">
          Trust visibility is read-only context for support, evidence, provenance,
          lineage, coverage, confidence, and diagnostics. It does not enable
          planner authority.
        </p>
        <div className="flex flex-wrap gap-3">
          <Link
            to="/trusted-data"
            className="rounded border border-[#2a3050] px-4 py-2 text-gray-200 no-underline hover:border-[#f5a623]"
          >
            Trusted data guide
          </Link>
          <Link
            to="/trusted-data/support"
            className="rounded border border-[#2a3050] px-4 py-2 text-gray-200 no-underline hover:border-[#f5a623]"
          >
            Support matrix
          </Link>
        </div>
      </nav>

      <FrontendTrustSurface />
    </div>
  );
}
