import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";

import ForgeSafeAffixesDebugPage from "@/pages/debug/ForgeSafeAffixesDebugPage";

describe("ForgeSafeAffixesDebugPage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders disabled response clearly", async () => {
    mockFetch({
      success: false,
      error: "debug_endpoint_disabled",
      message: "Forge-safe affix debug endpoint is disabled.",
    });

    render(<ForgeSafeAffixesDebugPage />);

    expect(await screen.findByText("Debug endpoint unavailable")).toBeInTheDocument();
    expect(screen.getByText("Forge-safe affix debug endpoint is disabled.")).toBeInTheDocument();
    expect(screen.getByText("This page is debug-only and does not power planner behavior.")).toBeInTheDocument();
  });

  it("renders successful summary counts and debug labels", async () => {
    mockFetch(successPayload());

    render(<ForgeSafeAffixesDebugPage />);

    expect(await screen.findByText("573")).toBeInTheDocument();
    expect(screen.getByText("deterministic_affix_only")).toBeInTheDocument();
    expect(screen.getByText("warning")).toBeInTheDocument();
    expect(screen.getByText("1227")).toBeInTheDocument();
    expect(screen.getByText("654")).toBeInTheDocument();
    expect(screen.getAllByText("true").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("Production consumer")).toBeInTheDocument();
    expect(screen.getByText("false")).toBeInTheDocument();
    expect(screen.getByText("Void Penetration")).toBeInTheDocument();
  });

  it("renders loader warnings", async () => {
    mockFetch({
      ...successPayload(),
      warning_count: 1,
      warnings: ["summary.exported_affix_records=2 does not match loaded record count 1."],
    });

    render(<ForgeSafeAffixesDebugPage />);

    expect(await screen.findByText(/summary\.exported_affix_records=2 does not match loaded record count 1\./)).toBeInTheDocument();
  });

  it("uses limit and affix id controls when loading", async () => {
    mockFetch(successPayload());

    render(<ForgeSafeAffixesDebugPage />);
    await screen.findByText("Void Penetration");

    fireEvent.change(screen.getByLabelText(/Limit/i), { target: { value: "2" } });
    fireEvent.change(screen.getByLabelText(/Affix ID/i), { target: { value: "7" } });
    fireEvent.click(screen.getByRole("button", { name: "Load debug data" }));

    await waitFor(() => {
      expect(fetch).toHaveBeenLastCalledWith("/debug/forge-safe-affixes?limit=2&affix_id=7");
    });
  });
});

function mockFetch(payload: unknown) {
  vi.mocked(fetch).mockResolvedValue({
    json: async () => payload,
  } as Response);
}

function successPayload() {
  return {
    success: true,
    debug_only: true,
    read_only: true,
    production_consumer: false,
    source_path: "D:\\Forge\\last-epoch-data\\docs\\generated\\forge_safe_canonical_affixes.json",
    loaded_record_count: 573,
    warning_count: 0,
    warnings: [],
    export_policy: "deterministic_affix_only",
    export_status: "warning",
    total_affix_records_seen: 1227,
    excluded_affix_records: 654,
    sample_count: 1,
    sample_records: [
      {
        affix_id: 0,
        name: "Void Penetration",
        source_type: "equipment",
        item_type: "Equipment",
        eligible_item_types: ["AMULET"],
      },
    ],
  };
}
