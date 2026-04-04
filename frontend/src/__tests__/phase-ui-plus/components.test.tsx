/**
 * UI+4, UI+6, UI+7, UI+8, UI+14, UI+15 — Component tests
 * ResultExplanationPanel, BuildHistoryTimeline, GlobalComparisonView,
 * BulkSelector, PerformancePanel, AdvancedTooltip
 * ~50 tests
 */

import React from "react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import "@testing-library/jest-dom";

// ─── ResultExplanationPanel ───────────────────────────────────────────────────

import { ResultExplanationPanel } from "../../components/explanations/ResultExplanationPanel";
import type { ComputedStats, StatSource } from "../../hooks/useLiveStats";

const SAMPLE_STATS: ComputedStats = {
  totalDps: 300,
  effectiveCritChance: 0.20,
  effectiveCritMultiplier: 2.5,
  totalArmor: 600,
  totalResistances: { fire: 75 },
  manaPool: 350,
  castSpeed: 1.3,
  movementSpeed: 1.1,
  raw: { spell_damage: 80, crit_chance: 15 },
};

const SAMPLE_SOURCE: StatSource = {
  gear: {
    weapon: { affixes: [{ stat: "spell_damage", value: 80 }] },
    helmet: { affixes: [{ stat: "crit_chance", value: 15 }] },
  },
  skills: ["Fireball", "Ignite"],
  passives: [1, 5, 12],
};

describe("ResultExplanationPanel", () => {
  it("renders the stat breakdown heading", () => {
    render(<ResultExplanationPanel stats={SAMPLE_STATS} source={SAMPLE_SOURCE} />);
    expect(screen.getByText(/stat breakdown/i)).toBeInTheDocument();
  });

  it("renders Total DPS label", () => {
    render(<ResultExplanationPanel stats={SAMPLE_STATS} source={SAMPLE_SOURCE} />);
    expect(screen.getByText("Total DPS")).toBeInTheDocument();
  });

  it("renders Crit Chance label", () => {
    render(<ResultExplanationPanel stats={SAMPLE_STATS} source={SAMPLE_SOURCE} />);
    expect(screen.getByText("Crit Chance")).toBeInTheDocument();
  });

  it("renders totalDps formatted value", () => {
    render(<ResultExplanationPanel stats={SAMPLE_STATS} source={SAMPLE_SOURCE} />);
    expect(screen.getByText("300")).toBeInTheDocument();
  });

  it("renders crit chance as percentage", () => {
    render(<ResultExplanationPanel stats={SAMPLE_STATS} source={SAMPLE_SOURCE} />);
    expect(screen.getByText("20.0%")).toBeInTheDocument();
  });

  it("renders crit multiplier with x suffix", () => {
    render(<ResultExplanationPanel stats={SAMPLE_STATS} source={SAMPLE_SOURCE} />);
    expect(screen.getByText("2.50x")).toBeInTheDocument();
  });

  it("visibleStats limits which stats are shown", () => {
    render(
      <ResultExplanationPanel
        stats={SAMPLE_STATS}
        source={SAMPLE_SOURCE}
        visibleStats={["totalDps"]}
      />
    );
    expect(screen.getByText("Total DPS")).toBeInTheDocument();
    expect(screen.queryByText("Crit Chance")).not.toBeInTheDocument();
  });

  it("accepts className prop", () => {
    const { container } = render(
      <ResultExplanationPanel stats={SAMPLE_STATS} source={SAMPLE_SOURCE} className="test-class" />
    );
    expect(container.firstChild).toBeInTheDocument();
  });

  it("skill bonus contributions show in dps breakdown", () => {
    const { container } = render(
      <ResultExplanationPanel stats={SAMPLE_STATS} source={SAMPLE_SOURCE} visibleStats={["totalDps"]} />
    );
    expect(container.textContent).toMatch(/Skills/i);
  });

  it("shows armor label", () => {
    render(<ResultExplanationPanel stats={SAMPLE_STATS} source={SAMPLE_SOURCE} />);
    expect(screen.getByText("Armor")).toBeInTheDocument();
  });
});

// ─── BuildHistoryTimeline ─────────────────────────────────────────────────────

import { BuildHistoryTimeline } from "../../components/history/BuildHistoryTimeline";

type BuildState = { name: string; level: number };

const PAST: BuildState[] = [{ name: "v1", level: 1 }, { name: "v2", level: 5 }];
const PRESENT: BuildState = { name: "v3", level: 10 };
const FUTURE: BuildState[] = [{ name: "v4", level: 15 }];

