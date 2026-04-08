/**
 * BackendDebugDashboard — minimal debug frontend for backend validation.
 *
 * Calls every API endpoint and displays raw JSON results with counts,
 * field schemas, and error visibility. No complex UI — just data truth.
 */

import { useState, useEffect, useCallback } from "react";

interface EndpointResult {
  endpoint: string;
  method: string;
  status: number | null;
  count: number | string;
  fields: string[];
  error: string | null;
  raw: unknown;
  durationMs: number;
}

const GET_ENDPOINTS = [
  "/api/ref/affixes",
  "/api/ref/affixes?type=prefix",
  "/api/ref/affixes?type=suffix",
  "/api/ref/base-items",
  "/api/ref/classes",
  "/api/ref/item-types",
  "/api/ref/skills",
  "/api/ref/crafting-rules",
  "/api/ref/fp-ranges",
  "/api/ref/enemy-profiles",
  "/api/ref/damage-types",
  "/api/ref/rarities",
  "/api/ref/implicit-stats",
  "/api/ref/uniques",
  "/api/passives/Acolyte",
  "/api/passives/Acolyte/Lich",
  "/api/passives/Mage",
  "/api/passives/Primalist",
  "/api/passives/Sentinel",
  "/api/passives/Rogue",
  "/api/builds",
  "/api/version",
];

const BASE = import.meta.env.VITE_API_URL ?? "/api";

function resolveUrl(ep: string): string {
  // If endpoint starts with /api/, replace with BASE
  if (ep.startsWith("/api/")) {
    return BASE + ep.slice(4);
  }
  return ep;
}

async function testEndpoint(endpoint: string, method = "GET", body?: unknown): Promise<EndpointResult> {
  const start = performance.now();
  try {
    const res = await fetch(resolveUrl(endpoint), {
      method,
      headers: body ? { "Content-Type": "application/json" } : {},
      body: body ? JSON.stringify(body) : undefined,
    });
    const durationMs = Math.round(performance.now() - start);
    const json = await res.json().catch(() => null);

    let count: number | string = 0;
    let fields: string[] = [];

    if (json) {
      const payload = json.data ?? json;
      if (Array.isArray(payload)) {
        count = payload.length;
        if (payload[0]) fields = Object.keys(payload[0]);
      } else if (payload && typeof payload === "object") {
        if ("nodes" in payload && Array.isArray(payload.nodes)) {
          count = payload.nodes.length;
          if (payload.nodes[0]) fields = Object.keys(payload.nodes[0]);
        } else {
          count = Object.keys(payload).length;
          fields = Object.keys(payload);
        }
      }
    }

    const errors = json?.errors;
    return {
      endpoint,
      method,
      status: res.status,
      count,
      fields,
      error: errors ? JSON.stringify(errors) : null,
      raw: json,
      durationMs,
    };
  } catch (e) {
    return {
      endpoint,
      method,
      status: null,
      count: 0,
      fields: [],
      error: e instanceof Error ? e.message : String(e),
      raw: null,
      durationMs: Math.round(performance.now() - start),
    };
  }
}

function StatusBadge({ status }: { status: number | null }) {
  if (!status) return <span style={{ color: "#ef4444" }}>ERR</span>;
  const color = status < 300 ? "#22c55e" : status < 400 ? "#f59e0b" : "#ef4444";
  return <span style={{ color, fontWeight: "bold" }}>{status}</span>;
}

