/**
 * ClassCard — displays a single character class with its masteries and skills.
 *
 * Reusable card component. Receives pre-validated data — no API calls.
 * Optionally clickable via `to` prop (wraps in react-router Link).
 */

import { Link } from "react-router-dom";

interface ClassCardProps {
  name: string;
  color: string;
  masteries: string[];
  skills: string[];
  /** One-liner describing the class playstyle. */
  description?: string;
  /** Per-mastery colour map. Falls back to the class colour. */
  masteryColors?: Record<string, string>;
  /** If provided, the whole card becomes a link to this path. */
  to?: string;
}

export default function ClassCard({
  name,
  color,
  masteries,
  skills,
  description,
  masteryColors,
  to,
}: ClassCardProps) {
  const card = (
    <div
      className={`rounded-lg border bg-forge-surface overflow-hidden transition-all duration-200 ${
        to ? "cursor-pointer hover:-translate-y-0.5" : ""
      }`}
      style={{
        borderColor: `${color}40`,
        boxShadow: to ? `0 2px 12px rgba(0,0,0,0.25)` : undefined,
      }}
      onMouseEnter={(e) => {
        if (!to) return;
        (e.currentTarget as HTMLDivElement).style.borderColor = color;
        (e.currentTarget as HTMLDivElement).style.boxShadow = `0 0 18px ${color}30`;
      }}
      onMouseLeave={(e) => {
        if (!to) return;
        (e.currentTarget as HTMLDivElement).style.borderColor = `${color}40`;
        (e.currentTarget as HTMLDivElement).style.boxShadow = `0 2px 12px rgba(0,0,0,0.25)`;
      }}
    >
      {/* Header */}
      <div
        className="px-5 py-3 border-b flex items-center justify-between gap-3"
        style={{ borderColor: `${color}30`, background: `${color}0a` }}
      >
        <h2 className="font-display text-lg font-bold" style={{ color }}>
          {name}
        </h2>
        {to && (
          <span className="font-mono text-[10px] uppercase tracking-widest text-forge-dim">
            Plan build →
          </span>
        )}
      </div>

      <div className="px-5 py-4 space-y-4">
        {/* Description */}
        {description && (
          <p className="font-body text-sm text-forge-muted leading-relaxed italic">
            {description}
          </p>
        )}

        {/* Masteries */}
        <div>
          <h3 className="font-mono text-[10px] uppercase tracking-widest text-forge-dim mb-2">
            Masteries
          </h3>
          <div className="flex flex-wrap gap-2">
            {masteries.map((mastery) => {
              const mc = masteryColors?.[mastery] ?? color;
              return (
                <span
                  key={mastery}
                  className="rounded px-2.5 py-1 text-xs font-medium border"
                  style={{
                    background: `${mc}14`,
                    color: mc,
                    borderColor: `${mc}40`,
                  }}
                >
                  {mastery}
                </span>
              );
            })}
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

  if (to) {
    return (
      <Link to={to} className="block no-underline">
        {card}
      </Link>
    );
  }
  return card;
}
