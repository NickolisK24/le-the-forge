import { MemoryRouter, Route, Routes } from "react-router-dom";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import PreV3MechanicalReadinessPage from "@/pages/PreV3MechanicalReadinessPage";
import TrustedDataExplanationPage from "@/pages/TrustedDataExplanationPage";
import TrustedDataSupportMatrixPage from "@/pages/TrustedDataSupportMatrixPage";
import V2DebugNavigationPage from "@/pages/debug/V2DebugNavigationPage";

describe("PreV3MechanicalReadinessPage", () => {
  it("renders the readiness dashboard", () => {
    renderPage();

    expect(screen.getByRole("heading", { name: "Mechanical readiness before v3" })).toBeInTheDocument();
    expect(screen.getByText(/will not use it to change build output yet/)).toBeInTheDocument();
  });

  it("route renders the dashboard", () => {
    render(
      <MemoryRouter initialEntries={["/trusted-data/pre-v3-readiness"]}>
        <Routes>
          <Route path="/trusted-data/pre-v3-readiness" element={<PreV3MechanicalReadinessPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "Mechanical readiness before v3" })).toBeInTheDocument();
  });

  it("shows readiness decisions and zero calculable counts", () => {
    renderPage();

    expect(screen.getByText("v2 Infrastructure")).toBeInTheDocument();
    expect(screen.getByText("Ready")).toBeInTheDocument();
    expect(screen.getByText("Production Planner")).toBeInTheDocument();
    expect(screen.getAllByText("Not Ready").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("Mechanical Remap")).toBeInTheDocument();
    expect(screen.getByText("Planner-Calculable Records")).toBeInTheDocument();
    expect(screen.getByText("Stable-Calculable Records")).toBeInTheDocument();
    expect(screen.getAllByText("0").length).toBeGreaterThanOrEqual(2);
  });

  it("explains audit-only value normalization and unbridged skill identity", () => {
    renderPage();

    expect(screen.getByText("Value Normalization")).toBeInTheDocument();
    expect(screen.getAllByText("Audit Only").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Skill Identity Bridge")).toBeInTheDocument();
    expect(screen.getByText("Unbridged")).toBeInTheDocument();
    expect(screen.getByText(/Skill identity gaps are shown honestly and are not bridged by guessing/)).toBeInTheDocument();
  });

  it("explains golden baselines are required", () => {
    renderPage();

    expect(screen.getByText("Golden Baselines")).toBeInTheDocument();
    expect(screen.getByText("Planned / Partial Scaffold")).toBeInTheDocument();
    expect(screen.getByText(/Golden baselines are required before any future remap can be trusted/)).toBeInTheDocument();
  });

  it("does not imply v3 mechanical work has started", () => {
    renderPage();

    expect(screen.getByText(/What v3 must prove/)).toBeInTheDocument();
    expect(screen.queryByText(/v3 mechanical work has started/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/production planner remap is ready/i)).not.toBeInTheDocument();
  });

  it("trusted-data page links to the dashboard", () => {
    render(
      <MemoryRouter>
        <TrustedDataExplanationPage />
      </MemoryRouter>,
    );

    expect(screen.getByRole("link", { name: "Open pre-v3 readiness" })).toHaveAttribute("href", "/trusted-data/pre-v3-readiness");
  });

  it("support matrix links to the dashboard", () => {
    render(
      <MemoryRouter>
        <TrustedDataSupportMatrixPage />
      </MemoryRouter>,
    );

    expect(screen.getByRole("link", { name: "Pre-v3 readiness" })).toHaveAttribute("href", "/trusted-data/pre-v3-readiness");
  });

  it("debug navigation links to the dashboard", () => {
    render(
      <MemoryRouter>
        <V2DebugNavigationPage />
      </MemoryRouter>,
    );

    expect(screen.getByRole("link", { name: /Pre-v3 Readiness/i })).toHaveAttribute("href", "/trusted-data/pre-v3-readiness");
  });
});

function renderPage() {
  render(
    <MemoryRouter>
      <PreV3MechanicalReadinessPage />
    </MemoryRouter>,
  );
}
