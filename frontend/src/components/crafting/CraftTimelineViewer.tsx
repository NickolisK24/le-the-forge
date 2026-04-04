/**
 * UI9 — Craft Timeline Viewer
 *
 * Step-by-step crafting timeline display with vertical connecting line,
 * outcome indicators, success chance bars, and FP costs.
 */

import { EmptyState } from "@/components/ui";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface CraftStep {
  stepNumber: number;
  action: string;
  successChance: number; // 0-1
  outcome: "success" | "failure" | "partial";
  fpCost: number;
  note?: string;
}

export interface CraftTimelineViewerProps {
  steps: CraftStep[];
  currentStep?: number;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function outcomeColor(outcome: CraftStep["outcome"]) {
  switch (outcome) {
    case "success": return "bg-forge-green border-forge-green text-forge-green";
    case "failure": return "bg-forge-red/20 border-forge-red text-forge-red";
    case "partial": return "bg-forge-amber/20 border-forge-amber text-forge-amber";
  }
}

function outcomeLabel(outcome: CraftStep["outcome"]) {
  switch (outcome) {
    case "success": return "Success";
    case "failure": return "Failure";
    case "partial": return "Partial";
  }
}

function outcomeDot(outcome: CraftStep["outcome"], isCurrent: boolean, isFuture: boolean) {
  if (isFuture) return "bg-forge-surface2 border-forge-border";
  switch (outcome) {
    case "success": return isCurrent ? "bg-forge-green border-forge-green shadow-glow-amber" : "bg-forge-green border-forge-green";
    case "failure": return isCurrent ? "bg-forge-red border-forge-red shadow-glow-amber" : "bg-forge-red border-forge-red";
    case "partial": return isCurrent ? "bg-forge-amber border-forge-amber shadow-glow-amber" : "bg-forge-amber border-forge-amber";
  }
}

// ---------------------------------------------------------------------------
// Single timeline step
// ---------------------------------------------------------------------------

function TimelineStep({
  step,
  isLast,
  isCurrent,
  isFuture,
}: {
  step: CraftStep;
  isLast: boolean;
  isCurrent: boolean;
  isFuture: boolean;
}) {
  const chancePct = Math.round(step.successChance * 100);

  return (
    <div className="flex gap-4">
      {/* Left: dot + connecting line */}
      <div className="flex flex-col items-center flex-shrink-0">
        <div
          className={[
            "w-4 h-4 rounded-full border-2 flex-shrink-0 transition-all",
            outcomeDot(step.outcome, isCurrent, isFuture),
            isCurrent ? "scale-125" : "",
          ].join(" ")}
        />
        {!isLast && <div className="w-px flex-1 bg-forge-border mt-1" />}
      </div>

      {/* Right: content */}
      <div
        className={[
          "flex-1 pb-6 rounded border px-4 py-3 mb-1 transition-all",
          isCurrent
            ? "border-forge-amber/60 bg-forge-amber/5 shadow-glow-amber"
            : isFuture
            ? "border-forge-border bg-forge-surface2 opacity-50"
            : "border-forge-border bg-forge-surface2",
        ].join(" ")}
      >
        {/* Header row */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="font-mono text-[10px] text-forge-dim uppercase tracking-widest">
              Step {step.stepNumber}
            </span>
            {isCurrent && (
              <span className="font-mono text-[10px] text-forge-amber uppercase tracking-widest">
                ● Current
              </span>
            )}
          </div>
          <span className="font-mono text-[10px] text-forge-amber">
            {step.fpCost} FP
          </span>
        </div>

        {/* Action name */}
        <div className="font-body text-sm text-forge-text mb-2">{step.action}</div>

        {/* Success chance bar */}
        {!isFuture && (
          <div className="mb-2">
            <div className="flex justify-between font-mono text-[10px] text-forge-dim mb-1">
              <span>Success Chance</span>
              <span className="text-forge-cyan">{chancePct}%</span>
            </div>
            <div className="h-1.5 rounded-full bg-forge-border overflow-hidden">
              <div
                className="h-full rounded-full bg-forge-cyan transition-all duration-300"
                style={{ width: `${chancePct}%` }}
              />
            </div>
          </div>
        )}

        {/* Outcome badge + note */}
        <div className="flex items-center gap-2 flex-wrap">
          {!isFuture && (
            <span
              className={[
                "inline-block font-mono text-[10px] uppercase tracking-widest px-2 py-0.5 rounded-sm border",
                outcomeColor(step.outcome),
              ].join(" ")}
            >
              {outcomeLabel(step.outcome)}
            </span>
          )}
          {step.note && (
            <span className="font-body text-xs text-forge-dim italic">{step.note}</span>
          )}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function CraftTimelineViewer({ steps, currentStep }: CraftTimelineViewerProps) {
  if (steps.length === 0) {
    return (
      <EmptyState
        title="No steps yet"
        description="Run a simulation to see the crafting timeline."
      />
    );
  }

  return (
    <div className="flex flex-col">
      {steps.map((step, idx) => (
        <TimelineStep
          key={step.stepNumber}
          step={step}
          isLast={idx === steps.length - 1}
          isCurrent={currentStep !== undefined && step.stepNumber === currentStep}
          isFuture={currentStep !== undefined && step.stepNumber > currentStep}
        />
      ))}
    </div>
  );
}

export default CraftTimelineViewer;
