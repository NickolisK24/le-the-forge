# 15 — Observability and Operations Audit

Audit date: 2026-10-06. Scope: `le-the-forge` `main` @ `1efcef7` (deployed), with `dev` @ `558557c` checked where noted. Read-only.

## 1. Headline

The only operational signal is a Discord embed that fires per failed import. It has no app version, no upstream response metadata, no build/commit, no dedupe or aggregation, and no way to replay the failure. `/api/health` is a liveness probe that touches neither the DB, Redis nor game-data freshness. There is no error tracker (Sentry or similar), no metrics, no uptime monitor in the repo, no retry queue and no dead-letter store beyond the `import_failures` table. The only way to read that table is an admin JSON endpoint that has no UI.

Live check: `https://api.epochforge.gg/api/health` and `https://epochforge.gg` could **not** be reached. The sandbox egress proxy refused the CONNECT (`curl: (56) CONNECT tunnel failed, response 403`; WebFetch: `EGRESS_BLOCKED`). This is a **proxy** refusal, not the site's response. Live production state is **UNKNOWN**.

## 2. Inventory

| Capability | Present? | Evidence |
|---|---|---|
| Structured logging | Partial | `backend/app/utils/logging.py:28-41` JsonFormatter; `ProductionConfig.LOG_FORMAT_JSON = True` (`config.py:86`). `ForgeLogger` is used in 42 app modules; the rest use plain `logging` with %-format strings, so their fields are not structured. |
| Request IDs / correlation | **No** | `grep -rn "request_id\|X-Request-ID\|correlation" backend/app` → 0 hits |
| Slow-request logging | Yes | `app/__init__.py:163-175`: logs a warning above 500 ms and sets the `X-Response-Time` header |
| Unhandled-exception logging | Yes | `app/__init__.py:260-264` (`logger.exception`, then a generic 500) |
| Error tracking (Sentry etc.) | **No** | not in `backend/requirements.txt` or `frontend/package.json`; grep for sentry/datadog/prometheus/statsd → 0 |
| Metrics | **No** (ops) | `backend/metrics/` holds simulation metrics, not service metrics |
| Product analytics | **No** | no gtag/plausible/posthog in `frontend/src` or `index.html` |
| Health check | Liveness only | `backend/app/routes/health.py:49-58` returns `status/version/patch_version/uptime_seconds`. **No DB ping, no Redis ping, no data-load status.** It always returns 200. |
| Version endpoint | Yes | `app/routes/version.py:58-67`. `commit` comes from `git rev-parse` at request time and is null when `.git` is absent at runtime (Render runtime: **UNKNOWN**) |
| Data freshness signal | Broken | `data/version.json` has `"patch_version": "unknown"` (synced 2026-04-26), so health reports `patch_version: "unknown"`. `CURRENT_PATCH` defaults to `1.4.3` (`config.py:28`), and test fixtures reference `game_version: "1.4.6"`. That gives three different "versions". |
| Import failure persistence | Yes | `ImportFailure` model (`app/models/__init__.py:330-345`): source, raw_url, missing_fields, partial_data, user_id, error_message (≤1024 chars), timestamps |
| Import failure UI | **No** | `GET /api/admin/import-failures` (`app/routes/admin.py:96-`; `login_required` + `is_admin`). No frontend consumer (`grep import-failures frontend/src` → 0) |
| Discord alert | Yes | `app/services/discord_notifier.py` (see §3) |
| Retry queue / dead-letter | **No** | Failed imports are recorded and nothing re-tries them |
| Job history | Ephemeral | `app/utils/jobs.py:25-34`: in-process `ThreadPoolExecutor(max_workers=4)` per gunicorn worker, state in Redis with a 1 h TTL. Errors are swallowed (`except Exception: pass`, lines 65-66, 79-80). Jobs are lost on restart or deploy. |
| Scheduler / cron | **No** | No Render cron in `render.yaml` and no APScheduler/Celery |
| Extractor health | **No runtime signal** | Upstream `last-epoch-data` CI has been red since 2026-05-29 (report 14). Nothing in the app surfaces upstream bundle age or version. |
| Upstream dependency health (LET, Maxroll) | **No** | Only visible indirectly through per-failure alerts |
| Dashboards | **No** | `docs/migration/V2_5_PRE_V3_MECHANICAL_READINESS_DASHBOARD.md` is a doc. `frontend/src/pages/debug/BackendDebugDashboard.tsx` is a dev page. |
| Uptime monitor | **UNKNOWN** | Nothing configured in the repo, and `docs/rollback.md` mentions "first alert" without naming a monitor |
| Incident runbook | Yes | `docs/rollback.md` (129 lines) |
| Committed stray log | — | `backend/error_log.txt` is tracked (2026-04-12) and contains a Windows venv path error. It is noise, not a log sink. |

## 3. The Discord import alert: forensic review

