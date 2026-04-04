/**
 * Q26 — BisResultsTable
 *
 * Sortable, paginated table of BIS search results.
 * Score colour-coded: green ≥80 %, yellow ≥60 %, red <60 %.
 */

import { useState } from "react";
import type { BisSearchResult } from "@/pages/bis/BisSearchPage";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const PAGE_SIZE = 10;

type SortKey = "rank" | "score";
type SortDir = "asc" | "desc";

function scoreColor(score: number): string {
  const pct = score * 100;
  if (pct >= 80) return "text-green-400";
  if (pct >= 60) return "text-yellow-400";
  return "text-red-400";
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface Props {
  results: BisSearchResult[];
  onSelect?: (r: BisSearchResult) => void;
  selectedId?: string;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function BisResultsTable({ results, onSelect, selectedId }: Props) {
  const [sortKey, setSortKey]   = useState<SortKey>("rank");
  const [sortDir, setSortDir]   = useState<SortDir>("asc");
  const [page,    setPage]      = useState(0);

  if (results.length === 0) {
    return (
      <div className="rounded-lg border border-forge-border bg-forge-surface p-6 text-center">
        <p className="text-sm text-forge-muted">No results yet</p>
      </div>
    );
  }

  function toggleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
    setPage(0);
  }

  const sorted = [...results].sort((a, b) => {
    const aVal = a[sortKey];
    const bVal = b[sortKey];
    return sortDir === "asc" ? aVal - bVal : bVal - aVal;
  });

  const totalPages = Math.ceil(sorted.length / PAGE_SIZE);
  const pageItems  = sorted.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  function SortIcon({ k }: { k: SortKey }) {
    if (sortKey !== k) return <span className="text-forge-muted ml-1">↕</span>;
    return <span className="text-[#f5a623] ml-1">{sortDir === "asc" ? "↑" : "↓"}</span>;
  }

  return (
    <div className="rounded-lg border border-forge-border bg-forge-surface">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-forge-border">
              <th
                className="cursor-pointer px-4 py-2 text-left text-xs uppercase tracking-wider text-forge-muted
                  hover:text-forge-text select-none"
                onClick={() => toggleSort("rank")}
              >
                Rank <SortIcon k="rank" />
              </th>
              <th className="px-4 py-2 text-left text-xs uppercase tracking-wider text-forge-muted">
                Build ID
              </th>
              <th
                className="cursor-pointer px-4 py-2 text-left text-xs uppercase tracking-wider text-forge-muted
                  hover:text-forge-text select-none"
                onClick={() => toggleSort("score")}
              >
                Score <SortIcon k="score" />
              </th>
              <th className="px-4 py-2 text-left text-xs uppercase tracking-wider text-forge-muted">
                Percentile
              </th>
            </tr>
          </thead>
          <tbody>
            {pageItems.map((r) => {
              const isSelected = r.build_id === selectedId;
              return (
                <tr
                  key={r.build_id}
                  onClick={() => onSelect?.(r)}
                  className={`cursor-pointer border-b border-forge-border/40 transition-colors
                    ${isSelected
                      ? "border-l-2 border-l-[#f5a623] bg-[#1e2840]"
                      : "hover:bg-[#161c30]"
                    }`}
                >
                  <td className="px-4 py-2 text-forge-muted font-mono">#{r.rank}</td>
                  <td className="px-4 py-2 font-mono text-[#22d3ee] text-xs">{r.build_id}</td>
                  <td className={`px-4 py-2 font-semibold tabular-nums ${scoreColor(r.score)}`}>
                    {(r.score * 100).toFixed(1)}%
                  </td>
                  <td className="px-4 py-2 text-forge-muted">
                    P{r.percentile}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-forge-border px-4 py-2">
          <span className="text-xs text-forge-muted">
            Page {page + 1} of {totalPages} ({results.length} results)
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="rounded px-2 py-1 text-xs text-forge-muted hover:text-forge-text
                disabled:opacity-40 disabled:cursor-not-allowed"
            >
              ← Prev
            </button>
            {Array.from({ length: totalPages }, (_, i) => (
              <button
                key={i}
                onClick={() => setPage(i)}
                className={`rounded px-2 py-1 text-xs transition-colors
                  ${i === page
                    ? "bg-[#f5a623] text-[#10152a] font-semibold"
                    : "text-forge-muted hover:text-forge-text"
                  }`}
              >
                {i + 1}
              </button>
            ))}
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page === totalPages - 1}
              className="rounded px-2 py-1 text-xs text-forge-muted hover:text-forge-text
                disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
