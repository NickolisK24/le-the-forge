import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { affixCatalogApi } from "@/lib/api";
import type { AffixCatalogEntry } from "@/types";

const DEFAULT_ENABLED = import.meta.env.VITE_FORGE_SAFE_AFFIX_CATALOG_ENABLED === "true" || import.meta.env.DEV;

export default function AffixCatalogPage({ enabled = DEFAULT_ENABLED }: { enabled?: boolean } = {}) {
  const [query, setQuery] = useState("");
  const [sourceType, setSourceType] = useState("");
  const [itemType, setItemType] = useState("");
  const [selected, setSelected] = useState<AffixCatalogEntry | null>(null);

  const params = useMemo(() => ({ q: query || undefined, source_type: sourceType || undefined, item_type: itemType || undefined, limit: 100 }), [query, sourceType, itemType]);

  const summaryQuery = useQuery({
    queryKey: ["affix-catalog", "summary"],
    queryFn: () => affixCatalogApi.summary(),
    enabled,
  });

  const catalogQuery = useQuery({
    queryKey: ["affix-catalog", params],
    queryFn: () => affixCatalogApi.list(params),
    enabled,
  });

  if (!enabled) {
    return (
      <main className="p-6 space-y-4" data-testid="affix-catalog-disabled">
        <h1 className="text-2xl font-semibold text-forge-text">Forge-safe Affix Catalog</h1>
        <p className="text-forge-muted">This development catalog is disabled. Set VITE_FORGE_SAFE_AFFIX_CATALOG_ENABLED=true to browse the controlled Forge-safe export.</p>
      </main>
    );
  }

  const affixes = catalogQuery.data?.data ?? [];
  const meta = catalogQuery.data?.meta;
  const summary = summaryQuery.data?.data;
  const error = catalogQuery.data?.errors?.[0]?.message ?? summaryQuery.data?.errors?.[0]?.message;

  return (
    <main className="p-6 space-y-6" data-testid="affix-catalog-page">
      <header className="space-y-2">
        <p className="text-sm uppercase tracking-wide text-forge-cyan">Controlled read-only source</p>
        <h1 className="text-3xl font-semibold text-forge-text">Forge-safe Affix Catalog</h1>
        <p className="max-w-3xl text-forge-muted">
          Browses the Forge-safe canonical export for lookup and migration review only. Planner, crafting, and simulation selections are not changed by this page.
        </p>
      </header>

      <section className="grid gap-3 md:grid-cols-3">
        <div className="rounded-lg border border-forge-border bg-forge-panel p-4">
          <div className="text-sm text-forge-muted">Data source</div>
          <div className="text-xl font-semibold text-forge-text">{meta?.data_source ?? summary?.active_source ?? "forge_safe"}</div>
          <div className="text-xs text-forge-muted">Forge-safe canonical export</div>
        </div>
        <div className="rounded-lg border border-forge-border bg-forge-panel p-4">
          <div className="text-sm text-forge-muted">Loaded Forge-safe affixes</div>
          <div className="text-xl font-semibold text-forge-text">{summary?.forge_safe_count ?? meta?.total ?? 0}</div>
        </div>
        <div className="rounded-lg border border-forge-border bg-forge-panel p-4">
          <div className="text-sm text-forge-muted">Mode</div>
          <div className="text-xl font-semibold text-forge-text">{summary?.mode ?? meta?.mode ?? "read_only"}</div>
          <div className="text-xs text-forge-muted">production_consumer=false</div>
        </div>
      </section>

      <section className="rounded-lg border border-forge-border bg-forge-panel p-4 space-y-4">
        <div className="grid gap-3 md:grid-cols-3">
          <label className="space-y-1">
            <span className="text-sm text-forge-muted">Search</span>
            <input aria-label="Search affixes" className="w-full rounded bg-forge-bg border border-forge-border px-3 py-2 text-forge-text" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="health, resistance..." />
          </label>
          <label className="space-y-1">
            <span className="text-sm text-forge-muted">Source type</span>
            <select aria-label="Source type" className="w-full rounded bg-forge-bg border border-forge-border px-3 py-2 text-forge-text" value={sourceType} onChange={(e) => setSourceType(e.target.value)}>
              <option value="">All</option>
              <option value="prefix">Prefix</option>
              <option value="suffix">Suffix</option>
            </select>
          </label>
          <label className="space-y-1">
            <span className="text-sm text-forge-muted">Item type</span>
            <input aria-label="Item type" className="w-full rounded bg-forge-bg border border-forge-border px-3 py-2 text-forge-text" value={itemType} onChange={(e) => setItemType(e.target.value)} placeholder="helm, ring..." />
          </label>
        </div>

        {error && <div role="alert" className="rounded border border-red-500/40 bg-red-500/10 p-3 text-red-200">{error}</div>}

        <div className="grid gap-4 lg:grid-cols-[1fr_22rem]">
          <div className="overflow-hidden rounded border border-forge-border">
            <table className="w-full text-left text-sm">
              <thead className="bg-forge-bg text-forge-muted">
                <tr><th className="p-3">Name</th><th className="p-3">Source</th><th className="p-3">Item types</th></tr>
              </thead>
              <tbody>
                {affixes.map((affix) => (
                  <tr key={affix.id} className="border-t border-forge-border hover:bg-forge-bg/60 cursor-pointer" onClick={() => setSelected(affix)}>
                    <td className="p-3 text-forge-text">{affix.name}</td>
                    <td className="p-3 text-forge-muted">{affix.source_type ?? "unknown"}</td>
                    <td className="p-3 text-forge-muted">{affix.item_types.join(", ") || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!catalogQuery.isLoading && affixes.length === 0 && <p className="p-4 text-forge-muted">No affixes match the current filters.</p>}
          </div>

          <aside className="rounded border border-forge-border bg-forge-bg p-4" data-testid="affix-detail">
            <h2 className="text-lg font-semibold text-forge-text">Affix detail</h2>
            {selected ? (
              <dl className="mt-3 space-y-2 text-sm">
                <div><dt className="text-forge-muted">Name</dt><dd className="text-forge-text">{selected.name}</dd></div>
                <div><dt className="text-forge-muted">ID</dt><dd className="text-forge-text break-all">{selected.id}</dd></div>
                <div><dt className="text-forge-muted">Source type</dt><dd className="text-forge-text">{selected.source_type ?? "unknown"}</dd></div>
                <div><dt className="text-forge-muted">Item types</dt><dd className="text-forge-text">{selected.item_types.join(", ") || "—"}</dd></div>
                <div><dt className="text-forge-muted">Safety</dt><dd className="text-forge-text">forge_safe=true · production_consumer=false</dd></div>
              </dl>
            ) : <p className="mt-3 text-sm text-forge-muted">Select an affix to inspect its safe metadata.</p>}
          </aside>
        </div>
      </section>
    </main>
  );
}
