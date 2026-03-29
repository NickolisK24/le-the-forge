/**
 * GearEditor — Paper-doll style gear layout
 *
 * Two tabs:
 *   Equipment — full body paper-doll (Helmet, Body, Weapon, Off-hand, etc.)
 *   Idols     — idol bag grid (1×1, 1×3, 1×4, 2×2)
 *
 * The "Weapon" and "Off-hand" slots are meta-categories that expand to all
 * weapon / off-hand slot types via the backend (?slot=weapon / ?slot=offhand).
 * The actual GearSlot stored uses the item's real slot (e.g. "bow", "shield").
 */

import { useState } from "react";
import type { GearSlot } from "@/types";
import type { UniqueItem } from "@/lib/api";
import UniqueItemPicker from "./UniqueItemPicker";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const WEAPON_SLOTS  = new Set(["sword","axe","mace","dagger","sceptre","wand","staff","bow","two_handed_spear"]);
const OFFHAND_SLOTS = new Set(["shield","quiver","catalyst"]);
const IDOL_SLOTS    = new Set(["idol_1x1_eterra","idol_1x3","idol_1x4","idol_2x2"]);

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Props {
  gear: GearSlot[];
  onChange: (gear: GearSlot[]) => void;
}

type TabId = "equipment" | "idols";

/** A slot definition for the paper-doll grid */
interface PaperSlotDef {
  /** The gear-array key — compound: slotName__index */
  gearKey:     string;
  /** CSS grid-area name */
  area:        string;
  /** Slot name to pass to the picker (may be "weapon" | "offhand" meta) */
  pickerSlot:  string;
  /** Display label */
  label:       string;
  /** Ghost icon shown at low opacity inside the slot */
  icon:        string;
  /** Lookup function — how to find this item in the gear array */
  findEquipped: (gear: GearSlot[]) => GearSlot | undefined;
  /** Slot name(s) used when storing to the gear array after pick */
  storeSlots:  Set<string> | null; // null = use item.slot directly
}

// ---------------------------------------------------------------------------
// Gear array helpers
// ---------------------------------------------------------------------------

/** Upsert a gear slot entry. Replaces the first entry matching slot+occurrence. */
function upsertGear(gear: GearSlot[], entry: GearSlot, occurrence = 0): GearSlot[] {
  let seen = 0;
  let found = false;
  const next = gear.map((g) => {
    if (g.slot === entry.slot) {
      if (seen === occurrence) { seen++; found = true; return entry; }
      seen++;
    }
    return g;
  });
  return found ? next : [...gear, entry];
}

/** Remove a gear slot entry by slot name + occurrence index. */
function removeGear(gear: GearSlot[], slot: string, occurrence = 0): GearSlot[] {
  let seen = 0;
  return gear.filter((g) => {
    if (g.slot === slot) {
      if (seen === occurrence) { seen++; return false; }
      seen++;
    }
    return true;
  });
}

/** Get gear entry by slot + occurrence. */
function getGear(gear: GearSlot[], slot: string, occurrence = 0): GearSlot | undefined {
  let seen = 0;
  for (const g of gear) {
    if (g.slot === slot) {
      if (seen === occurrence) return g;
      seen++;
    }
  }
}

/** Find any equipped item whose slot is in a Set. */
function findInSet(gear: GearSlot[], slots: Set<string>): GearSlot | undefined {
  return gear.find((g) => slots.has(g.slot));
}

// ---------------------------------------------------------------------------
// Paper-doll slot definitions
// ---------------------------------------------------------------------------
// The grid uses 3 columns:
//   ". helmet  amulet"   (helmet center, amulet top-right)
//   "weapon body offhand" (x2 rows so they're tall)
//   "weapon body offhand"
//   "ring1  belt ring2"
//   "gloves boots relic"

