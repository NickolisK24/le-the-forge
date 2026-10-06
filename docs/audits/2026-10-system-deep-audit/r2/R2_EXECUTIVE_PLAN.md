# AUDIT-R2 Executive Plan: Canonical Consumption

**Status: R2 READY — WAITING FOR CERTIFIED R1 SNAPSHOT.** Preparation only. Nothing in le-the-forge runtime is implemented, merged or deployed.

| Item | Value |
| --- | --- |
| R1 state | R1 PRE-EXTRACTION READY — OPERATOR RUN REQUIRED (not certified) |
| last-epoch-data `fix/audit-r1-extraction-truth` | `0111f1e` (was `308cf2f`; R1 contract fixes `7dc1ad6`, `0111f1e`, found during R2 prep) |
| le-the-forge R1 branch | `fix/audit-r1-extraction-consumption` @ `9e1356a` |
| R2 preparation branch | `docs/audit-r2-preparation` (based on the R1 branch; docs only) |
| Production | `main` @ `80bd559`, untouched |

## Purpose

The Forge must consume canonical, versioned, trust-preserving R1 data without:
- corrupting values;
- dropping fields;
- remapping identities by name or position;
- losing provenance or trust;
- keeping duplicate authorities;
- letting the frontend drift from the backend;
- silently accepting unresolved relationships.

R2 defines exactly how, and the packages are ready to start.

## What the investigation found (R2_CURRENT_CONSUMPTION_GRAPH.md)

| Area | Finding |
| --- | --- |
| Provenance, trust, patch | **None survive to runtime for any family.** No code reads trust. `data/version.json` says `unknown`. The sync cannot run as written: it reads a path inside the Forge repo that does not exist. |
| Parallel authorities | 5 affix paths, 4 mastery orderings, 6 slot vocabularies, 3 skill-tree sources, 2 passive sources that disagree, and backend vs frontend class stats that contradict each other |
| Identity | Name, slug, index and first-match resolution is the norm: 23 item-side and 31 character-side hazards with file:line, plus 39 mastery consumers |
| Fallbacks | 1,557 fallbacks in data paths. **744 are dangerous silent fallbacks**: 575 in runtime code, 512 owned by R2 packages, 69 by R6, and 163 disappear with retired code. |
| Legacy authorities | **79**: 60 to remove, 11 kept temporarily, 6 archived, 2 still required |
| Persistence | Builds have no data provenance. `patch_version` is client text defaulting to `1.2.1`. Render never seeds reference tables, and reads silently fall back to JSON. Five disagreeing patch values exist across surfaces. |
| New finding | Corrupted skill name↔id pairs (`fi9` "Frigid Tempest", `en6` "Create Shadow", `me27` "Shocking Impact", `rf1azz` "Reap"). Fireball, Meteor, Elemental Nova and Reaper Form have no metadata. Both importers inherit this. |

## R1 contract defects found and fixed during R2 preparation

These are authorized by the R2 instruction, since a concrete R2 investigation uncovered them. They are pushed to the R1 branch and the R1 suite passes (226 tests).

| Defect | Effect | Fix |
| --- | --- | --- |
| Run manifest counted the run's own uncommitted outputs as extractor changes | Every operator run recorded `extractor.dirty = true`, so **C7 could never pass** | Dirty covers paths outside run outputs only (`7dc1ad6`) |
| Run manifest did not inventory canonical exports | Canonical data could not be bound to the snapshot. The extract-stage reproduction compared against an inventory that never contained them, so **C8 could never pass**. | `canonical_exports` + `canonical_content_hash` (`7dc1ad6`) |
| Walker dropped `SkillTree.ability` | No canonical tree could be joined to its ability, which forces name joins (REL-4/6/10) | `abilityRef` carried; canonical `ability_ref` with status (`0111f1e`) |

## Architecture decisions

