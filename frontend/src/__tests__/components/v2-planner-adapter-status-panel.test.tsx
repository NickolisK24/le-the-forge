import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { V2PlannerAdapterStatusPanel } from "@/components/v2/V2PlannerAdapterStatusPanel";

describe("V2PlannerAdapterStatusPanel", () => {
  const status = {
    adapterModeEnabled: false,
    productionConsumed: false,
    adapterVisibleCount: 19398,
    blockedCount: 19398,
    plannerCalculableCount: 0,
    stableCalculableCount: 0,
    topBlockedReasons: {
      not_stable_calculable: 77592,
      unknown_value_scale: 52600,
      unresolved_skill_identity: 47696,
    },
    safeNowBaselineFixtureCount: 7,
    blockedBaselineFixtureCount: 6,
    valueNormalizationStatus: "audit_only",
    skillIdentityBridgeStatus: "unbridged",
  };

  it("renders disabled adapter state and production safety", () => {
    render(<V2PlannerAdapterStatusPanel status={status} />);

    expect(screen.getByText("v2 adapter status")).toBeInTheDocument();
    expect(screen.getAllByText("disabled").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("false").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Production Unchanged")).toBeInTheDocument();
  });

  it("renders adapter-visible, blocked, and zero calculable counts", () => {
    render(<V2PlannerAdapterStatusPanel status={status} />);

    expect(screen.getByText("Adapter-visible")).toBeInTheDocument();
    expect(screen.getByText("Blocked records")).toBeInTheDocument();
    expect(screen.getAllByText("19398").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("Planner-calculable")).toBeInTheDocument();
    expect(screen.getByText("Stable-calculable")).toBeInTheDocument();
    expect(screen.getAllByText("0").length).toBeGreaterThanOrEqual(2);
  });

  it("renders blocked reasons and baseline readiness", () => {
    render(<V2PlannerAdapterStatusPanel status={status} />);

    expect(screen.getByText("Top blocked reasons")).toBeInTheDocument();
    expect(screen.getByText(/not_stable_calculable: 77592/)).toBeInTheDocument();
    expect(screen.getByText("Baseline readiness")).toBeInTheDocument();
    expect(screen.getByText("7")).toBeInTheDocument();
    expect(screen.getByText("6")).toBeInTheDocument();
  });

  it("renders audit-only and unbridged identity status", () => {
    render(<V2PlannerAdapterStatusPanel status={status} />);

    expect(screen.getByText("audit_only")).toBeInTheDocument();
    expect(screen.getByText("unbridged")).toBeInTheDocument();
    expect(screen.getByText(/Audit-only value normalization:/)).toBeInTheDocument();
    expect(screen.getByText(/Unresolved skill identity:/)).toBeInTheDocument();
  });

  it("does not imply production planner calculations are enabled", () => {
    render(<V2PlannerAdapterStatusPanel status={status} />);

    expect(screen.getByText(/not production planner math/i)).toBeInTheDocument();
    expect(screen.getByText(/does not change DPS, EHP, crafting, or build output/i)).toBeInTheDocument();
    expect(screen.queryByText(/production planner calculations are enabled/i)).not.toBeInTheDocument();
  });
});
