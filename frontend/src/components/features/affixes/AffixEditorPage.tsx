import { useState, useEffect, useCallback, useMemo } from "react";
import { clsx } from "clsx";
import toast from "react-hot-toast";
import { adminApi } from "@/lib/api";
import type { AdminAffix, AdminAffixTier } from "@/lib/api";
import { Panel, Button, Badge, Spinner } from "@/components/ui";
import { BASE_CLASSES } from "@constants";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const ALL_SLOTS = [
  "helm", "chest", "belt", "boots", "gloves",
  "axe_1h", "axe_2h", "dagger", "mace_1h", "mace_2h", "sceptre", "shortsword",
  "sword_1h", "sword_2h", "wand", "staff", "polearm", "bow", "crossbow",
  "shield", "quiver", "catalyst",
  "amulet", "ring", "relic", "experimental",
  "idol_tiny_1x1", "idol_small_1x2", "idol_small_1x3", "idol_stout_2x1",
  "idol_grand_2x2", "idol_large_1x4", "idol_ornate_2x3", "idol_huge_4x1",
  "idol_immense_4x2",
];

const ALL_TAGS = [
  "damage", "resistance", "health", "mana", "armor", "dodge", "block",
  "crit", "attack_speed", "cast_speed", "movement", "spell", "minion",
  "ward", "endurance",
  "fire", "cold", "lightning", "void", "necrotic", "poison", "physical",
];

// ---------------------------------------------------------------------------
// Small reusable inputs
// ---------------------------------------------------------------------------

function Input({
  value, onChange, placeholder, className,
}: {
  value: string; onChange: (v: string) => void; placeholder?: string; className?: string;
}) {
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className={clsx(
        "w-full rounded-sm border border-forge-border bg-forge-surface2 px-3 py-1.5",
        "text-sm text-forge-text placeholder-forge-dim outline-none",
        "focus:border-forge-cyan/60 focus:ring-1 focus:ring-forge-cyan/20",
        className
      )}
    />
  );
}

function Select({
  value, onChange, options, className,
}: {
  value: string; onChange: (v: string) => void; options: { label: string; value: string }[]; className?: string;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={clsx(
        "rounded-sm border border-forge-border bg-forge-surface2 px-3 py-1.5",
        "text-sm text-forge-text outline-none",
        "focus:border-forge-cyan/60",
        className
      )}
    >
      {options.map((o) => (
        <option key={o.value} value={o.value}>{o.label}</option>
      ))}
    </select>
  );
}

function TagToggle({ tag, active, onClick }: { tag: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        "rounded-sm px-2 py-0.5 text-xs font-mono border transition-colors cursor-pointer",
        active
          ? "border-forge-cyan/60 bg-forge-cyan/10 text-forge-cyan"
          : "border-forge-border bg-forge-surface2 text-forge-dim hover:text-forge-text hover:border-forge-border"
      )}
    >
      {tag}
    </button>
  );
}

// ---------------------------------------------------------------------------
// Editor panel
// ---------------------------------------------------------------------------

interface EditorPanelProps {
  affix: AdminAffix;
  onSave: (updated: AdminAffix) => Promise<void>;
  onClose: () => void;
}

