/**
 * UniqueItemPicker
 *
 * Split-pane modal: scrollable item list (left) + preview card (right).
 * Accepts a `slot` which may be a real slot name (e.g. "helmet") or one
 * of the backend meta-categories ("weapon" | "offhand" | "idol").
 *
 * On selection calls onSelect(item) and closes.
 */

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { uniquesApi, type UniqueItem } from "@/lib/api";
import { Button } from "@/components/ui";

interface Props {
  slot: string;              // real slot name OR meta-category
  displayLabel?: string;     // shown in header, e.g. "Weapon"
  onSelect: (item: UniqueItem) => void;
  onClose: () => void;
}

const SLOT_LABEL: Record<string, string> = {
  helmet: "Helmet",
  body: "Body Armour",
  gloves: "Gloves",
  boots: "Boots",
  belt: "Belt",
  amulet: "Amulet",
  ring: "Ring",
  relic: "Relic",
  catalyst: "Catalyst",
  sword: "Sword",
  axe: "Axe",
  mace: "Mace",
  dagger: "Dagger",
  sceptre: "Sceptre",
  wand: "Wand",
  staff: "Staff",
  bow: "Bow",
  quiver: "Quiver",
  shield: "Shield",
  two_handed_spear: "Spear",
  idol_1x1_eterra: "Idol (1×1)",
  idol_1x3: "Idol (1×3)",
  idol_1x4: "Idol (1×4)",
  idol_2x2: "Idol (2×2)",
  // meta
  weapon: "Weapon",
  offhand: "Off-hand",
  idol: "Idol",
};

export default function UniqueItemPicker({ slot, displayLabel, onSelect, onClose }: Props) {
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
    return items.filter(
      (u) =>
        u.name.toLowerCase().includes(q) ||
        u.tags.some((t) => t.toLowerCase().includes(q)) ||
        u.base.toLowerCase().includes(q)
    );
  }, [items, search]);

  const preview = hovered ?? filtered[0] ?? null;
  const header = displayLabel ?? SLOT_LABEL[slot] ?? slot;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4"
      onClick={onClose}
    >
      <div
        className="relative flex w-full max-w-3xl rounded border border-forge-border bg-forge-bg shadow-2xl overflow-hidden"
        style={{ maxHeight: "88vh" }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* ── Left: list ── */}
        <div className="flex flex-col w-72 shrink-0 border-r border-forge-border">

          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-forge-border">
            <span className="font-display text-forge-amber tracking-wide">
              {header}
            </span>
            <button
              onClick={onClose}
              className="font-mono text-xs text-forge-dim hover:text-forge-text transition-colors leading-none"
            >
              ✕
            </button>
          </div>

          {/* Search */}
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

          {/* Count */}
          <div className="px-3 py-1 border-b border-forge-border/30">
            <span className="font-mono text-[10px] text-forge-dim">
              {isLoading ? "Loading…" : `${filtered.length} item${filtered.length !== 1 ? "s" : ""}`}
            </span>
          </div>

          {/* List */}
          <div className="flex-1 overflow-y-auto">
            {!isLoading && filtered.length === 0 && (
              <p className="px-4 py-3 font-mono text-xs text-forge-dim">No uniques found.</p>
            )}
            {filtered.map((item) => (
              <button
                key={item.id}
                onMouseEnter={() => setHovered(item)}
                onMouseLeave={() => setHovered(null)}
                onClick={() => { onSelect(item); onClose(); }}
                className="w-full text-left px-4 py-2.5 border-b border-forge-border/25 transition-colors hover:bg-forge-surface"
              >
                <div className="font-mono text-sm text-amber-300 leading-tight truncate">
                  {item.name}
                </div>
                <div className="font-mono text-[10px] text-forge-dim mt-0.5 flex gap-2">
                  <span>{item.base}</span>
                  {item.level_req && <span className="opacity-60">Lv {item.level_req}</span>}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* ── Right: preview ── */}
        <div className="flex-1 flex flex-col overflow-y-auto">
          {preview ? (
            <div className="p-5 flex flex-col gap-4">

              {/* Name + meta */}
              <div>
                <div className="font-display text-xl text-amber-300 leading-tight">
                  {preview.name}
                </div>
                <div className="mt-1 flex flex-wrap gap-x-3 gap-y-0.5 font-mono text-xs text-forge-dim">
                  <span>{preview.base}</span>
                  <span>·</span>
                  <span>{SLOT_LABEL[preview.slot] ?? preview.slot}</span>
                  {preview.level_req && <><span>·</span><span>Req. Lv {preview.level_req}</span></>}
                </div>
              </div>

              {/* Divider */}
              <div className="h-px bg-forge-border/50" />

              {/* Implicit */}
              {preview.implicit && (
                <div className="font-mono text-xs text-forge-text/65 italic">
                  {preview.implicit}
                </div>
              )}

              {/* Fixed affixes */}
              {preview.affixes.length > 0 && (
                <div className="flex flex-col gap-1">
                  {preview.affixes.map((a, i) => (
                    <div key={i} className="font-mono text-xs text-sky-200/80 leading-snug">
                      {a}
                    </div>
                  ))}
                </div>
              )}

              {/* Unique effects */}
              {preview.unique_effects.length > 0 && (
                <div className="rounded border border-amber-500/25 bg-amber-500/[0.04] p-3">
                  <div className="font-mono text-[9px] uppercase tracking-widest text-amber-500/80 mb-2">
                    Unique Effects
                  </div>
                  <div className="flex flex-col gap-1.5">
                    {preview.unique_effects.map((e, i) => (
                      <div key={i} className="font-body text-sm text-forge-text/85 leading-snug">
                        {e}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Lore */}
              {preview.lore && (
                <div className="pt-1 border-t border-forge-border/30">
                  <p className="font-body text-xs text-forge-dim/70 italic leading-relaxed">
                    "{preview.lore}"
                  </p>
                </div>
              )}

              {/* Tags */}
              {preview.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {preview.tags.map((t) => (
                    <span key={t} className="rounded-sm bg-forge-surface2 px-2 py-0.5 font-mono text-[10px] text-forge-dim">
                      {t}
                    </span>
                  ))}
                </div>
              )}

              {/* Equip */}
              <div className="flex justify-end pt-1">
                <Button variant="primary" size="sm" onClick={() => { onSelect(preview); onClose(); }}>
                  Equip →
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center p-8">
              <p className="font-mono text-xs text-forge-dim/50 text-center">
                Hover an item to preview
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
