/**
 * P23 — TargetAffixBuilder
 *
 * Lets the user pick affixes with tier goals. Validates against duplicates and
 * a max of 4 affixes, then exposes the list via onChange.
 */

import { useState } from "react";
import type { TargetAffix } from "@/pages/crafting/CraftingPage";

// ---------------------------------------------------------------------------
// Available affixes catalogue
// ---------------------------------------------------------------------------

const AVAILABLE_AFFIXES = [
  { id: "max_life",          name: "+Max Life",          type: "prefix" },
  { id: "flat_fire_damage",  name: "Flat Fire Damage",   type: "prefix" },
  { id: "crit_chance",       name: "Crit Chance",        type: "prefix" },
  { id: "spell_damage",      name: "Spell Damage",       type: "prefix" },
  { id: "attack_speed",      name: "Attack Speed",       type: "prefix" },
  { id: "resistances",       name: "+Resistances",       type: "suffix" },
  { id: "cast_speed",        name: "Cast Speed",         type: "suffix" },
  { id: "mana_regen",        name: "Mana Regeneration",  type: "suffix" },
  { id: "movement_speed",    name: "Movement Speed",     type: "suffix" },
  { id: "life_on_hit",       name: "Life on Hit",        type: "suffix" },
] as const;

const MAX_AFFIXES = 4;
const TIER_MIN = 1;
const TIER_MAX = 7;

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface Props {
  affixes: TargetAffix[];
  onChange: (affixes: TargetAffix[]) => void;
}

export default function TargetAffixBuilder({ affixes, onChange }: Props) {
  const [selectedId, setSelectedId] = useState(AVAILABLE_AFFIXES[0].id);
  const [minTier,    setMinTier]    = useState(1);
  const [targetTier, setTargetTier] = useState(4);
  const [error,      setError]      = useState<string | null>(null);

  function handleAdd() {
    setError(null);

    if (affixes.length >= MAX_AFFIXES) {
      setError(`Maximum ${MAX_AFFIXES} affixes allowed.`);
      return;
    }

    if (affixes.some((a) => a.affix_id === selectedId)) {
      setError("That affix is already in your list.");
      return;
    }

    const def = AVAILABLE_AFFIXES.find((a) => a.id === selectedId)!;
    const next: TargetAffix = {
      affix_id:   def.id,
      affix_name: def.name,
      min_tier:   minTier,
      target_tier: targetTier,
    };
    onChange([...affixes, next]);
  }

  function handleRemove(id: string) {
    onChange(affixes.filter((a) => a.affix_id !== id));
  }

  return (
    <div className="rounded-lg border border-[#2a3050] bg-[#10152a] p-4 space-y-4">
      <h2 className="font-display text-sm font-semibold text-[#f5a623] uppercase tracking-wider">
        Target Affixes
      </h2>

      {/* Add section */}
      <div className="space-y-3 rounded-md bg-[#0d1123] border border-[#2a3050] p-3">
        <div className="space-y-1">
          <label className="text-[11px] text-gray-400 uppercase tracking-wider">Affix</label>
          <select
            value={selectedId}
            onChange={(e) => setSelectedId(e.target.value)}
            className="w-full rounded border border-[#2a3050] bg-[#10152a] px-2 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-[#f5a623]"
          >
            {AVAILABLE_AFFIXES.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name} ({a.type})
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          {/* Min tier */}
          <div className="space-y-1">
            <label className="flex justify-between text-[11px] text-gray-400 uppercase tracking-wider">
              <span>Min Tier</span>
              <span className="text-[#22d3ee] font-bold">{minTier}</span>
            </label>
            <input
              type="range"
              min={TIER_MIN}
              max={TIER_MAX}
              value={minTier}
              onChange={(e) => {
                const v = Number(e.target.value);
                setMinTier(v);
                if (v > targetTier) setTargetTier(v);
              }}
              className="w-full accent-[#f5a623]"
            />
          </div>

          {/* Target tier */}
          <div className="space-y-1">
            <label className="flex justify-between text-[11px] text-gray-400 uppercase tracking-wider">
              <span>Target Tier</span>
              <span className="text-[#f5a623] font-bold">{targetTier}</span>
            </label>
            <input
              type="range"
              min={TIER_MIN}
              max={TIER_MAX}
              value={targetTier}
              onChange={(e) => {
                const v = Number(e.target.value);
                setTargetTier(v);
                if (v < minTier) setMinTier(v);
              }}
              className="w-full accent-[#f5a623]"
            />
          </div>
        </div>

        {error && (
          <p className="text-xs text-red-400">{error}</p>
        )}

        <button
          onClick={handleAdd}
          disabled={affixes.length >= MAX_AFFIXES}
          className="w-full rounded bg-[#f5a623] px-3 py-1.5 text-xs font-semibold text-[#10152a] transition hover:bg-[#f5a623cc] disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Add Affix
        </button>
      </div>

      {/* Current affixes */}
      {affixes.length > 0 ? (
        <ul className="space-y-1.5">
          {affixes.map((a) => (
            <li
              key={a.affix_id}
              className="flex items-center justify-between rounded-md border border-[#2a3050] bg-[#0d1123] px-3 py-2"
            >
              <span className="text-xs text-gray-200">{a.affix_name}</span>
              <div className="flex items-center gap-2">
                <span className="rounded bg-[#22d3ee22] px-1.5 py-0.5 text-[10px] text-[#22d3ee]">
                  min T{a.min_tier}
                </span>
                <span className="rounded bg-[#f5a62322] px-1.5 py-0.5 text-[10px] text-[#f5a623]">
                  T{a.target_tier}
                </span>
                <button
                  onClick={() => handleRemove(a.affix_id)}
                  className="text-gray-500 hover:text-red-400 text-xs ml-1 transition-colors"
                >
                  ✕
                </button>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-xs text-gray-500 text-center py-2">No affixes added yet.</p>
      )}

      <p className="text-[10px] text-gray-600 text-right">
        {affixes.length} / {MAX_AFFIXES} affixes
      </p>
    </div>
  );
}
