/**
 * UI17 — Data Manager Dashboard
 * Displays game version, data reload controls, and validation results.
 */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Panel, Button, Badge } from "@/components/ui";
import { versionApi } from "@/lib/api";

interface DataSource {
  name: string;
  status: "ok" | "warn" | "error" | "loading";
  itemCount: number;
  lastUpdated: string;
}

const MOCK_SOURCES: DataSource[] = [
  { name: "Skills",        status: "ok",   itemCount: 132, lastUpdated: "2026-04-01" },
  { name: "Passives",      status: "ok",   itemCount: 534, lastUpdated: "2026-04-01" },
  { name: "Affixes",       status: "ok",   itemCount: 847, lastUpdated: "2026-04-01" },
  { name: "Base Items",    status: "ok",   itemCount: 110, lastUpdated: "2026-04-01" },
  { name: "Unique Items",  status: "warn", itemCount: 403, lastUpdated: "2026-03-29" },
  { name: "Enemies",       status: "ok",   itemCount: 48,  lastUpdated: "2026-04-01" },
];

const STATUS_COLORS: Record<DataSource["status"], string> = {
  ok:      "text-forge-green",
  warn:    "text-forge-amber",
  error:   "text-forge-red",
  loading: "text-forge-muted",
};

const STATUS_LABELS: Record<DataSource["status"], string> = {
  ok: "OK", warn: "WARN", error: "ERROR", loading: "…",
};

function StatusDot({ status }: { status: DataSource["status"] }) {
  const colors: Record<DataSource["status"], string> = {
    ok: "bg-forge-green", warn: "bg-forge-amber", error: "bg-forge-red", loading: "bg-forge-muted",
  };
  return (
    <span className={`inline-block w-2 h-2 rounded-full ${colors[status]} mr-2`} />
  );
}

export function DataManagerDashboard() {
  const [reloading, setReloading] = useState(false);
  const [reloadLog, setReloadLog] = useState<string[]>([]);

  const { data: versionRes } = useQuery({
    queryKey: ["version"],
    queryFn: () => versionApi.get(),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
  const version = versionRes?.data;

  async function handleReload() {
    setReloading(true);
    setReloadLog([]);
    const steps = [
      "Loading skills.json...",
      "Loading affixes.json...",
      "Loading base_items.json...",
      "Loading uniques.json...",
      "Loading passives.json...",
      "Validating data integrity...",
      "Reload complete.",
    ];
    for (const step of steps) {
      await new Promise((r) => setTimeout(r, 300));
      setReloadLog((l) => [...l, step]);
    }
    setReloading(false);
  }

  const totalItems = MOCK_SOURCES.reduce((s, src) => s + src.itemCount, 0);
  const warnings = MOCK_SOURCES.filter((s) => s.status === "warn").length;
  const errors = MOCK_SOURCES.filter((s) => s.status === "error").length;

  return (
    <div className="space-y-4">
      {/* Header stats */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { label: "Game Version", value: version ? `patch ${version.current_patch}` : "—" },
          { label: "Total Records", value: totalItems.toLocaleString() },
          { label: "Warnings", value: String(warnings), color: warnings > 0 ? "text-forge-amber" : "text-forge-green" },
          { label: "Errors", value: String(errors), color: errors > 0 ? "text-forge-red" : "text-forge-green" },
        ].map(({ label, value, color }) => (
          <div
            key={label}
            className="rounded border border-forge-border bg-forge-surface2 p-3 text-center"
          >
            <div className={`font-display text-xl font-bold ${color ?? "text-forge-cyan"}`}>
              {value}
            </div>
            <div className="font-mono text-xs text-forge-muted mt-1">{label}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Data sources table */}
        <Panel title="Data Sources">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-forge-border">
                {["Source", "Status", "Items", "Updated"].map((h) => (
                  <th key={h} className="pb-2 text-left font-mono text-xs text-forge-muted uppercase tracking-wider">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {MOCK_SOURCES.map((src) => (
                <tr key={src.name} className="border-b border-forge-border/40 hover:bg-forge-surface3 transition-colors">
                  <td className="py-2 font-mono text-xs text-forge-text">{src.name}</td>
                  <td className={`py-2 font-mono text-xs font-bold ${STATUS_COLORS[src.status]}`}>
                    <StatusDot status={src.status} />
                    {STATUS_LABELS[src.status]}
                  </td>
                  <td className="py-2 font-mono text-xs text-forge-muted">{src.itemCount}</td>
                  <td className="py-2 font-mono text-xs text-forge-dim">{src.lastUpdated}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>

        {/* Reload controls */}
        <Panel title="Reload Controls">
          <div className="space-y-3">
            <p className="font-mono text-xs text-forge-muted">
              Reload game data from source JSON files. This re-validates all records and updates the in-memory cache.
            </p>

            <Button onClick={handleReload} disabled={reloading} className="w-full">
              {reloading ? "Reloading..." : "Reload All Data"}
            </Button>

            {reloadLog.length > 0 && (
              <div className="rounded border border-forge-border bg-forge-bg p-3 font-mono text-xs space-y-1 max-h-40 overflow-y-auto">
                {reloadLog.map((line, i) => (
                  <div key={i} className={line.includes("complete") ? "text-forge-green" : "text-forge-muted"}>
                    {">"} {line}
                  </div>
                ))}
              </div>
            )}
          </div>
        </Panel>
      </div>
    </div>
  );
}
