# Version Signal Reconciliation Audit

> Focused audit resolving finding **F6** (inconsistent version signals) from the
> Last Epoch data dependency documentation audit. Versioning policy and
> documentation alignment only — no runtime code, `package.json`, `VERSION`, git
> tags, or generated JSON were changed.

- **Date:** 2026-05-29
- **Branch:** `docs/version-signal-reconciliation` (cut from `dev`)
- **Predecessor:** [`DATA_DEPENDENCY_GOVERNANCE_ALIGNMENT.md`](DATA_DEPENDENCY_GOVERNANCE_ALIGNMENT.md)
  (left F6 open as an owner decision)
- **Policy produced:** [`../VERSIONING_POLICY.md`](../VERSIONING_POLICY.md)

---

## 1. Executive Summary

The repo carries multiple version-like signals that previously looked
contradictory (e.g. `VERSION` 0.8.0 vs `package.json` 0.3.0 vs git tag `v2.5.0`
vs `V4.5` migration phases). Investigation confirmed these are **not** a single
mis-set number — they describe **different concepts across two parallel tracks**
(a product/feature line and a trust/governance line) plus supporting metadata.

The reconciliation does **not** force the numbers equal. Instead it introduces a
canonical [`VERSIONING_POLICY.md`](../VERSIONING_POLICY.md) that defines each
signal, names its authoritative owner, states a non-conflict rule, and adds
contributor/AI guardrails. Entry-point docs now point to that policy. No version
value was changed, because no existing policy authorized a change and doing so
would risk fabricating release history or breaking the runtime version surfaced
by `/api/version` and `/api/health`.

Key clarifying fact established: the **runtime/app version is owned by the
`VERSION` file** (read by `backend/app/__init__.py`, surfaced at `/api/version`
and `/api/health`), **not** by `package.json`. The root `package.json` version is
Node tooling metadata.

---

## 2. Files Reviewed

- `VERSION`
- `package.json`, `frontend/package.json`
- `README.md`, `CHANGELOG.md`, `ROADMAP.md`
- `docs/README.md`, `docs/DATA_DEPENDENCY.md`, `ARCHITECTURE.md`
- `backend/app/__init__.py` (version reader), `backend/app/routes/version.py`,
  `backend/app/routes/health.py`
- `data/version.json`
- `docs/migration/` phase labels (V2.5 → V4.5), git tags
- backend schema-version constants (e.g. `v3_8.coordination_*`) — observed only

---

## 3. Observed Version Signals

| Signal | Observed value | Source |
|---|---|---|
| Product / public release version | `v0.8.0` | `README.md` badge + prose |
| Latest changelog entry | `0.8.1` (2026-04-21) | `CHANGELOG.md` |
| Package version (root) | `0.3.0` (`the-forge`, private) | `package.json` |
| Package version (frontend) | `0.1.0` (`the-forge-frontend`) | `frontend/package.json` |
| Deployment / runtime app version | `0.8.0` (reads `VERSION`) | `VERSION` → `backend/app/__init__.py` → `/api/version`, `/api/health` |
| Internal roadmap phase | Phases 1–9 done; 10–16 future | `ROADMAP.md` |
| Migration / governance phase | `V2.5` → `V4.5` | `docs/migration/` |
| Historical git tag | `v2.5.0` — "ship v2.5 trust foundation" (2026-05-14) | `git tag` |
| Data / patch sync state | `patch_version="unknown"`; README states `1.4.3`, S4 | `data/version.json`, `README.md` |
| Internal schema/contract IDs | e.g. `v3_8.coordination_*` | backend modules |

---

## 4. Conflicts / Misleading Areas Found

1. **Apparent track collision** — git tag `v2.5.0` (2026-05-14) is higher and
   later than the product `v0.8.x` line (2026-04-21). Without context this reads
   as a contradiction; in fact the tag is on the trust-foundation/governance line.
   *(Now explained by policy §3/§5.)*
2. **Package vs runtime version mismatch** — `package.json` `0.3.0` vs `VERSION`
   `0.8.0`. Looks wrong; actually two different concepts (Node metadata vs runtime
   app version). *(Now explained by policy §4/§5.)*
