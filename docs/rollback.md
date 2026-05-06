# Rollback & Incident Response

When something breaks in production, pick the smallest action that fixes it.
Rolling back a deploy is cheap; restoring a database is expensive and
irreversible to the backup point; bypassing CORS briefly is ugly but safe
if and only if it's narrow.

---

## 1. Rolling back to a previous deploy

Render keeps every successful build's artifact around. Rolling back reverts
the service to that artifact without touching code or the database.

1. Render dashboard → `epochforge-api` (or `epochforge-frontend`) → **Events**.
2. Find the last known-good deploy (green "Deployed" event, before the
   regression landed).
3. Click **Rollback** next to that event. Render redeploys the cached artifact
   in under 30 seconds — no rebuild, no migration.
4. Verify:
   ```bash
   curl -sSf https://api.epochforge.gg/api/health | jq .version
   curl -sSfI https://epochforge.gg | head -1
   ```
5. Open a revert PR against `main` for the offending commit so the repo
   and the running service stay in sync. Don't leave the branch behind —
   the next successful push to `main` will redeploy the broken version.

### If a migration ran before the bug surfaced

Rolling back the service reverts code only. If the last deploy ran
`flask db upgrade` and the new schema is incompatible with the previous
release, you need a **down-migration** too:

```bash
# In Render → epochforge-api → Shell
flask db downgrade -1
```

Check `backend/migrations/versions/` first — some migrations have empty
`downgrade()` functions (data-only migrations, drops of recreated columns)
and can't be safely reversed. In that case, a Postgres point-in-time
restore (next section) is the only option.

---

## 2. Restoring the database from a Render backup

Render's Starter Postgres plan automatically takes a daily snapshot and
retains it for 7 days.

1. Render dashboard → `epochforge-db` → **Backups**.
2. Pick the most recent backup taken **before** the incident. Note the
   timestamp — data written after that point will be lost.
3. Click **Restore**. Render creates a new Postgres instance from the
   backup (it does **not** overwrite the live one).
4. Copy the new instance's internal connection string.
5. In `epochforge-api` → Environment, point `DATABASE_URL` at the new
   instance. Click **Save and Deploy**.
6. Smoke test:
   ```bash
   curl -sSf https://api.epochforge.gg/api/health | jq
   curl -sSf https://api.epochforge.gg/api/version | jq
   ```
7. Once the restored instance is proven, archive the old one: rename it
   (e.g. `epochforge-db-pre-incident-YYYYMMDD`) rather than deleting it —
   keep it around for at least a week in case you need to pull data from
   the lost window.

> **Before clicking Restore**, take a manual snapshot of the *current*
> database via `pg_dump` (Shell → `pg_dump $DATABASE_URL > /tmp/pre-restore.sql`),
> download it, and stash it somewhere safe. It is the only thing standing
> between you and total data loss if the backup turns out to be corrupt.

---

## 3. Emergency CORS bypass

Symptoms: frontend console floods with
`Access to fetch at 'https://api.epochforge.gg/...' from origin
'https://epochforge.gg' has been blocked by CORS policy`, and every
data fetch fails. Root cause: a bad deploy wrote the wrong origins into
`ProductionConfig.CORS_ORIGINS` (or missed `www.epochforge.gg`, or a new
Cloudflare Workers subdomain isn't on the allowlist).

### Fastest fix (Render-only, 2 minutes)

1. Render → `epochforge-api` → **Environment** → add:
   ```
   CORS_EMERGENCY_ORIGIN = https://epochforge.gg
   ```
   and — if the login flow is also broken —
   ```
   CORS_EMERGENCY_ORIGIN_WWW = https://www.epochforge.gg
   ```
2. Edit `backend/app/__init__.py` locally on a hotfix branch to read those
   env vars and append them to `cors_origins`. Deploy the hotfix.
3. Once the real fix lands on `main`, remove the emergency env vars and
   redeploy. They should not live in production more than one day.

### Slower but safer fix (redeploy the last good image)

Use the rollback procedure in §1. If the previous deploy had working
CORS, this is a one-click revert that also rolls back whatever other
change introduced the regression.

### Do NOT do this

Don't set `CORS(app, origins="*")` or `supports_credentials=False` in
production to "unbreak" the app. `*` + credentials is invalid under the
CORS spec; browsers will still refuse. Dropping credentials will log every
user out and can't be reversed without a redeploy.

---

## 4. Incident postmortem checklist

After service is restored:

- [ ] Open a GitHub issue titled `postmortem: <date> <one-line summary>`.
- [ ] Record: timeline (first alert → detection → mitigation → resolution),
      blast radius (users affected, requests failed), root cause, and the
      `git log` range of commits involved.
- [ ] File follow-up issues for anything that made the incident slower or
      worse: missing alerts, confusing error messages, undocumented
      runbook steps.
- [ ] Remove any emergency env vars or temporary allowlist entries.
- [ ] If a downgrade migration was used, verify `alembic_version` in the
      DB matches the running code: `flask db current`.
