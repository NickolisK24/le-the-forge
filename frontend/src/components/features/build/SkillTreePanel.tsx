/**
 * SkillTreePanel — fetches tree + allocation data from API and composes
 * SkillTreeRenderer with loading/error states and mutation handling.
 *
 * Falls back to local SKILL_TREES data when the API tree is unavailable
 * (some skills exist locally but not in community_skill_trees.json).
 */

import { useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";

import { Panel, Spinner, ErrorMessage } from "@/components/ui";
import { skillsApi } from "@/lib/api";
import { getEntryIconId, getSkillTree, resolveSkillName } from "@/data/skillTrees";
import type { SkillNode } from "@/types";
import SkillTreeRenderer from "./SkillTreeRenderer";

interface Props {
  skillId: string;
  buildSlug: string;
  skillName: string;
  readOnly?: boolean;
}

/**
 * Convert local PassiveNode[] (from SKILL_TREES) to SkillNode[] that
 * SkillTreeRenderer expects.
 */
function localToSkillNodes(
  localNodes: ReturnType<typeof getSkillTree>,
): SkillNode[] {
  return localNodes.map((n) => ({
    id: n.id,
    name: n.name,
    description: n.description ?? "",
    maxPoints: n.maxPoints ?? 0,
    stats: [],
    requirements:
      n.parentId != null ? [{ node: n.parentId, requirement: 0 }] : [],
    transform: { x: n.x, y: n.y, scale: n.type === "notable" ? 1.3 : 1 },
    icon: n.iconId ?? null,
    abilityGrantedByNode: null,
  }));
}

export default function SkillTreePanel({ skillId, buildSlug, skillName, readOnly }: Props) {
  const qc = useQueryClient();
  const displayName = resolveSkillName(skillName);

  // Fetch tree structure
  const treeQuery = useQuery({
    queryKey: ["skill-tree", skillId],
    queryFn: () => skillsApi.getTree(skillId),
    staleTime: 24 * 60 * 60 * 1000, // 24 hours — tree data is static
    select: (res) => res.data,
    retry: false, // Don't retry — we fall back to local data
  });

  // Fetch current allocations for this build
  const allocQuery = useQuery({
    queryKey: ["build-skills", buildSlug],
    queryFn: () => skillsApi.getBuildSkills(buildSlug),
    staleTime: 30 * 1000,
    select: (res) => res.data,
  });

  // Mutation for allocating/deallocating nodes
  const allocMutation = useMutation({
    mutationFn: ({ nodeId, points }: { nodeId: number; points: number }) =>
      skillsApi.allocateNode(buildSlug, skillId, nodeId, points),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["build-skills", buildSlug] });
      qc.invalidateQueries({ queryKey: ["optimize", buildSlug] });
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to update node allocation");
    },
  });

  // Local tree fallback (only used when API tree is unavailable)
  const localTree = useMemo(() => getSkillTree(skillId), [skillId]);
  const localNodes = useMemo(() => localToSkillNodes(localTree), [localTree]);

  const isLoading = treeQuery.isLoading || allocQuery.isLoading;

  if (isLoading) {
    return (
      <Panel title={`Skill Tree — ${displayName}`}>
        <div className="flex items-center justify-center py-12">
          <Spinner size={28} />
        </div>
      </Panel>
    );
  }

  // Determine tree source: API first, local fallback
  const apiTree = treeQuery.data;
  const useLocal = !apiTree && localNodes.length > 0;

  if (!apiTree && !useLocal) {
    return (
      <Panel title={`Skill Tree — ${displayName}`}>
        <ErrorMessage
          title="Failed to load skill tree"
          message={(treeQuery.error as Error)?.message || "Tree data unavailable"}
          onRetry={() => { treeQuery.refetch(); allocQuery.refetch(); }}
        />
      </Panel>
    );
  }

  let nodes: SkillNode[];
  let rootNodeId: number;
  let treeName: string;

  if (apiTree) {
    // Patch root node icon from local data when the API returns null
    const entryIcon = getEntryIconId(skillId);
    nodes = apiTree.nodes.map((n) =>
      n.id === apiTree.root_node_id && n.icon == null && entryIcon
        ? { ...n, icon: entryIcon }
        : n,
    );
    rootNodeId = apiTree.root_node_id;
    treeName = apiTree.skill_name;
  } else {
    nodes = localNodes;
    rootNodeId = localNodes[0]?.id ?? 0;
    treeName = displayName;
  }

  const skillAlloc = allocQuery.data?.skills?.find((s) => s.skill_id === skillId);

  // Convert string-keyed map to number-keyed
  const allocMap: Record<number, number> = {};
  if (skillAlloc) {
    for (const [k, v] of Object.entries(skillAlloc.allocated_nodes)) {
      allocMap[Number(k)] = v;
    }
  }

  const handleAllocate = (nodeId: number, points: number) => {
    if (readOnly || useLocal) return; // Local trees are read-only (no API to persist)
    allocMutation.mutate({ nodeId, points });
  };

  return (
    <SkillTreeRenderer
      nodes={nodes}
      rootNodeId={rootNodeId}
      allocated={allocMap}
      onAllocate={handleAllocate}
      readOnly={readOnly || useLocal}
      skillName={treeName}
    />
  );
}
