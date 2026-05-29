# Data Dependency — How The Forge Depends on `last-epoch-data`

> Canonical explanation of the data dependency between `le-the-forge` (this repo,
> the consumer / analysis application behind [epochforge.gg](https://epochforge.gg))
> and `last-epoch-data` (the upstream extraction / data-generation repo).
>
> This is a governance/documentation reference. It does not change runtime,
> planner, simulator, backend, frontend, ingestion, extraction, or generated
> data behavior. It defines the trust rules those layers are expected to honor.

---

## 1. Purpose

`le-the-forge` is **downstream** of `last-epoch-data`.

- `last-epoch-data` is the canonical extraction / compiler / source-of-truth repo
  for Last Epoch game data. The cross-repo data architecture contracts
  (`FORGE_DATA_CONTRACT.md`, `DATA_BUNDLE_SPEC.md`) live there, not here
  (see [`FORGE_SYSTEM_PILLARS.md`](FORGE_SYSTEM_PILLARS.md)).
- `le-the-forge` is a **consumer**: it ingests generated artifacts, exposes them
  through visibility/debug layers, and — only where proven — uses them in scoped
  planner/runtime behavior and public-facing capability claims.

Trusted data must come from **upstream generated artifacts and certification
evidence**, not from self-asserted confidence inside this repo. When `le-the-forge`
hardcodes, approximates, or falls back to legacy data, that data is **not** trusted
just because it ships — it is trusted only when upstream provenance and
certification support it.

---

## 2. Dependency Chain

```
last-epoch-data
  → generated artifacts (bundles, normalized JSON)
    → schema / provenance / certification reports
      → le-the-forge ingestion (data pipeline, registries, DB seed)
        → visibility / debug layers (trust surfaces, coverage reports)
          → scoped planner / runtime behavior (only where certified)
            → public-facing capability claims (README / epochforge.gg)
```

Each arrow is a **trust boundary**. A capability may only be claimed at a later
stage if every earlier stage supports it. Concretely:

- A planner/runtime feature may not be promoted to "supported" unless ingestion +
  schema/provenance + upstream certification cover the data it depends on.
- A public claim (README, marketing, `epochforge.gg`) may not exceed the proven
  scoped-support state.

Current state of the chain is tracked in
[`migration/TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md`](migration/TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md),
which presently certifies coverage as `trusted_gameplay_coverage_partial_fail_visible`
(generated trusted assets exist, but planner completeness is **not** certified).

---

## 3. Data Trust Rules

These rules apply to every data domain consumed by `le-the-forge`:

1. **Trusted only with upstream evidence.** A domain is "trusted" only when backed
   by upstream generated artifacts plus provenance/schema/certification evidence.
   Self-asserted confidence inside this repo is not trust.
2. **Partial stays partial.** Partially covered domains must remain classified as
   partial. Partial is a first-class state and must not be rounded up to "complete".
3. **Unknown stays unknown.** Unknown-source or unknown-trust data must remain
   labeled unknown, not silently treated as verified.
4. **Quarantined data is not silently promoted.** Data isolated for review or
   excluded from production paths must stay isolated until upstream evidence
   clears it.
5. **Diagnostic-only is not production-safe.** Values produced by diagnostic /
   dry-run / audit-only tooling must not be treated as production-certified.
6. **Public wording must not exceed proven certification.** No README, UI, or
   `epochforge.gg` statement may claim more than the proven scoped-support state.

These rules are deliberately conservative: when in doubt, a domain is *less*
trusted, not more. Limitation, warning, quarantine, and diagnostic-only language
must be preserved unless it is directly proven obsolete.

---

## 4. Required Upstream Data Domains

`le-the-forge` depends on the following domains being supplied — and, for deeper
functionality, **certified** — by `last-epoch-data`:

- **Items & item bases** — base items, item types, implicits, rarities
- **Affixes** — affix definitions, tiers, eligibility, value ranges
- **Uniques** — unique item definitions and their mechanical text/effects
- **Set items** — set definitions and set bonuses
- **Idols** — idol affixes and slot rules
- **Skills** — skill metadata, base damage, skill trees, skill nodes
- **Passives** — passive trees, nodes, node stat payloads, layout coordinates
- **Crafting data** — crafting rules, materials, forging-potential model inputs
- **Modifiers / stat mappings** — modifier registry, stat identity, value
  normalization, stat-key mappings
- **Relationships between game objects** — skill ownership, class/mastery links,
  node→stat resolution, item→affix eligibility
- **Provenance & schema metadata** — source-kind, trust state, schema versions,
  patch/version manifests
- **Trust / certification reports** — coverage, support-matrix, schema-alignment,
  and extraction-gap reports

Domains with known **missing** or **incomplete** upstream coverage (per the
coverage audit) include blessings, crafting materials, monolith/echo systems,
bosses, ailments, damage types, and planner-facing gameplay contracts. These must
not be presented as fully supported.

---

## 5. Downstream Behavior Expectations

How `le-the-forge` is expected to behave by data state:

| Data state | Expected downstream behavior |
|---|---|
| **Trusted** (upstream-certified) | May be consumed by visibility and, where the chain supports it, scoped planner/runtime. May back a public capability claim. |
| **Partial** | Consume what is covered; keep the partial classification visible. Do not infer the uncovered remainder. No "complete coverage" claim. |
| **Unsupported** | Surface as a reportable, visible unsupported state. Do not silently substitute a guess or treat as failure. |
| **Quarantined** | Keep isolated from production/planner paths until upstream evidence clears it. Visible, not promoted. |
| **Diagnostic-only** | Use for inspection/debug only. Never treat as production-certified or as the basis of a public claim. |
| **Missing** | Report the gap explicitly. Do not fabricate a value to fill it. |
| **Stale after a patch** | Treat as suspect until re-synced/re-certified upstream. Patch/version manifests should make staleness visible rather than presenting old data as current. |

The governing principle: **unsupported / unknown data must remain visible, never
silently treated as trusted.**

---

## 6. Public-Facing Claims Policy

Public wording — README, UI copy, and anything on
[epochforge.gg](https://epochforge.gg) — must be scoped to proven support.

- The Forge may describe itself as a **deterministic** analysis engine: for a
  given input and a given data set, it produces the same inspectable result. That
  is provable today.
- The Forge **may not** claim **complete** simulation, optimization, upgrade
  recommendation, ranking, scoring, or production planner authority over Last
  Epoch mechanics until upstream trust **and** downstream consumption
  certification support those claims.
- Optimization, upgrade, ranking, and recommendation outputs are **advisory** and
  bounded by the confidence of the underlying data. They must be presented as
  such, not as certified ground truth.
- No public claim may outrun the certification state reported by
  [`migration/TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md`](migration/TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md).

Honest disclosure of approximations and limitations (e.g.
[`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md)) is required and must be preserved.

**Version labels do not override trust state.** A product, package, git-tag, or
governance-phase version number never implies more trusted data, more mechanical
coverage, or any certification. If a version label and the certified trust state
appear to disagree, the trust state wins and public wording follows it. See
[`VERSIONING_POLICY.md`](VERSIONING_POLICY.md).

---

## 7. Relationship to Existing Trust Docs

This document is the canonical entry point for the data dependency. It sits above
and links to the existing trust/governance material:

- [`migration/LAST_EPOCH_DATA_DEPENDENCY_DOCUMENTATION_AUDIT.md`](migration/LAST_EPOCH_DATA_DEPENDENCY_DOCUMENTATION_AUDIT.md)
  — the audit that motivated this document.
- [`migration/DATA_DEPENDENCY_GOVERNANCE_ALIGNMENT.md`](migration/DATA_DEPENDENCY_GOVERNANCE_ALIGNMENT.md)
  — the follow-up record of corrections made in response to the audit.
- [`migration/TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md`](migration/TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md)
  — current trusted gameplay data coverage state and what remains blocked.
- [`migration/TRUSTED_DATA_PROMOTION_READINESS_AUDIT.md`](migration/TRUSTED_DATA_PROMOTION_READINESS_AUDIT.md)
  — the upstream + downstream evidence and universal gates required before any
  domain may be promoted from advisory/partial/diagnostic to trusted (no domain is
  currently promotion-ready).
- [`FORGE_SYSTEM_PILLARS.md`](FORGE_SYSTEM_PILLARS.md) — product/system direction
  and why upstream extraction priorities matter.
- [`FORGE_DATA_CONSUMER_AUDIT.md`](FORGE_DATA_CONSUMER_AUDIT.md) — how this repo
  consumes game data, with `last-epoch-data` as canonical source of truth.
- [`migration/`](migration/) — the full trusted-data rebuild, schema/provenance
  governance, and dependency-chain migration series.
