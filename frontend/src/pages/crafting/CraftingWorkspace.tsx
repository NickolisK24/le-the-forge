/**
 * UI8 — Crafting Workspace
 *
 * Route: /crafting-workspace
 *
 * 4-step crafting workflow:
 *   1. Select Base Item
 *   2. Define Target
 *   3. Run Simulation
 *   4. Review Result
 */

import { useState } from "react";
import toast from "react-hot-toast";
import { Panel, Button, Badge, Spinner } from "@/components/ui";
import { predictCrafting, type CraftPredictResponse } from "@/services/craftingApi";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type Step = 1 | 2 | 3 | 4;

const BASE_ITEMS = [
  { id: "helm",  label: "Helm" },
  { id: "chest", label: "Chest" },
  { id: "sword", label: "Sword" },
  { id: "boots", label: "Boots" },
  { id: "ring",  label: "Ring" },
  { id: "staff", label: "Staff" },
];

// ---------------------------------------------------------------------------
// Stepper
// ---------------------------------------------------------------------------

const STEP_LABELS = [
  "Select Base Item",
  "Define Target",
  "Run Simulation",
  "Review Result",
];

function Stepper({ current }: { current: Step }) {
  return (
    <div className="flex items-center gap-0 mb-6">
      {STEP_LABELS.map((label, idx) => {
        const step = (idx + 1) as Step;
        const isActive = step === current;
        const isDone = step < current;
        return (
          <div key={step} className="flex items-center flex-1 last:flex-none">
            <div className="flex flex-col items-center">
              <div
                className={[
                  "w-8 h-8 rounded-full border-2 flex items-center justify-center font-mono text-xs font-bold transition-colors",
                  isActive
                    ? "border-forge-amber bg-forge-amber/20 text-forge-amber shadow-glow-amber"
                    : isDone
                    ? "border-forge-green bg-forge-green/20 text-forge-green"
                    : "border-forge-border bg-forge-surface2 text-forge-dim",
                ].join(" ")}
              >
                {isDone ? "✓" : step}
              </div>
              <span
                className={[
                  "mt-1 font-mono text-[10px] uppercase tracking-widest whitespace-nowrap",
                  isActive ? "text-forge-amber" : isDone ? "text-forge-green" : "text-forge-dim",
                ].join(" ")}
              >
                {label}
              </span>
            </div>
            {idx < STEP_LABELS.length - 1 && (
              <div
                className={[
                  "flex-1 h-px mx-2 mt-[-16px] transition-colors",
                  isDone ? "bg-forge-green/50" : "bg-forge-border",
                ].join(" ")}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Step panels
// ---------------------------------------------------------------------------

function Step1({
  selectedBase,
  onSelect,
  onNext,
}: {
  selectedBase: string | null;
  onSelect: (id: string) => void;
  onNext: () => void;
}) {
  return (
    <Panel title="Select Base Item">
      <div className="grid grid-cols-3 gap-3 mb-6">
        {BASE_ITEMS.map((item) => (
          <button
            key={item.id}
            onClick={() => onSelect(item.id)}
            className={[
              "rounded border px-4 py-5 font-body text-sm transition-all text-center",
              selectedBase === item.id
                ? "border-forge-amber bg-forge-amber/10 text-forge-amber shadow-glow-amber"
                : "border-forge-border bg-forge-surface2 text-forge-muted hover:border-forge-amber/40 hover:text-forge-text",
            ].join(" ")}
          >
            {item.label}
          </button>
        ))}
      </div>
      <div className="flex justify-end">
        <Button variant="primary" onClick={onNext} disabled={!selectedBase}>
          Next →
        </Button>
      </div>
    </Panel>
  );
}

function Step2({
  targetAffixes,
  onAdd,
  onRemove,
  onBack,
  onNext,
}: {
  targetAffixes: string[];
  onAdd: (affix: string) => void;
  onRemove: (affix: string) => void;
  onBack: () => void;
  onNext: () => void;
}) {
  const [inputVal, setInputVal] = useState("");

  const handleAdd = () => {
    const trimmed = inputVal.trim();
    if (trimmed && !targetAffixes.includes(trimmed)) {
      onAdd(trimmed);
      setInputVal("");
    }
  };

  return (
    <Panel title="Define Target">
      <div className="mb-4">
        <label className="font-mono text-[11px] uppercase tracking-widest text-forge-dim block mb-2">
          Target Affixes
        </label>
        <textarea
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          placeholder="Type an affix name and press Add..."
          rows={3}
          className="w-full rounded border border-forge-border bg-forge-surface2 px-3 py-2 font-body text-sm text-forge-text placeholder:text-forge-dim outline-none focus:border-forge-amber/60 resize-none"
        />
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        <Button variant="ghost" size="sm" onClick={() => onAdd("Add T7 Fire Resistance")}>
          + T7 Fire Resistance
        </Button>
        <Button variant="ghost" size="sm" onClick={() => onAdd("Add T7 Health")}>
          + T7 Health
        </Button>
        <Button variant="outline" size="sm" onClick={handleAdd} disabled={!inputVal.trim()}>
          Add Custom
        </Button>
      </div>

      {targetAffixes.length > 0 && (
        <div className="mb-4 flex flex-col gap-2">
          <div className="font-mono text-[11px] uppercase tracking-widest text-forge-dim mb-1">
            Added Affixes
          </div>
          {targetAffixes.map((affix) => (
            <div
              key={affix}
              className="flex items-center justify-between rounded border border-forge-border bg-forge-surface2 px-3 py-2"
            >
              <span className="font-body text-sm text-forge-text">{affix}</span>
              <button
                onClick={() => onRemove(affix)}
                className="font-mono text-xs text-forge-dim hover:text-forge-red transition-colors"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="flex justify-between mt-2">
        <Button variant="ghost" onClick={onBack}>← Back</Button>
        <Button variant="primary" onClick={onNext} disabled={targetAffixes.length === 0}>
          Next →
        </Button>
      </div>
    </Panel>
  );
}

function Step3({
  onBack,
  onNext,
  targetAffixes,
  onResult,
}: {
  onBack: () => void;
  onNext: () => void;
  targetAffixes: string[];
  onResult: (result: CraftPredictResponse) => void;
}) {
  const [isRunning, setIsRunning] = useState(false);
  const [isDone, setIsDone] = useState(false);

  const handleRun = async () => {
    setIsRunning(true);
    setIsDone(false);
    try {
      const result = await predictCrafting({
        forge_potential: 28,
        affixes: targetAffixes.map((name, i) => ({
          affix_id: `affix_${i}`,
          affix_name: name,
          current_tier: 0,
          target_tier: 5,
        })),
      });
      onResult(result);
      setIsDone(true);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Simulation failed");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <Panel title="Run Simulation">
      <div className="flex flex-col items-center gap-6 py-6">
        <Button
          variant="primary"
          className="w-full"
          onClick={handleRun}
          disabled={isRunning}
        >
          {isRunning ? "Simulating..." : "Run Monte Carlo Simulation"}
        </Button>

        <div className="text-center">
          <p className="font-body text-sm text-forge-muted">
            Simulates 1000 crafting attempts
          </p>
          {isRunning && (
            <div className="flex items-center justify-center gap-2 mt-4">
              <Spinner size={18} />
              <span className="font-mono text-xs text-forge-cyan">Running simulation...</span>
            </div>
          )}
          {isDone && !isRunning && (
            <div className="mt-4">
              <Badge variant="ladder">Simulation complete</Badge>
            </div>
          )}
        </div>
      </div>

      <div className="flex justify-between mt-2">
        <Button variant="ghost" onClick={onBack}>← Back</Button>
        {isDone && (
          <Button variant="primary" onClick={onNext}>Next →</Button>
        )}
      </div>
    </Panel>
  );
}

function Step4({
  onRestart,
  result,
}: {
  onRestart: () => void;
  result: CraftPredictResponse | null;
}) {
  const sim = result?.simulation_result;
  const path = result?.optimal_path ?? [];
  const strategies = result?.strategy_comparison ?? [];

  return (
    <Panel title="Review Result">
      {/* Simulation summary */}
      {sim && (
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="rounded border border-forge-border bg-forge-surface2 px-4 py-3">
            <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">Completion Chance</div>
            <div className="mt-1 font-display text-lg font-bold text-forge-green">
              {(sim.completion_chance * 100).toFixed(1)}%
            </div>
          </div>
          <div className="rounded border border-forge-border bg-forge-surface2 px-4 py-3">
            <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">Craft Steps</div>
            <div className="mt-1 font-display text-lg font-bold text-forge-amber">{path.length}</div>
          </div>
          <div className="rounded border border-forge-border bg-forge-surface2 px-4 py-3">
            <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">Simulations</div>
            <div className="mt-1 font-display text-lg font-bold text-forge-cyan">{sim.n_simulations.toLocaleString()}</div>
          </div>
        </div>
      )}

      {/* Optimal path */}
      {path.length > 0 && (
        <div className="mb-6">
          <div className="font-mono text-[11px] uppercase tracking-widest text-forge-dim mb-2">Optimal Path</div>
          <div className="overflow-x-auto">
            <table className="w-full font-mono text-xs">
              <thead>
                <tr className="border-b border-forge-border">
                  <th className="text-left px-3 py-2 uppercase tracking-widest text-forge-dim">Step</th>
                  <th className="text-left px-3 py-2 uppercase tracking-widest text-forge-dim">Action</th>
                  <th className="text-left px-3 py-2 uppercase tracking-widest text-forge-dim">Target</th>
                </tr>
              </thead>
              <tbody>
                {path.map((step, i) => (
                  <tr key={i} className="border-b border-forge-border/50 hover:bg-forge-surface2 transition-colors">
                    <td className="px-3 py-2 text-forge-muted">{i + 1}</td>
                    <td className="px-3 py-2 text-forge-text">{step.action}</td>
                    <td className="px-3 py-2 text-forge-amber">{step.affix_name ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Strategy comparison */}
      {strategies.length > 0 && (
        <div className="mb-6">
          <div className="font-mono text-[11px] uppercase tracking-widest text-forge-dim mb-2">Strategy Comparison</div>
          <div className="overflow-x-auto">
            <table className="w-full font-mono text-xs">
              <thead>
                <tr className="border-b border-forge-border">
                  <th className="text-left px-3 py-2 uppercase tracking-widest text-forge-dim">Strategy</th>
                  <th className="text-left px-3 py-2 uppercase tracking-widest text-forge-dim">Success</th>
                  <th className="text-left px-3 py-2 uppercase tracking-widest text-forge-dim">Avg FP</th>
                  <th className="text-left px-3 py-2 uppercase tracking-widest text-forge-dim">Steps</th>
                </tr>
              </thead>
              <tbody>
                {strategies.map((s, i) => (
                  <tr key={i} className="border-b border-forge-border/50 hover:bg-forge-surface2 transition-colors">
                    <td className="px-3 py-2 text-forge-text">{s.name}</td>
                    <td className="px-3 py-2">
                      <Badge variant={s.completion_chance > 0.5 ? "ladder" : "hc"}>
                        {(s.completion_chance * 100).toFixed(1)}%
                      </Badge>
                    </td>
                    <td className="px-3 py-2 text-forge-amber">{s.mean_fp_cost.toFixed(1)}</td>
                    <td className="px-3 py-2 text-forge-muted">{s.steps}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="flex gap-3">
        <Button variant="ghost" onClick={onRestart}>← Start Over</Button>
        <Button variant="outline">Export Results</Button>
      </div>
    </Panel>
  );
}

// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------

export default function CraftingWorkspace() {
  const [currentStep, setCurrentStep] = useState<Step>(1);
  const [selectedBase, setSelectedBase] = useState<string | null>(null);
  const [targetAffixes, setTargetAffixes] = useState<string[]>([]);
  const [craftResult, setCraftResult] = useState<CraftPredictResponse | null>(null);

  const goTo = (step: Step) => setCurrentStep(step);

  const handleAddAffix = (affix: string) => {
    setTargetAffixes((prev) => (prev.includes(affix) ? prev : [...prev, affix]));
  };

  const handleRemoveAffix = (affix: string) => {
    setTargetAffixes((prev) => prev.filter((a) => a !== affix));
  };

  const handleRestart = () => {
    setCurrentStep(1);
    setSelectedBase(null);
    setTargetAffixes([]);
    setCraftResult(null);
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      {/* Page header */}
      <div className="mb-6">
        <h1 className="font-display text-2xl font-bold text-forge-amber">
          Crafting Workspace
        </h1>
        <p className="mt-1 font-body text-sm text-forge-muted">
          Step-by-step crafting workflow with Monte Carlo simulation.
        </p>
      </div>

      {/* Stepper */}
      <Stepper current={currentStep} />

      {/* Step panels */}
      {currentStep === 1 && (
        <Step1
          selectedBase={selectedBase}
          onSelect={setSelectedBase}
          onNext={() => goTo(2)}
        />
      )}
      {currentStep === 2 && (
        <Step2
          targetAffixes={targetAffixes}
          onAdd={handleAddAffix}
          onRemove={handleRemoveAffix}
          onBack={() => goTo(1)}
          onNext={() => goTo(3)}
        />
      )}
      {currentStep === 3 && (
        <Step3
          onBack={() => goTo(2)}
          onNext={() => goTo(4)}
          targetAffixes={targetAffixes}
          onResult={(result) => setCraftResult(result)}
        />
      )}
      {currentStep === 4 && (
        <Step4 onRestart={handleRestart} result={craftResult} />
      )}
    </div>
  );
}
