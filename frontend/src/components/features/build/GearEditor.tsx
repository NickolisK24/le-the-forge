/**
 * GearEditor
 *
 * Displays all 18 gear slots in a two-column grid.
 * Each slot shows the equipped item (or an empty placeholder).
 * Clicking a slot opens UniqueItemPicker for that slot.
 *
 * Gear is stored as GearSlot[] in the build — when the user equips a
 * unique item we write: { slot, item_name, rarity: "legendary", affixes: [] }
 */

import { useState } from "react";
import type { GearSlot } from "@/types";
import type { UniqueItem } from "@/lib/api";
import UniqueItemPicker from "./UniqueItemPicker";

interface Props {
  gear: GearSlot[];
  characterClass?: string;
  onChange: (gear: GearSlot[]) => void;
}

// Ordered pairs: [slot, display label, emoji icon]
const GEAR_SLOTS: [string, string, string][] = [
  ["helmet",  "Helmet",       "⛑"],
  ["body",    "Body",         "🧥"],
  ["gloves",  "Gloves",       "🧤"],
  ["boots",   "Boots",        "👢"],
  ["belt",    "Belt",         "➰"],
  ["amulet",  "Amulet",       "📿"],
  ["ring",    "Ring (L)",     "💍"],
  ["ring",    "Ring (R)",     "💍"],
  ["relic",   "Relic",        "🔮"],
  ["sword",   "Weapon",       "⚔"],
  ["shield",  "Off-hand",     "🛡"],
  ["helmet",  "Helmet 2",     "⛑"],   // intentionally hidden if duplicate
];

// Canonical ordered slots we actually render (no duplicates, 2-column grid)
const SLOT_ORDER: [string, string, string][] = [
  ["helmet",  "Helmet",      "⛑"],
  ["body",    "Body Armour", "🧥"],
  ["gloves",  "Gloves",      "🧤"],
  ["boots",   "Boots",       "👢"],
  ["belt",    "Belt",        "➰"],
  ["amulet",  "Amulet",      "📿"],
  ["ring",    "Ring",        "💍"],
  ["relic",   "Relic",       "🔮"],
  ["sword",   "Weapon",      "⚔"],
  ["shield",  "Off-hand",    "🛡"],
  ["quiver",  "Quiver",      "🪃"],
  ["bow",     "Bow",         "🏹"],
  ["axe",     "Axe",         "🪓"],
  ["mace",    "Mace",        "🔨"],
  ["dagger",  "Dagger",      "🗡"],
  ["sceptre", "Sceptre",     "🔱"],
  ["wand",    "Wand",        "🪄"],
  ["staff",   "Staff",       "🪄"],
];

// Unique slot keys that can have multiple (ring can be worn twice)
const MULTI_SLOTS: Record<string, number> = { ring: 2 };

function buildSlotKey(slot: string, index: number) {
  return `${slot}__${index}`;
}

function parseSlotKey(key: string): { slot: string; index: number } {
  const [slot, idx] = key.split("__");
  return { slot, index: parseInt(idx ?? "0") };
}

/** Find a GearSlot entry in the array matching slot and occurrence index. */
function getEquipped(gear: GearSlot[], slot: string, index: number): GearSlot | undefined {
  let count = 0;
  for (const g of gear) {
    if (g.slot === slot) {
      if (count === index) return g;
      count++;
    }
  }
  return undefined;
}

/** Replace or insert a gear slot entry (by slot + occurrence). */
function setEquipped(gear: GearSlot[], slot: string, index: number, entry: GearSlot): GearSlot[] {
  // Collect all entries for this slot
  let occurrence = 0;
  let replaced = false;
  const result: GearSlot[] = gear.map((g) => {
    if (g.slot === slot) {
      if (occurrence === index) {
        occurrence++;
        replaced = true;
        return entry;
      }
      occurrence++;
    }
    return g;
  });
  if (!replaced) result.push(entry);
  return result;
}

/** Remove a gear slot entry. */
function clearEquipped(gear: GearSlot[], slot: string, index: number): GearSlot[] {
  let occurrence = 0;
  return gear.filter((g) => {
    if (g.slot === slot) {
      if (occurrence === index) {
        occurrence++;
        return false;
      }
      occurrence++;
    }
    return true;
  });
}

export default function GearEditor({ gear, characterClass, onChange }: Props) {
  const [pickerSlot, setPickerSlot] = useState<string | null>(null); // slotKey like "ring__1"

  // Build the list of rendered slot rows
  const rows: Array<{ key: string; slot: string; label: string; icon: string; index: number }> = [];
  const seenSlots: Record<string, number> = {};
  for (const [slot, label, icon] of SLOT_ORDER) {
    const idx = seenSlots[slot] ?? 0;
    seenSlots[slot] = idx + 1;
    const max = MULTI_SLOTS[slot] ?? 1;
    if (idx < max) {
      rows.push({
        key: buildSlotKey(slot, idx),
        slot,
        label: max > 1 ? `${label} ${idx + 1}` : label,
        icon,
        index: idx,
      });
    }
  }

  function handleSelect(item: UniqueItem, slotKey: string) {
    const { slot, index } = parseSlotKey(slotKey);
    const entry: GearSlot = {
      slot,
      item_name: item.name,
      rarity: "legendary",
      affixes: [],  // unique affixes are fixed — no craftable affixes
    };
    onChange(setEquipped(gear, slot, index, entry));
  }

  function handleClear(slotKey: string) {
    const { slot, index } = parseSlotKey(slotKey);
    onChange(clearEquipped(gear, slot, index));
  }

  const { slot: pickerSlotName } = pickerSlot
    ? parseSlotKey(pickerSlot)
    : { slot: "" };

  return (
    <>
      <div className="grid grid-cols-2 gap-1.5">
        {rows.map(({ key, slot, label, icon, index }) => {
          const equipped = getEquipped(gear, slot, index);
          return (
            <div
              key={key}
              className="group flex items-center gap-2 rounded-sm border border-forge-border bg-forge-surface px-2.5 py-2 transition-colors hover:border-forge-amber/40"
            >
              {/* Slot icon + label */}
              <span className="text-base shrink-0" title={label}>{icon}</span>
              <div className="flex-1 min-w-0">
                <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim leading-none">
                  {label}
                </div>
                {equipped ? (
                  <div className="font-mono text-xs text-amber-300 truncate mt-0.5">
                    {equipped.item_name}
                  </div>
                ) : (
                  <div className="font-mono text-xs text-forge-dim/50 mt-0.5 italic">
                    Empty
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-1 shrink-0">
                <button
                  onClick={() => setPickerSlot(key)}
                  title={equipped ? "Change item" : "Equip unique"}
                  className="font-mono text-[10px] text-forge-dim hover:text-forge-amber transition-colors"
                >
                  {equipped ? "↺" : "+"}
                </button>
                {equipped && (
                  <button
                    onClick={() => handleClear(key)}
                    title="Remove item"
                    className="font-mono text-[10px] text-forge-dim hover:text-red-400 transition-colors"
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {pickerSlot && (
        <UniqueItemPicker
          slot={pickerSlotName}
          characterClass={characterClass}
          onSelect={(item) => handleSelect(item, pickerSlot)}
          onClose={() => setPickerSlot(null)}
        />
      )}
    </>
  );
}
