"""Measure real production latency for POST /api/simulate/build.

Phase-4 measurement script. Issues repeated requests with a representative
Fireball Sorcerer payload and reports summary statistics. Reads the
X-Analysis-Compute-MS and X-Response-Time headers to separate engine
compute time from framework / DB / serialisation overhead and from
network round-trip time.

Run from a machine that has network access to the target (e.g. a laptop
or the project owner's dev box). The repo sandbox cannot reach
``api.epochforge.gg``.

Typical invocation
------------------

    python scripts/measure_analysis_latency.py \\
        --base-url https://api.epochforge.gg \\
        --iterations 50 \\
        --delay-ms 200

Output
------

Prints a per-request row while running (so long runs show progress) and
a three-block summary at the end: total round trip, server total (from
``X-Response-Time``), and engine compute (from ``X-Analysis-Compute-MS``).
Also prints cache-hit and HTTP-error counts.

The project owner pastes this stdout into the conversation. Phase 4's
recommendation in ``docs/unified-planner-phase4-notes.md`` is written
from those numbers.

Design notes
------------

- Sequential requests only. Parallel fires would saturate the 30/min
  per-IP rate limit and would not reflect a user's typing workload.
- 200 ms spacing is deliberately slower than the hook's 400 ms debounce
  — the goal is clean measurements, not stress testing.
- By default each request jitters ``n_simulations`` by ±5 so every
  payload hashes differently and the server's 5-minute result cache
  does not skew the numbers. Pass ``--no-cache-buster`` to measure
  cache-hit latency specifically.
- The script has no dependency other than the standard library and
  ``requests``. If the repo's dev virtualenv is not convenient, a
  plain ``pip install requests`` is sufficient.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from typing import Optional

try:
    import requests
except ImportError:
    print(
        "error: this script requires the 'requests' library.\n"
        "install with: pip install requests",
        file=sys.stderr,
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# Representative payload — Fireball Sorcerer @ level 100
#
# The class / mastery / skill triple is pinned; the passive tree allocation
# and gear affix list aim to approximate a "fully-kitted level-100 Fireball
# Sorcerer" without picking a specific archetype (pyro, crit-storm, etc.).
# The exact numbers do not need to match any real user's build — the engine
# pipeline runs through the same aggregation / combat / defense / optimization
# stages regardless. Only the *presence* of 20+ passives and 10+ gear
# affixes matters for realistic compute cost.
# ---------------------------------------------------------------------------

FIREBALL_SORCERER_PAYLOAD: dict = {
    "character_class": "Mage",
    "mastery": "Sorcerer",
    "skill_name": "Fireball",
    "skill_level": 20,
    # 20+ Mage passive node raw_ids spanning the standard Sorcerer travel
    # path. Sourced from data/classes/passives.json; exact path is not
    # material for latency measurement.
    "allocated_node_ids": [
        0, 2, 1, 4, 3, 7, 5, 6, 24, 9, 8, 59, 45, 58, 78,
        12, 11, 20, 14, 13, 15, 17, 16, 18, 66,
    ],
    # 12 affixes typical of a Fireball Sorcerer end-game gear set. Mix of
    # offense (fire damage, spell damage, crit, cast speed) and defense
    # (resistances, life, ward).
    "gear_affixes": [
        {"name": "Increased Fire Damage", "tier": 5},
        {"name": "Increased Spell Damage", "tier": 5},
        {"name": "Increased Cast Speed", "tier": 4},
        {"name": "Increased Critical Strike Chance", "tier": 4},
        {"name": "Added Critical Strike Multiplier", "tier": 4},
        {"name": "Increased Intelligence", "tier": 4},
        {"name": "Increased Health", "tier": 5},
        {"name": "Fire Resistance", "tier": 5},
        {"name": "Cold Resistance", "tier": 5},
        {"name": "Lightning Resistance", "tier": 5},
        {"name": "Increased Mana", "tier": 4},
        {"name": "Ward Retention", "tier": 3},
    ],
}


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------


def build_payload(
    base: dict, iteration: int, cache_buster: bool, seed: Optional[int]
) -> dict:
    """Return a fresh copy of the base payload, optionally jittered."""
    payload = {**base}
    # Jitter n_simulations by iteration modulo 11 so consecutive requests
    # hash differently and we exercise the uncached path (5000 ± 5).
    if cache_buster:
        payload["n_simulations"] = 5000 + (iteration % 11) - 5
    else:
        payload["n_simulations"] = 5000
    if seed is not None:
        payload["seed"] = seed
    return payload


def _parse_header_ms(value: Optional[str]) -> Optional[float]:
    """Parse a header value like '12.3' or '12.3ms' into a float; None on miss."""
    if not value:
        return None
    s = value.strip().rstrip("ms").rstrip()
    try:
        return float(s)
    except ValueError:
        return None


def run(
    base_url: str,
    iterations: int,
    delay_ms: int,
    cache_buster: bool,
    seed: Optional[int],
    timeout_s: float,
) -> int:
    url = base_url.rstrip("/") + "/api/simulate/build"

    total_ms: list[float] = []
    server_ms: list[float] = []
    compute_ms: list[float] = []
    sizes: list[int] = []
    cache_hits = 0
    http_errors = 0
    error_codes: dict[int, int] = {}

    print(
        f"measure_analysis_latency.py — Fireball Sorcerer @ level 100\n"
        f"base_url = {base_url}\n"
        f"iterations = {iterations}, delay_ms = {delay_ms}, "
        f"cache_buster = {cache_buster}\n"
    )
    header = "request  status  total_ms  server_ms  compute_ms  bytes"
    print(header)

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "epochforge-latency-measure/1.0",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )

    for i in range(1, iterations + 1):
        payload = build_payload(
            FIREBALL_SORCERER_PAYLOAD, i, cache_buster, seed
        )
        body = json.dumps(payload)

        t0 = time.perf_counter()
        try:
            resp = session.post(url, data=body, timeout=timeout_s)
        except requests.RequestException as exc:
            elapsed = (time.perf_counter() - t0) * 1000
            print(
                f"{i:>4}/{iterations:<3}   ERR  {elapsed:>8.1f}  "
                f"{'--':>9}  {'--':>10}  {'--':>6}  ({exc.__class__.__name__})"
            )
            http_errors += 1
            if i < iterations:
                time.sleep(delay_ms / 1000.0)
            continue

        elapsed = (time.perf_counter() - t0) * 1000
        total_ms.append(elapsed)
        sizes.append(len(resp.content))

        server = _parse_header_ms(resp.headers.get("X-Response-Time"))
        compute = _parse_header_ms(resp.headers.get("X-Analysis-Compute-MS"))
        cache = resp.headers.get("X-Cache")

        if resp.status_code != 200:
            http_errors += 1
            error_codes[resp.status_code] = error_codes.get(resp.status_code, 0) + 1
        if cache == "HIT":
            cache_hits += 1

        if server is not None:
            server_ms.append(server)
        if compute is not None:
            compute_ms.append(compute)

        server_disp = f"{server:>9.2f}" if server is not None else f"{'--':>9}"
        compute_disp = f"{compute:>10.2f}" if compute is not None else f"{'--':>10}"
        print(
            f"{i:>4}/{iterations:<3}   {resp.status_code}  "
            f"{elapsed:>8.1f}  {server_disp}  {compute_disp}  "
            f"{len(resp.content):>6}"
            + ("  [cache]" if cache == "HIT" else "")
        )

        if i < iterations:
            time.sleep(delay_ms / 1000.0)

    print()
    _print_summary("Summary (total round trip)", total_ms)
    _print_summary("Summary (server total, X-Response-Time)", server_ms)
    _print_summary("Summary (engine compute, X-Analysis-Compute-MS)", compute_ms)

    print(f"cache hits: {cache_hits}/{iterations}   HTTP errors: {http_errors}/{iterations}")
    if error_codes:
        codes = ", ".join(f"{code}×{count}" for code, count in sorted(error_codes.items()))
        print(f"error codes seen: {codes}")
    if sizes:
        print(f"response size (bytes): min={min(sizes)} median={int(statistics.median(sizes))} max={max(sizes)}")

    return 1 if http_errors else 0


def _pct(samples: list[float], pct: float) -> float:
    """Simple nearest-rank percentile (good enough for n=50)."""
    if not samples:
        return 0.0
    xs = sorted(samples)
    k = max(0, min(len(xs) - 1, int(round((pct / 100.0) * (len(xs) - 1)))))
    return xs[k]


def _print_summary(label: str, samples: list[float]) -> None:
    print(f"=== {label} ===")
    if not samples:
        print("    (no samples)\n")
        return
    print(f"    min: {min(samples):>6.1f} ms")
    print(f" median: {statistics.median(samples):>6.1f} ms")
    print(f"    p95: {_pct(samples, 95):>6.1f} ms")
    print(f"    p99: {_pct(samples, 99):>6.1f} ms")
    print(f"    max: {max(samples):>6.1f} ms")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Measure POST /api/simulate/build latency with a representative "
            "Fireball Sorcerer payload. See docs/unified-planner-phase4-notes.md."
        ),
    )
    parser.add_argument(
        "--base-url",
        default="https://api.epochforge.gg",
        help="API base URL (default: %(default)s)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=50,
        help="Number of sequential requests to issue (default: 50)",
    )
    parser.add_argument(
        "--delay-ms",
        type=int,
        default=200,
        help="Milliseconds to sleep between requests (default: 200)",
    )
    parser.add_argument(
        "--no-cache-buster",
        action="store_true",
        help=(
            "Send the exact same payload every request (hits the 5-minute "
            "server cache after the first warm request). Default: jitter "
            "n_simulations by ±5 to exercise the uncached path."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help=(
            "Forward a fixed Monte Carlo seed to the backend. Useful for "
            "reproducible runs; no effect on latency itself."
        ),
    )
    parser.add_argument(
        "--timeout-s",
        type=float,
        default=15.0,
        help="Per-request timeout in seconds (default: 15)",
    )
    args = parser.parse_args(argv)

    if args.iterations < 1:
        parser.error("--iterations must be >= 1")
    if args.delay_ms < 0:
        parser.error("--delay-ms must be >= 0")

    return run(
        base_url=args.base_url,
        iterations=args.iterations,
        delay_ms=args.delay_ms,
        cache_buster=not args.no_cache_buster,
        seed=args.seed,
        timeout_s=args.timeout_s,
    )


if __name__ == "__main__":
    sys.exit(main())