| # | Decision | Document |
| --- | --- | --- |
| D1 | One handoff: `CanonicalDataManifest` + byte-identical family files in `data/canonical/<data_version>/`, imported and verified from R1 artifacts. The Forge never interprets raw formats. | R2_CANONICAL_CONSUMPTION_CONTRACT.md |
| D2 | Typed views (classes and masteries, abilities, items, uniques, sets, ailments, blessings) are built **upstream** in last-epoch-data. That keeps one interpreter of game data. | same |
| D3 | Fail closed: 11 loader rejections, `503 DATASET_UNAVAILABLE`, no legacy fallback, trust narrowed and never widened | same |
| D4 | One dataset per process; `CROSS_BUILD` never allowed; same-snapshot rebuilds only through an explicit compatibility declaration | R2_MIXED_PATCH_POLICY.md |
| D5 | Source ids only. Composites where the game requires them: `(class_id, mastery_index)`, `(tree_id, node_id)`, `(base_type_id, sub_type_id)`, `(affix_id, property_index)`. Names are presentation. | R2_IDENTITY_POLICY.md |
| D6 | Graphs stay graphs: 0..n prerequisite edges with points; tree ↔ ability via `SkillTree.ability`; unresolved edges and stats reported, never coerced | R2_RELATIONSHIP_MODEL.md |
| D7 | Reference data from immutable bundles in memory (option B). DB reference tables and seeding retired. A `datasets` table anchors build provenance. | R2_DATABASE_PROVENANCE_PLAN.md |
| D8 | Server-stamped `data_version` on every build write. Existing builds become `LEGACY_UNKNOWN`, with no fabricated history and explicit degraded behaviour. | same |
| D9 | Frontend: generated artifacts from the same bundle plus API catalogues. Both carry `data_version`; a mismatch refuses to render; a CI parity test; no hand-written game facts | R2_FRONTEND_AUTHORITY_PLAN.md |
| D10 | Dangerous fallbacks replaced by explicit states. A CI ratchet gate goes from 575 runtime dangerous fallbacks to 0 R2-owned. | R2_FALLBACK_AUDIT.md |

## Packages (R2_IMPLEMENTATION_PACKAGES.json)

21 entries: R2-P00 is done; **20 are implementation packages**.

| When | Packages |
| --- | --- |
| **Can begin before the operator run** (code + tests, flags off, no production change) | P17 contract harness and fixtures; P01 bundle importer; P02 CanonicalDataStore; P03 typed ids; P09 reference API envelope; P15 migrations and Postgres CI; P16 fallback gate |
| **Build now against 1.4.6 canonical (ADVISORY), switch after the certified snapshot** | P05 affixes; P07 passives as a graph; P10 frontend authority; P12 game-fact constants (inventory and declarations); P13 build provenance (schema, `LEGACY_UNKNOWN` backfill); P14 seeding retirement; P19 version surfaces |
| **Must wait for the certified 1.5 snapshot** | P04 upstream typed views (needs TypeTree dumps); P06 classes/masteries (REL-1; needs the class view); P08 skills/abilities/trees (needs `ability_ref` and the Ability view); P11 items/uniques/sets/blessings (needs typed views); P20 production cutover; P18 legacy retirement (after cutover + one release) |

**Critical path:**
- **Before the run:** P17 → P01 → P02 → P03.
- **After the certified snapshot:** P04 → P06 → P07 → P08 → P13 → P10 → P20 → P18.

P04 (XL) is the longest single item and it cannot start until the operator run lands.

## Findings mapped

**28 findings mapped: all 18 AUDIT-R2 findings plus 10 R1 → R2 consumption handoffs.**

| Group | Findings |
| --- | --- |
| AUDIT-R2 (18) | REL-1, REL-2, REL-4, REL-6, REL-7, REL-9, REL-10, REL-16, REL-23, REL-24, DB-3, DB-4, DB-5, DOC-3, DRIFT-3, DRIFT-7, EXT-6, SYS-3 |
| R1 handoffs (10) | EXT-1, EXT-2, EXT-3, LOSS-1, LOSS-2, LOSS-3, LOSS-4, LOSS-5, LOSS-6, SYS-4 |

