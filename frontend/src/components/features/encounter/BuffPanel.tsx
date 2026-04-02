/**
 * E10 — Buff Panel
 *
 * Manages active buffs: add/remove, set duration and stat modifiers.
 */

import { useState } from "react";
import type { BuffDef } from "@/services/buildApi";

interface Props {
  buffs: BuffDef[];
  onChange: (buffs: BuffDef[]) => void;
  disabled?: boolean;
}

const PRESET_BUFFS: BuffDef[] = [
  { buff_id: "frenzy",      modifiers: { base_damage: 50.0 },              duration: null },
  { buff_id: "conviction",  modifiers: { crit_chance: 0.1 },               duration: null },
  { buff_id: "power_surge", modifiers: { spell_damage_pct: 30.0 },         duration: 10.0 },
  { buff_id: "exposure",    modifiers: { physical_damage_pct: 25.0 },      duration: null },
];

function BuffRow({
  buff,
  onRemove,
  disabled,
}: {
  buff: BuffDef;
  onRemove: () => void;
  disabled?: boolean;
}) {
  const modSummary = Object.entries(buff.modifiers)
    .map(([k, v]) => `${k}: ${v > 0 ? "+" : ""}${v}`)
    .join(", ");

  return (
    <div className="flex items-center justify-between rounded border border-forge-border bg-forge-surface/60 px-3 py-2">
      <div>
        <span className="text-sm font-medium text-forge-text">{buff.buff_id}</span>
        <p className="text-xs text-forge-muted font-mono">{modSummary}</p>
        {buff.duration !== null && (
          <p className="text-xs text-forge-muted">{buff.duration}s</p>
        )}
      </div>
      <button
        onClick={onRemove}
        disabled={disabled}
        className="text-xs text-red-400 hover:text-red-300 disabled:opacity-40 px-2"
      >
        Remove
      </button>
    </div>
  );
}

export default function BuffPanel({ buffs, onChange, disabled }: Props) {
  const [newId,  setNewId]  = useState("");
  const [newMod, setNewMod] = useState("base_damage: 50");
  const [newDur, setNewDur] = useState("");

  function addBuff() {
    const bid = newId.trim();
    if (!bid) return;

    const modifiers: Record<string, number> = {};
    for (const part of newMod.split(",")) {
      const [k, v] = part.split(":").map((s) => s.trim());
      const n = parseFloat(v);
      if (k && !isNaN(n)) modifiers[k] = n;
    }

    const duration = newDur.trim() ? parseFloat(newDur) : null;
    const buff: BuffDef = { buff_id: bid, modifiers, duration };
    onChange([...buffs.filter((b) => b.buff_id !== bid), buff]);
    setNewId("");
    setNewMod("base_damage: 50");
    setNewDur("");
  }

  function addPreset(p: BuffDef) {
    onChange([...buffs.filter((b) => b.buff_id !== p.buff_id), p]);
  }

  return (
    <section>
      <h3 className="mb-3 text-sm font-semibold text-forge-accent uppercase tracking-wider">
        Buffs
      </h3>

      {/* Presets */}
      <div className="mb-3 flex flex-wrap gap-2">
        {PRESET_BUFFS.map((p) => (
          <button
            key={p.buff_id}
            onClick={() => addPreset(p)}
            disabled={disabled}
            className="
              rounded border border-forge-border px-2 py-1 text-xs text-forge-muted
              hover:border-forge-accent hover:text-forge-accent disabled:opacity-40
            "
          >
            + {p.buff_id}
          </button>
        ))}
      </div>

      {/* Active buffs */}
      <div className="mb-3 space-y-2">
        {buffs.length === 0 ? (
          <p className="text-xs text-forge-muted">No active buffs.</p>
        ) : (
          buffs.map((b) => (
            <BuffRow
              key={b.buff_id}
              buff={b}
              onRemove={() => onChange(buffs.filter((x) => x.buff_id !== b.buff_id))}
              disabled={disabled}
            />
          ))
        )}
      </div>

      {/* Custom buff form */}
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
        <input
          type="text"
          placeholder="Buff ID"
          value={newId}
          disabled={disabled}
          onChange={(e) => setNewId(e.target.value)}
          className="
            rounded border border-forge-border bg-forge-input
            px-3 py-2 text-xs text-forge-text
            focus:border-forge-accent focus:outline-none disabled:opacity-50
          "
        />
        <input
          type="text"
          placeholder="Modifiers (e.g. base_damage: 50)"
          value={newMod}
          disabled={disabled}
          onChange={(e) => setNewMod(e.target.value)}
          className="
            rounded border border-forge-border bg-forge-input
            px-3 py-2 text-xs text-forge-text
            focus:border-forge-accent focus:outline-none disabled:opacity-50
          "
        />
        <div className="flex gap-2">
          <input
            type="number"
            placeholder="Duration (blank = permanent)"
            value={newDur}
            disabled={disabled}
            onChange={(e) => setNewDur(e.target.value)}
            className="
              flex-1 rounded border border-forge-border bg-forge-input
              px-3 py-2 text-xs text-forge-text
              focus:border-forge-accent focus:outline-none disabled:opacity-50
            "
          />
          <button
            onClick={addBuff}
            disabled={disabled || !newId.trim()}
            className="
              rounded bg-forge-accent px-3 py-2 text-xs font-semibold text-forge-bg
              hover:brightness-110 disabled:opacity-40
            "
          >
            Add
          </button>
        </div>
      </div>
    </section>
  );
}
