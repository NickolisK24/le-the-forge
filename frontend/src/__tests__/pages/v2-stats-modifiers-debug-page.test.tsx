import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import V2StatsModifiersDebugPage from "@/pages/debug/V2StatsModifiersDebugPage";

describe("V2StatsModifiersDebugPage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders disabled response clearly", async () => {
    mockFetch({ success: false, error: "v2_modifier_registry_missing", message: "v2 modifier registry not found" });

    render(<V2StatsModifiersDebugPage />);

    expect(await screen.findByText("Debug endpoint unavailable")).toBeInTheDocument();
    expect(screen.getByText("v2 modifier registry not found")).toBeInTheDocument();
  });

  it("loads the API-prefixed debug endpoint", async () => {
    mockFetch(successPayload());

    render(<V2StatsModifiersDebugPage />);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith("/api/experimental/v2/modifiers/debug");
    });
  });

  it("renders stat and modifier summary counts", async () => {
    mockFetch(successPayload());

    render(<V2StatsModifiersDebugPage />);

    expect(await screen.findByText("2070")).toBeInTheDocument();
    expect(screen.getAllByText("19398").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Planner-calculable")).toBeInTheDocument();
    expect(screen.getByText("Stable-calculable")).toBeInTheDocument();
    expect(screen.getAllByText("0").length).toBeGreaterThanOrEqual(2);
  });

  it("renders value scale counts and distributions", async () => {
    mockFetch(successPayload());

    render(<V2StatsModifiersDebugPage />);

    expect(await screen.findByText("Source units")).toBeInTheDocument();
    expect(screen.getByText("6248")).toBeInTheDocument();
    expect(screen.getByText("Unknown value scale")).toBeInTheDocument();
    expect(screen.getByText("13150")).toBeInTheDocument();
    expect(screen.getByText("source_units: 6248, unknown: 13150")).toBeInTheDocument();
    expect(screen.getAllByText(/unknown: 11606/).length).toBeGreaterThanOrEqual(1);
  });

  it("renders limitation copy for audit-only and not planner-calculable status", async () => {
    mockFetch(successPayload());

    render(<V2StatsModifiersDebugPage />);

    expect(await screen.findByText("Planner safety limitations")).toBeInTheDocument();
    expect(screen.getAllByText(/Audit-only value normalization:/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/Not planner-calculable:/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/must not be treated as planner-normalized/)).toBeInTheDocument();
    expect(screen.getByText(/blocked from planner math/)).toBeInTheDocument();
  });

  it("does not imply modifier values are calculation-ready", async () => {
    mockFetch(successPayload());

    render(<V2StatsModifiersDebugPage />);

    await screen.findByText("v2 stats and modifiers inspection");
    expect(screen.getByText(/Modifier values are not used for planner calculations/)).toBeInTheDocument();
    expect(screen.getByText(/v3 mechanical intelligence is required/i)).toBeInTheDocument();
    expect(screen.queryByText(/calculation-ready/i)).not.toBeInTheDocument();
  });
});

function mockFetch(payload: unknown) {
  vi.mocked(fetch).mockResolvedValue({ json: async () => payload } as Response);
}

function successPayload() {
  return {
    success: true,
    experimental: true,
    read_only: true,
    production_consumer: false,
    data_source: "v2_modifier_registries",
    debug_summary: {
      stats: {
        source_path: "D:\\Forge\\le-the-forge\\docs\\generated\\v2_stat_registry.json",
        stat_count: 2070,
        summary: { stat_count: 2070 },
        production_consumer: false,
        production_safe: false,
      },
      modifiers: {
        source_path: "D:\\Forge\\le-the-forge\\docs\\generated\\v2_modifier_registry.json",
        modifier_count: 19398,
        summary: {
          modifier_count: 19398,
          stat_count: 2070,
          stable_calculable_count: 0,
          value_scale_status_counts: { source_units: 6248, unknown: 13150 },
          operation_counts: { unknown: 11606, flat: 4627, increased: 1112 },
          blocked_reason_counts: {
            support_status_not_trusted: 19398,
            value_scale_not_planner_normalized: 19398,
            operation_unknown: 11606,
          },
          unresolved_skill_reference_count: 2,
          ambiguous_skill_reference_count: 1,
        },
        production_consumer: false,
        production_safe: false,
      },
    },
  };
}
