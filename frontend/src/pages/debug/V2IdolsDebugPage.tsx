import { FormEvent, useEffect, useMemo, useState } from "react";

import { V2EnvelopePanels } from "@/components/v2/V2EnvelopePanels";
import {
  getV2ErrorMessage,
  getV2Records,
  getV2Summary,
  summarizeMap,
  summarizeV2Support,
  type V2ApiEnvelope,
} from "@/lib/v2ApiEnvelope";
import type { CanonicalIdol, CanonicalIdolAffix } from "@/types";

interface V2IdolResponse extends V2ApiEnvelope<CanonicalIdol | CanonicalIdolAffix> {
  success: boolean;
  read_only?: boolean;
  production_consumer?: boolean;
  data_source?: string;
  source_path?: string;
  total_idols?: number;
  total_idol_affixes?: number;
  result_count?: number;
  records?: Array<CanonicalIdol | CanonicalIdolAffix>;
  summary?: Record<string, unknown>;
  message?: string;
}

const DEFAULT_LIMIT = 10;

function buildUrl(kind: "idols" | "affixes", limit: number, query: string, shape: string): string {
  const params = new URLSearchParams();
  params.set("limit", String(limit));
  if (query.trim()) params.set("q", query.trim());
  if (shape.trim()) params.set(kind === "idols" ? "shape" : "idol_type", shape.trim());
  return `/experimental/v2/idols${kind === "affixes" ? "/affixes" : ""}?${params.toString()}`;
}

async function fetchV2Idols(kind: "idols" | "affixes", limit: number, query: string, shape: string): Promise<V2IdolResponse> {
  const response = await fetch(buildUrl(kind, limit, query, shape));
  const json = await response.json().catch(() => null);
  if (!json || typeof json !== "object") {
    return { success: false, error: "invalid_response", message: `Backend returned an unreadable response (${response.status}).` };
  }
  return json as V2IdolResponse;
}

export default function V2IdolsDebugPage() {
  const [kind, setKind] = useState<"idols" | "affixes">("idols");
  const [limit, setLimit] = useState(DEFAULT_LIMIT);
  const [query, setQuery] = useState("");
  const [shape, setShape] = useState("");
  const [data, setData] = useState<V2IdolResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async (nextKind = kind, nextLimit = limit, nextQuery = query, nextShape = shape) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchV2Idols(nextKind, nextLimit, nextQuery, nextShape);
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
    load("idols", DEFAULT_LIMIT, "", "");
    // Initial debug fetch only for this dev-only route.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    load(kind, limit, query, shape);
  }

  const records = getV2Records(data);
  const responseSummary = getV2Summary(data);
  const summary = useMemo(
    () => [
      ["Data source", data?.data_source ?? "n/a"],
      ["Idols", data?.total_idols ?? "n/a"],
      ["Idol affixes", data?.total_idol_affixes ?? "n/a"],
      ["Support", summarizeV2Support(data)],
      ["Shapes", summarizeMap(responseSummary, "idol_shape_counts") || summarizeMap(responseSummary, "idol_type_restriction_counts")],
      ["Read only", String(data?.read_only ?? false)],
      ["Production consumer", String(data?.production_consumer ?? false)],
    ],
    [data, responseSummary],
  );

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-6">
      <header className="border-b border-[#2a3050] pb-4">
        <p className="font-mono text-xs uppercase tracking-wide text-[#22d3ee]">Debug / Experimental / Read-only</p>
        <h1 className="mt-2 font-display text-2xl text-[#f5a623]">v2 idol inspection</h1>
        <p className="mt-2 max-w-3xl text-sm text-gray-400">This page reads v2 idol bundles for diagnostics and does not power planner behavior.</p>
      </header>

      <section className="rounded border border-[#2a3050] bg-[#10152a] p-4">
        <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-4">
          <label className="grid gap-1 text-sm text-gray-300">
            <span className="text-xs uppercase text-gray-500">Kind</span>
            <select value={kind} onChange={(event) => setKind(event.target.value as "idols" | "affixes")} className="w-36 rounded border border-[#2a3050] bg-[#0f172a] px-3 py-2 text-gray-100">
              <option value="idols">Idols</option>
              <option value="affixes">Affixes</option>
            </select>
          </label>
          <label className="grid gap-1 text-sm text-gray-300">
            <span className="text-xs uppercase text-gray-500">Limit</span>
            <input type="number" min={0} max={50} value={limit} onChange={(event) => setLimit(Number(event.target.value))} className="w-28 rounded border border-[#2a3050] bg-[#0f172a] px-3 py-2 text-gray-100" />
          </label>
          <label className="grid gap-1 text-sm text-gray-300">
            <span className="text-xs uppercase text-gray-500">Search</span>
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="optional" className="w-48 rounded border border-[#2a3050] bg-[#0f172a] px-3 py-2 text-gray-100" />
          </label>
          <label className="grid gap-1 text-sm text-gray-300">
            <span className="text-xs uppercase text-gray-500">Shape</span>
            <input value={shape} onChange={(event) => setShape(event.target.value)} placeholder="idol_1x3" className="w-36 rounded border border-[#2a3050] bg-[#0f172a] px-3 py-2 text-gray-100" />
          </label>
          <button type="submit" className="rounded bg-[#f5a623] px-4 py-2 text-sm font-semibold text-[#10152a] hover:bg-[#f5a623cc]">Load debug data</button>
        </form>
      </section>

      {loading && <div className="rounded border border-[#2a3050] bg-[#0f172a] p-4 text-sm text-gray-300">Loading debug endpoint...</div>}
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
          <V2EnvelopePanels response={data} />
          <section className="overflow-hidden rounded border border-[#2a3050] bg-[#10152a]">
            <div className="border-b border-[#2a3050] p-4">
              <h2 className="text-sm font-semibold text-gray-100">Records</h2>
              <p className="mt-1 text-xs text-gray-500">Showing {records.length} records.</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[900px] text-left text-sm">
                <thead className="bg-[#0f172a] text-xs uppercase text-gray-500">
                  <tr>
                    <th className="px-4 py-3">Canonical ID</th>
                    <th className="px-4 py-3">Name</th>
                    <th className="px-4 py-3">Support</th>
                    <th className="px-4 py-3">Trust</th>
                    <th className="px-4 py-3">Shape/Type</th>
                    <th className="px-4 py-3">Class</th>
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
                      <td className="px-4 py-3 font-mono text-gray-300">{shapeOrType(record)}</td>
                      <td className="px-4 py-3 text-gray-300">{classRestriction(record)}</td>
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

function statusBadge(status: string) {
  const classes = status === "partial" ? "border-yellow-700 bg-yellow-950 text-yellow-200" : "border-gray-700 bg-gray-900 text-gray-300";
  return <span className={`inline-flex rounded border px-2 py-1 font-mono text-xs ${classes}`}>{status}</span>;
}

function shapeOrType(record: CanonicalIdol | CanonicalIdolAffix): string {
  if ("idol_shape" in record && record.idol_shape) return record.idol_shape;
  if ("idol_type_restrictions" in record && record.idol_type_restrictions) return record.idol_type_restrictions.slice(0, 2).join(", ");
  return "n/a";
}

function classRestriction(record: CanonicalIdol | CanonicalIdolAffix): string {
  return record.class_restrictions?.join(", ") || "Any";
}

function linkCount(record: CanonicalIdol | CanonicalIdolAffix): number | string {
  if ("modifier_references" in record && record.modifier_references) return record.modifier_references.length;
  if ("allowed_affix_ids" in record && record.allowed_affix_ids) return record.allowed_affix_ids.length;
  return "n/a";
}
