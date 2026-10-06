# 08 — Last Epoch Tools Import Forensics (Phase 6)

Audit date: 2026-10-06
Repo HEAD: `1efcef7` (shallow clone, 266 commits visible)
Scope: audit only. No code changed.

## 1. Incident

Discord import alert received twice for an anonymous user:

```
Source:         lastepochtools
URL:            https://www.lastepochtools.com/planner/B5P5P8M3
Missing Fields: None
Parsed Data:    No data parsed
Error:          Last Epoch Tools returned HTTP 403
```

## 2. Verdict (short)

| Question | Answer | Confidence |
|---|---|---|
| Which code path produced the alert? | `POST /api/import/build` → `LastEpochToolsImporter.parse()` → `HTTPError` branch → `_record_and_alert` | High (reproduced byte-for-byte locally with mocked 403) |
| Is the fetch broken? | Yes, in production: the server-side GET of the planner page received HTTP 403. The repo itself already states server-side fetching of LE Tools no longer works ("LET migrated to client-side rendering"), and the UI labels the path "Temporarily Unavailable" — yet one entry point still calls it. | High that it fails; origin of the 403 UNKNOWN (see §6) |
| Is the parser broken? | Not provable against live data. All LE Tools fixtures in the repo are synthetic ("not captured from live LET"). The code's own comments assert that `window.buildInfo` is no longer present in server HTML, which would make the HTML parser fail with 422 even if the fetch returned 200. The JSON mapper (bookmarklet path) has demonstrable mapping defects independent of the fetch (§9). | Medium |
| Is the alert accurate? | Partly. `Missing Fields: None` and `Parsed Data: No data parsed` are technically true but non-diagnostic: no status-code metadata, response headers, body markers, or `partial_data` are captured. The importer's own `partial_data` is discarded on hard failure. | High |
| Was this 403 from the audit container's proxy? | No. Production runs on Render and does not use this container's egress proxy. The local proxy did block all audit attempts to reach lastepochtools.com (see §6), so live behaviour could not be observed from here. | High |

## 3. End-to-end trace

### 3.1 Entry points (three backend routes, one frontend modal)

| Route | File:line | Fetches LE Tools? | Saves build? | Alerts on 403? | Used by UI? |
|---|---|---|---|---|---|
| `POST /api/import/build` | `backend/app/routes/import_route.py:502-547`, `_do_import` `:550-667` | Yes (via importer) | Yes (draft, `is_public=False` `:592`) | **Yes** (`:568-580`) | **Yes** — "Import URL" tab, `BuildImportModal.tsx:86-111` |
| `POST /api/import/url` | `import_route.py:306-414` | Yes (duplicated inline fetch `:336-348`) | No | No (returns 502 `:356`; alert only on unhandled exception `:401-414`) | No — "Quick Fetch" tab input and button are `disabled` (`BuildImportModal.tsx:394-439`) |
| `POST /api/import/let/json` | `import_route.py:421-481` | No (accepts browser-captured `window.buildInfo`) | No | Only on mapper exception (`:461-473`) | Yes — "{ } JSON" tab (`BuildImportModal.tsx:150-185`) |

### 3.2 Frontend → backend (the path the user took)

1. `BuildImportModal.tsx:49-53` `detectSource()` classifies `lastepochtools.com/planner/` URLs as `"lastepochtools"`.
2. `BuildImportModal.tsx:86-95` `handleFullImport()` only rejects `importSource === null`; an LE Tools URL **is accepted**.
3. The tab copy (`:263-289`) says "Last Epoch Tools cannot be fetched by URL (LET is client-side)" and shows a "Use JSON tab for LET" hint, but the "Import Build" button (`:304-317`) is enabled for LE Tools URLs (`disabled={importLoading || !importUrl.trim()}`).
4. `frontend/src/lib/api.ts:583-584` → `POST /import/build {url}`.

### 3.3 Backend request handling

1. Rate limit: `@limiter.limit(_dynamic_import_limit, key_func=_rate_key_import)` `import_route.py:488-503` — anonymous `2 per minute` keyed on `request.remote_addr`. No `ProxyFix` exists anywhere under `backend/app` or `backend/wsgi.py` (grep: no matches), so behind Render's proxy the key may be a shared proxy address (UNVERIFIED; depends on Render's forwarding behaviour). Two alerts from two attempts is consistent with the limit not blocking the second attempt.
2. URL validation / source detection: `importer_factory.py:162-173` `detect_source()` using `URL_PATTERN = re.compile(r"lastepochtools\.com/planner/([A-Za-z0-9_\-]+)")` (`lastepochtools_importer.py:593`). Unanchored `search` — accepts any string containing that substring (e.g. `https://evil.example/?x=lastepochtools.com/planner/AB`). The code is extracted and re-inserted into a fixed host URL (`:694`), so this is not an SSRF, but validation is lax.
3. Importer selection: `importer_factory.py:176-186`.

