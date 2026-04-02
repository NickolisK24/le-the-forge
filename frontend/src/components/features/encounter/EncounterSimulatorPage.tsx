/**
 * D4 — Encounter Simulator Page
 *
 * Root container for the Phase C encounter simulation UI.
 * Manages global form state and orchestrates the simulation API call.
 */

import { useState, useCallback } from "react";
import toast from "react-hot-toast";

import BuildControls from "./BuildControls";
import EncounterControls from "./EncounterControls";
import ResultsPanel from "./ResultsPanel";
import DamageChart from "./DamageChart";
import {
  runSimulation,
  type EncounterRequest,
  type EncounterResult,
} from "@/services/encounterApi";

const DEFAULT_REQUEST: EncounterRequest = {
  base_damage:     500.0,
  fight_duration:  60.0,
  tick_size:       0.1,
  enemy_template:  "STANDARD_BOSS",
  distribution:    "SINGLE",
  crit_chance:     0.05,
  crit_multiplier: 2.0,
};

export default function EncounterSimulatorPage() {
  const [request, setRequest] = useState<EncounterRequest>(DEFAULT_REQUEST);
  const [result,  setResult]  = useState<EncounterResult | null>(null);
  const [loading, setLoading] = useState(false);

  const patch = useCallback(
    (update: Partial<EncounterRequest>) => setRequest((prev) => ({ ...prev, ...update })),
    []
  );

  const handleRun = useCallback(async () => {
    setLoading(true);
    try {
      const res = await runSimulation(request);
      setResult(res);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Simulation failed");
    } finally {
      setLoading(false);
    }
  }, [request]);

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="mb-1 text-2xl font-bold text-forge-text">Encounter Simulator</h1>
      <p className="mb-6 text-sm text-forge-muted">
        Simulate your build against boss templates using the Phase C encounter engine.
      </p>

      <div className="space-y-6 rounded-lg border border-forge-border bg-forge-surface p-6">
        <BuildControls
          values={request}
          onChange={patch}
          disabled={loading}
        />

        <hr className="border-forge-border" />

        <EncounterControls
          values={request}
          onChange={patch}
          disabled={loading}
        />

        <div className="flex justify-end">
          <button
            onClick={handleRun}
            disabled={loading}
            className="
              rounded bg-forge-accent px-6 py-2 text-sm font-semibold text-forge-bg
              hover:brightness-110 active:brightness-90
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all
            "
          >
            {loading ? "Simulating…" : "Run Simulation"}
          </button>
        </div>
      </div>

      {(result || loading) && (
        <div className="mt-6 space-y-6 rounded-lg border border-forge-border bg-forge-surface p-6">
          <ResultsPanel result={result} isLoading={loading} />

          {result && result.damage_per_tick.length > 0 && (
            <>
              <hr className="border-forge-border" />
              <DamageChart data={result.damage_per_tick} tickSize={request.tick_size} />
            </>
          )}
        </div>
      )}
    </div>
  );
}