const PAPER_SLOTS: PaperSlotDef[] = [
  {
    gearKey: "helmet__0",
    area: "helmet",
    pickerSlot: "helmet",
    label: "Helmet",
    icon: "⛑",
    findEquipped: (g) => getGear(g, "helmet"),
    storeSlots: null,
  },
  {
    gearKey: "amulet__0",
    area: "amulet",
    pickerSlot: "amulet",
    label: "Amulet",
    icon: "📿",
    findEquipped: (g) => getGear(g, "amulet"),
    storeSlots: null,
  },
  {
    gearKey: "weapon__0",
    area: "weapon",
    pickerSlot: "weapon",            // backend meta-category
    label: "Weapon",
    icon: "⚔",
    findEquipped: (g) => findInSet(g, WEAPON_SLOTS),
    storeSlots: WEAPON_SLOTS,         // clear any weapon when replacing
  },
  {
    gearKey: "body__0",
    area: "body",
    pickerSlot: "body",
    label: "Body",
    icon: "🧥",
    findEquipped: (g) => getGear(g, "body"),
    storeSlots: null,
  },
  {
    gearKey: "offhand__0",
    area: "offhand",
    pickerSlot: "offhand",           // backend meta-category
    label: "Off-hand",
    icon: "🛡",
    findEquipped: (g) => findInSet(g, OFFHAND_SLOTS),
    storeSlots: OFFHAND_SLOTS,
  },
  {
    gearKey: "ring__0",
    area: "ring1",
    pickerSlot: "ring",
    label: "Ring",
    icon: "💍",
    findEquipped: (g) => getGear(g, "ring", 0),
    storeSlots: null,
  },
  {
    gearKey: "belt__0",
    area: "belt",
    pickerSlot: "belt",
    label: "Belt",
    icon: "➰",
    findEquipped: (g) => getGear(g, "belt"),
    storeSlots: null,
  },
  {
    gearKey: "ring__1",
    area: "ring2",
    pickerSlot: "ring",
    label: "Ring",
    icon: "💍",
    findEquipped: (g) => getGear(g, "ring", 1),
    storeSlots: null,
  },
  {
    gearKey: "gloves__0",
    area: "gloves",
    pickerSlot: "gloves",
    label: "Gloves",
    icon: "🧤",
    findEquipped: (g) => getGear(g, "gloves"),
    storeSlots: null,
  },
  {
    gearKey: "boots__0",
    area: "boots",
    pickerSlot: "boots",
    label: "Boots",
    icon: "👢",
    findEquipped: (g) => getGear(g, "boots"),
    storeSlots: null,
  },
  {
    gearKey: "relic__0",
    area: "relic",
    pickerSlot: "relic",
    label: "Relic",
    icon: "🔮",
    findEquipped: (g) => getGear(g, "relic"),
    storeSlots: null,
  },
];

// ---------------------------------------------------------------------------
// Idol slot definitions (Idols tab)
// ---------------------------------------------------------------------------

interface IdolSlotDef {
  type: string;
  label: string;
  count: number;         // how many of this type can be equipped
  colSpan: number;       // visual grid width
  rowSpan: number;       // visual grid height
}

const IDOL_DEFS: IdolSlotDef[] = [
  { type: "idol_1x1_eterra", label: "1×1",  count: 2, colSpan: 1, rowSpan: 1 },
  { type: "idol_2x2",        label: "2×2",  count: 4, colSpan: 2, rowSpan: 2 },
  { type: "idol_1x3",        label: "1×3",  count: 4, colSpan: 1, rowSpan: 3 },
  { type: "idol_1x4",        label: "1×4",  count: 2, colSpan: 1, rowSpan: 4 },
];

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface PaperSlotProps {
  def: PaperSlotDef;
  equipped: GearSlot | undefined;
  large?: boolean;
  onPick: () => void;
  onClear: () => void;
}

