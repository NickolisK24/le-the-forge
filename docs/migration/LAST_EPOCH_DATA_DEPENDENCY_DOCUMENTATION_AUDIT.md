# Last Epoch Data Dependency — Documentation Alignment Audit

> Read-only documentation audit. No runtime, planner, simulator, backend,
> frontend, extraction, ingestion, or generated-artifact logic was changed.
> Edits, where made, are minimal, additive, and explicitly tied to findings
> below.

- **Audit date:** 2026-05-29
- **Branch:** `docs/last-epoch-data-dependency-alignment-audit` (cut from latest `dev`, `baef7d7`)
- **Scope:** Whether `le-the-forge` documentation accurately reflects its
  downstream dependency on the upstream `last-epoch-data` trusted extraction /
  data-generation foundation.

---

## 1. Executive Summary

**Classification: PARTIALLY ALIGNED.**

`le-the-forge` documentation is split across two narratives that have not been
reconciled:

- **Track A — Governance / migration layer (well aligned).** The `docs/migration/`
  series (V2.5 → V4.5), `docs/FORGE_SYSTEM_PILLARS.md`,
  `docs/FORGE_DATA_CONSUMER_AUDIT.md`, `docs/FORGE_MIGRATION_TRACKER.md`,
  `docs/DATA_BUNDLE_COMPATIBILITY.md`, and especially
  `docs/migration/TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md` correctly and
  repeatedly frame `last-epoch-data` as the canonical extraction / compiler /
  source-of-truth repo. They preserve trust-first boundaries
  (`production_consumption_enabled=false`, `planner_recommendations_enabled=false`,
  `ranking_enabled=false`, `scoring_enabled=false`), classify all 27 gameplay
  domains as **partial / fail-visible**, and explicitly refuse to overclaim.

- **Track B — Public / entry-point layer (misaligned and stale).** The
  top-of-repo documents a new contributor, user, or AI agent reads **first** —
  `README.md`, `ROADMAP.md`, `docs/README.md`, and the data sections of
  `ARCHITECTURE.md` — carry a self-contained "v0.8 finished product" story.
  They present simulation, optimization, upgrade recommendations, and "concrete
  answers" as live and complete, describe `le-the-forge` as if it **owns its own
  extraction pipeline**, and **do not mention `last-epoch-data` as the upstream
  trusted dependency at all**.

**Biggest documentation risk:** the public/entry-point layer (`README.md`,
`ROADMAP.md`, `docs/README.md`) projects more completeness and more data
ownership than the program's own most recent trust audits certify. A reader who
stops at the entry-point docs would conclude that The Forge has full, trusted,
production-grade mechanical coverage and owns its data extraction — directly
contradicting `TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md`
(`trusted_gameplay_coverage_partial_fail_visible`, eligible planner-calculable
count = 0) and the preserved `production_consumption_enabled=false` posture. The
upstream `last-epoch-data` dependency, which is the entire premise of the current
program phase, is invisible at the entry points.

---

## 2. Current Intended Program Posture

This audit treats the following as the intended posture (consistent with the
governance-layer docs):

- `le-the-forge` is **downstream** of `last-epoch-data`. `last-epoch-data` is the
  trusted extraction / data-generation foundation; `FORGE_DATA_CONTRACT.md` and
  `DATA_BUNDLE_SPEC.md` live there (per `docs/FORGE_SYSTEM_PILLARS.md:13`).
- Dependency chain:
  `last-epoch-data` → trusted generated artifacts (schema-governed,
  provenance-bearing, certified) → `le-the-forge` ingestion / visibility /
  planner / runtime layers.
- **Trusted data, schema contracts, provenance, and generated reports govern
  what `le-the-forge` can safely expose or execute.** Generated bundles are
  currently read-only and **not production-consumed planner authority**
  (`TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md:75-76`).
- **Unsupported / untrusted / unknown / quarantined data must remain visible as
  limited / unknown / diagnostic** — never silently promoted to trusted. Partial
  support is a first-class classification, not collapsed into success or failure.
- No false confidence: deterministic trust first, provenance required, schema
  governance required, scoped support only where proven.

