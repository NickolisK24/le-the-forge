import type { V2ApiEnvelope } from "@/lib/v2ApiEnvelope";
import { getV2EnvelopeBadges } from "@/lib/v2TrustStatus";

import { V2Badge } from "./V2TrustBadge";

interface V2StatusBadgeGroupProps {
  response?: V2ApiEnvelope | null;
  statuses?: ReturnType<typeof getV2EnvelopeBadges>;
  label?: string;
}

export function V2StatusBadgeGroup({ response, statuses, label = "Trusted data status" }: V2StatusBadgeGroupProps) {
  const badges = statuses ?? getV2EnvelopeBadges(response);

  return (
    <div className="flex flex-wrap gap-1.5" aria-label={label}>
      {badges.map((badge) => (
        <V2Badge key={badge.key} badge={badge} />
      ))}
    </div>
  );
}
