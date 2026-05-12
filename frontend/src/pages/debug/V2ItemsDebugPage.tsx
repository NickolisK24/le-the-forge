import { FormEvent, useEffect, useMemo, useState } from "react";

import type { CanonicalImplicit, CanonicalItemBase } from "@/types";

interface V2ItemResponse {
  success: boolean;
  experimental?: boolean;
  read_only?: boolean;
  production_consumer?: boolean;
  data_source?: string;
  source_path?: string;
  total_item_bases?: number;
  total_implicits?: number;
  result_count?: number;
  records?: Array<CanonicalItemBase | CanonicalImplicit>;
  summary?: Record<string, unknown>;
  error?: string;
  message?: string;
}

const DEFAULT_LIMIT = 10;

function buildUrl(kind: "bases" | "implicits", limit: number, query: string, slot: string): string {
  const params = new URLSearchParams();
  params.set("limit", String(limit));
  if (query.trim()) params.set("q", query.trim());
  if (slot.trim() && kind === "bases") params.set("slot", slot.trim());
  return `/experimental/v2/items/${kind}?${params.toString()}`;
}

async function fetchV2Items(kind: "bases" | "implicits", limit: number, query: string, slot: string): Promise<V2ItemResponse> {
  const response = await fetch(buildUrl(kind, limit, query, slot));
  const json = await response.json().catch(() => null);
  if (!json || typeof json !== "object") {
    return {
      success: false,
      error: "invalid_response",
      message: `Backend returned an unreadable response (${response.status}).`,
    };
  }
  return json as V2ItemResponse;
}

