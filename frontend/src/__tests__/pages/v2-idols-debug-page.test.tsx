import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";

import V2IdolsDebugPage from "@/pages/debug/V2IdolsDebugPage";

describe("V2IdolsDebugPage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders disabled response clearly", async () => {
    mockFetch({ success: false, error: "v2_idol_bundle_missing", message: "v2 idol bundle not found" });

    render(<V2IdolsDebugPage />);

    expect(await screen.findByText("Debug endpoint unavailable")).toBeInTheDocument();
    expect(screen.getByText("v2 idol bundle not found")).toBeInTheDocument();
  });

  it("renders idol summary and rows", async () => {
    mockFetch(successPayload());

    render(<V2IdolsDebugPage />);

    expect(await screen.findByText("71")).toBeInTheDocument();
    expect(screen.getByText("483")).toBeInTheDocument();
    expect(screen.getByText("Small Eterran Idol")).toBeInTheDocument();
    expect(screen.getByText("idol:25:0")).toBeInTheDocument();
    expect(screen.getByText("idol_1x1_eterra")).toBeInTheDocument();
  });

  it("uses controls when loading", async () => {
    mockFetch(successPayload());

    render(<V2IdolsDebugPage />);
    await screen.findByText("Small Eterran Idol");

    fireEvent.change(screen.getByLabelText(/Limit/i), { target: { value: "2" } });
    fireEvent.change(screen.getByLabelText(/Search/i), { target: { value: "small" } });
    fireEvent.change(screen.getByLabelText(/Shape/i), { target: { value: "idol_1x1_eterra" } });
    fireEvent.click(screen.getByRole("button", { name: "Load debug data" }));

    await waitFor(() => {
      expect(fetch).toHaveBeenLastCalledWith("/experimental/v2/idols?limit=2&q=small&shape=idol_1x1_eterra");
    });
  });
});

function mockFetch(payload: unknown) {
  vi.mocked(fetch).mockResolvedValue({ json: async () => payload } as Response);
}

function successPayload() {
  return {
    success: true,
    read_only: true,
    production_consumer: false,
    data_source: "v2_idol_bundle",
    source_path: "D:\\Forge\\le-the-forge\\docs\\generated\\v2_idol_bundle.json",
    total_idols: 71,
    total_idol_affixes: 483,
    result_count: 1,
    summary: {
      support_status_counts: { partial: 71 },
      idol_shape_counts: { idol_1x1_eterra: 3 },
    },
    records: [
      {
        canonical_id: "idol:25:0",
        display_name: "Small Eterran Idol",
        source_id: "idol:25:0",
        source_file: "items.json",
        support_status: "partial",
        trust_level: "generated_from_game_data",
        provenance: { source_path: "items.json" },
        item_category: "idol",
        item_type: "IDOL_1x1_ETERRA",
        equipment_slot: "idol",
        slot: "idol",
        subtype: "Small Eterran Idol",
        classification: "idol",
        idol_size: "Small Idol",
        idol_shape: "idol_1x1_eterra",
        dimensions: { width: 1, height: 1 },
        class_restrictions: [],
        mastery_restrictions: [],
        implicit_ids: [],
        allowed_affix_ids: [],
        stable_calculable: false,
      },
    ],
  };
}
