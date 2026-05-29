# Data Dependency Governance Alignment

> Follow-up to the Last Epoch data dependency documentation audit. Records the
> documentation corrections made to resolve the overclaim and dependency-chain
> issues the audit identified.
>
> Documentation/governance only. No runtime, planner, simulator, backend,
> frontend, ingestion, extraction, or generated-JSON logic was changed. No
> certification status was fabricated. No limitation/warning/quarantine/
> diagnostic-only language was removed.

- **Date:** 2026-05-29
- **Branch:** `docs/data-dependency-governance-alignment` (cut from `dev`)
- **Predecessor audit:** [`LAST_EPOCH_DATA_DEPENDENCY_DOCUMENTATION_AUDIT.md`](LAST_EPOCH_DATA_DEPENDENCY_DOCUMENTATION_AUDIT.md)
  (classification: `documentation_partially_aligned_with_last_epoch_data_dependency`)
- **Canonical reference produced:** [`../DATA_DEPENDENCY.md`](../DATA_DEPENDENCY.md)

---

## 1. What Was Corrected

1. **Created the canonical dependency document** `docs/DATA_DEPENDENCY.md`,
   documenting the chain `last-epoch-data → generated artifacts →
   schema/provenance/certification → ingestion → visibility/debug → scoped
   planner/runtime → public claims`, the data trust rules, required upstream
   domains, downstream behavior by data state, and the public-claims policy.
2. **README opening + intro scoped.** The product description now states the
   engine is deterministic but that accuracy is bounded by **partial** game-data
   trust being rebuilt upstream; "concrete answer" → "deterministic, inspectable
   answer for the game data it currently has"; mechanical coverage explicitly
   marked **not complete**; optimization/upgrade/ranking outputs marked
   **advisory** and not yet certified.
3. **README Features scoping banner** added: feature accuracy is bounded by data
   confidence; optimization/upgrade/ranking/recommendation outputs are advisory
   and not certified against trusted upstream data; mechanical coverage is partial.
4. **README data-ownership wording corrected.** "Data Sources" and "Versioning"
   now state game data originates upstream in `last-epoch-data` and that The Forge
   **ingests** it rather than being the authoritative extractor.
5. **README roadmap section scoped.** "Phases 1–9 complete" reframed as
   implementation-complete vs. trusted mechanical coverage; future
   optimization/AI phases explicitly gated on upstream + downstream certification.
6. **`docs/README.md` index** now lists `DATA_DEPENDENCY.md` as the canonical
   "start here" entry in **Data & Trust**, and the "Data-driven recommendations"
   philosophy line was scoped to "advisory … bounded by upstream data confidence".
7. **`ROADMAP.md`** gained a trust-first preamble, the "Completed" header is now
   "Completed (feature implementation)", and the Future Phases gate
   optimization/encounter-optimization/AI work behind trusted data + consumption
   certification, plus an explicit trusted-data prerequisite track.
8. **`ARCHITECTURE.md`** reworded so `last-epoch-data` is named as the upstream
   extraction/generation source of truth and `scripts/sync_game_data.py` is
   described as **ingest + normalization**, not extraction; the System Overview
   distinguishes calculation source-of-truth (backend) from game-data
   source-of-truth (upstream).

---

## 2. Audit Findings Addressed

| Audit finding | Status now |
|---|---|
| **F1** — README did not disclose the `last-epoch-data` dependency | **Resolved** — Status bullet + intro + canonical `DATA_DEPENDENCY.md` link. |
| **F2** — README presented simulation/optimization/recommendations as complete/authoritative | **Resolved (wording)** — claims scoped to deterministic + advisory + partial coverage; not deleted, since the deployed engine does compute them. |
| **F3** — ROADMAP omitted dependency chain / trust-rebuild and ungated future capability | **Resolved** — trust-first preamble, implementation-vs-coverage distinction, gated future phases, prerequisite trusted-data track. |
| **F4** — docs index hid the trust/dependency program | **Resolved** — `DATA_DEPENDENCY.md` added as canonical index entry (audit had already added the Data & Trust group). |
| **F5** — ARCHITECTURE framed The Forge as the extractor/normalizer | **Resolved** — reworded to upstream extraction + downstream ingestion. |
| **F7** — README "Data Confidence" not tied to upstream provenance | **Partially addressed** — intro + Features banner now tie confidence to upstream trust and `DATA_DEPENDENCY.md`; the confidence **table** itself was preserved verbatim (see §5). |
| **F8** — governance/migration layer already aligned | **No change needed** — preserved. |

