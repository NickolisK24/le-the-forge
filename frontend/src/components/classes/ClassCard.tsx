/**
 * ClassCard — displays a single character class with its masteries and skills.
 *
 * Reusable card component. Receives pre-validated data — no API calls.
 */

interface ClassCardProps {
  name: string;
  color: string;
  masteries: string[];
  skills: string[];
}

export default function ClassCard({ name, color, masteries, skills }: ClassCardProps) {
  return (
    <div
      className="rounded-lg border bg-forge-surface overflow-hidden"
      style={{ borderColor: `${color}40` }}
    >
      {/* Header */}
      <div
        className="px-5 py-3 border-b"
        style={{ borderColor: `${color}30`, background: `${color}0a` }}
      >
        <h2 className="font-display text-lg font-bold" style={{ color }}>
          {name}
        </h2>
      </div>

      <div className="px-5 py-4 space-y-4">
        {/* Masteries */}
        <div>
          <h3 className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-2">
            Masteries
          </h3>
          <div className="flex flex-wrap gap-2">
            {masteries.map((mastery) => (
              <span
                key={mastery}
                className="rounded px-2.5 py-1 text-xs font-medium"
                style={{ background: `${color}18`, color }}
              >
                {mastery}
              </span>
            ))}
          </div>
        </div>

        {/* Skills */}
        <div>
          <h3 className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-2">
            Base Skills
          </h3>
          <div className="flex flex-wrap gap-1.5">
            {skills.map((skill) => (
              <span
                key={skill}
                className="rounded border border-forge-border bg-forge-surface2 px-2 py-0.5 text-xs text-forge-muted"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