### 3.4 Fetch (`lastepochtools_importer.py:691-733`)

| Property | Value | Evidence |
|---|---|---|
| Library | `requests==2.32.3` (urllib3 2.x, OpenSSL TLS stack, Python 3.11 in prod image) | `backend/requirements.txt:17`, `backend/Dockerfile:7,18` |
| Method / URL | `GET https://www.lastepochtools.com/planner/{code}` | `:693-694` |
| User-Agent | Hard-coded `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36` | `:696-700` |
| Accept | `text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` | `:701` |
| Accept-Language | `en-US,en;q=0.9` | `:702` |
| Accept-Encoding | `gzip, deflate` (requests default; no brotli installed) | prepared-request check, §8 cmd C |
| Connection | `keep-alive` (default) | same |
| Referer / Origin / cookies / `sec-ch-ua` / `sec-fetch-*` | None | `:695-703` |
| Session | None (one-off `requests.get`) | `:693` |
| Redirects | Followed (requests default) | — |
| Timeout | 15 s single value (connect+read each) | `:704` |
| Retries / backoff | None | — |
| Caching of fetched pages | None | — |
| Logged on failure | `"LET importer: HTTP %d for code=%s"` only — no response headers, no body snippet, no `cf-ray` | `:718` |

Observation (factual, not a recommendation to change it): the request declares a 2023 Chrome user agent while sending none of the headers a real Chrome sends and using a non-browser TLS client, from a datacenter address. That combination is a common trigger for upstream bot-protection rules. Whether LE Tools applies such rules is UNKNOWN from this environment.

### 3.5 Exact line producing the message

`backend/app/services/importers/lastepochtools_importer.py:716-727`

```python
except _requests.HTTPError as exc:
    status = exc.response.status_code if exc.response is not None else 502
    logger.warning("LET importer: HTTP %d for code=%s", status, code)
    if status == 404:
        return ImportResult(...)
    return ImportResult(
        success=False, source=self.source_name,
        error_message=f"Last Epoch Tools returned HTTP {status}.",
    )
```

(An identical string exists at `import_route.py:356` for `/api/import/url`, but that path returns 502 and does not alert, so it is not the source of this incident.)

### 3.6 Failure recording and alert

1. `_do_import` hard-failure branch `import_route.py:567-580`:
   ```python
   _record_and_alert(..., error_message=result.error_message or ...,
                     missing_fields=result.missing_fields,
                     partial_data=result.build_data)   # line 575
   ```
   `partial_data=result.build_data` is always `None` on a hard failure; the importer's own `result.partial_data` (e.g. `{"html_length", "code"}` at `lastepochtools_importer.py:751`, `{"keys", "code"}` at `:774`, or the rich mapper-crash dict at `:811-820`) is **never forwarded**. This is why every hard failure shows "No data parsed".
2. `_record_and_alert` `import_route.py:281-299` writes an `ImportFailure` row (`backend/app/models/__init__.py:330-345`: `source, raw_url, missing_fields, partial_data, user_id, error_message`) and calls `send_import_failure_alert`.
3. `backend/app/services/discord_notifier.py`:
   - `WEBHOOK_URL = os.environ.get("DISCORD_IMPORT_WEBHOOK_URL", "")` (`:18`).
   - Snapshot `:48-57`; background daemon thread `:60-65`.
   - Embed fields `:116-134`: Source, URL, **Missing Fields** (`", ".join(missing) if missing else "None"`), **Parsed Data** (`_summarize_partial_data`, returns `"No data parsed"` when `partial_data` is falsy `:70-71`), Error, plus optional Raw Gear / Raw Top-Level Keys, User.
   - No HTTP status field, no upstream headers, no attempt count, no dedupe/throttle. Every attempt on a known-dead path produces a red "hard" alert.
4. User response: HTTP 422 `{"errors":[{"message":"Last Epoch Tools returned HTTP 403."}]}`. The modal shows that raw message (`BuildImportModal.tsx:100-102`) with no pointer to the JSON/bookmarklet workaround. The "This issue has been reported" footer (`:560`) checks `importError.includes("422")`, which this message never contains, so it does not render.

