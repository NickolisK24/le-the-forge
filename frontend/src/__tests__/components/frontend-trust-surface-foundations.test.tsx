import { render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import Sidebar from "@/components/navigation/Sidebar";
import { FrontendTrustSurface } from "@/components/trust/FrontendTrustSurface";
import { TRUST_SURFACE_ROUTE } from "@/components/trust/TrustSurfaceEntryCallout";
import {
  FRONTEND_TRUST_SURFACE_DATA,
  FRONTEND_TRUST_SURFACE_NON_AUTHORITY_STATEMENT,
  isFrontendTrustSurfaceReadOnly,
} from "@/lib/frontendTrustSurfaceData";
import {
  FRONTEND_TRUST_REPORT_HASH,
  FRONTEND_TRUST_REPORT_INTEGRATION_DATA,
  FRONTEND_TRUST_REPORT_PATH,
  buildFallbackTrustReportIntegration,
  isFrontendTrustReportIntegrationReadOnly,
} from "@/lib/frontendTrustReportIntegration";
import {
  BACKEND_TRUST_VISIBILITY_ENDPOINT,
  buildBackendTrustFetchFallback,
  fetchBackendTrustVisibility,
  isBackendTrustVisibilityReadOnly,
} from "@/lib/frontendTrustBackendVisibility";
import FrontendTrustSurfaceFoundationsPage from "@/pages/FrontendTrustSurfaceFoundationsPage";
import TrustedDataExplanationPage from "@/pages/TrustedDataExplanationPage";
import type { BackendTrustVisibilityPayload } from "@/types/frontendTrustBackendVisibility";

const backendTrustSuccessPayload: BackendTrustVisibilityPayload = {
  schema_version: "v4.5d.3",
  status: "available",
  endpoint_contract: {
    endpoint_contract_id: "v4_5d_3_backend_trust_visibility_payload_expansion",
    endpoint_route: BACKEND_TRUST_VISIBILITY_ENDPOINT,
    schema_version: "v4.5d.3",
    methods: ["GET"],
    read_only: true,
    descriptive_only: true,
    non_mutating: true,
  },
  source_type: "backend_expanded_report_backed_visibility",
  report_reference: {
    name: "v4_5c_5_frontend_trust_closeout_backend_reflection_audit_report",
    path: "docs/generated/v4_5c_5_frontend_trust_closeout_backend_reflection_audit_report.json",
    hash: "4528555397312e45f82f4a9fac7d748b35b44e9724a92d2b2c2fec92827b466a",
    available: true,
    status: "report_available",
  },
  backend_reflection: {
    status: "backend_reflection_expanded_payload_defined",
    health_endpoint: "/api/health",
    trust_endpoint: BACKEND_TRUST_VISIBILITY_ENDPOINT,
    alignment_status: "frontend_backend_alignment_endpoint_visible",
  },
  frontend_alignment: {
    status: "frontend_backend_alignment_endpoint_visible",
    live_frontend_fetch: true,
    integration_readiness: "backend_payload_ready_frontend_rendering_pending",
  },
  diagnostics: [
    {
      id: "report_reference_available",
      severity: "informational",
      message: "Report-backed trust visibility metadata is available.",
    },
  ],
  payload_hash: "d1-endpoint-payload-hash",
};

function mockBackendTrustFetch(payload: unknown = backendTrustSuccessPayload) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => ({
      ok: true,
      status: 200,
      json: async () => payload,
    })),
  );
}