function EditorPanel({ affix, onSave, onClose }: EditorPanelProps) {
  const [draft, setDraft] = useState<AdminAffix>(() => JSON.parse(JSON.stringify(affix)));
  const [saving, setSaving] = useState(false);

  // Reset when affix changes
  useEffect(() => {
    setDraft(JSON.parse(JSON.stringify(affix)));
  }, [affix.id]);

  function setField<K extends keyof AdminAffix>(key: K, val: AdminAffix[K]) {
    setDraft((d) => ({ ...d, [key]: val }));
  }

  function toggleTag(tag: string) {
    setDraft((d) => ({
      ...d,
      tags: d.tags.includes(tag) ? d.tags.filter((t) => t !== tag) : [...d.tags, tag],
    }));
  }

  function toggleSlot(slot: string) {
    setDraft((d) => ({
      ...d,
      applicable_to: d.applicable_to.includes(slot)
        ? d.applicable_to.filter((s) => s !== slot)
        : [...d.applicable_to, slot],
    }));
  }

  function updateTier(idx: number, field: "min" | "max", val: string) {
    const n = parseInt(val, 10);
    setDraft((d) => {
      const tiers = [...d.tiers];
      tiers[idx] = { ...tiers[idx], [field]: isNaN(n) ? 0 : n };
      return { ...d, tiers };
    });
  }

  function addTier() {
    setDraft((d) => ({
      ...d,
      tiers: [...d.tiers, { tier: d.tiers.length + 1, min: 0, max: 0 }],
    }));
  }

  function removeTier(idx: number) {
    setDraft((d) => ({
      ...d,
      tiers: d.tiers.filter((_, i) => i !== idx).map((t, i) => ({ ...t, tier: i + 1 })),
    }));
  }

  async function handleSave() {
    setSaving(true);
    try {
      await onSave(draft);
    } finally {
      setSaving(false);
    }
  }

  const isDirty = JSON.stringify(draft) !== JSON.stringify(affix);

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-forge-border bg-forge-surface2 px-4 py-3 shrink-0">
        <span className="font-mono text-xs uppercase tracking-widest text-forge-cyan">
          Edit Affix
        </span>
        <div className="flex gap-2 items-center">
          {isDirty && (
            <span className="font-mono text-xs text-forge-amber">unsaved</span>
          )}
          <Button variant="ghost" size="sm" onClick={handleSave} disabled={saving || !isDirty}>
            {saving ? "Saving…" : "Save"}
          </Button>
          <button
            onClick={onClose}
            className="text-forge-dim hover:text-forge-text transition-colors font-mono text-sm leading-none cursor-pointer bg-transparent border-none"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Scrollable body */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-5">

        {/* ID (read-only) */}
        <div>
          <label className="block font-mono text-xs text-forge-muted mb-1">ID (read-only)</label>
          <div className="font-mono text-xs text-forge-dim bg-forge-surface3 rounded-sm px-3 py-1.5 border border-forge-border">
            {draft.id}
          </div>
        </div>

        {/* Name */}
        <div>
          <label className="block font-mono text-xs text-forge-muted mb-1">Name</label>
          <Input value={draft.name} onChange={(v) => setField("name", v)} />
        </div>

        {/* Type */}
        <div>
          <label className="block font-mono text-xs text-forge-muted mb-1">Type</label>
          <Select
            value={draft.type}
            onChange={(v) => setField("type", v as "prefix" | "suffix")}
            options={[
              { label: "Prefix", value: "prefix" },
              { label: "Suffix", value: "suffix" },
            ]}
          />
        </div>

        {/* Stat Key */}
        <div>
          <label className="block font-mono text-xs text-forge-muted mb-1">Stat Key</label>
          <Input
            value={draft.stat_key ?? ""}
            onChange={(v) => setField("stat_key", v || null)}
            placeholder="e.g. fire_resistance"
          />
        </div>

        {/* Class Requirement */}
        <div>
          <label className="block font-mono text-xs text-forge-muted mb-1">Class Requirement</label>
          <Select
            value={draft.class_requirement ?? ""}
            onChange={(v) => setField("class_requirement", v || null)}
            options={[
              { label: "Any class", value: "" },
              ...BASE_CLASSES.map((c) => ({ label: c, value: c })),
            ]}
          />
        </div>

        {/* Tags */}
        <div>
          <label className="block font-mono text-xs text-forge-muted mb-2">Tags</label>
          <div className="flex flex-wrap gap-1.5">
            {ALL_TAGS.map((tag) => (
              <TagToggle
                key={tag}
                tag={tag}
                active={draft.tags.includes(tag)}
                onClick={() => toggleTag(tag)}
              />
            ))}
          </div>
        </div>

        {/* Applicable To */}
        <div>
          <label className="block font-mono text-xs text-forge-muted mb-2">Applicable To</label>
          <div className="flex flex-wrap gap-1.5">
            {ALL_SLOTS.map((slot) => (
              <TagToggle
                key={slot}
                tag={slot}
                active={draft.applicable_to.includes(slot)}
                onClick={() => toggleSlot(slot)}
              />
            ))}
          </div>
        </div>

        {/* Tiers */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="font-mono text-xs text-forge-muted">Tiers</label>
            <button
              onClick={addTier}
              className="font-mono text-xs text-forge-cyan hover:text-forge-cyan-hot cursor-pointer bg-transparent border-none"
            >
              + Add Tier
            </button>
          </div>
          <div className="space-y-2">
            {draft.tiers.map((tier, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <span className="font-mono text-xs text-forge-dim w-6 text-right shrink-0">
                  T{tier.tier}
                </span>
                <input
                  type="number"
                  value={tier.min}
                  onChange={(e) => updateTier(idx, "min", e.target.value)}
                  className="w-20 rounded-sm border border-forge-border bg-forge-surface2 px-2 py-1 text-xs text-forge-text outline-none focus:border-forge-cyan/60"
                />
                <span className="text-forge-dim text-xs">–</span>
                <input
                  type="number"
                  value={tier.max}
                  onChange={(e) => updateTier(idx, "max", e.target.value)}
                  className="w-20 rounded-sm border border-forge-border bg-forge-surface2 px-2 py-1 text-xs text-forge-text outline-none focus:border-forge-cyan/60"
                />
                <button
                  onClick={() => removeTier(idx)}
                  className="text-forge-dim hover:text-forge-red transition-colors text-xs cursor-pointer bg-transparent border-none ml-1"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function AffixEditorPage() {
  const [affixes, setAffixes] = useState<AdminAffix[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<AdminAffix | null>(null);

  // Filters
  const [q, setQ] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [tagFilter, setTagFilter] = useState("");
  const [slotFilter, setSlotFilter] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    const res = await adminApi.affixes();
    if (res.data) setAffixes(res.data);
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const filtered = useMemo(() => {
    let list = affixes;
    const lq = q.toLowerCase();
    if (lq) {
      list = list.filter(
        (a) =>
          a.name.toLowerCase().includes(lq) ||
          a.id.toLowerCase().includes(lq) ||
          (a.stat_key ?? "").toLowerCase().includes(lq)
      );
    }
    if (typeFilter) list = list.filter((a) => a.type === typeFilter);
    if (tagFilter) list = list.filter((a) => a.tags.includes(tagFilter));
    if (slotFilter) list = list.filter((a) => a.applicable_to.includes(slotFilter));
    return list;
  }, [affixes, q, typeFilter, tagFilter, slotFilter]);

  async function handleSave(updated: AdminAffix) {
    const res = await adminApi.updateAffix(updated.id, {
      name: updated.name,
      type: updated.type,
      tags: updated.tags,
      applicable_to: updated.applicable_to,
      class_requirement: updated.class_requirement,
      tiers: updated.tiers,
      stat_key: updated.stat_key,
    });
    if (res.data) {
      setAffixes((prev) =>
        prev.map((a) => (a.id === res.data!.id ? res.data! : a))
      );
      // Keep panel open with saved data
      setSelected(res.data);
      toast.success(`Saved "${res.data.name}"`);
    } else {
      toast.error("Save failed");
    }
  }

  return (
    <div className="flex gap-4 h-[calc(100vh-10rem)]">
      {/* ---- Left: Table ---- */}
      <div className={clsx("flex flex-col min-w-0 transition-all", selected ? "flex-[2]" : "flex-1")}>
        <Panel
          title={`Affixes (${filtered.length} / ${affixes.length})`}
          className="flex flex-col h-full"
        >
          {/* Filters */}
          <div className="flex flex-wrap gap-2 mb-4">
            <Input
              value={q}
              onChange={setQ}
              placeholder="Search name / id / stat_key…"
              className="flex-1 min-w-40"
            />
            <Select
              value={typeFilter}
              onChange={setTypeFilter}
              options={[
                { label: "All types", value: "" },
                { label: "Prefix", value: "prefix" },
                { label: "Suffix", value: "suffix" },
              ]}
            />
            <Select
              value={tagFilter}
              onChange={setTagFilter}
              options={[
                { label: "All tags", value: "" },
                ...ALL_TAGS.map((t) => ({ label: t, value: t })),
              ]}
            />
            <Select
              value={slotFilter}
              onChange={setSlotFilter}
              options={[
                { label: "All slots", value: "" },
                ...ALL_SLOTS.map((s) => ({ label: s, value: s })),
              ]}
            />
          </div>

          {/* Table */}
          {loading ? (
            <div className="flex justify-center py-12"><Spinner /></div>
          ) : (
            <div className="flex-1 overflow-y-auto">
              <table className="w-full text-sm border-collapse">
                <thead className="sticky top-0 bg-forge-surface2 z-10">
                  <tr className="border-b border-forge-border text-left">
                    <th className="font-mono text-xs text-forge-muted py-2 px-3 font-normal">Name</th>
                    <th className="font-mono text-xs text-forge-muted py-2 px-2 font-normal w-16">Type</th>
                    <th className="font-mono text-xs text-forge-muted py-2 px-2 font-normal">Stat Key</th>
                    <th className="font-mono text-xs text-forge-muted py-2 px-2 font-normal w-14">Tiers</th>
                    <th className="font-mono text-xs text-forge-muted py-2 px-2 font-normal w-14">Slots</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((affix) => {
                    const isSelected = selected?.id === affix.id;
                    return (
                      <tr
                        key={affix.id}
                        onClick={() => setSelected(isSelected ? null : affix)}
                        className={clsx(
                          "border-b border-forge-border/40 cursor-pointer transition-colors",
                          isSelected
                            ? "bg-forge-cyan/8 border-l-2 border-l-forge-cyan"
                            : "hover:bg-forge-surface2"
                        )}
                      >
                        <td className="py-2 px-3 text-forge-text font-body">{affix.name}</td>
                        <td className="py-2 px-2">
                          <span className={clsx(
                            "font-mono text-xs",
                            affix.type === "prefix" ? "text-forge-amber" : "text-forge-cyan"
                          )}>
                            {affix.type === "prefix" ? "pre" : "suf"}
                          </span>
                        </td>
                        <td className="py-2 px-2 font-mono text-xs text-forge-dim max-w-[160px] truncate">
                          {affix.stat_key ?? <span className="text-forge-red/60">null</span>}
                        </td>
                        <td className="py-2 px-2 text-center font-mono text-xs text-forge-muted">
                          {affix.tiers.length}
                        </td>
                        <td className="py-2 px-2 text-center font-mono text-xs text-forge-muted">
                          {affix.applicable_to.length}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              {filtered.length === 0 && (
                <div className="py-12 text-center font-mono text-xs text-forge-dim">
                  No affixes match your filters
                </div>
              )}
            </div>
          )}
        </Panel>
      </div>

      {/* ---- Right: Editor panel ---- */}
      {selected && (
        <div className="flex-[1] min-w-[340px] max-w-[420px] rounded border border-forge-border bg-forge-surface overflow-hidden flex flex-col">
          <EditorPanel
            affix={selected}
            onSave={handleSave}
            onClose={() => setSelected(null)}
          />
        </div>
      )}
    </div>
  );
}
