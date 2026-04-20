# Handoff — 0G-2..0G-6: Skill base damage from Last Epoch Tools

**CSV rows:** `0G-2` Sentinel, `0G-3` Mage, `0G-4` Acolyte, `0G-5` Primalist, `0G-6` Rogue.
**Paste target:** `data/classes/skills_metadata.json` (fields were scaffolded by 0G-1).
**Field contract:** the `_schema` block at the top of `skills_metadata.json`.

## Goal

Replace the nulls on these four fields of every skill entry with LET-authoritative
values:

```jsonc
{
  "class":               "Sentinel" | "Mage" | "Acolyte" | "Primalist" | "Rogue",
  "base_damage_min":     number | null,   // level-1 tooltip, before any modifiers
  "base_damage_max":     number | null,   // level-1 tooltip
  "damage_scaling_stat": "strength" | "intelligence" | "dexterity" | "vitality" | "attunement" | "none",
  "attack_type":         "melee" | "ranged" | "throwing" | "spell" | "channeled" | "dot" | "minion" | "aura" | "utility"
}
```

`null` is a valid value for `base_damage_min/max` only when the skill deals no
direct damage (auras, buffs, movement utility). In that case set `attack_type:
"aura"` or `"utility"` and `damage_scaling_stat: "none"`.

## Why not infer from existing data

`data/classes/skills_with_trees.json` already has `attributeScaling[].attribute`
and `tagsDecoded[]`. Do **not** use them as the source of truth — they include
scalars that don't drive damage (a skill with `attributeScaling: Dexterity`
may still be a pure utility skill) and tag sets like `["Spell","Minion"]` that
don't reduce unambiguously to one of our nine `attack_type` enum values. They
are useful as a cross-check after you've captured the LET value, never as a
substitute.

## Scope

One class per output file, one file per CSV row. Do all 161 skills in
`skills_metadata.json` (some "shared" skills like `Decoy` or `Shield Rush` may
appear on multiple classes — duplicate the entry per class file; the merge
step later will pick the class-specific copy).

| CSV row | Class      | Output file                                         |
|---------|------------|-----------------------------------------------------|
| 0G-2    | Sentinel   | `data/classes/skill_base_damage/sentinel.json`      |
| 0G-3    | Mage       | `data/classes/skill_base_damage/mage.json`          |
| 0G-4    | Acolyte    | `data/classes/skill_base_damage/acolyte.json`       |
| 0G-5    | Primalist  | `data/classes/skill_base_damage/primalist.json`     |
| 0G-6    | Rogue      | `data/classes/skill_base_damage/rogue.json`         |

Each file is keyed by skill name (exactly matching the top-level keys in
`skills_metadata.json`) — case-sensitive, with the same capitalization.

## Output shape

```jsonc
// data/classes/skill_base_damage/sentinel.json
{
  "_meta": {
    "class": "Sentinel",
    "source": "lastepochtools.com",
    "captured_at": "2026-04-19",
    "patch_version": "<whatever the LET header shows>"
  },
  "Warpath": {
    "base_damage_min": 85,
    "base_damage_max": 85,
    "damage_scaling_stat": "strength",
    "attack_type": "melee",
    "source_url": "https://www.lastepochtools.com/db/skill/<id>"
  },
  "Shield Rush": {
    "base_damage_min": null,
    "base_damage_max": null,
    "damage_scaling_stat": "none",
    "attack_type": "utility",
    "source_url": "..."
  }
  // ... every Sentinel skill including ones that appear on other classes too
}
```

`base_damage_min` and `base_damage_max` take the tooltip's listed range. If the
tooltip shows a single value (e.g. "Deals 85 damage") set min == max.

Include `source_url` for every entry — the next reviewer needs to be able to
reconstruct your capture trivially.

## Capture procedure

1. Open the LET skill browser. I don't know the current URL — start from
   `https://www.lastepochtools.com/` and navigate to the skills list. Filter
   by class.
2. For each skill, open its page and capture the four fields from the
   rendered tooltip + metadata block. If LET exposes a `window.skillData` or
   similar global on that page, dump it verbatim first (same pattern as the
   build-info bookmarklet at `frontend/public/bookmarklets/let-import.js`) —
   a raw payload beats a hand-typed one every time. Attach the raw payload as
   a comment or sibling file; still distill the four fields into the shape
   above.
3. Work class-by-class to keep the output file + CSV row in sync. Don't skip
   around.
4. If a skill is genuinely absent from LET, set all four fields to `null` and
   add `"note": "not on LET — needs in-game tooltip"`.

## Enum disambiguation

`damage_scaling_stat`:

- Use the single attribute LET lists as the skill's damage-scaling stat. If the
  attribute listed is labelled "tag scaling" or "per-point global" rather than
  damage, record `"none"`.
- Pet/minion skills that scale off minion damage (not a player attribute): use
  `"none"` (minion scaling is modeled elsewhere).

`attack_type`:

- `melee` — hits in melee range, on-hit effects apply as melee
- `ranged` — bow/non-throwing projectile
- `throwing` — thrown weapon projectiles
- `spell` — cast, non-channelled, non-DoT-only
- `channeled` — held-to-cast (LET flag `channelled: true`)
- `dot` — primary damage is a damage-over-time with no initial hit
- `minion` — summons a persistent minion as its primary effect
- `aura` — persistent self-buff / party-buff with no direct hit
- `utility` — buffs, movement, traversal, transformations with no damage

Pick the single best fit. If a skill both hits and applies DoT, classify by the
direct hit (Abyssal Echoes → `spell`, Aura of Decay → `aura`).

## What I'll do with the files

Once all five files land, I will:

1. Cross-check each entry's key against `skills_metadata.json` (flag any typos).
2. Merge the values into `skills_metadata.json` in a single commit per class
   (one commit per CSV row so status column updates map 1:1).
3. Fix `sync_skills_metadata` in `scripts/sync_game_data.py:272` to preserve
   these four fields on re-run (currently it would wipe them — tracked as a
   follow-up before the next sync).
4. Wire `base_damage_min/max` into the stat pipeline for 0G-7 (replaces the
   estimated `base_damage` currently in `backend/app/game_data/skills.json`,
   calibrated in `docs/skill_damage_audit.md` — that file is the previous
   best-effort calibration and is explicitly what we're replacing).

## Ground rules

- Never paraphrase a tooltip number. If the tooltip says 85, record 85, not 80.
- If a tooltip value is a range (`100–120`), record both endpoints.
- If the skill has no base damage (buff/aura/utility), nulls are correct —
  don't fill in zero.
- Don't commit the output files to `main` or `dev`. Open a branch per class
  (`data/0G-2-sentinel-base-damage`, etc.) so each CSV row has a reviewable
  diff.
- Ping me when the first file (Sentinel is the smallest surface) is ready so we
  can validate shape + merge pipeline before you do the other four.
