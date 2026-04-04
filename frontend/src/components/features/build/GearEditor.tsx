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

import { useState, useMemo } from "react";
import { createPortal } from "react-dom";
import { useQuery } from "@tanstack/react-query";
import type { GearSlot, AffixOnItem } from "@/types";
import { uniquesApi, refApi, type UniqueItem, type BaseItemDef } from "@/lib/api";
import ItemPicker from "./ItemPicker";

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
  readOnly?: boolean;
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
// Slot label helper (mirrors UniqueItemPicker)
// ---------------------------------------------------------------------------

const SLOT_LABEL: Record<string, string> = {
  helmet: "Helmet", body: "Body Armour", gloves: "Gloves", boots: "Boots",
  belt: "Belt", amulet: "Amulet", ring: "Ring", relic: "Relic", catalyst: "Catalyst",
  sword: "Sword", axe: "Axe", mace: "Mace", dagger: "Dagger", sceptre: "Sceptre",
  wand: "Wand", staff: "Staff", bow: "Bow", quiver: "Quiver", shield: "Shield",
  two_handed_spear: "Spear",
  idol_1x1_eterra: "Idol (1×1)", idol_1x3: "Idol (1×3)",
  idol_1x4: "Idol (1×4)", idol_2x2: "Idol (2×2)",
};

// ---------------------------------------------------------------------------
// Item tooltip
// ---------------------------------------------------------------------------

interface TooltipProps {
  itemName: string;
  /** The item's actual stored slot (e.g. "bow", "helmet", "idol_1x3") */
  itemSlot: string;
  anchorRect: DOMRect;
}