export default function V2ItemsDebugPage() {
  const [kind, setKind] = useState<"bases" | "implicits">("bases");
  const [limit, setLimit] = useState(DEFAULT_LIMIT);
  const [query, setQuery] = useState("");
  const [slot, setSlot] = useState("");
  const [data, setData] = useState<V2ItemResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async (nextKind = kind, nextLimit = limit, nextQuery = query, nextSlot = slot) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchV2Items(nextKind, nextLimit, nextQuery, nextSlot);
      setData(result);
      if (!result.success) setError(result.message || result.error || "Debug endpoint returned an error.");
    } catch (err) {
      setData(null);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load("bases", DEFAULT_LIMIT, "", "");
    // Initial debug fetch only for this dev-only route.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    load(kind, limit, query, slot);
  }

  const records = data?.records ?? [];
  const summary = useMemo(
    () => [
      ["Data source", data?.data_source ?? "n/a"],
      ["Item bases", data?.total_item_bases ?? "n/a"],
      ["Implicits", data?.total_implicits ?? "n/a"],
      ["Support", summarizeMap(data?.summary, "support_status_counts")],
      ["Trust", summarizeMap(data?.summary, "trust_level_counts")],
      ["Read only", String(data?.read_only ?? false)],
      ["Production consumer", String(data?.production_consumer ?? false)],
    ],
    [data],
  );

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-6">
      <header className="border-b border-[#2a3050] pb-4">
        <p className="font-mono text-xs uppercase tracking-wide text-[#22d3ee]">
          Debug / Experimental / Read-only
        </p>
        <h1 className="mt-2 font-display text-2xl text-[#f5a623]">
          v2 item base and implicit inspection
        </h1>
        <p className="mt-2 max-w-3xl text-sm text-gray-400">
          This page reads v2 item bundles for diagnostics and does not power planner behavior.
        </p>
      </header>

      <section className="rounded border border-[#2a3050] bg-[#10152a] p-4">
        <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-4">
          <label className="grid gap-1 text-sm text-gray-300">
            <span className="text-xs uppercase text-gray-500">Kind</span>
            <select
              value={kind}
              onChange={(event) => setKind(event.target.value as "bases" | "implicits")}
              className="w-36 rounded border border-[#2a3050] bg-[#0f172a] px-3 py-2 text-gray-100"
            >
              <option value="bases">Bases</option>
              <option value="implicits">Implicits</option>
            </select>
          </label>
          <label className="grid gap-1 text-sm text-gray-300">
            <span className="text-xs uppercase text-gray-500">Limit</span>
            <input
              type="number"
              min={0}
              max={50}
              value={limit}
              onChange={(event) => setLimit(Number(event.target.value))}
              className="w-28 rounded border border-[#2a3050] bg-[#0f172a] px-3 py-2 text-gray-100"
            />
          </label>
          <label className="grid gap-1 text-sm text-gray-300">
            <span className="text-xs uppercase text-gray-500">Search</span>
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="optional"
              className="w-48 rounded border border-[#2a3050] bg-[#0f172a] px-3 py-2 text-gray-100"
            />
          </label>
          <label className="grid gap-1 text-sm text-gray-300">
            <span className="text-xs uppercase text-gray-500">Slot</span>
            <input
              value={slot}
              onChange={(event) => setSlot(event.target.value)}
              placeholder="helmet"
              disabled={kind !== "bases"}
              className="w-36 rounded border border-[#2a3050] bg-[#0f172a] px-3 py-2 text-gray-100 disabled:opacity-50"
            />
          </label>
          <button
            type="submit"
            className="rounded bg-[#f5a623] px-4 py-2 text-sm font-semibold text-[#10152a] hover:bg-[#f5a623cc]"
          >
            Load debug data
          </button>
        </form>
      </section>

      {loading && (
        <div className="rounded border border-[#2a3050] bg-[#0f172a] p-4 text-sm text-gray-300">
          Loading debug endpoint...
        </div>
      )}

      {!loading && error && (
        <section className="rounded border border-red-900 bg-red-950/30 p-4">
          <h2 className="text-sm font-semibold text-red-300">Debug endpoint unavailable</h2>
          <p className="mt-2 text-sm text-red-100">{error}</p>
        </section>
      )}

      {!loading && data?.success && (
        <>
          <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {summary.map(([label, value]) => (
              <div key={label} className="rounded border border-[#2a3050] bg-[#10152a] p-4">
                <div className="text-xs uppercase text-gray-500">{label}</div>
                <div className="mt-2 break-words font-mono text-lg text-gray-100">{value}</div>
              </div>
            ))}
          </section>

          <section className="rounded border border-[#2a3050] bg-[#10152a] p-4">
            <h2 className="text-sm font-semibold text-gray-100">Source</h2>
            <p className="mt-2 break-all font-mono text-xs text-gray-400">{data.source_path}</p>
          </section>

          <section className="overflow-hidden rounded border border-[#2a3050] bg-[#10152a]">
            <div className="border-b border-[#2a3050] p-4">
              <h2 className="text-sm font-semibold text-gray-100">Records</h2>
              <p className="mt-1 text-xs text-gray-500">Showing {records.length} records.</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[820px] text-left text-sm">
                <thead className="bg-[#0f172a] text-xs uppercase text-gray-500">
                  <tr>
                    <th className="px-4 py-3">Canonical ID</th>
                    <th className="px-4 py-3">Name</th>
                    <th className="px-4 py-3">Support</th>
                    <th className="px-4 py-3">Trust</th>
                    <th className="px-4 py-3">Type</th>
                    <th className="px-4 py-3">Slot/Base</th>
                    <th className="px-4 py-3">Links</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#2a3050]">
                  {records.map((record) => (
                    <tr key={record.canonical_id}>
                      <td className="px-4 py-3 font-mono text-[#f5a623]">{record.canonical_id}</td>
                      <td className="px-4 py-3 text-gray-100">{record.display_name}</td>
                      <td className="px-4 py-3">{statusBadge(record.support_status)}</td>
                      <td className="px-4 py-3 text-gray-300">{record.trust_level}</td>
                      <td className="px-4 py-3 text-gray-300">{itemType(record)}</td>
                      <td className="px-4 py-3 font-mono text-gray-300">{slotOrBase(record)}</td>
                      <td className="px-4 py-3 font-mono text-gray-300">{linkCount(record)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}

function summarizeMap(summary: Record<string, unknown> | undefined, key: string): string {
  const value = summary?.[key];
  if (!value || typeof value !== "object" || Array.isArray(value)) return "n/a";
  return Object.entries(value as Record<string, unknown>)
    .map(([name, count]) => `${name}: ${count}`)
    .join(", ");
}

function statusBadge(status: string) {
  const classes =
    status === "trusted"
      ? "border-emerald-700 bg-emerald-950 text-emerald-200"
      : status === "partial"
        ? "border-yellow-700 bg-yellow-950 text-yellow-200"
        : "border-gray-700 bg-gray-900 text-gray-300";
  return (
    <span className={`inline-flex rounded border px-2 py-1 font-mono text-xs ${classes}`}>
      {status}
    </span>
  );
}

function itemType(record: CanonicalItemBase | CanonicalImplicit): string {
  return "item_type" in record && record.item_type ? record.item_type : "n/a";
}

function slotOrBase(record: CanonicalItemBase | CanonicalImplicit): string {
  if ("slot" in record && record.slot) return record.slot;
  if ("item_base_id" in record && record.item_base_id) return record.item_base_id;
  return "n/a";
}

function linkCount(record: CanonicalItemBase | CanonicalImplicit): number | string {
  if ("implicit_ids" in record) return record.implicit_ids.length;
  if ("modifier_references" in record) return record.modifier_references.length;
  return "n/a";
}