---

## 3. Findings That Remain Open

- **F6 — Inconsistent version signals** (`VERSION` = 0.8.0, `package.json` = 0.3.0,
  git tag `v2.5.0`, migration series at V4.5). **Open.** Reconciling these
  requires owner intent on the authoritative versioning scheme (product line vs.
  data-trust program line) and touches non-doc files; left as a recommendation.
- **F7 (residual)** — A provenance/certification column or note inside the README
  "Data Confidence" table itself was intentionally **not** added, to avoid
  asserting per-row upstream certification states that are not yet proven. The
  surrounding scoping text now carries the qualification instead.
- **Deployed-runtime reconciliation** — Wording was scoped conservatively rather
  than asserting the deployed product's exact runtime enablement state, which is
  not verifiable from documentation alone (the `*_enabled=false` boundaries are
  governance-layer prohibitions for the trusted-consumption path).

---

## 4. Files Changed

**Created**
- `docs/DATA_DEPENDENCY.md` (canonical dependency reference)
- `docs/migration/DATA_DEPENDENCY_GOVERNANCE_ALIGNMENT.md` (this document)

**Modified**
- `README.md` — Status bullet; "What Is The Forge" intro; Features scoping banner;
  Data Sources / Versioning ingestion wording; Roadmap section scoping.
- `docs/README.md` — `DATA_DEPENDENCY.md` canonical index entry; scoped philosophy
  line.
- `ROADMAP.md` — trust-first preamble; Completed header; gated Future Phases.
- `ARCHITECTURE.md` — System Overview source-of-truth split; Data Pipeline and
  Data Sync Pipeline ingestion wording.

---

## 5. Intentionally Left Unchanged (and Why)

- **All `KNOWN_LIMITATIONS.md` and README "Known Limitations" entries** — these are
  honest, specific disclosures and must be preserved (not proven obsolete).
- **README "Data Confidence" table rows** — accurate per-value confidence labels;
  preserved verbatim. No fabricated certification was added.
- **Governance/migration layer docs** (`TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md`,
  `MACBOOK_TRANSITION_SAFETY_AUDIT.md`, `FORGE_*`, V2.5–V4.5 series) — already
  aligned; left as-is, only linked.
- **Generated reports under `docs/generated/`** — not hand-edited; no generator was
  run as part of this documentation phase.
- **Version files** — see F6; left for an owner decision.
- **The product vision / tagline** — retained; only the completeness/authority
  implications around it were scoped.

---

## 6. Final Classification

```text
data_dependency_documentation_partially_aligned
```

Rationale: the dependency chain, data-ownership framing, and capability-claim
scoping are now consistent across the entry-point docs (README, docs index,
ROADMAP, ARCHITECTURE) and anchored to a canonical `DATA_DEPENDENCY.md`. Full
alignment is held back only by the open version-signal reconciliation (F6) and by
the deliberate decision not to assert upstream certification states that are not
yet proven — i.e., remaining gaps are bounded by **missing upstream certification
evidence**, not by documentation wording.

---

## Next Recommended Step

Reconcile version signals (F6) under an explicit versioning policy, then — once
`last-epoch-data` trusted-bundle ingestion is production-consumed and certified —
revisit README/ROADMAP capability language to promote specific domains from
"advisory/partial" to "trusted" strictly in step with the certification state
reported by `TRUSTED_GAMEPLAY_DATA_COVERAGE_AUDIT.md`.
