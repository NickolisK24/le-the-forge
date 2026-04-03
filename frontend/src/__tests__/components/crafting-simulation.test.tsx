/**
 * Crafting & Simulation tests:
 *   CraftTimelineViewer, CraftProbabilityCharts, SimulationTimeline
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';

// Mock recharts to avoid ResizeObserver issues in jsdom
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Pie: () => <div data-testid="pie" />,
  Bar: () => <div data-testid="bar" />,
  Cell: () => null,
  XAxis: () => null,
  YAxis: () => null,
  Tooltip: () => null,
}));

import { CraftTimelineViewer } from '@/components/crafting/CraftTimelineViewer';
import type { CraftStep } from '@/components/crafting/CraftTimelineViewer';
import { CraftProbabilityCharts } from '@/components/crafting/CraftProbabilityCharts';
import { SimulationTimeline } from '@/components/simulation/SimulationTimeline';
import type { CombatEvent } from '@/components/simulation/SimulationTimeline';

// ---------------------------------------------------------------------------
// Test data
// ---------------------------------------------------------------------------

const SAMPLE_STEPS: CraftStep[] = [
  {
    stepNumber: 1,
    action: 'Apply T7 Fire Resistance',
    successChance: 0.72,
    outcome: 'success',
    fpCost: 24,
    note: 'First attempt',
  },
  {
    stepNumber: 2,
    action: 'Apply T7 Health',
    successChance: 0.45,
    outcome: 'partial',
    fpCost: 18,
  },
  {
    stepNumber: 3,
    action: 'Seal affix',
    successChance: 0.90,
    outcome: 'failure',
    fpCost: 8,
  },
];

const SAMPLE_EVENTS: CombatEvent[] = [
  { time: 0.5, type: 'ability', label: 'Rive', value: 1500 },
  { time: 1.2, type: 'damage', label: 'Hit', value: 850, targetId: 'boss' },
  { time: 3.0, type: 'buff', label: 'Haste Aura' },
  { time: 5.5, type: 'death', label: 'Enemy Death', targetId: 'skeleton' },
  { time: 8.0, type: 'debuff', label: 'Slow' },
];

// ---------------------------------------------------------------------------
// CraftTimelineViewer tests
// ---------------------------------------------------------------------------

describe('CraftTimelineViewer', () => {
  it('renders without crashing with steps', () => {
    render(<CraftTimelineViewer steps={SAMPLE_STEPS} />);
    expect(document.body).toBeInTheDocument();
  });

  it('shows empty state when no steps', () => {
    render(<CraftTimelineViewer steps={[]} />);
    expect(screen.getByText('No steps yet')).toBeInTheDocument();
  });

  it('shows empty state description', () => {
    render(<CraftTimelineViewer steps={[]} />);
    expect(screen.getByText('Run a simulation to see the crafting timeline.')).toBeInTheDocument();
  });

  it('renders step actions', () => {
    render(<CraftTimelineViewer steps={SAMPLE_STEPS} />);
    expect(screen.getByText('Apply T7 Fire Resistance')).toBeInTheDocument();
    expect(screen.getByText('Apply T7 Health')).toBeInTheDocument();
    expect(screen.getByText('Seal affix')).toBeInTheDocument();
  });

  it('shows step numbers', () => {
    render(<CraftTimelineViewer steps={SAMPLE_STEPS} />);
    expect(screen.getByText('Step 1')).toBeInTheDocument();
    expect(screen.getByText('Step 2')).toBeInTheDocument();
    expect(screen.getByText('Step 3')).toBeInTheDocument();
  });

  it('shows FP costs', () => {
    render(<CraftTimelineViewer steps={SAMPLE_STEPS} />);
    expect(screen.getByText('24 FP')).toBeInTheDocument();
    expect(screen.getByText('18 FP')).toBeInTheDocument();
    expect(screen.getByText('8 FP')).toBeInTheDocument();
  });

  it('shows outcome badges', () => {
    render(<CraftTimelineViewer steps={SAMPLE_STEPS} />);
    expect(screen.getByText('Success')).toBeInTheDocument();
    expect(screen.getByText('Partial')).toBeInTheDocument();
    expect(screen.getByText('Failure')).toBeInTheDocument();
  });

  it('shows notes when provided', () => {
    render(<CraftTimelineViewer steps={SAMPLE_STEPS} />);
    expect(screen.getByText('First attempt')).toBeInTheDocument();
  });

  it('shows success chance percentages', () => {
    render(<CraftTimelineViewer steps={SAMPLE_STEPS} />);
    expect(screen.getByText('72%')).toBeInTheDocument();
  });

  it('highlights current step', () => {
    render(<CraftTimelineViewer steps={SAMPLE_STEPS} currentStep={2} />);
    expect(screen.getByText('● Current')).toBeInTheDocument();
  });

  it('renders without currentStep prop', () => {
    expect(() => render(<CraftTimelineViewer steps={SAMPLE_STEPS} />)).not.toThrow();
  });

  it('renders a single step', () => {
    render(<CraftTimelineViewer steps={[SAMPLE_STEPS[0]]} />);
    expect(screen.getByText('Apply T7 Fire Resistance')).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// CraftProbabilityCharts tests
// ---------------------------------------------------------------------------

describe('CraftProbabilityCharts', () => {
  it('renders without crashing', () => {
    render(<CraftProbabilityCharts />);
    expect(document.body).toBeInTheDocument();
  });

  it('renders "Success vs Failure" section header', () => {
    render(<CraftProbabilityCharts />);
    expect(screen.getByText('Success vs Failure')).toBeInTheDocument();
  });

  it('renders "FP Cost Distribution" section header', () => {
    render(<CraftProbabilityCharts />);
    expect(screen.getByText('FP Cost Distribution')).toBeInTheDocument();
  });

  it('renders chart containers', () => {
    render(<CraftProbabilityCharts />);
    expect(screen.getAllByTestId('responsive-container').length).toBe(2);
  });

  it('renders pie chart', () => {
    render(<CraftProbabilityCharts />);
    expect(screen.getByTestId('pie-chart')).toBeInTheDocument();
  });

  it('renders bar chart', () => {
    render(<CraftProbabilityCharts />);
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });

  it('shows success percentage in legend', () => {
    render(<CraftProbabilityCharts successRate={0.72} />);
    expect(screen.getByText(/Success 72%/)).toBeInTheDocument();
  });

  it('shows failure percentage in legend', () => {
    render(<CraftProbabilityCharts successRate={0.72} />);
    expect(screen.getByText(/Failure 28%/)).toBeInTheDocument();
  });

  it('defaults to 0% success when no rate provided', () => {
    render(<CraftProbabilityCharts />);
    expect(screen.getByText(/Success 0%/)).toBeInTheDocument();
  });

  it('renders with distribution data', () => {
    const data = [
      { attempt: 1, success: true, fpUsed: 30 },
      { attempt: 2, success: false, fpUsed: 50 },
      { attempt: 3, success: true, fpUsed: 15 },
    ];
    expect(() => render(<CraftProbabilityCharts distributionData={data} />)).not.toThrow();
  });
});

// ---------------------------------------------------------------------------
// SimulationTimeline tests
// ---------------------------------------------------------------------------

describe('SimulationTimeline', () => {
  it('renders without crashing with events', () => {
    render(<SimulationTimeline events={SAMPLE_EVENTS} duration={10} />);
    expect(document.body).toBeInTheDocument();
  });

  it('shows empty state when no events', () => {
    render(<SimulationTimeline events={[]} />);
    expect(screen.getByText('No events')).toBeInTheDocument();
  });

  it('shows empty state description', () => {
    render(<SimulationTimeline events={[]} />);
    expect(screen.getByText('Run a simulation to populate the combat timeline.')).toBeInTheDocument();
  });

  it('renders by default with no events prop', () => {
    render(<SimulationTimeline />);
    expect(screen.getByText('No events')).toBeInTheDocument();
  });

  it('shows event labels', () => {
    render(<SimulationTimeline events={SAMPLE_EVENTS} duration={10} />);
    expect(screen.getByText('Rive')).toBeInTheDocument();
    expect(screen.getByText('Hit')).toBeInTheDocument();
  });

  it('shows event type badges', () => {
    render(<SimulationTimeline events={SAMPLE_EVENTS} duration={10} />);
    expect(screen.getAllByText('ability').length).toBeGreaterThan(0);
    expect(screen.getAllByText('damage').length).toBeGreaterThan(0);
  });

  it('shows event count in header', () => {
    render(<SimulationTimeline events={SAMPLE_EVENTS} duration={10} />);
    // "5 total" appears in header
    expect(screen.getAllByText('5 total').length).toBeGreaterThan(0);
  });

  it('shows event values', () => {
    render(<SimulationTimeline events={SAMPLE_EVENTS} duration={10} />);
    expect(screen.getByText('1,500')).toBeInTheDocument();
  });

  it('shows target IDs', () => {
    render(<SimulationTimeline events={SAMPLE_EVENTS} duration={10} />);
    expect(screen.getByText('→ boss')).toBeInTheDocument();
  });

  it('calls onEventSelect when event row clicked', () => {
    const onEventSelect = vi.fn();
    render(<SimulationTimeline events={SAMPLE_EVENTS} duration={10} onEventSelect={onEventSelect} />);
    const eventRows = screen.getAllByRole('button');
    fireEvent.click(eventRows[0]);
    expect(onEventSelect).toHaveBeenCalled();
  });

  it('renders the timeline bar', () => {
    const { container } = render(<SimulationTimeline events={SAMPLE_EVENTS} duration={10} />);
    expect(container.querySelector('.relative.h-8')).toBeInTheDocument();
  });

  it('shows "Events" section label', () => {
    render(<SimulationTimeline events={SAMPLE_EVENTS} duration={10} />);
    expect(screen.getByText('Events')).toBeInTheDocument();
  });

  it('shows duration in header', () => {
    render(<SimulationTimeline events={SAMPLE_EVENTS} duration={10} />);
    expect(screen.getByText(/10\.0s total/)).toBeInTheDocument();
  });

  it('sorts events by time', () => {
    const unsorted: CombatEvent[] = [
      { time: 5, type: 'damage', label: 'Late Event' },
      { time: 1, type: 'ability', label: 'Early Event' },
    ];
    render(<SimulationTimeline events={unsorted} duration={10} />);
    const labels = screen.getAllByRole('button').map((b) => b.textContent);
    // Early event should come first in the list
    const earlyIdx = labels.findIndex((t) => t?.includes('Early Event'));
    const lateIdx = labels.findIndex((t) => t?.includes('Late Event'));
    expect(earlyIdx).toBeLessThan(lateIdx);
  });
});
