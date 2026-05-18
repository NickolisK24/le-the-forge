import { render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

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
import FrontendTrustSurfaceFoundationsPage from "@/pages/FrontendTrustSurfaceFoundationsPage";
import TrustedDataExplanationPage from "@/pages/TrustedDataExplanationPage";

describe("v4.5C.1 frontend trust surface foundations", () => {
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
    expect(screen.getByText("report_backed")).toBeInTheDocument();
    expect(screen.getByText("Report metadata present")).toBeInTheDocument();
    expect(screen.getByText("Report hash visible")).toBeInTheDocument();
  });

  it("keeps deterministic fallback data fail-visible when report metadata is unavailable", () => {
    render(
      <FrontendTrustSurface
        reportIntegration={buildFallbackTrustReportIntegration("report_unavailable")}
      />,
    );

    expect(screen.getByText("Fallback deterministic trust data active")).toBeInTheDocument();
    expect(screen.getByText("fallback_active=true")).toBeInTheDocument();
    expect(screen.getByText("Report unavailable")).toBeInTheDocument();
    expect(screen.getByText("Report metadata missing")).toBeInTheDocument();
    expect(screen.getByText("Unsupported states preserved")).toBeInTheDocument();
    expect(screen.getByText("Unsupported states")).toBeInTheDocument();
    expect(screen.getByText("Fail-visible diagnostics")).toBeInTheDocument();
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
  });

  it("renders the stable trust surface route content", () => {
    render(
      <MemoryRouter initialEntries={[TRUST_SURFACE_ROUTE]}>
        <FrontendTrustSurfaceFoundationsPage />
      </MemoryRouter>,
    );

    expect(screen.getByText("Frontend trust surface foundations")).toBeInTheDocument();
    expect(screen.getByText("Generated trust report visibility")).toBeInTheDocument();
    expect(screen.getByText("Fail-visible diagnostics")).toBeInTheDocument();
  });

  it("renders a trusted data explanation entry point to the trust surface", () => {
    render(
      <MemoryRouter initialEntries={["/trusted-data"]}>
        <TrustedDataExplanationPage />
      </MemoryRouter>,
    );

    const callout = screen.getByTestId("trust-surface-entry-callout");
    expect(within(callout).getByText("Read-only trust surface")).toBeInTheDocument();
    expect(
      within(callout).getByText(/report-backed metadata, fallback visibility/i),
    ).toBeInTheDocument();
    expect(
      within(callout).getByText(/does not enable planner authority or operational behavior/i),
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
