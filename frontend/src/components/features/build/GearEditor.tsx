/**
 * GearEditor
 *
 * Displays all gear slots in a two-column grid, grouped by category.
 * Each slot shows the equipped item (or an empty placeholder).
 * Clicking a slot opens UniqueItemPicker for that slot.
 *
 * Gear is stored as GearSlot[] in the build — when the user equips a
 * unique item we write: { slot, item_name, rarity: "legendary", affixes: [] }
 *
 * Supported slots (from uniques.json):
 *   Armour:  helmet, body, gloves, boots, belt
 *   Access:  amulet, ring (×2), relic, catalyst
 *   Weapons: sword, axe, mace, dagger, sceptre, wand, staff, bow, two_handed_spear
 *   Off-hand: shield, quiver
 *   Idols:   idol_1x1_eterra, idol_1x3, idol_1x4, idol_2x2 (×4 each where applicable)
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

// [slot_key, display_label, emoji]
type SlotDef = [string, string, string];

// How many of each slot can be equipped simultaneously
const MULTI_SLOTS: Record<string, number> = {
  ring: 2,
  idol_2x2: 4,
  idol_1x3: 4,
  idol_1x4: 2,
  idol_1x1_eterra: 2,
};

// Grouped slot definitions for display
const SLOT_GROUPS: { label: string; slots: SlotDef[] }[] = [
  {
    label: "Armour",
    slots: [
      ["helmet",  "Helmet",      "⛑"],
      ["body",    "Body Armour", "🧥"],
      ["gloves",  "Gloves",      "🧤"],
      ["boots",   "Boots",       "👢"],
      ["belt",    "Belt",        "➰"],
    ],
  },
  {
    label: "Accessories",
    slots: [
      ["amulet",   "Amulet",    "📿"],
      ["ring",     "Ring",      "💍"],
      ["relic",    "Relic",     "🔮"],
      ["catalyst", "Catalyst",  "🔷"],
    ],
  },
  {
    label: "Weapons",
    slots: [
      ["sword",           "Sword",  "⚔"],
      ["axe",             "Axe",    "🪓"],
      ["mace",            "Mace",   "🔨"],
      ["dagger",          "Dagger", "🗡"],
      ["sceptre",         "Sceptre","🔱"],
      ["wand",            "Wand",   "🪄"],
      ["staff",           "Staff",  "🏑"],
      ["bow",             "Bow",    "🏹"],
      ["two_handed_spear","Spear",  "🔱"],
    ],
  },
  {
    label: "Off-hand",
    slots: [
      ["shield", "Shield", "🛡"],
      ["quiver", "Quiver", "🪃"],
    ],
  },
  {
    label: "Idols",
    slots: [
      ["idol_1x1_eterra", "Idol (1×1)", "🗿"],
      ["idol_1x3",        "Idol (1×3)", "🗿"],
      ["idol_1x4",        "Idol (1×4)", "🗿"],
      ["idol_2x2",        "Idol (2×2)", "🗿"],
    ],
  },
];

function buildSlotKey(slot: string, index: number) {
  return `${slot}__${index}`;
}

function parseSlotKey(key: string): { slot: string; index: number } {
  const [slot, idx] = key.split("__");
  return { slot, index: parseInt(idx ?? "0") };
}

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

function setEquipped(gear: GearSlot[], slot: string, index: number, entry: GearSlot): GearSlot[] {
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

interface SlotRowProps {
  slotKey: string;
  label: string;
  icon: string;
  equipped: GearSlot | undefined;
  onPick: () => void;
  onClear: () => void;
}

function SlotRow({ slotKey: _key, label, icon, equipped, onPick, onClear }: SlotRowProps) {
  return (
    <div className="flex items-center gap-2 rounded-sm border border-forge-border bg-forge-surface px-2.5 py-2 hover:border-forge-amber/40 transition-colors">
      <span className="text-base shrink-0 select-none">{icon}</span>
      <div className="flex-1 min-w-0">
        <div className="font-mono text-[10px] uppercase tracking-widest text-forge-dim leading-none">
          {label}
        </div>
        {equipped ? (
          <div className="font-mono text-xs text-amber-300 truncate mt-0.5">
            {equipped.item_name}
          </div>
        ) : (
          <div className="font-mono text-xs text-forge-dim/40 mt-0.5 italic">Empty</div>
        )}
      </div>
      <div className="flex gap-1.5 shrink-0">
        <button
          onClick={onPick}
          title={equipped ? "Change" : "Equip unique"}
          className="font-mono text-[11px] text-forge-dim hover:text-forge-amber transition-colors"
        >
          {equipped ? "↺" : "+"}
        </button>
        {equipped && (
          <button
            onClick={onClear}
            title="Remove"
            className="font-mono text-[11px] text-forge-dim hover:text-red-400 transition-colors"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}

export default function GearEditor({ gear, onChange }: Props) {
  const [pickerSlot, setPickerSlot] = useState<string | null>(null);

  function handleSelect(item: UniqueItem, slotKey: string) {
    const { slot, index } = parseSlotKey(slotKey);
    onChange(setEquipped(gear, slot, index, {
      slot,
      item_name: item.name,
      rarity: "legendary",
      affixes: [],
    }));
  }

  function handleClear(slotKey: string) {
    const { slot, index } = parseSlotKey(slotKey);
    onChange(clearEquipped(gear, slot, index));
  }

  const pickerSlotName = pickerSlot ? parseSlotKey(pickerSlot).slot : "";

  // Build flat row list, expanding multi-slots
  const rows: Array<{ key: string; slot: string; label: string; icon: string; index: number }> = [];
  for (const group of SLOT_GROUPS) {
    for (const [slot, baseLabel, icon] of group.slots) {
      const max = MULTI_SLOTS[slot] ?? 1;
      for (let i = 0; i < max; i++) {
        rows.push({
          key: buildSlotKey(slot, i),
          slot,
          label: max > 1 ? `${baseLabel} ${i + 1}` : baseLabel,
          icon,
          index: i,
        });
      }
    }
  }

  // Group rows by their group label for section headers
  const groupedRows: { groupLabel: string; rows: typeof rows }[] = [];
  let currentGroup = "";
  let currentRows: typeof rows = [];
  for (const row of rows) {
    const groupLabel =
      SLOT_GROUPS.find((g) => g.slots.some(([s]) => s === row.slot))?.label ?? "Other";
    if (groupLabel !== currentGroup) {
      if (currentRows.length > 0) groupedRows.push({ groupLabel: currentGroup, rows: currentRows });
      currentGroup = groupLabel;
      currentRows = [];
    }
    currentRows.push(row);
  }
  if (currentRows.length > 0) groupedRows.push({ groupLabel: currentGroup, rows: currentRows });

  const equippedCount = gear.length;

  return (
    <>
      <div className="flex flex-col gap-4">
        {equippedCount > 0 && (
          <div className="font-mono text-[10px] text-forge-dim">
            {equippedCount} item{equippedCount !== 1 ? "s" : ""} equipped
          </div>
        )}

        {groupedRows.map(({ groupLabel, rows: groupRows }) => (
          <div key={groupLabel}>
            <div className="font-mono text-[9px] uppercase tracking-widest text-forge-dim/60 mb-1.5 pl-0.5">
              {groupLabel}
            </div>
            <div className="grid grid-cols-2 gap-1.5">
              {groupRows.map(({ key, slot, label, icon, index }) => (
                <SlotRow
                  key={key}
                  slotKey={key}
                  label={label}
                  icon={icon}
                  equipped={getEquipped(gear, slot, index)}
                  onPick={() => setPickerSlot(key)}
                  onClear={() => handleClear(key)}
                />
              ))}
            </div>
          </div>
        ))}
      </div>

      {pickerSlot && (
        <UniqueItemPicker
          slot={pickerSlotName}
          onSelect={(item) => handleSelect(item, pickerSlot)}
          onClose={() => setPickerSlot(null)}
        />
      )}
    </>
  );
}