function PaperSlotCell({ def, equipped, large, onPick, onClear }: PaperSlotProps) {
  const [hovering, setHovering] = useState(false);

  return (
    <div
      style={{ gridArea: def.area }}
      className={`
        relative flex flex-col items-center justify-center rounded border
        cursor-pointer select-none transition-all duration-150 overflow-hidden
        ${equipped
          ? "border-amber-500/40 bg-forge-surface shadow-[inset_0_0_12px_rgba(245,158,11,0.06)]"
          : hovering
            ? "border-forge-amber/35 bg-forge-surface2"
            : "border-forge-border bg-forge-surface"
        }
      `}
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
      onClick={onPick}
    >
      {/* Ghost slot art */}
      <div
        className={`absolute inset-0 flex items-center justify-center pointer-events-none select-none transition-opacity duration-150 ${large ? "text-5xl" : "text-3xl"} ${equipped ? "opacity-[0.05]" : "opacity-[0.08]"}`}
      >
        {def.icon}
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center justify-center p-1.5 w-full">
        {equipped ? (
          <>
            <span className="font-mono text-[10px] text-forge-dim/70 uppercase tracking-widest leading-none mb-1">
              {def.label}
            </span>
            <span className={`font-mono text-center leading-tight text-amber-300 ${large ? "text-xs" : "text-[10px]"}`}>
              {equipped.item_name}
            </span>
          </>
        ) : (
          <>
            <span className="font-mono text-[9px] text-forge-dim/40 uppercase tracking-widest leading-none mb-1.5">
              {def.label}
            </span>
            <span className="font-mono text-lg text-forge-dim/20 leading-none">+</span>
          </>
        )}
      </div>

      {/* Clear button — top-right corner on hover when equipped */}
      {equipped && hovering && (
        <button
          className="absolute top-1 right-1 z-20 w-4 h-4 flex items-center justify-center rounded-sm bg-forge-bg/80 font-mono text-[9px] text-forge-dim hover:text-red-400 transition-colors"
          onClick={(e) => { e.stopPropagation(); onClear(); }}
          title="Remove"
        >
          ✕
        </button>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Idol cell
// ---------------------------------------------------------------------------

interface IdolCellProps {
  type: string;
  label: string;
  index: number;
  colSpan: number;
  rowSpan: number;
  equipped: GearSlot | undefined;
  onPick: () => void;
  onClear: () => void;
}

function IdolCell({ type: _type, label, index: _index, colSpan, rowSpan, equipped, onPick, onClear }: IdolCellProps) {
  const [hovering, setHovering] = useState(false);

  return (
    <div
      style={{
        gridColumn: `span ${colSpan}`,
        gridRow: `span ${rowSpan}`,
        minHeight: rowSpan * 40,
      }}
      className={`
        relative flex flex-col items-center justify-center rounded border cursor-pointer
        select-none transition-all duration-150 overflow-hidden
        ${equipped
          ? "border-amber-500/35 bg-forge-surface shadow-[inset_0_0_8px_rgba(245,158,11,0.05)]"
          : "border-forge-border/70 bg-forge-surface hover:border-forge-amber/25 hover:bg-forge-surface2"
        }
      `}
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
      onClick={onPick}
    >
      {/* Ghost art */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none text-2xl opacity-[0.06]">
        🗿
      </div>

      <div className="relative z-10 flex flex-col items-center justify-center p-1 w-full">
        {equipped ? (
          <>
            <span className="font-mono text-[9px] text-forge-dim/60 uppercase tracking-widest leading-none mb-1">{label}</span>
            <span className="font-mono text-[10px] text-amber-300 text-center leading-tight">{equipped.item_name}</span>
          </>
        ) : (
          <>
            <span className="font-mono text-[9px] text-forge-dim/35 uppercase tracking-widest leading-none mb-1">{label}</span>
            <span className="font-mono text-sm text-forge-dim/15 leading-none">+</span>
          </>
        )}
      </div>

      {equipped && hovering && (
        <button
          className="absolute top-0.5 right-0.5 z-20 w-3.5 h-3.5 flex items-center justify-center rounded-sm bg-forge-bg/80 font-mono text-[8px] text-forge-dim hover:text-red-400 transition-colors"
          onClick={(e) => { e.stopPropagation(); onClear(); }}
        >
          ✕
        </button>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function GearEditor({ gear, onChange }: Props) {
  const [tab, setTab] = useState<TabId>("equipment");
  const [activePicker, setActivePicker] = useState<{ slot: string; label: string; gearKey: string } | null>(null);

  // ---- Equip handler ----
  function handleEquip(item: UniqueItem, gearKey: string, storeSlots: Set<string> | null) {
    const [slotBase, idxStr] = gearKey.split("__");
    const occurrence = parseInt(idxStr ?? "0");

    // For meta-slots (weapon/offhand), remove any existing item of that category first
    let next = gear;
    if (storeSlots) {
      next = next.filter((g) => !storeSlots.has(g.slot));
    }

    // Determine actual slot to store (for ring etc, use slotBase; for weapon/offhand use item.slot)
    const actualSlot = storeSlots ? item.slot : slotBase;

    next = upsertGear(next, { slot: actualSlot, item_name: item.name, rarity: "legendary", affixes: [] }, occurrence);
    onChange(next);
  }

  // ---- Clear handler ----
  function handleClear(def: PaperSlotDef) {
    const [slotBase, idxStr] = def.gearKey.split("__");
    const occurrence = parseInt(idxStr ?? "0");

    if (def.storeSlots) {
      // Remove the actual equipped item (any slot in the meta-set)
      const equipped = def.findEquipped(gear);
      if (equipped) onChange(gear.filter((g) => g !== equipped));
    } else {
      onChange(removeGear(gear, slotBase, occurrence));
    }
  }

  function handleIdolClear(type: string, occurrence: number) {
    onChange(removeGear(gear, type, occurrence));
  }

  const equippedCount = gear.length;

  return (
    <div className="flex flex-col gap-0">
      {/* ── Tabs ── */}
      <div className="flex items-center gap-0 border-b border-forge-border mb-4">
        {(["equipment", "idols"] as TabId[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`
              px-4 py-2 font-mono text-xs uppercase tracking-widest transition-colors border-b-2 -mb-px
              ${tab === t
                ? "border-forge-amber text-forge-amber"
                : "border-transparent text-forge-dim hover:text-forge-text"
              }
            `}
          >
            {t === "equipment" ? `Equipment${equippedCount > 0 ? ` (${equippedCount})` : ""}` : "Idols"}
          </button>
        ))}
      </div>

      {/* ── Equipment tab ── */}
      {tab === "equipment" && (
        <div
          style={{
            display: "grid",
            gridTemplateAreas: `
              ".      helmet  amulet"
              "weapon body    offhand"
              "weapon body    offhand"
              "ring1  belt    ring2"
              "gloves boots   relic"
            `,
            gridTemplateColumns: "1fr 1.4fr 1fr",
            gridTemplateRows: "80px 80px 80px 60px 68px",
            gap: "6px",
          }}
        >
          {PAPER_SLOTS.map((def) => (
            <PaperSlotCell
              key={def.gearKey}
              def={def}
              equipped={def.findEquipped(gear)}
              large={["weapon", "body", "offhand"].includes(def.area)}
              onPick={() => setActivePicker({ slot: def.pickerSlot, label: def.label, gearKey: def.gearKey })}
              onClear={() => handleClear(def)}
            />
          ))}
        </div>
      )}

      {/* ── Idols tab ── */}
      {tab === "idols" && (
        <div className="flex flex-col gap-4">
          <p className="font-mono text-[10px] text-forge-dim/60">
            Click a slot to equip a unique idol.
          </p>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(5, 1fr)",
              gridAutoRows: "40px",
              gap: "4px",
            }}
          >
            {IDOL_DEFS.flatMap((def) =>
              Array.from({ length: def.count }, (_, i) => (
                <IdolCell
                  key={`${def.type}__${i}`}
                  type={def.type}
                  label={`${def.label} · ${i + 1}`}
                  index={i}
                  colSpan={def.colSpan}
                  rowSpan={def.rowSpan}
                  equipped={getGear(gear, def.type, i)}
                  onPick={() =>
                    setActivePicker({
                      slot: "idol",
                      label: `Idol ${def.label}`,
                      gearKey: `${def.type}__${i}`,
                    })
                  }
                  onClear={() => handleIdolClear(def.type, i)}
                />
              ))
            )}
          </div>
        </div>
      )}

      {/* ── Picker modal ── */}
      {activePicker && (
        <UniqueItemPicker
          slot={activePicker.slot}
          displayLabel={activePicker.label}
          onSelect={(item) => {
            const def = PAPER_SLOTS.find((d) => d.gearKey === activePicker.gearKey);
            handleEquip(item, activePicker.gearKey, def?.storeSlots ?? null);
            setActivePicker(null);
          }}
          onClose={() => setActivePicker(null)}
        />
      )}
    </div>
  );
}