3. **Changelog vs badge drift** — `CHANGELOG.md` top is `0.8.1` while the badge and
   prose say `v0.8.0`. Minor product-line lag within one owner. *(Recorded; left
   for owner — see §7.)*
4. **Governance phase mistaken for product version** — `V4.5` could be read as
   "version 4". *(Now explicitly guarded against in policy §7.)*
5. **Data patch signal mismatch** — `data/version.json` `patch_version="unknown"`
   vs README `1.4.3`. Distinct data/patch signal, not an app version. *(Recorded;
   data-sync owner decision — §7.)*
6. **Code docstring example** — `backend/app/routes/version.py` docstring shows an
   illustrative `"1.0.0-beta"` / `data_version "1.0.0"` example that matches no
   real signal. *(Left unchanged — code file; see §6.)*

---

## 5. Corrections Made

- **Created `docs/VERSIONING_POLICY.md`** — canonical definitions, current
  observed values, authoritative-source rules, non-conflict rule, update policy,
  AI/contributor guardrails, and the link to data-dependency governance.
- **`README.md`** — added a "Version signals" Status bullet linking the policy and
  stating the signals are separate and that a version number does not imply data
  trust or capability completion.
- **`docs/README.md`** — added `VERSIONING_POLICY.md` to the Data & Trust index.
- **`ROADMAP.md`** — added a note that roadmap phase labels are internal
  planning/governance labels, not package/public-release/governance versions.
- **`docs/DATA_DEPENDENCY.md`** — added a cross-reference that version labels do
  not override trust/certification state (trust state wins).

No numeric version value was changed in any file.

---

## 6. Items Intentionally Left Unchanged

- **`VERSION` (0.8.0)** — it is the authoritative runtime/app version consumed by
  `/api/version` and `/api/health`; changing it would alter the deployed version
  surface with no release reason. Not stale.
- **`package.json` / `frontend/package.json`** — Node tooling metadata; no policy
  authorized a bump, and changing it would not be a real release event.
- **Git tag `v2.5.0`** — immutable historical release snapshot; not renamed.
- **`docs/migration/` phase docs and names (V2.5 → V4.5)** — historical governance
  labels are retained as-is; not renamed.
- **`CHANGELOG.md`** — historical entries left intact (the 0.8.0/0.8.1 drift is a
  product-owner reconciliation, not a docs rewrite).
- **`backend/app/routes/version.py` docstring** — code file; example value left
  untouched to avoid modifying code (recorded as an owner decision).
- **`data/version.json`** — generated/sync artifact; not hand-edited.
- **`ARCHITECTURE.md`** — its only version references are factual endpoint
  descriptions; nothing misleading, so no edit.

---

## 7. Remaining Owner Decisions

- Whether to reconcile the **CHANGELOG `0.8.1` vs badge/`VERSION` `0.8.0`** drift
  (cut a release or align the badge).
- Whether to **bump `VERSION`/`package.json`** under a defined release event (the
  policy now defines the rules; the trigger is an owner call).
- Whether to refresh `data/version.json` `patch_version` from "unknown" to the
  tracked patch on the next upstream sync.
- Whether to update the illustrative example value in the
  `backend/app/routes/version.py` docstring (code change, out of scope here).

None of these block the policy; they are deferred product/release decisions.

---

## 8. Final Classification

```text
version_signals_partially_aligned_pending_owner_decision
```

Rationale: the signals are now **explained and governed by an authoritative
policy**, and entry-point docs point to it, so the repo no longer reads as
contradictory. Full numeric alignment (where desired) and the changelog/patch
drifts remain **owner decisions** with real release triggers, deliberately not
forced by this documentation phase.

---

## Recommended Next Step

Have the owner action the §7 decisions under the new policy — at minimum
reconciling the CHANGELOG/badge drift and refreshing the data patch version on the
next `last-epoch-data` sync — then keep `VERSIONING_POLICY.md`'s "current observed
signals" table updated whenever a signal legitimately changes.
