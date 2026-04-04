/**
 * P22 — BaseItemSelector
 *
 * Displays a filterable grid of base items fetched from the backend API.
 * Clicking a card selects it and calls onSelect.
 */

import { useState, useMemo } from "react";
import { useBaseItems } from "@/hooks";
import type { BaseItem } from "@/pages/crafting/CraftingPage";

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface Props {
  onSelect: (item: BaseItem) => void;
  selected: BaseItem | null;
}

export default function BaseItemSelector({ onSelect, selected }: Props) {
  const { data: baseItemsRes, isLoading } = useBaseItems();
  const baseItemsRaw = baseItemsRes?.data ?? null;
  const [filter, setFilter] = useState<string>("All");

  // Flatten the API response (dict of slot -> items[]) into a flat list
  const allItems: BaseItem[] = useMemo(() => {
    if (!baseItemsRaw) return [];

    // baseItemsRaw can be either Record<string, items[]> or items[] depending on endpoint
    const items: BaseItem[] = [];
    if (Array.isArray(baseItemsRaw)) {
      for (const item of baseItemsRaw) {
        items.push({
          id: item.id ?? item.name ?? `item-${items.length}`,
          name: item.name ?? "Unknown",
          item_class: item.slot ?? item.category ?? "Other",
          forging_potential: item.forging_potential ?? item.fp ?? 50,
        });
      }
    } else if (typeof baseItemsRaw === "object") {
      for (const [slot, slotItems] of Object.entries(baseItemsRaw)) {
        if (!Array.isArray(slotItems)) continue;
        for (const item of slotItems) {
          items.push({
            id: item.id ?? item.name ?? `${slot}-${items.length}`,
            name: item.name ?? "Unknown",
            item_class: slot.charAt(0).toUpperCase() + slot.slice(1),
            forging_potential: item.forging_potential ?? item.fp ?? 50,
          });
        }
      }
    }
    return items;
  }, [baseItemsRaw]);

  // Available filter categories
  const categories = useMemo(() => {
    const cats = new Set(allItems.map((i) => i.item_class));
    return ["All", ...Array.from(cats).sort()];
  }, [allItems]);

  const visible =
    filter === "All" ? allItems : allItems.filter((i) => i.item_class === filter);

  return (
    <div className="rounded-lg border border-[#2a3050] bg-[#10152a] p-4 space-y-3">
      <h2 className="font-display text-sm font-semibold text-[#f5a623] uppercase tracking-wider">
        Base Item
      </h2>

      {isLoading ? (
        <div className="text-xs text-gray-500 py-4 text-center">Loading base items...</div>
      ) : (
        <>
          {/* Class filter */}
          <div className="flex flex-wrap gap-1">
            {categories.map((cls) => (
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
          <div className="grid grid-cols-2 gap-2 max-h-80 overflow-y-auto">
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
            <p className="text-xs text-gray-500 text-center py-4">No items in this category.</p>
          )}
        </>
      )}
    </div>
  );
}
