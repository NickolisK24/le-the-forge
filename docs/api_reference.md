# The Forge -- API Reference

All endpoints are prefixed with `/api`. All responses use the standard JSON envelope:

```json
{
  "data": <payload or null>,
  "meta": <pagination or null>,
  "errors": [{"message": "...", "field": "..."}] or null
}
```

---

## Authentication

Discord OAuth2 with JWT bearer tokens. Protected endpoints require:

```
Authorization: Bearer <token>
```

### `GET /api/auth/discord`
Redirects to Discord OAuth consent page.
**Rate limit:** 20/min

### `GET /api/auth/discord/authorized`
OAuth callback. Exchanges code, creates/updates user, redirects frontend with `?token=<jwt>`.
**Rate limit:** 20/min

### `GET /api/auth/me`
Returns current authenticated user.
**Requires auth.**

### `POST /api/auth/logout`
Stateless logout -- client discards JWT.

### `GET /api/auth/dev-login`
Dev-only JWT bypass. Only available when `FLASK_ENV=development`.

---

## Builds

### `GET /api/builds`
List community builds with filtering and pagination.

**Query params:** `q`, `character_class`, `mastery`, `tier` (S/A/B/C), `is_ssf`, `is_hc`, `is_ladder_viable`, `is_budget`, `cycle`, `sort` (votes/new/tier/views), `page`, `per_page` (max 100)

### `POST /api/builds`
Create a new build. Auth optional (anonymous builds allowed).
**Rate limit:** 20/min

### `GET /api/builds/meta/snapshot`
Legacy meta snapshot (class distribution, tier counts).

### `GET /api/builds/<slug>`
Get a single build by slug. Increments view_count. Includes user_vote if authenticated.

### `PATCH /api/builds/<slug>`
Update a build. **Requires auth.** Owner only.
**Rate limit:** 20/min

### `DELETE /api/builds/<slug>`
Delete a build. **Requires auth.** Owner only.
**Rate limit:** 10/min

### `POST /api/builds/<slug>/vote`
Vote on a build (+1 or -1). Same direction toggles off. **Requires auth.**
**Rate limit:** 30/min

### `POST /api/builds/<slug>/simulate`
Run full simulation pipeline for a saved build. Returns stats, DPS, Monte Carlo, defense, stat upgrades, per-skill DPS breakdown.
**Rate limit:** 10/min

### `POST /api/builds/<slug>/optimize`
Get stat upgrade recommendations for a build.
**Rate limit:** 10/min

### `GET /api/builds/<slug>/optimize`
Sensitivity analysis + ranked upgrades + efficiency scoring.
**Query params:** `mode` (balanced/offense/defense)
**Rate limit:** 10/min. Cached 30 minutes.

---

## Build Analysis

### `GET /api/builds/<slug>/analysis/boss/<boss_id>`
Boss encounter simulation with per-phase results.
**Query params:** `corruption` (default 0)
**Rate limit:** 10/min. Cached 30 minutes.

### `GET /api/builds/<slug>/analysis/corruption`
Corruption scaling curve analysis.
**Query params:** `boss_id` (optional)
**Rate limit:** 10/min. Cached 30 minutes.

### `GET /api/builds/<slug>/analysis/gear-upgrades`
Per-slot gear upgrade ranking.
**Query params:** `slot` (filter to specific slot)
**Rate limit:** 10/min. Cached 30 minutes.

---

## Build Comparison

### `GET /api/compare/<slug_a>/<slug_b>`
Compare two builds with full DPS/EHP simulation, stat deltas, skill comparison, and weighted overall winner (60% DPS / 40% EHP).
Returns 400 if `slug_a == slug_b`. Cache key uses alphabetically sorted slugs.
**Rate limit:** 15/min. Cached 20 minutes.

---

## Meta Analytics

### `GET /api/meta/snapshot`
Full meta analytics: class/mastery distribution, popular skills, popular affixes, average stats by class, current patch.
**Rate limit:** 30/min. Cached 6 hours.

