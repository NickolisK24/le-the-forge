import { FormEvent, useEffect, useMemo, useState } from "react";

import { V2EnvelopePanels } from "@/components/v2/V2EnvelopePanels";
import {
  getV2ErrorMessage,
  getV2Records,
  getV2SourcePath,
  getV2Summary,
  summarizeMap,
  summarizeV2Support,
  type V2ApiEnvelope,
} from "@/lib/v2ApiEnvelope";
import type { CanonicalAffix } from "@/types";

interface V2AffixDebugResponse extends V2ApiEnvelope<CanonicalAffix> {
  success: boolean;
  experimental?: boolean;
  debug_only?: boolean;
  read_only?: boolean;
  production_consumer?: boolean;
  data_source?: string;
  source_path?: string;
  loaded_record_count?: number;
  total_loaded_count?: number;
  total_affixes?: number;
  total_modifiers?: number | null;
  warning_count?: number;
  warnings?: string[];
  export_policy?: string;
  export_status?: string;
  total_affix_records_seen?: number;
  excluded_affix_records?: number;
  sample_count?: number;
  sample_records?: CanonicalAffix[];
  result_count?: number;
  records?: CanonicalAffix[];
  summary?: Record<string, unknown>;
  message?: string;
}

const DEFAULT_LIMIT = 10;

function buildDebugUrl(limit: number, affixId: string, includeModifiers: boolean): string {
  const params = new URLSearchParams();
  params.set("limit", String(limit));
  if (includeModifiers) params.set("include_modifiers", "true");
  if (affixId.trim()) params.set("affix_id", affixId.trim());
  return `/experimental/v2/affixes?${params.toString()}`;
}

async function fetchForgeSafeAffixes(
  limit: number,
  affixId: string,
  includeModifiers: boolean,
): Promise<V2AffixDebugResponse> {
  const res = await fetch(buildDebugUrl(limit, affixId, includeModifiers));
  const json = await res.json().catch(() => null);
  if (!json || typeof json !== "object") {
    return {
      success: false,
      error: "invalid_response",
      message: `Backend returned an unreadable response (${res.status}).`,
    };
  }
  return json as V2AffixDebugResponse;
}

