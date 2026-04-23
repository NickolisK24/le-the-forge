# Unified Planner — Phase 4 Notes (performance audit)

Companion to `docs/unified-planner-design.md`, `docs/unified-planner-phase2-notes.md`,
and `docs/unified-planner-phase3-notes.md`. Phase 4 of 5.

Phase 4 was originally scoped as "performance optimization of the analysis
endpoint." The phase-2 baseline (§2 of the phase-2 notes) reported the
stateless `/api/simulate/build` endpoint returning in **4–7 ms** in-process
on a representative build. That is already fast enough that aggressive
optimisation may be unnecessary. **This phase is therefore a measurement and
decision phase first.** We measure real production latency, identify whether
real bottlenecks exist, and only then either propose targeted fixes or
recommend closing the phase with no code changes.

No optimisation code lands until measurements justify it.

## 1. Current request flow — end to end

Summarised so that later sections of this doc can refer back instead of
re-deriving it. Sources: `frontend/src/hooks/useDebouncedAnalysis.ts`,
`frontend/src/store/buildWorkspace.ts`, `backend/app/routes/simulate.py`,
`backend/app/services/simulation_service.py`, `backend/app/__init__.py`.

### 1.1 Frontend (browser)

1. **Edit lands in the store.** Any `setMeta` / `setSkills` / `setGear` /
   `setPassiveTree` / `setBlessings` call on `useBuildWorkspaceStore`
   produces a new top-level state object.
   (`frontend/src/store/buildWorkspace.ts:226-239`.)
2. **`useDebouncedAnalysis` reacts.** The hook subscribes to
   `character_class`, `mastery`, `level`, `skills`, `passive_tree`, `gear`,
   `blessings`, and `workspaceStatus`. A change in any of these schedules
   a `setTimeout(runAnalysis, 400)` — except on the very first fire after
   `status` flips to `"ready"`, which uses a 0 ms delay.
   (`useDebouncedAnalysis.ts:171-206`.)
3. **Gate: `buildIsSimulatable`.** Inside `runAnalysis`, the latest store
   build is re-read and the simulatability check runs. If the build is not
   simulatable (no class, no mastery, or no skills with a `skill_name`),
   the function returns early without firing a request.
   (`useDebouncedAnalysis.ts:43-50, 142-144`.)
4. **Request-id bump.** `store.requestAnalysis()` increments the monotonic
   `analysisRequestId` counter, flips `analysisStatus` to `"pending"`, and
   returns the new id. The previous `analysisResult` stays visible so the
   panel does not flicker.
   (`buildWorkspace.ts:245-258`.)
5. **POST to the stateless endpoint.** `simulateApi.buildInline(payload)`
   (`frontend/src/lib/api.ts`) wraps `fetch` to `POST /api/simulate/build`
   with the payload from `buildAnalysisPayload()`: `character_class`,
   `mastery`, `skill_name`, `skill_level`, `allocated_node_ids`,
   `gear_affixes`. `n_simulations` is omitted — the backend default (5000)
   applies.
6. **Response discriminator.** `res.data` → `setAnalysisResult(id, data)`.
   `res.errors` or a thrown error → `setAnalysisError(id, message)`.
7. **Stale-request discard.** Both setters compare `id` to the current
   `analysisRequestId`. A response whose id does not match is silently
   dropped — this is the phase-2 guarantee the presentation layer depends
   on.
   (`buildWorkspace.ts:260-280`.)

### 1.2 Backend (Flask)

1. **Global `before_request` timer.** `_start_timer` stashes
   `g.start_time = time.perf_counter()`. Every request gets this.
   (`backend/app/__init__.py:159-162`.)
2. **Rate limiter.** `@limiter.limit(_LIMIT_BUILD)` — default `"30 per
   minute"` per IP, configurable via `RATE_LIMIT_SIMULATE_BUILD`.
