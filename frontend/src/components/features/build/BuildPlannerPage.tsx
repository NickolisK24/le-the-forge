import { useMemo, useState, useEffect, useRef } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";

import { Badge, Button, EmptyState, Panel, SectionLabel, Spinner } from "@/components/ui";
import PageMeta from "@/components/PageMeta";
import { useBuild, useCreateBuild, useUpdateBuild, useVote } from "@/hooks";
import { useAuthStore } from "@/store";
import { CLASS_COLORS, CLASS_SKILLS, MASTERIES, getAffixValue } from "@/lib/gameData";
import type { GearItem, GearAffix } from "@/lib/gameData";
import { BASE_CLASSES } from "@constants";
import type { Build, BuildSkill, CharacterClass, AffixOnItem } from "@/types";
import { versionApi, simulateApi, buildsApi, viewApi, type BuildSimulationResult, type ImportedBuild } from "@/lib/api";
import { PRESETS } from "@/data/presets";
import type { OptimizeMode } from "@/types";
import StatUpgradePanel from "./StatUpgradePanel";
import UpgradeCandidatesPanel from "./UpgradeCandidatesPanel";
import BuildPassiveTree from "./BuildPassiveTree";
import PassiveProgressBar from "./PassiveProgressBar";
import BuildImportModal from "./BuildImportModal";
import GearEditor from "./GearEditor";
import GearSlotEditor from "./GearSlotEditor";
import SkillSelector from "./SkillSelector";
import BossEncounterPanel from "./BossEncounterPanel";
import CorruptionScalingPanel from "./CorruptionScalingPanel";
import GearUpgradePanel from "./GearUpgradePanel";
import BuildScoreCard from "./simulation/BuildScoreCard";
import AccordionSection from "./simulation/AccordionSection";
import OffenseDefenseSplit from "./simulation/OffenseDefenseSplit";
import PrimarySkillBreakdown from "./simulation/PrimarySkillBreakdown";
import AllSkillsSummary from "./simulation/AllSkillsSummary";
import { resolveSkillName } from "@/data/skillTrees";
import type { GearSlot } from "@/types";
import BlessingsPanel from "@/components/blessings/BlessingsPanel";
import type { SelectedBlessing } from "@/types/blessings";

const CHARACTER_CLASSES: CharacterClass[] = [...BASE_CLASSES] as CharacterClass[];
const MAX_SKILLS = 5;
const MAX_SKILL_LEVEL = 30; // Base cap is 20; gear can grant additional levels

const inputCls =
  "w-full rounded-sm border border-forge-border bg-forge-surface2 px-3 py-2 font-body text-sm text-forge-text outline-none focus:border-forge-amber/60 disabled:opacity-50";
const labelCls = "font-mono text-[11px] uppercase tracking-widest text-forge-dim";

// ---------------------------------------------------------------------------
// Checkbox toggle
// ---------------------------------------------------------------------------
function FlagToggle({
  label, checked, onChange,
}: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className="flex items-center gap-2 cursor-pointer select-none"
    >
      <div
        className={`w-4 h-4 rounded-sm border flex-shrink-0 flex items-center justify-center transition-colors ${
          checked
            ? "bg-forge-amber border-forge-amber"
            : "bg-forge-surface2 border-forge-border"
        }`}
      >
        {checked && <span className="text-forge-bg text-[10px] font-bold">✓</span>}
      </div>
      <span className="font-body text-sm text-forge-text">{label}</span>
    </button>
  );
}

// ---------------------------------------------------------------------------
// QuickGearGrid — 11-slot grid that opens GearSlotEditor per slot.
// Used in create mode so users can craft affixes on each gear piece without
// leaving the build planner.
// ---------------------------------------------------------------------------
const QUICK_SLOT_DEFS = [
  { key: "helmet",  label: "Helm",        icon: "⛑",  slotType: "Helm",   storeSlot: "helmet",  occurrence: 0 },
  { key: "body",    label: "Body Armour", icon: "🧥", slotType: "Chest",  storeSlot: "body",    occurrence: 0 },
  { key: "gloves",  label: "Gloves",      icon: "🧤", slotType: "Gloves", storeSlot: "gloves",  occurrence: 0 },
  { key: "boots",   label: "Boots",       icon: "👢", slotType: "Boots",  storeSlot: "boots",   occurrence: 0 },
  { key: "belt",    label: "Belt",        icon: "➰", slotType: "Belt",   storeSlot: "belt",    occurrence: 0 },
  { key: "amulet",  label: "Amulet",      icon: "📿", slotType: "Amulet", storeSlot: "amulet",  occurrence: 0 },
  { key: "ring_1",  label: "Ring 1",      icon: "💍", slotType: "Ring",   storeSlot: "ring",    occurrence: 0 },
  { key: "ring_2",  label: "Ring 2",      icon: "💍", slotType: "Ring",   storeSlot: "ring",    occurrence: 1 },
  { key: "weapon",  label: "Weapon",      icon: "⚔",  slotType: "Wand",   storeSlot: "weapon",  occurrence: 0 },
  { key: "offhand", label: "Off-hand",    icon: "🛡", slotType: "Shield", storeSlot: "offhand", occurrence: 0 },
  // Relic uses Amulet-class affixes as proxy (AFFIX_DEFINITIONS has no "Relic"
  // applicable tag; spell-caster affixes on relics mirror amulet roll tables).
  { key: "relic",   label: "Relic",       icon: "🔮", slotType: "Amulet", storeSlot: "relic",   occurrence: 0 },
] as const;

function findGearAt(gear: GearSlot[], storeSlot: string, occurrence: number): GearSlot | undefined {
  let seen = 0;
  for (const g of gear) {
    if (g.slot === storeSlot) {
      if (seen === occurrence) return g;
      seen++;
    }
  }
  return undefined;
}

function removeGearAt(gear: GearSlot[], storeSlot: string, occurrence: number): GearSlot[] {
  let seen = 0;
  return gear.filter((g) => {
    if (g.slot !== storeSlot) return true;
    const keep = seen !== occurrence;
    seen++;
    return keep;
  });
}

function upsertGearAt(
  gear: GearSlot[],
  storeSlot: string,
  occurrence: number,
  next: GearSlot,
): GearSlot[] {
  let seen = 0;
  let replaced = false;
  const result: GearSlot[] = [];
  for (const g of gear) {
    if (g.slot === storeSlot) {
      if (seen === occurrence) {
        result.push(next);
        replaced = true;
      } else {
        result.push(g);
      }
      seen++;
    } else {
      result.push(g);
    }
  }
  if (!replaced) result.push(next);
  return result;
}

