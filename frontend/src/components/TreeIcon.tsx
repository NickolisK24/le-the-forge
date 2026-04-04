/**
 * TreeIcon — renders a game asset icon for passive/skill tree nodes.
 *
 * Uses local PNG files from /assets/passive-icons/ when available.
 * Falls back to a colored abbreviation placeholder when no local file exists.
 *
 * Icon IDs are strings like "a-r-292" matching filenames in public/assets/passive-icons/.
 */

import { useMemo } from "react";

// Pre-built set of known local icon files.
// This avoids runtime 404s — if the icon isn't in this set, show a placeholder.
// The set is populated by importing the sprite map keys that follow the a-r-* pattern,
// since all local PNGs correspond to sprite map entries.
import iconSpriteMap from "@/data/iconSpriteMap.json";

const LOCAL_ICONS: Set<string> = new Set(
  Object.keys(iconSpriteMap as Record<string, unknown>).filter((k) =>
    k.startsWith("a-r-"),
  ),
);

interface TreeIconProps {
  /** Icon asset ID, e.g. "a-r-292" */
  iconId: string | null | undefined;
  /** Display size in pixels */
  size: number;
  /** Node name for generating placeholder text */
  nodeName?: string;
}

/**
 * SVG foreignObject icon for use inside tree renderers.
 */
export default function TreeIcon({ iconId, size, nodeName }: TreeIconProps) {
  if (!iconId) return null;

  const hasLocal = LOCAL_ICONS.has(iconId);

  // Placeholder letter(s) derived from node name
  const abbr = useMemo(() => {
    if (!nodeName) return "?";
    const words = nodeName.split(/\s+/).filter(Boolean);
    if (words.length >= 2) return (words[0][0] + words[1][0]).toUpperCase();
    return nodeName.slice(0, 2).toUpperCase();
  }, [nodeName]);

  if (hasLocal) {
    return (
      <foreignObject
        x={-size / 2}
        y={-size / 2}
        width={size}
        height={size}
        pointerEvents="none"
      >
        <img
          src={`/assets/passive-icons/${iconId}.png`}
          alt=""
          width={size}
          height={size}
          style={{
            borderRadius: "50%",
            objectFit: "cover",
            display: "block",
          }}
          loading="lazy"
        />
      </foreignObject>
    );
  }

  // Fallback: colored circle with text abbreviation
  return (
    <g pointerEvents="none">
      <circle r={size / 2 - 1} fill="#1a2040" stroke="#3a4070" strokeWidth={0.5} />
      <text
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={size * 0.35}
        fill="#8890b8"
        fontFamily="monospace"
        fontWeight="bold"
      >
        {abbr}
      </text>
    </g>
  );
}

/**
 * Standalone HTML icon (not in SVG context) for use in tooltips/lists.
 */
export function TreeIconHtml({
  iconId,
  size,
  nodeName,
}: TreeIconProps) {
  if (!iconId) return null;

  const hasLocal = LOCAL_ICONS.has(iconId);

  if (hasLocal) {
    return (
      <img
        src={`/assets/passive-icons/${iconId}.png`}
        alt={nodeName ?? ""}
        width={size}
        height={size}
        style={{ borderRadius: "50%", objectFit: "cover" }}
        loading="lazy"
      />
    );
  }

  const abbr = nodeName
    ? nodeName.split(/\s+/).filter(Boolean).map((w) => w[0]).join("").slice(0, 2).toUpperCase()
    : "?";

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        width: size,
        height: size,
        borderRadius: "50%",
        background: "#1a2040",
        border: "1px solid #3a4070",
        fontSize: size * 0.35,
        fontFamily: "monospace",
        fontWeight: "bold",
        color: "#8890b8",
      }}
    >
      {abbr}
    </span>
  );
}