### `GET /api/meta/trending`
Trending builds ranked by view velocity (view_count / age_days, minimum 10 views).
**Rate limit:** 30/min. Cached 1 hour.

---

## View Tracking

### `POST /api/builds/<slug>/view`
Record a build view. IP is SHA-256 hashed before storage. Rate limited to 1 view per IP per build per hour via Redis key. Silently returns 204 if rate limited.
**Rate limit:** 60/min.

---

## Build Reports

### `GET /api/builds/<slug>/report`
Shareable build report with identity, stats, DPS, EHP, top 3 upgrades, skills, gear, and OpenGraph meta tags. Returns 403 for private builds unless requester is owner.
**Rate limit:** 20/min. Cached 1 hour.

---

## Craft Sessions

### `POST /api/craft`
Create a new crafting session.
**Rate limit:** 30/min

### `GET /api/craft/<slug>`
Get a craft session with step history.

### `POST /api/craft/<slug>/action`
Apply a crafting action. Actions: `add_affix`, `upgrade_affix`, `seal_affix`, `unseal_affix`, `remove_affix`.
**Rate limit:** 60/min

### `POST /api/craft/<slug>/undo`
Undo the last crafting action.
**Rate limit:** 30/min

### `GET /api/craft/<slug>/summary`
Get session summary with optimal path search, Monte Carlo simulation, and strategy comparison.

### `DELETE /api/craft/<slug>`
Delete a craft session.
**Rate limit:** 10/min

### `POST /api/craft/predict`
Stateless FP cost prediction. No session required.
**Rate limit:** 30/min

### `POST /api/craft/simulate`
Monte Carlo craft simulation.
**Rate limit:** 20/min

---

## Simulation (Stateless)

These endpoints accept raw build data (no saved build required).

### `POST /api/simulate/stats`
Compute aggregate stats from class/mastery/passives/gear.
**Rate limit:** 60/min (configurable). Cached 5 minutes.

### `POST /api/simulate/combat`
DPS + Monte Carlo simulation. Supports async via `"async": true` in body.
**Rate limit:** 20/min. Cached 5 minutes.

### `POST /api/simulate/defense`
EHP + survivability analysis.
**Rate limit:** 30/min. Cached 5 minutes.

### `POST /api/simulate/optimize`
Stat upgrade recommendations from raw data.
**Rate limit:** 10/min. Cached 5 minutes.

### `POST /api/simulate/sensitivity`
Stat sensitivity analysis with weighted impact scoring.
**Rate limit:** 10/min. Cached 5 minutes.

### `POST /api/simulate/encounter`
Encounter simulation with enemy templates.
**Rate limit:** 15/min (configurable).

### `POST /api/simulate/encounter-build`
Encounter simulation from full build definition.
**Rate limit:** 20/min

### `POST /api/simulate/build`
Full pipeline (stats + combat + defense) in one call. Supports async.
**Rate limit:** 30/min (configurable). Cached 5 minutes.

### `POST /api/simulate/rotation`
Skill rotation simulation with priority ordering and cooldown tracking.
**Rate limit:** 10/min

### `POST /api/simulate/conditional`
Conditional modifier evaluation against simulation state.
**Rate limit:** 30/min

### `POST /api/simulate/multi-target`
Multi-target encounter simulation (AOE, chain, splash).
**Rate limit:** 20/min

---

## Optimization

### `POST /api/optimize/build`
Full variant generation + simulation + ranking.
**Rate limit:** 5/min

---

## BIS Search

### `POST /api/bis/search`
Best-in-slot incremental search with weighted affix targeting.
**Rate limit:** 15/min

---

## Build Import

### `POST /api/import/url`
Proxy-fetch and parse a Last Epoch Tools or Maxroll URL.
**Rate limit:** 20/min

### `POST /api/import/build`
Full import pipeline: detect source, parse, save, track failures.
**Rate limit:** 5/min (authenticated), 2/min (anonymous). Dynamic key function.

---

## Skill Trees

