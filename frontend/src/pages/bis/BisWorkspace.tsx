/**
 * UI11 — BIS Search Workspace
 *
 * Route: /bis-workspace
 *
 * Unified workspace version of BisSearchPage with accordion config panel
 * and tabbed results area.
 */

import { useState, useCallback } from "react";
import { Panel, Button, Spinner } from "@/components/ui";

import SlotSelector       from "@/components/bis/SlotSelector";
import AffixTargetPanel   from "@/components/bis/AffixTargetPanel";
import WeightConfigPanel  from "@/components/bis/WeightConfigPanel";
import SearchControls     from "@/components/bis/SearchControls";
import BisResultsTable    from "@/components/bis/BisResultsTable";
import ComparisonViewer   from "@/components/bis/ComparisonViewer";
import SearchVisualization from "@/components/bis/SearchVisualization";

import type {
  SlotConfig,
  AffixTarget,
  WeightConfig,
  BisSearchResult,
  BisSearchResponse,
} from "./BisSearchPage";

// ---------------------------------------------------------------------------
// Defaults (mirrored from BisSearchPage)
// ---------------------------------------------------------------------------

const ALL_SLOT_TYPES = [
  "helm","chest","gloves","boots","belt",
  "ring1","ring2","amulet","weapon1","weapon2","offhand",
];

const DEFAULT_SLOTS: SlotConfig[] = ALL_SLOT_TYPES.map((s) => ({ slot_type: s, enabled: true }));
const DEFAULT_WEIGHTS: WeightConfig = { tier: 0.4, coverage: 0.3, fp: 0.15, feasibility: 0.15 };

function generateMockResults(count = 20): BisSearchResult[] {
  const scores = Array.from({ length: count }, () => 0.4 + Math.random() * 0.55);
  scores.sort((a, b) => b - a);
  return scores.map((score, i) => ({
    rank:       i + 1,
    build_id:   `build-${Math.random().toString(36).slice(2, 10).toUpperCase()}`,
    score:      +score.toFixed(4),
    percentile: Math.round(((count - (i + 1)) / count) * 100),
    slot:       null,
    item_name:  null,
    affixes:    [],
  }));
}

// ---------------------------------------------------------------------------
// Accordion
// ---------------------------------------------------------------------------

