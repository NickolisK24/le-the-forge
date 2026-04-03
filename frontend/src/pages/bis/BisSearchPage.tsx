/**
 * Q21 — BIS Search Page
 *
 * Route: /bis-search
 *
 * Main page composing the BIS search engine UI:
 *   Left panel  — SlotSelector, AffixTargetPanel, WeightConfigPanel, SearchControls
 *   Right panel — BisResultsTable, ComparisonViewer, SearchVisualization
 */

import { useState, useCallback } from "react";

import SlotSelector       from "@/components/bis/SlotSelector";
import AffixTargetPanel   from "@/components/bis/AffixTargetPanel";
import WeightConfigPanel  from "@/components/bis/WeightConfigPanel";
import SearchControls     from "@/components/bis/SearchControls";
import BisResultsTable    from "@/components/bis/BisResultsTable";
import ComparisonViewer   from "@/components/bis/ComparisonViewer";
import SearchVisualization from "@/components/bis/SearchVisualization";

// ---------------------------------------------------------------------------
// Exported types
// ---------------------------------------------------------------------------

export interface SlotConfig {
  slot_type: string;
  enabled:   boolean;
}

export interface AffixTarget {
  affix_id:    string;
  affix_name:  string;
  min_tier:    number;
  target_tier: number;
}

export interface WeightConfig {
  tier:        number;
  coverage:    number;
  fp:          number;
  feasibility: number;
}

export interface BisSearchResult {
  rank:          number;
  build_id:      string;
  score:         number;
  percentile:    number;
  slot_details?: Record<string, { affix_id: string; tier: number }[]>;
}

export interface BisSearchResponse {
  search_id:       string;
  total_evaluated: number;
  best_score:      number;
  duration_s:      number;
  results:         BisSearchResult[];
}

// ---------------------------------------------------------------------------
// Defaults
// ---------------------------------------------------------------------------

const ALL_SLOT_TYPES = [
  "helm","chest","gloves","boots","belt",
  "ring1","ring2","amulet","weapon1","weapon2","offhand",
];

const DEFAULT_SLOTS: SlotConfig[] = ALL_SLOT_TYPES.map((s) => ({ slot_type: s, enabled: true }));

const DEFAULT_WEIGHTS: WeightConfig = { tier: 0.4, coverage: 0.3, fp: 0.15, feasibility: 0.15 };

// ---------------------------------------------------------------------------
// Mock generator
// ---------------------------------------------------------------------------

function generateMockResults(count = 20): BisSearchResult[] {
  const results: BisSearchResult[] = [];
  const scores = Array.from({ length: count }, () => 0.4 + Math.random() * 0.55);
  scores.sort((a, b) => b - a); // highest first

  for (let i = 0; i < count; i++) {
    const rank = i + 1;
    const score = scores[i];
    results.push({
      rank,
      build_id:   `build-${Math.random().toString(36).slice(2, 10).toUpperCase()}`,
      score:      +score.toFixed(4),
      percentile: Math.round(((count - rank) / count) * 100),
    });
  }
  return results;
}

// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------

export default function BisSearchPage() {
  const [slots,           setSlots]           = useState<SlotConfig[]>(DEFAULT_SLOTS);
  const [targetAffixes,   setTargetAffixes]   = useState<AffixTarget[]>([]);
  const [weights,         setWeights]         = useState<WeightConfig>(DEFAULT_WEIGHTS);
  const [maxCandidates,   setMaxCandidates]   = useState(200);
  const [isSearching,     setIsSearching]     = useState(false);
  const [result,          setResult]          = useState<BisSearchResponse | null>(null);
  const [selectedResult,  setSelectedResult]  = useState<BisSearchResult | null>(null);

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
      {/* Page header */}
      <div className="mb-6">
        <h1 className="font-display text-2xl font-bold text-[#f5a623]">BIS Search Engine</h1>
        <p className="mt-1 text-sm text-forge-muted">
          Find the optimal gear combination across all slots by evaluating thousands of
          candidate builds against your target affixes and score weights.
        </p>
      </div>

      {/* Summary bar — only shown when results are available */}
      {result && !isSearching && (
        <div className="mb-4 flex flex-wrap gap-6 rounded-lg border border-forge-border bg-forge-surface px-6 py-3 text-sm">
          <div>
            <span className="text-forge-muted">Evaluated: </span>
            <span className="font-semibold text-forge-text">{result.total_evaluated}</span>
          </div>
          <div>
            <span className="text-forge-muted">Best Score: </span>
            <span className="font-semibold text-green-400">{(result.best_score * 100).toFixed(1)}%</span>
          </div>
          <div>
            <span className="text-forge-muted">Duration: </span>
            <span className="font-semibold text-forge-text">{result.duration_s}s</span>
          </div>
          <div>
            <span className="text-forge-muted">Search ID: </span>
            <span className="font-mono text-xs text-[#22d3ee]">{result.search_id}</span>
          </div>
        </div>
      )}

      {/* Two-column layout */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[320px_1fr]">
        {/* ---- Left panel ---- */}
        <div className="flex flex-col gap-4">
          <SlotSelector      slots={slots}           onChange={setSlots} />
          <AffixTargetPanel  affixes={targetAffixes} onChange={setTargetAffixes} />
          <WeightConfigPanel weights={weights}        onChange={setWeights} />
          <SearchControls
            onSearch={runSearch}
            isSearching={isSearching}
            disabled={slots.every((s) => !s.enabled)}
            maxCandidates={maxCandidates}
            onMaxCandidatesChange={setMaxCandidates}
          />
        </div>

        {/* ---- Right panel ---- */}
        <div className="flex flex-col gap-4">
          <div>
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wider text-forge-accent">
              Results
            </h2>
            <BisResultsTable
              results={allResults}
              onSelect={setSelectedResult}
              selectedId={selectedResult?.build_id}
            />
          </div>

          <ComparisonViewer
            selected={selectedResult}
            allResults={allResults}
          />

          <SearchVisualization
            results={allResults}
            isSearching={isSearching}
          />
        </div>
      </div>
    </div>
  );
}
