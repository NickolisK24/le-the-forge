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
    expect(screen.getByText("This page reads the v2 canonical affix bundle for diagnostics and does not power planner behavior.")).toBeInTheDocument();
  });

  it("renders successful summary counts and debug labels", async () => {
    mockFetch(successPayload());

    render(<ForgeSafeAffixesDebugPage />);

    expect(await screen.findByText("1098")).toBeInTheDocument();
    expect(screen.getAllByText("v2_affix_bundle").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("pass")).toBeInTheDocument();
    expect(screen.getAllByText("partial: 1098").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("equipment: 615, idol: 483")).toBeInTheDocument();
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
    fireEvent.change(screen.getByLabelText(/Affix ID/i), { target: { value: "affix:equipment:7" } });
    fireEvent.click(screen.getByLabelText(/Include modifier detail/i));
    fireEvent.click(screen.getByRole("button", { name: "Load debug data" }));

    await waitFor(() => {
      expect(fetch).toHaveBeenLastCalledWith("/experimental/v2/affixes?limit=2&include_modifiers=true&affix_id=affix%3Aequipment%3A7");
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
    data_source: "v2_affix_bundle",
    source_path: "D:\\Forge\\le-the-forge\\docs\\generated\\v2_affix_bundle.json",
    total_loaded_count: 1098,
    total_affixes: 1098,
    total_modifiers: 1624,
    warning_count: 0,
    warnings: [],
    export_policy: "v2_affix_bundle",
    export_status: "pass",
    summary: {
      support_status_counts: { partial: 1098 },
      affix_domain_counts: { equipment: 615, idol: 483 },
    },
    result_count: 1,
    records: [
      {
        canonical_id: "affix:equipment:0",
        display_name: "Void Penetration",
        support_status: "partial",
        trust_level: "generated_from_game_data",
        provenance: {
          source_path: "exports_json/affixes.json",
          source_type: "equipment",
          extraction_method: "forge_safe_affix_bundle",
          schema_version: "v2.affix_bundle.1",
          notes: [],
          raw_reference: {},
        },
        source_id: "equipment:0",
        source_file: "exports_json/affixes.json",
        patch_version: null,
        source_type: "equipment",
        affix_domain: "equipment",
        affix_type: "prefix",
        prefix_suffix: "prefix",
        item_applicability: ["AMULET"],
        slot_restrictions: ["AMULET"],
        item_type_restrictions: ["AMULET"],
        class_restrictions: [],
        mastery_restrictions: [],
        tier_ranges: [{ tier: 1, min_value: 1, max_value: 2 }],
        modifier_references: [{ modifier_id: "equipment:0", property: "Penetration" }],
        modifier_reference_count: 1,
        value_scale_policy: "source_units_preserved_pending_v2_value_normalization",
        polarity_policy: "source_sign_preserved_no_inference",
        stable_calculable: false,
        warnings: [],
        raw_reference: {},
        normalized_fields: {},
        consumer_safe_fields: {},
      },
    ],
  };
}