function slotToItem(slot: GearSlot | undefined, storeSlot: string): GearItem | undefined {
  if (!slot) return undefined;
  const rarity = (slot.rarity ?? "rare") as GearItem["rarity"];
  const safeRarity: GearItem["rarity"] =
    rarity === "normal" || rarity === "magic" || rarity === "rare" || rarity === "exalted"
      ? rarity
      : "rare";
  return {
    slot: storeSlot,
    rarity: safeRarity,
    affixes: (slot.affixes ?? []).map((a): GearAffix => ({
      name: a.name,
      tier: a.tier,
      value: getAffixValue(a.name, a.tier),
    })),
  };
}

function itemToSlot(item: GearItem, storeSlot: string, previousItemName?: string): GearSlot {
  return {
    slot: storeSlot,
    item_name: previousItemName,
    rarity: item.rarity,
    affixes: item.affixes.map((a): AffixOnItem => ({
      name: a.name,
      tier: a.tier,
      sealed: false,
    })),
  };
}

function QuickGearGrid({
  gear, onChange,
}: { gear: GearSlot[]; onChange: (g: GearSlot[]) => void }) {
  const [editingKey, setEditingKey] = useState<string | null>(null);

  const activeDef = editingKey
    ? QUICK_SLOT_DEFS.find((d) => d.key === editingKey) ?? null
    : null;
  const activeExisting = activeDef
    ? findGearAt(gear, activeDef.storeSlot, activeDef.occurrence)
    : undefined;

  return (
    <>
      <div className="grid grid-cols-4 sm:grid-cols-6 gap-2">
        {QUICK_SLOT_DEFS.map((def) => {
          const equipped = findGearAt(gear, def.storeSlot, def.occurrence);
          const affixCount = equipped?.affixes?.length ?? 0;
          const hasItem = !!equipped;
          return (
            <button
              key={def.key}
              type="button"
              onClick={() => setEditingKey(def.key)}
              className={`relative flex flex-col items-center justify-center gap-1 border rounded-sm px-2 py-3 cursor-pointer transition-colors ${
                hasItem
                  ? "border-forge-amber/60 bg-forge-amber/10 hover:bg-forge-amber/15"
                  : "border-forge-border bg-forge-surface2 hover:border-forge-border-hot"
              }`}
              aria-label={`Edit ${def.label}`}
            >
              <span className="text-2xl leading-none">{def.icon}</span>
              <span className="font-mono text-[9px] uppercase tracking-wider text-forge-dim">
                {def.label}
              </span>
              {affixCount > 0 && (
                <span className="absolute top-1 right-1 min-w-[18px] h-[18px] px-1 rounded-full bg-forge-amber text-forge-bg font-mono text-[10px] font-bold flex items-center justify-center">
                  {affixCount}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {activeDef && (
        <GearSlotEditor
          slot={activeDef.label}
          slotIcon={activeDef.icon}
          slotType={activeDef.slotType}
          initial={slotToItem(activeExisting, activeDef.storeSlot)}
          onSave={(item) => {
            const next = itemToSlot(item, activeDef.storeSlot, activeExisting?.item_name);
            onChange(upsertGearAt(gear, activeDef.storeSlot, activeDef.occurrence, next));
            setEditingKey(null);
          }}
          onClear={() => {
            onChange(removeGearAt(gear, activeDef.storeSlot, activeDef.occurrence));
            setEditingKey(null);
          }}
          onClose={() => setEditingKey(null)}
        />
      )}
    </>
  );
}

// ---------------------------------------------------------------------------
// Shared types
// ---------------------------------------------------------------------------
interface DraftSkill {
  skill_name: string;
  slot: number;
  points_allocated: number;
  spec_tree: number[];
}

interface AllocMap { [nodeId: number]: number }

// ---------------------------------------------------------------------------
// Build summary (view mode)
// ---------------------------------------------------------------------------
function BuildSummary({ build }: { build: Build }) {
  const { user } = useAuthStore();
  const vote = useVote();
  const updateBuild = useUpdateBuild();
  const isOwner = user && build.author?.id === user.id;

  const { data: versionRes } = useQuery({
    queryKey: ["version"],
    queryFn: () => versionApi.get(),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });

  const [simResult, setSimResult] = useState<BuildSimulationResult | null>(null);
  const [showDashboard, setShowDashboard] = useState(false);
  const [optimizeMode, setOptimizeMode] = useState<OptimizeMode>("balanced");
  const simulateMutation = useMutation({
    mutationFn: () => simulateApi.build(build.slug),
    onSuccess: (res) => {
      if (res.data) {
        setSimResult(res.data);
        setShowDashboard(true);
      } else {
        toast.error("Simulation returned no data");
      }
    },
    onError: () => toast.error("Simulation failed — backend may be unavailable"),
  });

  const optimizeQuery = useQuery({
    queryKey: ["optimize", build.slug, optimizeMode],
    queryFn: () => buildsApi.optimize(build.slug, optimizeMode),
    enabled: showDashboard && simResult !== null,
    staleTime: 30 * 60 * 1000,
    select: (res) => res.data,
  });

  function handleExport() {
    const payload = {
      name: build.name,
      description: build.description,
      character_class: build.character_class,
      mastery: build.mastery,
      level: build.level,
      patch_version: build.patch_version,
      cycle: build.cycle,
      is_ssf: build.is_ssf,
      is_hc: build.is_hc,
      is_ladder_viable: build.is_ladder_viable,
      is_budget: build.is_budget,
      passive_tree: build.passive_tree,
      skills: build.skills.map((s) => ({
        skill_name: s.skill_name,
        slot: s.slot,
        points_allocated: s.points_allocated,
        spec_tree: s.spec_tree,
      })),
      gear: build.gear,
    };
    navigator.clipboard.writeText(JSON.stringify(payload, null, 2))
      .then(() => toast.success("Build JSON copied to clipboard"))
      .catch(() => toast.error("Clipboard write failed"));
  }

  // Edit mode state — initialised from the existing build
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(build.name);
  const [description, setDescription] = useState(build.description ?? "");
  const [level, setLevel] = useState(build.level);
  const [isSsf, setIsSsf] = useState(build.is_ssf);
  const [isHc, setIsHc] = useState(build.is_hc);
  const [isLadder, setIsLadder] = useState(build.is_ladder_viable);
  const [isBudget, setIsBudget] = useState(build.is_budget);
  const [draftSkills, setDraftSkills] = useState<DraftSkill[]>(
    build.skills.map((s) => ({
      skill_name: s.skill_name,
      slot: s.slot,
      points_allocated: s.points_allocated,
      spec_tree: s.spec_tree ?? [],
    }))
  );

  // Passive tree allocation (stored as flat array of node IDs in DB)
  const [passiveTree, setPassiveTree] = useState<number[]>(build.passive_tree ?? []);

  // Gear slots
  const [gearSlots, setGearSlots] = useState<GearSlot[]>(build.gear ?? []);

  // Monolith blessings
  const [draftBlessings, setDraftBlessings] = useState<SelectedBlessing[]>(
    build.blessings ?? [],
  );

  function getPassiveAllocMap(): AllocMap {
    const map: AllocMap = {};
    for (const id of passiveTree) map[id] = (map[id] ?? 0) + 1;
    return map;
  }

  function setPassiveAlloc(nodeId: number, points: number) {
    setPassiveTree((prev) => {
      const current = prev.filter(id => id === nodeId).length;
      if (points > current) {
        // Add one point at end (preserves chronological order)
        return [...prev, nodeId];
      } else if (points < current) {
        // Remove the last occurrence (most recently added)
        const idx = prev.lastIndexOf(nodeId);
        return idx === -1 ? prev : [...prev.slice(0, idx), ...prev.slice(idx + 1)];
      }
      return prev;
    });
  }

  function rewindPassiveTo(stepIndex: number) {
    // Keep only the first stepIndex entries (undo everything after)
    setPassiveTree(prev => prev.slice(0, stepIndex));
  }
  const characterClass = build.character_class;
  const [mastery, setMastery] = useState(build.mastery);
  const [showMasteryConfirm, setShowMasteryConfirm] = useState<string | null>(null);

  const masteryOptions = useMemo(
    () => MASTERIES[characterClass] ?? [],
    [characterClass],
  );

  function handleMasteryChangeRequest(next: string) {
    if (next === mastery) return;
    // Show confirmation if there are passive points or skills that might be affected
    if (passiveTree.length > 0 || draftSkills.length > 0) {
      setShowMasteryConfirm(next);
    } else {
      setMastery(next);
    }
  }

  function confirmMasteryChange() {
    if (!showMasteryConfirm) return;
    setMastery(showMasteryConfirm);
    // Drop mastery-specific skills that don't belong to the new mastery
    setDraftSkills((prev) =>
      prev.filter((ds) => {
        const def = CLASS_SKILLS[characterClass].find((s) => s.name === ds.skill_name);
        return !def?.mastery || def.mastery === showMasteryConfirm;
      })
    );
    setShowMasteryConfirm(null);
  }

  function handleVote(direction: 1 | -1) {
    if (!user) { toast.error("Sign in to vote"); return; }
    vote.mutate(
      { slug: build.slug, direction },
      {
        onSuccess: (res) => {
          if (res.errors) toast.error(res.errors[0]?.message ?? "Vote failed");
        },
        onError: () => toast.error("Vote failed"),
      }
    );
  }

  function addSkill(skillName: string) {
    if (draftSkills.length >= MAX_SKILLS) { toast.error(`Max ${MAX_SKILLS} skills`); return; }
    setDraftSkills((prev) => [...prev, { skill_name: skillName, slot: prev.length + 1, points_allocated: 20, spec_tree: [] }]);
  }

  function removeSkill(index: number) {
    setDraftSkills((prev) => prev.filter((_, i) => i !== index).map((s, i) => ({ ...s, slot: i + 1 })));
  }

  function setPoints(index: number, points: number) {
    setDraftSkills((prev) => prev.map((s, i) => i === index ? { ...s, points_allocated: points } : s));
  }

  function cancelEdit() {
    // Reset form to current build values
    setName(build.name);
    setDescription(build.description ?? "");
    setLevel(build.level);
    setIsSsf(build.is_ssf);
    setIsHc(build.is_hc);
    setIsLadder(build.is_ladder_viable);
    setIsBudget(build.is_budget);
    setDraftSkills(build.skills.map((s) => ({ skill_name: s.skill_name, slot: s.slot, points_allocated: s.points_allocated, spec_tree: s.spec_tree ?? [] })));
    setPassiveTree(build.passive_tree ?? []);
    setGearSlots(build.gear ?? []);
    setDraftBlessings(build.blessings ?? []);
    setEditing(false);
  }

  async function handleSave() {
    if (!name.trim()) { toast.error("Build name is required"); return; }
    const res = await updateBuild.mutateAsync({
      slug: build.slug,
      payload: {
        name: name.trim(),
        description: description.trim() || undefined,
        mastery,
        level,
        is_ssf: isSsf,
        is_hc: isHc,
        is_ladder_viable: isLadder,
        is_budget: isBudget,
        skills: draftSkills.map((s) => ({ skill_name: s.skill_name, slot: s.slot, points_allocated: s.points_allocated, spec_tree: s.spec_tree })) as Partial<BuildSkill>[],
        passive_tree: passiveTree,
        gear: gearSlots,
        blessings: draftBlessings,
      },
    });
    if (res.errors) { toast.error(res.errors[0]?.message ?? "Update failed"); return; }
    toast.success("Build updated!");
    setEditing(false);
  }

  // ── View mode ──
  if (!editing) {
    const currentPatch = versionRes?.data?.current_patch;
    const patchMismatch = currentPatch && build.patch_version && build.patch_version !== currentPatch;

    return (
      <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr] min-w-0">
        {patchMismatch && (
          <div className="lg:col-span-2 flex items-start gap-3 rounded border border-forge-amber/40 bg-forge-amber/8 px-4 py-3 text-sm">
            <span className="text-forge-amber font-display font-bold shrink-0">⚠ Outdated build</span>
            <span className="text-forge-muted font-body">
              This build was created for patch <strong className="text-forge-text">{build.patch_version}</strong>{" "}
              but the current patch is <strong className="text-forge-text">{currentPatch}</strong>.
              Stats and skills may have changed — verify before using.
            </span>
          </div>
        )}
        <Panel title="Overview">
          <div className="space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h1 className="font-display text-4xl font-bold text-forge-amber tracking-wider">{build.name}</h1>
                {build.description && (
                  <p className="mt-2 max-w-3xl font-body text-sm leading-relaxed text-forge-muted">{build.description}</p>
                )}
              </div>
              {isOwner && (
                <Button variant="outline" size="sm" onClick={() => setEditing(true)}>Edit</Button>
              )}
            </div>

            {/* Action row */}
            <div className="flex flex-wrap gap-2">
              <Button
                variant="primary"
                size="sm"
                onClick={() => simulateMutation.mutate()}
                disabled={simulateMutation.isPending}
              >
                {simulateMutation.isPending ? "Analyzing…" : "⚡ Analyze Build"}
              </Button>
              {simResult && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowDashboard((v) => !v)}
                >
                  {showDashboard ? "Hide Results" : "Show Results"}
                </Button>
              )}
              <Button variant="ghost" size="sm" onClick={handleExport}>
                ↓ Export JSON
              </Button>
            </div>

            <div className="flex flex-wrap gap-2">
              <Badge variant="class">{build.character_class}</Badge>
              <Badge variant="mastery">{build.mastery}</Badge>
              {build.tier && (
                <Badge variant={`tier-${build.tier.toLowerCase()}` as "tier-s" | "tier-a" | "tier-b" | "tier-c"}>
                  {build.tier}
                </Badge>
              )}
              {build.is_ssf && <Badge variant="ssf">SSF</Badge>}
              {build.is_hc && <Badge variant="hc">HC</Badge>}
              {build.is_ladder_viable && <Badge variant="ladder">Ladder</Badge>}
              {build.is_budget && <Badge variant="budget">Budget</Badge>}
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <div className="rounded border border-forge-border bg-forge-surface2 p-4">
                <div className={labelCls}>Level</div>
                <div className="mt-2 font-display text-2xl text-forge-text">{build.level}</div>
              </div>
              <div className="rounded border border-forge-border bg-forge-surface2 p-4">
                <div className={labelCls}>Votes</div>
                <div className="mt-2 flex items-center gap-3">
                  <span className="font-display text-2xl text-forge-text">{build.vote_count}</span>
                  <div className="flex gap-1">
                    <button onClick={() => handleVote(1)} disabled={vote.isPending}
                      className={`px-2 py-0.5 rounded text-xs border transition-colors ${build.user_vote === 1 ? "border-forge-amber bg-forge-amber/20 text-forge-amber" : "border-forge-border text-forge-dim hover:border-forge-amber hover:text-forge-amber"}`}>▲</button>
                    <button onClick={() => handleVote(-1)} disabled={vote.isPending}
                      className={`px-2 py-0.5 rounded text-xs border transition-colors ${build.user_vote === -1 ? "border-red-500 bg-red-500/20 text-red-400" : "border-forge-border text-forge-dim hover:border-red-500 hover:text-red-400"}`}>▼</button>
                  </div>
                </div>
              </div>
              <div className="rounded border border-forge-border bg-forge-surface2 p-4">
                <div className={labelCls}>Views</div>
                <div className="mt-2 font-display text-2xl text-forge-text">{build.view_count}</div>
              </div>
            </div>
          </div>
        </Panel>

        <Panel title="Snapshot">
          <dl className="space-y-4">
            {([["Patch", build.patch_version], ["Cycle", build.cycle], ["Passive Nodes", build.passive_tree.length], ["Skills", build.skills.length], ["Gear Slots", build.gear.length]] as [string, string | number][]).map(([label, value]) => (
              <div key={label}>
                <dt className={labelCls}>{label}</dt>
                <dd className="mt-1 font-body text-sm text-forge-text">{value}</dd>
              </div>
            ))}
          </dl>
        </Panel>

        {build.gear.length > 0 && (
          <Panel title={`Gear (${build.gear.length} equipped)`}>
            <GearEditor
              gear={build.gear}
              onChange={() => {}}
              readOnly
            />
          </Panel>
        )}

        <Panel title="Skills" className="lg:col-span-2">
          {build.skills.length ? (
            <SkillSelector
              skills={build.skills.map((s) => ({
                skill_name: s.skill_name,
                slot: s.slot,
                points_allocated: s.points_allocated,
                spec_tree: s.spec_tree,
              }))}
              characterClass={build.character_class}
              mastery={build.mastery}
              buildSlug={build.slug}
              readOnly={!isOwner || !editing}
            />
          ) : (
            <EmptyState title="No skills saved" description="This build does not have specialized skills attached yet." />
          )}
        </Panel>

        <Panel title="Passive Tree" className="lg:col-span-2">
          <BuildPassiveTree
            characterClass={build.character_class}
            mastery={build.mastery}
            allocated={(() => {
              const map: AllocMap = {};
              for (const id of (build.passive_tree ?? [])) map[id] = (map[id] ?? 0) + 1;
              return map;
            })()}
            onAllocate={() => {}}
            readOnly
          />
          {(build.passive_tree?.length ?? 0) > 0 && (
            <div className="mt-3 min-w-0 overflow-hidden">
              <PassiveProgressBar
                history={build.passive_tree ?? []}
                characterClass={build.character_class}
                readOnly
              />
            </div>
          )}
        </Panel>

        {/* Simulation results — restructured 6-section UX */}
        {showDashboard && simResult && (
          <div className="mt-2 flex flex-col gap-6 min-w-0">
            {/* SECTION 1 — Build Score Card (hero, above fold) */}
            <BuildScoreCard
              skillName={simResult.primary_skill}
              characterClass={build.character_class}
              mastery={build.mastery}
              dps={simResult.dps.total_dps ?? simResult.dps.dps ?? 0}
              effectiveHp={simResult.defense.effective_hp}
              survivabilityScore={simResult.defense.survivability_score}
              weaknesses={simResult.defense.weaknesses ?? []}
              topUpgrade={simResult.stat_upgrades?.[0]?.label ?? null}
            />

            {/* SECTION 2 — Offense vs Defense split */}
            <OffenseDefenseSplit
              dps={simResult.dps}
              defense={simResult.defense}
              stats={simResult.stats}
            />

            {/* SECTION 3 — Primary skill breakdown */}
            <PrimarySkillBreakdown
              skillName={simResult.primary_skill}
              dps={simResult.dps}
              skills={simResult.dps_per_skill}
            />

            {/* SECTION 4 — All skills summary */}
            <AllSkillsSummary
              skills={build.skills.map((s) => ({
                slot: s.slot,
                skill_name: s.skill_name,
                points_allocated: s.points_allocated,
              }))}
              dpsPerSkill={simResult.dps_per_skill}
            />

            {/* SECTION 5 — What To Improve Next */}
            <div className="flex flex-col gap-3 min-w-0">
              <div className="flex flex-col gap-1">
                <h3 className="font-display text-lg font-bold tracking-wider text-forge-text">
                  What To Improve Next
                </h3>
                <p className="font-body text-sm text-forge-dim">
                  Highest-impact stat upgrades and affix swaps ranked by simulated DPS &amp; effective HP gains.
                </p>
              </div>
              <div className="grid gap-4 lg:grid-cols-2">
                <StatUpgradePanel
                  rankings={optimizeQuery.data?.stat_rankings ?? []}
                  mode={optimizeMode}
                  onModeChange={setOptimizeMode}
                  isLoading={optimizeQuery.isLoading}
                  error={optimizeQuery.error}
                  onRetry={() => optimizeQuery.refetch()}
                />
                <UpgradeCandidatesPanel
                  candidates={optimizeQuery.data?.top_upgrade_candidates ?? []}
                  isLoading={optimizeQuery.isLoading}
                  error={optimizeQuery.error}
                  onRetry={() => optimizeQuery.refetch()}
                />
              </div>
            </div>

            {/* SECTION 6 — Advanced Analysis (collapsed by default) */}
            {build.slug && (
              <AccordionSection
                title="Advanced Analysis — Boss Encounters, Corruption Scaling & Gear Upgrades"
                storageKey="forge_advanced_analysis_open"
                defaultOpen={false}
              >
                <div className="grid gap-4 lg:grid-cols-2 min-w-0">
                  <BossEncounterPanel slug={build.slug} />
                  <CorruptionScalingPanel slug={build.slug} />
                </div>
                <GearUpgradePanel slug={build.slug} />
              </AccordionSection>
            )}
          </div>
        )}
      </div>
    );
  }

  // ── Edit mode ──
  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_360px] min-w-0">
      <div className="flex flex-col gap-6 min-w-0">

        <Panel title="Edit Build">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block md:col-span-2">
              <SectionLabel>Build Name</SectionLabel>
              <input value={name} onChange={(e) => setName(e.target.value)} className={inputCls + " mt-1.5"} />
            </label>
            <label className="block md:col-span-2">
              <SectionLabel>Description (optional)</SectionLabel>
              <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={2} className={inputCls + " mt-1.5 resize-none"} />
            </label>

            {/* Class is fixed at creation; mastery can be changed */}
            <div className="block">
              <SectionLabel>Class</SectionLabel>
              <div className={inputCls + " mt-1.5 opacity-50 cursor-not-allowed"}>{characterClass}</div>
            </div>
            <label className="block">
              <SectionLabel>Mastery</SectionLabel>
              <select
                value={mastery}
                onChange={(e) => handleMasteryChangeRequest(e.target.value)}
                className={inputCls + " mt-1.5"}
              >
                {masteryOptions.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </label>

            <label className="block">
              <SectionLabel>Level</SectionLabel>
              <input type="number" min={1} max={100} value={level}
                onChange={(e) => setLevel(Math.min(100, Math.max(1, Number(e.target.value) || 1)))}
                className={inputCls + " mt-1.5"} />
            </label>

            <div className="flex flex-col justify-end gap-3 pb-1">
              <SectionLabel>Tags</SectionLabel>
              <div className="flex flex-wrap gap-4">
                <FlagToggle label="SSF" checked={isSsf} onChange={setIsSsf} />
                <FlagToggle label="Hardcore" checked={isHc} onChange={setIsHc} />
                <FlagToggle label="Ladder viable" checked={isLadder} onChange={setIsLadder} />
                <FlagToggle label="Budget" checked={isBudget} onChange={setIsBudget} />
              </div>
            </div>
          </div>
        </Panel>

        {/* Consolidated skills section — single panel with per-slot point
            controls, expand/collapse toggle, and inline skill tree view. */}
        <Panel title={`Skills (${draftSkills.length}/${MAX_SKILLS})`}>
          <SkillSelector
            skills={draftSkills.map((s) => ({
              skill_name: s.skill_name,
              slot: s.slot,
              points_allocated: s.points_allocated,
              spec_tree: s.spec_tree,
            }))}
            characterClass={characterClass}
            mastery={mastery}
            buildSlug={build.slug}
            onAddSkill={addSkill}
            onRemoveSkill={removeSkill}
            onPointsChange={setPoints}
            maxSkillLevel={MAX_SKILL_LEVEL}
          />
        </Panel>

        <Panel title="Passive Tree">
          <BuildPassiveTree
            characterClass={characterClass}
            mastery={mastery}
            allocated={getPassiveAllocMap()}
            onAllocate={setPassiveAlloc}
          />
          <div className="mt-3 min-w-0 overflow-hidden">
            <PassiveProgressBar
              history={passiveTree}
              characterClass={characterClass}
              onRewindTo={rewindPassiveTo}
            />
          </div>
        </Panel>
      </div>

      <div className="flex flex-col gap-6 min-w-0">
        <Panel title={`Gear (${gearSlots.length} equipped)`}>
          <GearEditor
            gear={gearSlots}
            onChange={setGearSlots}
          />
        </Panel>

        <BlessingsPanel
          selectedBlessings={draftBlessings}
          onChange={setDraftBlessings}
        />

        <Panel title="Save Changes">
          <div className="flex flex-col gap-3">
            <Button onClick={handleSave} disabled={updateBuild.isPending || !name.trim()} className="w-full">
              {updateBuild.isPending ? "Saving…" : "Save Changes"}
            </Button>
            <Button variant="ghost" onClick={cancelEdit} className="w-full">Cancel</Button>
          </div>
        </Panel>
      </div>

      {/* Mastery change confirmation modal */}
      {showMasteryConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="w-full max-w-sm rounded-lg border border-forge-border bg-forge-bg p-6 shadow-2xl">
            <h3 className="font-display text-lg font-bold text-forge-amber">Change Mastery?</h3>
            <p className="mt-2 font-body text-sm text-forge-muted">
              Switching from <strong className="text-forge-text">{mastery}</strong> to{" "}
              <strong className="text-forge-text">{showMasteryConfirm}</strong> will remove
              skills exclusive to your current mastery. Passive tree allocations will be preserved
              but mastery-specific nodes may become locked.
            </p>
            <div className="mt-4 flex gap-3 justify-end">
              <Button variant="outline" size="sm" onClick={() => setShowMasteryConfirm(null)}>
                Cancel
              </Button>
              <Button size="sm" onClick={confirmMasteryChange}>
                Confirm
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Build planner (create mode)
// ---------------------------------------------------------------------------
export default function BuildPlannerPage() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { data, isLoading } = useBuild(slug ?? "");
  const createBuild = useCreateBuild();
  const { user } = useAuthStore();

  // URL-driven class override: links like /build?class=Acolyte (e.g. from the
  // Classes page) must win over any autosaved draft so navigating with intent
  // never silently drops back to the previous class. Validated against
  // CHARACTER_CLASSES so unknown/malformed values fall through to defaults.
  const urlClassParam = searchParams.get("class");
  const urlClass: CharacterClass | null =
    urlClassParam && (CHARACTER_CLASSES as readonly string[]).includes(urlClassParam)
      ? (urlClassParam as CharacterClass)
      : null;

  // Form state
  const [name, setName] = useState("New Forge Build");
  const [description, setDescription] = useState("");
  const [characterClass, setCharacterClass] = useState<CharacterClass>(urlClass ?? "Sentinel");
  const [mastery, setMastery] = useState(MASTERIES[urlClass ?? "Sentinel"][0]);
  const [level, setLevel] = useState(70);
  const [isSsf, setIsSsf] = useState(false);
  const [isHc, setIsHc] = useState(false);
  const [isLadder, setIsLadder] = useState(false);
  const [isBudget, setIsBudget] = useState(false);
  const [draftSkills, setDraftSkills] = useState<DraftSkill[]>([]);
  const [passiveTree, setPassiveTree] = useState<number[]>([]);
  const [draftGear, setDraftGear] = useState<GearSlot[]>([]);
  const [draftBlessings, setDraftBlessings] = useState<SelectedBlessing[]>([]);
  const [hasDraft, setHasDraft] = useState(false);
  // Informational banner — set when we had to override a stored draft's class
  // with the one from the URL. The draft stays on disk so the user can undo.
  const [urlClassOverride, setUrlClassOverride] = useState<{
    from: CharacterClass;
    to: CharacterClass;
  } | null>(null);

  // Import / preset modal state — auto-open if ?import=true in URL
  const [showImportModal, setShowImportModal] = useState(
    () => new URLSearchParams(window.location.search).get("import") === "true"
  );
  const [showPresets, setShowPresets] = useState(false);

  function handleApplyImport(imported: ImportedBuild) {
    if (imported.name) setName(imported.name);
    if (imported.description) setDescription(imported.description);
    if (imported.character_class) handleClassChange(imported.character_class as CharacterClass);
    if (imported.mastery) setMastery(imported.mastery);
    if (typeof imported.level === "number") setLevel(imported.level);
    if (typeof (imported as any).is_ssf === "boolean") setIsSsf((imported as any).is_ssf);
    if (typeof (imported as any).is_hc === "boolean") setIsHc((imported as any).is_hc);
    if (typeof (imported as any).is_ladder_viable === "boolean") setIsLadder((imported as any).is_ladder_viable);
    if (typeof (imported as any).is_budget === "boolean") setIsBudget((imported as any).is_budget);
    if (Array.isArray(imported.passive_tree)) setPassiveTree(imported.passive_tree);
    if (Array.isArray(imported.skills)) {
      setDraftSkills(imported.skills.map((s) => ({
        skill_name: s.skill_name,
        slot: s.slot ?? 1,
        points_allocated: s.points_allocated ?? 20,
        spec_tree: Array.isArray(s.spec_tree) ? s.spec_tree : [],
      })));
    }
    if (Array.isArray(imported.gear) && imported.gear.length > 0) {
      setDraftGear(imported.gear as GearSlot[]);
    }
  }

  function handleLoadPreset(presetId: string) {
    const preset = PRESETS.find((p) => p.id === presetId);
    if (!preset) return;
    handleClassChange(preset.character_class);
    setMastery(preset.mastery);
    setName(`${preset.label} (Template)`);
    setDescription(preset.description);
    setLevel(preset.level);
    setIsSsf(preset.tags.is_ssf ?? false);
    setIsHc(preset.tags.is_hc ?? false);
    setIsLadder(preset.tags.is_ladder_viable ?? false);
    setIsBudget(preset.tags.is_budget ?? false);
    setDraftSkills([{ skill_name: preset.primary_skill, slot: 1, points_allocated: 20, spec_tree: [] }]);
    setPassiveTree([]);
    setShowPresets(false);
    toast.success(`Loaded preset: ${preset.label}`);
  }

  // ---------------------------------------------------------------------------
  // Draft save / restore (only for new builds, not when editing an existing slug)
  // ---------------------------------------------------------------------------
  const DRAFT_KEY = "forge_draft_build";
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Restore draft on mount for new builds only. When a ?class= URL param is
  // present it takes priority over the draft's class/mastery — the rest of
  // the draft (name, level, skills, passive tree, etc.) still restores so the
  // user's in-progress work isn't thrown away. A banner below surfaces the
  // override so the swap isn't silent.
  useEffect(() => {
    if (slug) return; // editing existing — don't overwrite
    const raw = localStorage.getItem(DRAFT_KEY);
    if (!raw) return;
    try {
      const draft = JSON.parse(raw);
      if (draft.name) setName(draft.name);
      if (draft.description) setDescription(draft.description);
      const draftClass: CharacterClass | undefined = draft.characterClass;
      if (urlClass) {
        // URL param wins. Keep the draft's class on the override banner so the
        // user can see what was swapped.
        setCharacterClass(urlClass);
        setMastery(MASTERIES[urlClass][0]);
        // Drop skills tied to a different class — they'd be invalid anyway.
        if (draftClass && draftClass !== urlClass) {
          setUrlClassOverride({ from: draftClass, to: urlClass });
        } else if (Array.isArray(draft.draftSkills)) {
          setDraftSkills(draft.draftSkills);
        }
      } else {
        if (draftClass) setCharacterClass(draftClass);
        if (draft.mastery) setMastery(draft.mastery);
        if (Array.isArray(draft.draftSkills)) setDraftSkills(draft.draftSkills);
      }
      if (typeof draft.level === "number") setLevel(draft.level);
      if (typeof draft.isSsf === "boolean") setIsSsf(draft.isSsf);
      if (typeof draft.isHc === "boolean") setIsHc(draft.isHc);
      if (typeof draft.isLadder === "boolean") setIsLadder(draft.isLadder);
      if (typeof draft.isBudget === "boolean") setIsBudget(draft.isBudget);
      if (Array.isArray(draft.passiveTree)) setPassiveTree(draft.passiveTree);
      if (Array.isArray(draft.draftBlessings)) setDraftBlessings(draft.draftBlessings);
      setHasDraft(true);
    } catch {
      localStorage.removeItem(DRAFT_KEY);
    }
    // urlClass is derived synchronously from searchParams at render time —
    // the effect should run only on mount / slug change, matching the
    // original behaviour. Re-reading urlClass here would re-apply the draft
    // on every render.
  }, [slug]);

  // Auto-save draft to localStorage (debounced 1.5s) for new builds only
  useEffect(() => {
    if (slug) return;
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(() => {
      const draft = { name, description, characterClass, mastery, level, isSsf, isHc, isLadder, isBudget, draftSkills, passiveTree, draftBlessings };
      localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
    }, 1500);
    return () => { if (saveTimerRef.current) clearTimeout(saveTimerRef.current); };
  }, [slug, name, description, characterClass, mastery, level, isSsf, isHc, isLadder, isBudget, draftSkills, passiveTree, draftBlessings]);

  // Track view on mount (fire and forget — no loading/error state)
  useEffect(() => {
    if (slug) {
      viewApi.track(slug).catch(() => {});
    }
  }, [slug]);

  function clearDraft() {
    localStorage.removeItem(DRAFT_KEY);
    setHasDraft(false);
  }

  function getPassiveAllocMap(): AllocMap {
    const map: AllocMap = {};
    for (const id of passiveTree) map[id] = (map[id] ?? 0) + 1;
    return map;
  }

  function setPassiveAlloc(nodeId: number, points: number) {
    setPassiveTree((prev) => {
      const current = prev.filter(id => id === nodeId).length;
      if (points > current) {
        return [...prev, nodeId];
      } else if (points < current) {
        const idx = prev.lastIndexOf(nodeId);
        return idx === -1 ? prev : [...prev.slice(0, idx), ...prev.slice(idx + 1)];
      }
      return prev;
    });
  }

  function rewindPassiveTo(stepIndex: number) {
    setPassiveTree(prev => prev.slice(0, stepIndex));
  }

  const masteryOptions = useMemo(() => MASTERIES[characterClass], [characterClass]);

  function handleClassChange(next: CharacterClass) {
    setCharacterClass(next);
    setMastery(MASTERIES[next][0]);
    setDraftSkills([]);
  }

  function handleMasteryChange(next: string) {
    setMastery(next);
    // Drop skills that belong to a different mastery
    setDraftSkills((prev) =>
      prev.filter((ds) => {
        const def = (CLASS_SKILLS[characterClass] ?? []).find((s) => s.name === ds.skill_name);
        return !def?.mastery || def.mastery === next;
      })
    );
  }

  function addSkill(skillName: string) {
    if (draftSkills.length >= MAX_SKILLS) {
      toast.error(`Max ${MAX_SKILLS} skills per build`);
      return;
    }
    setDraftSkills((prev) => [
      ...prev,
      { skill_name: skillName, slot: prev.length + 1, points_allocated: 20, spec_tree: [] },
    ]);
  }

  function removeSkill(index: number) {
    setDraftSkills((prev) =>
      prev
        .filter((_, i) => i !== index)
        .map((s, i) => ({ ...s, slot: i + 1 }))
    );
  }

  function setPoints(index: number, points: number) {
    setDraftSkills((prev) =>
      prev.map((s, i) => (i === index ? { ...s, points_allocated: points } : s))
    );
  }

  // Updates draft spec_tree when the user allocates a skill-tree node before
  // saving. spec_tree stores one entry per point (e.g. [5,5,5] = 3 pts on
  // node 5), so we strip all existing entries for this node and push `points`
  // copies back in.
  function setTreeAlloc(skillIndex: number, nodeId: number, points: number) {
    setDraftSkills((prev) =>
      prev.map((s, i) => {
        if (i !== skillIndex) return s;
        const tree = (s.spec_tree ?? []).filter((id) => id !== nodeId);
        const updated = points >= 1 ? [...tree, ...Array(points).fill(nodeId)] : tree;
        return { ...s, spec_tree: updated };
      })
    );
  }

  async function handleSave() {
    if (!name.trim()) { toast.error("Build name is required"); return; }

    const payload = {
      name: name.trim(),
      description: description.trim() || undefined,
      character_class: characterClass,
      mastery,
      level,
      is_ssf: isSsf,
      is_hc: isHc,
      is_ladder_viable: isLadder,
      is_budget: isBudget,
      skills: draftSkills.map((s) => ({
        skill_name: s.skill_name,
        slot: s.slot,
        points_allocated: s.points_allocated,
        spec_tree: s.spec_tree,
      })) as Partial<BuildSkill>[],
      passive_tree: passiveTree,
      gear: draftGear,
      blessings: draftBlessings,
    };

    const res = await createBuild.mutateAsync(payload);

    if (res.errors) {
      toast.error(res.errors[0]?.message ?? "Failed to save build");
      return;
    }

    clearDraft();
    toast.success("Build saved!");
    if (res.data?.slug) navigate(`/build/${res.data.slug}`);
  }

  // ── Loading / not-found states ──
  if (slug && isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Spinner size={28} />
      </div>
    );
  }

  if (slug && !isLoading && !data?.data) {
    return (
      <EmptyState
        title="Build not found"
        description="This build could not be loaded."
        action={<Link to="/builds"><Button size="sm">Back to Builds</Button></Link>}
      />
    );
  }

  if (data?.data) return <BuildSummary build={data.data} />;

  // ── Create form ──
  const pageTitle = slug ? `${data?.data?.name ?? "Build"} — Build Planner` : "Build Planner";
  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_360px] min-w-0">
      <PageMeta
        title={pageTitle}
        description="Plan your Last Epoch build with interactive passive tree, skill specializations, gear editor, and real-time DPS simulation."
        path={slug ? `/build/${slug}` : "/build"}
      />

      {/* Draft / auth banners */}
      {!user && (
        <div className="xl:col-span-2 flex items-center justify-between gap-4 rounded border border-forge-amber/30 bg-forge-amber/8 px-4 py-3">
          <div className="flex items-center gap-3">
            <span className="text-forge-amber text-sm">⚠</span>
            <span className="font-body text-sm text-forge-muted">
              {hasDraft
                ? "Draft restored from local storage. "
                : "Your build is saved locally. "}
              <span className="text-forge-amber">Sign in to save permanently and share with the community.</span>
            </span>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            {hasDraft && (
              <Button variant="danger" size="sm" onClick={clearDraft}>
                Clear Draft
              </Button>
            )}
            <a
              href={`${import.meta.env.VITE_API_URL ?? "/api"}/auth/discord`}
              onClick={() => sessionStorage.setItem("forge_login_attempted", "1")}
            >
              <Button variant="primary" size="sm">Sign In</Button>
            </a>
          </div>
        </div>
      )}

      {hasDraft && user && (
        <div className="xl:col-span-2 flex items-center justify-between gap-4 rounded border border-forge-cyan/30 bg-forge-cyan/8 px-4 py-3">
          <span className="font-body text-sm text-forge-muted">
            <span className="text-forge-cyan">Draft restored.</span> Fill in the details and save.
          </span>
          <Button variant="ghost" size="sm" onClick={clearDraft}>
            Clear Draft
          </Button>
        </div>
      )}

      {urlClassOverride && (
        <div className="xl:col-span-2 flex items-center justify-between gap-4 rounded border border-forge-amber/40 bg-forge-amber/8 px-4 py-3">
          <span className="font-body text-sm text-forge-muted">
            <span className="text-forge-amber">URL class applied.</span> Switched to{" "}
            <strong className="text-forge-text">{urlClassOverride.to}</strong> from your{" "}
            <strong className="text-forge-text">{urlClassOverride.from}</strong> draft. Other draft
            fields (name, level, gear, tags) were preserved.
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              // Revert to the draft's class; the banner closes and the draft
              // stays intact on disk.
              const from = urlClassOverride.from;
              setCharacterClass(from);
              setMastery(MASTERIES[from][0]);
              setUrlClassOverride(null);
            }}
          >
            Use draft class
          </Button>
        </div>
      )}

      {/* Quick start: presets + import */}
      <div className="xl:col-span-2 flex items-center gap-3">
        <Button variant="outline" size="sm" onClick={() => setShowPresets((v) => !v)}>
          📋 Load Preset
        </Button>
        <Button variant="ghost" size="sm" onClick={() => setShowImportModal(true)}>
          ↑ Import Build
        </Button>
      </div>

      {showPresets && (
        <div className="xl:col-span-2 rounded border border-forge-border bg-forge-surface2 p-4">
          <div className="font-mono text-xs uppercase tracking-widest text-forge-muted mb-3">Select a preset</div>
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
            {PRESETS.map((p) => (
              <button
                key={p.id}
                onClick={() => handleLoadPreset(p.id)}
                className="text-left rounded border border-forge-border bg-forge-surface hover:border-forge-amber/60 hover:bg-forge-amber/5 p-3 transition-colors"
              >
                <div className="font-display text-sm font-bold text-forge-amber">{p.label}</div>
                <div className="font-mono text-[10px] text-forge-cyan mt-0.5">{p.character_class} · {p.mastery}</div>
                <p className="font-body text-xs text-forge-dim mt-1 leading-snug line-clamp-2">{p.description}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {showImportModal && (
        <BuildImportModal
          onImport={handleApplyImport}
          onClose={() => setShowImportModal(false)}
        />
      )}

      {/* ── LEFT: main form ── */}
      <div className="flex flex-col gap-6 min-w-0">

        {/* Identity */}
        <Panel title="Build Identity">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block md:col-span-2">
              <SectionLabel>Build Name</SectionLabel>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                className={inputCls + " mt-1.5"}
                placeholder="e.g. Bone Minion Necromancer"
              />
            </label>

            <label className="block md:col-span-2">
              <SectionLabel>Description (optional)</SectionLabel>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
                className={inputCls + " mt-1.5 resize-none"}
                placeholder="Brief description of the build strategy..."
              />
            </label>

            <label className="block">
              <SectionLabel>Class</SectionLabel>
              <select
                value={characterClass}
                onChange={(e) => handleClassChange(e.target.value as CharacterClass)}
                className={inputCls + " mt-1.5"}
              >
                {CHARACTER_CLASSES.map((c) => <option key={c}>{c}</option>)}
              </select>
            </label>

            <label className="block">
              <SectionLabel>Mastery</SectionLabel>
              <select
                value={mastery}
                onChange={(e) => handleMasteryChange(e.target.value)}
                className={inputCls + " mt-1.5"}
              >
                {masteryOptions.map((m) => <option key={m}>{m}</option>)}
              </select>
            </label>

            <label className="block">
              <SectionLabel>Level</SectionLabel>
              <input
                type="number"
                min={1}
                max={100}
                value={level}
                onChange={(e) => setLevel(Math.min(100, Math.max(1, Number(e.target.value) || 1)))}
                className={inputCls + " mt-1.5"}
              />
            </label>

            <div className="flex flex-col justify-end gap-3 pb-1">
              <SectionLabel>Tags</SectionLabel>
              <div className="flex flex-wrap gap-4">
                <FlagToggle label="SSF" checked={isSsf} onChange={setIsSsf} />
                <FlagToggle label="Hardcore" checked={isHc} onChange={setIsHc} />
                <FlagToggle label="Ladder viable" checked={isLadder} onChange={setIsLadder} />
                <FlagToggle label="Budget" checked={isBudget} onChange={setIsBudget} />
              </div>
            </div>
          </div>
        </Panel>

        {/* Consolidated skills section — single panel with per-slot point
            controls, expand/collapse toggle, and inline skill tree view. */}
        <Panel title={`Skills (${draftSkills.length}/${MAX_SKILLS})`}>
          <SkillSelector
            skills={draftSkills.map((s) => ({
              skill_name: s.skill_name,
              slot: s.slot,
              points_allocated: s.points_allocated,
              spec_tree: s.spec_tree,
            }))}
            characterClass={characterClass}
            mastery={mastery}
            onAddSkill={addSkill}
            onRemoveSkill={removeSkill}
            onPointsChange={setPoints}
            onTreeAlloc={setTreeAlloc}
            maxSkillLevel={MAX_SKILL_LEVEL}
          />
        </Panel>

        <Panel title="Passive Tree">
          <BuildPassiveTree
            characterClass={characterClass}
            mastery={mastery}
            allocated={getPassiveAllocMap()}
            onAllocate={setPassiveAlloc}
          />
          <div className="mt-3 min-w-0 overflow-hidden">
            <PassiveProgressBar
              history={passiveTree}
              characterClass={characterClass}
              onRewindTo={rewindPassiveTo}
            />
          </div>
        </Panel>
      </div>

      {/* ── RIGHT: preview + gear + save ── */}
      <div className="flex flex-col gap-6 min-w-0">
        <Panel title="Preview">
          <div className="space-y-3">
            <div className="font-display text-2xl text-forge-amber">{name || "Untitled Build"}</div>
            {description && (
              <p className="font-body text-xs text-forge-muted leading-relaxed">{description}</p>
            )}
            <div className="flex flex-wrap gap-1.5">
              <Badge variant="class">{characterClass}</Badge>
              <Badge variant="mastery">{mastery}</Badge>
              <span
                className="rounded-sm border px-2 py-0.5 font-mono text-[10px] uppercase tracking-widest"
                style={{
                  color: CLASS_COLORS[characterClass],
                  borderColor: `${CLASS_COLORS[characterClass]}55`,
                  background: `${CLASS_COLORS[characterClass]}14`,
                }}
              >
                Lv {level}
              </span>
              {isSsf && <Badge variant="ssf">SSF</Badge>}
              {isHc && <Badge variant="hc">HC</Badge>}
              {isLadder && <Badge variant="ladder">Ladder</Badge>}
              {isBudget && <Badge variant="budget">Budget</Badge>}
            </div>
            {draftSkills.length > 0 && (
              <div className="mt-2 flex flex-col gap-1">
                {draftSkills.map((s) => (
                  <div key={s.skill_name} className="flex justify-between font-mono text-[11px] text-forge-dim">
                    <span>{resolveSkillName(s.skill_name)}</span>
                    <span>{s.points_allocated} pts</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Panel>

        <Panel title={`Gear (${draftGear.length} equipped)`}>
          <QuickGearGrid
            gear={draftGear}
            onChange={setDraftGear}
          />
        </Panel>

        <BlessingsPanel
          selectedBlessings={draftBlessings}
          onChange={setDraftBlessings}
        />

        <Panel title="Save">
          <div className="flex flex-col gap-4">
            {!user && (
              <p className="font-body text-xs text-forge-dim">
                You're not signed in. The build will be saved anonymously.
              </p>
            )}
            <Button
              onClick={handleSave}
              disabled={createBuild.isPending || !name.trim()}
              className="w-full"
            >
              {createBuild.isPending ? "Saving…" : "Save Build"}
            </Button>
            <Link to="/builds">
              <Button variant="ghost" className="w-full">Browse Builds</Button>
            </Link>
          </div>
        </Panel>
      </div>

    </div>
  );
}