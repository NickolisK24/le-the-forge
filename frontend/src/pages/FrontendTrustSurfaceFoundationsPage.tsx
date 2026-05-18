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

      <nav className="flex flex-wrap gap-3 text-sm">
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
      </nav>

      <FrontendTrustSurface />
    </div>
  );
}