Code path: `POST /api/import/build` → `_do_import` → `LastEpochToolsImporter.parse` (`lastepochtools_importer.py:693-727`) catches `HTTPError` and returns `ImportResult(success=False, error_message="Last Epoch Tools returned HTTP {status}.")`. `import_route.py:568-580` then calls `_record_and_alert`, which runs `ImportFailure(...)`, `commit` and `send_import_failure_alert` (`import_route.py:281-298`). The notifier then sends a daemon-thread POST (`discord_notifier.py:59-65, 109-182`).

The observed alert ("Source: lastepochtools; URL: …/planner/B5P5P8M3; Missing Fields: None; Parsed Data: No data parsed; Error: Last Epoch Tools returned HTTP 403", twice) maps exactly to `discord_notifier.py:116-133`.

### What the alert can and cannot answer

| Question | Answerable from alert? | Why / missing field |
|---|---|---|
| WHAT failed | Partly | The HTTP status is shown, but "Missing Fields: None" is misleading for a fetch failure. No failure class is attached (fetch/parse/map/save). |
| WHERE (which build) | Yes | raw_url |
| WHY (upstream reason) | **No** | No response headers (`server`, `cf-ray`, `cf-mitigated`), body snippet, or egress IP. A Cloudflare challenge cannot be told apart from an auth wall or a removed build. |
| Upstream version / page format | **No** | Not captured |
| App version / commit | **No** | Not in the embed; `__version__` and the commit are not attached |
| Extractor / data bundle version | **No** | Not attached (and `patch_version` is "unknown") |
| Build source (LET / Maxroll) | Yes | source |
| Isolated vs systemic | **No** | No counter, rate or "N failures in last hour" field, and no dedupe. The "twice" event produced two identical embeds. |
| Replayable | **No** | The fetched HTML is never stored on failure. `partial_data` is null for a fetch failure. |
| Which user | Partly | user_id or "anonymous" |
| Request correlation | **No** | No request ID |
| Severity routing | Minimal | Only red/orange by "hard"/"partial" |

### Reliability gaps in the alert path

1. If the DB `commit` fails, the alert is **not** sent, because both are inside the same `try` (`import_route.py:286-299`). An outage of the DB hides import failures too.
2. `WEBHOOK_URL` is read once at import time (`discord_notifier.py:18`), so rotating it requires a restart.
3. Each failure starts an unbounded daemon thread with no rate limit. A systemic upstream block (such as the 403) produces one Discord message per user attempt and can hit Discord webhook rate limits (HTTP 429). That outcome is logged only as `discord_notifier: webhook returned 429`.
4. Discord failures are logged only as text, with no counter.
5. The prose error string is persisted (≤1024 chars). The status code is not stored as a field, so `import_failures` cannot be aggregated by cause without parsing strings.

## 4. Health-check depth

`/api/health` returns 200 whenever the process is up. It does not detect:
- DB unreachable (only `pool_pre_ping` per request)
- Redis unreachable. At boot, `_init_limiter` silently falls back to per-process in-memory rate limiting (`app/__init__.py:31-45`), which multiplies the effective limits by the worker count with no signal.
- Game data failed or partial load (the pipeline loads at `create_app` and a hard failure crashes boot, but a degraded load is not reported)
- Upstream import sources blocked

## 5. Recommended minimum ops contract (for the remediation phase; no changes made)

- Add `app_version`, `commit`, `data_version`/bundle hash, `upstream_status`, selected `upstream_headers` (server, cf-ray, cf-mitigated) and a `failure_stage` enum to `ImportFailure` and the embed.
- Store a capped snippet of the upstream response (for example the first 2 KB) so failures can be replayed.
- Aggregate: dedupe by (source, status) per N minutes and emit "X failures / Y attempts in last hour".
- Readiness endpoint: DB `SELECT 1`, Redis ping, data loaded with counts and version. Keep `/api/health` as liveness.
- Add an error tracker and an external uptime monitor on both domains.

## 6. Commands used

```
grep -rn "DISCORD_IMPORT_WEBHOOK_URL\|ImportFailure\|import_failure" backend --include=*.py
sed -n 1,182p backend/app/services/discord_notifier.py
sed -n 270,320p,500-620p backend/app/routes/import_route.py
sed -n 680,740p backend/app/services/importers/lastepochtools_importer.py
grep -rn "sentry|prometheus|statsd|datadog|posthog|plausible|gtag" -i backend frontend/src
grep -rln ForgeLogger backend/app | wc -l          # 42
curl -sS -D - https://api.epochforge.gg/api/health  # proxy 403 (CONNECT refused)
cat data/version.json
```

## 7. UNKNOWNs

- Live `/api/health` and `/api/version` responses (egress blocked).
- Render-side alerting, log retention and metrics configuration (dashboard-only settings).
- Whether an external uptime monitor exists.
- Volume of rows in `import_failures` in production.

## 8. What this does NOT prove

- It does not prove that production is unhealthy. It shows that nothing in the repo would tell anyone if it were.
- It does not identify the root cause of the LET 403. It shows that the alert lacks the fields needed to determine it. Datacenter-IP or anti-automation blocking is a hypothesis only.
