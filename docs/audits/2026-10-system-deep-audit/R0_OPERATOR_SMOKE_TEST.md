# R0 Production Smoke Test — Operator Guide

This finishes the six remaining AUDIT-R0 production checks. It takes about 10 minutes.

**You need:**
- a terminal on your computer;
- Google Chrome;
- **two different Discord accounts**, called **Account A** and **Account B** below.

**What the test does:**
- Sends requests to the live API that the site is expected to refuse.
- Creates **one** temporary build (deleted at the end).
- Creates **one** anonymous test build, which stays because anonymous builds cannot be deleted by design. It is private and unlisted.
- Never touches anyone else's builds or the game data.

---

## STEP 1 — Get the script

In your local copy of the `le-the-forge` repository:

```
git fetch origin
git switch ops/r0-production-smoke
```

## STEP 2 — Run it

```
python3 scripts/verify_r0_production.py --target https://epochforge-api.onrender.com/api
```

**It will ask:**

1. **"Type YES to continue"**: type `YES`. It then runs the automatic checks for about a minute: game data, simulation limits and imports.
   - It pauses for 31 seconds in the middle. That is expected.
2. **"Type CREATE to continue"**: type `CREATE` to run the account checks (STEP 3).

## STEP 3 — Sign in with the two accounts when it asks

**Account A:**
1. Open a normal Chrome window and go to https://epochforge.gg.
2. Sign in with **Account A**.
3. Open the console: **View → Developer → JavaScript Console**.
4. Type this exactly, then press Enter:
   ```
   copy(sessionStorage.getItem("forge_token"))
   ```
   If Chrome says pasting is blocked, type `allow pasting`, press Enter, and repeat.
5. Go back to the terminal and paste when it asks for **ACCOUNT A**. Nothing shows while you paste; that is normal. Press Enter.

**Account B:**
1. Open a **Chrome Incognito window**.
2. Go to https://epochforge.gg and sign in with **Account B**.
3. Do steps 3–5 above, pasting when it asks for **ACCOUNT B**.

The script then checks, by itself:
- the private build is hidden from Account B and from signed-out visitors;
- only Account A can edit it;
- deleting a build that has been viewed works;
- anonymous builds can't be edited or deleted.

**EXPECTED:** the last line is `TOTAL PASS=32 FAIL=0 SKIP=0`.

## STEP 4 — Check Discord

Open Discord → **#forge-alerts**. Find the alert that appeared during the run: **"Import Failure — maxroll"** for `r0telemetrytest`.

**EXPECTED fields:**

| Field | Should show |
|---|---|
| Stage | `fetch` |
| Category | an `upstream_…` value (e.g. `upstream_not_found`, `upstream_blocked`), or `unknown` if Maxroll answered without a build |
| HTTP Status | a number such as `404` or `403` (absent if Maxroll answered 200 without a build) |
| Missing Fields | `Not evaluated — parsing did not complete` (must **not** say `None`) |
| Parsed Data | `Not attempted (failed at fetch)` |
| Versions | app / data / extractor versions |
| Replay | `url_retry` |
| Failure ID | an ID |

**The alert must NOT contain:** raw gear JSON, cookies, "Authorization" or "Bearer" text, secrets, or any build contents.

Also confirm there is **no** alert for the Last Epoch Tools link (`B5P5P8M3`) from this run.

## STEP 5 — Check the API logs

Render → **epochforge-api** → **Logs**, around the time of the run.

**EXPECTED:**
- no `500`;
- no `IntegrityError`, `NotNullViolation` or `ForeignKeyViolation`;
- no worker restart.

## STEP 6 — Send back

1. Everything the script printed below **"COPY EVERYTHING BELOW THIS LINE AND SEND IT BACK"**.
2. A screenshot of the Discord alert, or the field values from STEP 4.
3. A one-line STEP 5 result: "no errors in logs", or paste the error.

---

**If something fails or a line says SKIP:** send the output anyway. The script stops itself before any risky request if the protections aren't live, so it is safe to run again.

**Afterwards:**
- Sign out of both browser windows. That clears the copied sign-in sessions from the browser.
- The anonymous test build, `R0 Verification - Anonymous - Cannot Be Deleted`, stays on purpose. It is private and unlisted.
