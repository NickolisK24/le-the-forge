# Trusted Data Promotion Readiness Audit

> **Readiness audit only — this document does NOT promote any data domain to
> trusted.** It defines the upstream and downstream evidence, gates, and current
> gaps that would be required *before* any Last Epoch data domain could be
> promoted from advisory / partial / diagnostic to trusted in `le-the-forge`.
>
> No runtime, planner, simulator, optimizer, ingestion, extraction, or generated
> JSON behavior was changed. No certification status was fabricated. No warning,
> partial-state, fail-visible, quarantine, or diagnostic-only language was
> weakened.

- **Date:** 2026-05-29
- **Branch:** `docs/trusted-data-promotion-readiness-audit` (cut from `dev`)
- **Anchors:** [`DATA_DEPENDENCY.md`](../DATA_DEPENDENCY.md),
  [`TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md`](TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md),
  [`VERSIONING_POLICY.md`](../VERSIONING_POLICY.md)

---

## 1. Executive Summary

**`le-the-forge` is NOT currently ready to promote any data domain to trusted.**

The most recent coverage evidence
(`docs/generated/gameplay_support_matrix_report.json`,
certification `trusted_gameplay_coverage_partial_fail_visible`, maturity
`generated_trusted_assets_exist_but_planner_completeness_not_certified`) records,
across all 27 audited systems:

- `stable_calculable_count = 0` for **every** system,
- `planner_dependency_gap` on **every** system,
- all 27 systems classified `partial` and `stale`, and `untrusted` at the
  program level even where trusted *generated assets* exist.

"Trusted generated assets exist" is **not** the same as "domain is promotable to
trusted." Generated bundles are read-only and are explicitly **not**
production-consumed planner authority. Therefore the count of domains classified
`promotion_ready` by this audit is **zero**. The remainder are blocked on specific
upstream and/or downstream evidence, catalogued below.

---

## 2. Current Governance Posture

- **Upstream `last-epoch-data` certification is necessary but not sufficient.**
  Even where upstream generated artifacts and provenance exist, a domain cannot be
  promoted until downstream behavior is proven.
- **Downstream evidence is also required.** `le-the-forge` must demonstrate a real
  ingestion path, schema validation, visibility/debug state, fail-visible handling
  of unsupported/unknown/quarantined records, and scoped + tested consumption
  before any promotion.
- **Version labels do not override trust state.** Per
  [`VERSIONING_POLICY.md`](../VERSIONING_POLICY.md), no product/package/tag/
  governance-phase number implies trust, coverage, or certification. If a version
  label and the trust state disagree, the trust state wins.
- **Promotion is per-capability, not per-domain.** A domain may be safe for
  *display* while remaining blocked for *calculation/planner/optimization*
  (see §5).

---

## 3. Domain Readiness Matrix

Apparent support state and classifications are taken from
`gameplay_support_matrix_report.json` and the named per-domain generated reports.
All domains share two universal blockers — `stable_calculable_count = 0` and
`planner_dependency_gap` — so none reach `promotion_ready`.

### 3.1 affixes
- **Apparent state:** trusted *generated assets* + provenance; partial; planner gap.
- **Evidence present:** `v2_affix_bundle.json`, `v2_affix_validation_report.json`,
  `v2_affix_display_provenance_report.json`, controlled affix resolver reports.
  Consumed by `affix_registry.py` / `affix_catalog_service.py` (display + craft).
- **Upstream required:** certified affix definitions/tiers/eligibility/value ranges
  with provenance + deterministic hash.
- **Downstream required:** schema validation on ingest; planner-calculable
  normalization (currently `stable_calculable_count=0`); fail-visible handling of
  unresolved tiers.
- **Fail-visible req:** malformed/unresolved affixes must remain visible, not
  silently defaulted.
- **Blockers/gaps:** value normalization is audit-only; no stable calculable path.
- **Classification:** `partially_ready_requires_evidence` (display closest; calc/planner blocked).

### 3.2 item bases
- **Apparent state:** trusted generated assets; partial; planner gap.
- **Evidence present:** `v2_item_base_bundle.json`, `v2_item_implicit_bundle.json`,
  `v2_item_validation_report.json`, `v2_item_base_display_metadata_report.json`.
  Note: `items.json` / `item_types.json` are **not** loaded by the central
  `GameDataPipeline` (per `FORGE_DATA_CONSUMER_AUDIT.md`).
- **Upstream required:** certified base items / item types / implicits / rarities.
- **Downstream required:** confirmed central ingestion path + schema validation
  (currently partly outside the pipeline / hybrid).
