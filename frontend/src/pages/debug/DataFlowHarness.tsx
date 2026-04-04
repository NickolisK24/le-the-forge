/**
 * DataFlowHarness — verifies frontend-backend data flow for every dataset.
 *
 * Calls each API endpoint and displays raw counts. No styling, no
 * transformation — just proof that data flows end-to-end.
 */

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";

interface DatasetResult {
  name: string;
  endpoint: string;
  count: number | null;
  error: string | null;
  loading: boolean;
}

const DATASETS: { name: string; endpoint: string; countFn: (data: unknown) => number }[] = [
  {
    name: "Passives (Acolyte)",
    endpoint: "/passives/Acolyte",
    countFn: (d: any) => d?.nodes?.length ?? 0,
  },
  {
    name: "Passives (All)",
    endpoint: "/passives",
    countFn: (d: any) => d?.nodes?.length ?? 0,
  },
  {
    name: "Affixes",
    endpoint: "/ref/affixes",
    countFn: (d: any) => (Array.isArray(d) ? d.length : 0),
  },
  {
    name: "Affixes (helmet slot)",
    endpoint: "/ref/affixes?slot=helmet",
    countFn: (d: any) => (Array.isArray(d) ? d.length : 0),
  },
  {
    name: "Base Items",
    endpoint: "/ref/base-items",
    countFn: (d: any) =>
      typeof d === "object" && d !== null
        ? Object.values(d).reduce((sum: number, arr: any) => sum + (Array.isArray(arr) ? arr.length : 0), 0)
        : 0,
  },
  {
    name: "Item Types",
    endpoint: "/ref/item-types",
    countFn: (d: any) => (Array.isArray(d) ? d.length : 0),
  },
  {
    name: "Classes",
    endpoint: "/ref/classes",
    countFn: (d: any) => (typeof d === "object" && d !== null ? Object.keys(d).length : 0),
  },
  {
    name: "Skills",
    endpoint: "/ref/skills",
    countFn: (d: any) => (typeof d === "object" && d !== null ? Object.keys(d).length : 0),
  },
  {
    name: "Enemy Profiles",
    endpoint: "/ref/enemy-profiles",
    countFn: (d: any) => (Array.isArray(d) ? d.length : 0),
  },
  {
    name: "Uniques",
    endpoint: "/ref/uniques",
    countFn: (d: any) => (Array.isArray(d) ? d.length : 0),
  },
  {
    name: "Rarities",
    endpoint: "/ref/rarities",
    countFn: (d: any) => (Array.isArray(d) ? d.length : 0),
  },
  {
    name: "Damage Types",
    endpoint: "/ref/damage-types",
    countFn: (d: any) => (Array.isArray(d) ? d.length : 0),
  },
  {
    name: "Builds",
    endpoint: "/builds",
    countFn: (d: any) => (Array.isArray(d) ? d.length : 0),
  },
];

export default function DataFlowHarness() {
  const [results, setResults] = useState<DatasetResult[]>(
    DATASETS.map((d) => ({ name: d.name, endpoint: d.endpoint, count: null, error: null, loading: true })),
  );

  useEffect(() => {
    DATASETS.forEach(async (ds, idx) => {
      try {
        const res = await apiGet<unknown>(ds.endpoint);
        const count = res.data !== null ? ds.countFn(res.data) : 0;
        const error = res.errors ? res.errors[0]?.message ?? "Unknown error" : null;
        setResults((prev) => {
          const next = [...prev];
          next[idx] = { ...next[idx], count: error ? null : count, error, loading: false };
          return next;
        });
      } catch (e) {
        setResults((prev) => {
          const next = [...prev];
          next[idx] = { ...next[idx], error: e instanceof Error ? e.message : String(e), loading: false };
          return next;
        });
      }
    });
  }, []);

  const allDone = results.every((r) => !r.loading);
  const allOk = results.every((r) => !r.loading && !r.error && (r.count ?? 0) > 0);

  return (
    <div style={{ padding: 24, fontFamily: "monospace", background: "#0f172a", color: "#e2e8f0", minHeight: "100vh" }}>
      <h1 style={{ fontSize: 20, color: "#f59e0b", marginBottom: 16 }}>Data Flow Test Harness</h1>
      <p style={{ fontSize: 12, color: "#64748b", marginBottom: 16 }}>
        Verifies that every dataset loads from the backend API. No UI rendering — raw counts only.
      </p>

      <div style={{ display: "flex", gap: 16, marginBottom: 16, fontSize: 13 }}>
        <span>Status: {allDone ? (allOk ? "ALL PASS" : "ISSUES DETECTED") : "Loading..."}</span>
      </div>

      <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 13 }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #1e293b" }}>
            <th style={{ textAlign: "left", padding: "6px 12px", color: "#64748b" }}>Dataset</th>
            <th style={{ textAlign: "left", padding: "6px 12px", color: "#64748b" }}>Endpoint</th>
            <th style={{ textAlign: "right", padding: "6px 12px", color: "#64748b" }}>Count</th>
            <th style={{ textAlign: "left", padding: "6px 12px", color: "#64748b" }}>Status</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r) => (
            <tr key={r.endpoint} style={{ borderBottom: "1px solid #1e293b" }}>
              <td style={{ padding: "6px 12px" }}>{r.name}</td>
              <td style={{ padding: "6px 12px", color: "#94a3b8" }}>{r.endpoint}</td>
              <td style={{ padding: "6px 12px", textAlign: "right", color: "#f59e0b", fontWeight: "bold" }}>
                {r.loading ? "..." : r.count ?? "—"}
              </td>
              <td style={{ padding: "6px 12px" }}>
                {r.loading ? (
                  <span style={{ color: "#64748b" }}>Loading</span>
                ) : r.error ? (
                  <span style={{ color: "#ef4444" }}>FAIL: {r.error}</span>
                ) : (r.count ?? 0) > 0 ? (
                  <span style={{ color: "#22c55e" }}>OK</span>
                ) : (
                  <span style={{ color: "#f59e0b" }}>EMPTY</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
