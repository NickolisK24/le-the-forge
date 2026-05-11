/**
 * GearSection — wraps the existing GearEditor, binding it to the workspace store.
 *
 * GearEditor already manages its own paper-doll / idol tab UI and exposes
 * gear / onChange props. This wrapper adds no logic beyond reading and
 * writing through the store.
 */

import GearEditor from "@/components/features/build/GearEditor";
import { useBuildWorkspaceStore } from "@/store";

export default function GearSection() {
  const gear = useBuildWorkspaceStore((s) => s.build.gear);
  const setGear = useBuildWorkspaceStore((s) => s.setGear);

  return (
    <section data-testid="workspace-section-gear">
      <GearEditor gear={gear} onChange={setGear} />
    </section>
  );
}