- **Fail-visible req:** unknown base items must surface (e.g. `gear_missing`), not
  be coerced.
- **Blockers/gaps:** hybrid/partial ingestion; planner gap.
- **Classification:** `partially_ready_requires_evidence`.

### 3.3 uniques
- **Apparent state:** trusted generated assets; partial; **unsupported** records; planner gap.
- **Evidence present:** `v2_unique_bundle.json`,
  `v2_unique_set_validation_report.json`, `v2_unique_set_unsupported_report.json`.
- **Upstream required:** certified unique definitions + calculable mechanical text.
- **Downstream required:** proven consumption of mechanical effects (much is
  tooltip/prose, non-calculable); fail-visible unsupported handling.
- **Fail-visible req:** non-calculable unique effects must stay visibly unsupported.
- **Blockers/gaps:** unsupported mechanics; prose parsing; planner gap.
- **Classification:** `blocked_missing_downstream_consumption_evidence`.

### 3.4 set items
- **Apparent state:** trusted generated assets; partial; **unsupported**; planner gap.
- **Evidence present:** `v2_set_bundle.json`, `v2_unique_set_unsupported_report.json`.
- **Upstream required:** certified set definitions + set-bonus mechanics.
- **Downstream required:** proven set-bonus consumption; fail-visible unsupported.
- **Blockers/gaps:** set-bonus behavior non-calculable in places; planner gap.
- **Classification:** `blocked_missing_downstream_consumption_evidence`.

### 3.5 idols
- **Apparent state:** trusted generated assets; partial; planner gap.
- **Evidence present:** `v2_idol_bundle.json`, `v2_idol_affix_bundle.json`,
  `v2_idol_validation_report.json`.
- **Upstream required:** certified idol affixes + slot rules.
- **Downstream required:** ingestion + schema validation + calculable path.
- **Blockers/gaps:** no stable calculable path; planner gap.
- **Classification:** `partially_ready_requires_evidence`.

### 3.6 skills
- **Apparent state:** trusted generated assets; partial; **unsupported**;
  **schema_mismatch**; planner gap.
- **Evidence present:** `v2_skill_bundle.json`, `v2_skill_validation_report.json`,
  `v2_skill_unsupported_report.json`, `v2_skill_identity_alignment_report.json`,
  `v3_passive_skill_mechanical_comparison_report.json`.
- **Upstream required:** certified skill metadata/base damage + resolved skill
  identity; schema-versioned artifacts.
- **Downstream required:** skill identity bridge (currently **unbridged**); schema
  alignment; fail-visible unsupported nodes.
- **Blockers/gaps:** unresolved skill ownership links; schema mismatch; planner gap;
  34 skill base-damage values are approximations (README/limitations).
- **Classification:** `blocked_missing_schema_or_provenance_evidence`.

### 3.7 passives
- **Apparent state:** trusted generated assets; partial; **unsupported**; planner gap.
- **Evidence present:** `v2_passive_tree_bundle.json`,
  `v2_passive_tree_validation_report.json`, `v2_passive_unsupported_report.json`,
  `v2_passive_skill_identity_remap_report.json`.
- **Upstream required:** certified passive nodes + stat payloads + identity remap.
- **Downstream required:** node→stat resolution proven; ~60.8% of stat entries are
  preserved in `special_effects` (non-numeric); fail-visible for unmapped nodes.
- **Blockers/gaps:** partial node→stat mapping; scripted/text-only nodes
  unsupported; planner gap.
- **Classification:** `blocked_missing_downstream_consumption_evidence`.

### 3.8 crafting data
- **Apparent state:** partial; **missing** trusted generated coverage; planner gap.
- **Evidence present:** craft services consume affix data, but `crafting_materials`
  is classified `missing` (no trusted generated bundle).
- **Upstream required:** certified crafting materials + rules bundle with provenance.
- **Downstream required:** ingestion path + schema validation once upstream exists.
- **Blockers/gaps:** no upstream trusted generated crafting-materials coverage.
- **Classification:** `blocked_missing_upstream_certification`.

### 3.9 modifiers / stat mappings
- **Apparent state:** trusted generated assets; partial; planner gap; blocked
  modifiers visible.
- **Evidence present:** `v2_modifier_registry.json`,
  `v2_modifier_validation_report.json`, `v2_modifier_blocked_reasons_report.json`,
  `missing_modifier_reference_mapping_report.json`,
  `forge_safe_stat_key_mapping_report.json`, controlled modifier resolver reports,
  `v3_stat_identity_resolution_policy_report.json`.
