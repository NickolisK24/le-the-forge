import { MemoryRouter, Route, Routes } from "react-router-dom";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import TrustedDataExplanationPage from "@/pages/TrustedDataExplanationPage";
import TrustedDataSupportMatrixPage from "@/pages/TrustedDataSupportMatrixPage";
import V2DebugNavigationPage from "@/pages/debug/V2DebugNavigationPage";

describe("TrustedDataSupportMatrixPage", () => {
  it("renders the support matrix page", () => {
    renderPage();

    expect(screen.getByRole("heading", { name: "What EpochForge can safely show today" })).toBeInTheDocument();
    expect(screen.getByText(/separates trusted visibility from planner calculation support/)).toBeInTheDocument();
  });

  it("route renders the matrix", () => {
    render(
      <MemoryRouter initialEntries={["/trusted-data/support"]}>
        <Routes>
          <Route path="/trusted-data/support" element={<TrustedDataSupportMatrixPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "What EpochForge can safely show today" })).toBeInTheDocument();
  });

  it("shows all major domains", () => {
    renderPage();

    for (const domain of [
      "Items / item bases",
      "Affixes",
      "Unique/set items",
      "Idols",
      "Classes/masteries",
      "Passive trees",
      "Skills / skill trees",
      "Stats",
      "Modifiers",
      "Planner adapter",
    ]) {
      expect(screen.getByText(domain)).toBeInTheDocument();
    }
  });

  it("explains planner-calculable and stable-calculable are unavailable", () => {
    renderPage();

    expect(screen.getByText(/Planner-calculable count is 0/)).toBeInTheDocument();
    expect(screen.getByText(/Stable-calculable count is 0/)).toBeInTheDocument();
    expect(screen.getByText(/Planner-calculable and stable-calculable counts remain 0/)).toBeInTheDocument();
  });

  it("explains audit-only value normalization and unbridged skill identity gaps", () => {
    renderPage();

    expect(screen.getAllByText(/Value normalization is audit-only/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/Skill identity bridge status is unbridged/)).toBeInTheDocument();
    expect(screen.getByText(/Unresolved and ambiguous skill identity refs are unbridged/)).toBeInTheDocument();
  });

  it("explains planner adapter is read-only and disabled by default", () => {
    renderPage();

    expect(screen.getByText("Read-only disabled")).toBeInTheDocument();
    expect(screen.getByText(/Adapter context is diagnostic-only and disabled by default/)).toBeInTheDocument();
  });

  it("does not imply production planner consumption", () => {
    renderPage();

    expect(screen.getByText(/Production planner consumption is false/)).toBeInTheDocument();
    expect(screen.getByText(/Production planner unchanged:/)).toBeInTheDocument();
    expect(screen.queryByText(/production planner calculations are powered by v2/i)).not.toBeInTheDocument();
  });

  it("trusted-data page links to the support matrix", () => {
    render(
      <MemoryRouter>
        <TrustedDataExplanationPage />
      </MemoryRouter>,
    );

    expect(screen.getByRole("link", { name: "Open support matrix" })).toHaveAttribute("href", "/trusted-data/support");
  });

  it("debug navigation page links to the support matrix", () => {
    render(
      <MemoryRouter>
        <V2DebugNavigationPage />
      </MemoryRouter>,
    );

    expect(screen.getByRole("link", { name: /Support Matrix/i })).toHaveAttribute("href", "/trusted-data/support");
  });
});

function renderPage() {
  render(
    <MemoryRouter>
      <TrustedDataSupportMatrixPage />
    </MemoryRouter>,
  );
}
