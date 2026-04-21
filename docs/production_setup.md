# Production Setup — One-Off Database Jobs

After the Render services in `docs/deployment.md` are running, the Postgres
instance is empty. Follow the steps below to apply schema migrations, seed
reference data, and verify the deployment.

All commands run as Render **one-off jobs** — open a service and click
**Shell** (or **Jobs → New Job**). The `flask` CLI is already on the
path because `wsgi.py` + `FLASK_APP=wsgi.py` are set by `render.yaml`.

---

## 1. Apply database migrations

The blueprint's `preDeployCommand` runs `flask db upgrade` on every deploy,
so this step is usually automatic. To force it manually (for example after
adding a new migration without redeploying):

```bash
# On epochforge-api → Shell
flask db upgrade
```

Expected output ends with `-> <latest revision>, <description>`.

---

## 2. Seed reference data

The seed commands are idempotent — they skip rows that already exist, so
running them twice is safe.

```bash
# Item types + affix definitions from data/items/affixes.json
flask seed

# Passive tree nodes from data/classes/passives.json
flask seed-passives

# (Optional) Three demo builds. Only run in staging — the live site starts
# empty on purpose so the Community page reflects real user submissions.
flask seed-builds
```

Run these once, during initial provisioning.

---

## 3. Verify the deploy

### Health check

Render uses `/api/health` as its health check. Probe it directly to confirm
the app booted and the deploy is live:

```bash
curl -sSf https://api.epochforge.gg/api/health | jq
```

Expected:

```json
{
  "status": "ok",
  "version": "0.8.0",
  "patch_version": "1.4.3",
  "uptime_seconds": 42
}
```

`uptime_seconds` should reset to a small number after each deploy — that
confirms the new build is actually running.

### Version endpoint

```bash
curl -sSf https://api.epochforge.gg/api/version | jq
```

Should return the same `version` string and a matching `commit` SHA.

### Database sanity

```bash
# On epochforge-api → Shell
flask shell -c "from app.models import Build, AffixDef; print(Build.query.count(), AffixDef.query.count())"
```

`AffixDef` count should be non-zero after `flask seed`.

### Frontend

Open https://epochforge.gg in an incognito window. Check the network tab:
every `fetch` should go to `https://api.epochforge.gg/api/...` (not
`localhost` or a relative `/api/...`). A 200 on `/api/version` is a good
smoke test that CORS and routing are working end-to-end.

---

## 4. Operational notes

- **Rate-limit store**: `REDIS_URL` must be set. The app falls back to
  in-memory rate limiting if Redis is unreachable, which breaks the limiter
  across Gunicorn workers — fine for smoke tests, not for production.
- **Discord OAuth**: `DISCORD_REDIRECT_URI` in Render **and** the Discord
  developer portal must exactly match
  `https://api.epochforge.gg/api/auth/discord/authorized`.
- **`flask validate-data`** is run in CI but can also be invoked from the
  Render shell when debugging — it exits non-zero on any malformed JSON in
  `/data`.
