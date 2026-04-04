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
import toast from "react-hot-toast";

import BaseItemSelector   from "@/components/crafting/BaseItemSelector";
import TargetAffixBuilder from "@/components/crafting/TargetAffixBuilder";
import CraftSequenceViewer from "@/components/crafting/CraftSequenceViewer";
import ProbabilityPanel   from "@/components/crafting/ProbabilityPanel";
import CraftOutcomeChart  from "@/components/crafting/CraftOutcomeChart";
import { predictCrafting } from "@/services/craftingApi";

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
    if (!canRun || !selectedBase) return;
    setIsSimulating(true);
    try {
      const response = await predictCrafting({
        forge_potential: selectedBase.forging_potential,
        affixes: targetAffixes.map((a) => ({
          affix_id: a.affix_id,
          affix_name: a.affix_name,
          current_tier: a.min_tier,
          target_tier: a.target_tier,
        })),
      });

      const path = response.optimal_path ?? [];
      const sim = response.simulation_result ?? {};
      const strategies = response.strategy_comparison ?? [];

      // Map backend response to the UI result shape
      const completionChance = sim.completion_chance ?? 0;
      const bestStrategy = strategies.length > 0
        ? strategies.reduce((best, s) => s.completion_chance > best.completion_chance ? s : best, strategies[0])
        : null;

      setResult({
        optimal_path: path.map((s) => ({
          action_type: s.action ?? "unknown",
          target_affix_id: s.affix_name,
          new_affix_id: s.affix_name,
        })),
        score: completionChance,
        success_probability: completionChance,
        mean_fp_cost: bestStrategy?.mean_fp_cost ?? 0,
        fracture_rate: 1 - completionChance,
        confidence_interval: [
          Math.max(0, completionChance - 0.05),
          Math.min(1, completionChance + 0.05),
        ],
        steps: path.length,
      });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Craft prediction failed");
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
