import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { V2LimitationNotice } from "@/components/v2/V2LimitationNotice";
import { V2WarningSummaryPanel } from "@/components/v2/V2TrustSummaryPanels";
import { getV2LimitationCodes, getV2LimitationCopy } from "@/lib/v2Limitations";

describe("v2 limitation notice", () => {
  it("renders major limitation codes with plain-language copy", () => {
    render(
      <V2LimitationNotice
        codes={[
          "display_only",
          "audit_only_value_normalization",
          "not_planner_calculable",
          "unsupported_mechanics",
          "partial_support",
          "unresolved_skill_identity",
          "missing_provenance",
          "experimental_only",
          "stable_calculable_unavailable",
          "production_not_consuming_v2",
        ]}
      />,
    );

    expect(screen.getByText(/Display-only data:/)).toBeInTheDocument();
    expect(screen.getByText(/Audit-only value normalization:/)).toBeInTheDocument();
    expect(screen.getByText(/Not planner-calculable:/)).toBeInTheDocument();
    expect(screen.getByText(/Unsupported mechanics:/)).toBeInTheDocument();
    expect(screen.getByText(/Partial support:/)).toBeInTheDocument();
    expect(screen.getByText(/Unresolved skill identity:/)).toBeInTheDocument();
    expect(screen.getByText(/Missing provenance:/)).toBeInTheDocument();
    expect(screen.getByText(/Experimental-only:/)).toBeInTheDocument();
    expect(screen.getByText(/Stable calculation unavailable:/)).toBeInTheDocument();
    expect(screen.getByText(/Production planner unchanged:/)).toBeInTheDocument();
  });

  it("renders unknown and missing limitation codes safely", () => {
    render(<V2LimitationNotice codes={["not-real"]} />);

    expect(screen.getByText(/Unknown limitation:/)).toBeInTheDocument();
    expect(screen.getByText(/does not recognize its specific type/)).toBeInTheDocument();
  });

  it("renders missing code input safely", () => {
    render(<V2LimitationNotice />);

    expect(screen.getByText(/Unknown limitation:/)).toBeInTheDocument();
  });

  it("compact mode keeps safety meaning", () => {
    render(<V2LimitationNotice codes={["not_planner_calculable"]} mode="compact" />);

    expect(screen.getByText(/This mechanic is not currently planner-calculable/)).toBeInTheDocument();
  });

  it("full mode renders fuller explanations", () => {
    render(<V2LimitationNotice codes={["display_only"]} mode="full" />);

    expect(screen.getByText(/damage, defense, crafting, or build calculations/)).toBeInTheDocument();
  });

  it("not planner-calculable copy does not imply unsupported mechanics are solved", () => {
    const copy = getV2LimitationCopy("not_planner_calculable");

    expect(copy.full).toMatch(/blocked from planner math/);
    expect(copy.full).not.toMatch(/DPS is accurate|mechanics are solved|calculations are supported/i);
  });

  it("audit-only value normalization copy does not imply values are normalized", () => {
    const copy = getV2LimitationCopy("audit_only_value_normalization");

    expect(copy.full).toMatch(/must not be treated as planner-normalized/);
    expect(copy.full).not.toMatch(/normalization is complete|values are normalized/i);
  });

  it("unresolved skill identity copy does not imply bridges exist", () => {
    const copy = getV2LimitationCopy("unresolved_skill_identity");

    expect(copy.full).toMatch(/No bridge is assumed/);
    expect(copy.full).not.toMatch(/bridge exists|resolved by name/i);
  });

  it("derives limitation codes from envelope safety fields", () => {
    const codes = getV2LimitationCodes({
      experimental: true,
      read_only: true,
      support_summary: { partial: 1, stable_calculable: 0 },
      meta: { value_normalization_status: "audit_only", production_consumed: false },
      debug: { planner_calculable_count: 0, unresolved_skill_reference_count: 2 },
    });

    expect(codes).toContain("display_only");
    expect(codes).toContain("audit_only_value_normalization");
    expect(codes).toContain("not_planner_calculable");
    expect(codes).toContain("partial_support");
    expect(codes).toContain("unresolved_skill_identity");
    expect(codes).toContain("production_not_consuming_v2");
  });

  it("integrated warning panel renders limitation copy", () => {
    render(
      <V2WarningSummaryPanel
        response={{
          read_only: true,
          support_summary: { stable_calculable: 0 },
          summary: { value_normalization_status: "audit_only" },
        }}
      />,
    );

    expect(screen.getByText("What this means")).toBeInTheDocument();
    expect(screen.getByText(/Display-only data:/)).toBeInTheDocument();
    expect(screen.getByText(/Not planner-calculable:/)).toBeInTheDocument();
    expect(screen.getByText(/Audit-only value normalization:/)).toBeInTheDocument();
  });
});
