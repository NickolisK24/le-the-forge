# Versioning Policy — What Each Version Signal Means

> This repository carries several independent version-like signals. They are
> **not** the same number and are **not meant to match**. This document defines
> what each one means, which file owns it, and when it changes, so the repo does
> not look contradictory to contributors or AI agents.
>
> Policy/documentation only. It does not change runtime behavior, package
> versions, the `VERSION` file, git tags, or any code.

---

## 1. Purpose

The Forge has evolved along **two parallel tracks** plus several supporting
metadata signals:

- a **product / feature track** (the deployed v0.x application), and
- a **trust / governance track** (the V2.5 → V4.x data-trust and governance
  program).

Because these tracks advance independently — and because packages, deployments,
data syncs, and git tags each carry their own version metadata — the repo
contains multiple numbers that look like "the version" but describe different
things. Conflating them creates false impressions (e.g. reading a `v4.x`
governance phase as a "version 4 product", or a package version as proof of
release maturity). This policy keeps them distinct.

---

## 2. Version Signal Definitions

| # | Signal | What it describes |
|---|---|---|
| 1 | **Product / public release version** | The user-facing release line of the deployed application (v0.x). |
| 2 | **Package / application version** | Node package metadata for build/tooling (`package.json`). Not a release-maturity claim. |
| 3 | **Internal roadmap phase** | Product feature-development phases (e.g. "Phase 9"). Planning labels, not release numbers. |
| 4 | **Migration / governance phase** | Trust/data-governance program phases (V2.5 → V4.x). Historical and ongoing governance milestones. |
| 5 | **Public deployment / site version** | The version string the running service reports (`/api/version`, `/api/health`), sourced from the `VERSION` file. |
| 6 | **Historical Git tags / releases** | Snapshots cut at a point in time (e.g. `v2.5.0`, the trust-foundation release). |

Supporting metadata signals (related but distinct):

- **Data / patch sync state** — `data/version.json` (`patch_version`, `synced_at`)
  and the README "Game data synced to" line; tracks the Last Epoch patch the data
  reflects, not the application version.
- **Internal schema / contract version identifiers** — strings such as
  `v3_8.coordination_*` in backend modules; these version individual
  schemas/contracts, not the product.

---

## 3. Current Observed Version Signals

Recorded as observed on this branch. Values not verifiable are marked **unknown**.
No values were invented or changed by this document.

| Signal | Observed value | Source |
|---|---|---|
| Product / public release version | `v0.8.0` | `README.md` badge + prose |
| Latest changelog entry | `0.8.1` (2026-04-21) | `CHANGELOG.md` (top entry) |
| Package / application version (root) | `0.3.0` (name `the-forge`, private) | `package.json` |
| Package version (frontend) | `0.1.0` (name `the-forge-frontend`) | `frontend/package.json` |
| Public deployment / site version | `0.8.0` (reads `VERSION`) | `VERSION` → `backend/app/__init__.py` `__version__` → `/api/version`, `/api/health` |
| Internal roadmap phase | Phases 1–9 complete; 10–16 future | `ROADMAP.md` |
| Migration / governance phase | `V2.5` → `V4.5` series | `docs/migration/` |
| Historical Git tags | `v2.5.0` only — "ship v2.5 trust foundation" (2026-05-14) | `git tag` |
| Data / patch sync state | `patch_version = "unknown"`; README states patch `1.4.3`, Season 4 | `data/version.json`, `README.md` |
| Internal schema/contract IDs | e.g. `v3_8.coordination_*` | backend modules (code) |

Observed timeline nuance (not a defect, but the source of apparent contradiction):
the `v2.5.0` **git tag** (2026-05-14) is both numerically higher and later than
the **product** `v0.8.x` line (2026-04-21). They are different tracks — the tag
belongs to the trust-foundation/governance line, the v0.8.x line is the product
release line. See §5.

---

## 4. Authoritative Source Rules

Each signal has exactly one owning source. Other places that mention it are
**reflections** and should defer to the owner.