- **Upstream required:** certified modifier registry + stat identity + value
  normalization.
- **Downstream required:** resolution beyond audit-only; clear blocked/unresolved
  fail-visible records.
- **Blockers/gaps:** value normalization audit-only; blocked + missing-reference
  modifiers visible; planner gap.
- **Classification:** `blocked_missing_downstream_consumption_evidence`.

### 3.10 relationship integrity between game objects
- **Apparent state:** cross-cutting; partial; planner gap.
- **Evidence present:** skill identity alignment + passive/skill identity remap
  reports; mechanical comparison reports.
- **Upstream required:** certified relationship/ownership links (skill↔skill tree,
  class↔mastery, item↔affix eligibility, node↔stat).
- **Downstream required:** bridged identity resolution (currently unbridged for
  skills); referential validation on ingest.
- **Blockers/gaps:** unresolved/unbridged links; no single owning system_id.
- **Classification:** `blocked_missing_downstream_consumption_evidence`.

### 3.11 provenance metadata
- **Apparent state:** present; partial; schema_mismatch.
- **Evidence present:** `trusted_extraction_manifests` (system),
  `v4_5b_4_provenance_lineage_visibility_report.json`,
  `v2_affix_display_provenance_report.json`,
  `v3_3_runtime_provenance_contracts_report.json`.
- **Upstream required:** complete provenance/lineage for every generated artifact.
- **Downstream required:** provenance surfaced in visibility layers + validated.
- **Blockers/gaps:** schema mismatch; incomplete lineage coverage.
- **Classification:** `partially_ready_requires_evidence`.

### 3.12 schema contracts
- **Apparent state:** trusted/partial; **schema_mismatch**; planner gap.
- **Evidence present:** `v2_canonical_contract_report.json`, `schema_mappings`
  system, `v4_1_schema_continuity_certification_report.json`,
  `v4_1_schema_evolution_governance_report.json`,
  `v4_1_schema_integrity_certification_report.json`.
- **Upstream required:** schema versions on every artifact; contract conformance.
- **Downstream required:** ingest-time schema validation; mismatch fail-visible.
- **Blockers/gaps:** absent schema versions in some report-level artifacts;
  incomplete mapping coverage; recorded schema drift.
- **Classification:** `blocked_missing_schema_or_provenance_evidence`.

### 3.13 patch / version drift metadata
- **Apparent state:** all 27 systems `stale`; patch provenance unknown.
- **Evidence present:** `data/version.json` reports `patch_version = "unknown"`;
  README states patch 1.4.3 / Season 4 (unreconciled);
  `v4_1_schema_evolution_diagnostics_report.json`.
- **Upstream required:** certified patch/version manifest with deterministic
  provenance per sync.
- **Downstream required:** drift detection that marks stale data visibly.
- **Blockers/gaps:** unknown patch provenance; universal stale flag.
- **Classification:** `blocked_missing_schema_or_provenance_evidence`.

### Summary table

| Domain | Apparent state | Readiness classification |
|---|---|---|
| affixes | trusted-assets / partial | `partially_ready_requires_evidence` |
| item bases | trusted-assets / partial / hybrid ingest | `partially_ready_requires_evidence` |
| uniques | partial / unsupported | `blocked_missing_downstream_consumption_evidence` |
| set items | partial / unsupported | `blocked_missing_downstream_consumption_evidence` |
| idols | trusted-assets / partial | `partially_ready_requires_evidence` |
| skills | partial / unsupported / schema_mismatch | `blocked_missing_schema_or_provenance_evidence` |
| passives | partial / unsupported | `blocked_missing_downstream_consumption_evidence` |
| crafting data | partial / missing | `blocked_missing_upstream_certification` |
| modifiers/stat mappings | partial / blocked visible | `blocked_missing_downstream_consumption_evidence` |
| relationship integrity | partial / unbridged | `blocked_missing_downstream_consumption_evidence` |
| provenance metadata | partial / schema_mismatch | `partially_ready_requires_evidence` |
| schema contracts | partial / schema_mismatch | `blocked_missing_schema_or_provenance_evidence` |
| patch/version drift | stale / unknown | `blocked_missing_schema_or_provenance_evidence` |

**Domains classified `promotion_ready`: none (0).**

---

## 4. Required Trust Promotion Gates (universal)

Before *any* domain may be promoted from advisory/partial/diagnostic to trusted,
**all** of these must be satisfied for that domain:

