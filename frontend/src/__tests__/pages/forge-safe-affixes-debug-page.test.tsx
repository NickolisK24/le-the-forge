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
      error: "experimental_catalog_disabled",
      message: "Forge-safe affix catalog is disabled.",
    });

    render(<ForgeSafeAffixesDebugPage />);

    expect(await screen.findByText("Debug endpoint unavailable")).toBeInTheDocument();
    expect(screen.getByText("Forge-safe affix catalog is disabled.")).toBeInTheDocument();
    expect(screen.getByText("This page is debug-only and does not power planner behavior.")).toBeInTheDocument();
  });

  it("renders successful summary counts and debug labels", async () => {
    mockFetch(successPayload());

    render(<ForgeSafeAffixesDebugPage />);

    expect(await screen.findByText("1098")).toBeInTheDocument();
    expect(screen.getByText("deterministic_affix_bundle")).toBeInTheDocument();
    expect(screen.getByText("pass")).toBeInTheDocument();
    expect(screen.getByText("1227")).toBeInTheDocument();
    expect(screen.getByText("129")).toBeInTheDocument();
    expect(screen.getAllByText("true").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("Production consumer")).toBeInTheDocument();
    expect(screen.getByText("false")).toBeInTheDocument();
    expect(screen.getByText("Void Penetration")).toBeInTheDocument();
    expect(screen.getByText("1624")).toBeInTheDocument();
    expect(screen.getAllByText("1").length).toBeGreaterThanOrEqual(1);
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
    fireEvent.click(screen.getByLabelText(/Include modifier detail/i));
    fireEvent.click(screen.getByRole("button", { name: "Load debug data" }));

    await waitFor(() => {
      expect(fetch).toHaveBeenLastCalledWith("/experimental/forge-safe-affixes?limit=2&include_modifiers=true&affix_id=7");
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
    experimental: true,
    debug_only: true,
    read_only: true,
    production_consumer: false,
    data_source: "forge_safe_affix_bundle",
    source_path: "D:\\Forge\\last-epoch-data\\docs\\generated\\forge_safe_affix_bundle.json",
    total_loaded_count: 1098,
    total_affixes: 1098,
    total_modifiers: 1624,
    warning_count: 0,
    warnings: [],
    export_policy: "deterministic_affix_bundle",
    export_status: "pass",
    total_affix_records_seen: 1227,
    excluded_affix_records: 129,
    result_count: 1,
    records: [
      {
        affix_id: 0,
        affix_name: "Void Penetration",
        source_type: "equipment",
        item_type: "Equipment",
        eligible_item_types: ["AMULET"],
        modifier_count: 1,
      },
    ],
  };
}
