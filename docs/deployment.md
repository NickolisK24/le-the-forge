# Production Deployment — Render + Cloudflare

This guide walks through the one-time infrastructure setup for deploying The
Forge to production at https://epochforge.gg. It assumes the Render Blueprint
(`render.yaml`) is already committed at the repo root.

---

## Architecture

```
┌──────────────────────┐      ┌──────────────────────┐
│  Cloudflare (DNS)    │      │  Render              │
│  epochforge.gg       │ ───▶ │  epochforge-frontend │  static Vite build
│  www.epochforge.gg   │ ───▶ │  epochforge-frontend │
│  api.epochforge.gg   │ ───▶ │  epochforge-api      │  Flask + Gunicorn
└──────────────────────┘      └──────────────────────┘
                                        │
                                        ▼
                              ┌──────────────────────┐
                              │  Postgres + Redis    │  Render-managed
                              └──────────────────────┘
```

---

## 1. Create the Render services

The Blueprint in `render.yaml` creates all four services in the correct
order (databases first, then API, then frontend). If you are doing this
manually instead of via Blueprint, follow the same order:

1. **`epochforge-db`** (Postgres, Starter plan) — nothing depends on it yet,
   but the API needs its connection string before it can boot.
2. **`epochforge-redis`** (Redis / Key Value, Starter plan) — same reason.
3. **`epochforge-api`** (Python web service) — wires `DATABASE_URL` and
   `REDIS_URL` from the two services above via `fromDatabase` / `fromService`.
4. **`epochforge-frontend`** (static site) — only needs `VITE_API_BASE_URL`
   pointed at the API's custom domain.

### Blueprint flow

1. Push `render.yaml` to the branch Render tracks.
2. In the Render dashboard: **New → Blueprint → Connect repo**. Render will
   provision all four services in one pass.
3. Open `epochforge-api → Environment` and paste the required secrets
   (values should come from your Discord app + `secrets.token_hex(32)`):

   | Variable                     | Source                                       |
   | ---------------------------- | -------------------------------------------- |
   | `DATABASE_URL`               | Render Postgres → Internal connection string |
   | `REDIS_URL`                  | Render Redis → Internal connection string    |
   | `SECRET_KEY`                 | `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `JWT_SECRET_KEY`             | `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `DISCORD_CLIENT_ID`          | Discord developer portal                     |
   | `DISCORD_CLIENT_SECRET`      | Discord developer portal                     |
   | `DISCORD_REDIRECT_URI`       | `https://api.epochforge.gg/api/auth/discord/authorized` |
   | `DISCORD_IMPORT_WEBHOOK_URL` | Discord channel → Integrations → Webhooks (optional) |

   The following are set by the blueprint itself and should not be edited:
   `FLASK_ENV`, `FLASK_APP`, `PYTHON_VERSION`, `FRONTEND_URL`.

5. Click **Manual Deploy** on `epochforge-api` once the env vars are saved.
   The preDeployCommand (`flask db upgrade`) will run the migrations; the
   service will fail to boot if `SECRET_KEY` / `JWT_SECRET_KEY` are still
   dev defaults (enforced by `ProductionConfig.validate()`).

6. On `epochforge-frontend`, confirm `VITE_API_BASE_URL=https://api.epochforge.gg`
   is set, then **Manual Deploy**.

---

## 2. Configure custom domains in Render

On each service: **Settings → Custom Domains → Add**.

| Service              | Domains                                   |
| -------------------- | ----------------------------------------- |
| `epochforge-api`     | `api.epochforge.gg`                       |
| `epochforge-frontend`| `epochforge.gg`, `www.epochforge.gg`      |

Render will show a CNAME target like `<service>.onrender.com` — use this in
the next step when wiring Cloudflare.

Because Cloudflare terminates TLS at the edge, set each custom domain to
**HTTP only** in Render (uncheck "Redirect HTTP to HTTPS"). Cloudflare will
redirect to HTTPS before the request ever hits Render.

---

## 3. Configure Cloudflare DNS

