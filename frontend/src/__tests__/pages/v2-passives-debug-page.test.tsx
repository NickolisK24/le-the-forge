import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";

import V2PassivesDebugPage from "@/pages/debug/V2PassivesDebugPage";

describe("V2PassivesDebugPage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders disabled response clearly", async () => {
    mockFetch({ success: false, error: "v2_passive_tree_bundle_missing", message: "v2 passive tree bundle not found" });

    render(<V2PassivesDebugPage />);

    expect(await screen.findByText("Debug endpoint unavailable")).toBeInTheDocument();
    expect(screen.getByText("v2 passive tree bundle not found")).toBeInTheDocument();
  });

  it("renders passive summary and rows", async () => {
    mockFetch(successPayload());

    render(<V2PassivesDebugPage />);

    expect(await screen.findByText("5")).toBeInTheDocument();
    expect(screen.getByText("535")).toBeInTheDocument();
    expect(screen.getByText("Mage Passive Tree")).toBeInTheDocument();
    expect(screen.getByText("passive_tree:mg_1")).toBeInTheDocument();
    expect(screen.getByText("class:mage")).toBeInTheDocument();
  });

  it("uses controls when loading", async () => {
    mockFetch(successPayload());

    render(<V2PassivesDebugPage />);
    await screen.findByText("passive_tree:mg_1");

    fireEvent.change(screen.getByLabelText(/Limit/i), { target: { value: "2" } });
    fireEvent.change(screen.getByLabelText(/Search/i), { target: { value: "mage" } });
    fireEvent.change(screen.getByLabelText(/Class ID/i), { target: { value: "class:mage" } });
    fireEvent.click(screen.getByRole("button", { name: "Load debug data" }));

    await waitFor(() => {
      expect(fetch).toHaveBeenLastCalledWith("/experimental/v2/passives?limit=2&q=mage&class_id=class%3Amage");
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
    data_source: "v2_passive_tree_bundle",
    source_path: "D:\\Forge\\le-the-forge\\docs\\generated\\v2_passive_tree_bundle.json",
    total_passive_trees: 5,
    total_passive_nodes: 535,
    result_count: 1,
    summary: {
      support_status_counts: { partial: 540 },
      special_behavior_classification_counts: { partial_modifier: 72, unsupported_special_behavior: 254 },
    },
    records: [
      {
        canonical_id: "passive_tree:mg_1",
        display_name: "Mage Passive Tree",
        source_id: "mg-1",
        source_file: "passive_trees.json",
        support_status: "partial",
        trust_level: "generated_from_game_data",
        provenance: { source_path: "passive_trees.json" },
        owner_class_id: "class:mage",
        owner_mastery_id: null,
        source_tree_id: "mg-1",
        node_ids: ["passive_node:mg_1:1"],
        edges: [],
        stable_calculable: false,
      },
    ],
  };
}
