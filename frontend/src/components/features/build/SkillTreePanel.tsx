/**
 * SkillTreePanel — fetches tree + allocation data from API and composes
 * SkillTreeRenderer with loading/error states and mutation handling.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";

import { Panel, Spinner, ErrorMessage } from "@/components/ui";
import { skillsApi } from "@/lib/api";
import { getEntryIconId } from "@/data/skillTrees";
import SkillTreeRenderer from "./SkillTreeRenderer";

interface Props {
  skillId: string;
  buildSlug: string;
  skillName: string;
  readOnly?: boolean;
}

export default function SkillTreePanel({ skillId, buildSlug, skillName, readOnly }: Props) {
  const qc = useQueryClient();

  // Fetch tree structure
  const treeQuery = useQuery({
    queryKey: ["skill-tree", skillId],
    queryFn: () => skillsApi.getTree(skillId),
    staleTime: 24 * 60 * 60 * 1000, // 24 hours — tree data is static
    select: (res) => res.data,
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

  const isLoading = treeQuery.isLoading || allocQuery.isLoading;
  const error = treeQuery.error || allocQuery.error;

  if (isLoading) {
    return (
      <Panel title={`Skill Tree — ${skillName}`}>
        <div className="flex items-center justify-center py-12">
          <Spinner size={28} />
        </div>
      </Panel>
    );
  }

  if (error || !treeQuery.data) {
    return (
      <Panel title={`Skill Tree — ${skillName}`}>
        <ErrorMessage
          title="Failed to load skill tree"
          message={(error as Error)?.message || "Tree data unavailable"}
          onRetry={() => { treeQuery.refetch(); allocQuery.refetch(); }}
        />
      </Panel>
    );
  }

  const tree = treeQuery.data;
  const skillAlloc = allocQuery.data?.skills?.find(s => s.skill_id === skillId);

  // Patch root node icon from local data when the API returns null
  const entryIcon = getEntryIconId(skillId);
  const nodes = tree.nodes.map(n =>
    n.id === tree.root_node_id && n.icon == null && entryIcon
      ? { ...n, icon: entryIcon }
      : n,
  );

  // Convert string-keyed map to number-keyed
  const allocMap: Record<number, number> = {};
  if (skillAlloc) {
    for (const [k, v] of Object.entries(skillAlloc.allocated_nodes)) {
      allocMap[Number(k)] = v;
    }
  }

  const handleAllocate = (nodeId: number, points: number) => {
    if (readOnly) return;
    allocMutation.mutate({ nodeId, points });
  };

  return (
    <SkillTreeRenderer
      nodes={nodes}
      rootNodeId={tree.root_node_id}
      allocated={allocMap}
      onAllocate={handleAllocate}
      readOnly={readOnly}
      skillName={tree.skill_name}
    />
  );
}