Log into Cloudflare → `epochforge.gg` → **DNS → Records**.

Create three records:

| Type    | Name  | Target                                 | Proxy    |
| ------- | ----- | -------------------------------------- | -------- |
| `CNAME` | `@`   | `epochforge-frontend.onrender.com`     | Proxied  |
| `CNAME` | `www` | `epochforge-frontend.onrender.com`     | Proxied  |
| `CNAME` | `api` | `epochforge-api.onrender.com`          | Proxied  |

> Cloudflare automatically "flattens" the apex (`@`) CNAME, so there is no
> need to manage A records manually. If your plan disallows CNAME flattening,
> use the Render-provided anycast A records instead.

### SSL / TLS

Cloudflare → **SSL/TLS → Overview**: set mode to **Full** — *not*
**Full (strict)**. Full trusts Render's auto-provisioned cert even while it's
still being issued for the custom domain; Full (strict) will return 526
errors for the first few hours of the cut-over while the cert propagates.
You can revisit Full (strict) a week after launch if you want the extra
hardening, but Full is the correct default here.

Cloudflare → **SSL/TLS → Edge Certificates**: enable **Always Use HTTPS** and
**Automatic HTTPS Rewrites**.

---

## 4. Configure GitHub Actions deploys

1. Render dashboard → `epochforge-api` → **Settings → Deploy Hook** → copy URL.
2. GitHub → repo → **Settings → Secrets and variables → Actions → New**:
   - Name: `RENDER_DEPLOY_HOOK_URL`
   - Value: the URL from step 1.
3. Pushes to `main` now trigger `.github/workflows/deploy.yml`, which POSTs
   to the deploy hook. If you want deploys for both services, repeat the
   process and chain two curl calls in the workflow.

---

## 5. Smoke test checklist

Run each of these after the initial deploy and after every non-trivial
release. Anything that returns non-200 or an unexpected body is a launch
blocker.

### Backend

```bash
# 1. Health check — must return status:ok with a small uptime after a deploy
curl -sSf https://api.epochforge.gg/api/health | jq
# → { "status": "ok", "version": "0.8.0", "patch_version": "1.4.3", "uptime_seconds": 12 }

# 2. Version endpoint — commit should match the latest green main
curl -sSf https://api.epochforge.gg/api/version | jq

# 3. CORS preflight — must echo only allowed origins
curl -sSI -X OPTIONS https://api.epochforge.gg/api/health \
  -H "Origin: https://epochforge.gg" \
  -H "Access-Control-Request-Method: GET" \
  | grep -i access-control-allow-origin
# → access-control-allow-origin: https://epochforge.gg

# 4. CORS block on unknown origin — must NOT return an allow-origin header
curl -sSI -X OPTIONS https://api.epochforge.gg/api/health \
  -H "Origin: https://evil.example.com" \
  -H "Access-Control-Request-Method: GET" \
  | grep -i access-control-allow-origin || echo "blocked (correct)"

# 5. Rate limit — 61st request within a minute must 429
for i in $(seq 1 62); do
  curl -s -o /dev/null -w "%{http_code}\n" https://api.epochforge.gg/api/health
done | tail -5
# → … 200 200 429
```

### Frontend

```bash
# 6. Root must return index.html (HTTP 200 + html content-type)
curl -sSfI https://epochforge.gg | head -1

# 7. SPA fallback — any client-side route must also return index.html
curl -sSfI https://epochforge.gg/builds/some-slug | head -1

# 8. Assets cached aggressively
curl -sSI https://epochforge.gg/assets/index-<hash>.js | grep -i cache-control
# → cache-control: public, max-age=31536000, immutable
```

### End-to-end

- Open https://epochforge.gg in an incognito window. Network tab should
  show every `fetch` going to `https://api.epochforge.gg/...`, not
  `localhost` or a relative `/api/...`.
- Sign in with Discord. The redirect should land back on
  `https://epochforge.gg` with a valid session (no `?auth=failed` query).
- Load `/debug/backend` and confirm every endpoint reports a green 200.
