/**
 * P24 — CraftSequenceViewer
 *
 * Renders the ordered list of crafting steps returned by the optimizer.
 * Shows a loading placeholder while the simulation is running.
 */

import type { CraftStep } from "@/pages/crafting/CraftingPage";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function stepLabel(step: CraftStep, index: number): { icon: string; text: string } {
  const type = step.action_type.toLowerCase();

  switch (type) {
    case "add_affix":
      return { icon: "➕", text: `Add affix: ${step.new_affix_id ?? "—"}` };
    case "upgrade_affix":
      return { icon: "⬆", text: `Upgrade: ${step.target_affix_id ?? "—"}` };
    case "remove_affix":
      return { icon: "➖", text: `Remove: ${step.target_affix_id ?? "—"}` };
    case "apply_glyph":
      return { icon: "✨", text: "Apply Glyph" };
    case "apply_rune":
      return { icon: "🔮", text: "Apply Rune" };
    default:
      return { icon: "•", text: `${step.action_type} (step ${index + 1})` };
  }
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface Props {
  steps: CraftStep[];
  isLoading: boolean;
}

export default function CraftSequenceViewer({ steps, isLoading }: Props) {
  return (
    <div className="rounded-lg border border-[#2a3050] bg-[#10152a] p-4 space-y-3">
      <h2 className="font-display text-sm font-semibold text-[#f5a623] uppercase tracking-wider">
        Optimal Craft Sequence
      </h2>

      {isLoading ? (
        <div className="flex items-center gap-2 py-6 justify-center text-[#22d3ee] text-sm">
          <span className="animate-spin text-base">⟳</span>
          Calculating optimal sequence…
        </div>
      ) : steps.length === 0 ? (
        <p className="text-xs text-gray-500 text-center py-6">
          No sequence generated yet.
        </p>
      ) : (
        <>
          <div className="max-h-64 overflow-y-auto space-y-1.5 pr-1">
            {steps.map((step, i) => {
              const { icon, text } = stepLabel(step, i);
              return (
                <div
                  key={i}
                  className="flex items-center gap-2 rounded-md border border-[#2a3050] bg-[#0d1123] px-3 py-2"
                >
                  <span className="w-5 text-center text-xs text-gray-500 shrink-0">
                    {i + 1}
                  </span>
                  <span className="text-sm shrink-0">{icon}</span>
                  <span className="text-xs text-gray-200">{text}</span>
                </div>
              );
            })}
          </div>

          <div className="flex justify-end">
            <span className="rounded bg-[#f5a62322] px-2 py-0.5 text-[10px] text-[#f5a623]">
              {steps.length} step{steps.length !== 1 ? "s" : ""} total
            </span>
          </div>
        </>
      )}
    </div>
  );
}