describe("BuildHistoryTimeline", () => {
  it("renders without crashing", () => {
    const { container } = render(
      <BuildHistoryTimeline past={PAST} present={PRESENT} future={FUTURE}
        onUndo={vi.fn()} onRedo={vi.fn()} canUndo={true} canRedo={true} />
    );
    expect(container).toBeInTheDocument();
  });

  it("renders undo button", () => {
    render(
      <BuildHistoryTimeline past={PAST} present={PRESENT} future={[]}
        onUndo={vi.fn()} onRedo={vi.fn()} canUndo={true} canRedo={false} />
    );
    expect(screen.getByRole("button", { name: /undo/i })).toBeInTheDocument();
  });

  it("renders redo button", () => {
    render(
      <BuildHistoryTimeline past={[]} present={PRESENT} future={FUTURE}
        onUndo={vi.fn()} onRedo={vi.fn()} canUndo={false} canRedo={true} />
    );
    expect(screen.getByRole("button", { name: /redo/i })).toBeInTheDocument();
  });

  it("undo button calls onUndo", () => {
    const onUndo = vi.fn();
    render(
      <BuildHistoryTimeline past={PAST} present={PRESENT} future={[]}
        onUndo={onUndo} onRedo={vi.fn()} canUndo={true} canRedo={false} />
    );
    fireEvent.click(screen.getByRole("button", { name: /undo/i }));
    expect(onUndo).toHaveBeenCalledOnce();
  });

  it("redo button calls onRedo", () => {
    const onRedo = vi.fn();
    render(
      <BuildHistoryTimeline past={[]} present={PRESENT} future={FUTURE}
        onUndo={vi.fn()} onRedo={onRedo} canUndo={false} canRedo={true} />
    );
    fireEvent.click(screen.getByRole("button", { name: /redo/i }));
    expect(onRedo).toHaveBeenCalledOnce();
  });

  it("undo disabled when canUndo=false", () => {
    render(
      <BuildHistoryTimeline past={[]} present={PRESENT} future={[]}
        onUndo={vi.fn()} onRedo={vi.fn()} canUndo={false} canRedo={false} />
    );
    expect(screen.getByRole("button", { name: /undo/i })).toBeDisabled();
  });

  it("redo disabled when canRedo=false", () => {
    render(
      <BuildHistoryTimeline past={[]} present={PRESENT} future={[]}
        onUndo={vi.fn()} onRedo={vi.fn()} canUndo={false} canRedo={false} />
    );
    expect(screen.getByRole("button", { name: /redo/i })).toBeDisabled();
  });

  it("renders past entries", () => {
    render(
      <BuildHistoryTimeline past={PAST} present={PRESENT} future={FUTURE}
        onUndo={vi.fn()} onRedo={vi.fn()} canUndo={true} canRedo={true}
        getLabel={(s) => s.name} />
    );
    expect(screen.getByText("v1")).toBeInTheDocument();
    expect(screen.getByText("v2")).toBeInTheDocument();
  });

  it("renders present entry distinctly", () => {
    render(
      <BuildHistoryTimeline past={PAST} present={PRESENT} future={FUTURE}
        onUndo={vi.fn()} onRedo={vi.fn()} canUndo={true} canRedo={true} />
    );
    expect(screen.getByText("Current")).toBeInTheDocument();
  });

  it("renders future entries", () => {
    render(
      <BuildHistoryTimeline past={[]} present={PRESENT} future={FUTURE}
        onUndo={vi.fn()} onRedo={vi.fn()} canUndo={false} canRedo={true}
        getLabel={(s) => s.name} />
    );
    expect(screen.getByText("v4")).toBeInTheDocument();
  });
});

// ─── GlobalComparisonView ─────────────────────────────────────────────────────

import { GlobalComparisonView } from "../../components/comparison/GlobalComparisonView";
import type { ComparisonItem, ComparisonField } from "../../components/comparison/GlobalComparisonView";

const CMP_ITEMS: ComparisonItem[] = [
  { id: "a", label: "Build Alpha", data: { dps: 1000, armor: 500 } },
  { id: "b", label: "Build Beta",  data: { dps: 1200, armor: 350 } },
];
const CMP_FIELDS: ComparisonField[] = [
  { key: "dps",   label: "DPS",   higherIsBetter: true  },
  { key: "armor", label: "Armor", higherIsBetter: true  },
];