export default function ForgeSafeAffixesDebugPage() {
  const [limit, setLimit] = useState(DEFAULT_LIMIT);
  const [includeModifiers, setIncludeModifiers] = useState(false);
  const [affixIdInput, setAffixIdInput] = useState("");
  const [activeAffixId, setActiveAffixId] = useState("");
  const [data, setData] = useState<V2AffixDebugResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async (
    nextLimit = limit,
    nextAffixId = activeAffixId,
    nextIncludeModifiers = includeModifiers,
  ) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchForgeSafeAffixes(nextLimit, nextAffixId, nextIncludeModifiers);
      setData(response);
      if (!response.success) {
        setError(getV2ErrorMessage(response));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(DEFAULT_LIMIT, "");
    // Initial debug fetch only for this dev-only route.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setActiveAffixId(affixIdInput);
    load(limit, affixIdInput, includeModifiers);
  }

  const records = getV2Records(data);
  const responseSummary = getV2Summary(data);
  const summary = useMemo(
    () => [
      ["Data source", data?.data_source ?? "n/a"],
      ["Loaded affixes", data?.total_affixes ?? data?.total_loaded_count ?? data?.loaded_record_count ?? "n/a"],
      ["Loaded modifiers", data?.total_modifiers ?? "n/a"],
      ["Warnings", data?.warning_count ?? "n/a"],
      ["Export policy", data?.export_policy ?? "n/a"],
      ["Export status", data?.export_status ?? "n/a"],
      ["Support", summarizeV2Support(data)],
      ["Domains", summarizeMap(responseSummary, "affix_domain_counts")],
      ["Debug only", String((data?.debug_only ?? data?.experimental) ?? false)],
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
          Forge-safe affix catalog inspection
        </h1>
          <p className="mt-2 max-w-3xl text-sm text-gray-400">
          This page reads the v2 canonical affix bundle for diagnostics and does not power planner behavior.
        </p>
      </header>

      <section className="rounded border border-[#2a3050] bg-[#10152a] p-4">
        <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-4">
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
            <span className="text-xs uppercase text-gray-500">Affix ID</span>
            <input
              value={affixIdInput}
              onChange={(event) => setAffixIdInput(event.target.value)}
              placeholder="optional"
              className="w-44 rounded border border-[#2a3050] bg-[#0f172a] px-3 py-2 text-gray-100"
            />
          </label>
          <label className="flex items-center gap-2 pb-2 text-sm text-gray-300">
            <input
              type="checkbox"
              checked={includeModifiers}
              onChange={(event) => setIncludeModifiers(event.target.checked)}
              className="h-4 w-4 rounded border border-[#2a3050] bg-[#0f172a]"
            />
            Include modifier detail
          </label>
          <button
            type="submit"
            className="rounded bg-[#f5a623] px-4 py-2 text-sm font-semibold text-[#10152a] hover:bg-[#f5a623cc]"
          >
            Load debug data
          </button>
          <button
            type="button"
            onClick={() => {
              setAffixIdInput("");
              setActiveAffixId("");
              load(limit, "", includeModifiers);
            }}
            className="rounded border border-[#2a3050] px-4 py-2 text-sm text-gray-300 hover:border-gray-500"
          >
            Clear lookup
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
          <p className="mt-2 text-xs text-red-200/80">
            Generate the v2 affix bundle or configure V2_AFFIX_BUNDLE_PATH before using this page.
          </p>
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
            <p className="mt-2 break-all font-mono text-xs text-gray-400">{getV2SourcePath(data)}</p>
          </section>

          <V2EnvelopePanels response={data} />

          <section className="rounded border border-[#2a3050] bg-[#10152a] p-4">
            <h2 className="text-sm font-semibold text-gray-100">Warnings</h2>
            {data.warnings?.length ? (
              <ul className="mt-3 space-y-2 text-sm text-yellow-200">
                {data.warnings.map((warning) => (
                  <li key={warning}>- {warning}</li>
                ))}
              </ul>
            ) : (
              <p className="mt-2 text-sm text-gray-400">No loader warnings.</p>
            )}
          </section>

          <section className="overflow-hidden rounded border border-[#2a3050] bg-[#10152a]">
            <div className="border-b border-[#2a3050] p-4">
              <h2 className="text-sm font-semibold text-gray-100">Sample records</h2>
              <p className="mt-1 text-xs text-gray-500">
                Showing {records.length} records returned by the experimental endpoint.
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[760px] text-left text-sm">
                <thead className="bg-[#0f172a] text-xs uppercase text-gray-500">
                  <tr>
                    <th className="px-4 py-3">Canonical ID</th>
                    <th className="px-4 py-3">Name</th>
                    <th className="px-4 py-3">Support</th>
                    <th className="px-4 py-3">Trust</th>
                    <th className="px-4 py-3">Source</th>
                    <th className="px-4 py-3">Domain</th>
                    <th className="px-4 py-3">Slots</th>
                    <th className="px-4 py-3">Modifiers</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#2a3050]">
                  {records.map((record) => (
                    <tr key={record.canonical_id}>
                      <td className="px-4 py-3 font-mono text-[#f5a623]">{record.canonical_id}</td>
                      <td className="px-4 py-3 text-gray-100">{record.display_name}</td>
                      <td className="px-4 py-3">{statusBadge(record.support_status)}</td>
                      <td className="px-4 py-3 text-gray-300">{record.trust_level}</td>
                      <td className="px-4 py-3 text-gray-300">{record.source_type ?? "n/a"}</td>
                      <td className="px-4 py-3 text-gray-300">{record.affix_domain}</td>
                      <td className="px-4 py-3 text-gray-400">
                        {(record.slot_restrictions ?? []).join(", ") || "none"}
                      </td>
                      <td className="px-4 py-3 font-mono text-gray-300">
                        {record.modifier_reference_count ?? record.modifier_references?.length ?? "n/a"}
                      </td>
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
  return (
    <span className={`inline-flex rounded border px-2 py-1 font-mono text-xs ${classes}`}>
      {status}
    </span>
  );
}