function ItemTooltip({ itemName, itemSlot, anchorRect }: TooltipProps) {
  const { data: res } = useQuery({
    queryKey: ["uniques", itemSlot],
    queryFn: () => uniquesApi.list({ slot: itemSlot }),
    staleTime: 86_400_000,
  });

  const item: UniqueItem | undefined = res?.data?.find((u) => u.name === itemName);

  const TOOLTIP_W = 272;
  const left = anchorRect.left - TOOLTIP_W - 10;
  // If not enough room on the left, show to the right
  const finalLeft = left < 8 ? anchorRect.right + 10 : left;
  const finalTop = Math.max(8, Math.min(anchorRect.top, window.innerHeight - 420));

  return createPortal(
    <div
      style={{ position: "fixed", left: finalLeft, top: finalTop, width: TOOLTIP_W, zIndex: 9999 }}
      className="pointer-events-none rounded border border-forge-border bg-forge-bg shadow-2xl"
    >
      {!item ? (
        <div className="px-4 py-3 font-mono text-xs text-forge-dim">Loading…</div>
      ) : (
        <div className="flex flex-col gap-3 p-4">

          {/* Name + meta */}
          <div>
            <div className="font-display text-base text-amber-300 leading-tight">{item.name}</div>
            <div className="mt-0.5 flex flex-wrap gap-x-2 gap-y-0 font-mono text-[10px] text-forge-dim">
              <span>{item.base}</span>
              <span>·</span>
              <span>{SLOT_LABEL[item.slot] ?? item.slot}</span>
              {item.level_req && <><span>·</span><span>Req. Lv {item.level_req}</span></>}
            </div>
          </div>

          <div className="h-px bg-forge-border/50" />

          {/* Implicit */}
          {item.implicit && (
            <div className="font-mono text-[11px] text-forge-text/65 italic">{item.implicit}</div>
          )}

          {/* Fixed affixes */}
          {(item.affixes ?? []).length > 0 && (
            <div className="flex flex-col gap-0.5">
              {(item.affixes ?? []).map((a, i) => (
                <div key={i} className="font-mono text-[11px] text-sky-200/80 leading-snug">{a}</div>
              ))}
            </div>
          )}

          {/* Unique effects */}
          {(item.unique_effects ?? []).length > 0 && (
            <div className="rounded border border-amber-500/25 bg-amber-500/[0.04] p-2.5">
              <div className="font-mono text-[9px] uppercase tracking-widest text-amber-500/80 mb-1.5">
                Unique Effects
              </div>
              <div className="flex flex-col gap-1">
                {(item.unique_effects ?? []).map((e, i) => (
                  <div key={i} className="font-body text-xs text-forge-text/85 leading-snug">{e}</div>
                ))}
              </div>
            </div>
          )}

          {/* Lore */}
          {item.lore && (
            <div className="border-t border-forge-border/30 pt-2">
              <p className="font-body text-[10px] text-forge-dim/60 italic leading-relaxed">
                "{item.lore}"
              </p>
            </div>
          )}

          {/* Tags */}
          {(item.tags ?? []).length > 0 && (
            <div className="flex flex-wrap gap-1">
              {(item.tags ?? []).map((t) => (
                <span key={t} className="rounded-sm bg-forge-surface2 px-1.5 py-0.5 font-mono text-[9px] text-forge-dim">
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>,
    document.body,
  );
}

/** True when the item is crafted (has a rarity other than "legendary"). */
function isCrafted(g: GearSlot): boolean {
  return g.rarity !== "legendary";
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface PaperSlotProps {
  def: PaperSlotDef;
  equipped: GearSlot | undefined;
  large?: boolean;
  readOnly?: boolean;
  onPick: () => void;
  onClear: () => void;
  onHoverEnter: (rect: DOMRect) => void;
  onHoverLeave: () => void;
}

function PaperSlotCell({ def, equipped, large, readOnly, onPick, onClear, onHoverEnter, onHoverLeave }: PaperSlotProps) {
  const [hovering, setHovering] = useState(false);

  return (
    <div
      style={{ gridArea: def.area }}
      className={`
        relative flex flex-col items-center justify-center rounded border
        ${readOnly ? "cursor-default" : "cursor-pointer"} select-none transition-all duration-150 overflow-hidden
        ${equipped
          ? "border-amber-500/40 bg-forge-surface shadow-[inset_0_0_12px_rgba(245,158,11,0.06)]"
          : hovering && !readOnly
            ? "border-forge-amber/35 bg-forge-surface2"
            : "border-forge-border bg-forge-surface"
        }
      `}
      onMouseEnter={(e) => {
        setHovering(true);
        if (equipped) onHoverEnter((e.currentTarget as HTMLElement).getBoundingClientRect());
      }}
      onMouseLeave={() => { setHovering(false); onHoverLeave(); }}
      onClick={readOnly ? undefined : onPick}
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
            <span className={`font-mono text-center leading-tight ${
              isCrafted(equipped) ? "text-emerald-300" : "text-amber-300"
            } ${large ? "text-xs" : "text-[10px]"}`}>
              {equipped.item_name}
            </span>
            {isCrafted(equipped) && (
              <span className="font-mono text-[8px] text-emerald-500/70 uppercase tracking-wider mt-0.5">
                {equipped.rarity} · {(equipped.affixes ?? []).length} affix{(equipped.affixes ?? []).length !== 1 ? "es" : ""}
              </span>
            )}
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

      {/* Clear button — top-right corner on hover when equipped (edit mode only) */}
      {equipped && hovering && !readOnly && (
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
  readOnly?: boolean;
  onPick: () => void;
  onClear: () => void;
  onHoverEnter: (rect: DOMRect) => void;
  onHoverLeave: () => void;
}

function IdolCell({ type: _type, label, index: _index, colSpan, rowSpan, equipped, readOnly, onPick, onClear, onHoverEnter, onHoverLeave }: IdolCellProps) {
  const [hovering, setHovering] = useState(false);

  return (
    <div
      style={{
        gridColumn: `span ${colSpan}`,
        gridRow: `span ${rowSpan}`,
        minHeight: rowSpan * 40,
      }}
      className={`
        relative flex flex-col items-center justify-center rounded border
        ${readOnly ? "cursor-default" : "cursor-pointer"}
        select-none transition-all duration-150 overflow-hidden
        ${equipped
          ? "border-amber-500/35 bg-forge-surface shadow-[inset_0_0_8px_rgba(245,158,11,0.05)]"
          : readOnly
            ? "border-forge-border/70 bg-forge-surface"
            : "border-forge-border/70 bg-forge-surface hover:border-forge-amber/25 hover:bg-forge-surface2"
        }
      `}
      onMouseEnter={(e) => {
        setHovering(true);
        if (equipped) onHoverEnter((e.currentTarget as HTMLElement).getBoundingClientRect());
      }}
      onMouseLeave={() => { setHovering(false); onHoverLeave(); }}
      onClick={readOnly ? undefined : onPick}
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

      {equipped && hovering && !readOnly && (
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
// Affix editor modal (crafted items)
// ---------------------------------------------------------------------------

interface AffixEditorProps {
  gearSlot: GearSlot;
  onSave: (updated: GearSlot) => void;
  onClose: () => void;
  onReplace: () => void;
}

const RARITY_COLOR: Record<string, string> = {
  normal:  "text-forge-text",
  magic:   "text-blue-400",
  rare:    "text-yellow-400",
  exalted: "text-emerald-400",
};

// Map GearEditor slot names → affixes.json applicable_to values
const SLOT_TO_AFFIX_SLOT: Record<string, string> = {
  body:             "chest",
  helmet:           "helm",
  sword:            "sword_1h",
  axe:              "axe_1h",
  mace:             "mace_1h",
  two_handed_spear: "spear",
  // identical names — no mapping needed for: boots, gloves, belt, amulet, ring,
  // relic, dagger, sceptre, wand, staff, bow, quiver, shield, catalyst
};

function AffixEditorModal({ gearSlot, onSave, onClose, onReplace }: AffixEditorProps) {
  const [affixes, setAffixes] = useState<AffixOnItem[]>(gearSlot.affixes ?? []);
  const [addingAffix, setAddingAffix] = useState(false);
  const [newAffixName, setNewAffixName] = useState("");
  const [newAffixTier, setNewAffixTier] = useState(5);
  const [newAffixSealed, setNewAffixSealed] = useState(false);

  const affixSlot = SLOT_TO_AFFIX_SLOT[gearSlot.slot] ?? gearSlot.slot;
  const { data: affixRes } = useQuery({
    queryKey: ["affixes", affixSlot],
    queryFn: () => refApi.affixes({ slot: affixSlot }),
    staleTime: 86_400_000,
  });
  const availableAffixes = useMemo(
    () => (affixRes?.data ?? []).map((a) => a.name),
    [affixRes]
  );

  const maxTierForAffix = useMemo(() => {
    if (!newAffixName) return 5;
    const found = (affixRes?.data ?? []).find((a) => a.name === newAffixName);
    return found ? Math.max(...found.tiers.map((t) => t.tier)) : 5;
  }, [newAffixName, affixRes]);

  function addAffix() {
    if (!newAffixName) return;
    setAffixes((prev) => [...prev, { name: newAffixName, tier: newAffixTier, sealed: newAffixSealed }]);
    setNewAffixName("");
    setNewAffixTier(5);
    setNewAffixSealed(false);
    setAddingAffix(false);
  }

  function removeAffix(idx: number) {
    setAffixes((prev) => prev.filter((_, i) => i !== idx));
  }

  const rarityColor = RARITY_COLOR[gearSlot.rarity ?? "normal"] ?? "text-forge-text";

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded border border-forge-border bg-forge-bg shadow-2xl flex flex-col overflow-hidden"
        style={{ maxHeight: "80vh" }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-forge-border shrink-0">
          <div>
            <div className={`font-display text-base ${rarityColor} leading-tight`}>{gearSlot.item_name}</div>
            <div className="font-mono text-[10px] text-forge-dim capitalize">{gearSlot.rarity} · {SLOT_LABEL[gearSlot.slot] ?? gearSlot.slot}</div>
          </div>
          <div className="flex gap-2 items-center">
            <button
              onClick={onReplace}
              className="font-mono text-[10px] text-forge-dim hover:text-forge-text border border-forge-border px-2 py-0.5 rounded-sm transition-colors"
            >
              Swap
            </button>
            <button onClick={onClose} className="font-mono text-xs text-forge-dim hover:text-forge-text">✕</button>
          </div>
        </div>

        {/* Affixes list */}
        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-2">
          {affixes.length === 0 && (
            <p className="font-mono text-xs text-forge-dim/50 text-center py-4">No affixes. Add up to 4 (2 prefix + 2 suffix).</p>
          )}
          {affixes.map((a, i) => (
            <div key={i} className="flex items-center gap-2 rounded border border-forge-border bg-forge-surface px-3 py-2">
              <div className="flex-1">
                <div className="font-mono text-xs text-sky-200/85 leading-tight">{a.name}</div>
                <div className="font-mono text-[10px] text-forge-dim mt-0.5 flex gap-2">
                  <span>T{a.tier}</span>
                  {a.sealed && <span className="text-amber-400/70">sealed</span>}
                </div>
              </div>
              <button
                onClick={() => removeAffix(i)}
                className="font-mono text-[10px] text-forge-dim/50 hover:text-red-400 transition-colors px-1"
              >
                ✕
              </button>
            </div>
          ))}

          {/* Add affix form */}
          {addingAffix ? (
            <div className="rounded border border-forge-border bg-forge-surface p-3 flex flex-col gap-2 mt-1">
              <select
                value={newAffixName}
                onChange={(e) => { setNewAffixName(e.target.value); setNewAffixTier(5); }}
                className="w-full rounded-sm border border-forge-border bg-forge-surface2 px-2 py-1.5 font-body text-xs text-forge-text outline-none focus:border-forge-amber/60"
              >
                <option value="">Select affix…</option>
                {availableAffixes.map((n) => (
                  <option key={n} value={n}>{n}</option>
                ))}
              </select>
              <div className="flex items-center gap-3">
                <label className="font-mono text-[10px] text-forge-dim shrink-0">
                  Tier {newAffixTier}
                </label>
                <input
                  type="range"
                  min={1}
                  max={maxTierForAffix}
                  value={newAffixTier}
                  onChange={(e) => setNewAffixTier(Number(e.target.value))}
                  className="flex-1 accent-forge-amber"
                />
                <label className="flex items-center gap-1 font-mono text-[10px] text-forge-dim cursor-pointer">
                  <input
                    type="checkbox"
                    checked={newAffixSealed}
                    onChange={(e) => setNewAffixSealed(e.target.checked)}
                    className="accent-forge-amber"
                  />
                  Sealed
                </label>
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => setAddingAffix(false)}
                  className="font-mono text-[10px] text-forge-dim hover:text-forge-text px-2 py-1"
                >
                  Cancel
                </button>
                <button
                  onClick={addAffix}
                  disabled={!newAffixName}
                  className="font-mono text-[10px] text-forge-amber border border-forge-amber/50 rounded-sm px-3 py-1 hover:bg-forge-amber/10 transition-colors disabled:opacity-40"
                >
                  Add
                </button>
              </div>
            </div>
          ) : affixes.length < 4 ? (
            <button
              onClick={() => setAddingAffix(true)}
              className="font-mono text-xs text-forge-dim/60 hover:text-forge-amber border border-dashed border-forge-border/50 hover:border-forge-amber/40 rounded px-3 py-2 transition-colors mt-1"
            >
              + Add Affix
            </button>
          ) : null}
        </div>

        {/* Footer */}
        <div className="flex gap-2 justify-end px-4 py-3 border-t border-forge-border shrink-0">
          <button onClick={onClose} className="font-mono text-xs text-forge-dim hover:text-forge-text px-3 py-1.5">
            Cancel
          </button>
          <button
            onClick={() => onSave({ ...gearSlot, affixes })}
            className="font-mono text-xs text-forge-amber border border-forge-amber/50 rounded-sm px-4 py-1.5 hover:bg-forge-amber/10 transition-colors"
          >
            Save Affixes
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function GearEditor({ gear, onChange, readOnly }: Props) {
  const [tab, setTab] = useState<TabId>("equipment");
  const [activePicker, setActivePicker] = useState<{ slot: string; label: string; gearKey: string } | null>(null);
  const [tooltip, setTooltip] = useState<{ name: string; slot: string; rect: DOMRect } | null>(null);
  const [affixEditor, setAffixEditor] = useState<{ gearSlot: GearSlot; storeSlots: Set<string> | null } | null>(null);

  // ---- Equip unique handler ----
  function handleEquipUnique(item: UniqueItem, gearKey: string, storeSlots: Set<string> | null) {
    const [slotBase, idxStr] = gearKey.split("__");
    const occurrence = parseInt(idxStr ?? "0");
    let next = gear;
    if (storeSlots) next = next.filter((g) => !storeSlots.has(g.slot));
    const actualSlot = storeSlots ? item.slot : slotBase;
    next = upsertGear(next, { slot: actualSlot, item_name: item.name, rarity: "legendary", affixes: [] }, occurrence);
    onChange(next);
  }

  // ---- Equip crafted base handler ----
  function handleEquipCrafted(
    base: BaseItemDef,
    actualSlot: string,
    rarity: string,
    gearKey: string,
    storeSlots: Set<string> | null,
  ) {
    const [slotBase, idxStr] = gearKey.split("__");
    const occurrence = parseInt(idxStr ?? "0");
    let next = gear;
    if (storeSlots) next = next.filter((g) => !storeSlots.has(g.slot));
    const slot = storeSlots ? actualSlot : slotBase;
    next = upsertGear(next, { slot, item_name: base.name, rarity, affixes: [] }, occurrence);
    onChange(next);
  }

  // ---- Save affixes from the inline editor ----
  function handleSaveAffixes(updatedSlot: GearSlot, storeSlots: Set<string> | null) {
    let next: GearSlot[];
    if (storeSlots) {
      next = gear.map((g) => (storeSlots.has(g.slot) && g.item_name === updatedSlot.item_name ? updatedSlot : g));
    } else {
      next = gear.map((g) => (g.slot === updatedSlot.slot && g.item_name === updatedSlot.item_name ? updatedSlot : g));
    }
    onChange(next);
    setAffixEditor(null);
  }

  // ---- Clear handler ----
  function handleClear(def: PaperSlotDef) {
    const [slotBase, idxStr] = def.gearKey.split("__");
    const occurrence = parseInt(idxStr ?? "0");
    if (def.storeSlots) {
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
          {PAPER_SLOTS.map((def) => {
            const eq = def.findEquipped(gear);
            const equipped_crafted = eq && isCrafted(eq);
            return (
              <PaperSlotCell
                key={def.gearKey}
                def={def}
                equipped={eq}
                large={["weapon", "body", "offhand"].includes(def.area)}
                readOnly={readOnly}
                onPick={() => {
                  if (equipped_crafted && !readOnly) {
                    // Crafted item: open affix editor on click
                    setAffixEditor({ gearSlot: eq!, storeSlots: def.storeSlots });
                  } else {
                    setActivePicker({ slot: def.pickerSlot, label: def.label, gearKey: def.gearKey });
                  }
                }}
                onClear={() => handleClear(def)}
                onHoverEnter={(rect) => eq && !equipped_crafted && setTooltip({ name: eq.item_name!, slot: eq.slot, rect })}
                onHoverLeave={() => setTooltip(null)}
              />
            );
          })}
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
              Array.from({ length: def.count }, (_, i) => {
                const eq = getGear(gear, def.type, i);
                return (
                  <IdolCell
                    key={`${def.type}__${i}`}
                    type={def.type}
                    label={`${def.label} · ${i + 1}`}
                    index={i}
                    colSpan={def.colSpan}
                    rowSpan={def.rowSpan}
                    equipped={eq}
                    readOnly={readOnly}
                    onPick={() =>
                      setActivePicker({
                        slot: "idol",
                        label: `Idol ${def.label}`,
                        gearKey: `${def.type}__${i}`,
                      })
                    }
                    onClear={() => handleIdolClear(def.type, i)}
                    onHoverEnter={(rect) => eq && setTooltip({ name: eq.item_name, slot: eq.slot, rect })}
                    onHoverLeave={() => setTooltip(null)}
                  />
                );
              })
            )}
          </div>
        </div>
      )}

      {/* ── Hover tooltip ── */}
      {tooltip && (
        <ItemTooltip
          itemName={tooltip.name}
          itemSlot={tooltip.slot}
          anchorRect={tooltip.rect}
        />
      )}

      {/* ── Item picker modal (edit mode only) ── */}
      {activePicker && !readOnly && (
        <ItemPicker
          slot={activePicker.slot}
          displayLabel={activePicker.label}
          onSelectUnique={(item) => {
            const def = PAPER_SLOTS.find((d) => d.gearKey === activePicker.gearKey);
            handleEquipUnique(item, activePicker.gearKey, def?.storeSlots ?? null);
            setActivePicker(null);
          }}
          onSelectCrafted={(base, actualSlot, rarity) => {
            const def = PAPER_SLOTS.find((d) => d.gearKey === activePicker.gearKey);
            handleEquipCrafted(base, actualSlot, rarity, activePicker.gearKey, def?.storeSlots ?? null);
            setActivePicker(null);
          }}
          onClose={() => setActivePicker(null)}
        />
      )}

      {/* ── Affix editor modal for crafted items ── */}
      {affixEditor && !readOnly && (
        <AffixEditorModal
          gearSlot={affixEditor.gearSlot}
          onSave={(updated) => handleSaveAffixes(updated, affixEditor.storeSlots)}
          onClose={() => setAffixEditor(null)}
          onReplace={() => {
            // Open picker to swap this crafted item out
            const def = PAPER_SLOTS.find((d) => {
              const eq = d.findEquipped(gear);
              return eq?.item_name === affixEditor.gearSlot.item_name && eq?.slot === affixEditor.gearSlot.slot;
            });
            setAffixEditor(null);
            if (def) setActivePicker({ slot: def.pickerSlot, label: def.label, gearKey: def.gearKey });
          }}
        />
      )}
    </div>
  );
}
