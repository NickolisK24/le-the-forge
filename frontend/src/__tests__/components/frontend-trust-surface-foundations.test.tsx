import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { FrontendTrustSurface } from "@/components/trust/FrontendTrustSurface";
import {
  FRONTEND_TRUST_SURFACE_DATA,
  FRONTEND_TRUST_SURFACE_NON_AUTHORITY_STATEMENT,
  isFrontendTrustSurfaceReadOnly,
} from "@/lib/frontendTrustSurfaceData";

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
    expect(screen.getByText("READ-ONLY")).toBeInTheDocument();
    expect(screen.getByText("DESCRIPTIVE-ONLY")).toBeInTheDocument();
    expect(screen.getByText("NON-operational")).toBeInTheDocument();
    expect(screen.getByText("NON-authorizing")).toBeInTheDocument();
    expect(screen.getByText("NON-approving")).toBeInTheDocument();
    expect(screen.getByText("NON-recommending")).toBeInTheDocument();
    expect(screen.getByText("NON-ranking")).toBeInTheDocument();
    expect(screen.getByText("NON-scoring")).toBeInTheDocument();
    expect(screen.getByText(FRONTEND_TRUST_SURFACE_NON_AUTHORITY_STATEMENT)).toBeInTheDocument();
  });

  it("does not render action controls for authorization, approval, ranking, recommendation, scoring, or execution", () => {
    render(<FrontendTrustSurface />);

    const prohibitedActionPattern =
      /authorize|approve|recommend|rank|score|execute|run planner|enable production/i;

    expect(screen.queryByRole("button", { name: prohibitedActionPattern })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: prohibitedActionPattern })).not.toBeInTheDocument();
  });
});
