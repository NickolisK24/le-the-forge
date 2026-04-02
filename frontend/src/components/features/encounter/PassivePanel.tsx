/**
 * E10 — Passive Panel
 *
 * Simple list of allocated passive node IDs (comma-separated input).
 * In a full implementation these would be picked from the passive tree UI.
 */

interface Props {
  passiveIds: number[];
  onChange: (ids: number[]) => void;
  disabled?: boolean;
}

export default function PassivePanel({ passiveIds, onChange, disabled }: Props) {
  const raw = passiveIds.join(", ");

  function handleChange(value: string) {
    const ids = value
      .split(/[,\s]+/)
      .map((s) => parseInt(s.trim(), 10))
      .filter((n) => !isNaN(n) && n > 0);
    onChange(ids);
  }

  return (
    <section>
      <h3 className="mb-3 text-sm font-semibold text-forge-accent uppercase tracking-wider">
        Passive Nodes
      </h3>
      <p className="mb-2 text-xs text-forge-muted">
        Enter allocated passive node IDs (comma-separated).
      </p>
      <textarea
        value={raw}
        disabled={disabled}
        onChange={(e) => handleChange(e.target.value)}
        rows={3}
        placeholder="e.g. 101, 205, 340"
        className="
          w-full rounded border border-forge-border bg-forge-input
          px-3 py-2 text-sm text-forge-text font-mono
          focus:border-forge-accent focus:outline-none
          disabled:opacity-50 resize-none
        "
      />
      {passiveIds.length > 0 && (
        <p className="mt-1 text-xs text-forge-muted">
          {passiveIds.length} node{passiveIds.length !== 1 ? "s" : ""} allocated
        </p>
      )}
    </section>
  );
}