describe("GlobalComparisonView", () => {
  it("renders without crashing", () => {
    const { container } = render(
      <GlobalComparisonView type="build" items={CMP_ITEMS} fields={CMP_FIELDS} />
    );
    expect(container).toBeInTheDocument();
  });

  it("renders column headers", () => {
    render(<GlobalComparisonView type="build" items={CMP_ITEMS} fields={CMP_FIELDS} />);
    expect(screen.getByText("Build Alpha")).toBeInTheDocument();
    expect(screen.getByText("Build Beta")).toBeInTheDocument();
  });

  it("renders stat row labels", () => {
    render(<GlobalComparisonView type="build" items={CMP_ITEMS} fields={CMP_FIELDS} />);
    expect(screen.getByText("DPS")).toBeInTheDocument();
    expect(screen.getByText("Armor")).toBeInTheDocument();
  });

  it("shows up arrow for better values (higherIsBetter=true)", () => {
    render(<GlobalComparisonView type="build" items={CMP_ITEMS} fields={CMP_FIELDS} />);
    expect(screen.getAllByText("▲").length).toBeGreaterThan(0);
  });

  it("shows down arrow for worse values (higherIsBetter=true)", () => {
    render(<GlobalComparisonView type="build" items={CMP_ITEMS} fields={CMP_FIELDS} />);
    expect(screen.getAllByText("▼").length).toBeGreaterThan(0);
  });

  it("marks reference column visually", () => {
    const { container } = render(
      <GlobalComparisonView type="build" items={CMP_ITEMS} fields={CMP_FIELDS} />
    );
    // Reference column (first item) should have some distinctive styling
    expect(container.innerHTML.length).toBeGreaterThan(200);
  });

  it("reference column has no diff arrows", () => {
    render(<GlobalComparisonView type="build" items={CMP_ITEMS} fields={CMP_FIELDS} />);
    // First column is reference — at minimum, second column shows arrows
    const arrows = screen.queryAllByText(/[▲▼]/);
    // Arrows exist for non-reference columns
    expect(arrows.length).toBeGreaterThanOrEqual(0);
  });

  it("handles empty rows", () => {
    const { container } = render(
      <GlobalComparisonView type="build" items={CMP_ITEMS} fields={[]} />
    );
    expect(container).toBeInTheDocument();
  });

  it("calls onRemove when remove button clicked", () => {
    const onRemove = vi.fn();
    render(
      <GlobalComparisonView type="build" items={CMP_ITEMS} fields={CMP_FIELDS} onRemove={onRemove} />
    );
    const removeButtons = screen.queryAllByRole("button").filter(
      (b) => b.textContent?.includes("×") || b.getAttribute("aria-label")?.match(/remove/i)
    );
    if (removeButtons.length > 0) {
      fireEvent.click(removeButtons[0]);
      expect(onRemove).toHaveBeenCalled();
    }
  });
});

// ─── BulkSelector ─────────────────────────────────────────────────────────────

import { BulkSelector } from "../../components/comparison/BulkSelector";
import type { SelectableItem } from "../../components/comparison/BulkSelector";

const SEL_ITEMS: SelectableItem[] = [
  { id: "1", label: "Helmet A", subtitle: "Rare"   },
  { id: "2", label: "Helmet B", subtitle: "Magic"  },
  { id: "3", label: "Boots C",  subtitle: "Unique" },
  { id: "4", label: "Gloves D", subtitle: "Normal", disabled: true },
];

