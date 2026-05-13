import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";

import V2ItemsDebugPage from "@/pages/debug/V2ItemsDebugPage";

describe("V2ItemsDebugPage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders disabled response clearly", async () => {
    mockFetch({
      success: false,
      error: "v2_item_bundle_missing",
      message: "v2 item base bundle not found",
    });

    render(<V2ItemsDebugPage />);

    expect(await screen.findByText("Debug endpoint unavailable")).toBeInTheDocument();
    expect(screen.getByText("v2 item base bundle not found")).toBeInTheDocument();
  });

  it("renders item base summary and rows", async () => {
    mockFetch(successPayload());

    render(<V2ItemsDebugPage />);

    expect(await screen.findByText("542")).toBeInTheDocument();
    expect(screen.getByText("1182")).toBeInTheDocument();
    expect(screen.getAllByText("partial: 542").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("generated_from_game_data: 542")).toBeInTheDocument();
    expect(screen.getByText("Support summary")).toBeInTheDocument();
    expect(screen.getByText("Provenance")).toBeInTheDocument();
    expect(screen.getByText("Debug contract")).toBeInTheDocument();
    expect(screen.getByText("Iron Casque")).toBeInTheDocument();
    expect(screen.getByText("item_base:equippable:0:1")).toBeInTheDocument();
    expect(screen.getAllByText("helmet").length).toBeGreaterThanOrEqual(1);
  });

  it("uses controls when loading", async () => {
    mockFetch(successPayload());

    render(<V2ItemsDebugPage />);
    await screen.findByText("Iron Casque");

    fireEvent.change(screen.getByLabelText(/Limit/i), { target: { value: "2" } });
    fireEvent.change(screen.getByLabelText(/Search/i), { target: { value: "iron" } });
    fireEvent.change(screen.getByLabelText(/Slot/i), { target: { value: "helmet" } });
    fireEvent.click(screen.getByRole("button", { name: "Load debug data" }));

    await waitFor(() => {
      expect(fetch).toHaveBeenLastCalledWith("/experimental/v2/items/bases?limit=2&q=iron&slot=helmet");
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
    data_source: "v2_item_base_bundle",
    source_path: "D:\\Forge\\le-the-forge\\docs\\generated\\v2_item_base_bundle.json",
    total_item_bases: 542,
    total_implicits: 1182,
    result_count: 1,
    summary: {
      support_status_counts: { partial: 542 },
      trust_level_counts: { generated_from_game_data: 542 },
    },
    records: [
      {
        canonical_id: "item_base:equippable:0:1",
        display_name: "Iron Casque",
        source_id: "equippable:0:1",
        source_file: "items.json",
        support_status: "partial",
        trust_level: "generated_from_game_data",
        provenance: {
          source_path: "items.json",
          source_type: "item_base",
          extraction_method: "last_epoch_items_export",
          schema_version: "v2.item.1",
          notes: [],
          raw_reference: {},
        },
        item_category: "equipment",
        item_type: "helmet",
        equipment_slot: "helmet",
        slot: "helmet",
        subtype: "Iron Helmet",
        classification: "armor",
        level_requirement: 10,
        class_restrictions: [],
        implicit_ids: ["implicit:equippable:0:1:0"],
        warnings: [],
        raw_reference: {},
        normalized_fields: {},
        consumer_safe_fields: {},
      },
    ],
  };
}
