import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { V2StatusBadgeGroup } from "@/components/v2/V2StatusBadgeGroup";
import { V2SupportBadge, V2TrustBadge } from "@/components/v2/V2TrustBadge";
import { V2EnvelopePanels } from "@/components/v2/V2EnvelopePanels";
import { getSupportBadge, getTrustBadge } from "@/lib/v2TrustStatus";

describe("v2 trust and support badges", () => {
  it("renders known support statuses with clear labels", () => {
    render(
      <div>
        <V2SupportBadge status="trusted" />
        <V2SupportBadge status="partial" />
        <V2SupportBadge status="unsupported" />
      </div>,
    );

    expect(screen.getByText("Trusted Data")).toBeInTheDocument();
    expect(screen.getByText("Partial Support")).toBeInTheDocument();
    expect(screen.getByText("Unsupported")).toBeInTheDocument();
  });

  it("renders trust statuses with clear labels", () => {
    render(
      <div>
        <V2TrustBadge status="generated_from_game_data" />
        <V2TrustBadge status="validated" />
        <V2TrustBadge status="provenance_available" />
      </div>,
    );

    expect(screen.getByText("Generated")).toBeInTheDocument();
    expect(screen.getByText("Validated")).toBeInTheDocument();
    expect(screen.getByText("Provenance Available")).toBeInTheDocument();
  });

  it("renders unknown and missing statuses safely", () => {
    render(
      <div>
        <V2SupportBadge />
        <V2TrustBadge status="not-a-real-status" />
      </div>,
    );

    expect(screen.getByText("Unknown Status")).toBeInTheDocument();
    expect(screen.getByText("Unknown Trust")).toBeInTheDocument();
  });

  it("keeps not planner-calculable distinct from supported", () => {
    const notPlannerCalculable = getSupportBadge("not_planner_calculable");
    const supported = getSupportBadge("supported");

    expect(notPlannerCalculable.label).toBe("Not Planner-Calculable");
    expect(supported.label).toBe("Supported");
    expect(notPlannerCalculable.label).not.toBe(supported.label);
  });

  it("renders audit-only and display-only distinctly", () => {
    render(
      <div>
        <V2SupportBadge status="audit_only" />
        <V2SupportBadge status="display_only" />
      </div>,
    );

    expect(screen.getByText("Audit Only")).toBeInTheDocument();
    expect(screen.getByText("Display Only")).toBeInTheDocument();
  });

  it("badge titles explain meaning without implying planner support", () => {
    render(<V2SupportBadge status="not_planner_calculable" />);

    const badge = screen.getByText("Not Planner-Calculable");
    expect(badge).toHaveAttribute("title", expect.stringContaining("not eligible for production planner calculations"));
  });

  it("badge group renders multiple statuses from a v2 envelope", () => {
    render(
      <V2StatusBadgeGroup
        response={{
          experimental: true,
          read_only: true,
          support_summary: { partial: 2, stable_calculable: 0 },
          provenance: { source_path: "docs/generated/v2_affix_bundle.json" },
          summary: { trust_level_counts: { generated_from_game_data: 2 }, value_normalization_status: "audit_only" },
        }}
      />,
    );

    expect(screen.getByText("Partial Support")).toBeInTheDocument();
    expect(screen.getByText("Not Planner-Calculable")).toBeInTheDocument();
    expect(screen.getByText("Audit Only")).toBeInTheDocument();
    expect(screen.getByText("Display Only")).toBeInTheDocument();
    expect(screen.getByText("Experimental")).toBeInTheDocument();
    expect(screen.getByText("Generated")).toBeInTheDocument();
    expect(screen.getByText("Provenance Available")).toBeInTheDocument();
  });

  it("integrated envelope panel still renders support, provenance, and debug sections", () => {
    render(
      <V2EnvelopePanels
        response={{
          meta: { experimental: true, read_only: true },
          support_summary: { partial: 1, stable_calculable: 0 },
          provenance: { source_path: "docs/generated/v2_item_base_bundle.json" },
          debug: { validation: "ok" },
        }}
      />,
    );

    expect(screen.getByText("Support summary")).toBeInTheDocument();
    expect(screen.getByText("Partial Support")).toBeInTheDocument();
    expect(screen.getByText("Not Planner-Calculable")).toBeInTheDocument();
    expect(screen.getByText("Provenance")).toBeInTheDocument();
    expect(screen.getByText("Debug contract")).toBeInTheDocument();
  });

  it("normalizes trust status aliases", () => {
    expect(getTrustBadge("generated_from_game_data").label).toBe("Generated");
    expect(getTrustBadge("source_path").label).toBe("Provenance Available");
  });
});
