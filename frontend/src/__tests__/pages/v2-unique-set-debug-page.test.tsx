import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";

import V2UniqueSetDebugPage from "@/pages/debug/V2UniqueSetDebugPage";

describe("V2UniqueSetDebugPage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders disabled response clearly", async () => {
    mockFetch({
      success: false,
      error: "v2_unique_set_bundle_missing",
      message: "v2 unique bundle not found",
    });

    render(<V2UniqueSetDebugPage />);

    expect(await screen.findByText("Debug endpoint unavailable")).toBeInTheDocument();
    expect(screen.getByText("v2 unique bundle not found")).toBeInTheDocument();
  });

  it("renders unique summary and rows", async () => {
    mockFetch(successPayload());

    render(<V2UniqueSetDebugPage />);

    expect(await screen.findByText("409")).toBeInTheDocument();
    expect(screen.getByText("23")).toBeInTheDocument();
    expect(screen.getByText("partial_modifier: 385, text_only_effect: 24")).toBeInTheDocument();
    expect(screen.getByText("Calamity")).toBeInTheDocument();
    expect(screen.getByText("unique:0")).toBeInTheDocument();
    expect(screen.getByText("partial_modifier")).toBeInTheDocument();
  });

  it("uses controls when loading", async () => {
    mockFetch(successPayload());

    render(<V2UniqueSetDebugPage />);
    await screen.findByText("Calamity");

    fireEvent.change(screen.getByLabelText(/Limit/i), { target: { value: "2" } });
    fireEvent.change(screen.getByLabelText(/Search/i), { target: { value: "calamity" } });
    fireEvent.change(screen.getByLabelText(/Slot/i), { target: { value: "helmet" } });
    fireEvent.click(screen.getByRole("button", { name: "Load debug data" }));

    await waitFor(() => {
      expect(fetch).toHaveBeenLastCalledWith("/experimental/v2/uniques?limit=2&q=calamity&slot=helmet");
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
    read_only: true,
    production_consumer: false,
    data_source: "v2_unique_bundle",
    source_path: "D:\\Forge\\le-the-forge\\docs\\generated\\v2_unique_bundle.json",
    total_uniques: 409,
    total_sets: 23,
    total_set_items: 59,
    total_set_bonuses: 45,
    result_count: 1,
    summary: {
      special_mechanic_classification_counts: { partial_modifier: 385, text_only_effect: 24 },
    },
    records: [
      {
        canonical_id: "unique:0",
        display_name: "Calamity",
        source_id: "unique:0",
        source_file: "uniques.json",
        support_status: "partial",
        trust_level: "generated_from_game_data",
        provenance: {
          source_path: "uniques.json",
          source_type: "unique",
          extraction_method: "last_epoch_unique_set_export",
          schema_version: "v2.unique_set.1",
          notes: [],
          raw_reference: {},
        },
        item_category: "equipment",
        item_type: "helmet",
        equipment_slot: "helmet",
        slot: "helmet",
        subtype: "Leather Helmet",
        classification: "armor",
        level_requirement: 7,
        class_restrictions: [],
        implicit_ids: [],
        unique_effect_text: [],
        modifier_references: [{ modifier_id: "unique_modifier:unique:0:0", property: "Damage" }],
        special_mechanic_classification: "partial_modifier",
        stable_calculable: false,
        warnings: [],
        raw_reference: {},
        normalized_fields: {},
        consumer_safe_fields: {},
      },
    ],
  };
}