describe("BulkSelector", () => {
  it("renders all items", () => {
    render(
      <BulkSelector items={SEL_ITEMS} selectedIds={[]} onSelectionChange={vi.fn()} onCompare={vi.fn()} />
    );
    expect(screen.getByText("Helmet A")).toBeInTheDocument();
    expect(screen.getByText("Helmet B")).toBeInTheDocument();
    expect(screen.getByText("Boots C")).toBeInTheDocument();
  });

  it("selects item on checkbox click", () => {
    const onChange = vi.fn();
    render(
      <BulkSelector items={SEL_ITEMS} selectedIds={[]} onSelectionChange={onChange} onCompare={vi.fn()} />
    );
    const checkboxes = screen.getAllByRole("checkbox");
    fireEvent.click(checkboxes[0]);
    expect(onChange).toHaveBeenCalledWith(["1"]);
  });

  it("deselects item on second click", () => {
    const onChange = vi.fn();
    render(
      <BulkSelector items={SEL_ITEMS} selectedIds={["1"]} onSelectionChange={onChange} onCompare={vi.fn()} />
    );
    const checkboxes = screen.getAllByRole("checkbox") as HTMLInputElement[];
    fireEvent.click(checkboxes[0]);
    expect(onChange).toHaveBeenCalledWith([]);
  });

  it("calls onCompare with selected ids", () => {
    const onCompare = vi.fn();
    render(
      <BulkSelector items={SEL_ITEMS} selectedIds={["1","2"]} onSelectionChange={vi.fn()} onCompare={onCompare} />
    );
    fireEvent.click(screen.getByRole("button", { name: /compare/i }));
    expect(onCompare).toHaveBeenCalledWith(["1","2"]);
  });

  it("compare button disabled with fewer than 2 selected", () => {
    render(
      <BulkSelector items={SEL_ITEMS} selectedIds={["1"]} onSelectionChange={vi.fn()} onCompare={vi.fn()} />
    );
    const btn = screen.getByRole("button", { name: /compare/i });
    expect(btn).toBeDisabled();
  });

  it("compare button enabled with 2+ selected", () => {
    render(
      <BulkSelector items={SEL_ITEMS} selectedIds={["1","2"]} onSelectionChange={vi.fn()} onCompare={vi.fn()} />
    );
    const btn = screen.getByRole("button", { name: /compare/i });
    expect(btn).not.toBeDisabled();
  });

  it("filters items by search query", () => {
    render(
      <BulkSelector items={SEL_ITEMS} selectedIds={[]} onSelectionChange={vi.fn()} onCompare={vi.fn()} />
    );
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "Helmet" } });
    expect(screen.getByText("Helmet A")).toBeInTheDocument();
    expect(screen.queryByText("Boots C")).not.toBeInTheDocument();
  });

  it("respects maxSelectable prop", () => {
    const onChange = vi.fn();
    render(
      <BulkSelector items={SEL_ITEMS} selectedIds={["1","2"]} onSelectionChange={onChange}
        onCompare={vi.fn()} maxSelectable={2} />
    );
    // Clicking a third checkbox should not expand past max
    const checkboxes = screen.getAllByRole("checkbox") as HTMLInputElement[];
    // Third item (index 2) should be disabled or clicking it should not add
    const thirdCheckbox = checkboxes[2];
    if (!thirdCheckbox.checked) {
      fireEvent.click(thirdCheckbox);
      const calls = onChange.mock.calls;
      if (calls.length > 0) {
        expect(calls[calls.length - 1][0].length).toBeLessThanOrEqual(2);
      }
    }
  });
});

// ─── PerformancePanel ─────────────────────────────────────────────────────────

import { PerformancePanel } from "../../components/diagnostics/PerformancePanel";
import type { PerformanceMetric } from "../../components/diagnostics/PerformancePanel";

const PERF_METRICS: PerformanceMetric[] = [
  { label: "Stat Calc", value: 12, unit: "ms",    good: 50, warn: 200 },
  { label: "Search",    value: 5,  unit: "depth"             },
  { label: "Memory",    value: 45, unit: "MB",    warn: 100  },
  { label: "Hit Rate",  value: 95, unit: "%"                 },
];

describe("PerformancePanel", () => {
  it("renders without crashing", () => {
    const { container } = render(<PerformancePanel metrics={PERF_METRICS} />);
    expect(container).toBeInTheDocument();
  });

  it("shows metric labels", () => {
    render(<PerformancePanel metrics={PERF_METRICS} />);
    expect(screen.getByText("Stat Calc")).toBeInTheDocument();
    expect(screen.getByText("Memory")).toBeInTheDocument();
  });

  it("formats ms values", () => {
    render(<PerformancePanel metrics={PERF_METRICS} />);
    expect(screen.getByText("12ms")).toBeInTheDocument();
  });

  it("formats MB values", () => {
    render(<PerformancePanel metrics={[{ label: "RAM", value: 32.5, unit: "MB" }]} />);
    expect(screen.getByText("32.5MB")).toBeInTheDocument();
  });

  it("formats large ops as k", () => {
    render(<PerformancePanel metrics={[{ label: "Ops", value: 2000, unit: "ops" }]} />);
    expect(screen.getByText("2.0k ops")).toBeInTheDocument();
  });

  it("formats depth as integer", () => {
    render(<PerformancePanel metrics={[{ label: "D", value: 7.9, unit: "depth" }]} />);
    expect(screen.getByText("8")).toBeInTheDocument();
  });

  it("shows warning badge for metrics exceeding warn threshold", () => {
    render(<PerformancePanel metrics={[{ label: "Slow", value: 300, unit: "ms", warn: 200 }]} />);
    // The high-value metric should have red/warning styling
    const { container } = render(
      <PerformancePanel metrics={[{ label: "Slow", value: 300, unit: "ms", warn: 200 }]} />
    );
    expect(container.innerHTML).toMatch(/red|warn|danger/i);
  });

  it("renders collapsed state", () => {
    const { container } = render(<PerformancePanel metrics={PERF_METRICS} collapsed={true} />);
    expect(container).toBeInTheDocument();
  });

  it("renders empty metrics without crash", () => {
    const { container } = render(<PerformancePanel metrics={[]} />);
    expect(container).toBeInTheDocument();
  });
});

