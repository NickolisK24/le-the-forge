import fs from "node:fs";

import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";

import V2DebugNavigationPage from "@/pages/debug/V2DebugNavigationPage";

describe("V2DebugNavigationPage", () => {
  it("renders trusted-data debug navigation", () => {
    renderPage();

    expect(screen.getByRole("heading", { name: "v2 trusted-data debug pages" })).toBeInTheDocument();
    expect(screen.getByText(/read-only inspection surfaces/)).toBeInTheDocument();
  });

  it("links trusted-data and stats modifiers pages", () => {
    renderPage();

    expect(screen.getByRole("link", { name: /Trusted Data Explanation/i })).toHaveAttribute("href", "/trusted-data");
    expect(screen.getByRole("link", { name: /Stats \/ Modifiers/i })).toHaveAttribute("href", "/debug/v2-stats-modifiers");
  });

  it("links the canonical forge-safe affix route", () => {
    renderPage();

    expect(screen.getByRole("link", { name: /Forge-Safe Affixes/i })).toHaveAttribute("href", "/debug/forge-safe-affixes");
    expect(screen.getByText(/canonical affix debug page is/)).toBeInTheDocument();
    expect(screen.getAllByText("/debug/v2-affixes").length).toBeGreaterThanOrEqual(1);
  });

  it("links all current v2 debug pages", () => {
    renderPage();

    for (const path of [
      "/debug/v2-items",
      "/debug/v2-unique-sets",
      "/debug/v2-idols",
      "/debug/v2-classes",
      "/debug/v2-passives",
      "/debug/v2-skills",
    ]) {
      expect(screen.getByRole("link", { name: (_, element) => element?.getAttribute("href") === path })).toBeInTheDocument();
    }
  });

  it("does not imply production planner support", () => {
    renderPage();

    expect(screen.getByText(/They do not power production planner calculations/)).toBeInTheDocument();
    expect(screen.getByText(/Production planner unchanged:/)).toBeInTheDocument();
    expect(screen.queryByText(/production planner calculations are enabled/i)).not.toBeInTheDocument();
  });

  it("route renders the page", () => {
    render(
      <MemoryRouter initialEntries={["/debug/v2"]}>
        <Routes>
          <Route path="/debug/v2" element={<V2DebugNavigationPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "v2 trusted-data debug pages" })).toBeInTheDocument();
  });

  it("registers the v2 affix alias in App routes", () => {
    const app = fs.readFileSync("src/App.tsx", "utf8");

    expect(app).toContain('path="/debug/v2-affixes"');
    expect(app).toContain('to="/debug/forge-safe-affixes"');
  });

  it("registers v2.5 debug routes outside the development-only debug block", () => {
    const app = fs.readFileSync("src/App.tsx", "utf8");
    const v25RouteIndex = app.indexOf('path="/debug/v2"');
    const devOnlyBlockIndex = app.indexOf("{IS_DEV &&");

    expect(v25RouteIndex).toBeGreaterThan(-1);
    expect(devOnlyBlockIndex).toBeGreaterThan(-1);
    expect(v25RouteIndex).toBeLessThan(devOnlyBlockIndex);
    expect(app.indexOf('path="/debug"', devOnlyBlockIndex)).toBeGreaterThan(devOnlyBlockIndex);
  });
});

function renderPage() {
  render(
    <MemoryRouter>
      <V2DebugNavigationPage />
    </MemoryRouter>,
  );
}
