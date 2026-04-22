# The Forge -- Documentation

Welcome to the official documentation for **The Forge**.

The Forge is a simulation-driven analysis platform for Last Epoch, designed to evaluate builds, predict crafting outcomes, simulate boss encounters, and provide optimization insights using backend-driven engines.

---

## Documentation Index

**Reference**

- [api_reference.md](api_reference.md) -- Full REST API reference with all endpoints, auth, request/response shapes, and rate limits
- [engine_architecture.md](engine_architecture.md) -- Every engine module, its inputs, outputs, and how engines chain together
- [data_models.md](data_models.md) -- Every SQLAlchemy model with fields, types, relationships, and indexes
- [simulation_design.md](simulation_design.md) -- Combat simulation design, stat pipeline layers, Monte Carlo methodology
- [passive_tree.md](passive_tree.md) -- Passive tree system design, layout, path validation, and allocation state

**Operations**

- [deployment.md](deployment.md) -- Production deployment runbook for Render + Cloudflare (service creation order, custom domains, SSL, smoke tests)
- [production_setup.md](production_setup.md) -- Production environment configuration, database migration, seed commands, secret rotation
- [rollback.md](rollback.md) -- Emergency rollback procedures: Render service rollback, Postgres backup restore, CORS bypass
- [deployment_readiness.md](deployment_readiness.md) -- 2026-04-21 deployment readiness audit (backend, frontend, CI/CD, docs checklist)

**Transparency**

- [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) -- Public-facing disclosure of verified, approximate, and incomplete systems
- [dps_audit_report.md](dps_audit_report.md) -- DPS calculation audit identifying gaps and formula verification
- [skill_damage_audit.md](skill_damage_audit.md) -- Skill base-damage calibration audit for the 34 estimated skills
- [audits/](audits/) -- Dated audit reports (issue board audits, post-deployment audits, etc.)

---

## Core Philosophy

The Forge is built around:

- **Deterministic calculations** -- reproducible results for any given input
- **Monte Carlo simulations** -- statistical analysis across thousands of runs
- **Data-driven recommendations** -- insights derived from game data, not opinions

---

## Key Architectural Rule

The backend is the **single source of truth**.

The frontend:
- Sends input
- Receives results
- Renders UI

It does **not** perform game calculations.
