import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import AffixCatalogPage from '@/components/features/affixCatalog/AffixCatalogPage';

function renderPage(enabled = true) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <AffixCatalogPage enabled={enabled} />
    </QueryClientProvider>
  );
}

describe('AffixCatalogPage', () => {
  beforeEach(() => {
    vi.stubEnv('VITE_FORGE_SAFE_AFFIX_CATALOG_ENABLED', 'true');
    global.fetch = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes('/affixes/catalog/summary')) {
        return new Response(JSON.stringify({
          data: { active_source: 'forge_safe', mode: 'read_only', consumption_enabled: true, legacy_count: 2, forge_safe_count: 2, production_consumer: false },
          meta: null,
          errors: null,
        }), { status: 200, headers: { 'Content-Type': 'application/json' } });
      }
      return new Response(JSON.stringify({
        data: [
          { id: 'health', name: 'Health', source_type: 'prefix', item_types: ['helm'], data_source: 'forge_safe', safety: { forge_safe: true }, production_consumer: false },
          { id: 'fire_res', name: 'Fire Resistance', source_type: 'suffix', item_types: ['ring'], data_source: 'forge_safe', safety: { forge_safe: true }, production_consumer: false },
        ],
        meta: { total: 2, limit: 100, offset: 0, data_source: 'forge_safe', mode: 'read_only', production_consumer: false },
        errors: null,
      }), { status: 200, headers: { 'Content-Type': 'application/json' } });
    }) as any;
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
  });


  it('renders disabled state when the feature gate is off', () => {
    renderPage(false);
    expect(screen.getByTestId('affix-catalog-disabled')).toHaveTextContent('disabled');
  });

  it('renders Forge-safe data and loaded count', async () => {
    renderPage();
    expect(await screen.findByText('Forge-safe Affix Catalog')).toBeInTheDocument();
    expect(await screen.findByText('Health')).toBeInTheDocument();
    expect(screen.getByText('Forge-safe canonical export')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('sends search and filter interactions to the catalog endpoint', async () => {
    renderPage();
    await screen.findByText('Health');
    fireEvent.change(screen.getByLabelText('Search affixes'), { target: { value: 'res' } });
    fireEvent.change(screen.getByLabelText('Source type'), { target: { value: 'suffix' } });
    fireEvent.change(screen.getByLabelText('Item type'), { target: { value: 'ring' } });
    await waitFor(() => {
      const calls = (global.fetch as any).mock.calls.map((call: any[]) => String(call[0]));
      expect(calls.some((url: string) => url.includes('q=res') && url.includes('source_type=suffix') && url.includes('item_type=ring'))).toBe(true);
    });
  });

  it('renders affix detail when selected', async () => {
    renderPage();
    fireEvent.click(await screen.findByText('Fire Resistance'));
    expect(screen.getByTestId('affix-detail')).toHaveTextContent('fire_res');
    expect(screen.getByTestId('affix-detail')).toHaveTextContent('forge_safe=true');
  });
});
