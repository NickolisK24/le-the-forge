/**
 * Q22 — SlotSelector
 *
 * Lets the user toggle which of the 11 LE gear slots are included in a BIS search.
 */

import type { SlotConfig } from "@/pages/bis/BisSearchPage";

// ---------------------------------------------------------------------------
// Slot metadata
// ---------------------------------------------------------------------------

const ALL_SLOTS: { slot_type: string; label: string }[] = [
  { slot_type: "helm",    label: "⛑ Helm" },
  { slot_type: "chest",   label: "🛡 Chest" },
  { slot_type: "gloves",  label: "🧤 Gloves" },
  { slot_type: "boots",   label: "👢 Boots" },
  { slot_type: "belt",    label: "🔗 Belt" },
  { slot_type: "ring1",   label: "💍 Ring 1" },
  { slot_type: "ring2",   label: "💍 Ring 2" },
  { slot_type: "amulet",  label: "📿 Amulet" },
  { slot_type: "weapon1", label: "⚔ Weapon 1" },
  { slot_type: "weapon2", label: "⚔ Weapon 2" },
  { slot_type: "offhand", label: "🗡 Off-hand" },
];

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface Props {
  slots: SlotConfig[];
  onChange: (slots: SlotConfig[]) => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function SlotSelector({ slots, onChange }: Props) {
  const enabledCount = slots.filter((s) => s.enabled).length;

  function toggle(slot_type: string) {
    onChange(
      slots.map((s) =>
        s.slot_type === slot_type ? { ...s, enabled: !s.enabled } : s
      )
    );
  }

  function enableAll() {
    onChange(slots.map((s) => ({ ...s, enabled: true })));
  }

  function disableAll() {
    onChange(slots.map((s) => ({ ...s, enabled: false })));
  }

  return (
    <div className="rounded-lg border border-forge-border bg-forge-surface p-4">
      {/* Header */}
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-forge-accent">
          Gear Slots
        </h2>
        <span className="rounded-full bg-[#1a2040] px-2 py-0.5 text-xs font-medium text-[#f5a623]">
          {enabledCount} / {ALL_SLOTS.length} slots
        </span>
      </div>

      {/* Slot list */}
      <div className="grid grid-cols-2 gap-1.5 sm:grid-cols-1">
        {ALL_SLOTS.map(({ slot_type, label }) => {
          const slotCfg = slots.find((s) => s.slot_type === slot_type);
          const enabled = slotCfg?.enabled ?? false;

          return (
            <label
              key={slot_type}
              className={`flex cursor-pointer items-center gap-2 rounded px-2 py-1.5 text-sm transition-colors
                ${enabled
                  ? "bg-[#1e2840] text-forge-text"
                  : "text-forge-muted hover:bg-[#161c30]"
                }`}
            >
              <input
                type="checkbox"
                checked={enabled}
                onChange={() => toggle(slot_type)}
                className="h-3.5 w-3.5 rounded border-forge-border accent-[#f5a623]"
              />
              {label}
            </label>
          );
        })}
      </div>

      {/* Controls */}
      <div className="mt-3 flex gap-2">
        <button
          onClick={enableAll}
          className="flex-1 rounded border border-forge-border px-2 py-1 text-xs text-forge-muted
            hover:border-[#f5a623] hover:text-[#f5a623] transition-colors"
        >
          Enable All
        </button>
        <button
          onClick={disableAll}
          className="flex-1 rounded border border-forge-border px-2 py-1 text-xs text-forge-muted
            hover:border-red-500 hover:text-red-400 transition-colors"
        >
          Disable All
        </button>
      </div>
    </div>
  );
}