function EndpointRow({ result, onExpand }: { result: EndpointResult; onExpand: () => void }) {
  return (
    <tr
      onClick={onExpand}
      style={{ cursor: "pointer", borderBottom: "1px solid #1e293b" }}
    >
      <td style={{ padding: "6px 12px", fontFamily: "monospace", fontSize: 11, color: "#94a3b8" }}>
        {result.method}
      </td>
      <td style={{ padding: "6px 12px", fontFamily: "monospace", fontSize: 12, color: "#e2e8f0" }}>
        {result.endpoint}
      </td>
      <td style={{ padding: "6px 12px", textAlign: "center" }}>
        <StatusBadge status={result.status} />
      </td>
      <td style={{ padding: "6px 12px", fontFamily: "monospace", fontSize: 12, color: "#f59e0b", textAlign: "right" }}>
        {result.count}
      </td>
      <td style={{ padding: "6px 12px", fontFamily: "monospace", fontSize: 10, color: "#64748b", maxWidth: 300, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
        {result.fields.join(", ")}
      </td>
      <td style={{ padding: "6px 12px", fontFamily: "monospace", fontSize: 11, color: "#64748b", textAlign: "right" }}>
        {result.durationMs}ms
      </td>
      <td style={{ padding: "6px 12px", fontSize: 11, color: "#ef4444" }}>
        {result.error ?? ""}
      </td>
    </tr>
  );
}

export default function BackendDebugDashboard() {
  const [results, setResults] = useState<EndpointResult[]>([]);
  const [running, setRunning] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  const runAll = useCallback(async () => {
    setRunning(true);
    setResults([]);
    setExpanded(null);

    const all: EndpointResult[] = [];
    for (const ep of GET_ENDPOINTS) {
      const r = await testEndpoint(ep);
      all.push(r);
      setResults([...all]);
    }

    // POST tests
    const posts: [string, unknown][] = [
      ["/api/craft/predict", { forge_potential: 28, affixes: [], n_simulations: 100 }],
      ["/api/simulate/encounter", {
        base_damage: 500, fight_duration: 10, tick_size: 0.1,
        enemy_template: "STANDARD_BOSS", distribution: "SINGLE",
        crit_chance: 0.05, crit_multiplier: 2.0,
      }],
    ];
    for (const [ep, body] of posts) {
      const r = await testEndpoint(ep, "POST", body);
      all.push(r);
      setResults([...all]);
    }

    setRunning(false);
  }, []);

  useEffect(() => { runAll(); }, []);

  const passed = results.filter((r) => r.status === 200 && !r.error).length;
  const failed = results.filter((r) => r.status !== 200 || r.error).length;
  const total = results.length;

  return (
    <div style={{ background: "#0f172a", color: "#e2e8f0", minHeight: "100vh", padding: 24, fontFamily: "system-ui, sans-serif" }}>
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        <h1 style={{ fontSize: 24, fontWeight: "bold", color: "#f59e0b", marginBottom: 4 }}>
          Backend Debug Dashboard
        </h1>
        <p style={{ fontSize: 13, color: "#64748b", marginBottom: 16 }}>
          Raw API endpoint validation — no frontend abstractions
        </p>

        {/* Summary bar */}
        <div style={{ display: "flex", gap: 24, marginBottom: 16, fontSize: 14 }}>
          <span>
            Total: <strong>{total}</strong>
          </span>
          <span style={{ color: "#22c55e" }}>
            Passed: <strong>{passed}</strong>
          </span>
          <span style={{ color: "#ef4444" }}>
            Failed: <strong>{failed}</strong>
          </span>
          <span style={{ color: "#64748b" }}>
            {running ? "Running..." : "Complete"}
          </span>
          <button
            onClick={runAll}
            disabled={running}
            style={{
              marginLeft: "auto", padding: "4px 16px", fontSize: 12,
              background: running ? "#1e293b" : "#f59e0b", color: "#0f172a",
              border: "none", borderRadius: 4, cursor: running ? "not-allowed" : "pointer",
              fontWeight: "bold",
            }}
          >
            {running ? "Running..." : "Re-run All"}
          </button>
        </div>

        {/* Results table */}
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ borderBottom: "2px solid #1e293b", textAlign: "left" }}>
              <th style={{ padding: "8px 12px", color: "#64748b", fontSize: 11, textTransform: "uppercase" }}>Method</th>
              <th style={{ padding: "8px 12px", color: "#64748b", fontSize: 11, textTransform: "uppercase" }}>Endpoint</th>
              <th style={{ padding: "8px 12px", color: "#64748b", fontSize: 11, textTransform: "uppercase", textAlign: "center" }}>Status</th>
              <th style={{ padding: "8px 12px", color: "#64748b", fontSize: 11, textTransform: "uppercase", textAlign: "right" }}>Count</th>
              <th style={{ padding: "8px 12px", color: "#64748b", fontSize: 11, textTransform: "uppercase" }}>Fields</th>
              <th style={{ padding: "8px 12px", color: "#64748b", fontSize: 11, textTransform: "uppercase", textAlign: "right" }}>Time</th>
              <th style={{ padding: "8px 12px", color: "#64748b", fontSize: 11, textTransform: "uppercase" }}>Error</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r) => (
              <EndpointRow
                key={`${r.method}-${r.endpoint}`}
                result={r}
                onExpand={() => setExpanded(expanded === r.endpoint ? null : r.endpoint)}
              />
            ))}
          </tbody>
        </table>

        {/* Expanded raw JSON */}
        {expanded && (() => {
          const r = results.find((x) => x.endpoint === expanded);
          if (!r) return null;
          return (
            <div style={{ marginTop: 16, padding: 16, background: "#1e293b", borderRadius: 8, overflow: "auto", maxHeight: 500 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                <span style={{ fontFamily: "monospace", fontSize: 13, color: "#f59e0b" }}>
                  {r.method} {r.endpoint}
                </span>
                <button
                  onClick={() => setExpanded(null)}
                  style={{ background: "none", border: "none", color: "#64748b", cursor: "pointer", fontSize: 14 }}
                >
                  Close
                </button>
              </div>
              <pre style={{ fontFamily: "monospace", fontSize: 11, color: "#94a3b8", whiteSpace: "pre-wrap", wordBreak: "break-all" }}>
                {JSON.stringify(r.raw, null, 2)}
              </pre>
            </div>
          );
        })()}
      </div>
    </div>
  );
}
