/**
 * R0 regression: Last Epoch Tools planner URLs must not be sent to the
 * server-side importer (it is blocked upstream; production received HTTP 403).
 * The user is routed to the JSON/bookmarklet flow with their URL preserved.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import React from 'react';

const importBuild = vi.fn();
const fromUrl = vi.fn();
const letFromJson = vi.fn();

vi.mock('@/lib/api', () => ({
  importApi: {
    importBuild: (...args: unknown[]) => importBuild(...args),
    fromUrl: (...args: unknown[]) => fromUrl(...args),
    letFromJson: (...args: unknown[]) => letFromJson(...args),
  },
}));

vi.mock('react-hot-toast', () => ({ default: { success: vi.fn(), error: vi.fn() } }));

import BuildImportModal from '@/components/features/build/BuildImportModal';
import { decideUrlImport, detectImportSource } from '@/lib/importRouting';

const INCIDENT_URL = 'https://www.lastepochtools.com/planner/B5P5P8M3';

function renderModal() {
  const onImport = vi.fn();
  const onClose = vi.fn();
  render(
    <MemoryRouter>
      <BuildImportModal onImport={onImport} onClose={onClose} />
    </MemoryRouter>,
  );
  return { onImport, onClose };
}

function submitUrl(url: string) {
  fireEvent.change(screen.getByPlaceholderText(/maxroll\.gg\/last-epoch\/planner/), {
    target: { value: url },
  });
  fireEvent.click(screen.getByRole('button', { name: /Next: capture from browser|Import Build/ }));
}

describe('decideUrlImport', () => {
  it('routes LET planner URLs to the JSON flow, never the server', () => {
    expect(decideUrlImport(INCIDENT_URL)).toEqual({
      kind: 'let_json_required',
      source: 'lastepochtools',
      url: INCIDENT_URL,
    });
    expect(decideUrlImport(`  ${INCIDENT_URL}  `).kind).toBe('let_json_required');
  });

  it('keeps Maxroll on the server importer', () => {
    const url = 'https://maxroll.gg/last-epoch/planner/zge0t60e';
    expect(decideUrlImport(url)).toEqual({ kind: 'server_import', source: 'maxroll', url });
  });

  it('rejects unknown sources and empty input', () => {
    expect(decideUrlImport('https://example.com/build/1').kind).toBe('unsupported');
    expect(decideUrlImport('   ').kind).toBe('empty');
    expect(detectImportSource('https://example.com')).toBeNull();
  });
});

describe('BuildImportModal — Last Epoch Tools URL', () => {
  beforeEach(() => {
    importBuild.mockReset();
    fromUrl.mockReset();
    letFromJson.mockReset();
  });

  it('does not call the server importer for a LET planner URL', async () => {
    renderModal();
    submitUrl(INCIDENT_URL);
    expect(await screen.findByTestId('let-json-required')).toBeInTheDocument();
    expect(importBuild).not.toHaveBeenCalled();
    expect(fromUrl).not.toHaveBeenCalled();
  });

  it('explains the extra step without calling the URL invalid or expired', async () => {
    renderModal();
    submitUrl(INCIDENT_URL);
    const panel = await screen.findByTestId('let-json-required');
    expect(panel).toHaveTextContent(/link looks right/i);
    expect(panel).toHaveTextContent(/blocks requests from our server/i);
    expect(panel.textContent?.toLowerCase()).not.toMatch(/invalid|expired/);
  });

  it('routes the user to the JSON tab with the original URL preserved', async () => {
    renderModal();
    submitUrl(INCIDENT_URL);
    fireEvent.click(await screen.findByRole('button', { name: /Continue with Last Epoch Tools import/ }));
    const link = await screen.findByTestId('let-original-url');
    expect(link).toHaveAttribute('href', INCIDENT_URL);
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    expect(screen.getByText(/The Forge: Copy LET Build/)).toBeInTheDocument();
  });

  it('still sends Maxroll URLs to the server importer', async () => {
    importBuild.mockResolvedValue({
      data: { slug: 's', build_name: 'B', source: 'maxroll', imported_fields: [], missing_fields: [], warnings: [] },
      meta: null,
      errors: null,
    });
    renderModal();
    submitUrl('https://maxroll.gg/last-epoch/planner/zge0t60e');
    await waitFor(() => expect(importBuild).toHaveBeenCalledWith('https://maxroll.gg/last-epoch/planner/zge0t60e'));
  });

  it('switches to the JSON flow if the backend reports LET_SERVER_FETCH_UNSUPPORTED', async () => {
    // Defensive path: e.g. a URL the client did not recognise as LET.
    importBuild.mockResolvedValue({
      data: null,
      meta: null,
      errors: [{ code: 'LET_SERVER_FETCH_UNSUPPORTED', message: 'unsupported' }],
    });
    renderModal();
    submitUrl('https://maxroll.gg/last-epoch/planner/x');
    expect(await screen.findByTestId('let-json-required')).toBeInTheDocument();
  });

  it('still imports pasted LET JSON through the JSON tab', async () => {
    letFromJson.mockResolvedValue({
      data: { build: { character_class: 'Sentinel', mastery: 'Paladin', level: 85, passive_tree: [], skills: [], gear: [] } },
      meta: null,
      errors: null,
    });
    const { onImport } = renderModal();
    fireEvent.click(screen.getByRole('button', { name: /\{ \} JSON/ }));
    fireEvent.change(screen.getByPlaceholderText(/character_class/), {
      target: { value: JSON.stringify({ bio: { characterClass: 2, chosenMastery: 3, level: 85 }, charTree: {} }) },
    });
    fireEvent.click(screen.getByRole('button', { name: /Import →/ }));
    await waitFor(() => expect(onImport).toHaveBeenCalled());
    expect(letFromJson).toHaveBeenCalledTimes(1);
  });
});
