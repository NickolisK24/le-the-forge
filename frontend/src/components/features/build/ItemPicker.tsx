/**
 * ItemPicker — unified item selection modal.
 *
 * Two tabs:
 *   Unique  — filters uniques.json by slot (existing UniqueItemPicker logic)
 *   Crafted — selects a named base item from base_items.json and a rarity
 *
 * For meta-slot keys ("weapon", "offhand") the Crafted tab fetches all
 * sub-slot categories and merges the results.
 */

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { uniquesApi, refApi, type UniqueItem, type BaseItemDef } from "@/lib/api";
import { Button } from "@/components/ui";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const WEAPON_SLOTS  = ["sword","axe","mace","dagger","sceptre","wand","staff","bow","two_handed_spear"];
const OFFHAND_SLOTS = ["shield","quiver","catalyst"];

const SLOT_LABEL: Record<string, string> = {
  helmet: "Helmet", body: "Body Armour", gloves: "Gloves", boots: "Boots",
  belt: "Belt", amulet: "Amulet", ring: "Ring", relic: "Relic", catalyst: "Catalyst",
  sword: "Sword", axe: "Axe", mace: "Mace", dagger: "Dagger", sceptre: "Sceptre",
  wand: "Wand", staff: "Staff", bow: "Bow", quiver: "Quiver", shield: "Shield",
  two_handed_spear: "Spear",
  idol_1x1_eterra: "Idol (1×1)", idol_1x3: "Idol (1×3)",
  idol_1x4: "Idol (1×4)", idol_2x2: "Idol (2×2)",
  weapon: "Weapon", offhand: "Off-hand", idol: "Idol",
};

const CRAFTED_RARITIES = [
  { value: "normal",  label: "Normal",  color: "text-forge-text" },
  { value: "magic",   label: "Magic",   color: "text-blue-400" },
  { value: "rare",    label: "Rare",    color: "text-yellow-400" },
  { value: "exalted", label: "Exalted", color: "text-emerald-400" },
];