---

## 3. Documentation Files Reviewed

The full `docs/` tree, `docs/migration/`, and `docs/generated/` were enumerated;
the files below were read directly or examined for dependency framing. (Branch
`docs/last-epoch-data-dependency-alignment-audit`, base `dev`.)

**Root README / top-level**
- `README.md`
- `ROADMAP.md`
- `ARCHITECTURE.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `AGENTS.md`
- `ACCURACY_AUDIT.md`
- `VERSION`, `package.json` (version signals)

**docs/ (index + reference)**
- `docs/README.md`
- `docs/FORGE_SYSTEM_PILLARS.md`
- `docs/FORGE_DATA_CONSUMER_AUDIT.md`
- `docs/FORGE_MIGRATION_TRACKER.md`
- `docs/DATA_BUNDLE_COMPATIBILITY.md`
- `docs/BUNDLE_ITEM_MIGRATION_MILESTONE_SUMMARY.md`
- `docs/KNOWN_LIMITATIONS.md`
- `docs/engine_architecture.md`, `docs/simulation_design.md` (reference framing)

**docs/migration/ (governance / trust layer)**
- `docs/migration/TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md` (current-state anchor)
- `docs/migration/MACBOOK_TRANSITION_SAFETY_AUDIT.md` (preserved prohibitions)
- `docs/migration/V2_CANONICAL_DATA_CONTRACT.md`, `V2_SOURCE_INVENTORY.md`,
  affix/skill/item/idol/unique migration docs, and the V3.x / V4.x
  runtime / orchestration / governance / trust-visibility series (enumerated;
  sampled for `last-epoch-data` and overclaim language).

**docs/generated/**
- Enumerated; `bundle_item_adapter_map_report.md` and the trusted-coverage JSON
  reports referenced by the coverage audit were treated as generated evidence,
  **not edited**.

---

## 4. Alignment Findings

Severity: **blocker** / **high** / **medium** / **low**.
Status: **corrected in branch** / **recommendation-only**.

### F1 — README does not disclose the `last-epoch-data` upstream dependency
- **File:** `README.md` (whole document; only mention is the community
  acknowledgement at `README.md:366`).
- **Section:** "Status", "What Is The Forge", "Game Data".
- **Issue:** The single most-read document never states that `le-the-forge`
  consumes trusted/generated data from the upstream `last-epoch-data` repo. Data
  is described as "extracted from Last Epoch and normalized into JSON"
  (`README.md:217`) via `scripts/sync_game_data.py`, framing `le-the-forge` as
  the owner of extraction.
- **Why it matters:** The entire current program phase is about the upstream
  dependency. Its invisibility at the entry point is the audit's central risk
  (false sense of self-contained data ownership; future contributors will not
  know where trusted data comes from).
- **Recommended correction:** Add a short, factual "Upstream data dependency"
  pointer in the Status block linking to `last-epoch-data` and to
  `docs/migration/TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md`.
- **Severity:** high.
- **Status:** **corrected in branch** (minimal additive Status bullet; feature
  claims left untouched).

### F2 — README presents simulation / optimization / recommendations as complete and authoritative
- **File:** `README.md`
- **Section:** "What Is The Forge" (`:26`, `:28`, `:30`), "Features" (`:36-60`).
- **Issue:** "The Forge gives you a concrete answer" (`:26`); "The goal is
  mechanical accuracy — every number traces back to a formula" (`:28`); "The core
  simulation pipeline is stable" (`:30`); "Optimization engine … upgrade
  efficiency scoring … Pareto-optimal candidate detection" presented as a live
  feature. The current trust posture is
  `trusted_gameplay_coverage_partial_fail_visible`, with eligible
  planner-calculable count = 0 and `planner_recommendations_enabled=false`,
  `ranking_enabled=false`, `scoring_enabled=false`
  (`MACBOOK_TRANSITION_SAFETY_AUDIT.md:141-148`).
- **Why it matters:** False-confidence risk and public-facing overpromise for
  `epochforge.gg`. The recommendation/scoring/ranking language is exactly what
  the governance layer keeps disabled.
- **Recommended correction:** Reconcile the feature narrative with the current
  trust posture — qualify recommendation/optimization/scoring language as
  legacy/advisory pending trusted-data certification, or explicitly scope the
  README's claims to the deployed legacy build and link to the coverage audit.
  Requires confirming the deployed product's actual runtime state; **not** safe
  to assert in a docs-only branch.
- **Severity:** high.
- **Status:** recommendation-only.

### F3 — ROADMAP omits the dependency chain and the trust-rebuild program
- **File:** `ROADMAP.md`
- **Section:** "Completed" (`:5-47`), "Future Phases" (`:61-68`).
- **Issue:** Roadmap presents Phases 1–9 (v0.1 → v0.8) as the complete arc and
  lists future phases including "AI-powered build Q&A … recommendations". There
  is **no** mention of `last-epoch-data`, trusted generated artifacts, the
  V2.5 → V4.5 trust / provenance / schema-governance program, or the dependency
  chain that now gates deeper functionality.
- **Why it matters:** The roadmap is the canonical "where are we going" doc; it
  is two-plus major program tracks out of date and does not reflect that deeper
  planner/simulator functionality is **blocked on upstream trusted-data
  certification**.
- **Recommended correction:** Add a roadmap section describing the dependency
  chain (`last-epoch-data` → trusted artifacts → ingestion/visibility →
  scoped planner/runtime) and that planner/recommendation features are gated on
  upstream certification, cross-linking the migration series.
- **Severity:** high.
- **Status:** recommendation-only.

### F4 — docs/ index hides the entire trust / dependency program
- **File:** `docs/README.md`
- **Section:** "Documentation Index", "Core Philosophy", "Key Architectural Rule".
- **Issue:** The index lists only reference/operations/transparency docs. It does
  not surface `docs/migration/`, `FORGE_SYSTEM_PILLARS.md`,
  `FORGE_DATA_CONSUMER_AUDIT.md`, or `TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md`.
  It states "The backend is the **single source of truth**" (`:47`) and
  "Data-driven recommendations" (`:41`) — which, for *game data*, conflicts with
  `last-epoch-data` being the canonical source of truth and with recommendations
  being disabled.
- **Why it matters:** A contributor browsing the docs index would never discover
  the dependency on `last-epoch-data` or the trust program — the audit's
  discoverability gap in concentrated form.
- **Recommended correction:** Add a "Data & Trust" group to the index linking the
  dependency/governance docs; clarify that "single source of truth" refers to
  *calculation*, while *game data* originates upstream in `last-epoch-data`.
- **Severity:** medium.
- **Status:** **corrected in branch** (additive index group + one clarifying
  parenthetical; existing entries preserved).

### F5 — ARCHITECTURE frames le-the-forge as the extractor/transformer
- **File:** `ARCHITECTURE.md`
- **Section:** "Data Sync Pipeline" (`:253`), "Data Sources" mirror in
  `README.md:217`.
- **Issue:** "`scripts/sync_game_data.py` transforms raw exports from
  `last-epoch-data/` into normalized JSON files in `/data/`." This describes the
  legacy local-transform path and positions `le-the-forge` as the normalizer of
  raw exports. It predates the trusted-bundle model in which `last-epoch-data`
  *generates* schema-governed, provenance-bearing artifacts that `le-the-forge`
  *ingests*. It does not mention bundle ingestion, trust state, or that the
  generated assets are not yet production-consumed.
- **Why it matters:** Stale data-architecture framing; understates the upstream
  role and overstates `le-the-forge`'s data authority.
- **Recommended correction:** Note that `last-epoch-data` is the upstream
  extraction/generation source of truth and that the bundle-ingestion / trusted
  generated-artifact model (per `FORGE_DATA_CONSUMER_AUDIT.md` and the migration
  series) supersedes the raw-export transform path; cross-link.
- **Severity:** medium.
- **Status:** recommendation-only (architecture-of-record change; outside minimal
  docs-only edit scope).

### F6 — Version signals are inconsistent across the repo
- **Files:** `VERSION` (`0.8.0`), `package.json` (`0.3.0`), git tag `v2.5.0`,
  `docs/migration/` series at V4.5.
- **Issue:** Four different version stories. README/ROADMAP assert v0.8; the
  trust program is at v2.5 → v4.5.
- **Why it matters:** Compounds the two-track confusion; a reader cannot tell
  which version line is authoritative.
- **Recommended correction:** Decide and document the authoritative versioning
  scheme (product line vs. data-trust program line) and reconcile the files.
  Requires owner intent; not a docs-only edit.
- **Severity:** medium.
- **Status:** recommendation-only.

### F7 — README "Data Confidence" table is good but does not name the upstream source
- **File:** `README.md:236-247`
- **Issue:** The confidence table (Verified / High / Estimated / Mixed) is an
  honest, well-scoped artifact and should be **kept**. However it attributes
  confidence to in-repo extraction ("Extracted from game files") without naming
  `last-epoch-data` as the certifying upstream, so confidence appears to be
  self-asserted rather than provenance-derived.
- **Why it matters:** Provenance attribution is part of the trust model; the
  table is the right place to anchor it.
- **Recommended correction:** Note that data confidence/provenance is governed
  upstream by `last-epoch-data` certification once the trusted-bundle ingestion
  path is production-consumed. Do **not** remove or weaken the existing table.
- **Severity:** low.
- **Status:** recommendation-only.

### F8 — Governance / migration layer is well aligned (no action)
- **Files:** `docs/migration/TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md`,
  `MACBOOK_TRANSITION_SAFETY_AUDIT.md`, `FORGE_SYSTEM_PILLARS.md`,
  `FORGE_DATA_CONSUMER_AUDIT.md`, `FORGE_MIGRATION_TRACKER.md`,
  `DATA_BUNDLE_COMPATIBILITY.md`, `BUNDLE_ITEM_MIGRATION_MILESTONE_SUMMARY.md`.
- **Issue:** None. These correctly frame `last-epoch-data` as canonical source of
  truth, keep partial/unsupported/quarantined states visible, preserve the
  no-production-consumption boundaries, and explicitly refuse to overclaim
  completeness.
- **Severity:** n/a.
- **Status:** no change (validated as aligned; warnings/limitation language
  deliberately preserved).

---

## 5. Dependency Clarity Review

| Question | Governance/migration layer | Entry-point layer (README/ROADMAP/docs index) |
|---|---|---|
| What data must come from `last-epoch-data`? | Clear — canonical extraction/compiler/source-of-truth; contracts live upstream (`FORGE_SYSTEM_PILLARS.md:13`, `FORGE_DATA_CONSUMER_AUDIT.md:5`). | **Absent** — not mentioned. |
| How should generated artifacts be trusted? | Clear — read-only generated bundles exist but are **not** production-consumed planner authority (`TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md:75-76`). | **Absent / contradicted** — features framed as live. |
| Schema / provenance / certification expectations? | Present — schema drift tracked, deterministic report hashes, certification states (`TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md:140-154`). | **Absent.** |
| Which domains are partial / unsafe? | Explicit — all 27 partial; missing coverage for blessings, crafting materials, monolith/echo, bosses, ailments, damage types, planner contracts (`:80-126`). | **Absent** — implied complete. |
| Behavior when data is unsupported / unknown / quarantined? | Explicit — reportable, fail-visible, never hidden, never silently trusted (`:93-108`, `:196-212`). | **Absent.** |

**Conclusion:** Dependency clarity is strong in the governance layer and missing
in the entry-point layer.

---

## 6. False-Confidence Risk Review

Language that could lead a user, contributor, or AI agent to believe support is
more complete than proven:

- `README.md:26` — "The Forge gives you a concrete answer."
- `README.md:28` — "The goal is mechanical accuracy — every number traces back to
  a formula you can inspect."
- `README.md:30` — "The core simulation pipeline is stable."
- `README.md` Features (`:36-60`) — Optimization engine, upgrade efficiency
  scoring, Pareto-optimal detection, meta analytics presented as live.
- `ROADMAP.md:16-17` — "Optimization Engine (v0.4.0) … multi-objective
  optimization with Pareto front" listed under **Completed**.
- `ROADMAP.md:67` — future "AI-powered build … recommendations" with no trust gate.
- `docs/README.md:41` — "Data-driven recommendations."
- `ARCHITECTURE.md:253` / `README.md:217` — extraction/normalization framed as
  owned by `le-the-forge`.

Each conflicts with the preserved boundaries
`planner_recommendations_enabled=false`, `ranking_enabled=false`,
`scoring_enabled=false`, `production_consumption_enabled=false` and with eligible
planner-calculable count = 0.

**Mitigating factors (kept, not removed):** `README.md:30` already discloses that
some inputs are "benchmarked approximations rather than verified game extracts";
the README "Data Confidence" table and `docs/KNOWN_LIMITATIONS.md` are honest and
prominent. The risk is *partial* overclaiming, not total — hence "partially
aligned" rather than "misaligned".

---

## 7. Public-Facing Safety Review (`epochforge.gg`)

- The README header markets "A deterministic Last Epoch build analysis and
  **simulation platform**" and "concrete answer", which can read as a correctness
  guarantee. Paired with the disabled planner/scoring posture, this is the main
  public overpromise.
- **Safe / good:** the prominent beta framing (`README.md:323` "live in beta and
  is honest about what is not yet complete"), the linked transparency document,
  the per-skill/enemy confidence disclosures, and community-validation requests.
- **Recommended guardrail:** ensure the public surface never implies trusted,
  certified, or production-grade mechanical coverage while the coverage audit
  remains `..._partial_fail_visible`. No public claim should outrun the upstream
  certification state of `last-epoch-data`.

---

## 8. Recommended Documentation Corrections

**Immediate (low-risk, additive — partially applied in this branch)**
1. README: add an upstream `last-epoch-data` dependency pointer in Status.
   *(applied — F1)*
2. docs/README: add a "Data & Trust" index group surfacing the dependency /
   governance docs and clarify the "single source of truth" scope. *(applied — F4)*

**Next-pass (needs owner intent / runtime confirmation)**
3. README "What Is The Forge" + Features: qualify simulation/optimization/
   recommendation claims against the current trust posture, or scope them to the
   deployed legacy build with a link to the coverage audit. *(F2)*
4. ROADMAP: add the dependency chain and trust-rebuild track; mark deeper
   planner/recommendation phases as gated on upstream certification. *(F3)*
5. ARCHITECTURE "Data Sync Pipeline": describe the trusted-bundle ingestion model
   and `last-epoch-data` as the generation source of truth. *(F5)*
6. Reconcile version signals (`VERSION`, `package.json`, tags, migration series). *(F6)*

**Future roadmap documentation improvements**
7. Add a dedicated `docs/DATA_DEPENDENCY.md` (or section in `FORGE_SYSTEM_PILLARS.md`)
   that diagrams `last-epoch-data` → trusted generated artifacts → ingestion →
   visibility → scoped planner/runtime, and lists, per domain, what must be
   certified upstream before `le-the-forge` may enable deeper functionality.
8. Add a provenance/confidence note to the README "Data Confidence" table tying
   confidence to upstream certification. *(F7)*

---

## 9. Final Classification

```text
documentation_partially_aligned_with_last_epoch_data_dependency
```

Rationale: the governance/migration layer is well aligned and disciplined
(trust-first, fail-visible, no overclaim), but the public/entry-point layer
(`README.md`, `ROADMAP.md`, `docs/README.md`, `ARCHITECTURE.md` data sections)
omits the `last-epoch-data` dependency and overstates completeness and data
ownership.

---

## 10. Next Recommended Phase

Reconcile the two documentation tracks at the entry points (next-pass items 3–6),
starting with a `docs/DATA_DEPENDENCY.md` that future contributors and AI agents
are pointed to from README and the docs index. This should be an
**integration-governance documentation phase** that makes the dependency chain
the canonical framing, and that gates README/ROADMAP capability language on the
upstream certification state reported by
`docs/migration/TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md`. Capability-claim
language should not be promoted beyond `..._partial_fail_visible` until
`last-epoch-data` trusted-bundle ingestion is production-consumed and certified.
