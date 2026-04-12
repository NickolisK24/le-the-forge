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
import toast from "react-hot-toast";

import SlotSelector       from "@/components/bis/SlotSelector";
import AffixTargetPanel   from "@/components/bis/AffixTargetPanel";
import WeightConfigPanel  from "@/components/bis/WeightConfigPanel";
import SearchControls     from "@/components/bis/SearchControls";
import BisResultsTable    from "@/components/bis/BisResultsTable";
import ComparisonViewer   from "@/components/bis/ComparisonViewer";
import SearchVisualization from "@/components/bis/SearchVisualization";
import { runBisSearch }   from "@/services/bisApi";

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
// Page component
// ---------------------------------------------------------------------------

// Physical DPS preset — covers the most common melee/ranged weapons and
// basic offence stats. Tiers are modest so results are usually feasible.
const PHYSICAL_DPS_PRESET: AffixTarget[] = [
  { affix_id: "physical_damage",            affix_name: "Physical Damage",            min_tier: 3, target_tier: 5 },
  { affix_id: "attack_speed",               affix_name: "Attack Speed",               min_tier: 3, target_tier: 5 },
  { affix_id: "critical_strike_chance",     affix_name: "Critical Strike Chance",     min_tier: 3, target_tier: 5 },
  { affix_id: "critical_strike_multiplier", affix_name: "Critical Strike Multiplier", min_tier: 3, target_tier: 5 },
];

export default function BisSearchPage() {
  const [slots,           setSlots]           = useState<SlotConfig[]>(DEFAULT_SLOTS);
  const [targetAffixes,   setTargetAffixes]   = useState<AffixTarget[]>([]);
  const [weights,         setWeights]         = useState<WeightConfig>(DEFAULT_WEIGHTS);
  const [maxCandidates,   setMaxCandidates]   = useState(200);
  const [isSearching,     setIsSearching]     = useState(false);
  const [result,          setResult]          = useState<BisSearchResponse | null>(null);
  const [selectedResult,  setSelectedResult]  = useState<BisSearchResult | null>(null);
  const [error,           setError]           = useState<string | null>(null);
  const [howToOpen,       setHowToOpen]       = useState(true);

  const runSearch = useCallback(async () => {
    setIsSearching(true);
    setSelectedResult(null);
    setError(null);

    try {
      const enabledSlots = slots.filter((s) => s.enabled).map((s) => s.slot_type);
      const affixIds = targetAffixes.map((a) => a.affix_id);
      const tierMap: Record<string, number> = {};
      for (const a of targetAffixes) {
        tierMap[a.affix_id] = a.target_tier;
      }

      const response = await runBisSearch({
        slots: enabledSlots,
        target_affixes: affixIds,
        target_tiers: tierMap,
        top_n: 20,
        max_candidates: maxCandidates,
      });

      setResult({
        search_id: response.search_id,
        total_evaluated: response.total_evaluated,
        best_score: response.best_score,
        duration_s: response.duration_s,
        results: response.results,
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : "BIS search failed";
      setError(msg);
      toast.error(msg);
    } finally {
      setIsSearching(false);
    }
  }, [slots, targetAffixes, maxCandidates]);

  const allResults = result?.results ?? [];

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* Page header */}
      <div className="mb-4">
        <h1 className="font-display text-2xl font-bold text-[#f5a623]">BIS Search Engine</h1>
        <p className="mt-1 text-sm text-forge-muted">
          Find the optimal gear combination across all slots by evaluating thousands of
          candidate builds against your target affixes and score weights.
        </p>
      </div>

      {/* How-to + preset panel */}
      <div className="mb-6 rounded-lg border border-forge-cyan/25 bg-forge-cyan/[0.04]">
        <button
          type="button"
          onClick={() => setHowToOpen((v) => !v)}
          className="w-full flex items-center justify-between px-4 py-2.5 bg-transparent border-none cursor-pointer text-left"
        >
          <span className="font-mono text-[11px] uppercase tracking-widest text-forge-cyan">
            {howToOpen ? "▾" : "▸"} How to use BIS Search
          </span>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setTargetAffixes(PHYSICAL_DPS_PRESET);
              setHowToOpen(false);
            }}
            className="rounded bg-forge-amber/20 border border-forge-amber/50 text-forge-amber hover:bg-forge-amber/30 px-3 py-1 text-[11px] font-mono uppercase tracking-widest transition-colors"
          >
            Load Example · Physical DPS
          </button>
        </button>
        {howToOpen && (
          <div className="px-4 pb-4 pt-1 text-sm text-forge-muted leading-relaxed space-y-2">
            <p>
              <span className="font-mono text-[11px] uppercase tracking-widest text-forge-amber mr-2">Step 1</span>
              Choose the <strong className="text-forge-text">gear slots</strong> to include in the search
              (weapons, armour, jewellery). Disable slots you've already locked in.
            </p>
            <p>
              <span className="font-mono text-[11px] uppercase tracking-widest text-forge-amber mr-2">Step 2</span>
              Add the <strong className="text-forge-text">target affixes</strong> you want — e.g. Physical Damage,
              Attack Speed, Crit Multi — and set the minimum tier that counts as "good enough".
            </p>
            <p>
              <span className="font-mono text-[11px] uppercase tracking-widest text-forge-amber mr-2">Step 3</span>
              Tune <strong className="text-forge-text">score weights</strong> (tier vs. coverage vs. FP vs.
              feasibility) and hit <strong className="text-forge-text">Run Search</strong>. The top-scoring
              candidates appear on the right.
            </p>
          </div>
        )}
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

      {/* Error banner */}
      {error && !isSearching && (
        <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm text-red-400">
          {error}
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