function Accordion({
  title,
  summary,
  children,
  defaultOpen = false,
}: {
  title: string;
  summary: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="rounded border border-forge-border bg-forge-surface overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-3 bg-forge-surface2 hover:bg-forge-surface3 transition-colors"
      >
        <span className="font-mono text-xs uppercase tracking-widest text-forge-cyan">
          {title}
        </span>
        <div className="flex items-center gap-3">
          {!open && (
            <span className="font-body text-xs text-forge-dim truncate max-w-[140px]">
              {summary}
            </span>
          )}
          <span className="font-mono text-forge-dim text-sm leading-none">
            {open ? "▲" : "▼"}
          </span>
        </div>
      </button>
      {open && <div className="p-4">{children}</div>}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Results tabs
// ---------------------------------------------------------------------------

type ResultTab = "results" | "comparison" | "visualization";

const RESULT_TAB_LABELS: { id: ResultTab; label: string }[] = [
  { id: "results",       label: "Results Table" },
  { id: "comparison",    label: "Comparison" },
  { id: "visualization", label: "Visualization" },
];

// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------

export default function BisWorkspace() {
  const [slots,          setSlots]          = useState<SlotConfig[]>(DEFAULT_SLOTS);
  const [targetAffixes,  setTargetAffixes]  = useState<AffixTarget[]>([]);
  const [weights,        setWeights]        = useState<WeightConfig>(DEFAULT_WEIGHTS);
  const [maxCandidates,  setMaxCandidates]  = useState(200);
  const [isSearching,    setIsSearching]    = useState(false);
  const [result,         setResult]         = useState<BisSearchResponse | null>(null);
  const [selectedResult, setSelectedResult] = useState<BisSearchResult | null>(null);
  const [activeTab,      setActiveTab]      = useState<ResultTab>("results");

  const runSearch = useCallback(() => {
    setIsSearching(true);
    setSelectedResult(null);
    setTimeout(() => {
      const results   = generateMockResults(20);
      const bestScore = results[0]?.score ?? 0;
      setResult({
        search_id:       `srch-${Date.now()}`,
        total_evaluated: maxCandidates,
        best_score:      bestScore,
        duration_s:      +(maxCandidates / 200).toFixed(2),
        results,
      });
      setIsSearching(false);
    }, 800);
  }, [maxCandidates]);

  const allResults = result?.results ?? [];

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* Workspace header */}
      <div className="mb-6">
        <h1 className="font-display text-2xl font-bold text-forge-amber">
          BIS Search Workspace
        </h1>
        <p className="mt-1 font-body text-sm text-forge-muted">
          Find optimal gear combinations for your build
        </p>
      </div>

      {/* Summary bar */}
      {result && !isSearching && (
        <div className="mb-4 flex flex-wrap gap-6 rounded border border-forge-border bg-forge-surface px-6 py-3 font-body text-sm">
          <div>
            <span className="text-forge-muted">Evaluated: </span>
            <span className="font-semibold text-forge-text">{result.total_evaluated}</span>
          </div>
          <div>
            <span className="text-forge-muted">Best Score: </span>
            <span className="font-semibold text-forge-green">{(result.best_score * 100).toFixed(1)}%</span>
          </div>
          <div>
            <span className="text-forge-muted">Duration: </span>
            <span className="font-semibold text-forge-text">{result.duration_s}s</span>
          </div>
          <div>
            <span className="text-forge-muted">Search ID: </span>
            <span className="font-mono text-xs text-forge-cyan">{result.search_id}</span>
          </div>
        </div>
      )}

      {/* Two-column layout */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[320px_1fr]">

        {/* Left: Configuration panel with accordions */}
        <div className="flex flex-col gap-3">
          <Accordion
            title="Slot Selection"
            summary={`${slots.filter((s) => s.enabled).length} / ${slots.length} enabled`}
            defaultOpen
          >
            <SlotSelector slots={slots} onChange={setSlots} />
          </Accordion>

          <Accordion
            title="Affix Targets"
            summary={
              targetAffixes.length > 0
                ? `${targetAffixes.length} target${targetAffixes.length === 1 ? "" : "s"}`
                : "None configured"
            }
          >
            <AffixTargetPanel affixes={targetAffixes} onChange={setTargetAffixes} />
          </Accordion>

          <Accordion
            title="Weight Config"
            summary={`Tier ${weights.tier} · Cov ${weights.coverage} · FP ${weights.fp}`}
          >
            <WeightConfigPanel weights={weights} onChange={setWeights} />
          </Accordion>
        </div>

        {/* Right: Results area with tabs */}
        <div className="flex flex-col gap-4">
          {/* Tab bar */}
          <div className="flex gap-1 border-b border-forge-border">
            {RESULT_TAB_LABELS.map(({ id, label }) => (
              <button
                key={id}
                type="button"
                onClick={() => setActiveTab(id)}
                className={[
                  "px-4 py-2 font-mono text-xs uppercase tracking-widest border-b-2 -mb-px transition-colors",
                  activeTab === id
                    ? "border-forge-amber text-forge-amber"
                    : "border-transparent text-forge-dim hover:text-forge-muted",
                ].join(" ")}
              >
                {label}
              </button>
            ))}
            {isSearching && (
              <div className="ml-auto flex items-center gap-2 px-4 py-2">
                <Spinner size={14} />
                <span className="font-mono text-xs text-forge-cyan">Searching...</span>
              </div>
            )}
          </div>

          {/* Tab content */}
          <div>
            {activeTab === "results" && (
              <BisResultsTable
                results={allResults}
                onSelect={setSelectedResult}
                selectedId={selectedResult?.build_id}
              />
            )}
            {activeTab === "comparison" && (
              <ComparisonViewer selected={selectedResult} allResults={allResults} />
            )}
            {activeTab === "visualization" && (
              <SearchVisualization results={allResults} isSearching={isSearching} />
            )}
          </div>
        </div>
      </div>

      {/* Bottom: Search controls */}
      <div className="mt-6 pt-4 border-t border-forge-border">
        <SearchControls
          onSearch={runSearch}
          isSearching={isSearching}
          disabled={slots.every((s) => !s.enabled)}
          maxCandidates={maxCandidates}
          onMaxCandidatesChange={setMaxCandidates}
        />
      </div>
    </div>
  );
}
