/**
 * MetaSection — name, description, class, mastery, level, flags.
 *
 * Thin wrapper around primitive form inputs. Reads the meta slice of the
 * working build from the store and writes through setMeta(). No local
 * build state.
 */

import type { CharacterClass } from "@/types";
import { useBuildWorkspaceStore } from "@/store";

const CLASSES: CharacterClass[] = [
  "Acolyte",
  "Mage",
  "Primalist",
  "Sentinel",
  "Rogue",
];

export default function MetaSection() {
  const build = useBuildWorkspaceStore((s) => s.build);
  const setMeta = useBuildWorkspaceStore((s) => s.setMeta);

  return (
    <section
      data-testid="workspace-section-meta"
      className="space-y-4 rounded-lg border border-white/10 bg-black/30 p-4"
    >
      <h2 className="text-base font-semibold text-white">Build details</h2>

      <label className="block text-sm">
        <span className="mb-1 block text-white/60">Name</span>
        <input
          type="text"
          value={build.name}
          onChange={(e) => setMeta({ name: e.target.value })}
          className="w-full rounded border border-white/15 bg-black/40 px-2 py-1 text-white"
          data-testid="meta-name"
        />
      </label>

      <label className="block text-sm">
        <span className="mb-1 block text-white/60">Description</span>
        <textarea
          value={build.description}
          onChange={(e) => setMeta({ description: e.target.value })}
          rows={3}
          className="w-full rounded border border-white/15 bg-black/40 px-2 py-1 text-white"
          data-testid="meta-description"
        />
      </label>

      <div className="grid grid-cols-3 gap-3">
        <label className="block text-sm">
          <span className="mb-1 block text-white/60">Class</span>
          <select
            value={build.character_class}
            onChange={(e) =>
              setMeta({ character_class: e.target.value as CharacterClass })
            }
            className="w-full rounded border border-white/15 bg-black/40 px-2 py-1 text-white"
            data-testid="meta-class"
          >
            {CLASSES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>

        <label className="block text-sm">
          <span className="mb-1 block text-white/60">Mastery</span>
          <input
            type="text"
            value={build.mastery}
            onChange={(e) => setMeta({ mastery: e.target.value })}
            className="w-full rounded border border-white/15 bg-black/40 px-2 py-1 text-white"
            data-testid="meta-mastery"
          />
        </label>

        <label className="block text-sm">
          <span className="mb-1 block text-white/60">Level</span>
          <input
            type="number"
            value={build.level}
            min={1}
            max={100}
            onChange={(e) =>
              setMeta({ level: Number(e.target.value) || 0 })
            }
            className="w-full rounded border border-white/15 bg-black/40 px-2 py-1 text-white"
            data-testid="meta-level"
          />
        </label>
      </div>

      <fieldset className="grid grid-cols-2 gap-2 text-sm text-white/80">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={build.is_ssf}
            onChange={(e) => setMeta({ is_ssf: e.target.checked })}
          />
          SSF
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={build.is_hc}
            onChange={(e) => setMeta({ is_hc: e.target.checked })}
          />
          Hardcore
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={build.is_ladder_viable}
            onChange={(e) => setMeta({ is_ladder_viable: e.target.checked })}
          />
          Ladder viable
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={build.is_budget}
            onChange={(e) => setMeta({ is_budget: e.target.checked })}
          />
          Budget
        </label>
      </fieldset>
    </section>
  );
}
