/**
 * P22 — BaseItemSelector
 *
 * Displays a filterable grid of mock base items. Clicking a card selects it
 * and calls onSelect. The selected item is highlighted with an amber border.
 */

import { useState } from "react";
import type { BaseItem } from "@/pages/crafting/CraftingPage";

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

const MOCK_ITEMS: BaseItem[] = [
  { id: "helm_001",    name: "Titan's Crown",       item_class: "Helm",   forging_potential: 80 },
  { id: "helm_002",    name: "Warden's Visage",      item_class: "Helm",   forging_potential: 65 },
  { id: "chest_001",   name: "Ironclad Hauberk",     item_class: "Chest",  forging_potential: 95 },
  { id: "chest_002",   name: "Shadowweave Tunic",    item_class: "Chest",  forging_potential: 72 },
  { id: "gloves_001",  name: "Forgemaster's Grips",  item_class: "Gloves", forging_potential: 58 },
  { id: "boots_001",   name: "Quickstep Treads",     item_class: "Boots",  forging_potential: 60 },
  { id: "belt_001",    name: "Reinforced Girdle",    item_class: "Belt",   forging_potential: 40 },
  { id: "weapon_001",  name: "Embersteel Blade",     item_class: "Weapon", forging_potential: 100 },
];

const ALL_CLASSES = ["All", "Helm", "Chest", "Gloves", "Boots", "Belt", "Weapon"] as const;

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface Props {
  onSelect: (item: BaseItem) => void;
  selected: BaseItem | null;
}

export default function BaseItemSelector({ onSelect, selected }: Props) {
  const [filter, setFilter] = useState<string>("All");

  const visible = filter === "All"
    ? MOCK_ITEMS
    : MOCK_ITEMS.filter((i) => i.item_class === filter);

  return (
    <div className="rounded-lg border border-[#2a3050] bg-[#10152a] p-4 space-y-3">
      <h2 className="font-display text-sm font-semibold text-[#f5a623] uppercase tracking-wider">
        Base Item
      </h2>

      {/* Class filter */}
      <div className="flex flex-wrap gap-1">
        {ALL_CLASSES.map((cls) => (
          <button
            key={cls}
            onClick={() => setFilter(cls)}
            className={[
              "rounded px-2 py-0.5 text-xs font-medium transition-colors",
              filter === cls
                ? "bg-[#f5a623] text-[#10152a]"
                : "bg-[#1a2035] text-gray-400 hover:text-[#f5a623]",
            ].join(" ")}
          >
            {cls}
          </button>
        ))}
      </div>

      {/* Item cards */}
      <div className="grid grid-cols-2 gap-2">
        {visible.map((item) => {
          const isSelected = selected?.id === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelect(item)}
              className={[
                "rounded-md border p-2 text-left transition-all",
                isSelected
                  ? "border-[#f5a623] bg-[#1a2035]"
                  : "border-[#2a3050] bg-[#0d1123] hover:border-[#f5a62366]",
              ].join(" ")}
            >
              <p className="text-xs font-semibold text-gray-100 truncate">{item.name}</p>
              <div className="mt-1 flex items-center justify-between">
                <span className="rounded bg-[#22d3ee22] px-1.5 py-0.5 text-[10px] text-[#22d3ee]">
                  {item.item_class}
                </span>
                <span className="text-[10px] text-gray-400">
                  FP&nbsp;
                  <span className={item.forging_potential >= 80 ? "text-[#f5a623]" : "text-gray-300"}>
                    {item.forging_potential}
                  </span>
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {visible.length === 0 && (
        <p className="text-xs text-gray-500 text-center py-4">No items in this class.</p>
      )}
    </div>
  );
}
