/**
 * GearSlotEditor — modal for adding/editing affixes on a single gear slot.
 * Opens when user clicks a gear slot in BuildPlannerPage.
 */

import { useState } from "react";
import { clsx } from "clsx";
import { Button } from "@/components/ui";
import { AFFIX_DEFINITIONS, getAffixValue, type GearItem, type GearAffix } from "@/lib/gameData";

interface GearSlotEditorProps {
  slot: string;
  slotIcon: string;
  /** Canonical slot name for filtering affixes (e.g. "Ring" for "Ring ×2") */
  slotType: string;
  initial?: GearItem;
  onSave: (item: GearItem) => void;
  onClear: () => void;
  onClose: () => void;
}

const RARITY_OPTIONS = [
  { value: "magic",   label: "Magic",   color: "#5ab0ff", maxAffixes: 2 },
  { value: "rare",    label: "Rare",    color: "#f5d060", maxAffixes: 4 },
  { value: "exalted", label: "Exalted", color: "#b870ff", maxAffixes: 4 },
] as const;

const TIER_LABELS = ["T1", "T2", "T3", "T4", "T5"] as const;

export default function GearSlotEditor({
  slot, slotIcon, slotType, initial, onSave, onClear, onClose,
}: GearSlotEditorProps) {
  const [rarity, setRarity] = useState<GearItem["rarity"]>(initial?.rarity ?? "rare");
  const [affixes, setAffixes] = useState<GearAffix[]>(initial?.affixes ?? []);

  const rarityDef = RARITY_OPTIONS.find((r) => r.value === rarity)!;
  const maxAffixes = rarityDef.maxAffixes;

  // Affixes applicable to this slot type
  const slotAffixes = AFFIX_DEFINITIONS.filter((d) => d.applicable.includes(slotType));
  const usedNames = new Set(affixes.map((a) => a.name));
  const available = slotAffixes.filter((d) => !usedNames.has(d.name));

  function addAffix(name: string) {
    if (affixes.length >= maxAffixes) return;
    const value = getAffixValue(name, 4); // default T4
    setAffixes((prev) => [...prev, { name, tier: 4, value }]);
  }

  function removeAffix(idx: number) {
    setAffixes((prev) => prev.filter((_, i) => i !== idx));
  }

  function setTier(idx: number, tier: number) {
    setAffixes((prev) => prev.map((a, i) =>
      i === idx ? { ...a, tier, value: getAffixValue(a.name, tier) } : a
    ));
  }

  function handleSave() {
    onSave({ slot, rarity, affixes });
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div
        className="bg-forge-surface border border-forge-border rounded-sm w-full max-w-md mx-4 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-forge-border">
          <div className="flex items-center gap-2">
            <span className="text-lg">{slotIcon}</span>
            <span className="font-display text-base font-bold text-forge-amber tracking-wider">{slot}</span>
          </div>
          <button
            onClick={onClose}
            className="font-mono text-forge-dim hover:text-forge-text bg-transparent border-none cursor-pointer text-lg leading-none"
          >×</button>
        </div>

        <div className="p-4 flex flex-col gap-4">
          {/* Rarity */}
          <div>
            <div className="font-mono text-[9px] uppercase tracking-widest text-forge-dim mb-2">Rarity</div>
            <div className="flex gap-2">
              {RARITY_OPTIONS.map((r) => (
                <button
                  key={r.value}
                  onClick={() => {
                    setRarity(r.value as GearItem["rarity"]);
                    // Trim affixes if switching to magic
                    if (r.value === "magic" && affixes.length > 2) {
                      setAffixes((prev) => prev.slice(0, 2));
                    }
                  }}
                  className={clsx(
                    "flex-1 font-mono text-[10px] uppercase tracking-wider py-1.5 border rounded-sm cursor-pointer transition-all",
                    rarity === r.value
                      ? "border-current"
                      : "border-forge-border text-forge-dim hover:border-forge-border-hot"
                  )}
                  style={rarity === r.value ? { color: r.color, borderColor: r.color, background: `${r.color}10` } : undefined}
                >
                  {r.label}
                </button>
              ))}
            </div>
          </div>

          {/* Current affixes */}
          <div>
            <div className="font-mono text-[9px] uppercase tracking-widest text-forge-dim mb-2">
              Affixes ({affixes.length}/{maxAffixes})
            </div>
            <div className="flex flex-col gap-1.5">
              {affixes.length === 0 && (
                <p className="font-body text-xs italic text-forge-dim text-center py-2">No affixes — add from the list below</p>
              )}
              {affixes.map((affix, idx) => {
                const def = AFFIX_DEFINITIONS.find((d) => d.name === affix.name);
                const tierRange = def?.tiers[`T${affix.tier}`];
                return (
                  <div key={idx} className="flex items-center gap-2 bg-forge-surface2 border border-forge-border rounded-sm px-2.5 py-2">
                    <div className="flex-1 min-w-0">
                      <div className="font-body text-xs text-forge-text truncate">{affix.name}</div>
                      <div className="font-mono text-[9px] text-forge-muted">
                        {tierRange ? `${tierRange[0]}–${tierRange[1]} · sim value: ${affix.value}` : "—"}
                      </div>
                    </div>
                    {/* Tier selector */}
                    <div className="flex gap-0.5 flex-shrink-0">
                      {TIER_LABELS.map((t, ti) => {
                        const tierNum = ti + 1;
                        const hasTier = !!def?.tiers[t];
                        return (
                          <button
                            key={t}
                            disabled={!hasTier}
                            onClick={() => setTier(idx, tierNum)}
                            className={clsx(
                              "font-mono text-[8px] w-6 h-5 rounded-sm border cursor-pointer transition-all",
                              !hasTier ? "border-transparent text-forge-dim/30 cursor-default" :
                              affix.tier === tierNum
                                ? "border-forge-amber text-forge-amber bg-forge-amber/10"
                                : "border-forge-border text-forge-dim hover:border-forge-border-hot hover:text-forge-muted"
                            )}
                          >{t}</button>
                        );
                      })}
                    </div>
                    <button
                      onClick={() => removeAffix(idx)}
                      className="font-mono text-forge-dim hover:text-forge-red bg-transparent border-none cursor-pointer flex-shrink-0"
                    >×</button>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Affix picker */}
          {affixes.length < maxAffixes && (
            <div>
              <div className="font-mono text-[9px] uppercase tracking-widest text-forge-dim mb-2">Add Affix</div>
              <div className="flex flex-col gap-1 max-h-40 overflow-y-auto border border-forge-border rounded-sm">
                {available.length === 0 && (
                  <p className="font-body text-xs italic text-forge-dim text-center py-3">All available affixes added</p>
                )}
                {available.map((def) => (
                  <button
                    key={def.name}
                    onClick={() => addAffix(def.name)}
                    className="flex items-center justify-between px-2.5 py-1.5 text-left hover:bg-forge-surface2 transition-colors cursor-pointer bg-transparent border-none group"
                  >
                    <div className="flex items-center gap-2">
                      <span className={clsx(
                        "font-mono text-[8px] px-1 py-0.5 rounded-sm border",
                        def.type === "prefix"
                          ? "border-forge-amber/40 text-forge-amber bg-forge-amber/6"
                          : "border-forge-purple/40 text-forge-purple bg-forge-purple/6"
                      )}>{def.type === "prefix" ? "PRE" : "SUF"}</span>
                      <span className="font-body text-xs text-forge-muted group-hover:text-forge-text">{def.name}</span>
                    </div>
                    <span className="font-mono text-[9px] text-forge-dim">
                      T1: {def.tiers.T1?.[0]}–{def.tiers.T1?.[1]}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex gap-2 px-4 py-3 border-t border-forge-border">
          <Button variant="ghost" size="sm" onClick={onClear} className="text-forge-red hover:text-forge-red">
            Clear Slot
          </Button>
          <div className="flex-1" />
          <Button variant="outline" size="sm" onClick={onClose}>Cancel</Button>
          <Button variant="primary" size="sm" onClick={handleSave}>Apply</Button>
        </div>
      </div>
    </div>
  );
}