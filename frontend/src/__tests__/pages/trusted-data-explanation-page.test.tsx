import { MemoryRouter, Route, Routes } from "react-router-dom";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import TrustedDataExplanationPage from "@/pages/TrustedDataExplanationPage";

describe("TrustedDataExplanationPage", () => {
  it("renders trusted-data explanation", () => {
    renderPage();

    expect(screen.getByRole("heading", { name: "Understanding trusted data" })).toBeInTheDocument();
    expect(screen.getByText(/Trusted data means EpochForge can trace where the data came from/)).toBeInTheDocument();
  });

  it("explains display-only data", () => {
    renderPage();

    expect(screen.getByText("Display-only data")).toBeInTheDocument();
    expect(screen.getByText(/not used for damage, defense, crafting, or build output/)).toBeInTheDocument();
  });

  it("explains not planner-calculable status", () => {
    renderPage();

    expect(screen.getByText("Not planner-calculable")).toBeInTheDocument();
    expect(screen.getByText(/will not use this data to change DPS, EHP, recommendations, or build output yet/)).toBeInTheDocument();
  });

  it("explains audit-only value normalization", () => {
    renderPage();

    expect(screen.getByText("Audit-only value normalization")).toBeInTheDocument();
    expect(screen.getByText(/not safely converting those values into planner math yet/)).toBeInTheDocument();
  });

  it("explains unsupported mechanics are not guessed", () => {
    renderPage();

    expect(screen.getByText("Unsupported mechanics")).toBeInTheDocument();
    expect(screen.getByText(/Unsupported mechanics are shown instead of guessed/)).toBeInTheDocument();
  });

  it("explains unresolved skill identity gaps are not bridged", () => {
    renderPage();

    expect(screen.getByText("Skill identity gaps")).toBeInTheDocument();
    expect(screen.getByText(/does not bridge them from display names, nested evidence, or tooltip text/)).toBeInTheDocument();
  });

  it("does not imply production planner consumption", () => {
    renderPage();

    expect(screen.getByText(/none of it is used to change production planner calculations yet/)).toBeInTheDocument();
    expect(screen.getByText(/production planner consumption is enabled/)).toBeInTheDocument();
    expect(screen.queryByText(/v2 data powers production planner calculations/i)).not.toBeInTheDocument();
  });

  it("uses shared v2.5 trust and limitation components", () => {
    renderPage();

    expect(screen.getByText("Generated")).toBeInTheDocument();
    expect(screen.getByText("Validated")).toBeInTheDocument();
    expect(screen.getByText("Display Only")).toBeInTheDocument();
    expect(screen.getByText("What this means")).toBeInTheDocument();
    expect(screen.getByText(/Production planner unchanged:/)).toBeInTheDocument();
  });

  it("route renders the page", () => {
    render(
      <MemoryRouter initialEntries={["/trusted-data"]}>
        <Routes>
          <Route path="/trusted-data" element={<TrustedDataExplanationPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "Understanding trusted data" })).toBeInTheDocument();
  });
});

function renderPage() {
  render(
    <MemoryRouter>
      <TrustedDataExplanationPage />
    </MemoryRouter>,
  );
}
