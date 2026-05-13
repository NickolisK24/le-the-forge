import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { V2EnvelopePanels } from "@/components/v2/V2EnvelopePanels";
import {
  V2ProvenanceSummaryPanel,
  V2TrustSummaryPanels,
  V2WarningSummaryPanel,
} from "@/components/v2/V2TrustSummaryPanels";
import { getV2ProvenanceSummary, getV2WarningSummary } from "@/lib/v2TrustSummaries";

describe("v2 trust summary panels", () => {
  it("renders available provenance summary", () => {
    render(
      <V2ProvenanceSummaryPanel
        response={{
          success: true,
          data_source: "v2_affix_bundle",
          provenance: {
            source_path: "docs/generated/v2_affix_bundle.json",
            source_type: "affix",
            extraction_method: "last_epoch_affix_export",
          },
        }}
      />,
    );

    expect(screen.getByText("Provenance")).toBeInTheDocument();
    expect(screen.getByText("Source information is available for affix.")).toBeInTheDocument();
    expect(screen.getByText("docs/generated/v2_affix_bundle.json")).toBeInTheDocument();
    expect(screen.getByText("Validation status: available")).toBeInTheDocument();
  });

  it("handles missing provenance safely", () => {
    const summary = getV2ProvenanceSummary({});

    expect(summary.hasProvenance).toBe(false);
    expect(summary.sourceLabel).toBe("Source information is available for this data.");
    expect(summary.sourcePath).toBe("n/a");
  });

  it("warning panel renders explicit warnings", () => {
    render(<V2WarningSummaryPanel response={{ warnings: ["source field missing"] }} />);

    expect(screen.getByText("Warnings and limitations")).toBeInTheDocument();
    expect(screen.getByText("source field missing")).toBeInTheDocument();
  });

  it("warning panel renders audit-only and not planner-calculable messaging distinctly", () => {
    render(
      <V2WarningSummaryPanel
        response={{
          support_summary: { stable_calculable: 0 },
          summary: { value_normalization_status: "audit_only" },
        }}
      />,
    );

    expect(screen.getAllByText("Value normalization is still audit-only.")).not.toHaveLength(0);
    expect(screen.getAllByText("This mechanic is not currently planner-calculable.")).not.toHaveLength(0);
  });

  it("warning copy does not imply planner calculation support", () => {
    const summary = getV2WarningSummary({
      read_only: true,
      support_summary: { stable_calculable: 0 },
    });

    expect(summary.messages).toContain("This data is display-only and is not used for planner calculations.");
    expect(summary.messages.join(" ")).not.toMatch(/DPS is accurate|planner calculations are supported/i);
  });

  it("combined panels render with badges", () => {
    render(
      <V2TrustSummaryPanels
        response={{
          experimental: true,
          read_only: true,
          support_summary: { partial: 1, stable_calculable: 0 },
          provenance: { source_path: "docs/generated/v2_item_base_bundle.json" },
        }}
      />,
    );

    expect(screen.getByText("Trust status")).toBeInTheDocument();
    expect(screen.getByText("Partial Support")).toBeInTheDocument();
    expect(screen.getByText("Display Only")).toBeInTheDocument();
    expect(screen.getByText("Not Planner-Calculable")).toBeInTheDocument();
    expect(screen.getByText("Warnings")).toBeInTheDocument();
  });

  it("integrated envelope panel still renders existing support provenance and debug sections", () => {
    render(
      <V2EnvelopePanels
        response={{
          meta: { read_only: true },
          support_summary: { partial: 1, stable_calculable: 0 },
          provenance: { source_path: "docs/generated/v2_skill_bundle.json" },
          debug: { validation: "ok" },
        }}
      />,
    );

    expect(screen.getByText("Support summary")).toBeInTheDocument();
    expect(screen.getByText("Provenance")).toBeInTheDocument();
    expect(screen.getByText("Debug contract")).toBeInTheDocument();
    expect(screen.getByText("Warnings and limitations")).toBeInTheDocument();
    expect(screen.getByText("docs/generated/v2_skill_bundle.json")).toBeInTheDocument();
  });
});