### `GET /api/skills/<skill_id>/tree`
Get skill tree node graph for a specific skill.
**Rate limit:** 30/min. Cached 24 hours.

### `GET /api/builds/<slug>/skills`
Get skill allocation state for a build.
**Rate limit:** 20/min

### `PATCH /api/builds/<slug>/skills/<skill_id>/nodes/<node_id>`
Allocate or deallocate points on a skill tree node.
**Rate limit:** 30/min

---

## Passives

### `GET /api/passives`
All passive nodes. Filter by `class`, `mastery`.

### `GET /api/passives/<character_class>`
Full passive tree for a class.

### `GET /api/passives/<character_class>/<mastery>`
Mastery-specific passive nodes plus base class nodes.

---

## Reference Data

All reference endpoints return static game data. Most are cached 24 hours.

### `GET /api/ref/classes`
All character classes with masteries and skills.

### `GET /api/ref/item-types`
All item type definitions.

### `GET /api/ref/affixes`
All affix definitions. Filter by `type`, `slot`, `class`, `tag`.

### `GET /api/ref/affix-categories`
Affix category descriptions.

### `GET /api/ref/passives`
Passive nodes. Filter by `class`, `mastery`.

### `GET /api/ref/skills`
Skill metadata. Filter by `class`.

### `GET /api/ref/crafting-rules`
FP cost ranges and crafting action rules.

### `GET /api/ref/base-items`
All base item definitions.

### `GET /api/ref/base-items/<base_type>`
Single base item definition.

### `GET /api/ref/fp-ranges`
FP ranges by rarity tier.

### `GET /api/ref/fp-ranges/<rarity>`
FP range for a specific rarity.

### `GET /api/ref/enemy-profiles`
All enemy profiles.

### `GET /api/ref/enemy-profiles/<enemy_id>`
Single enemy profile with resistances and damage types.

### `GET /api/ref/damage-types`
All damage type definitions.

### `GET /api/ref/rarities`
All rarity tier definitions.

### `GET /api/ref/implicit-stats`
All implicit stats by item type.

### `GET /api/ref/implicit-stats/<item_type>`
Implicit stat for a specific item type.

### `GET /api/ref/uniques`
All unique items. Filter by `slot`, `q` (search).

### `GET /api/ref/uniques/<slug>`
Single unique item.

---

## Entities

### `GET /api/entities/bosses`
All boss profiles. Cached 24 hours.

---

## Profile

All profile endpoints require authentication.

### `GET /api/profile`
Current user profile with stats (build count, session count) and recent activity.

### `GET /api/profile/builds`
Paginated list of user's own builds (including private).

### `GET /api/profile/sessions`
Paginated list of user's craft sessions.

---

## Admin

### `GET /api/admin/affixes`
All affixes from data file. Filter by `q`, `type`, `tag`, `slot`.

### `PATCH /api/admin/affixes/<affix_id>`
Update a single affix definition.
**Rate limit:** 30/min

### `GET /api/admin/import-failures`
Paginated import failure log. **Requires auth.**
**Rate limit:** 60/min

---

## Jobs

### `GET /api/jobs/<job_id>`
Poll status of an async simulation job.

---

## System

### `GET /api/version`
Version metadata.

### `POST /api/load/game-data`
Hot-reload all game data and run integrity check.
**Rate limit:** 5/min

---

## Error Responses

All errors follow the envelope format:

```json
{
  "data": null,
  "meta": null,
  "errors": [{"message": "Build not found"}]
}
```

| HTTP Status | Meaning |
|-------------|---------|
| `400` | Bad request / validation error |
| `401` | Unauthorized (missing or expired token) |
| `403` | Forbidden (not the owner or not admin) |
| `404` | Resource not found |
| `422` | Validation error (includes field-level details) |
| `429` | Rate limit exceeded |
| `500` | Internal server error |

Validation errors include a `field` key:

```json
{
  "errors": [
    {"field": "character_class", "message": "Not a valid class."},
    {"field": "level", "message": "Must be between 1 and 100."}
  ]
}
```
