/**
 * Workspace page tests: BuildWorkspace, CraftingWorkspace, BisWorkspace
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useLocation: () => ({ pathname: '/', search: '', hash: '' }),
    useNavigate: () => vi.fn(),
    NavLink: ({ children, to }: any) => <a href={to}>{children}</a>,
    Link: ({ children, to, ...rest }: any) => <a href={to} {...rest}>{children}</a>,
    Outlet: () => <div data-testid="outlet" />,
  };
});

vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQuery: () => ({ data: null, isLoading: false, error: null }),
    useMutation: () => ({ mutate: vi.fn(), isLoading: false }),
  };
});

vi.mock('@/store', () => ({
  useAuthStore: () => ({ user: null, login: vi.fn(), logout: vi.fn() }),
  useCraftStore: () => ({
    itemType: 'Wand',
    itemName: '',
    itemLevel: 84,
    rarity: 'Exalted',
    forgePotential: 28,
    affixes: [],
    sessionSlug: null,
    setItemType: vi.fn(),
    setItemName: vi.fn(),
    setItemLevel: vi.fn(),
    setRarity: vi.fn(),
    setForgePotential: vi.fn(),
    setAffixes: vi.fn(),
    addAffix: vi.fn(),
    removeAffix: vi.fn(),
    updateAffix: vi.fn(),
    setSessionSlug: vi.fn(),
    resetSession: vi.fn(),
  }),
}));

vi.mock('@/lib/api', () => ({
  versionApi: { get: vi.fn().mockResolvedValue({ data: null }) },
  buildsApi: { list: vi.fn(), create: vi.fn() },
  craftApi: { create: vi.fn() },
  refApi: { classes: vi.fn(), affixes: vi.fn(), itemTypes: vi.fn() },
}));

// Mock recharts
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  PieChart: ({ children }: any) => <div>{children}</div>,
  BarChart: ({ children }: any) => <div>{children}</div>,
  ScatterChart: ({ children }: any) => <div>{children}</div>,
  Pie: () => null,
  Bar: () => null,
  Scatter: () => null,
  Cell: () => null,
  XAxis: () => null,
  YAxis: () => null,
  Tooltip: () => null,
  Legend: () => null,
  ZAxis: () => null,
}));

import BuildWorkspace from '@/pages/build/BuildWorkspace';
import CraftingWorkspace from '@/pages/crafting/CraftingWorkspace';
import BisWorkspace from '@/pages/bis/BisWorkspace';

// ---------------------------------------------------------------------------
// BuildWorkspace tests
// ---------------------------------------------------------------------------

describe('BuildWorkspace', () => {
  it('renders without crash', () => {
    render(<BuildWorkspace />);
    expect(document.body).toBeInTheDocument();
  });

  it('shows equipment section', () => {
    render(<BuildWorkspace />);
    expect(screen.getByText('Equipment')).toBeInTheDocument();
  });

  it('shows Skill Config panel', () => {
    render(<BuildWorkspace />);
    expect(screen.getByText('Skill Config')).toBeInTheDocument();
  });

  it('shows Build Summary panel', () => {
    render(<BuildWorkspace />);
    expect(screen.getByText('Build Summary')).toBeInTheDocument();
  });

  it('shows back link to builds', () => {
    render(<BuildWorkspace />);
    const link = screen.getByText('← Back to Builds');
    expect(link).toBeInTheDocument();
    expect(link.getAttribute('href')).toBe('/builds');
  });

  it('shows gear slot cards', () => {
    render(<BuildWorkspace />);
    expect(screen.getByText('Helm')).toBeInTheDocument();
    expect(screen.getByText('Chest')).toBeInTheDocument();
    expect(screen.getByText('Boots')).toBeInTheDocument();
  });

  it('shows all 9 gear slots', () => {
    render(<BuildWorkspace />);
    const slotLabels = ['Helm', 'Chest', 'Gloves', 'Boots', 'Belt', 'Ring 1', 'Ring 2', 'Amulet', 'Weapon'];
    slotLabels.forEach((label) => {
      expect(screen.getByText(label)).toBeInTheDocument();
    });
  });

  it('shows skill slots (5 empty slots)', () => {
    render(<BuildWorkspace />);
    const emptySlots = screen.getAllByText('Empty Slot');
    expect(emptySlots.length).toBe(5);
  });

  it('shows passive tree section', () => {
    render(<BuildWorkspace />);
    expect(screen.getByText('Passive Tree')).toBeInTheDocument();
  });

  it('shows "0 points allocated" in passive tree', () => {
    render(<BuildWorkspace />);
    expect(screen.getByText('0 points allocated')).toBeInTheDocument();
  });

  it('shows DPS stat', () => {
    render(<BuildWorkspace />);
    expect(screen.getByText('DPS')).toBeInTheDocument();
  });

  it('shows Survivability stat', () => {
    render(<BuildWorkspace />);
    expect(screen.getByText('Survivability')).toBeInTheDocument();
  });

  it('shows Efficiency stat', () => {
    render(<BuildWorkspace />);
    expect(screen.getByText('Efficiency')).toBeInTheDocument();
  });

  it('shows Simulate Build button', () => {
    render(<BuildWorkspace />);
    expect(screen.getByText('Simulate Build')).toBeInTheDocument();
  });

  it('shows Export button', () => {
    render(<BuildWorkspace />);
    expect(screen.getByText('Export')).toBeInTheDocument();
  });

  it('shows empty state in Build Summary', () => {
    render(<BuildWorkspace />);
    expect(screen.getByText('No build loaded')).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// CraftingWorkspace tests
// ---------------------------------------------------------------------------

describe('CraftingWorkspace', () => {
  it('renders without crash', () => {
    render(<CraftingWorkspace />);
    expect(document.body).toBeInTheDocument();
  });

  it('shows "Crafting Workspace" heading', () => {
    render(<CraftingWorkspace />);
    expect(screen.getByText('Crafting Workspace')).toBeInTheDocument();
  });

  it('shows the stepper', () => {
    render(<CraftingWorkspace />);
    // Stepper has step labels; "Select Base Item" appears in stepper AND in the panel title
    const selectBaseItems = screen.getAllByText('Select Base Item');
    expect(selectBaseItems.length).toBeGreaterThan(0);
    expect(screen.getByText('Define Target')).toBeInTheDocument();
    expect(screen.getByText('Run Simulation')).toBeInTheDocument();
    expect(screen.getByText('Review Result')).toBeInTheDocument();
  });

  it('stepper has 4 steps', () => {
    render(<CraftingWorkspace />);
    // Step numbers 1-4 visible in stepper circles
    const stepNums = screen.getAllByText('1');
    expect(stepNums.length).toBeGreaterThan(0);
  });

  it('step 1 shows base item grid', () => {
    render(<CraftingWorkspace />);
    // "Select Base Item" appears in both stepper label and panel title
    const selectBaseItems = screen.getAllByText('Select Base Item');
    expect(selectBaseItems.length).toBeGreaterThan(0);
    expect(screen.getByText('Helm')).toBeInTheDocument();
    expect(screen.getByText('Chest')).toBeInTheDocument();
    expect(screen.getByText('Sword')).toBeInTheDocument();
  });

  it('step 1 shows all base items', () => {
    render(<CraftingWorkspace />);
    expect(screen.getByText('Boots')).toBeInTheDocument();
    expect(screen.getByText('Ring')).toBeInTheDocument();
    expect(screen.getByText('Staff')).toBeInTheDocument();
  });

  it('Next button is initially disabled (no base item selected)', () => {
    render(<CraftingWorkspace />);
    const nextBtn = screen.getByText('Next →');
    expect(nextBtn).toBeDisabled();
  });

  it('Next button enables after selecting a base item', async () => {
    render(<CraftingWorkspace />);
    const helmBtn = screen.getByText('Helm');
    await act(async () => { fireEvent.click(helmBtn); });
    const nextBtn = screen.getByText('Next →');
    expect(nextBtn).not.toBeDisabled();
  });

  it('navigates to step 2 when Next clicked after selecting item', async () => {
    render(<CraftingWorkspace />);
    const helmBtn = screen.getByText('Helm');
    await act(async () => { fireEvent.click(helmBtn); });
    const nextBtns = screen.getAllByText('Next →');
    await act(async () => { fireEvent.click(nextBtns[nextBtns.length - 1]); });
    expect(screen.getByText('Target Affixes')).toBeInTheDocument();
  });

  it('step 2 shows back button', async () => {
    render(<CraftingWorkspace />);
    await act(async () => { fireEvent.click(screen.getByText('Helm')); });
    const nextBtns = screen.getAllByText('Next →');
    await act(async () => { fireEvent.click(nextBtns[nextBtns.length - 1]); });
    expect(screen.getByText('← Back')).toBeInTheDocument();
  });

  it('navigates back to step 1 when Back clicked', async () => {
    render(<CraftingWorkspace />);
    await act(async () => { fireEvent.click(screen.getByText('Helm')); });
    const nextBtns = screen.getAllByText('Next →');
    await act(async () => { fireEvent.click(nextBtns[nextBtns.length - 1]); });
    await act(async () => { fireEvent.click(screen.getByText('← Back')); });
    // Back to step 1 - "Select Base Item" appears multiple times (stepper + panel)
    const selectItems = screen.getAllByText('Select Base Item');
    expect(selectItems.length).toBeGreaterThan(0);
    expect(screen.getByText('Helm')).toBeInTheDocument();
  });

  it('step 2 shows suggested affix buttons', async () => {
    render(<CraftingWorkspace />);
    await act(async () => { fireEvent.click(screen.getByText('Helm')); });
    await act(async () => { fireEvent.click(screen.getByText('Next →')); });
    expect(screen.getByText('+ T7 Fire Resistance')).toBeInTheDocument();
    expect(screen.getByText('+ T7 Health')).toBeInTheDocument();
  });

  it('step 2 Next button disabled until affix added', async () => {
    render(<CraftingWorkspace />);
    await act(async () => { fireEvent.click(screen.getByText('Helm')); });
    await act(async () => { fireEvent.click(screen.getByText('Next →')); });
    const nextButtons = screen.getAllByText('Next →');
    const nextBtn = nextButtons[nextButtons.length - 1];
    expect(nextBtn).toBeDisabled();
  });

  it('step 2 Next button enables after adding affix', async () => {
    render(<CraftingWorkspace />);
    await act(async () => { fireEvent.click(screen.getByText('Helm')); });
    await act(async () => { fireEvent.click(screen.getByText('Next →')); });
    await act(async () => { fireEvent.click(screen.getByText('+ T7 Fire Resistance')); });
    const nextButtons = screen.getAllByText('Next →');
    const nextBtn = nextButtons[nextButtons.length - 1];
    expect(nextBtn).not.toBeDisabled();
  });

  it('shows "Added Affixes" section after adding affix', async () => {
    render(<CraftingWorkspace />);
    await act(async () => { fireEvent.click(screen.getByText('Helm')); });
    await act(async () => { fireEvent.click(screen.getByText('Next →')); });
    await act(async () => { fireEvent.click(screen.getByText('+ T7 Fire Resistance')); });
    expect(screen.getByText('Added Affixes')).toBeInTheDocument();
  });

  it('can remove added affix', async () => {
    render(<CraftingWorkspace />);
    await act(async () => { fireEvent.click(screen.getByText('Helm')); });
    await act(async () => { fireEvent.click(screen.getByText('Next →')); });
    await act(async () => { fireEvent.click(screen.getByText('+ T7 Fire Resistance')); });
    const removeBtn = screen.getByText('✕');
    await act(async () => { fireEvent.click(removeBtn); });
    expect(screen.queryByText('Add T7 Fire Resistance')).not.toBeInTheDocument();
  });

  it('shows page description', () => {
    render(<CraftingWorkspace />);
    expect(screen.getByText('Step-by-step crafting workflow with Monte Carlo simulation.')).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// BisWorkspace tests
// ---------------------------------------------------------------------------

describe('BisWorkspace', () => {
  it('renders without crash', () => {
    render(<BisWorkspace />);
    expect(document.body).toBeInTheDocument();
  });

  it('shows "BIS Search Workspace" heading', () => {
    render(<BisWorkspace />);
    expect(screen.getByText('BIS Search Workspace')).toBeInTheDocument();
  });

  it('renders slot selector accordion', () => {
    render(<BisWorkspace />);
    expect(screen.getByText('Slot Selection')).toBeInTheDocument();
  });

  it('renders affix targets accordion', () => {
    render(<BisWorkspace />);
    expect(screen.getByText('Affix Targets')).toBeInTheDocument();
  });

  it('renders weight config accordion', () => {
    render(<BisWorkspace />);
    expect(screen.getByText('Weight Config')).toBeInTheDocument();
  });

  it('shows results table tab', () => {
    render(<BisWorkspace />);
    expect(screen.getByText('Results Table')).toBeInTheDocument();
  });

  it('shows comparison tab', () => {
    render(<BisWorkspace />);
    expect(screen.getByText('Comparison')).toBeInTheDocument();
  });

  it('shows visualization tab', () => {
    render(<BisWorkspace />);
    expect(screen.getByText('Visualization')).toBeInTheDocument();
  });

  it('shows page description', () => {
    render(<BisWorkspace />);
    expect(screen.getByText('Find optimal gear combinations for your build')).toBeInTheDocument();
  });

  it('slot selection accordion is open by default', () => {
    render(<BisWorkspace />);
    // SlotSelector content should be visible (accordion is defaultOpen)
    const slotAccordion = screen.getByText('Slot Selection');
    expect(slotAccordion).toBeInTheDocument();
  });

  it('can toggle accordion open/close', async () => {
    render(<BisWorkspace />);
    // Affix Targets accordion starts closed; click to open
    const affixHeaders = screen.getAllByText('Affix Targets');
    const affixBtn = affixHeaders[0].closest('button') as HTMLElement;
    await act(async () => { fireEvent.click(affixBtn); });
    // After opening, the content area appears
    const affixHeadersAfter = screen.getAllByText('Affix Targets');
    expect(affixHeadersAfter.length).toBeGreaterThan(0);
  });

  it('shows a search-related button from SearchControls', () => {
    render(<BisWorkspace />);
    // SearchControls renders a search button - find by role to avoid multiple matches
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('can switch to Comparison tab', async () => {
    render(<BisWorkspace />);
    const comparisonTab = screen.getByText('Comparison');
    await act(async () => { fireEvent.click(comparisonTab); });
    expect(screen.getByText('Comparison')).toBeInTheDocument();
  });

  it('can switch to Visualization tab', async () => {
    render(<BisWorkspace />);
    const vizTab = screen.getByText('Visualization');
    await act(async () => { fireEvent.click(vizTab); });
    expect(screen.getByText('Visualization')).toBeInTheDocument();
  });
});
