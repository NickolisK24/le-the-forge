/**
 * BlessingsSection — wraps BlessingsPanel.
 *
 * Straight pass-through — BlessingsPanel already takes selectedBlessings
 * and onChange props that map one-to-one to the store.
 */

import { BlessingsPanel } from "@/components/blessings/BlessingsPanel";
import { useBuildWorkspaceStore } from "@/store";

export default function BlessingsSection() {
  const blessings = useBuildWorkspaceStore((s) => s.build.blessings);
  const setBlessings = useBuildWorkspaceStore((s) => s.setBlessings);

  return (
    <section data-testid="workspace-section-blessings">
      <BlessingsPanel selectedBlessings={blessings} onChange={setBlessings} />
    </section>
  );
}