R2 packages also advance 11 findings owned by R1, R4 or R6 without closing them: EXT-12 (R1); IMP-4, IMP-6 (R4); FE-10, FE-8, FE-3, SYS-5, DEAD-3, CALC-6, CALC-14, DOC-11 (R6).

## Architectural blockers and decisions needed

| # | Blocker | Why it matters | Resolution |
| --- | --- | --- | --- |
| B1 | **No typed canonical views exist for classes, abilities, items, uniques, sets, ailments or blessings.** R1 produces lossless TypeTree envelopes only, after the operator run. | Six REQUIRED families have no consumable schema yet. Their fields cannot be designed from the layout alone. | R2-P04, upstream, after the run (XL, critical path) |
| B2 | **Trust policy at cutover.** Every R1 family is QUARANTINED today, and trees are DEFECTIVE until the strict decoder and TypeTree dumps prove them. If the certified snapshot still leaves a REQUIRED family below CERTIFIED, TRUSTED-only production would serve nothing for it. | Decides whether R2-P20 can ship | **Owner decision before P20:** either block the family (`UNSUPPORTED_DATA`), or allow ADVISORY calculations labelled end to end. The contract supports both; the default is block. |
| B3 | **Masteries have no id**, only a position in `CharacterClass.masteries` | REL-1 fix depends on source order being carried | The class view must carry the ordered list (R2-P04 acceptance) |
| B4 | **Tree node values and some stat namespaces are undecoded.** `AutomaticNodeStat` and the 5000–9999 property band are undecoded. | Specialization-tree modifiers cannot be TRUSTED calculation input; R2 delivers graph and references only | Needs the TypeTree node dump (operator run) + R6 semantics |
| B5 | **No canonical node coordinates.** RectTransforms are not dumped. | Frontend layout stays a third-party presentation overlay, parity-checked, never identity | Optional extractor addition (R2-P04 optional scope) |
| B6 | **Skill numeric values are not extracted** (base damage, scaling; CALC-1) | R2 fixes skill identity, but the hand-authored values remain (`skills.json`, `SKILL_STATS`) | R6 |
| B7 | **No interim canonical production is possible on 1.4.6.** It has no raw snapshot, so the loader rejects it (`PROVENANCE_MISSING`). | Production keeps the legacy path until the certified 1.5 snapshot | By design; interim narrow fixes (REL-1, REL-23, corrupted skill names) are possible from 1.4.6 evidence if the owner wants them, but they are not R2 |

## Deliverables (`docs/audits/2026-10-system-deep-audit/r2/`)

| Document | Content |
| --- | --- |
| R2_EXECUTIVE_PLAN.md | This document |
| R2_CURRENT_CONSUMPTION_GRAPH.md | Per-family hop tables (input/output identity, dropped, derived, value and relationship transforms, provenance, trust, patch) with file:line |
| R2_CANONICAL_CONSUMPTION_CONTRACT.md | Manifest and types, loader rejections, consumption modes, required families |
| R2_IDENTITY_POLICY.md | Canonical identities and composites, third-party id maps |
| R2_RELATIONSHIP_MODEL.md | Mastery derivation (REL-1) with the 15-mastery tests; skill and tree graph; item relationships |
| R2_DATABASE_PROVENANCE_PLAN.md | Reference-data decision, deterministic init, build provenance, `LEGACY_UNKNOWN` |
| R2_FRONTEND_AUTHORITY_PLAN.md | One bundle, two channels, parity, deletion list |
| R2_FALLBACK_AUDIT.md + R2_FALLBACK_CENSUS.jsonl | 1,557 classified fallbacks with owners |
| R2_MIXED_PATCH_POLICY.md | Load-time invariant, compatibility modes, upgrade procedure |
| R2_MIGRATION_DAG.md | Dependency order with code evidence; hazard → package |
| R2_CONTRACT_TEST_PLAN.md | T1–T14, fixtures, CI jobs |
| R2_LEGACY_RETIREMENT_PLAN.md | 79 legacy authorities with dispositions |
| R2_IMPLEMENTATION_PACKAGES.json | 21 package records (P00 done + 20) |