### 3.7 Parsing (only reached on HTTP 2xx)

`_extract_build_info` (`lastepochtools_importer.py:596-673`; duplicated verbatim in `import_route.py:90-168`):

1. Regex `window\s*(?:\[\s*["']buildInfo["']\s*\]|\.buildInfo)\s*=\s*` then `json.JSONDecoder().raw_decode` (`:599-614`).
2. `<script id="__NEXT_DATA__" type="application/json">` → `props.pageProps.{buildInfo|build}` or pageProps containing `bio`/`charTree` (`:617-645`). Speculative: nothing in the repo shows LE Tools ever used Next.js.
3. Scan every `<script>` for a JSON object with `bio` or `charTree` (`:648-670`).
4. Otherwise 422-style failure "Could not find build data in the page…" with `partial_data={"html_length", "code"}` (`:745-752`) — which, per §3.6, is then dropped by the route.

Post-extract: `buildLoadError` flag → "Build not found or deleted" (`:754-759`); optional `data` envelope unwrap (`:762-764`); requires `bio` or `charTree` (`:766-775`); then `_map` (`:828-936`).

No HTML-level detection of bot-challenge pages exists (no check for `cf-mitigated`, "Just a moment", `challenge-platform`). A 200 challenge page would be reported as "LE Tools may have updated their format".

### 3.8 Normalization, validation, persistence

- `_map` (`:828-936`) → class (`_CLASS_MAP` `:32-38`), mastery (`_MASTERY_MAP` `:40-46`), passives (`charTree.selected` expanded to repeated node IDs `:855-863`), skills (`skillTrees[]`, `hud` order `:866-903`), gear (`_parse_gear` `:938-1222`).
- `BaseImporter.validate` (`base_importer.py:111-146`) only checks class name, mastery name, non-empty skill names.
- Persistence: `build_service.create_build` (`backend/app/services/build_service.py:44-81`) — no Marshmallow schema validation on this path; see contract doc 09.
- Detailed field-level behaviour, defects, and the coverage matrix are in `09_BUILD_IMPORT_CONTRACT.md`.

## 4. The durable legitimate representation that exists today: the bookmarklet

`frontend/public/bookmarklets/let-import.js:17-51` (minified copy inlined at `BuildImportModal.tsx:23-26`, also `let-import.bookmarklet.txt`):

- Runs in the user's own browser on a LE Tools planner page, reads `window.buildInfo`, `JSON.stringify`s it, writes it to the clipboard, shows a toast. No network calls, no data sent anywhere.
- Header comment (`:9-11`): "Necessary because LET moved to client-side rendering — the server cannot fetch window.buildInfo any more".
- UX wiring: "{ } JSON" tab (`BuildImportModal.tsx:485-525`) shows drag-to-bookmark link plus a DevTools fallback `copy(window.buildInfo)`. `looksLikeLetBuildInfo` (`:28-38`) auto-detects and posts to `/api/import/let/json` (`:167-185`).
- It is **not** the default tab; the default "Import URL" tab still accepts LE Tools URLs and routes them to the dead server-fetch path (root cause of the alert noise).
- Durability caveat: it depends on LE Tools continuing to expose `window.buildInfo` as a global. That is an undocumented page internal. Current presence is UNKNOWN (not observable from this environment).
- Earliest commit in the shallow history containing the bookmarklet: `e2c64eb` 2026-04-21 (true first-introduction date UNKNOWN due to shallow clone).

Browser-side data loading: whether the planner page loads build data through a JSON endpoint (XHR) after hydration is UNKNOWN — no network capture exists in the repo and live access was blocked. The repo contains no reference to any LE Tools JSON/API endpoint.

## 5. Public documentation search (LE Tools API / export format / bot protection)

