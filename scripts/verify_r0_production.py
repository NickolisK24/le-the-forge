#!/usr/bin/env python3
"""
AUDIT-R0 production smoke verification for The Forge / EpochForge.

Standalone operator script: Python 3.9+ standard library only, no install,
no repository checkout of the backend needed. It talks to an already-deployed
API and verifies the R0 security and behaviour gates that were proven locally:

  Gate 4   game-data mutation blocked (affix PATCH, game-data reload)
  Gate 10  multi-target simulation limits enforced
  Gate 9   import-failure telemetry (plus the retired LE Tools server fetch)
  Gate 5/6 cross-user mutation and private-build disclosure blocked
  Gate 7   deleting a viewed build works
           anonymous builds are read-only

Safety:
  * Only the EpochForge API hosts are accepted (or localhost with --allow-local).
  * The target is printed and must be confirmed before anything is sent.
  * Probes that could have side effects on an unpatched server are gated on a
    harmless probe proving the R0 guard is live first.
  * Existing user builds are never read or changed. Only builds named
    "R0 Verification ..." created by this run are touched.
  * Game data is never modified or reloaded.
  * Session tokens are read with a hidden prompt and never printed.

Exit status: 0 when every executed check passes, 1 when any check fails,
2 for usage errors or when the operator cancels.

Usage:
  python3 scripts/verify_r0_production.py --target https://epochforge-api.onrender.com/api
"""

from __future__ import annotations

import argparse
import getpass
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ALLOWED_HOSTS = {"epochforge-api.onrender.com", "api.epochforge.gg"}
LOCAL_HOSTS = {"localhost", "127.0.0.1"}
USER_AGENT = "EpochForge-R0-Smoke/1.0"

PRIVATE_BUILD_NAME = "R0 Verification - Delete Me"
ANON_BUILD_NAME = "R0 Verification - Anonymous - Cannot Be Deleted"
LET_INCIDENT_URL = "https://www.lastepochtools.com/planner/B5P5P8M3"
MAXROLL_TELEMETRY_URL = "https://maxroll.gg/last-epoch/planner/r0telemetrytest"

_TOKEN_RE = re.compile(r"eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+")
_BEARER_RE = re.compile(r"(?i)bearer\s+\S+")


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def redact(text: str) -> str:
    text = _TOKEN_RE.sub("[redacted-token]", text or "")
    return _BEARER_RE.sub("Bearer [redacted]", text)