/** Resolve which slot categories to fetch base items for. */
function resolveCraftedSlots(slot: string): string[] {
  if (slot === "weapon")  return WEAPON_SLOTS;
  if (slot === "offhand") return OFFHAND_SLOTS;
  if (slot === "idol")    return [];  // idol uniques only
  return [slot];
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface Props {
  slot: string;
  displayLabel?: string;
  onSelectUnique: (item: UniqueItem) => void;
  onSelectCrafted: (base: BaseItemDef, actualSlot: string, rarity: string) => void;
  onClose: () => void;
}

// ---------------------------------------------------------------------------
// Unique tab
// ---------------------------------------------------------------------------

function UniqueTab({ slot, onSelect }: { slot: string; onSelect: (item: UniqueItem) => void }) {
  const [search, setSearch] = useState("");
  const [hovered, setHovered] = useState<UniqueItem | null>(null);

  const { data: res, isLoading } = useQuery({
    queryKey: ["uniques", slot],
    queryFn: () => uniquesApi.list({ slot }),
    staleTime: 86_400_000,
  });
  const items: UniqueItem[] = res?.data ?? [];

  const filtered = useMemo(() => {
    if (!search.trim()) return items;
    const q = search.toLowerCase();
    return items.filter((u) =>
      (u.name ?? "").toLowerCase().includes(q) ||
      (u.base ?? "").toLowerCase().includes(q) ||
      (u.tags ?? []).some((t) => (t ?? "").toLowerCase().includes(q))
    );
  }, [items, search]);

  const preview = hovered ?? filtered[0] ?? null;

  return (
    <div className="flex flex-1 overflow-hidden">
      {/* List */}
      <div className="flex flex-col w-64 shrink-0 border-r border-forge-border overflow-hidden">
        <div className="px-3 py-2 border-b border-forge-border">
          <input
            autoFocus
            type="text"
            placeholder="Search name, tag, base…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-sm border border-forge-border bg-forge-surface2 px-2 py-1.5 font-body text-sm text-forge-text outline-none focus:border-forge-amber/60 placeholder:text-forge-dim/50"
          />
        </div>
        <div className="px-3 py-1 border-b border-forge-border/30">
          <span className="font-mono text-[10px] text-forge-dim">
            {isLoading ? "Loading…" : `${filtered.length} item${filtered.length !== 1 ? "s" : ""}`}
          </span>
        </div>
        <div className="flex-1 overflow-y-auto">
          {filtered.map((item) => (
            <button
              key={item.id}
              onMouseEnter={() => setHovered(item)}
              onMouseLeave={() => setHovered(null)}
              onClick={() => onSelect(item)}
              className="w-full text-left px-4 py-2.5 border-b border-forge-border/25 transition-colors hover:bg-forge-surface"
            >
              <div className="font-mono text-sm text-amber-300 leading-tight truncate">{item.name}</div>
              <div className="font-mono text-[10px] text-forge-dim mt-0.5 flex gap-2">
                <span>{item.base}</span>
                {item.level_req && <span className="opacity-60">Lv {item.level_req}</span>}
              </div>
            </button>
          ))}
          {!isLoading && filtered.length === 0 && (
            <p className="px-4 py-3 font-mono text-xs text-forge-dim">No uniques found.</p>
          )}
        </div>
      </div>

      {/* Preview */}
      <div className="flex-1 overflow-y-auto">
        {preview ? (
          <div className="p-5 flex flex-col gap-4">
            <div>
              <div className="font-display text-xl text-amber-300 leading-tight">{preview.name}</div>
              <div className="mt-1 flex flex-wrap gap-x-3 font-mono text-xs text-forge-dim">
                <span>{preview.base}</span>
                <span>·</span>
                <span>{SLOT_LABEL[preview.slot] ?? preview.slot}</span>
                {preview.level_req && <><span>·</span><span>Req. Lv {preview.level_req}</span></>}
              </div>
            </div>
            <div className="h-px bg-forge-border/50" />
            {preview.implicit && (
              <div className="font-mono text-xs text-forge-text/65 italic">{preview.implicit}</div>
            )}
            {(preview.affixes ?? []).length > 0 && (
              <div className="flex flex-col gap-1">
                {(preview.affixes ?? []).map((a, i) => (
                  <div key={i} className="font-mono text-xs text-sky-200/80 leading-snug">{a}</div>
                ))}
              </div>
            )}
            {(preview.unique_effects ?? []).length > 0 && (
              <div className="rounded border border-amber-500/25 bg-amber-500/[0.04] p-3">
                <div className="font-mono text-[9px] uppercase tracking-widest text-amber-500/80 mb-2">Unique Effects</div>
                <div className="flex flex-col gap-1.5">
                  {(preview.unique_effects ?? []).map((e, i) => (
                    <div key={i} className="font-body text-sm text-forge-text/85 leading-snug">{e}</div>
                  ))}
                </div>
              </div>
            )}
            {preview.lore && (
              <div className="pt-1 border-t border-forge-border/30">
                <p className="font-body text-xs text-forge-dim/70 italic leading-relaxed">"{preview.lore}"</p>
              </div>
            )}
            {(preview.tags ?? []).length > 0 && (
              <div className="flex flex-wrap gap-1">
                {(preview.tags ?? []).map((t) => (
                  <span key={t} className="rounded-sm bg-forge-surface2 px-2 py-0.5 font-mono text-[10px] text-forge-dim">{t}</span>
                ))}
              </div>
            )}
            <div className="flex justify-end pt-1">
              <Button variant="primary" size="sm" onClick={() => onSelect(preview)}>Equip →</Button>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center p-8 h-full">
            <p className="font-mono text-xs text-forge-dim/50 text-center">Hover an item to preview</p>
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Crafted tab
// ---------------------------------------------------------------------------

interface BaseItemWithSlot extends BaseItemDef { slot: string }

function CraftedTab({ pickerSlot, onSelect }: {
  pickerSlot: string;
  onSelect: (base: BaseItemDef, actualSlot: string, rarity: string) => void;
}) {
  const [search, setSearch] = useState("");
  const [hovered, setHovered] = useState<BaseItemWithSlot | null>(null);
  const [rarity, setRarity] = useState<string>("exalted");

  const craftedSlots = resolveCraftedSlots(pickerSlot);

  // Fetch base items for all relevant slots
  const { data: allBasesData, isLoading } = useQuery({
    queryKey: ["base-items"],
    queryFn: () => refApi.baseItems(),
    staleTime: 86_400_000,
  });

  const allItems = useMemo<BaseItemWithSlot[]>(() => {
    if (!allBasesData?.data) return [];
    const slotsToShow = craftedSlots.length > 0 ? craftedSlots : Object.keys(allBasesData.data);
    return slotsToShow.flatMap((s) =>
      (allBasesData.data[s] ?? []).map((item) => ({ ...item, slot: s }))
    );
  }, [allBasesData, craftedSlots]);

  const filtered = useMemo(() => {
    if (!search.trim()) return allItems;
    const q = search.toLowerCase();
    return allItems.filter((b) =>
      b.name.toLowerCase().includes(q) ||
      b.slot.toLowerCase().includes(q) ||
      (b.tags ?? []).some((t) => t.toLowerCase().includes(q))
    );
  }, [allItems, search]);

  const preview = hovered ?? filtered[0] ?? null;
  const rarityStyle = CRAFTED_RARITIES.find((r) => r.value === rarity) ?? CRAFTED_RARITIES[3];

  return (
    <div className="flex flex-1 overflow-hidden">
      {/* List */}
      <div className="flex flex-col w-64 shrink-0 border-r border-forge-border overflow-hidden">
        <div className="px-3 py-2 border-b border-forge-border">
          <input
            autoFocus
            type="text"
            placeholder="Search name, slot, tag…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-sm border border-forge-border bg-forge-surface2 px-2 py-1.5 font-body text-sm text-forge-text outline-none focus:border-forge-amber/60 placeholder:text-forge-dim/50"
          />
        </div>
        {/* Rarity picker */}
        <div className="px-3 py-2 border-b border-forge-border/30 flex gap-1 flex-wrap">
          {CRAFTED_RARITIES.map((r) => (
            <button
              key={r.value}
              onClick={() => setRarity(r.value)}
              className={`px-2 py-0.5 rounded-sm font-mono text-[10px] border transition-colors ${
                rarity === r.value
                  ? `border-forge-amber/60 bg-forge-amber/10 ${r.color}`
                  : "border-forge-border text-forge-dim hover:border-forge-border/60"
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
        <div className="px-3 py-1 border-b border-forge-border/30">
          <span className="font-mono text-[10px] text-forge-dim">
            {isLoading ? "Loading…" : `${filtered.length} base${filtered.length !== 1 ? "s" : ""}`}
          </span>
        </div>
        <div className="flex-1 overflow-y-auto">
          {filtered.map((item, i) => (
            <button
              key={`${item.slot}-${item.name}-${i}`}
              onMouseEnter={() => setHovered(item)}
              onMouseLeave={() => setHovered(null)}
              onClick={() => onSelect(item, item.slot, rarity)}
              className="w-full text-left px-4 py-2.5 border-b border-forge-border/25 transition-colors hover:bg-forge-surface"
            >
              <div className={`font-mono text-sm leading-tight truncate ${rarityStyle.color}`}>{item.name}</div>
              <div className="font-mono text-[10px] text-forge-dim mt-0.5 flex gap-2">
                <span>{SLOT_LABEL[item.slot] ?? item.slot}</span>
                <span className="opacity-60">Lv {item.level_req}</span>
              </div>
            </button>
          ))}
          {!isLoading && filtered.length === 0 && (
            <p className="px-4 py-3 font-mono text-xs text-forge-dim">No base items found.</p>
          )}
        </div>
      </div>

      {/* Preview */}
      <div className="flex-1 overflow-y-auto">
        {preview ? (
          <div className="p-5 flex flex-col gap-4">
            <div>
              <div className={`font-display text-xl leading-tight ${rarityStyle.color}`}>{preview.name}</div>
              <div className="mt-1 flex flex-wrap gap-x-3 font-mono text-xs text-forge-dim">
                <span>{SLOT_LABEL[preview.slot] ?? preview.slot}</span>
                <span>·</span>
                <span>Req. Lv {preview.level_req}</span>
              </div>
            </div>
            <div className="h-px bg-forge-border/50" />
            {preview.implicit && (
              <div className="font-mono text-xs text-forge-text/65 italic">{preview.implicit}</div>
            )}
            {preview.armor > 0 && (
              <div className="font-mono text-xs text-sky-200/80">{preview.armor} Base Armour</div>
            )}
            <div className="flex flex-col gap-1">
              <div className="font-mono text-[10px] text-forge-dim/60">FP Range</div>
              <div className="font-mono text-xs text-forge-text">{preview.min_fp}–{preview.max_fp}</div>
            </div>
            {(preview.tags ?? []).length > 0 && (
              <div className="flex flex-wrap gap-1">
                {(preview.tags ?? []).map((t) => (
                  <span key={t} className="rounded-sm bg-forge-surface2 px-2 py-0.5 font-mono text-[10px] text-forge-dim">{t}</span>
                ))}
              </div>
            )}
            <div className="pt-1 border-t border-forge-border/30 flex items-center justify-between gap-3">
              <span className={`font-mono text-xs ${rarityStyle.color}`}>{rarityStyle.label}</span>
              <Button variant="primary" size="sm" onClick={() => onSelect(preview, preview.slot, rarity)}>
                Equip →
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center p-8 h-full">
            <p className="font-mono text-xs text-forge-dim/50 text-center">Hover a base to preview</p>
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function ItemPicker({ slot, displayLabel, onSelectUnique, onSelectCrafted, onClose }: Props) {
  const [tab, setTab] = useState<"unique" | "crafted">("unique");
  const isIdol = slot === "idol" || slot.startsWith("idol_");
  const header = displayLabel ?? SLOT_LABEL[slot] ?? slot;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4"
      onClick={onClose}
    >
      <div
        className="relative flex flex-col w-full max-w-3xl rounded border border-forge-border bg-forge-bg shadow-2xl overflow-hidden"
        style={{ maxHeight: "88vh" }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-forge-border shrink-0">
          <span className="font-display text-forge-amber tracking-wide">{header}</span>
          <button onClick={onClose} className="font-mono text-xs text-forge-dim hover:text-forge-text transition-colors">✕</button>
        </div>

        {/* Tab bar */}
        {!isIdol && (
          <div className="flex border-b border-forge-border shrink-0">
            {(["unique", "crafted"] as const).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-5 py-2 font-mono text-xs uppercase tracking-widest border-b-2 -mb-px transition-colors ${
                  tab === t
                    ? "border-forge-amber text-forge-amber"
                    : "border-transparent text-forge-dim hover:text-forge-text"
                }`}
              >
                {t === "unique" ? "Unique Items" : "Crafted Items"}
              </button>
            ))}
          </div>
        )}

        {/* Content */}
        <div className="flex flex-1 overflow-hidden min-h-0">
          {(tab === "unique" || isIdol) && (
            <UniqueTab slot={slot} onSelect={(item) => { onSelectUnique(item); onClose(); }} />
          )}
          {tab === "crafted" && !isIdol && (
            <CraftedTab
              pickerSlot={slot}
              onSelect={(base, actualSlot, rarity) => { onSelectCrafted(base, actualSlot, rarity); onClose(); }}
            />
          )}
        </div>
      </div>
    </div>
  );
}
