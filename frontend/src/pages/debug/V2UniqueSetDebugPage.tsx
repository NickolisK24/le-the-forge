import { FormEvent, useEffect, useMemo, useState } from "react";

import { V2EnvelopePanels } from "@/components/v2/V2EnvelopePanels";
import {
  getV2ErrorMessage,
  getV2Records,
  getV2SourcePath,
  getV2Summary,
  summarizeMap,
  type V2ApiEnvelope,
} from "@/lib/v2ApiEnvelope";
import type { CanonicalSet, CanonicalUnique } from "@/types";

interface V2UniqueSetResponse extends V2ApiEnvelope<CanonicalUnique | CanonicalSet> {
  success: boolean;
  experimental?: boolean;
  read_only?: boolean;
  production_consumer?: boolean;
  data_source?: string;
  source_path?: string;
  total_uniques?: number;
  total_sets?: number;
  total_set_items?: number;
  total_set_bonuses?: number;
  result_count?: number;
  records?: Array<CanonicalUnique | CanonicalSet>;
  summary?: Record<string, unknown>;
  message?: string;
}

const DEFAULT_LIMIT = 10;

function buildUrl(kind: "uniques" | "sets", limit: number, query: string, slot: string): string {
  const params = new URLSearchParams();
  params.set("limit", String(limit));
  if (query.trim()) params.set("q", query.trim());
  if (slot.trim() && kind === "uniques") params.set("slot", slot.trim());
  return `/experimental/v2/${kind}?${params.toString()}`;
}

async function fetchV2UniqueSets(kind: "uniques" | "sets", limit: number, query: string, slot: string): Promise<V2UniqueSetResponse> {
  const response = await fetch(buildUrl(kind, limit, query, slot));
  const json = await response.json().catch(() => null);
  if (!json || typeof json !== "object") {
    return {
      success: false,
      error: "invalid_response",
      message: `Backend returned an unreadable response (${response.status}).`,
    };
  }
  return json as V2UniqueSetResponse;
}

export default function V2UniqueSetDebugPage() {
  const [kind, setKind] = useState<"uniques" | "sets">("uniques");
  const [limit, setLimit] = useState(DEFAULT_LIMIT);
  const [query, setQuery] = useState("");
  const [slot, setSlot] = useState("");
  const [data, setData] = useState<V2UniqueSetResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async (nextKind = kind, nextLimit = limit, nextQuery = query, nextSlot = slot) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchV2UniqueSets(nextKind, nextLimit, nextQuery, nextSlot);
      setData(result);
      if (!result.success) setError(getV2ErrorMessage(result));
    } catch (err) {
      setData(null);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load("uniques", DEFAULT_LIMIT, "", "");
    // Initial debug fetch only for this dev-only route.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    load(kind, limit, query, slot);
  }

  const records = getV2Records(data);
  const responseSummary = getV2Summary(data);
  const summary = useMemo(
    () => [
      ["Data source", data?.data_source ?? "n/a"],
      ["Uniques", data?.total_uniques ?? "n/a"],
      ["Set groups", data?.total_sets ?? "n/a"],
      ["Set items", data?.total_set_items ?? "n/a"],
      ["Set bonuses", data?.total_set_bonuses ?? "n/a"],
      ["Special", summarizeMap(responseSummary, "special_mechanic_classification_counts")],
      ["Read only", String(data?.read_only ?? false)],
      ["Production consumer", String(data?.production_consumer ?? false)],
    ],
    [data, responseSummary],
  );

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-6">
      <header className="border-b border-[#2a3050] pb-4">
        <p className="font-mono text-xs uppercase tracking-wide text-[#22d3ee]">
          Debug / Experimental / Read-only
        </p>
        <h1 className="mt-2 font-display text-2xl text-[#f5a623]">
          v2 unique and set inspection
        </h1>
        <p className="mt-2 max-w-3xl text-sm text-gray-400">
          This page reads v2 unique/set bundles for diagnostics and does not power planner behavior.
        </p>
      </header>

      <section className="rounded border border-[#2a3050] bg-[#10152a] p-4">
        <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-4">
          <label className="grid gap-1 text-sm text-gray-300">
            <span className="text-xs uppercase text-gray-500">Kind</span>
            <select
              value={kind}
              onChange={(event) => setKind(event.target.value as "uniques" | "sets")}
              className="w-36 rounded border border-[#2a3050] bg-[#0f172a] px-3 py-2 text-gray-100"
            >
              <option value="uniques">Uniques</option>
              <option value="sets">Sets</option>
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
              disabled={kind !== "uniques"}
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
          <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {summary.map(([label, value]) => (
              <div key={label} className="rounded border border-[#2a3050] bg-[#10152a] p-4">
                <div className="text-xs uppercase text-gray-500">{label}</div>
                <div className="mt-2 break-words font-mono text-lg text-gray-100">{value}</div>
              </div>
            ))}
          </section>

          <section className="rounded border border-[#2a3050] bg-[#10152a] p-4">
            <h2 className="text-sm font-semibold text-gray-100">Source</h2>
            <p className="mt-2 break-all font-mono text-xs text-gray-400">{getV2SourcePath(data)}</p>
          </section>

          <V2EnvelopePanels response={data} />

          <section className="overflow-hidden rounded border border-[#2a3050] bg-[#10152a]">
            <div className="border-b border-[#2a3050] p-4">
              <h2 className="text-sm font-semibold text-gray-100">Records</h2>
              <p className="mt-1 text-xs text-gray-500">Showing {records.length} records.</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[940px] text-left text-sm">
                <thead className="bg-[#0f172a] text-xs uppercase text-gray-500">
                  <tr>
                    <th className="px-4 py-3">Canonical ID</th>
                    <th className="px-4 py-3">Name</th>
                    <th className="px-4 py-3">Support</th>
                    <th className="px-4 py-3">Trust</th>
                    <th className="px-4 py-3">Special</th>
                    <th className="px-4 py-3">Type</th>
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
                      <td className="px-4 py-3">{specialBadge(special(record))}</td>
                      <td className="px-4 py-3 text-gray-300">{itemType(record)}</td>
                      <td className="px-4 py-3 font-mono text-gray-300">{linkSummary(record)}</td>
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

function statusBadge(status: string) {
  const classes =
    status === "trusted"
      ? "border-emerald-700 bg-emerald-950 text-emerald-200"
      : status === "partial"
        ? "border-yellow-700 bg-yellow-950 text-yellow-200"
        : "border-gray-700 bg-gray-900 text-gray-300";
  return <span className={`inline-flex rounded border px-2 py-1 font-mono text-xs ${classes}`}>{status}</span>;
}

function specialBadge(value: string) {
  const classes =
    value === "partial_modifier"
      ? "border-cyan-700 bg-cyan-950 text-cyan-200"
      : value === "text_only_effect"
        ? "border-purple-700 bg-purple-950 text-purple-200"
        : "border-gray-700 bg-gray-900 text-gray-300";
  return <span className={`inline-flex rounded border px-2 py-1 font-mono text-xs ${classes}`}>{value}</span>;
}

function special(record: CanonicalUnique | CanonicalSet): string {
  return record.special_mechanic_classification ?? "unknown";
}

function itemType(record: CanonicalUnique | CanonicalSet): string {
  return "item_type" in record && record.item_type ? record.item_type : "n/a";
}

function linkSummary(record: CanonicalUnique | CanonicalSet): number | string {
  if ("modifier_references" in record && record.modifier_references) return record.modifier_references.length;
  if ("item_ids" in record && record.item_ids) return `${record.item_ids.length} items`;
  return "n/a";
}
