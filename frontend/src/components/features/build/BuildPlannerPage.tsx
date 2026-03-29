import { useMemo, useState, useEffect, useRef } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";

import { Badge, Button, EmptyState, Panel, SectionLabel, Spinner } from "@/components/ui";
import { useBuild, useCreateBuild, useUpdateBuild, useVote } from "@/hooks";
import { useAuthStore } from "@/store";
import { CLASS_COLORS, CLASS_SKILLS, MASTERIES } from "@/lib/gameData";
import type { Build, BuildSkill, CharacterClass } from "@/types";
import { versionApi, simulateApi, type BuildSimulationResult, type ImportedBuild } from "@/lib/api";
import { PRESETS } from "@/data/presets";
import SimulationDashboard from "./SimulationDashboard";
import SkillTreeGraph from "./SkillTreeGraph";
import PassiveTreeGraph from "./PassiveTreeGraph";
import PassiveProgressBar from "./PassiveProgressBar";
import BuildImportModal from "./BuildImportModal";
import GearEditor from "./GearEditor";
import { getSkillTree, hasSkillTree } from "@/data/skillTrees";
import type { GearSlot } from "@/types";

const CHARACTER_CLASSES: CharacterClass[] = ["Acolyte", "Mage", "Primalist", "Sentinel", "Rogue"];
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
// Skill row inside the picker
// ---------------------------------------------------------------------------
interface DraftSkill {
  skill_name: string;
  slot: number;
  points_allocated: number;
  spec_tree: number[];
}

