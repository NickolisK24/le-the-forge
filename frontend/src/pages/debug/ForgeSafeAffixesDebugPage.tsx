import { FormEvent, useEffect, useMemo, useState } from "react";

interface ForgeSafeAffixSample {
  affix_id: number | string;
  name?: string | null;
  source_type?: string | null;
  item_type?: string | null;
  eligible_item_types?: string[];
}

interface ForgeSafeAffixDebugResponse {
  success: boolean;
  debug_only?: boolean;
  read_only?: boolean;
  production_consumer?: boolean;
  source_path?: string;
  loaded_record_count?: number;
  warning_count?: number;
  warnings?: string[];
  export_policy?: string;
  export_status?: string;
  total_affix_records_seen?: number;
  excluded_affix_records?: number;
  sample_count?: number;
  sample_records?: ForgeSafeAffixSample[];
  error?: string;
  message?: string;
}

const DEFAULT_LIMIT = 10;

function buildDebugUrl(limit: number, affixId: string): string {
  const params = new URLSearchParams();
  params.set("limit", String(limit));
  if (affixId.trim()) params.set("affix_id", affixId.trim());
  return `/debug/forge-safe-affixes?${params.toString()}`;
}

async function fetchForgeSafeAffixes(limit: number, affixId: string): Promise<ForgeSafeAffixDebugResponse> {
  const res = await fetch(buildDebugUrl(limit, affixId));
  const json = await res.json().catch(() => null);
  if (!json || typeof json !== "object") {
    return {
      success: false,
      error: "invalid_response",
      message: `Backend returned an unreadable response (${res.status}).`,
    };
  }
  return json as ForgeSafeAffixDebugResponse;
}

export default function ForgeSafeAffixesDebugPage() {
  const [limit, setLimit] = useState(DEFAULT_LIMIT);
  const [affixIdInput, setAffixIdInput] = useState("");
  const [activeAffixId, setActiveAffixId] = useState("");
  const [data, setData] = useState<ForgeSafeAffixDebugResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async (nextLimit = limit, nextAffixId = activeAffixId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchForgeSafeAffixes(nextLimit, nextAffixId);
      setData(response);
      if (!response.success) {
        setError(response.message || response.error || "Debug endpoint returned an error.");
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
    load(limit, affixIdInput);
  }

  const summary = useMemo(
    () => [
      ["Loaded records", data?.loaded_record_count ?? "n/a"],
      ["Warnings", data?.warning_count ?? "n/a"],
      ["Export policy", data?.export_policy ?? "n/a"],
      ["Export status", data?.export_status ?? "n/a"],
      ["Total seen", data?.total_affix_records_seen ?? "n/a"],
      ["Excluded", data?.excluded_affix_records ?? "n/a"],
      ["Debug only", String(data?.debug_only ?? false)],
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
          Forge-safe affix export inspection
        </h1>
        <p className="mt-2 max-w-3xl text-sm text-gray-400">
          This page is debug-only and does not power planner behavior.
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
              load(limit, "");
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
            Enable the backend debug flag and configure the export path before using this page.
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
            <p className="mt-2 break-all font-mono text-xs text-gray-400">{data.source_path}</p>
          </section>

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
                Showing {data.sample_records?.length ?? 0} records returned by the debug endpoint.
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[760px] text-left text-sm">
                <thead className="bg-[#0f172a] text-xs uppercase text-gray-500">
                  <tr>
                    <th className="px-4 py-3">Affix ID</th>
                    <th className="px-4 py-3">Name</th>
                    <th className="px-4 py-3">Source</th>
                    <th className="px-4 py-3">Item Type</th>
                    <th className="px-4 py-3">Eligible Types</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#2a3050]">
                  {(data.sample_records ?? []).map((record) => (
                    <tr key={`${record.source_type}-${record.affix_id}`}>
                      <td className="px-4 py-3 font-mono text-[#f5a623]">{record.affix_id}</td>
                      <td className="px-4 py-3 text-gray-100">{record.name ?? "n/a"}</td>
                      <td className="px-4 py-3 text-gray-300">{record.source_type ?? "n/a"}</td>
                      <td className="px-4 py-3 text-gray-300">{record.item_type ?? "n/a"}</td>
                      <td className="px-4 py-3 text-gray-400">
                        {(record.eligible_item_types ?? []).join(", ") || "none"}
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
