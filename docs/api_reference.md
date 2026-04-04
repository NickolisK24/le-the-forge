# The Forge — API Reference

All endpoints are prefixed with `/api`. All responses are JSON.

---

## Authentication

The Forge uses Discord OAuth 2.0. Protected endpoints require a JWT bearer token:

```
Authorization: Bearer <token>
```

### `GET /api/auth/discord`
Redirects the browser to Discord's OAuth consent page.

### `GET /api/auth/discord/authorized`
OAuth callback. Exchanges the Discord code for a token, creates/updates the user, and redirects to the frontend with `?token=<jwt>`.

**Error redirects:** `?auth=failed&reason=<reason>`
- `discord_unreachable` — could not reach Discord
- `discord_timeout` — Discord timed out
- `token_exchange` — token exchange failed
- `profile_fetch` — could not fetch Discord profile
- `no_code` — authorization cancelled

### `GET /api/auth/me`
Returns the current authenticated user.

**Requires auth.** Returns `401` if token is missing or expired.

```json
{
  "data": {
    "id": "uuid",
    "username": "Player#1234",
    "avatar_url": "https://cdn.discordapp.com/...",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

### `POST /api/auth/logout`
Clears the server-side session (stateless JWT — client should discard the token).

```json
{ "message": "logged out" }
```

### `GET /api/auth/dev-login` *(dev only)*
Bypasses Discord and returns a JWT for a local test user. Only available when `FLASK_ENV=development`.

---

## Builds

### `GET /api/builds`
List community builds with filtering and pagination.

**Query parameters:**

| Param | Type | Description |
|---|---|---|
| `q` | string | Search builds by name/description |
| `character_class` | string | Filter by class |
| `mastery` | string | Filter by mastery |
| `tier` | string | Filter by tier (`S`, `A`, `B`, `C`) |
| `is_ssf` | bool | SSF builds only |
| `is_hc` | bool | Hardcore builds only |
| `is_ladder_viable` | bool | Ladder-viable only |
| `is_budget` | bool | Budget builds only |
| `sort` | string | `votes` (default), `new`, `tier`, `views` |
| `page` | int | Page number (default: 1) |
| `per_page` | int | Results per page (default: 20, max: 100) |

```json
{
  "data": [
    {
      "id": "uuid",
      "slug": "wraithlord-7xk3",
      "name": "Wraithlord One-Shot",
      "description": "Fastest T4 clear...",
      "character_class": "Acolyte",
      "mastery": "Lich",
      "level": 100,
      "tier": "S",
      "vote_count": 142,
      "view_count": 3201,
      "is_ssf": false,
      "is_hc": false,
      "is_ladder_viable": true,
      "is_budget": false,
      "author": { "username": "Ghostblade" },
      "created_at": "2025-06-01T12:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "pages": 5,
    "total": 94,
    "per_page": 20,
    "has_next": true,
    "has_prev": false
  }
}
```

### `GET /api/builds/meta/snapshot`
Aggregate stats about all public builds (class distribution, tier counts).

```json
{
  "data": {
    "total": 94,
    "by_class": { "Acolyte": 23, "Mage": 18, ... },
    "by_tier": { "S": 5, "A": 21, "B": 38, "C": 30 }
  }
}
```

### `POST /api/builds`
Create a new build. Rate limited: 20/min.

**Request body:**

```json
{
  "name": "Wraithlord One-Shot",
  "description": "Fastest T4 clear in patch 1.2",
  "character_class": "Acolyte",
  "mastery": "Lich",
  "level": 100,
  "passive_tree": [0, 1, 3, 7, 12],
  "skills": [
    { "slot": 0, "skill_name": "Transplant", "points_allocated": 20, "spec_tree": [1, 2, 5] }
  ],
  "gear": [
    { "slot": "head", "item_name": "Drowned Wraith", "rarity": "Exalted",
      "affixes": [{ "name": "% Increased Health", "tier": 5 }] }
  ],
  "is_ssf": false,
  "is_hc": false,
  "is_ladder_viable": true,
  "is_budget": false,
  "patch_version": "1.2",
  "cycle": "Cycle of the Tides"
}
```

**Response:** `201 Created`

```json
{
  "data": { "slug": "wraithlord-7xk3", ...full build object }
}
```

### `GET /api/builds/<slug>`
Get a single build by slug. Increments `view_count`.

```json
{
  "data": {
    "id": "uuid",
    "slug": "wraithlord-7xk3",
    "name": "Wraithlord One-Shot",
    "character_class": "Acolyte",
    "mastery": "Lich",
    "level": 100,
    "passive_tree": [0, 1, 3, 7, 12],
    "gear": [...],
    "skills": [
      { "id": "uuid", "slot": 0, "skill_name": "Transplant", "points_allocated": 20, "spec_tree": [...] }
    ],
    "is_ssf": false,
    "is_hc": false,
    "is_ladder_viable": true,
    "is_budget": false,
    "tier": "S",
    "vote_count": 142,
    "view_count": 3202,
    "user_vote": null,
    "author": { "id": "uuid", "username": "Ghostblade" },
    "patch_version": "1.2",
    "cycle": "Cycle of the Tides",
    "created_at": "2025-06-01T12:00:00Z",
    "updated_at": "2025-06-01T14:00:00Z"
  }
}
```

### `PATCH /api/builds/<slug>`
Update a build. **Requires auth.** Only the build author can update.

**Request body:** any subset of the `POST /api/builds` fields.

**Response:** `200 OK` with updated build object.

### `DELETE /api/builds/<slug>`
Delete a build. **Requires auth.** Only the build author can delete.

**Response:** `204 No Content`

### `POST /api/builds/<slug>/simulate`
Run a quick simulation for this saved build. Rate limited: 10/min.

**Request body (optional):**

```json
{ "seed": 42 }
```

**Response:**

```json
{
  "data": {
    "dps": 148200.5,
    "average_hit": 24700.1,
    "crit_chance": 0.72,
    "effective_attack_speed": 6.0,
    "ehp": 185000,
    "survivability_score": 0.81
  }
}
```

### `POST /api/builds/<slug>/vote`
Vote on a build. **Requires auth.** Rate limited: 30/min.

**Request body:**

```json
{ "direction": 1 }
```

`direction`: `1` (upvote) or `-1` (downvote). Sending the same direction again toggles the vote off.

**Response:**

```json
{
  "data": {
    "vote_count": 143,
    "user_vote": 1,
    "tier": "S"
  }
}
```

---

## Craft Sessions

### `POST /api/craft`
Create a new crafting session.

**Request body:**

```json
{
  "item_type": "Wand",
  "item_name": "Driftwood Wand",
  "item_level": 85,
  "rarity": "Rare",
  "forge_potential": 40,
  "affixes": [
    { "name": "% Increased Spell Damage", "tier": 3, "sealed": false }
  ]
}
```

**Response:** `201 Created`

```json
{
  "data": {
    "id": "uuid",
    "slug": "craft-9xp2",
    "item_type": "Wand",
    "item_name": "Driftwood Wand",
    "item_level": 85,
    "rarity": "Rare",
    "forge_potential": 40,
    "affixes": [...],
    "steps": [],
    "created_at": "2025-06-01T12:00:00Z"
  }
}
```

### `GET /api/craft/<slug>`
Get a craft session by slug.

### `DELETE /api/craft/<slug>`
Delete a craft session. **Requires auth** if the session belongs to a user.

### `POST /api/craft/<slug>/action`
Apply a crafting action to an active session.

**Request body:**

```json
{
  "action": "upgrade_affix",
  "affix_name": "% Increased Spell Damage",
  "seed": 42
}
```

`action` values: `add_affix`, `upgrade_affix`, `seal_affix`, `unseal_affix`, `remove_affix`

**Response:**

```json
{
  "data": {
    "step": {
      "step_number": 1,
      "action": "upgrade_affix",
      "affix_name": "% Increased Spell Damage",
      "tier_before": 3,
      "tier_after": 4,
      "roll": 72,
      "outcome": "success",
      "fp_before": 40,
      "fp_after": 35
    },
    "session": { ...updated session }
  }
}
```

### `POST /api/craft/<slug>/undo`
Undo the last crafting action.

### `GET /api/craft/<slug>/summary`
Get a summary and simulation results for a craft session.

```json
{
  "data": {
    "item_type": "Wand",
    "rarity": "Rare",
    "affixes": [...],
    "fp_remaining": 35,
    "optimal_path": {
      "steps": ["upgrade_affix: % Increased Spell Damage → T5", "seal_affix"],
      "total_fp_cost": 25,
      "expected_fp_needed": 28.4
    },
    "simulation": {
      "runs": 3000,
      "success_rate": 0.68,
      "expected_fp_used": 27.1
    }
  }
}
```

### `POST /api/craft/predict`
Stateless FP cost prediction. No session required.

**Request body:**

```json
{
  "item_type": "Wand",
  "item_level": 85,
  "rarity": "Rare",
  "affixes": [
    { "name": "% Increased Spell Damage", "tier": 3, "sealed": false }
  ],
  "target_tiers": { "% Increased Spell Damage": 5 },
  "seed": null
}
```

**Response:**

```json
{
  "data": {
    "optimal_path": { "steps": [...], "total_fp_cost": 20 },
    "strategies": {
      "aggressive": { "fp_cost": 18, "success_rate": 0.55, "risk": "high" },
      "balanced":   { "fp_cost": 22, "success_rate": 0.71, "risk": "medium" },
      "conservative": { "fp_cost": 28, "success_rate": 0.85, "risk": "low" }
    }
  }
}
```

### `POST /api/craft/simulate`
Run a Monte Carlo simulation for a craft configuration. Rate limited: 10/min.

**Request body:**

```json
{
  "item_type": "Wand",
  "item_level": 85,
  "rarity": "Rare",
  "forge_potential": 40,
  "affixes": [{ "name": "% Increased Spell Damage", "tier": 3, "sealed": false }],
  "runs": 3000,
  "seed": 42
}
```

**Response:**

```json
{
  "data": {
    "runs": 3000,
    "success_rate": 0.68,
    "expected_fp_used": 27.1,
    "percentiles": { "p25": 22, "p50": 27, "p75": 33, "p90": 40 },
    "seed": 42
  }
}
```

---

## Simulation

### `POST /api/simulate/stats`
Compute aggregate stats for a build config.

**Request body:**

```json
{
  "character_class": "Acolyte",
  "mastery": "Lich",
  "level": 100,
  "passive_nodes": [0, 1, 3, 7],
  "gear": [
    { "slot": "head", "affixes": [{ "stat_key": "spell_damage_pct", "value": 50 }] }
  ],
  "skills": [{ "skill_name": "Transplant", "points_allocated": 20 }]
}
```

**Response:**

```json
{
  "data": {
    "stats": {
      "base_damage": 120,
      "crit_chance": 0.72,
      "crit_multiplier": 3.5,
      "spell_damage_pct": 280,
      "max_health": 2800,
      "armour": 1500,
      "void_res": 75,
      ...
    }
  }
}
```

### `POST /api/simulate/combat`
Simulate combat DPS against an enemy profile. Rate limited: 20/min.

**Request body:**

```json
{
  "character_class": "Acolyte",
  "mastery": "Lich",
  "level": 100,
  "passive_nodes": [0, 1, 3],
  "gear": [...],
  "skills": [...],
  "enemy_id": "boss_lagon",
  "skill_name": "Transplant",
  "runs": 1000,
  "seed": 42
}
```

**Response:**

```json
{
  "data": {
    "dps": 148200.5,
    "average_hit": 24700.1,
    "crit_contribution_pct": 0.62,
    "effective_attack_speed": 6.0,
    "hit_damage": 12350.0,
    "seed": 42
  }
}
```

### `POST /api/simulate/defense`
Compute defensive stats. Rate limited: 30/min.

**Request body:** Same structure as `/simulate/stats` + `enemy_id` (optional).

**Response:**

```json
{
  "data": {
    "ehp": 185000,
    "armor_reduction_pct": 0.60,
    "resistances": { "fire": 75, "cold": 58, "lightning": 75, "void": 42 },
    "survivability_score": 0.81,
    "weaknesses": ["cold", "void"],
    "strengths": ["fire", "lightning"]
  }
}
```

### `POST /api/simulate/optimize`
Get top stat upgrade recommendations. Rate limited: 10/min.

**Request body:** Same as `/simulate/stats`.

**Response:**

```json
{
  "data": {
    "top_upgrades": [
      { "stat": "crit_chance_pct", "label": "Critical Strike Chance", "dps_gain": 18400, "pct_gain": 0.124 },
      { "stat": "spell_damage_pct", "label": "Increased Spell Damage", "dps_gain": 14200, "pct_gain": 0.096 }
    ]
  }
}
```

### `POST /api/simulate/build`
Full build simulation — stats + combat + defense in one call. Rate limited: 10/min.

**Request body:**

```json
{
  "character_class": "Acolyte",
  "mastery": "Lich",
  "level": 100,
  "passive_nodes": [...],
  "gear": [...],
  "skills": [...],
  "enemy_id": "boss_lagon",
  "skill_name": "Transplant",
  "runs": 1000,
  "seed": 42
}
```

**Response:**

```json
{
  "data": {
    "stats": { ...aggregate stats },
    "combat": { ...dps breakdown },
    "defense": { ...ehp + resistances },
    "top_upgrades": [...],
    "seed": 42
  }
}
```

---

## Reference Data

These endpoints return static game data. All are cached indefinitely.

### `GET /api/ref/classes`
All character classes with masteries and available skills.

```json
{
  "data": {
    "Acolyte": {
      "color": "#9b59b6",
      "masteries": ["Lich", "Necromancer", "Warlock"],
      "skills": ["Transplant", "Marrow Shards", ...]
    },
    ...
  }
}
```

### `GET /api/ref/item-types`
All item type definitions.

```json
{
  "data": [
    { "name": "Wand", "category": "weapon", "base_implicit": "cast speed" },
    ...
  ]
}
```

### `GET /api/ref/affixes`
All affix definitions. Filterable.

**Query params:** `?type=prefix&slot=wand&class=Acolyte&tag=spell`

```json
{
  "data": [
    {
      "id": "spell-damage-prefix",
      "name": "% Increased Spell Damage",
      "type": "prefix",
      "stat_key": "spell_damage_pct",
      "applicable_to": ["wand", "staff", "sceptre"],
      "class_requirement": null,
      "tags": ["spell", "damage"],
      "tiers": [
        { "tier": 1, "min": 10, "max": 20 },
        { "tier": 5, "min": 60, "max": 90 }
      ]
    }
  ]
}
```

### `GET /api/ref/affixes/<affix_id>`
Single affix by ID.

### `GET /api/ref/skills`
All skill definitions. Filter by `?class=Acolyte`.

```json
{
  "data": [
    { "name": "Transplant", "class": "Acolyte", "tags": ["spell", "movement"], "icon": "transplant" }
  ]
}
```

### `GET /api/ref/passives`
Passive tree nodes. Filter by `?class=Acolyte&mastery=Lich`.

```json
{
  "data": [
    { "id": 0, "name": "Node 0", "type": "notable", "region": "base", "max_points": 8, "description": "..." }
  ]
}
```

### `GET /api/ref/crafting-rules`
FP cost ranges and crafting action rules.

### `GET /api/ref/base-items`
All base item definitions (base type, FP range, implicits).

### `GET /api/ref/base-items/<base_type>`
Single base item definition.

### `GET /api/ref/fp-ranges`
FP ranges by rarity tier.

### `GET /api/ref/fp-ranges/<rarity>`
FP range for a specific rarity. Optional `?ilvl=85` for item-level scaling.

```json
{ "data": { "rarity": "Exalted", "min_fp": 30, "max_fp": 60 } }
```

### `GET /api/ref/enemy-profiles`
All enemy profiles (normal, elite, bosses).

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

---

## Profile

### `GET /api/profile`
Get the current user's profile. **Requires auth.**

```json
{
  "data": {
    "user": { "id": "uuid", "username": "Ghostblade", "avatar_url": "...", "created_at": "..." },
    "stats": { "builds_count": 7, "sessions_count": 12 }
  }
}
```

### `GET /api/profile/builds`
Builds created by the current user. **Requires auth.**

**Query params:** `?page=1&per_page=10`

### `GET /api/profile/sessions`
Craft sessions owned by the current user. **Requires auth.**

**Query params:** `?page=1&per_page=10`

---

## Admin

> Admin endpoints are for managing game data files. These require a user with admin privileges.

### `GET /api/admin/affixes`
List all affixes from `data/affixes.json`.

**Query params:** `?q=spell&type=prefix&tag=damage&slot=wand`

### `PATCH /api/admin/affixes/<affix_id>`
Update a single affix in `data/affixes.json`.

**Request body (any subset):**

```json
{
  "name": "% Increased Spell Damage",
  "type": "prefix",
  "stat_key": "spell_damage_pct",
  "tags": ["spell", "damage"],
  "applicable_to": ["wand", "staff"],
  "class_requirement": null,
  "tiers": [{ "tier": 1, "min": 10, "max": 20 }, ...]
}
```

**Response:** `200 OK` with updated affix object.

---

## Error Responses

All errors follow this shape:

```json
{
  "errors": [
    { "message": "Build not found", "code": "not_found" }
  ]
}
```

| HTTP Status | Meaning |
|---|---|
| `400` | Bad request / validation error |
| `401` | Unauthorized (missing or expired token) |
| `403` | Forbidden (not the owner) |
| `404` | Resource not found |
| `429` | Rate limit exceeded |
| `500` | Internal server error |

### Validation errors

When request body validation fails, errors include a `field` key:

```json
{
  "errors": [
    { "field": "crit_chance", "message": "Must be between 0 and 1." },
    { "field": "level", "message": "Must be between 1 and 100." }
  ]
}
```