3. **Schema validation.** `SimulateBuildSchema().load(request.get_json())`.
   Failures return 422 with per-field messages.
4. **`_load_passive_nodes(character_class)` — synchronous DB query.**
   `PassiveNode.query.filter_by(character_class=…).all()`. This is the
   only DB hit on the request path. Results are not cached at the query
   layer — fresh query on every request.
   (`backend/app/routes/simulate.py:76-79, 297`.)
5. **Passive stat resolver.** `resolve_passive_stats(passive_tree)` runs
   only if the frontend sent string-id `passive_tree` — today the
   frontend hook omits this field, so this call is skipped entirely for
   unified-workspace traffic.
6. **Result cache lookup.** Cache key is the SHA-256 of the validated
   payload plus the loaded nodes list. On hit, returns the cached dict
   with `X-Cache: HIT`. TTL is 300 s.
   (`simulate.py:301-306`.)
7. **Compute — `simulation_service.simulate_full_build(...)`.** The full
   pipeline: `aggregate_stats` → `_resolve_skill_modifiers` →
   `_extract_conversions` → `combat_engine.calculate_dps` →
   `combat_engine.monte_carlo_dps` (5000 samples) →
   `defense_engine.calculate_defense` → `optimization_engine.get_stat_upgrades`
   (top 5). No DB access inside these engines.
   (`backend/app/services/simulation_service.py:213-285`.)
8. **Cache populate.** `cache_set(cache_key, result, 300)`.
9. **`ok(data=result)` → JSON serialise.**
10. **Global `after_request`.** `X-Response-Time: {elapsed_ms}ms` header
    is set for every response. Requests > 500 ms are logged WARNING.
    (`backend/app/__init__.py:164-175`.)

### 1.3 Known quantities

- Phase-2 in-process baseline: **4.3–6.8 ms** for `simulate_full_build`,
  measured via `flask.test_client()` on the sandbox host.
- Expected real-client round trip at phase-2 write time: **30–100 ms p50**,
  well under the 400 ms debounce budget.
- Debounce window: **400 ms**.
- `n_simulations` default: **5 000**.
- Rate limit: **30 req/min/IP**.
- Result cache TTL: **300 s**. Every unique payload hash is a cache miss
  the first time, a hit subsequently.

### 1.4 Observations that motivate measurement

- **Only one DB query per request** (`_load_passive_nodes`). This runs
  before the cache lookup, so cache hits still pay for the DB round trip.
  If production DB latency is meaningful, that could dominate the
  in-process number.
- **Monte Carlo at 5 000 samples is the heaviest compute step.** If
  production CPU is slower than the sandbox host or if contention on the
  web dyno matters, real compute time could exceed the 4–7 ms baseline by
  a material factor.
- **Cache effectiveness under typing workloads is unclear.** Each
  keystroke produces a different payload hash (different skill_level,
  different passives list, different affix set) so the result cache only
  helps on repeat visits to the same final build. The in-workspace hit
  rate is likely near zero.
- **Network latency dominates on WAN connections.** A 60 ms WAN RTT is
  already an order of magnitude larger than the in-process compute, so
  the question "is user-facing latency a problem?" is primarily a
  network + TCP handshake + TLS question, not a compute question.

The rest of this phase answers these open questions with measurements
taken against the live production endpoint.

## 2. Measurement plan

Defined in §3 below. At a high level:

1. Add a narrow server-side timing header `X-Analysis-Compute-MS` that
   reports only the `simulation_service.simulate_full_build()` call
   duration, separate from framework overhead and the existing
   `X-Response-Time` header.
2. Author `scripts/measure_analysis_latency.py` — a standalone script
   the project owner runs from a production-adjacent host. It posts a
   representative Fireball Sorcerer payload 50 times with 200 ms
   spacing and reports min/median/p95/p99/max for both total round trip
   and server compute.
3. Feed the results back into this doc and write the recommendation in
   §4.

## 3. Measurement infrastructure