1. **Upstream certification present** — `last-epoch-data` certifies the domain.
2. **Artifact provenance present** — source/lineage recorded for each artifact.
3. **Schema contract present** — versioned schema the artifact conforms to.
4. **Deterministic artifact hash/report present** — reproducible hash + replay.
5. **Downstream ingestion path identified** — a real, central ingestion route in
   `le-the-forge` (not a hybrid/hardcoded fallback).
6. **Downstream schema validation present** — validated at ingest; mismatches fail
   visibly.
7. **Downstream visibility/debug state present** — domain state is observable in
   the trust/visibility surfaces.
8. **Unsupported/unknown/quarantined records remain fail-visible** — never
   silently promoted or defaulted.
9. **Planner/runtime consumption is scoped and tested** — only the proven
   capability is enabled, with tests; `stable_calculable_count > 0` where
   calculation is claimed.
10. **Public docs updated only after evidence exists** — README/site wording
    follows the certified state, never precedes it.

A domain is `promotion_ready` only when every applicable gate is green **for the
specific capability being promoted**.

---

## 5. Downstream Consumption Requirements (by capability)

Promotion is per-capability. Increasing evidence is required as consumption
deepens:

- **Display only** — gates 1–8: certified artifact, provenance, schema, ingestion,
  validation, visibility; unknowns fail-visible. (Lowest bar.)
- **Advisory planner output** — display gates **plus** explicit "advisory /
  not-certified" labeling and fail-visible gaps; no authority implied.
- **Deterministic calculation** — advisory gates **plus** a tested calculable path
  (`stable_calculable_count > 0`), value normalization beyond audit-only, and
  regression tests.
- **Comparison** — calculation gates **plus** proven parity/consistency across
  compared records.
- **Recommendation** — comparison gates **plus** certified inputs end-to-end; must
  remain advisory until certified.
- **Optimization** — recommendation gates **plus** scoped, tested optimization over
  certified inputs only.
- **Simulation** — calculation gates **plus** certified mechanical coverage for the
  simulated systems; uncovered mechanics fail-visible.
- **Public confidence labels** — all relevant gates green **and** the coverage
  audit reflects the certified state; only then may public wording be raised.

No capability above display is currently supported by evidence for any domain
(`stable_calculable_count = 0`, `planner_dependency_gap` everywhere).

---

## 6. Current Risks

- **"Trusted generated assets exist" can be misread as "trusted domain."** The
  matrix marks 17 systems with a `trusted` flag while the program certification is
  `..._partial_fail_visible` and `untrusted_system_count = 27`. Readers must not
  treat the per-asset trusted flag as promotion.
- **Hybrid/hardcoded ingestion** for some domains (item bases, passives, enemy
  profiles) means generated artifacts are not always the consumed source — a
  promotion based on the artifact alone would not reflect what runs.
- **Patch provenance unknown** (`data/version.json: patch_version = "unknown"`)
  while README states a concrete patch — any "current/trusted" claim risks
  presenting stale data as current.
- **Entry-point capability language** (simulation/optimization) was scoped to
  advisory in prior phases; this audit must not re-imply completeness. No domain
  here is promoted.

(Prior phases already scoped README/ROADMAP/ARCHITECTURE capability claims to
advisory/partial; this audit adds no new capability claims.)

---

## 7. Recommended Next Phases (narrow)

1. **Per-domain promotion checklists** — instantiate the §4 gates as a checklist
   artifact for the closest domains (affixes, item bases, idols, provenance) to
   make "what's missing" explicit and trackable.
2. **Ingestion-path certification (read-only audit)** — confirm, per domain,
   whether the consumed source is the generated artifact or a hybrid/hardcoded
   fallback; record gaps (no logic changes).
3. **Schema-version backfill audit** — identify report-level artifacts missing a
   schema version and the mismatches recorded for skills/payloads.
4. **Patch/provenance reconciliation** — resolve `patch_version = "unknown"` vs the
   README patch on the next upstream sync (owner decision per versioning policy).
5. **Skill identity bridge audit** — narrow audit of the unbridged skill identity
   links blocking the skill domain.

Each is a narrow audit/checklist phase. No broad rewrites, no promotions, no
runtime/planner changes.

---

## Final Classification

```text
no_domain_promotion_ready_evidence_gates_unmet
```

`le-the-forge` is not ready to promote any Last Epoch data domain to trusted.
Zero domains are `promotion_ready`; the closest (affixes, item bases, idols,
provenance metadata) are `partially_ready_requires_evidence`, and the rest are
blocked on specific upstream certification, downstream consumption, or
schema/provenance evidence as catalogued in §3.
