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
import { Panel, Button, Badge, Spinner } from "@/components/ui";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type Step = 1 | 2 | 3 | 4;

interface SimulationResult {
  attempt: number;
  success: boolean;
  fpUsed: number;
  affixes: string;
}

const BASE_ITEMS = [
  { id: "helm",  label: "Helm" },
  { id: "chest", label: "Chest" },
  { id: "sword", label: "Sword" },
  { id: "boots", label: "Boots" },
  { id: "ring",  label: "Ring" },
  { id: "staff", label: "Staff" },
];

const MOCK_RESULTS: SimulationResult[] = [
  { attempt: 1, success: true,  fpUsed: 42, affixes: "T7 Fire Res, T6 Health" },
  { attempt: 2, success: false, fpUsed: 18, affixes: "T5 Fire Res" },
  { attempt: 3, success: true,  fpUsed: 55, affixes: "T7 Fire Res, T7 Health" },
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
}: {
  onBack: () => void;
  onNext: () => void;
}) {
  const [isRunning, setIsRunning] = useState(false);
  const [isDone, setIsDone] = useState(false);

  const handleRun = () => {
    setIsRunning(true);
    setIsDone(false);
    setTimeout(() => {
      setIsRunning(false);
      setIsDone(true);
    }, 1800);
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

function Step4({ onRestart }: { onRestart: () => void }) {
  return (
    <Panel title="Review Result">
      <div className="overflow-x-auto mb-6">
        <table className="w-full font-mono text-xs">
          <thead>
            <tr className="border-b border-forge-border">
              {["Attempt", "Success", "FP Used", "Affixes"].map((col) => (
                <th
                  key={col}
                  className="text-left px-3 py-2 uppercase tracking-widest text-forge-dim"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {MOCK_RESULTS.map((row) => (
              <tr
                key={row.attempt}
                className="border-b border-forge-border/50 hover:bg-forge-surface2 transition-colors"
              >
                <td className="px-3 py-2 text-forge-muted">{row.attempt}</td>
                <td className="px-3 py-2">
                  <Badge variant={row.success ? "ladder" : "hc"}>
                    {row.success ? "Yes" : "No"}
                  </Badge>
                </td>
                <td className="px-3 py-2 text-forge-amber">{row.fpUsed}</td>
                <td className="px-3 py-2 text-forge-text">{row.affixes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

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
  const [, setSimulationResult] = useState<SimulationResult[] | null>(null);

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
    setSimulationResult(null);
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
          onNext={() => {
            setSimulationResult(MOCK_RESULTS);
            goTo(4);
          }}
        />
      )}
      {currentStep === 4 && (
        <Step4 onRestart={handleRestart} />
      )}
    </div>
  );
}
