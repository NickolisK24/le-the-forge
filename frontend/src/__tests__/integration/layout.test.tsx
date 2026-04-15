/**
 * Integration tests: AppLayout
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
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
    NavLink: ({ children, to, title, style, ...rest }: any) => (
      <a href={to} title={title} style={typeof style === 'function' ? undefined : style} {...rest}>
        {children}
      </a>
    ),
    Link: ({ children, to, ...rest }: any) => <a href={to} {...rest}>{children}</a>,
    Outlet: () => <div data-testid="outlet">Page Content</div>,
  };
});

vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQuery: () => ({ data: null, isLoading: false, error: null }),
  };
});

vi.mock('@/store', () => ({
  useAuthStore: () => ({ user: null, login: vi.fn(), logout: vi.fn() }),
}));

vi.mock('@/lib/api', () => ({
  versionApi: { get: vi.fn().mockResolvedValue({ data: null }) },
}));

import AppLayout from '@/components/layout/AppLayout';
import userEvent from '@testing-library/user-event';

// ---------------------------------------------------------------------------
// AppLayout integration tests
// ---------------------------------------------------------------------------

describe('AppLayout', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders without crashing', () => {
    render(<AppLayout />);
    expect(document.body).toBeInTheDocument();
  });

  it('renders sidebar', () => {
    const { container } = render(<AppLayout />);
    expect(container.querySelector('aside')).toBeInTheDocument();
  });

  it('renders topbar header', () => {
    render(<AppLayout />);
    expect(screen.getByRole('banner')).toBeInTheDocument();
  });

  it('renders outlet (page content)', () => {
    render(<AppLayout />);
    expect(screen.getByTestId('outlet')).toBeInTheDocument();
  });

  it('renders footer', () => {
    render(<AppLayout />);
    expect(screen.getByText('The Forge — Last Epoch Build Analyzer')).toBeInTheDocument();
  });

  it('THE FORGE logo appears in topbar', () => {
    render(<AppLayout />);
    const forgeTexts = screen.getAllByText('THE FORGE');
    expect(forgeTexts.length).toBeGreaterThan(0);
  });

  it('sidebar starts collapsed by default', () => {
    const { container } = render(<AppLayout />);
    const aside = container.querySelector('aside') as HTMLElement;
    // Desktop collapsed width is applied via Tailwind `md:w-[56px]`.
    expect(aside.className).toContain('md:w-[56px]');
  });

  it('sidebar starts expanded when localStorage has true', () => {
    localStorage.setItem('forge_sidebar_open', 'true');
    const { container } = render(<AppLayout />);
    const aside = container.querySelector('aside') as HTMLElement;
    expect(aside.className).toContain('md:w-[200px]');
  });

  it('sidebar toggle button exists in topbar', () => {
    render(<AppLayout />);
    expect(screen.getByTitle('Toggle sidebar')).toBeInTheDocument();
  });

  it('sidebar toggle changes layout when clicked via sidebar expand button', async () => {
    const { container } = render(<AppLayout />);
    // The sidebar's own expand button
    const expandBtn = screen.getByTitle('Expand sidebar');
    await act(async () => { fireEvent.click(expandBtn); });
    const aside = container.querySelector('aside') as HTMLElement;
    expect(aside.className).toContain('md:w-[200px]');
  });

  it('sidebar can be collapsed via expand/collapse toggle', async () => {
    const { container } = render(<AppLayout />);
    // Expand via sidebar's own expand button
    await act(async () => { fireEvent.click(screen.getByTitle('Expand sidebar')); });
    const aside = container.querySelector('aside') as HTMLElement;
    expect(aside.className).toContain('md:w-[200px]');
    // Collapse via sidebar's own collapse button
    await act(async () => { fireEvent.click(screen.getByTitle('Collapse sidebar')); });
    expect(aside.className).toContain('md:w-[56px]');
  });

  it('GlobalSearch is not visible initially', () => {
    render(<AppLayout />);
    expect(screen.queryByPlaceholderText('Search items, skills, affixes, builds…')).not.toBeInTheDocument();
  });

  it('GlobalSearch opens when search button in topbar is clicked', async () => {
    render(<AppLayout />);
    const searchBtn = screen.getByText('Search…').closest('button') as HTMLElement;
    await act(async () => { fireEvent.click(searchBtn); });
    expect(screen.getByPlaceholderText('Search items, skills, affixes, builds…')).toBeInTheDocument();
  });

  it('GlobalSearch closes on Escape key', async () => {
    render(<AppLayout />);
    const searchBtn = screen.getByText('Search…').closest('button') as HTMLElement;
    await act(async () => { fireEvent.click(searchBtn); });
    expect(screen.getByPlaceholderText('Search items, skills, affixes, builds…')).toBeInTheDocument();
    await act(async () => { fireEvent.keyDown(window, { key: 'Escape' }); });
    expect(screen.queryByPlaceholderText('Search items, skills, affixes, builds…')).not.toBeInTheDocument();
  });

  it('GlobalSearch opens with Ctrl+K', async () => {
    render(<AppLayout />);
    await act(async () => {
      fireEvent.keyDown(window, { key: 'k', ctrlKey: true });
    });
    expect(screen.getByPlaceholderText('Search items, skills, affixes, builds…')).toBeInTheDocument();
  });

  it('GlobalSearch toggles closed with Ctrl+K when already open', async () => {
    render(<AppLayout />);
    await act(async () => {
      fireEvent.keyDown(window, { key: 'k', ctrlKey: true });
    });
    expect(screen.getByPlaceholderText('Search items, skills, affixes, builds…')).toBeInTheDocument();
    // Pressing Ctrl+K again should toggle it closed (AppLayout impl closes on second Ctrl+K)
    await act(async () => {
      fireEvent.keyDown(window, { key: 'k', ctrlKey: true });
    });
    expect(screen.queryByPlaceholderText('Search items, skills, affixes, builds…')).not.toBeInTheDocument();
  });

  it('Sign In button appears in topbar when no user', () => {
    render(<AppLayout />);
    expect(screen.getByText('Sign In')).toBeInTheDocument();
  });

  it('main content area renders', () => {
    const { container } = render(<AppLayout />);
    expect(container.querySelector('main')).toBeInTheDocument();
  });

  it('renders nav items in sidebar', () => {
    render(<AppLayout />);
    // With sidebar collapsed, nav items are still in the DOM (just no label text)
    const aside = document.querySelector('aside');
    expect(aside?.querySelector('nav')).toBeInTheDocument();
  });

  it('sidebar nav has correct number of links', () => {
    render(<AppLayout />);
    const aside = document.querySelector('aside') as HTMLElement;
    const links = aside.querySelectorAll('a');
    expect(links.length).toBeGreaterThan(5);
  });

  it('renders THE FORGE text in sidebar when expanded', async () => {
    render(<AppLayout />);
    await act(async () => { fireEvent.click(screen.getByTitle('Expand sidebar')); });
    const theForgeTexts = screen.getAllByText('THE FORGE');
    expect(theForgeTexts.length).toBeGreaterThan(0);
  });

  it('shows nav labels in sidebar when expanded', async () => {
    render(<AppLayout />);
    await act(async () => { fireEvent.click(screen.getByTitle('Expand sidebar')); });
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Build Planner')).toBeInTheDocument();
  });

  it('clicking search opens global search with results', async () => {
    render(<AppLayout />);
    const searchBtn = screen.getByText('Search…').closest('button') as HTMLElement;
    await act(async () => { fireEvent.click(searchBtn); });
    expect(screen.getByText('Items')).toBeInTheDocument();
  });

  it('can search after opening GlobalSearch', async () => {
    const user = userEvent.setup();
    render(<AppLayout />);
    const searchBtn = screen.getByText('Search…').closest('button') as HTMLElement;
    await act(async () => { fireEvent.click(searchBtn); });
    const input = screen.getByPlaceholderText('Search items, skills, affixes, builds…');
    await user.type(input, 'Rive');
    expect(screen.getByText('Rive')).toBeInTheDocument();
  });

  it('renders without footer version info when version data is null', () => {
    render(<AppLayout />);
    // Footer still renders even with no version
    const footer = document.querySelector('footer');
    expect(footer).toBeInTheDocument();
  });
});