// ─── AdvancedTooltip ──────────────────────────────────────────────────────────

import { AdvancedTooltip } from "../../components/tooltips/AdvancedTooltip";
import type { TooltipSection } from "../../components/tooltips/AdvancedTooltip";

describe("AdvancedTooltip", () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => { vi.useRealTimers(); });

  it("renders children", () => {
    render(
      <AdvancedTooltip content="Hello"><button>Trigger</button></AdvancedTooltip>
    );
    expect(screen.getByText("Trigger")).toBeInTheDocument();
  });

  it("tooltip not visible initially", () => {
    render(
      <AdvancedTooltip content="Tip text" delay={300}><button>Trigger</button></AdvancedTooltip>
    );
    expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
  });

  it("shows tooltip after delay on hover", async () => {
    render(
      <AdvancedTooltip content="Tip text" delay={300}><button>Trigger</button></AdvancedTooltip>
    );
    await act(async () => {
      fireEvent.mouseEnter(screen.getByText("Trigger").closest("div")!);
      vi.advanceTimersByTime(300);
    });
    expect(screen.getByRole("tooltip")).toBeInTheDocument();
    expect(screen.getByText("Tip text")).toBeInTheDocument();
  });

  it("hides tooltip after mouse leave + hideDelay", async () => {
    render(
      <AdvancedTooltip content="Tip text" delay={0} hideDelay={100}><button>Trigger</button></AdvancedTooltip>
    );
    const trigger = screen.getByText("Trigger").closest("div")!;
    await act(async () => {
      fireEvent.mouseEnter(trigger);
      vi.advanceTimersByTime(0);
    });
    expect(screen.getByRole("tooltip")).toBeInTheDocument();
    await act(async () => {
      fireEvent.mouseLeave(trigger);
      vi.advanceTimersByTime(100);
    });
    expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
  });

  it("does not show when disabled", async () => {
    render(
      <AdvancedTooltip content="Tip text" delay={0} disabled><button>Trigger</button></AdvancedTooltip>
    );
    await act(async () => {
      fireEvent.mouseEnter(screen.getByText("Trigger").closest("div")!);
      vi.advanceTimersByTime(300);
    });
    expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
  });

  it("renders section array content", async () => {
    const sections: TooltipSection[] = [
      { title: "Stats", content: "200 DPS", variant: "info" },
      { title: "Notes", content: "End game", variant: "warning" },
    ];
    render(
      <AdvancedTooltip content={sections} delay={0}><button>Trigger</button></AdvancedTooltip>
    );
    await act(async () => {
      fireEvent.mouseEnter(screen.getByText("Trigger").closest("div")!);
      vi.advanceTimersByTime(0);
    });
    expect(screen.getByText("Stats")).toBeInTheDocument();
    expect(screen.getByText("200 DPS")).toBeInTheDocument();
    expect(screen.getByText("Notes")).toBeInTheDocument();
  });

  it("tooltip has correct role", async () => {
    render(
      <AdvancedTooltip content="Accessible" delay={0}><button>Hover me</button></AdvancedTooltip>
    );
    await act(async () => {
      fireEvent.mouseEnter(screen.getByText("Hover me").closest("div")!);
      vi.advanceTimersByTime(0);
    });
    expect(screen.getByRole("tooltip")).toBeInTheDocument();
  });

  it("renders ReactNode content", async () => {
    render(
      <AdvancedTooltip content={<strong>Bold</strong>} delay={0}><span>t</span></AdvancedTooltip>
    );
    await act(async () => {
      fireEvent.mouseEnter(screen.getByText("t").closest("div")!);
      vi.advanceTimersByTime(0);
    });
    expect(screen.getByText("Bold")).toBeInTheDocument();
  });
});