describe("v4.5C.1 frontend trust surface foundations", () => {
  beforeEach(() => {
    mockBackendTrustFetch();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders deterministic support badges for every public support state", () => {
    render(<FrontendTrustSurface />);

    const badgeSection = screen.getByText("Deterministic labels").closest("section");
    expect(badgeSection).not.toBeNull();

    const labels = within(badgeSection as HTMLElement)
      .getAllByTitle(/Visible/i)
      .map((node) => node.textContent);

    expect(labels).toEqual([
      "Supported",
      "Partially Supported",
      "Unsupported",
      "Experimental",
      "Deprecated",
      "Blocked",
      "Unknown",
    ]);
  });

  it("keeps unsupported, blocked, stale, unknown, and missing states visible", () => {
    render(<FrontendTrustSurface />);

    expect(screen.getByText("Unsupported states")).toBeInTheDocument();
    expect(screen.getByText("Blocked states")).toBeInTheDocument();
    expect(screen.getByText("Unknown provenance")).toBeInTheDocument();
    expect(screen.getByText("Stale provenance")).toBeInTheDocument();
    expect(screen.getAllByText("Missing evidence visibility").length).toBeGreaterThan(0);
    expect(screen.getByText("Unsupported evidence")).toBeInTheDocument();
  });

  it("renders read-only explainability panels for required explanation categories", () => {
    render(<FrontendTrustSurface />);

    expect(screen.getByText("Support explanations")).toBeInTheDocument();
    expect(screen.getByText("Limitation explanations")).toBeInTheDocument();
    expect(screen.getByText("Unsupported-state explanations")).toBeInTheDocument();
    expect(screen.getByText("Continuity explanations")).toBeInTheDocument();
    expect(screen.getByText("Trust explanations")).toBeInTheDocument();
    expect(screen.getByText("Diagnostics explanations")).toBeInTheDocument();
  });

  it("renders report-backed metadata, source visibility, hash, and certification status", () => {
    render(<FrontendTrustSurface />);

    expect(screen.getByText("Generated trust report visibility")).toBeInTheDocument();
    expect(screen.getByText("v4.5C.1 frontend trust surface foundations report")).toBeInTheDocument();
    expect(screen.getAllByText(FRONTEND_TRUST_REPORT_PATH).length).toBeGreaterThan(0);
    expect(screen.getByText(FRONTEND_TRUST_REPORT_HASH)).toBeInTheDocument();
    expect(
      screen.getByText("read_only_descriptive_frontend_trust_surface_certified"),
    ).toBeInTheDocument();
    expect(screen.getAllByText("report backed").length).toBeGreaterThan(0);
    expect(screen.getByText("Report metadata present")).toBeInTheDocument();
    expect(screen.getByText("Report hash visible")).toBeInTheDocument();
    expect(screen.getByText("Backend endpoint context visible")).toBeInTheDocument();
    expect(
      screen.getByText(
        "This surface shows deterministic frontend/report-backed visibility alongside read-only backend endpoint metadata, not backend trust authority.",
      ),
    ).toBeInTheDocument();
  });

  it("keeps deterministic fallback data fail-visible when report metadata is unavailable", () => {
    render(
      <FrontendTrustSurface
        reportIntegration={buildFallbackTrustReportIntegration("report_unavailable")}
        backendVisibility={buildBackendTrustFetchFallback(
          "fetch_failed",
          "Backend fetch unavailable - showing deterministic fallback.",
        )}
        enableBackendFetch={false}
      />,
    );

    expect(screen.getByText("Fallback deterministic trust data active")).toBeInTheDocument();
    expect(screen.getByText("fallback_active=true")).toBeInTheDocument();
    expect(screen.getByText("Report unavailable")).toBeInTheDocument();
    expect(screen.getByText("Report metadata missing")).toBeInTheDocument();
    expect(screen.getByText("Unsupported states preserved")).toBeInTheDocument();
    expect(screen.getByText("Unsupported states")).toBeInTheDocument();
    expect(screen.getByText("Fail-visible diagnostics")).toBeInTheDocument();
    expect(
      screen.getByText("Backend fetch unavailable - showing deterministic fallback"),
    ).toBeInTheDocument();
    expect(screen.getByText("backend_fallback_active=true")).toBeInTheDocument();
  });

  it("fetch client handles backend success payload with GET-only endpoint visibility", async () => {
    const fetcher = vi.fn(async () => ({
      ok: true,
      status: 200,
      json: async () => backendTrustSuccessPayload,
    }));

    const state = await fetchBackendTrustVisibility(fetcher);

    expect(fetcher).toHaveBeenCalledWith(BACKEND_TRUST_VISIBILITY_ENDPOINT, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });
    expect(state.endpointAvailable).toBe(true);
    expect(state.schemaVersion).toBe("v4.5d.3");
    expect(state.backendReflectionStatus).toBe("backend_reflection_expanded_payload_defined");
    expect(state.frontendBackendAlignmentStatus).toBe(
      "frontend_backend_alignment_endpoint_visible",
    );
    expect(state.reportReference.hash).toBe(
      "4528555397312e45f82f4a9fac7d748b35b44e9724a92d2b2c2fec92827b466a",
    );
    expect(isBackendTrustVisibilityReadOnly(state)).toBe(true);
  });

  it("fetch client handles network failure with fail-visible fallback", async () => {
    const fetcher = vi.fn(async () => {
      throw new Error("network unavailable");
    });

    const state = await fetchBackendTrustVisibility(fetcher);

    expect(state.endpointAvailable).toBe(false);
    expect(state.fetchStatus).toBe("fetch_failed");
    expect(state.frontendBackendAlignmentStatus).toBe(
      "frontend_backend_alignment_fetch_attempted_with_fail_visible_fallback",
    );
    expect(state.fallbackActive).toBe(true);
    expect(state.diagnostics.map((item) => item.id)).toContain("fetch_failed");
  });

  it("fetch client handles malformed payload and missing schema version", async () => {
    const malformedState = await fetchBackendTrustVisibility(
      vi.fn(async () => ({
        ok: true,
        status: 200,
        json: async () => "not an object",
      })),
    );
    const missingSchemaState = await fetchBackendTrustVisibility(
      vi.fn(async () => ({
        ok: true,
        status: 200,
        json: async () => ({ status: "available" }),
      })),
    );

    expect(malformedState.fetchStatus).toBe("malformed_payload");
    expect(malformedState.fallbackActive).toBe(true);
    expect(missingSchemaState.fetchStatus).toBe("missing_schema_version");
    expect(missingSchemaState.fallbackActive).toBe(true);
  });

  it("renders endpoint-backed backend visibility when fetch data is available", async () => {
    render(<FrontendTrustSurface enableBackendFetch />);

    await waitFor(() => {
      expect(screen.getAllByText("Backend trust endpoint visible").length).toBeGreaterThan(0);
    });

    expect(screen.getByText("Read-only backend trust endpoint")).toBeInTheDocument();
    expect(screen.getAllByText(BACKEND_TRUST_VISIBILITY_ENDPOINT).length).toBeGreaterThan(0);
    expect(screen.getByText("v4.5d.3")).toBeInTheDocument();
    expect(screen.getByText("backend_reflection_expanded_payload_defined")).toBeInTheDocument();
    expect(
      screen.getAllByText("frontend_backend_alignment_endpoint_visible").length,
    ).toBeGreaterThan(0);
    expect(
      screen.getByText("v4_5c_5_frontend_trust_closeout_backend_reflection_audit_report"),
    ).toBeInTheDocument();
    expect(screen.getByText("backend_fallback_active=false")).toBeInTheDocument();
  });

  it("renders fail-visible backend fallback when the endpoint is unavailable", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new Error("backend unavailable");
      }),
    );

    render(<FrontendTrustSurface enableBackendFetch />);

    await waitFor(() => {
      expect(
        screen.getByText("Backend fetch unavailable - showing deterministic fallback"),
      ).toBeInTheDocument();
    });

    expect(screen.getByText("frontend_backend_alignment_fetch_attempted_with_fail_visible_fallback")).toBeInTheDocument();
    expect(screen.getByText("backend_fallback_active=true")).toBeInTheDocument();
    expect(screen.getByText("Unsupported states")).toBeInTheDocument();
    expect(screen.getByText("Generated trust report visibility")).toBeInTheDocument();
  });

  it("renders evidence, provenance, lineage, coverage, confidence, and diagnostics surfaces", () => {
    render(<FrontendTrustSurface />);

    expect(screen.getByText("Generated report evidence")).toBeInTheDocument();
    expect(screen.getByText("Support status evidence")).toBeInTheDocument();
    expect(screen.getByText("Explainability evidence")).toBeInTheDocument();
    expect(screen.getByText("Source references")).toBeInTheDocument();
    expect(screen.getByText("Lineage continuity")).toBeInTheDocument();
    expect(screen.getByText("Coverage visibility")).toBeInTheDocument();
    expect(screen.getByText("Incomplete coverage")).toBeInTheDocument();
    expect(screen.getByText("Confidence visibility")).toBeInTheDocument();
    expect(screen.getByText("Unknown confidence")).toBeInTheDocument();
    expect(screen.getByText("Public warning")).toBeInTheDocument();
    expect(screen.getByText("Evidence gap")).toBeInTheDocument();
    expect(screen.getByText("Explainability gap")).toBeInTheDocument();
  });

  it("renders refined scan groups, limitation labels, and context-only summaries", () => {
    render(<FrontendTrustSurface />);

    expect(screen.getByLabelText("Trust surface scan summary")).toBeInTheDocument();
    expect(screen.getByText("Report source")).toBeInTheDocument();
    expect(screen.getByText("Evidence groups")).toBeInTheDocument();
    expect(screen.getAllByText(/limitation remains visible/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText("context only").length).toBeGreaterThan(0);
    expect(screen.getByText(/fail-visible report diagnostics/i)).toBeInTheDocument();
  });

  it("preserves explicit read-only and descriptive-only guarantees", () => {
    render(<FrontendTrustSurface />);

    expect(isFrontendTrustSurfaceReadOnly(FRONTEND_TRUST_SURFACE_DATA)).toBe(true);
    expect(screen.getAllByText("READ-ONLY").length).toBeGreaterThan(0);
    expect(screen.getAllByText("DESCRIPTIVE-ONLY").length).toBeGreaterThan(0);
    expect(screen.getAllByText("NON-operational").length).toBeGreaterThan(0);
    expect(screen.getAllByText("NON-authorizing").length).toBeGreaterThan(0);
    expect(screen.getAllByText("NON-approving").length).toBeGreaterThan(0);
    expect(screen.getAllByText("NON-recommending").length).toBeGreaterThan(0);
    expect(screen.getAllByText("NON-ranking").length).toBeGreaterThan(0);
    expect(screen.getAllByText("NON-scoring").length).toBeGreaterThan(0);
    expect(screen.getByText("NON-triaging")).toBeInTheDocument();
    expect(screen.getByText(FRONTEND_TRUST_SURFACE_NON_AUTHORITY_STATEMENT)).toBeInTheDocument();
    expect(isFrontendTrustReportIntegrationReadOnly(FRONTEND_TRUST_REPORT_INTEGRATION_DATA)).toBe(true);
  });

  it("does not render action controls for authorization, approval, ranking, recommendation, scoring, or execution", () => {
    render(<FrontendTrustSurface />);

    const prohibitedActionPattern =
      /authorize|approve|recommend|rank|score|execute|run planner|enable production/i;

    expect(screen.queryByRole("button", { name: prohibitedActionPattern })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: prohibitedActionPattern })).not.toBeInTheDocument();
    expect(document.body).not.toHaveTextContent(
      /approved|safe to use|recommended|best build|fully trusted|production ready|guaranteed correct/i,
    );
  });

  it("renders the stable trust surface route content", async () => {
    render(
      <MemoryRouter initialEntries={[TRUST_SURFACE_ROUTE]}>
        <Routes>
          <Route path={TRUST_SURFACE_ROUTE} element={<FrontendTrustSurfaceFoundationsPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText("Frontend trust surface foundations")).toBeInTheDocument();
    expect(screen.getByText("Generated trust report visibility")).toBeInTheDocument();
    expect(screen.getByText("Fail-visible diagnostics")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getAllByText("Backend trust endpoint visible").length).toBeGreaterThan(0);
    });
  });

  it("renders a trusted data explanation entry point to the trust surface", () => {
    render(
      <MemoryRouter initialEntries={["/trusted-data"]}>
        <Routes>
          <Route path="/trusted-data" element={<TrustedDataExplanationPage />} />
        </Routes>
      </MemoryRouter>,
    );

    const callout = screen.getByTestId("trust-surface-entry-callout");
    expect(within(callout).getByText("Read-only trust surface")).toBeInTheDocument();
    expect(
      within(callout).getByText(/report metadata, fallback visibility/i),
    ).toBeInTheDocument();
    expect(
      within(callout).getByText(/stays read-only and does not enable planner authority/i),
    ).toBeInTheDocument();
    expect(within(callout).getByRole("link", { name: "View trust visibility" }))
      .toHaveAttribute("href", TRUST_SURFACE_ROUTE);
    expect(callout).not.toHaveTextContent(
      /approved|safe to use|recommended|best build|fully trusted|production ready|guaranteed correct/i,
    );
  });

  it("renders a sidebar navigation entry point to trust visibility", () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <Sidebar />
      </MemoryRouter>,
    );

    expect(screen.getByRole("link", { name: "Trust Visibility" }))
      .toHaveAttribute("href", TRUST_SURFACE_ROUTE);
  });
});
