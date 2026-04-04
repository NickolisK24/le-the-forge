/**
 * Q23 — AffixTargetPanel
 *
 * Allows the user to specify up to 4 affix targets for the BIS search,
 * each with a min_tier and target_tier. Fetches real affix data from API.
 */

import { useState, useMemo, useEffect } from "react";
import { useAffixes } from "@/hooks";
import type { AffixTarget } from "@/pages/bis/BisSearchPage";

const MAX_AFFIXES = 4;

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface Props {
  affixes: AffixTarget[];
  onChange: (affixes: AffixTarget[]) => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function AffixTargetPanel({ affixes, onChange }: Props) {
  const { data: affixRes, isLoading } = useAffixes();
  const allAffixes = affixRes?.data ?? [];
  const [selectedId, setSelectedId] = useState("");
  const [minTier,    setMinTier]    = useState(1);
  const [targetTier, setTargetTier] = useState(5);
  const [error,      setError]      = useState("");
  const [search,     setSearch]     = useState("");

  // Filter affixes for the dropdown
  const filteredAffixes = useMemo(() => {
    if (!allAffixes.length) return [];
    let list = allAffixes;
    if (search) {
      const q = search.toLowerCase();
      list = list.filter((a) => a.name.toLowerCase().includes(q));
    }
    return list.slice(0, 100);
  }, [allAffixes, search]);

  // Auto-select first
  useEffect(() => {
    if (!selectedId && filteredAffixes.length > 0) {
      setSelectedId(filteredAffixes[0].id);
    }
  }, [filteredAffixes, selectedId]);

  function addAffix() {
    if (affixes.length >= MAX_AFFIXES) {
      setError(`Maximum ${MAX_AFFIXES} affixes allowed.`);
      return;
    }
    if (affixes.some((a) => a.affix_id === selectedId)) {
      setError("That affix is already added.");
      return;
    }
    setError("");
    const meta = allAffixes.find((a) => a.id === selectedId);
    if (!meta) return;
    onChange([
      ...affixes,
      {
        affix_id:    selectedId,
        affix_name:  meta.name,
        min_tier:    minTier,
        target_tier: targetTier,
      },
    ]);
  }

  function remove(affix_id: string) {
    setError("");
    onChange(affixes.filter((a) => a.affix_id !== affix_id));
  }

  return (
    <div className="rounded-lg border border-forge-border bg-forge-surface p-4">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-forge-accent">
        Affix Targets
      </h2>

      {/* Add row */}
      <div className="space-y-2">
        {/* Search filter */}
        <div className="flex flex-col gap-1">
          <label className="text-xs uppercase tracking-wide text-forge-muted">Search</label>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter affixes..."
            className="w-full rounded border border-forge-border bg-forge-input px-3 py-1.5 text-sm text-forge-text placeholder:text-forge-dim
              focus:border-forge-accent focus:outline-none"
          />
        </div>

        {/* Affix select */}
        <div className="flex flex-col gap-1">
          <label className="text-xs uppercase tracking-wide text-forge-muted">Affix</label>
          {isLoading ? (
            <div className="text-xs text-forge-dim py-2">Loading affixes...</div>
          ) : (
            <select
              value={selectedId}
              onChange={(e) => setSelectedId(e.target.value)}
              className="w-full rounded border border-forge-border bg-forge-input px-3 py-1.5 text-sm text-forge-text
                focus:border-forge-accent focus:outline-none"
            >
              {filteredAffixes.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} ({a.type})
                </option>
              ))}
              {filteredAffixes.length === 0 && (
                <option disabled>No matching affixes</option>
              )}
            </select>
          )}
        </div>

        {/* Tier sliders */}
        <div className="grid grid-cols-2 gap-3">
          <div className="flex flex-col gap-1">
            <label className="text-xs uppercase tracking-wide text-forge-muted">
              Min Tier: <span className="text-[#f5a623]">T{minTier}</span>
            </label>
            <input
              type="range" min={1} max={7} step={1}
              value={minTier}
              onChange={(e) => setMinTier(Number(e.target.value))}
              className="accent-[#f5a623]"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs uppercase tracking-wide text-forge-muted">
              Target Tier: <span className="text-[#22d3ee]">T{targetTier}</span>
            </label>
            <input
              type="range" min={1} max={7} step={1}
              value={targetTier}
              onChange={(e) => setTargetTier(Number(e.target.value))}
              className="accent-[#22d3ee]"
            />
          </div>
        </div>

        {/* Error */}
        {error && (
          <p className="text-xs text-red-400">{error}</p>
        )}

        {/* Add button */}
        <button
          onClick={addAffix}
          disabled={affixes.length >= MAX_AFFIXES || !selectedId}
          className="w-full rounded border border-forge-border px-3 py-1.5 text-xs font-medium text-forge-muted
            hover:border-[#f5a623] hover:text-[#f5a623] transition-colors
            disabled:cursor-not-allowed disabled:opacity-40"
        >
          + Add Affix
        </button>
      </div>

      {/* Current list */}
      {affixes.length > 0 && (
        <div className="mt-3 space-y-1.5">
          <p className="text-xs uppercase tracking-wide text-forge-muted">Active Targets</p>
          {affixes.map((a) => (
            <div
              key={a.affix_id}
              className="flex items-center justify-between rounded bg-[#1a2040] px-3 py-2 text-xs"
            >
              <span className="font-medium text-forge-text">{a.affix_name}</span>
              <div className="flex items-center gap-3">
                <span className="text-forge-muted">
                  min <span className="text-[#f5a623]">T{a.min_tier}</span>
                </span>
                <span className="text-forge-muted">
                  target <span className="text-[#22d3ee]">T{a.target_tier}</span>
                </span>
                <button
                  onClick={() => remove(a.affix_id)}
                  className="text-forge-muted hover:text-red-400 transition-colors font-bold"
                  aria-label={`Remove ${a.affix_name}`}
                >
                  x
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {affixes.length === 0 && (
        <p className="mt-3 text-xs text-forge-muted italic">No affix targets set — add up to {MAX_AFFIXES}.</p>
      )}
    </div>
  );
}
