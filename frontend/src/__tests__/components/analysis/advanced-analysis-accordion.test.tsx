/**
 * AdvancedAnalysisAccordion — phase 3 tests.
 *
 * Covers:
 *   - Default state is collapsed on first mount.
 *   - Toggling updates the visual state and persists to localStorage.
 *   - Expanded state persists across remounts via localStorage.
 *   - When no slug is available, the unsaved-build explainer renders.
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

// Mock the heavy slug-scoped panels so the test doesn't spin up React Query.
vi.mock("@/components/features/build/BossEncounterPanel", () => ({
  default: ({ slug }: { slug: string }) => (
    <div data-testid="mock-boss-panel">boss:{slug}</div>
  ),
}));
vi.mock("@/components/features/build/CorruptionScalingPanel", () => ({
  default: ({ slug }: { slug: string }) => (
    <div data-testid="mock-corruption-panel">corr:{slug}</div>
  ),
}));
vi.mock("@/components/features/build/GearUpgradePanel", () => ({
  default: ({ slug }: { slug: string }) => (
    <div data-testid="mock-gear-panel">gear:{slug}</div>
  ),
}));

import AdvancedAnalysisAccordion, {
  ADVANCED_EXPANDED_KEY,
} from "@/components/features/build-workspace/analysis/AdvancedAnalysisAccordion";

beforeEach(() => {
  window.localStorage.clear();
  cleanup();
});

// ---------------------------------------------------------------------------
// Default state
// ---------------------------------------------------------------------------

describe("AdvancedAnalysisAccordion — default state", () => {
  it("is collapsed on first mount (no localStorage key yet)", () => {
    render(<AdvancedAnalysisAccordion slug="my-build" />);
    const accordion = screen.getByTestId("advanced-analysis-accordion");
    expect(accordion.getAttribute("data-open")).toBe("false");
    const toggle = screen.getByTestId("advanced-analysis-toggle");
    expect(toggle.getAttribute("aria-expanded")).toBe("false");
  });

  it("renders the full prompt-specified header", () => {
    render(<AdvancedAnalysisAccordion slug="my-build" />);
    const toggle = screen.getByTestId("advanced-analysis-toggle");
    expect(toggle.textContent?.toLowerCase()).toContain("boss encounters");
    expect(toggle.textContent?.toLowerCase()).toContain("corruption scaling");
    expect(toggle.textContent?.toLowerCase()).toContain("gear upgrades");
  });
});

// ---------------------------------------------------------------------------
// Toggle + persistence
// ---------------------------------------------------------------------------

describe("AdvancedAnalysisAccordion — persistence", () => {
  it("opens on click and writes 'true' to localStorage", () => {
    render(<AdvancedAnalysisAccordion slug="my-build" />);
    fireEvent.click(screen.getByTestId("advanced-analysis-toggle"));
    expect(
      screen.getByTestId("advanced-analysis-accordion").getAttribute("data-open"),
    ).toBe("true");
    expect(window.localStorage.getItem(ADVANCED_EXPANDED_KEY)).toBe("true");
  });

  it("closes on second click and writes 'false' to localStorage", () => {
    render(<AdvancedAnalysisAccordion slug="my-build" />);
    const toggle = screen.getByTestId("advanced-analysis-toggle");
    fireEvent.click(toggle);
    fireEvent.click(toggle);
    expect(
      screen.getByTestId("advanced-analysis-accordion").getAttribute("data-open"),
    ).toBe("false");
    expect(window.localStorage.getItem(ADVANCED_EXPANDED_KEY)).toBe("false");
  });

  it("reads the stored 'true' on remount so power users stay opted in", () => {
    window.localStorage.setItem(ADVANCED_EXPANDED_KEY, "true");
    render(<AdvancedAnalysisAccordion slug="my-build" />);
    expect(
      screen.getByTestId("advanced-analysis-accordion").getAttribute("data-open"),
    ).toBe("true");
  });

  it("reads the stored 'false' on remount and stays collapsed", () => {
    window.localStorage.setItem(ADVANCED_EXPANDED_KEY, "false");
    render(<AdvancedAnalysisAccordion slug="my-build" />);
    expect(
      screen.getByTestId("advanced-analysis-accordion").getAttribute("data-open"),
    ).toBe("false");
  });
});

// ---------------------------------------------------------------------------
// Unsaved build branch
// ---------------------------------------------------------------------------

describe("AdvancedAnalysisAccordion — unsaved build (no slug)", () => {
  it("renders the explainer and does not mount the slug-scoped panels", () => {
    render(<AdvancedAnalysisAccordion slug={null} />);
    // Expand so the body is visible to the test.
    fireEvent.click(screen.getByTestId("advanced-analysis-toggle"));
    expect(screen.getByTestId("advanced-analysis-unsaved-note")).toBeInTheDocument();
    expect(screen.queryByTestId("mock-boss-panel")).toBeNull();
    expect(screen.queryByTestId("mock-corruption-panel")).toBeNull();
    expect(screen.queryByTestId("mock-gear-panel")).toBeNull();
  });
});

describe("AdvancedAnalysisAccordion — saved build (slug present)", () => {
  it("passes the slug through to each leaf panel", () => {
    render(<AdvancedAnalysisAccordion slug="my-build-slug" />);
    fireEvent.click(screen.getByTestId("advanced-analysis-toggle"));
    expect(screen.getByTestId("mock-boss-panel")).toHaveTextContent("my-build-slug");
    expect(screen.getByTestId("mock-corruption-panel")).toHaveTextContent("my-build-slug");
    expect(screen.getByTestId("mock-gear-panel")).toHaveTextContent("my-build-slug");
  });
});