class Results:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str, str]] = []

    def record(self, gate: str, name: str, ok: bool | None, detail: str) -> None:
        status = "PASS" if ok else ("SKIP" if ok is None else "FAIL")
        self.rows.append((status, gate, name, redact(detail)))
        print(f"  [{status}] {name} — {redact(detail)}")

    @property
    def failed(self) -> bool:
        return any(r[0] == "FAIL" for r in self.rows)

    def summary(self) -> str:
        lines = ["R0 PRODUCTION SMOKE RESULTS"]
        for status, gate, name, detail in self.rows:
            lines.append(f"{status:4}  {gate:7}  {name}: {detail}")
        counts = {s: sum(1 for r in self.rows if r[0] == s) for s in ("PASS", "FAIL", "SKIP")}
        lines.append(f"TOTAL  PASS={counts['PASS']}  FAIL={counts['FAIL']}  SKIP={counts['SKIP']}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

class Response:
    def __init__(self, status: int, body: bytes, elapsed: float) -> None:
        self.status = status
        self.elapsed = elapsed
        self.text = body.decode("utf-8", errors="replace")
        try:
            self.json = json.loads(self.text) if self.text else None
        except ValueError:
            self.json = None

    def error_message(self) -> str:
        errs = (self.json or {}).get("errors") if isinstance(self.json, dict) else None
        if errs and isinstance(errs, list) and isinstance(errs[0], dict):
            return str(errs[0].get("message", ""))[:160]
        return ""

    def error_code(self) -> str:
        errs = (self.json or {}).get("errors") if isinstance(self.json, dict) else None
        if errs and isinstance(errs, list) and isinstance(errs[0], dict):
            return str(errs[0].get("code", "") or "")
        return ""

    def data(self):
        return (self.json or {}).get("data") if isinstance(self.json, dict) else None


class Api:
    def __init__(self, base: str) -> None:
        self.base = base.rstrip("/")

    def call(self, method: str, path: str, body=None, token: str | None = None,
             timeout: float = 60.0) -> Response:
        url = f"{self.base}{path}"
        data = None
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        start = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = resp.read()
                return Response(resp.status, payload, time.monotonic() - start)
        except urllib.error.HTTPError as exc:
            return Response(exc.code, exc.read() or b"", time.monotonic() - start)


# ---------------------------------------------------------------------------
# Target validation and prompts
# ---------------------------------------------------------------------------

def validate_target(raw: str, allow_local: bool) -> str:
    parsed = urllib.parse.urlparse(raw.strip())
    host = (parsed.hostname or "").lower()
    path = parsed.path.rstrip("/")
    local = host in LOCAL_HOSTS
    if local and not allow_local:
        raise SystemExit("Refusing localhost target without --allow-local.")
    if not local:
        if parsed.scheme != "https":
            raise SystemExit("Target must use https://")
        if host not in ALLOWED_HOSTS:
            raise SystemExit(f"Refusing unknown host {host!r}. Allowed: {', '.join(sorted(ALLOWED_HOSTS))}")
    if path != "/api":
        raise SystemExit("Target must be the API root ending in /api, e.g. https://epochforge-api.onrender.com/api")
    if parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise SystemExit("Target must not contain credentials, a query string, or a fragment.")
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def confirm(word: str, prompt: str) -> bool:
    return ask(f"{prompt}\nType {word} to continue (anything else skips): ") == word


def ask_token(label: str) -> str:
    print(f"\n{label}: paste the copied sign-in token and press Enter (input is hidden).")
    try:
        token = getpass.getpass(f"{label} token: ").strip().strip('"')
    except EOFError:
        token = ""
    return token


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_service(api: Api, r: Results) -> bool:
    print("\n== Service reachable ==")
    health = api.call("GET", "/health", timeout=30)
    r.record("pre", "API health", health.status == 200, f"HTTP {health.status}")
    version = api.call("GET", "/version", timeout=30)
    d = version.data() or {}
    detail = f"HTTP {version.status}"
    if isinstance(d, dict):
        detail += f"; version={d.get('version')} commit={d.get('commit')}"
    print(f"  [INFO] {redact(detail)}")
    return health.status == 200


def check_game_data(api: Api, r: Results) -> None:
    print("\n== Gate 4: game data cannot be changed by anonymous requests ==")
    listing = api.call("GET", "/admin/affixes", timeout=30)
    rows = listing.data() if listing.status == 200 else None
    affix_id = rows[0].get("id") if isinstance(rows, list) and rows and isinstance(rows[0], dict) else None
    if not affix_id:
        r.record("gate4", "affix edit blocked", False, f"could not read an affix id (HTTP {listing.status})")
        r.record("gate4", "game-data reload blocked", None, "skipped: affix probe did not run")
        return
    # Empty body: an unpatched server answers 400 "Empty payload" before any
    # write, so this probe never modifies data either way.
    probe = api.call("PATCH", f"/admin/affixes/{urllib.parse.quote(str(affix_id))}", body={}, timeout=30)
    guarded = probe.status in (401, 403) or (probe.status == 404 and "affix" not in probe.error_message().lower())
    r.record("gate4", "affix edit blocked", guarded,
             f"HTTP {probe.status} {probe.error_message()!r} (unpatched server would answer 400)")
    if not guarded:
        r.record("gate4", "game-data reload blocked", None,
                 "skipped for safety: the affix guard was not confirmed, so a reload probe could reload live data")
        return
    reload_probe = api.call("POST", "/load/game-data", timeout=30)
    r.record("gate4", "game-data reload blocked", reload_probe.status in (401, 403, 404),
             f"HTTP {reload_probe.status}")


def check_multi_target(api: Api, r: Results) -> None:
    print("\n== Gate 10: multi-target simulation limits ==")
    target = [{"target_id": "r0_probe", "max_health": 1_000_000}]
    # Cheap guard probe: 3600 s at a 10 s tick is only 360 steps even on an
    # unpatched server. The patched server rejects it (duration > 300 s).
    guard = api.call("POST", "/simulate/multi-target",
                     body={"base_damage": 1, "tick_size": 10, "max_duration": 3600, "targets": target},
                     timeout=30)
    if guard.status != 422:
        r.record("gate10", "oversized simulation rejected", False,
                 f"guard probe returned HTTP {guard.status}; limits not live, pathological request NOT sent")
    else:
        targets = [{"target_id": f"r0_probe_{i}", "max_health": 1_000_000_000_000, "position_index": i}
                   for i in range(10)]
        big = api.call("POST", "/simulate/multi-target",
                       body={"base_damage": 1, "tick_size": 0.01, "max_duration": 3600, "targets": targets},
                       timeout=30)
        r.record("gate10", "oversized simulation rejected", big.status == 422 and big.elapsed < 5,
                 f"HTTP {big.status} in {big.elapsed:.2f}s (3600 s, 0.01 s tick, 10 targets)")
    normal = api.call("POST", "/simulate/multi-target",
                      body={"base_damage": 1000, "template": "single_boss"}, timeout=60)
    d = normal.data() or {}
    ok = normal.status == 200 and isinstance(d, dict) and d.get("damage_events_truncated") is False
    r.record("gate10", "normal simulation works", ok,
             f"HTTP {normal.status}, damage_events_truncated={d.get('damage_events_truncated') if isinstance(d, dict) else None}, "
             f"{normal.elapsed:.2f}s")


def check_imports(api: Api, r: Results) -> None:
    print("\n== Gate 9: import paths and failure telemetry ==")
    let = api.call("POST", "/import/build", body={"url": LET_INCIDENT_URL}, timeout=60)
    if let.status == 429:
        r.record("gate9", "LE Tools URL not fetched by server", None, "rate limited (HTTP 429); rerun in a minute")
    else:
        r.record("gate9", "LE Tools URL not fetched by server",
                 let.status == 422 and let.error_code() == "LET_SERVER_FETCH_UNSUPPORTED",
                 f"HTTP {let.status}, code={let.error_code() or '-'} in {let.elapsed:.2f}s")
    print("  Waiting 31 s so the import rate limit allows the telemetry probe...")
    time.sleep(31)
    tel = api.call("POST", "/import/build", body={"url": MAXROLL_TELEMETRY_URL}, timeout=180)
    if tel.status == 429:
        r.record("gate9", "telemetry probe (Maxroll failure)", None, "rate limited (HTTP 429); rerun in a minute")
        return
    msg = tel.error_message()
    r.record("gate9", "telemetry probe (Maxroll failure)", tel.status == 422,
             f"HTTP {tel.status} in {tel.elapsed:.1f}s, message={msg!r}")
    r.record("gate9", "failure message does not blame an expired build on a refusal",
             not ("refused" in msg.lower() and "expired" in msg.lower()), "checked response text")


def check_builds(api: Api, r: Results, token_a: str, token_b: str) -> None:
    print("\n== Gates 5, 6, 7: build privacy, ownership and deletion ==")
    me_a = api.call("GET", "/auth/me", token=token_a)
    me_b = api.call("GET", "/auth/me", token=token_b)
    if me_a.status != 200 or me_b.status != 200:
        r.record("gate5-7", "sign-in tokens accepted", False,
                 f"Account A HTTP {me_a.status}, Account B HTTP {me_b.status} (sign in again and recopy)")
        return
    a, b = me_a.data() or {}, me_b.data() or {}
    if a.get("id") == b.get("id"):
        r.record("gate5-7", "two different accounts", False, "Account A and Account B are the same user")
        return
    r.record("gate5-7", "two different accounts", True,
             f"Account A={a.get('username')}, Account B={b.get('username')}")

    created = api.call("POST", "/builds", token=token_a, body={
        "name": PRIVATE_BUILD_NAME, "description": "Disposable AUDIT-R0 verification build.",
        "character_class": "Mage", "mastery": "Sorcerer", "is_public": False,
    })
    slug = (created.data() or {}).get("slug") if created.status == 201 else None
    if not slug:
        r.record("gate5-7", "create disposable private build", False, f"HTTP {created.status} {created.error_message()!r}")
        return
    r.record("gate5-7", "create disposable private build", True, f"slug={slug}")
    path = f"/builds/{urllib.parse.quote(slug)}"
    deleted = False
    try:
        # Private build
        r.record("gate6", "owner can read private build", api.call("GET", path, token=token_a).status == 200, "Account A")
        st = api.call("GET", path, token=token_b).status
        r.record("gate6", "other account cannot read private build", st == 404, f"Account B HTTP {st}")
        st = api.call("GET", path).status
        r.record("gate6", "signed-out visitor cannot read private build", st == 404, f"HTTP {st}")
        st = api.call("POST", f"{path}/simulate", token=token_b).status
        r.record("gate6", "other account cannot simulate private build", st == 404, f"Account B HTTP {st}")
        st = api.call("PATCH", path, token=token_b, body={"description": "R0 tamper attempt"}).status
        r.record("gate5", "other account cannot edit private build", st == 404, f"Account B HTTP {st}")
        st = api.call("PATCH", path, body={"description": "R0 tamper attempt"}).status
        r.record("gate5", "signed-out visitor cannot edit private build", st == 404, f"HTTP {st}")

        # Make it public
        st = api.call("PATCH", path, token=token_a, body={"is_public": True, "description": "R0 owner edit 1"}).status
        r.record("gate5", "owner can edit and make public", st == 200, f"Account A HTTP {st}")
        st = api.call("GET", path).status
        r.record("gate6", "signed-out visitor can read public build", st == 200, f"HTTP {st}")
        st = api.call("PATCH", path, token=token_b, body={"description": "R0 tamper attempt"}).status
        r.record("gate5", "other account cannot edit public build", st == 403, f"Account B HTTP {st}")
        st = api.call("PATCH", path, body={"description": "R0 tamper attempt"}).status
        r.record("gate5", "signed-out visitor cannot edit public build", st == 401, f"HTTP {st}")
        st = api.call("PATCH", f"{path}/skills/r0probe/nodes/1", token=token_b, body={"points": 1}).status
        r.record("gate5", "other account cannot change skill nodes", st == 403, f"Account B HTTP {st}")
        st = api.call("PATCH", path, token=token_a, body={"description": "R0 owner edit 2"}).status
        r.record("gate5", "owner can still edit public build", st == 200, f"Account A HTTP {st}")
        desc = (api.call("GET", path).data() or {}).get("description")
        r.record("gate5", "no tamper attempt was saved", desc == "R0 owner edit 2", f"description={desc!r}")

        # Viewed-build delete
        st = api.call("POST", f"{path}/view").status
        r.record("gate7", "record a page view", st == 204, f"HTTP {st}")
        st = api.call("DELETE", path, token=token_b).status
        r.record("gate7", "other account cannot delete", st == 403, f"Account B HTTP {st}")
        st = api.call("DELETE", path).status
        r.record("gate7", "signed-out visitor cannot delete", st == 401, f"HTTP {st}")
        res = api.call("DELETE", path, token=token_a)
        deleted = res.status == 204
        r.record("gate7", "owner deletes viewed build", deleted, f"Account A HTTP {res.status} (500 here = the old bug)")
        st = api.call("GET", path, token=token_a).status
        r.record("gate7", "deleted build no longer resolves", st == 404, f"HTTP {st}")
    finally:
        if not deleted:
            res = api.call("DELETE", path, token=token_a)
            print(f"  [CLEANUP] owner delete of {slug}: HTTP {res.status}")


def check_anonymous_build(api: Api, r: Results) -> None:
    print("\n== Anonymous builds are read-only ==")
    created = api.call("POST", "/builds", body={
        "name": ANON_BUILD_NAME,
        "description": "Disposable AUDIT-R0 verification build. Anonymous builds cannot be deleted by design.",
        "character_class": "Mage", "mastery": "Sorcerer", "is_public": False,
    })
    slug = (created.data() or {}).get("slug") if created.status == 201 else None
    if not slug:
        r.record("anon", "create one anonymous build", False, f"HTTP {created.status} {created.error_message()!r}")
        return
    r.record("anon", "create one anonymous build", True, f"slug={slug} (private, unlisted; kept by design)")
    path = f"/builds/{urllib.parse.quote(slug)}"
    st = api.call("GET", path).status
    r.record("anon", "readable by its link", st == 200, f"HTTP {st}")
    st = api.call("PATCH", path, body={"description": "R0 tamper attempt"}).status
    r.record("anon", "anonymous edit denied", st == 403, f"HTTP {st}")
    st = api.call("DELETE", path).status
    r.record("anon", "anonymous delete denied", st == 401, f"HTTP {st}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TOKEN_HELP = """
How to copy a sign-in token (takes about 20 seconds):
  1. In that browser window, open https://epochforge.gg and make sure you are signed in.
  2. Open the browser console:
       Chrome:  View > Developer > JavaScript Console
  3. Type exactly this line and press Enter:
       copy(sessionStorage.getItem("forge_token"))
     (If Chrome asks you to allow pasting, type: allow pasting  then press Enter, and repeat.)
  4. Come back here and paste. Nothing is shown while you paste; that is expected.
"""


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="AUDIT-R0 production smoke verification.")
    parser.add_argument("--target", required=True, help="API root, e.g. https://epochforge-api.onrender.com/api")
    parser.add_argument("--allow-local", action="store_true", help="allow a localhost target (testing only)")
    args = parser.parse_args(argv)

    target = validate_target(args.target, args.allow_local)
    api = Api(target)
    r = Results()

    print("=" * 72)
    print("AUDIT-R0 production smoke verification")
    print(f"TARGET: {target}")
    print("=" * 72)
    if not confirm("YES", "This sends read-only and rejected-by-design requests to the target above."):
        print("Cancelled. Nothing was sent.")
        return 2

    if not check_service(api, r):
        print("\nThe API is not healthy; stopping before any checks.")
        print("\n" + r.summary())
        return 1

    check_game_data(api, r)
    check_multi_target(api, r)
    check_imports(api, r)

    print("\n" + "-" * 72)
    print("Next part: build privacy, ownership and deletion.")
    print(f"It creates ONE private build named {PRIVATE_BUILD_NAME!r} as Account A and deletes it at")
    print(f"the end, and ONE anonymous build named {ANON_BUILD_NAME!r}, which cannot be deleted")
    print("by design (it is private and unlisted). No other builds are read or changed.")
    if confirm("CREATE", "Run the build checks now?"):
        print(TOKEN_HELP)
        print("ACCOUNT A: a normal Chrome window, signed in with your first Discord account.")
        token_a = ask_token("ACCOUNT A")
        print("\nACCOUNT B: a Chrome Incognito window, signed in with a DIFFERENT Discord account.")
        token_b = ask_token("ACCOUNT B")
        if token_a and token_b:
            check_builds(api, r, token_a, token_b)
        else:
            r.record("gate5-7", "build checks", None, "skipped: a token was not provided")
        check_anonymous_build(api, r)
    else:
        r.record("gate5-7", "build checks", None, "skipped by operator")

    print("\n" + "=" * 72)
    print("COPY EVERYTHING BELOW THIS LINE AND SEND IT BACK")
    print("=" * 72)
    print(r.summary())
    print("Discord #forge-alerts check: see R0_OPERATOR_SMOKE_TEST.md step 2.")
    return 1 if r.failed else 0


if __name__ == "__main__":
    sys.exit(main())
