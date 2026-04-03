/**
 * Data management tests: DataManagerDashboard + ErrorReportingPanel
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act, waitFor } from '@testing-library/react';
import React from 'react';

vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQuery: () => ({ data: null, isLoading: false, error: null }),
  };
});

vi.mock('@/lib/api', () => ({
  versionApi: { get: vi.fn().mockResolvedValue({ data: null }) },
}));

import { DataManagerDashboard } from '@/components/data/DataManagerDashboard';
import { ErrorReportingPanel } from '@/components/data/ErrorReportingPanel';
import type { ValidationError } from '@/components/data/ErrorReportingPanel';

// ---------------------------------------------------------------------------
// DataManagerDashboard tests
// ---------------------------------------------------------------------------

describe('DataManagerDashboard', () => {
  it('renders without crashing', () => {
    render(<DataManagerDashboard />);
    expect(document.body).toBeInTheDocument();
  });

  it('shows "Total Records" stat', () => {
    render(<DataManagerDashboard />);
    expect(screen.getByText('Total Records')).toBeInTheDocument();
  });

  it('shows "Warnings" stat', () => {
    render(<DataManagerDashboard />);
    expect(screen.getByText('Warnings')).toBeInTheDocument();
  });

  it('shows "Errors" stat', () => {
    render(<DataManagerDashboard />);
    expect(screen.getByText('Errors')).toBeInTheDocument();
  });

  it('shows "Game Version" stat', () => {
    render(<DataManagerDashboard />);
    expect(screen.getByText('Game Version')).toBeInTheDocument();
  });

  it('renders the Data Sources table', () => {
    render(<DataManagerDashboard />);
    expect(screen.getByText('Data Sources')).toBeInTheDocument();
  });

  it('shows known data source names', () => {
    render(<DataManagerDashboard />);
    expect(screen.getByText('Skills')).toBeInTheDocument();
    expect(screen.getByText('Affixes')).toBeInTheDocument();
    expect(screen.getByText('Passives')).toBeInTheDocument();
  });

  it('shows "Base Items" data source', () => {
    render(<DataManagerDashboard />);
    expect(screen.getByText('Base Items')).toBeInTheDocument();
  });

  it('shows "Unique Items" data source', () => {
    render(<DataManagerDashboard />);
    expect(screen.getByText('Unique Items')).toBeInTheDocument();
  });

  it('renders the Reload Controls panel', () => {
    render(<DataManagerDashboard />);
    expect(screen.getByText('Reload Controls')).toBeInTheDocument();
  });

  it('renders the Reload All Data button', () => {
    render(<DataManagerDashboard />);
    expect(screen.getByText('Reload All Data')).toBeInTheDocument();
  });

  it('clicking reload button starts reload process', async () => {
    render(<DataManagerDashboard />);
    const btn = screen.getByText('Reload All Data');
    await act(async () => { fireEvent.click(btn); });
    expect(screen.getByText('Reloading...')).toBeInTheDocument();
  });

  it('shows total records count', () => {
    render(<DataManagerDashboard />);
    // 132 + 534 + 847 + 110 + 403 + 48 = 2074
    expect(screen.getByText('2,074')).toBeInTheDocument();
  });

  it('shows warning count for mock data', () => {
    render(<DataManagerDashboard />);
    // Unique Items has "warn" status
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('shows table headers', () => {
    render(<DataManagerDashboard />);
    expect(screen.getByText('Source')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Items')).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// ErrorReportingPanel tests
// ---------------------------------------------------------------------------

describe('ErrorReportingPanel', () => {
  it('renders without crashing', () => {
    render(<ErrorReportingPanel />);
    expect(document.body).toBeInTheDocument();
  });

  it('renders "Validation Report" title', () => {
    render(<ErrorReportingPanel />);
    expect(screen.getByText('Validation Report')).toBeInTheDocument();
  });

  it('shows default mock errors', () => {
    render(<ErrorReportingPanel />);
    expect(screen.getByText(/48 items missing level_req field/)).toBeInTheDocument();
  });

  it('shows filter tabs', () => {
    render(<ErrorReportingPanel />);
    expect(screen.getByText('All')).toBeInTheDocument();
    expect(screen.getByText('error')).toBeInTheDocument();
    expect(screen.getByText('warning')).toBeInTheDocument();
    expect(screen.getByText('info')).toBeInTheDocument();
  });

  it('filters to show only warnings when warning tab clicked', async () => {
    render(<ErrorReportingPanel />);
    const warningTab = screen.getByText('warning');
    await act(async () => { fireEvent.click(warningTab); });
    // Only warning items should show
    expect(screen.getByText(/48 items missing level_req field/)).toBeInTheDocument();
    expect(screen.queryByText(/All 534 nodes/)).not.toBeInTheDocument();
  });

  it('filters to show only info when info tab clicked', async () => {
    render(<ErrorReportingPanel />);
    const infoTab = screen.getByText('info');
    await act(async () => { fireEvent.click(infoTab); });
    expect(screen.getByText(/All 534 nodes have descriptions/)).toBeInTheDocument();
    expect(screen.queryByText(/48 items missing/)).not.toBeInTheDocument();
  });

  it('dismisses an error when dismiss button clicked', async () => {
    render(<ErrorReportingPanel />);
    const dismissButtons = screen.getAllByLabelText('Dismiss');
    await act(async () => { fireEvent.click(dismissButtons[0]); });
    // One fewer error visible
    const remaining = screen.getAllByLabelText('Dismiss');
    expect(remaining.length).toBe(dismissButtons.length - 1);
  });

  it('renders "Dismiss All" button', () => {
    render(<ErrorReportingPanel />);
    expect(screen.getByText('Dismiss All')).toBeInTheDocument();
  });

  it('dismisses all errors when Dismiss All clicked', async () => {
    render(<ErrorReportingPanel />);
    const dismissAll = screen.getByText('Dismiss All');
    await act(async () => { fireEvent.click(dismissAll); });
    expect(screen.getByText('All issues dismissed.')).toBeInTheDocument();
  });

  it('calls onDismiss callback when error dismissed', async () => {
    const onDismiss = vi.fn();
    render(<ErrorReportingPanel onDismiss={onDismiss} />);
    const dismissButtons = screen.getAllByLabelText('Dismiss');
    await act(async () => { fireEvent.click(dismissButtons[0]); });
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it('calls onDismissAll callback when Dismiss All clicked', async () => {
    const onDismissAll = vi.fn();
    render(<ErrorReportingPanel onDismissAll={onDismissAll} />);
    const dismissAll = screen.getByText('Dismiss All');
    await act(async () => { fireEvent.click(dismissAll); });
    expect(onDismissAll).toHaveBeenCalledTimes(1);
  });

  it('accepts external errors prop', () => {
    const errors: ValidationError[] = [
      { id: 'ext1', severity: 'error', source: 'TestSource', message: 'Test error message' },
    ];
    render(<ErrorReportingPanel errors={errors} />);
    expect(screen.getByText('Test error message')).toBeInTheDocument();
    expect(screen.getByText('TestSource')).toBeInTheDocument();
  });

  it('shows field when provided in error', () => {
    const errors: ValidationError[] = [
      { id: 'f1', severity: 'warning', source: 'Items', message: 'Missing field', field: 'level_req' },
    ];
    render(<ErrorReportingPanel errors={errors} />);
    expect(screen.getByText(/level_req/)).toBeInTheDocument();
  });

  it('shows "No issues found" when no external errors', () => {
    render(<ErrorReportingPanel errors={[]} />);
    expect(screen.getByText('No issues found. All data is valid.')).toBeInTheDocument();
  });
});