function SkillRow({
  skill, onRemove, onPoints, onOpenTree,
}: { skill: DraftSkill; onRemove: () => void; onPoints: (p: number) => void; onOpenTree: () => void }) {
  const hasTree = hasSkillTree(skill.skill_name);
  return (
    <div className="flex items-center gap-3 rounded border border-forge-border bg-forge-surface2 px-3 py-2">
      <span className="flex-1 font-body text-sm text-forge-text truncate">{skill.skill_name}</span>
      <span className="font-mono text-[10px] text-forge-dim w-4 text-center">{skill.slot}</span>
      <input
        type="number"
        min={0}
        max={MAX_SKILL_LEVEL}
        value={skill.points_allocated}
        onChange={(e) => onPoints(Math.min(MAX_SKILL_LEVEL, Math.max(0, Number(e.target.value) || 0)))}
        className="w-14 rounded-sm border border-forge-border bg-forge-bg px-2 py-0.5 font-mono text-xs text-forge-text outline-none focus:border-forge-amber/60 text-center"
        title={`Skill level (0–${MAX_SKILL_LEVEL}; base cap 20, gear can push higher)`}
      />
      <button
        onClick={onOpenTree}
        className={`font-mono text-xs leading-none transition-colors ${hasTree ? "text-forge-amber hover:text-amber-300" : "text-forge-dim hover:text-forge-muted"}`}
        title={hasTree ? "View skill tree" : "No tree data for this skill yet"}
      >🌿</button>
      <button
        onClick={onRemove}
        className="text-forge-dim hover:text-red-400 transition-colors font-mono text-xs leading-none"
        title="Remove skill"
      >✕</button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Skill tree modal
// ---------------------------------------------------------------------------
interface AllocMap { [nodeId: number]: number }

function SkillTreeModal({
  skillName, allocated, onAllocate, onClose, readOnly,
}: {
  skillName: string;
  allocated: AllocMap;
  onAllocate: (nodeId: number, points: number) => void;
  onClose: () => void;
  readOnly?: boolean;
}) {
  const nodes = getSkillTree(skillName);
  const totalPoints = Object.values(allocated).reduce((a, b) => a + b, 0);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" onClick={onClose}>
      <div
        className="relative w-full max-w-2xl rounded border border-forge-border bg-forge-bg shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-forge-border px-4 py-3">
          <div>
            <span className="font-display text-lg text-forge-amber">{skillName}</span>
            <span className="ml-3 font-mono text-xs text-forge-dim">
              {totalPoints} node{totalPoints !== 1 ? "s" : ""} allocated
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-forge-dim hover:text-forge-text font-mono text-sm transition-colors"
          >✕ Close</button>
        </div>
        {nodes.length ? (
          <SkillTreeGraph nodes={nodes} allocated={allocated} onAllocate={onAllocate} readOnly={readOnly} skillName={skillName} />
        ) : (
          <div className="flex items-center justify-center py-16 font-mono text-sm text-forge-dim">
            No tree data for this skill yet.
          </div>
        )}
        {!readOnly && (
          <div className="border-t border-forge-border px-4 py-2 text-right">
            <Button variant="outline" size="sm" onClick={onClose}>Done</Button>
          </div>
        )}
      </div>
    </div>
  );
}

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

  // Skill tree modal state: { skillIndex, readOnly }
  const [treeModal, setTreeModal] = useState<{ skillIndex: number; readOnly: boolean } | null>(null);

  // Passive tree allocation (stored as flat array of node IDs in DB)
  const [passiveTree, setPassiveTree] = useState<number[]>(build.passive_tree ?? []);

  // Gear slots
  const [gearSlots, setGearSlots] = useState<GearSlot[]>(build.gear ?? []);

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
  const mastery = build.mastery;

  const availableSkills = useMemo(
    () => CLASS_SKILLS[characterClass].filter((s) => !s.mastery || s.mastery === mastery),
    [characterClass, mastery]
  );
  const selectedNames = new Set(draftSkills.map((s) => s.skill_name));

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

  function setTreeAlloc(skillIndex: number, nodeId: number, points: number) {
    setDraftSkills((prev) => prev.map((s, i) => {
      if (i !== skillIndex) return s;
      const tree = s.spec_tree.filter((id) => id !== nodeId);
      const updated = points >= 1 ? [...tree, ...Array(points).fill(nodeId)] : tree;
      return { ...s, spec_tree: updated };
    }));
  }

  function getTreeAllocMap(skillIndex: number): AllocMap {
    const skill = draftSkills[skillIndex];
    if (!skill) return {};
    const map: AllocMap = {};
    for (const id of skill.spec_tree) map[id] = (map[id] ?? 0) + 1;
    return map;
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
    setEditing(false);
  }

  async function handleSave() {
    if (!name.trim()) { toast.error("Build name is required"); return; }
    const res = await updateBuild.mutateAsync({
      slug: build.slug,
      payload: {
        name: name.trim(),
        description: description.trim() || undefined,
        level,
        is_ssf: isSsf,
        is_hc: isHc,
        is_ladder_viable: isLadder,
        is_budget: isBudget,
        skills: draftSkills.map((s) => ({ skill_name: s.skill_name, slot: s.slot, points_allocated: s.points_allocated, spec_tree: s.spec_tree })) as Partial<BuildSkill>[],
        passive_tree: passiveTree,
        gear: gearSlots,
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
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {build.skills.map((skill, i) => {
                const nodes = getSkillTree(skill.skill_name);
                const allocMap: AllocMap = {};
                for (const id of (skill.spec_tree ?? [])) allocMap[id] = (allocMap[id] ?? 0) + 1;
                const totalNodes = Object.values(allocMap).reduce((a, b) => a + b, 0);
                return (
                  <div key={skill.id} className="rounded border border-forge-border bg-forge-surface2 p-4 flex flex-col gap-3">
                    <div>
                      <div className="font-display text-lg text-forge-text">{skill.skill_name}</div>
                      <div className="mt-1 font-mono text-[11px] uppercase tracking-widest text-forge-dim">
                        Slot {i + 1} · {skill.points_allocated} pts
                        {totalNodes > 0 && <span className="ml-2 text-forge-amber">· {totalNodes} tree nodes</span>}
                      </div>
                    </div>
                    {nodes.length > 0 ? (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setTreeModal({ skillIndex: i, readOnly: true })}
                      >
                        🌿 View Skill Tree
                      </Button>
                    ) : (
                      <span className="font-mono text-[10px] text-forge-dim italic">No tree data yet</span>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState title="No skills saved" description="This build does not have specialized skills attached yet." />
          )}
        </Panel>

        <Panel title="Passive Tree" className="lg:col-span-2">
          <PassiveTreeGraph
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

        {/* Skill tree modal (view-only) */}
        {treeModal !== null && (
          <SkillTreeModal
            skillName={build.skills[treeModal.skillIndex]?.skill_name ?? ""}
            allocated={getTreeAllocMap(treeModal.skillIndex)}
            onAllocate={() => {}}
            onClose={() => setTreeModal(null)}
            readOnly
          />
        )}

        {/* Simulation results dashboard */}
        {showDashboard && simResult && (
          <div className="mt-2">
            <SimulationDashboard result={simResult} />
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

            {/* Class & mastery are read-only — fixed at creation */}
            <div className="block">
              <SectionLabel>Class</SectionLabel>
              <div className={inputCls + " mt-1.5 opacity-50 cursor-not-allowed"}>{characterClass}</div>
            </div>
            <div className="block">
              <SectionLabel>Mastery</SectionLabel>
              <div className={inputCls + " mt-1.5 opacity-50 cursor-not-allowed"}>{mastery}</div>
            </div>

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

        <Panel title={`Skills (${draftSkills.length}/${MAX_SKILLS})`}>
          <div className="flex flex-col gap-4">
            {draftSkills.length > 0 && (
              <div className="flex flex-col gap-2">
                {draftSkills.map((skill, i) => (
                  <SkillRow key={skill.skill_name} skill={skill} onRemove={() => removeSkill(i)} onPoints={(p) => setPoints(i, p)} onOpenTree={() => setTreeModal({ skillIndex: i, readOnly: false })} />
                ))}
              </div>
            )}
            {draftSkills.length < MAX_SKILLS && (
              <div>
                <SectionLabel>Add skill — {characterClass} · {mastery}</SectionLabel>
                <div className="mt-2 flex flex-wrap gap-2">
                  {availableSkills.filter((s) => !selectedNames.has(s.name)).map((s) => (
                    <button key={s.name} onClick={() => addSkill(s.name)} title={s.tags.join(", ")}
                      className="flex items-center gap-1.5 rounded-sm border border-forge-border bg-forge-surface2 px-2.5 py-1.5 font-body text-xs text-forge-text hover:border-forge-amber/60 hover:text-forge-amber transition-colors">
                      <span>{s.icon}</span><span>{s.name}</span>
                      {s.mastery && <span className="font-mono text-[9px] text-forge-dim opacity-70">{s.mastery}</span>}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Panel>

        <Panel title="Passive Tree">
          <PassiveTreeGraph
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

        <Panel title="Save Changes">
          <div className="flex flex-col gap-3">
            <Button onClick={handleSave} disabled={updateBuild.isPending || !name.trim()} className="w-full">
              {updateBuild.isPending ? "Saving…" : "Save Changes"}
            </Button>
            <Button variant="ghost" onClick={cancelEdit} className="w-full">Cancel</Button>
          </div>
        </Panel>
      </div>

      {/* Skill tree modal (edit mode) */}
      {treeModal !== null && (
        <SkillTreeModal
          skillName={draftSkills[treeModal.skillIndex]?.skill_name ?? ""}
          allocated={getTreeAllocMap(treeModal.skillIndex)}
          onAllocate={(nodeId, pts) => setTreeAlloc(treeModal.skillIndex, nodeId, pts)}
          onClose={() => setTreeModal(null)}
          readOnly={treeModal.readOnly}
        />
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
  const { data, isLoading } = useBuild(slug ?? "");
  const createBuild = useCreateBuild();
  const { user } = useAuthStore();

  // Form state
  const [name, setName] = useState("New Forge Build");
  const [description, setDescription] = useState("");
  const [characterClass, setCharacterClass] = useState<CharacterClass>("Sentinel");
  const [mastery, setMastery] = useState(MASTERIES.Sentinel[0]);
  const [level, setLevel] = useState(70);
  const [isSsf, setIsSsf] = useState(false);
  const [isHc, setIsHc] = useState(false);
  const [isLadder, setIsLadder] = useState(false);
  const [isBudget, setIsBudget] = useState(false);
  const [draftSkills, setDraftSkills] = useState<DraftSkill[]>([]);
  const [treeModal, setTreeModal] = useState<{ skillIndex: number; readOnly: boolean } | null>(null);
  const [passiveTree, setPassiveTree] = useState<number[]>([]);
  const [draftGear, setDraftGear] = useState<GearSlot[]>([]);
  const [hasDraft, setHasDraft] = useState(false);

  // Import / preset modal state
  const [showImportModal, setShowImportModal] = useState(false);
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

  // Restore draft on mount for new builds only
  useEffect(() => {
    if (slug) return; // editing existing — don't overwrite
    const raw = localStorage.getItem(DRAFT_KEY);
    if (!raw) return;
    try {
      const draft = JSON.parse(raw);
      if (draft.name) setName(draft.name);
      if (draft.description) setDescription(draft.description);
      if (draft.characterClass) setCharacterClass(draft.characterClass);
      if (draft.mastery) setMastery(draft.mastery);
      if (typeof draft.level === "number") setLevel(draft.level);
      if (typeof draft.isSsf === "boolean") setIsSsf(draft.isSsf);
      if (typeof draft.isHc === "boolean") setIsHc(draft.isHc);
      if (typeof draft.isLadder === "boolean") setIsLadder(draft.isLadder);
      if (typeof draft.isBudget === "boolean") setIsBudget(draft.isBudget);
      if (Array.isArray(draft.draftSkills)) setDraftSkills(draft.draftSkills);
      if (Array.isArray(draft.passiveTree)) setPassiveTree(draft.passiveTree);
      setHasDraft(true);
    } catch {
      localStorage.removeItem(DRAFT_KEY);
    }
  }, [slug]);

  // Auto-save draft to localStorage (debounced 1.5s) for new builds only
  useEffect(() => {
    if (slug) return;
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(() => {
      const draft = { name, description, characterClass, mastery, level, isSsf, isHc, isLadder, isBudget, draftSkills, passiveTree };
      localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
    }, 1500);
    return () => { if (saveTimerRef.current) clearTimeout(saveTimerRef.current); };
  }, [slug, name, description, characterClass, mastery, level, isSsf, isHc, isLadder, isBudget, draftSkills, passiveTree]);

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

  // Skills available for the selected class, filtered to base + chosen mastery
  const availableSkills = useMemo(() =>
    CLASS_SKILLS[characterClass].filter(
      (s) => !s.mastery || s.mastery === mastery
    ),
    [characterClass, mastery]
  );

  const selectedNames = new Set(draftSkills.map((s) => s.skill_name));

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
        const def = CLASS_SKILLS[characterClass].find((s) => s.skill_name === ds.skill_name);
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

  function setTreeAlloc(skillIndex: number, nodeId: number, points: number) {
    setDraftSkills((prev) => prev.map((s, i) => {
      if (i !== skillIndex) return s;
      const tree = s.spec_tree.filter((id) => id !== nodeId);
      const updated = points >= 1 ? [...tree, ...Array(points).fill(nodeId)] : tree;
      return { ...s, spec_tree: updated };
    }));
  }

  function getTreeAllocMap(skillIndex: number): AllocMap {
    const skill = draftSkills[skillIndex];
    if (!skill) return {};
    const map: AllocMap = {};
    for (const id of skill.spec_tree) map[id] = (map[id] ?? 0) + 1;
    return map;
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
  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_360px] min-w-0">

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
            <a href={`${import.meta.env.VITE_API_URL ?? "/api"}/auth/discord`}>
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

        {/* Skills */}
        <Panel title={`Skills (${draftSkills.length}/${MAX_SKILLS})`}>
          <div className="flex flex-col gap-4">

            {/* Selected skills */}
            {draftSkills.length > 0 && (
              <div className="flex flex-col gap-2">
                {draftSkills.map((skill, i) => (
                  <SkillRow
                    key={skill.skill_name}
                    skill={skill}
                    onRemove={() => removeSkill(i)}
                    onPoints={(p) => setPoints(i, p)}
                    onOpenTree={() => setTreeModal({ skillIndex: i, readOnly: false })}
                  />
                ))}
              </div>
            )}

            {/* Skill picker */}
            {draftSkills.length < MAX_SKILLS && (
              <div>
                <SectionLabel>
                  Add skill — {characterClass} · {mastery}
                </SectionLabel>
                <div className="mt-2 flex flex-wrap gap-2">
                  {availableSkills
                    .filter((s) => !selectedNames.has(s.name))
                    .map((s) => (
                      <button
                        key={s.name}
                        onClick={() => addSkill(s.name)}
                        title={s.tags.join(", ")}
                        className="flex items-center gap-1.5 rounded-sm border border-forge-border bg-forge-surface2 px-2.5 py-1.5 font-body text-xs text-forge-text hover:border-forge-amber/60 hover:text-forge-amber transition-colors"
                      >
                        <span>{s.icon}</span>
                        <span>{s.name}</span>
                        {s.mastery && (
                          <span className="font-mono text-[9px] text-forge-dim opacity-70">{s.mastery}</span>
                        )}
                      </button>
                    ))}
                </div>
              </div>
            )}

            {draftSkills.length === 0 && (
              <p className="font-body text-xs text-forge-dim">
                Pick up to {MAX_SKILLS} skills to specialize. Base level cap is 20; set higher to account for +skill levels from gear.
              </p>
            )}
          </div>
        </Panel>

        <Panel title="Passive Tree">
          <PassiveTreeGraph
            characterClass={characterClass}
            mastery={mastery}
            allocated={getPassiveAllocMap()}
            onAllocate={setPassiveAlloc}
            onMasteryChange={handleMasteryChange}
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
                    <span>{s.skill_name}</span>
                    <span>{s.points_allocated} pts</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Panel>

        <Panel title={`Gear (${draftGear.length} equipped)`}>
          <GearEditor
            gear={draftGear}
            onChange={setDraftGear}
          />
        </Panel>

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

      {/* Skill tree modal (create mode) */}
      {treeModal !== null && (
        <SkillTreeModal
          skillName={draftSkills[treeModal.skillIndex]?.skill_name ?? ""}
          allocated={getTreeAllocMap(treeModal.skillIndex)}
          onAllocate={(nodeId, pts) => setTreeAlloc(treeModal.skillIndex, nodeId, pts)}
          onClose={() => setTreeModal(null)}
          readOnly={false}
        />
      )}
    </div>
  );
}