"""Verify passive stat key mapping coverage against the game data file.

Walks every PassiveNode stat entry in ``data/classes/passives.json`` and
reports what fraction gets picked up by
``app.services.passive_stat_resolver.STAT_KEY_MAP``. The remainder falls
through to ``special_effects`` at resolver runtime, which is fine for
conditional or flag-style keys but represents a gap whenever a common,
type-clean stat is missing an alias.

Two coverage floors are enforced, both measured against the file as it
ships today:

* ``--overall-floor`` (default ``25.0``) — fraction of all stat entries
  that hit the map. Keeps a safety margin so a large batch of newly
  scraped nodes doesn't accidentally drag the number below the pre-fix
  baseline of 25.1%.
* ``--freq-floor`` (default ``60.0``) — fraction of entries whose key
  appears 2+ times in the data file. Workhorse keys (resistances,
  attributes, increased X damage, etc.) should almost all be mapped;
  this floor catches regressions where a common alias is accidentally
  removed.

Exits with status 1 if either floor is breached. Intended for CI.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PASSIVES_JSON = REPO_ROOT / "data" / "classes" / "passives.json"


def _load_stat_key_map() -> dict[str, str]:
    """Import STAT_KEY_MAP without pulling in Flask/DB dependencies."""
    resolver_src = (
        REPO_ROOT / "backend" / "app" / "services" / "passive_stat_resolver.py"
    ).read_text()
    start = resolver_src.find("STAT_KEY_MAP:")
    end = resolver_src.find("\n}\n", start) + 2
    namespace: dict[str, object] = {}
    exec(resolver_src[start:end], namespace)  # noqa: S102 — trusted source file
    mapping = namespace.get("STAT_KEY_MAP")
    if not isinstance(mapping, dict):
        raise SystemExit("Failed to extract STAT_KEY_MAP from passive_stat_resolver.py")
    return mapping


def _load_passive_stat_keys() -> Counter[str]:
    raw = json.loads(PASSIVES_JSON.read_text())
    nodes = raw if isinstance(raw, list) else raw.get("nodes", [])
    counter: Counter[str] = Counter()
    for node in nodes:
        for stat in node.get("stats") or []:
            counter[stat.get("key", "")] += 1
    return counter


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overall-floor", type=float, default=25.0,
                        help="Minimum overall coverage %% (default 25.0).")
    parser.add_argument("--freq-floor", type=float, default=60.0,
                        help="Minimum freq>=2 coverage %% (default 60.0).")
    parser.add_argument("--top", type=int, default=20,
                        help="How many unmapped keys to print (default 20).")
    args = parser.parse_args()

    mapping = _load_stat_key_map()
    counts = _load_passive_stat_keys()

    total = sum(counts.values())
    mapped = sum(c for k, c in counts.items() if k in mapping)
    overall_pct = 100.0 * mapped / total if total else 0.0

    freq2_items = [(k, c) for k, c in counts.items() if c >= 2]
    freq2_total = sum(c for _, c in freq2_items)
    freq2_mapped = sum(c for k, c in freq2_items if k in mapping)
    freq2_pct = 100.0 * freq2_mapped / freq2_total if freq2_total else 0.0

    print(f"STAT_KEY_MAP entries        : {len(mapping)}")
    print(f"Passive stat entries total  : {total}")
    print(f"  mapped                    : {mapped}")
    print(f"  unmapped                  : {total - mapped}")
    print(f"  overall coverage          : {overall_pct:.1f}% "
          f"(floor {args.overall_floor:.1f}%)")
    print(f"freq>=2 entries total       : {freq2_total}")
    print(f"  mapped                    : {freq2_mapped}")
    print(f"  freq>=2 coverage          : {freq2_pct:.1f}% "
          f"(floor {args.freq_floor:.1f}%)")

    unmapped = sorted(
        ((k, c) for k, c in counts.items() if k not in mapping),
        key=lambda kv: (-kv[1], kv[0]),
    )
    if unmapped:
        print(f"\nTop {min(args.top, len(unmapped))} unmapped keys:")
        for key, count in unmapped[: args.top]:
            print(f"  {count:4d}  {key!r}")

    failed = False
    if overall_pct < args.overall_floor:
        print(f"\nFAIL: overall coverage {overall_pct:.1f}% "
              f"< floor {args.overall_floor:.1f}%", file=sys.stderr)
        failed = True
    if freq2_pct < args.freq_floor:
        print(f"FAIL: freq>=2 coverage {freq2_pct:.1f}% "
              f"< floor {args.freq_floor:.1f}%", file=sys.stderr)
        failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
