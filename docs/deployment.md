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

1. Push `render.yaml` to the branch Render tracks.
2. In the Render dashboard: **New → Blueprint → Connect repo**. Render will
   create `epochforge-api` and `epochforge-frontend` from the blueprint.
3. Provision **Render Postgres** and **Render Redis** from the dashboard.
4. Open `epochforge-api → Environment` and paste the required secrets
   (values should come from the new Postgres / Redis / your Discord app):

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

Cloudflare → **SSL/TLS → Overview**: set mode to **Full** (not Strict — Render
already serves valid certs on `*.onrender.com` but the custom-domain cert
is provisioned asynchronously; Full is safest during the initial cut-over).
Revisit and move to **Full (strict)** once Render finishes provisioning.

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

## 5. Verifying the cut-over

```bash
# API health
curl -sSf https://api.epochforge.gg/api/health | jq
# → { "status": "ok", "version": "0.8.0", "patch_version": "1.4.3", "uptime_seconds": 12 }

# Frontend
curl -sSfI https://epochforge.gg | head -1
# → HTTP/2 200

# SPA fallback (must also return index.html)
curl -sSfI https://epochforge.gg/builds/some-slug | head -1
# → HTTP/2 200
```

CORS: use an incognito window and confirm the app can authenticate via Discord
without console errors. Only `https://epochforge.gg` and
`https://www.epochforge.gg` are accepted as origins in production.
