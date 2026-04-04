/**
 * N17 — Report Exporter
 *
 * Provides JSON export, CSV export (first section), and clipboard copy.
 */

import { useState } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ReportSection {
  title: string;
  data: Record<string, unknown>[];
  summary?: Record<string, unknown>;
}

export interface ReportExporterProps {
  title: string;
  sections: ReportSection[];
  onExport?: (format: string, content: string) => void;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function toJson(title: string, sections: ReportSection[]): string {
  return JSON.stringify({ title, sections }, null, 2);
}

function toCsv(sections: ReportSection[]): string {
  if (sections.length === 0) return "";
  const rows = sections[0].data;
  if (rows.length === 0) return "";
  const headers = Object.keys(rows[0]);
  const lines = [
    headers.join(","),
    ...rows.map((row) =>
      headers
        .map((h) => {
          const v = row[h];
          const s = v === null || v === undefined ? "" : String(v);
          // Wrap in quotes if the value contains commas, quotes, or newlines
          return /[,"\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
        })
        .join(",")
    ),
  ];
  return lines.join("\n");
}

function downloadFile(filename: string, content: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

const btnCls =
  "px-4 py-1.5 rounded border border-[#f5a623]/60 bg-[#0d1124] font-mono text-xs text-[#f5a623] " +
  "hover:bg-[#f5a623]/10 transition-colors";

export default function ReportExporter({ title, sections, onExport }: ReportExporterProps) {
  const [copied, setCopied] = useState(false);

  function handleExportJson() {
    const content = toJson(title, sections);
    downloadFile(`${title.replace(/\s+/g, "_")}.json`, content, "application/json");
    onExport?.("json", content);
  }

  function handleExportCsv() {
    const content = toCsv(sections);
    downloadFile(`${title.replace(/\s+/g, "_")}.csv`, content, "text/csv");
    onExport?.("csv", content);
  }

  async function handleCopy() {
    const content = toJson(title, sections);
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      onExport?.("clipboard", content);
    } catch {
      // clipboard API may be unavailable in some contexts
    }
  }

  return (
    <div className="rounded border border-[#2a3050] bg-[#10152a] p-4">
      <p className="font-mono text-[11px] uppercase tracking-widest text-[#6b7280] mb-3">
        Export Report
      </p>
      <div className="flex items-center gap-3 flex-wrap">
        <button onClick={handleExportJson} className={btnCls}>
          Export JSON
        </button>
        <button onClick={handleExportCsv} className={btnCls}>
          Export CSV
        </button>
        <button onClick={handleCopy} className={btnCls}>
          {copied ? (
            <span className="text-green-400">Copied!</span>
          ) : (
            "Copy to Clipboard"
          )}
        </button>
      </div>
    </div>
  );
}
