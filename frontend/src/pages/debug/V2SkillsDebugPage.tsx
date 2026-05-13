import { FormEvent, useEffect, useMemo, useState } from "react";

import type { CanonicalSkill } from "@/types";

interface V2SkillResponse {
  success: boolean;
  read_only?: boolean;
  production_consumer?: boolean;
  data_source?: string;
  source_path?: string;
  total_skills?: number;
  total_skill_trees?: number;
  total_skill_nodes?: number;
  result_count?: number;
  records?: CanonicalSkill[];
  summary?: Record<string, unknown>;
  error?: string;
  message?: string;
}

const DEFAULT_LIMIT = 10;

function buildUrl(limit: number, query: string, classId: string): string {
  const params = new URLSearchParams();
  params.set("limit", String(limit));
  if (query.trim()) params.set("q", query.trim());
  if (classId.trim()) params.set("class_id", classId.trim());
  return `/experimental/v2/skills?${params.toString()}`;
}

async function fetchV2Skills(limit: number, query: string, classId: string): Promise<V2SkillResponse> {
  const response = await fetch(buildUrl(limit, query, classId));
  const json = await response.json().catch(() => null);
  if (!json || typeof json !== "object") {
    return { success: false, error: "invalid_response", message: `Backend returned an unreadable response (${response.status}).` };
  }
  return json as V2SkillResponse;
}

export default function V2SkillsDebugPage() {
  const [limit, setLimit] = useState(DEFAULT_LIMIT);
  const [query, setQuery] = useState("");
  const [classId, setClassId] = useState("");
  const [data, setData] = useState<V2SkillResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async (nextLimit = limit, nextQuery = query, nextClassId = classId) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchV2Skills(nextLimit, nextQuery, nextClassId);
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
    load(DEFAULT_LIMIT, "", "");
    // Initial debug fetch only for this dev-only route.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    load(limit, query, classId);
  }

  const records = data?.records ?? [];
  const summary = useMemo(
    () => [
      ["Data source", data?.data_source ?? "n/a"],
      ["Skills", data?.total_skills ?? "n/a"],
      ["Trees", data?.total_skill_trees ?? "n/a"],
      ["Nodes", data?.total_skill_nodes ?? "n/a"],
      ["Support", summarizeMap(data?.summary, "support_status_counts")],
      ["Behavior", summarizeMap(data?.summary, "skill_special_behavior_classification_counts")],
      ["Read only", String(data?.read_only ?? false)],
      ["Production consumer", String(data?.production_consumer ?? false)],
    ],
    [data],
  );

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-6">
      <header className="border-b border-[#2a3050] pb-4">
        <p className="font-mono text-xs uppercase tracking-wide text-[#22d3ee]">Debug / Experimental / Read-only</p>
        <h1 className="mt-2 font-display text-2xl text-[#f5a623]">v2 skill tree inspection</h1>
        <p className="mt-2 max-w-3xl text-sm text-gray-400">This page reads v2 skill and skill tree records for diagnostics and does not power planner behavior.</p>
      </header>

      <section className="rounded border border-[#2a3050] bg-[#10152a] p-4">
        <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-4">
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
              <h2 className="text-sm font-semibold text-gray-100">Skills</h2>
              <p className="mt-1 text-xs text-gray-500">Showing {records.length} skills.</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[980px] text-left text-sm">
                <thead className="bg-[#0f172a] text-xs uppercase text-gray-500">
                  <tr>
                    <th className="px-4 py-3">Canonical ID</th>
                    <th className="px-4 py-3">Name</th>
                    <th className="px-4 py-3">Support</th>
                    <th className="px-4 py-3">Trust</th>
                    <th className="px-4 py-3">Tags</th>
                    <th className="px-4 py-3">Behavior</th>
                    <th className="px-4 py-3">Tree</th>
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
                      <td className="px-4 py-3 text-gray-300">{record.skill_tags?.join(", ") || "n/a"}</td>
                      <td className="px-4 py-3">{behaviorBadge(record.special_behavior_classification ?? "unknown")}</td>
                      <td className="px-4 py-3 font-mono text-gray-300">{record.skill_tree_id ?? "n/a"}</td>
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

function behaviorBadge(status: string) {
  const classes = status === "partial_modifier" ? "border-cyan-700 bg-cyan-950 text-cyan-200" : "border-orange-800 bg-orange-950 text-orange-200";
  return <span className={`inline-flex rounded border px-2 py-1 font-mono text-xs ${classes}`}>{status}</span>;
}