### 3.1 Server-side timing header

A new `X-Analysis-Compute-MS` header is set on every
`/api/simulate/build` response. It reports the wall-clock milliseconds
spent inside `simulation_service.simulate_full_build(**sim_kwargs)` —
i.e. just the engine pipeline, excluding DB load, schema validation,
cache lookup, and JSON serialisation. Combined with the existing
`X-Response-Time` header, the script can break a single request into:

- Network + client overhead = `total_roundtrip_ms − X-Response-Time`
- Framework / DB / serialisation = `X-Response-Time − X-Analysis-Compute-MS`
- Engine compute = `X-Analysis-Compute-MS`

On cache hits the header reports `0` (the pipeline did not run).

The header lives on the `/build` route only — other stateless endpoints
are out of scope for this phase.

### 3.2 Measurement script

`scripts/measure_analysis_latency.py`. See its top-of-file docstring for
the full usage block. In summary:

**Command the project owner runs** (from a shell that has `requests`
available; the repo's dev virtualenv is sufficient):

```bash
python scripts/measure_analysis_latency.py \
  --base-url https://api.epochforge.gg \
  --iterations 50 \
  --delay-ms 200
```

**What to paste back into the conversation:** the full stdout block,
which looks like:

```
measure_analysis_latency.py — Fireball Sorcerer @ level 100
base_url = https://api.epochforge.gg
iterations = 50, delay_ms = 200

request  status  total_ms  server_ms  compute_ms  bytes
  1/50      200       67.2      12.1         6.4   4120
  2/50      200       54.9       9.3         5.1   4120
  ...
=== Summary (total round trip) ===
    min:   48.1 ms
 median:   62.5 ms
    p95:   88.3 ms
    p99:   91.0 ms
    max:   94.2 ms
=== Summary (server total, X-Response-Time) ===
    min:    8.7 ms
 median:   11.2 ms
    p95:   15.8 ms
    p99:   17.1 ms
    max:   18.3 ms
=== Summary (engine compute, X-Analysis-Compute-MS) ===
    min:    4.6 ms
 median:    6.0 ms
    p95:    9.1 ms
    p99:   10.2 ms
    max:   11.0 ms
cache hits: 0/50   HTTP errors: 0/50
```

Flags the script supports:

- `--base-url` (default `https://api.epochforge.gg`)
- `--iterations` (default `50`)
- `--delay-ms` (default `200`)
- `--seed` (optional; forwarded to the backend so repeated calls produce
  the same Monte Carlo output — useful for cache-hit testing)
- `--no-cache-buster` — by default the script adds a fresh `n_simulations`
  jitter of ±5 to each request so cache hits don't skew the measurement;
  pass this flag to hit the cache deliberately.

**Do not run the script from the sandbox.** The sandbox has no network
path to `api.epochforge.gg`. The project owner runs it and pastes results
back. The branch up to this point contains only measurement
infrastructure, not optimisation code.

## 4. Recommendation

_To be written once the measurement results are available._

This section will evaluate the results against the perception thresholds:

- Debounce (400 ms) + round trip < 600 ms: effectively instant.
- 600–1000 ms: acceptable.
- \> 1000 ms: sluggish.

And will recommend one of:

1. **No optimisation needed.** Close phase 4, proceed to phase 5.
2. **Targeted backend optimisation.** E.g. cache `_load_passive_nodes`
   per-process (it's a class-scoped query and passive data is static
   between deploys), reorder the cache lookup ahead of the passive-node
   load, or reduce `n_simulations` default.
3. **Frontend architecture change.** A fast client-side preview with
   the authoritative server result arriving after — only if round trip
   itself is the bottleneck and no backend fix will close the gap.

Any implementation must include a correctness test (optimised output
matches the baseline output for equivalent inputs), before/after
measurements, and an explicit note about the stale-request discard
mechanism from phase 2 if caching layers are introduced.