| Query | Result |
|---|---|
| "lastepochtools planner import API export build code" | No relevant results. |
| "Last Epoch Tools build planner import export" (reddit / lastepochtools.com) | LE Tools news post on online character import and character profiles: import into the planner by account/character name or offline save upload; builds shared via "Save / Share". No public developer API documented. Source: [LE Tools: Online character import and Character Profiles](https://www.lastepochtools.com/news/article/site-update-online-character-import-and-character-profiles) |
| "github lastepochtools planner buildInfo parser import" | No LE Tools API docs. Mentions the community offline planner [Musholic/LastEpochPlanner](https://repos.ecosyste.ms/topics/last-epoch) and the [LE Tools forum thread](https://forum.lastepoch.com/t/last-epoch-tools-build-planner/28469). Whether those projects import LE Tools links, and how, is UNKNOWN. |
| "lastepochtools.com cloudflare 403" | Only generic scraping/bypass vendor pages; nothing LE Tools specific. Not used. |

Conclusions: **No publicly documented LE Tools API or third-party export format was found** (UNKNOWN whether a private one exists). No public announcement of planner-page or bot-protection changes was found. The repo's "moved to client-side rendering" claim is unsourced in-repo.

## 6. Origin of the 403

### 6.1 Live observation attempts from this container (3 of 5 allowed)

| # | Command | Result |
|---|---|---|
| A | `curl -sS -o robots.body -D robots.hdr -w 'http=%{http_code} ip=%{remote_ip}\n' https://www.lastepochtools.com/robots.txt` | `curl: (56) CONNECT tunnel failed, response 403`; headers are the **local proxy's**: `HTTP/1.1 403 Forbidden`, `Content-Type: text/plain; charset=utf-8`, `X-Content-Type-Options: nosniff`, `Content-Length: 80`; `remote_ip=127.0.0.1`. No `server: cloudflare`, no `cf-ray`. |
| — | local egress-proxy status endpoint query | `{"kind":"connect_rejected","detail":"gateway answered 403 to CONNECT (policy denial or upstream failure)","host":"www.lastepochtools.com:443"}` |
| B | WebFetch `https://www.lastepochtools.com/robots.txt` | `EGRESS_BLOCKED: Access to www.lastepochtools.com is blocked by the network egress proxy.` |
| C | WebFetch `https://www.lastepochtools.com/planner/B5P5P8M3` | same `EGRESS_BLOCKED` |

These 403s are produced by the audit environment's egress policy at CONNECT time; no packet reached LE Tools. **They say nothing about production.** Per proxy guidance, no retries or workarounds were attempted.

### 6.2 What can be said about production

- Production backend runs on Render (`render.yaml`: `epochforge-api` Flask+Gunicorn). It does not traverse this container's proxy. The 403 in the alert therefore came from whatever answered Render's outbound request: LE Tools' origin or an edge/WAF in front of it.
- Cloudflare vs origin: **UNKNOWN**. The importer records only the integer status (`:717-718`); no `server`, `cf-ray`, `cf-mitigated` headers or body snippet are logged or stored, so the evidence needed to distinguish was never captured. Whether lastepochtools.com is fronted by Cloudflare could not be verified from here.
- Render outbound traffic originates from shared cloud-provider address ranges. Many bot-protection products score datacenter ASNs as higher risk; combined with the header/TLS profile in §3.4, a 403 for this request shape is plausible from any such product. This is an inference, not a verified cause.
- The repo independently states server fetch is dead (`import_route.py:432-434`, `let-import.js:9-11`, `BuildImportModal.tsx:272-275, 397-401`). So the failure is a known, pre-existing condition, not a new regression introduced in v2.5.

## 7. Tests run

Command (scratch venv already provisioned with `backend/requirements.txt`):

```
cd backend && FLASK_ENV=testing SECRET_KEY=dummy JWT_SECRET_KEY=dummy \
  $SCRATCH/venv-backend/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_importers.py tests/test_build_import.py \
  tests/test_le_tools_importer_stage_context.py \
  tests/test_le_tools_importer_fixture_context.py \
  tests/test_le_tools_import_context_sidecar.py
```

Result: `232 passed, 4 warnings in 1.90s`.

What they prove:
- All LE Tools HTTP is mocked (`@patch("app.services.importers.lastepochtools_importer._requests.get")`, `test_importers.py:159-217`; inline `_LET_HTML` `:31-42` with `window["buildInfo"]`). They prove the parser handles the *assumed* format and that 404/500 map to messages.
- Sidecar / stage-context tests run against fixtures declared `"source": "synthetic_offline_not_captured_from_live_let"` (`backend/tests/fixtures/le_tools_offline_buildinfo_*.json`), all committed in `d98bb4c` 2026-05-11. The sidecar golden file `le_tools_import_context_sidecar_current.json` (`generated_at: 2026-05-07`) records incorrect mappings as `"status": "resolved"` (see 09 §5, IMP-4).
- No test exercises a 403, a challenge page, the alert `partial_data` content on hard failure, or the frontend's acceptance of LE Tools URLs on the Import URL tab.

What they do NOT prove: anything about the live LE Tools page format, `window.buildInfo` presence, field semantics (affix encoding, tier base, item IDs), or reachability from Render.

## 8. Reproduction evidence (local, mocked, no network)

**Cmd R1 — exact alert reproduction** (`$SCRATCH/imp_route403.py`: Flask test client, `_requests.get` patched to raise `HTTPError` with status 403, `send_import_failure_alert` patched):

```
status 422 {'data': None, 'errors': [{'message': 'Last Epoch Tools returned HTTP 403.'}], 'meta': None}
fetch call kwargs: call('https://www.lastepochtools.com/planner/B5P5P8M3', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.9'}, timeout=15)
alert: lastepochtools https://www.lastepochtools.com/planner/B5P5P8M3 [] None Last Epoch Tools returned HTTP 403. {'severity': 'hard'}
Parsed Data field -> No data parsed
```

Matches the production alert field-for-field.

**Cmd C — effective outbound headers** (prepared request, not sent): `{'User-Agent': ..., 'Accept-Encoding': 'gzip, deflate', 'Accept': ..., 'Connection': 'keep-alive', 'Accept-Language': 'en-US,en;q=0.9'}`; `brotli no`.

**Cmd R2 — mapper on repo fixture** (`$SCRATCH/imp_repro.py`): see 09 §5.

## 9. Fixture age vs current site

| Fixture | First commit (shallow) | Origin | Encodes |
|---|---|---|---|
| `le_tools_offline_buildinfo_equipment_sample.json` | 2026-05-11 `d98bb4c` | synthetic | `equipment[]` with integer `baseTypeID`, `slot` strings, `ir`/`ur` |
| `le_tools_offline_buildinfo_stage_context_sample.json` | 2026-05-11 | synthetic | same, plus `expected_diagnostic_category` |
| `le_tools_parsed_gear_context_sample.json` | 2026-05-11 | synthetic | already-mapped gear |
| `le_tools_import_context_sidecar_current.json` | 2026-05-11 (generated 2026-05-07) | generated from synthetic | diagnostic sidecar |
| Inline `_LET_HTML` in `test_importers.py` / `test_build_import.py` | UNKNOWN (shallow) | hand-written | server HTML with `window["buildInfo"]` |

No captured live LE Tools payload exists in the repo. Comparison against the current site: **UNKNOWN**. The code comments in `_parse_gear` (`:1079-1091`) record that `ir` and base64 `id` decoding turned out to be "item seed data, not type IDs" — evidence that the real format was reverse-engineered by trial and differs from the documented schema at the top of the module (`:7-14`).

## 10. Other importer (Maxroll) — brief

`backend/app/services/importers/maxroll_importer.py`: `URL_PATTERN` `:265`; probes **seven guessed endpoints** (`:275-281`) with spoofed browser UA plus `Referer`/`Origin: https://maxroll.gg` (`:735-744`), then falls back to HTML (`:783-810`). Diagnostics are better than LE Tools: per-attempt status list in the error (`test_build_import.py:3504-3519` asserts "HTTP 403" surfaces), `raw_keys` in `partial_data`. Same structural exposure (undocumented endpoints, datacenter egress, no retries), same `partial_data=result.build_data` drop on hard failure. Live status UNKNOWN.

## 11. What this audit does NOT prove

- It does not prove the 403 was issued by Cloudflare, by LE Tools' origin, or by any specific rule. No upstream response was observed.
- It does not prove that `window.buildInfo` still exists on LE Tools pages today, or that the bookmarklet works today.
- It does not prove the HTML parser would fail on a 200 response today (only that the repo itself asserts so).
- It does not measure how many users hit this path (ImportFailure table not queried; production DB not accessible).
- It does not verify Render outbound IP ranges or how Render forwards client IPs.

## 12. Commands used (summary)

```
sed/grep/cat over backend/app/services/importers/*, backend/app/routes/import_route.py,
  backend/app/services/discord_notifier.py, backend/app/models/__init__.py,
  backend/app/services/build_service.py, frontend/src/components/features/build/BuildImportModal.tsx,
  frontend/src/components/features/build/BuildPlannerPage.tsx, frontend/src/lib/api.ts,
  frontend/public/bookmarklets/let-import.js
git log --format='%ci %h %s' -- <fixtures, importer, bookmarklets>
git rev-parse --is-shallow-repository   # true
pytest (see §7)
python $SCRATCH/imp_route403.py; python $SCRATCH/imp_repro.py
curl robots.txt (blocked locally); local egress-proxy status query
WebFetch x2 (blocked); WebSearch x4
```
