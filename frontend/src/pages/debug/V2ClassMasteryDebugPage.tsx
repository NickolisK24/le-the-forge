import { FormEvent, useEffect, useMemo, useState } from "react";

import type { CanonicalClass, CanonicalMastery } from "@/types";

interface V2ClassMasteryResponse {
  success: boolean;
  read_only?: boolean;
  production_consumer?: boolean;
  data_source?: string;
  source_path?: string;
  total_classes?: number;
  total_masteries?: number;
  result_count?: number;
  records?: Array<CanonicalClass | CanonicalMastery>;
  summary?: Record<string, unknown>;
  error?: string;
  message?: string;
}

const DEFAULT_LIMIT = 20;

function buildUrl(kind: "classes" | "masteries", limit: number, query: string, classId: string): string {
  const params = new URLSearchParams();
  params.set("limit", String(limit));
  if (query.trim()) params.set("q", query.trim());
  if (kind === "masteries" && classId.trim()) params.set("class_id", classId.trim());
  return `/experimental/v2/${kind}?${params.toString()}`;
}

async function fetchV2ClassMastery(kind: "classes" | "masteries", limit: number, query: string, classId: string): Promise<V2ClassMasteryResponse> {
  const response = await fetch(buildUrl(kind, limit, query, classId));
  const json = await response.json().catch(() => null);
  if (!json || typeof json !== "object") {
    return { success: false, error: "invalid_response", message: `Backend returned an unreadable response (${response.status}).` };
  }
  return json as V2ClassMasteryResponse;
}

export default function V2ClassMasteryDebugPage() {
  const [kind, setKind] = useState<"classes" | "masteries">("classes");
  const [limit, setLimit] = useState(DEFAULT_LIMIT);
  const [query, setQuery] = useState("");
  const [classId, setClassId] = useState("");
  const [data, setData] = useState<V2ClassMasteryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async (nextKind = kind, nextLimit = limit, nextQuery = query, nextClassId = classId) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchV2ClassMastery(nextKind, nextLimit, nextQuery, nextClassId);
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
    load("classes", DEFAULT_LIMIT, "", "");
    // Initial debug fetch only for this dev-only route.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    load(kind, limit, query, classId);
  }

  const records = data?.records ?? [];
  const summary = useMemo(
    () => [
      ["Data source", data?.data_source ?? "n/a"],
      ["Classes", data?.total_classes ?? "n/a"],
      ["Masteries", data?.total_masteries ?? "n/a"],
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
        <p className="font-mono text-xs uppercase tracking-wide text-[#22d3ee]">Debug / Experimental / Read-only</p>
        <h1 className="mt-2 font-display text-2xl text-[#f5a623]">v2 class and mastery inspection</h1>
        <p className="mt-2 max-w-3xl text-sm text-gray-400">This page reads v2 class/mastery records for diagnostics and does not power planner behavior.</p>
      </header>

      <section className="rounded border border-[#2a3050] bg-[#10152a] p-4">
        <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-4">
          <label className="grid gap-1 text-sm text-gray-300">
            <span className="text-xs uppercase text-gray-500">Kind</span>
            <select value={kind} onChange={(event) => setKind(event.target.value as "classes" | "masteries")} className="w-36 rounded border border-[#2a3050] bg-[#0f172a] px-3 py-2 text-gray-100">
              <option value="classes">Classes</option>
              <option value="masteries">Masteries</option>
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
            <span className="text-xs uppercase text-gray-500">Class ID</span>
            <input value={classId} onChange={(event) => setClassId(event.target.value)} placeholder="class:mage" className="w-48 rounded border border-[#2a3050] bg-[#0f172a] px-3 py-2 text-gray-100" />
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
                    <th className="px-4 py-3">Parent/Links</th>
                    <th className="px-4 py-3">Restriction Labels</th>
                    <th className="px-4 py-3">Stable</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#2a3050]">
                  {records.map((record) => (
                    <tr key={record.canonical_id}>
                      <td className="px-4 py-3 font-mono text-[#f5a623]">{record.canonical_id}</td>
                      <td className="px-4 py-3 text-gray-100">{record.display_name}</td>
                      <td className="px-4 py-3">{statusBadge(record.support_status)}</td>
                      <td className="px-4 py-3 text-gray-300">{record.trust_level}</td>
                      <td className="px-4 py-3 font-mono text-gray-300">{linkSummary(record)}</td>
                      <td className="px-4 py-3 text-gray-300">{record.known_restriction_labels?.join(", ") || "None"}</td>
                      <td className="px-4 py-3 font-mono text-gray-300">{String(record.stable_calculable ?? false)}</td>
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
  return Object.entries(value as Record<string, unknown>).map(([name, count]) => `${name}: ${count}`).join(", ");
}

function statusBadge(status: string) {
  const classes = status === "partial" ? "border-yellow-700 bg-yellow-950 text-yellow-200" : "border-gray-700 bg-gray-900 text-gray-300";
  return <span className={`inline-flex rounded border px-2 py-1 font-mono text-xs ${classes}`}>{status}</span>;
}

function linkSummary(record: CanonicalClass | CanonicalMastery): string {
  if ("mastery_ids" in record && record.mastery_ids) return `${record.mastery_ids.length} masteries`;
  if ("class_id" in record && record.class_id) return record.class_id;
  return "n/a";
}
