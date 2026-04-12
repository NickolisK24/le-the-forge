/**
 * SkillTreeDraftPanel — draft-mode skill tree panel.
 *
 * Mirrors SkillTreePanel but uses local `spec_tree` array (passed by the
 * parent) instead of fetching allocations from the API. All mutations flow
 * through `onAllocate`, which the parent converts back into a spec_tree
 * array so points can be persisted on save.
 *
 * spec_tree format: flat array of node IDs where each occurrence = 1 point.
 *   e.g. [5, 5, 5, 7] = 3 points on node 5, 1 point on node 7.
 */

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import { Panel, Spinner, ErrorMessage } from "@/components/ui";
import { skillsApi } from "@/lib/api";
import { getEntryIconId, getSkillTree, resolveSkillName } from "@/data/skillTrees";
import type { SkillNode } from "@/types";
import SkillTreeRenderer from "./SkillTreeRenderer";

interface Props {
  skillId: string;
  skillName: string;
  specTree: number[];
  onAllocate: (nodeId: number, points: number) => void;
  readOnly?: boolean;
}

/**
 * Convert local PassiveNode[] (from SKILL_TREES) to SkillNode[] that
 * SkillTreeRenderer expects. Mirrors SkillTreePanel's helper.
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

export default function SkillTreeDraftPanel({
  skillId,
  skillName,
  specTree,
  onAllocate,
  readOnly,
}: Props) {
  const displayName = resolveSkillName(skillName);

  // Fetch tree structure (static, cached 24h). Allocations come from
  // the draft state, not the API.
  const treeQuery = useQuery({
    queryKey: ["skill-tree", skillId],
    queryFn: () => skillsApi.getTree(skillId),
    staleTime: 24 * 60 * 60 * 1000,
    select: (res) => res.data,
    retry: false,
  });

  // Local tree fallback (used when API tree is unavailable)
  const localTree = useMemo(() => getSkillTree(skillId), [skillId]);
  const localNodes = useMemo(() => localToSkillNodes(localTree), [localTree]);

  // Derive allocation map from spec_tree: each occurrence of a node id = 1 point
  const allocMap = useMemo(() => {
    const m: Record<number, number> = {};
    for (const id of specTree) m[id] = (m[id] ?? 0) + 1;
    return m;
  }, [specTree]);

  if (treeQuery.isLoading) {
    return (
      <Panel title={`Skill Tree — ${displayName}`}>
        <div className="flex items-center justify-center py-12">
          <Spinner size={28} />
        </div>
      </Panel>
    );
  }

  const apiTree = treeQuery.data;
  const useLocal = !apiTree && localNodes.length > 0;

  if (!apiTree && !useLocal) {
    return (
      <Panel title={`Skill Tree — ${displayName}`}>
        <ErrorMessage
          title="Failed to load skill tree"
          message={(treeQuery.error as Error)?.message || "Tree data unavailable"}
          onRetry={() => { treeQuery.refetch(); }}
        />
      </Panel>
    );
  }

  let nodes: SkillNode[];
  let rootNodeId: number;
  let treeName: string;

  if (apiTree) {
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

  const handleAllocate = (nodeId: number, points: number) => {
    if (readOnly) return;
    onAllocate(nodeId, points);
  };

  return (
    <SkillTreeRenderer
      nodes={nodes}
      rootNodeId={rootNodeId}
      allocated={allocMap}
      onAllocate={handleAllocate}
      readOnly={readOnly}
      skillName={treeName}
    />
  );
}
