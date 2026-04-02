/**
 * E10 — Gear Panel
 *
 * Allows adding/removing affix entries per gear slot.
 * Keeps it simple: one input row per slot, up to 3 affixes each.
 */

import { useState } from "react";
import type { GearItem, GearAffix } from "@/services/buildApi";
import { GEAR_SLOTS } from "@/services/buildApi";

interface Props {
  gear: GearItem[];
  onChange: (gear: GearItem[]) => void;
  disabled?: boolean;
}

function slotLabel(slot: string): string {
  return slot.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function findItem(gear: GearItem[], slot: string): GearItem | undefined {
  return gear.find((g) => g.slot === slot);
}

function upsertGear(gear: GearItem[], updated: GearItem): GearItem[] {
  const rest = gear.filter((g) => g.slot !== updated.slot);
  if (updated.affixes.length === 0) return rest;
  return [...rest, updated];
}

function AffixRow({
  affix,
  index,
  onUpdate,
  onRemove,
  disabled,
}: {
  affix: GearAffix;
  index: number;
  onUpdate: (a: GearAffix) => void;
  onRemove: () => void;
  disabled?: boolean;
}) {
  return (
    <div className="flex items-center gap-2 mt-1">
      <input
        type="text"
        placeholder="Affix name (e.g. Increased Spell Damage)"
        value={affix.name}
        disabled={disabled}
        onChange={(e) => onUpdate({ ...affix, name: e.target.value })}
        className="
          flex-1 rounded border border-forge-border bg-forge-input
          px-2 py-1 text-xs text-forge-text
          focus:border-forge-accent focus:outline-none
          disabled:opacity-50
        "
      />
      <input
        type="number"
        min={1}
        max={10}
        value={affix.tier}
        disabled={disabled}
        onChange={(e) => {
          const v = parseInt(e.target.value, 10);
          if (!isNaN(v) && v >= 1 && v <= 10) onUpdate({ ...affix, tier: v });
        }}
        className="
          w-14 rounded border border-forge-border bg-forge-input
          px-2 py-1 text-xs text-forge-text text-center
          focus:border-forge-accent focus:outline-none
          disabled:opacity-50
        "
      />
      <button
        onClick={onRemove}
        disabled={disabled}
        className="text-xs text-red-400 hover:text-red-300 disabled:opacity-40 px-1"
        title="Remove affix"
      >✕</button>
    </div>
  );
}

function SlotRow({
  slot, gear, onChange, disabled,
}: {
  slot: string;
  gear: GearItem[];
  onChange: (gear: GearItem[]) => void;
  disabled?: boolean;
}) {
  const item = findItem(gear, slot) ?? { slot, affixes: [], rarity: "magic" as const };

  function updateAffix(i: number, a: GearAffix) {
    const affixes = item.affixes.map((x, idx) => (idx === i ? a : x));
    onChange(upsertGear(gear, { ...item, affixes }));
  }

  function removeAffix(i: number) {
    const affixes = item.affixes.filter((_, idx) => idx !== i);
    onChange(upsertGear(gear, { ...item, affixes }));
  }

  function addAffix() {
    if (item.affixes.length >= 6) return;
    const affixes = [...item.affixes, { name: "", tier: 1 }];
    onChange(upsertGear(gear, { ...item, affixes }));
  }

  return (
    <div className="rounded border border-forge-border bg-forge-surface/60 px-3 py-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-forge-muted uppercase tracking-wide">
          {slotLabel(slot)}
        </span>
        {item.affixes.length < 6 && (
          <button
            onClick={addAffix}
            disabled={disabled}
            className="text-xs text-forge-accent hover:brightness-110 disabled:opacity-40"
          >
            + Affix
          </button>
        )}
      </div>
      {item.affixes.map((a, i) => (
        <AffixRow
          key={i}
          affix={a}
          index={i}
          onUpdate={(a) => updateAffix(i, a)}
          onRemove={() => removeAffix(i)}
          disabled={disabled}
        />
      ))}
    </div>
  );
}

export default function GearPanel({ gear, onChange, disabled }: Props) {
  return (
    <section>
      <h3 className="mb-3 text-sm font-semibold text-forge-accent uppercase tracking-wider">
        Gear
      </h3>
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {GEAR_SLOTS.map((slot) => (
          <SlotRow key={slot} slot={slot} gear={gear} onChange={onChange} disabled={disabled} />
        ))}
      </div>
    </section>
  );
}
