/**
 * SimulationPage — unified entry point for encounter simulation.
 *
 * Offers two modes:
 *   - Quick Sim: scalar damage inputs (EncounterSimulatorPage)
 *   - Build Sim: full build definition with skills, gear, passives (BuildEditorPage)
 */

import { useState } from "react";
import EncounterSimulatorPage from "@/components/features/encounter/EncounterSimulatorPage";
import BuildEditorPage from "@/components/features/encounter/BuildEditorPage";

type Mode = "quick" | "build";

export default function SimulationPage() {
  const [mode, setMode] = useState<Mode>("build");

  return (
    <div>
      {/* Mode toggle */}
      <div className="mx-auto max-w-5xl px-4 pt-6">
        <div className="flex items-center gap-1 rounded-lg border border-forge-border bg-forge-surface p-1 w-fit">
          <button
            onClick={() => setMode("build")}
            className={`rounded px-4 py-1.5 font-mono text-xs uppercase tracking-wider transition-all ${
              mode === "build"
                ? "bg-forge-amber/20 text-forge-amber font-semibold"
                : "text-forge-dim hover:text-forge-muted"
            }`}
          >
            Build Simulator
          </button>
          <button
            onClick={() => setMode("quick")}
            className={`rounded px-4 py-1.5 font-mono text-xs uppercase tracking-wider transition-all ${
              mode === "quick"
                ? "bg-forge-amber/20 text-forge-amber font-semibold"
                : "text-forge-dim hover:text-forge-muted"
            }`}
          >
            Quick Sim
          </button>
        </div>
      </div>

      {mode === "build" ? <BuildEditorPage /> : <EncounterSimulatorPage />}
    </div>
  );
}