| Signal | Authoritative owner |
|---|---|
| Public deployment / runtime app version | **`VERSION`** (read at runtime by `backend/app/__init__.py`; surfaced at `/api/version`, `/api/health`) |
| Product / public release version (human-facing) | **`VERSION`** is the canonical number; `README.md` and the version badge reflect it; `CHANGELOG.md` owns the release **history** |
| Package / application (Node) version | **`package.json`** (root) and **`frontend/package.json`** (frontend) — tooling metadata only |
| Internal roadmap (product) phases | **`ROADMAP.md`** |
| Migration / governance phases | **`docs/migration/`** documents (historical labels are immutable) |
| Historical release snapshots | **Git tags** (e.g. `v2.5.0`) |
| Data / patch sync state | **`data/version.json`** (and the README "synced to" line as a reflection) |
| Internal schema/contract versions | the **backend module** that defines each schema constant |

> Note: the runtime app version is owned by the `VERSION` file, **not** by
> `package.json`. The root `package.json` version (`0.3.0`) is build/tooling
> metadata and is not the deployed application version.

---

## 5. Non-Conflict Rule

These values are **allowed to differ** because they describe different concepts.

- A `package.json` version of `0.3.0` and a `VERSION` of `0.8.0` is **not** a
  conflict — one is Node tooling metadata, the other is the runtime app version.
- A `v2.5.0` git tag and a `v0.8.0` product version are **not** a conflict — the
  tag belongs to the trust-foundation/governance line; the product line is v0.x.
- A `V4.5` migration phase and a `v0.8.0` product version are **not** a conflict —
  one is a governance-program milestone, the other a product release.

Do not "fix" these by forcing them equal. The fix for apparent contradiction is
**clarity of meaning** (this policy), not numeric normalization.

---

## 6. Update Policy

When each signal changes:

- **`VERSION` / runtime app version** — only when a new application build/release
  is cut for deployment.
- **`package.json` / `frontend/package.json`** — only on a package/tooling
  release change; independent of product release maturity.
- **`CHANGELOG.md`** — appended whenever a release is documented; existing entries
  are historical and not rewritten.
- **Roadmap phases (`ROADMAP.md`)** — only when a product feature phase actually
  advances.
- **Migration/governance phases (`docs/migration/`)** — a new phase adds new
  documents; **historical phase documents and names are retained as-is**.
- **Git tags** — only when a release snapshot is cut; tags are immutable history.
- **`data/version.json` / patch line** — only when game data is re-synced from
  upstream `last-epoch-data` for a new patch.

---

## 7. AI / Contributor Guardrails

Explicitly:

- **Do not** "normalize" all version numbers to match.
- **Do not** rename historical migration docs (e.g. the `V4_*` files) to match the
  current phase.
- **Do not** treat a `V4.x` governance phase as equivalent to a public **product**
  version.
- **Do not** treat the `package.json` version as proof of public release maturity.
- **Do not** infer capability completion, coverage, or certification from any
  version label. Capability is governed by trusted-data evidence, not by a number.
- **Do not** change `VERSION` or `package.json` solely to reduce visual mismatch;
  change them only per §6, with a real release reason.

---

## 8. Relationship to Data Dependency Governance

Version labels are orthogonal to data trust. A higher version number — product,
package, tag, or governance phase — does **not** imply more trusted data, more
mechanical coverage, or any certification.

- [`DATA_DEPENDENCY.md`](DATA_DEPENDENCY.md) — the canonical dependency chain and
  data-trust rules. Trust comes from upstream `last-epoch-data` evidence, not from
  version numbers.
- [`migration/DATA_DEPENDENCY_GOVERNANCE_ALIGNMENT.md`](migration/DATA_DEPENDENCY_GOVERNANCE_ALIGNMENT.md)
  — the governance alignment that scoped capability claims to proven support.

If a version label and the certified trust state ever appear to disagree, the
trust state (per the coverage audit) wins, and public wording must follow the
trust state — never the version number.
