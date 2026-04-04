/**
 * P21 — Crafting Optimizer Page
 *
 * Route: /crafting
 *
 * Composes BaseItemSelector, TargetAffixBuilder, CraftSequenceViewer,
 * ProbabilityPanel, and CraftOutcomeChart. Runs a client-side mock simulation
 * and distributes results to child components.
 */

import { useState } from "react";

import BaseItemSelector   from "@/components/crafting/BaseItemSelector";
import TargetAffixBuilder from "@/components/crafting/TargetAffixBuilder";
import CraftSequenceViewer from "@/components/crafting/CraftSequenceViewer";
import ProbabilityPanel   from "@/components/crafting/ProbabilityPanel";
import CraftOutcomeChart  from "@/components/crafting/CraftOutcomeChart";

// ---------------------------------------------------------------------------
// Types (exported so sub-components can import them)
// ---------------------------------------------------------------------------

export interface BaseItem {
  id: string;
  name: string;
  item_class: string;
  forging_potential: number;
}

export interface TargetAffix {
  affix_id: string;
  affix_name: string;
  min_tier: number;
  target_tier: number;
}

export interface CraftStep {
  action_type: string;
  target_affix_id?: string;
  new_affix_id?: string;
}

export interface CraftOptimizationResult {
  optimal_path: CraftStep[];
  score: number;
  success_probability: number;
  mean_fp_cost: number;
  fracture_rate: number;
  confidence_interval: [number, number];
  steps: number;
}

// ---------------------------------------------------------------------------
// Mock simulation
// ---------------------------------------------------------------------------

async function generateMockResult(affixes: TargetAffix[]): Promise<CraftOptimizationResult> {
  await new Promise<void>((resolve) => setTimeout(resolve, 600));

  // One ADD_AFFIX per affix, then UPGRADE_AFFIX for each tier gap
  const optimalPath: CraftStep[] = [];

  for (const a of affixes) {
    optimalPath.push({ action_type: "add_affix", new_affix_id: a.affix_id });
  }

  for (const a of affixes) {
    const gap = a.target_tier - a.min_tier;
    for (let i = 0; i < gap; i++) {
      optimalPath.push({ action_type: "upgrade_affix", target_affix_id: a.affix_id });
    }
  }

  const successProbability = 0.65 + Math.random() * 0.2;

  return {
    optimal_path: optimalPath,
    score: 0.7 + Math.random() * 0.25,
    success_probability: successProbability,
    mean_fp_cost: affixes.length * 15 + Math.random() * 20,
    fracture_rate: 0.1 + Math.random() * 0.15,
    confidence_interval: [successProbability - 0.08, successProbability + 0.08],
    steps: optimalPath.length,
  };
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function CraftingPage() {
  const [selectedBase,  setSelectedBase]  = useState<BaseItem | null>(null);
  const [targetAffixes, setTargetAffixes] = useState<TargetAffix[]>([]);
  const [isSimulating,  setIsSimulating]  = useState(false);
  const [result,        setResult]        = useState<CraftOptimizationResult | null>(null);

  const canRun =
    selectedBase !== null && targetAffixes.length > 0 && !isSimulating;

  async function runSimulation() {
    if (!canRun) return;
    setIsSimulating(true);
    try {
      const res = await generateMockResult(targetAffixes);
      setResult(res);
    } finally {
      setIsSimulating(false);
    }
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-6">
      {/* Header */}
      <div>
        <h1 className="font-display text-2xl text-[#f5a623]">Crafting Optimizer</h1>
        <p className="font-body text-sm text-gray-400 mt-1">
          Select a base item, define your affix targets, then run the simulation to
          find the optimal crafting sequence.
        </p>
      </div>

      {/* Run button */}
      <div className="flex items-center gap-4">
        <button
          onClick={runSimulation}
          disabled={!canRun}
          className="rounded bg-[#f5a623] px-5 py-2 text-sm font-semibold text-[#10152a] transition hover:bg-[#f5a623cc] disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {isSimulating ? "Simulating…" : "Run Simulation"}
        </button>

        {isSimulating && (
          <span className="flex items-center gap-1.5 text-[#22d3ee] text-sm">
            <span className="animate-spin text-base leading-none">⟳</span>
            Calculating…
          </span>
        )}

        {selectedBase && (
          <span className="text-xs text-gray-400">
            Base:{" "}
            <span className="text-gray-200 font-medium">{selectedBase.name}</span>
            {" "}· FP{" "}
            <span className="text-[#f5a623]">{selectedBase.forging_potential}</span>
          </span>
        )}
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left column */}
        <div className="space-y-4">
          <BaseItemSelector
            selected={selectedBase}
            onSelect={setSelectedBase}
          />
          <TargetAffixBuilder
            affixes={targetAffixes}
            onChange={setTargetAffixes}
          />
        </div>

        {/* Right column */}
        <div className="space-y-4">
          <CraftSequenceViewer
            steps={result?.optimal_path ?? []}
            isLoading={isSimulating}
          />
          <ProbabilityPanel result={result} />
          <CraftOutcomeChart result={result} />
        </div>
      </div>
    </div>
  );
}
