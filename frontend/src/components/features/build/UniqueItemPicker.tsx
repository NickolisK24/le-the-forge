/**
 * UniqueItemPicker
 *
 * Modal for browsing and selecting a unique item for a specific gear slot.
 * Fetches from GET /api/ref/uniques?slot=<slot>&class=<class>
 * and lets the user search by name.
 *
 * On selection calls onSelect(item) and closes.
 */

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { uniquesApi, type UniqueItem } from "@/lib/api";
import { Button } from "@/components/ui";

interface Props {
  slot: string;
  characterClass?: string;
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
};

const CLASS_COLOR: Record<string, string> = {
  Acolyte: "text-purple-400",
  Mage: "text-blue-400",
  Primalist: "text-green-400",
  Sentinel: "text-orange-400",
  Rogue: "text-red-400",
};

export default function UniqueItemPicker({
  slot,
  characterClass,
  onSelect,
  onClose,
}: Props) {
  const [search, setSearch] = useState("");
  const [hovered, setHovered] = useState<UniqueItem | null>(null);

  const { data: res, isLoading } = useQuery({
    queryKey: ["uniques", slot, characterClass],
    queryFn: () =>
      uniquesApi.list({
        slot,
        ...(characterClass ? { class: characterClass } : {}),
      }),
    staleTime: 86_400_000,
  });

  const items: UniqueItem[] = res?.data ?? [];

  const filtered = useMemo(() => {
    if (!search.trim()) return items;
    const q = search.toLowerCase();
    return items.filter((u) => u.name.toLowerCase().includes(q));
  }, [items, search]);

  const preview = hovered ?? filtered[0] ?? null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
      onClick={onClose}
    >
      <div
        className="relative flex w-full max-w-3xl rounded border border-forge-border bg-forge-bg shadow-2xl overflow-hidden"
        style={{ maxHeight: "90vh" }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* ---- Left panel: list ---- */}
        <div className="flex flex-col w-72 border-r border-forge-border shrink-0">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-forge-border px-4 py-3">
            <span className="font-display text-forge-amber text-base">
              {SLOT_LABEL[slot] ?? slot} — Uniques
            </span>
            <button
              onClick={onClose}
              className="font-mono text-xs text-forge-dim hover:text-forge-text transition-colors"
            >
              ✕
            </button>
          </div>

          {/* Search */}
          <div className="px-3 py-2 border-b border-forge-border">
            <input
              autoFocus
              type="text"
              placeholder="Search…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-sm border border-forge-border bg-forge-surface2 px-2 py-1.5 font-body text-sm text-forge-text outline-none focus:border-forge-amber/60"
            />
          </div>

          {/* List */}
          <div className="flex-1 overflow-y-auto">
            {isLoading && (
              <p className="px-4 py-3 font-mono text-xs text-forge-dim">
                Loading…
              </p>
            )}
            {!isLoading && filtered.length === 0 && (
              <p className="px-4 py-3 font-mono text-xs text-forge-dim">
                No uniques found for this slot.
              </p>
            )}
            {filtered.map((item) => (
              <button
                key={item.id}
                onMouseEnter={() => setHovered(item)}
                onMouseLeave={() => setHovered(null)}
                onClick={() => { onSelect(item); onClose(); }}
                className="w-full text-left px-4 py-2.5 border-b border-forge-border/40 transition-colors hover:bg-forge-surface"
              >
                <div className="font-mono text-sm text-amber-300 leading-tight">
                  {item.name}
                </div>
                <div className="font-mono text-[10px] text-forge-dim mt-0.5">
                  {item.base}
                  {item.class_req && (
                    <span className={`ml-2 ${CLASS_COLOR[item.class_req] ?? "text-forge-dim"}`}>
                      · {item.class_req}
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* ---- Right panel: preview ---- */}
        <div className="flex-1 flex flex-col overflow-y-auto bg-forge-surface/30">
          {preview ? (
            <div className="p-5 flex flex-col gap-4">
              {/* Item name + base */}
              <div>
                <div className="font-display text-xl text-amber-300">
                  {preview.name}
                </div>
                <div className="font-mono text-xs text-forge-dim mt-0.5">
                  {preview.base} · {SLOT_LABEL[preview.slot] ?? preview.slot}
                  {preview.class_req && (
                    <span className={`ml-2 ${CLASS_COLOR[preview.class_req] ?? "text-forge-dim"}`}>
                      · {preview.class_req} only
                    </span>
                  )}
                </div>
              </div>

              {/* Implicit */}
              {preview.implicit && (
                <div className="font-mono text-xs text-forge-text/70 italic border-b border-forge-border/40 pb-3">
                  {preview.implicit}
                </div>
              )}

              {/* Fixed affixes */}
              {preview.affixes.length > 0 && (
                <div className="flex flex-col gap-1">
                  {preview.affixes.map((a, i) => (
                    <div key={i} className="font-mono text-xs text-forge-text/90">
                      {a}
                    </div>
                  ))}
                </div>
              )}

              {/* Unique passive */}
              <div className="rounded border border-amber-500/30 bg-amber-500/5 p-3">
                <div className="font-mono text-[10px] uppercase tracking-widest text-amber-400 mb-1.5">
                  Unique Passive
                </div>
                <div className="font-body text-sm text-forge-text/90 leading-relaxed">
                  {preview.unique_passive}
                </div>
              </div>

              {/* Tags */}
              {preview.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {preview.tags.map((t) => (
                    <span
                      key={t}
                      className="rounded-sm bg-forge-surface2 px-2 py-0.5 font-mono text-[10px] text-forge-dim"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              )}

              {/* Equip button */}
              <div className="flex justify-end pt-2">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => { onSelect(preview); onClose(); }}
                >
                  Equip {preview.name} →
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <p className="font-mono text-xs text-forge-dim">
                Hover an item to preview
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
