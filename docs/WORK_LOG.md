# DFL technical work log

A running record of what has been built, what has been verified, and what is still open. It complements, and does not replace, `docs/decisions.md` (rule rationale), `docs/DECISION_LOG.md` (decision register), `PROJECT_STATUS.md` (navigation) and the `reports/verification_*.md` files (evidence).

**How to keep it current.** Add a dated entry at the bottom of the Timeline when a milestone lands, and move items between *Open work* and the Timeline as they close. Label claims **verified** (a command was run on a named commit), **untested**, or **proposed**. Do not record a decision here as approved unless the project owner said so.

Last updated: 2026-10-15, on `main` at `9961ff6`.

## Where things stand

- `main` and `step6-rebuild` point at the same commit (`00b6fb2`). `main` was fast-forwarded on 2026-10-15; before that it had stopped at `02490ab` (2026-10-05).
- `step6-rebuild` is **kept as a mirror of `main` on purpose**: `deploy/setup.sh`, `deploy/update.sh` and `deploy/start-live.sh` all default to it (override with `DFL_BRANCH`), and `PROJECT_STATUS.md` records it as the deployed branch. Do not delete it until the server is switched to `main`. Until then, any commit to `main` must also be pushed to `step6-rebuild`, or the server will not receive it.
- The fast tier passes (31 of 31). The slow tier passes (24 of 24) with the regenerated baselines; see Verification for the revisions. The fairness study (`engine/fairness.py`) has **not** been re-run since PR #14 (Open work, item 0).
- Nothing in this log authorizes a production deploy, restart or reset of live league state.

## Timeline

### Through 2026-10-05 (the old `main`, `02490ab`)
- League engine: schedule generator and checker, standings with NFL-style tiebreaks, playoffs, exile of the five-place teams, Ambassador Season, lottery and 48-pick draft (Phases 0 and 1).
- Rosters and a drive-by-drive game engine, injuries, offseason (Phase 2).
- Character cards: players, head coaches, owners and GMs as living cards with persistence in SQLite (`engine/store.py`); Decision Points as the single guarded door for choices (`engine/decisions.py`); stand-in agents and adversaries for testing.
- Economy: $100M cap, banking up to $125M, 90% floor, exile absorption (`engine/economy.py`); negotiation tables with the job interview as the first live table.

### 2026-10-07 — Step 6a, 6b (earned service)
- Earned player service accounting with expiry classification (6a); service integrated into minimum base pay and practice-squad eligibility (6b). Published as branch `step6-service`; see `docs/step6a_handoff.md`, `reports/verification_step6a.md`, `reports/verification_step6b.md`.

### Step 6c to 6i (branch `step6-rebuild`)
- 6c/6d rebuilt after the earlier work was lost before publication: pick ownership, qualifying tenders, funded offers, five-day matching, compensation (`engine/movement.py`). `reports/verification_step6cd.md`.
- 6e to 6i: waivers, franchise and transition tags, full trades, compensatory picks, contract tables; value-to-price re-signing replaces the old dice. `reports/verification_step6e_i.md` records 22 scripts passing, all 13 fairness bands inside range, and four independent-review findings, all fixed with tests.
- Dates for these steps are not recorded in the repository history.

### 2026-10-09
- Step 8c: governance, the Commissioner's shrink-only powers, the DFLPA representative and discipline.
- Step 9a: overtime ties, practice-squad elevations, extensions, autopilot trades, cutdown waivers, lasting injury damage.
- Fanbase card redesign (evolving meters, fading memories, boycott, exile mood); "owner" renamed "CEO" in user-facing text.
- "Ring of accountability" step A (CEO pledge and boycott response) and step B (coordinator cards with a head-coach veto, scheme fit, the GM's draft focus and cap-room plan). Fairness regenerated: 13 of 13 bands, both engines.

### 2026-10-10 and 2026-10-11
- One coaching pool: head coaches and coordinators are the same card; the CEO and head coach hire.
- Step C: the GM builds the roster; role utility.
- Character creator stages 1 and 2: the draft class as a table of prospects (real colleges, birth dates, derived college stats).
- GM and head coach have separate spheres; every draft pick is the GM's; relationship meters.

### 2026-10-12
- Calendar (Founding Day 1/1/2000, dated offseason, trade deadline) and Founding Day (all-rookie league).
- The clubs' real identities and the Commissioner's first-season schedule; the schedule skeleton (fixed slot template re-seeded each season from the previous final division rankings, divisions rotating through slot divisions, conferences swapping every fifth year).
- Ethics rule; the Commissioner's exile standard as two measured fairness bands; the early exile overshoot recorded with cause and ruling.
- Tiered checks (fast and slow) and error-bar verdicts for the fairness bands (`engine/run_checks.py`).
- Read-only website window, schedule guide page, play log in the engine, live league on the real clock.
- Deploy scripts (Caddy, sslip.io https) and `deploy/INSTALL.md`.
- Club names: 27 new nicknames; Jacksonville Tarpons became Florida Fangs.

### 2026-10-13 and 2026-10-14 (pull requests #2 to #23, merged into `step6-rebuild`)
Live pacing blocks, pause button, play-by-play text, field visuals, parity profiles, rules version 2 (penalties), statistics tab, live results, past seasons, night game, sprite field, standings tiebreak columns and magic number, live playoff seeds, division order by the league's tiebreakers, clock management, live play reveal at game pace, down and distance after the play, rules version 4 (injuries during the game), rules version 5 (kickoffs and conversions), a 3D view of the field, the site hierarchy, and team pages that grow with the league.

### 2026-10-15 — repository housekeeping
- `main` fast-forwarded from `02490ab` to `fd6555f`; no history rewritten.
- 22 merged feature branches and `step6-service` deleted (all contained in `main`). `step6-rebuild` was deleted by mistake and immediately recreated at `fd6555f` once the deploy scripts' dependence on it was noticed; it is kept as a mirror (see above).
- The founding data was compared with the owner's latest workbook (see Open work, item 5).
- The fast check tier was run on `main`; two failures were found and traced to PR #6 and PR #14 (see Verification).
- The two failing fast checks were fixed through PR #25 (rulebook exemption for `economy.REGULATED`) and PR #27 (`check_coordinators` compares GM banking over 5 seeds instead of 1; the GM behavior itself did not change).
- PR #29 fixed `check_fans` (the check, not the fans: the boycott-end memory assertion now clears the memory list first, because memory trimming can legitimately drop an old entry).
- PR #30 regenerated the autopilot goldens (`engine/golden_fingerprints.json`, seeds 33, 5, 21), the `check_parity` seed-33 hash, and `check_tables`' own copy of the seed 33 and 21 goldens, all stale since the Commissioner's tiebreak-order change (PR #14). Owner approved the regeneration.
- PR #26 added GitHub Actions (`.github/workflows/checks.yml`): the fast tier on every pull request and push to `main`, the slow tier weekly or on demand.
- This log was added, and `AGENTS.md`, `PROJECT_STATUS.md` and `docs/DECISION_LOG.md` were updated to reflect the branch change, through pull request #24.

### 2026-10-16: website made public (production change, owner approved in chat)
- PRs #32 (Standings tab restored), #33 (login moved to `/api/*` only; the page asks for the Pause switch only in a browser opened with `?admin=1`), #34 (`deploy/make-public.sh` and `deploy/RUNBOOK_public_site.md`).
- **Server state found (verified, read-only):** `/opt/dfl` at `5cd50ab` (updated 07:32 UTC with `update.sh`, which also restarted `dfl-live`), league `meta.json` `engine_commit` `fd6555f`, seed 7, Founding Day 2026-10-14. Between `fd6555f` and `5cd50ab` the only non-check engine change is one `engine/rulebook.py` exemption line (no gameplay code), so the restart's replay-from-seed warning did not change any result. Worth knowing for any later update: the warning is real whenever gameplay code differs.
- **Done:** DigitalOcean snapshot `before-public-site-2026-10-16` (2.56 GB) taken first; `/root/dfl-backup-2026-10-16/` holds the Caddyfile and a tarball of `/var/www/dfl/live` and `/etc/dfl`; then `make-public.sh` was run. **Verified from the server with plain requests:** `/`, `/live/results.json`, `/live/meta.json` answer 200 without a password; `/api/state` answers 401; `x-robots-tag: noindex, nofollow` still sent; `dfl-live`, `dfl-control` and `caddy` active; the deployed page contains the `?admin=1` logic. **Not verified:** the Pause button after logging in (the login for `/api/*` is the existing one).
- Rollback: `bash /opt/dfl/deploy/make-public.sh --undo` (restores `/etc/caddy/Caddyfile.before-public`), or restore the snapshot.
- Noted, left alone: `/var/www/dfl/dfl-frontend-review.tar.gz` (400 KB, 2026-10-15) sits in the web root, so it is now downloadable; it holds an older copy of the page and live feed (same data the site serves). Remove it if it should not be public.

### 2026-10-16: own domain, diamondfootballleague.com (production change, owner approved in chat)
- The owner bought `diamondfootballleague.com` at IONOS. In IONOS DNS: `A @` changed from IONOS's parking address (`74.208.236.111`) to the server (`143.198.130.68`), `A www` added at the same address; IONOS disabled its own "Default Site" records in the same step (the old A, an IPv6 `AAAA @` to the parking host, and a `_dep_ws_mutex` TXT). Mail records (MX, SPF, DKIM, DMARC, autodiscover) were not touched. TTL 1 hour.
- Server: `/etc/caddy/Caddyfile` site address is now `diamondfootballleague.com, www.diamondfootballleague.com, 143-198-130-68.sslip.io`. Backups: `/root/dfl-backup-2026-10-16/Caddyfile.before-domain` and `/etc/caddy/Caddyfile.pre-domain` (config as it was before this change; `Caddyfile.before-public` is the one from before the site was made public).
- **Verified:** Caddy logged "certificate obtained" for both new names; from the server, all three hostnames return 200 with a valid certificate and `/api/state` returns 401 on each; `https://diamondfootballleague.com/` loads in the owner's Chrome over public DNS. **Not verified:** `www` through public DNS in a browser (it resolves to the server at IONOS's own nameservers), and a Pause-button login on the new name.
- **Heads up:** the extra names live only in the server's Caddyfile. Running `deploy/render.sh` rewrites that file from `/etc/dfl/host` (still the `sslip.io` name) and would drop them; re-add them afterwards or change `/etc/dfl/host`.
- Rollback: copy `Caddyfile.pre-domain` over `/etc/caddy/Caddyfile` and `systemctl reload caddy`. DNS can be set back in IONOS.
- Not done, proposed: a DigitalOcean Reserved IP, so the domain keeps working if the server is ever rebuilt or upgraded (before any peer-review release).

## Open work

Sources are named so each item can be checked. Nothing here is an approved decision unless the cited document says so.

### 0. Fairness bands after PR #14
`engine/fairness.py` (the 13 fairness bands, hours-long) is not part of either check tier and has not been run since the tiebreak-order change. The regenerated goldens only show that outcomes changed; whether any band moved is **untested**. Run it on `main` and record the result (it needs the owner's attention if a band leaves its range).

### 1. Step 6 gaps (`reports/verification_step6e_i.md`)
- Extensions are made only when a contract expires; the contract table has no guarantee or bonus terms.
- The DFLPA representative is a guard in the table, not a character with a card; there is no trade table.
- Waivers do not cover cutdown or offseason releases.
- A compensatory pick's slot equals the last slot of its round, so two rookies in a round share a draft-pick number.
- Waiver priority for the wire run at the end of Week 3 uses draft order (a low-confidence reading of "through Week 3").
- The exile effect sits near the lower edge of its fairness band (-0.36 fast engine, -0.31 drive engine, band -0.5 to 0.5): a Step 9 calibration item.
- Trades by the autopilot are not built.

### 2. Step 6 completion gate (`docs/step6_remaining_plan.md`)
Boundary and atomicity checks, then the full suite, an explanation of any intended fingerprint change, re-run of the both-engine fairness and cap studies, reconciliation of the rulebook, and a recovery checkpoint. Parts of that file still describe design intent for pieces that have since been built; read its first section before treating anything in it as outstanding.

### 3. Orientation questions (`PROJECT_STATUS.md`, pull request #24)
Authority boundaries for CEO, GM, head coach and coordinators (including the requested third coordinator role); Commissioner selection from sitting CEOs, removal, and the simulated fan election for the vacated seat; exile recovery balance, fan election behavior, media factual grounding, agent visibility of character cards; the Truth, Beta, Alpha release pipeline (proposed, not implemented).

### 4. Deployment
- Switch the server from `step6-rebuild` to `main` (set `DFL_BRANCH=main`, or change the script defaults and the three raw-GitHub URLs in `deploy/INSTALL.md`, `setup.sh` and `start-live.sh`), then retire `step6-rebuild`. **Proposed; needs the owner and a backup/rollback plan.**

### 5. Founding data versus the owner's latest workbook (`DFL.xlsx`, compared 2026-10-15)
- **Verified:** the 360 Season 1 games in `data/schedule_2000.csv` match the workbook exactly (week, game number, date, kickoff, away and home club), and the 48 club IDs, cities, nicknames, venues, locations, conferences and divisions match.
- **Differences needing an owner decision (not applied):** colour palettes differ for 14 clubs (for example Montana, Utah, Calgary, Idaho, Mexico City, Oklahoma City, New Mexico, Toronto, Portland, Los Angeles, Sacramento, Omaha); the workbook lists the Florida abbreviation as `JAX`, the repository as `FLA`; the workbook has no hex codes for 14 clubs.
- **Schedule observations (workbook, Season 1 only; later seasons are not in the file):** time-slot points are inside the 33 to 38 band but uneven (23 of 40 clubs at 34; Chicago 38, Omaha 37); five clubs have a four-game home or away streak; all byes fall in weeks 15 to 19, which are all divisional games; the workbook's formulas refer to team rows by position and to teams by city name rather than by ID.
- Palette overlaps among the non-NFL clubs (for example Montana and Utah) conflict with the rule that each of the 16 gets a unique palette; this needs checking against whichever palette set is adopted.

## Verification

**Fast tier: all 31 scripts pass** (GitHub Actions; `main` at `9961ff6`, and again on the PR #30 branch at `7eba956`). First fully green since PR #6 and PR #14.

**Slow tier (GitHub Actions, workflow_dispatch):** run on the PR #30 branch. At `9bbc723` (goldens regenerated, `check_tables` copy not yet) 23 of 24 passed, the failure being `check_tables`; at `7eba956` (the same plus the `check_tables` fix) `check_tables`, `check_decisions` and `check_parity` pass. **The full slow tier passed on `7eba956`: 24 of 24** (run 38786772303).

**Before the baselines were regenerated** (slow tier on `e29785f`): `check_decisions`, `check_tables`, `check_parity` and `check_fans` failed. The first three were the stale baselines above (PR #14); `check_fans` was PR #29.

**History of the two failures** (found by running the fast tier locally on `fd6555f`: 29 of 31 passed). Both were absent at commit `2621f79` (2026-10-12, before pull requests #2 to #23) and were traced by re-running the failing script at each merge.

| Script | Failure | First failing merge | Resolution |
| --- | --- | --- | --- |
| `check_rulebook.py` | "every constant in economy.py is in a rulebook row" (`economy.REGULATED`) | PR #6, `parity` (`25e7d82`) | PR #25: classified as a parity-profile switch in `rulebook.EXEMPT`. No behavior change. |
| `check_coordinators.py` | "a GM who keeps extra room back banks more of it than one who spends to the limit" (9.53 versus 10.21 on seed 21) | PR #14, `tiebreak-order` (`d32a88f`) | PR #27: the check was fragile, not the behavior. Over 7 seeds the gap (keeps room back minus all-in) was +0.96 before PR #14 and +1.02 after, with one reversed seed each. The check now compares means over 5 seeds (8.90 versus 8.14). Only 7 seeds per side were sampled; this is a test-design fix, not proof for every league. |

Both failures sat on `step6-rebuild` from the merges (2026-10-13 for PR #6, 2026-10-14 for PR #14). Whether the checks were run before those merges is not recorded in the repository.

**Not yet verified**
- **Fairness bands** after PR #14 (Open work, item 0).
- **Workbook comparison:** see item 5 under Open work.

### 2026-10-17: the Chronicle (narrative layer), built on branch `chronicle`, not deployed
The Commissioner asked for 1 to 10 narrative entries after each week, 1 to 5 paragraphs each (about 2 on average), with up to $20 a month for AI writing, and decided the game never sees the narrative.
- `engine/chronicle.py`: a read-only consumer of the live feed. Per finished unit (a regular-season week, a playoff round) it scores each game (upset, thriller, overtime, blowout, shutout, streaks, big individual nights, star injuries, the playoffs), picks 1 to 9 stories under a 950-word cap, builds a closed fact sheet per story, writes the prose, holds it to the sheet with a checker (every number, score and name must be on the sheet), and adds a short "Around the league" roundup. Written once to `chronicle/<year>_<unit>.json` and never regenerated (the runner replays past seasons from the seed, so the words cannot be re-derived). Another league's chronicle is refused.
- Writers: a free template writer (the fallback, always passes its own checker) and an LLM writer that is OFF unless `ANTHROPIC_API_KEY`, `DFL_CHRONICLE_MODEL`, `DFL_PRICE_IN` and `DFL_PRICE_OUT` are set on the server. Bad text is retried once, then replaced by the template; a monthly budget (`DFL_CHRONICLE_BUDGET`, default 18 dollars) in `spend.json` stops it. `--estimate` sizes one week's prompts (about 4,000 tokens in, 1,300 out for 7 stories).
- Site: a "From the Chronicle" block on the live home page and a `#chronicle` page (every week, `#chronicle-<year>_<unit>`); no new tab.
- Rule (Commissioner): the game machine never sees the narrative. The chronicle only reads the feed; `check_chronicle.py` fails if it imports the simulation or the runner imports it. Characters other than the CEO do not read it; the CEO reads the press through the engine's own deterministic media cards, never the prose.
- Not yet: season review piece, playoff seeds in the playoff stories, firings/exile/trade events (they are not in the feed), the LLM prompts tuned on real output, deployment (needs the Commissioner's go-ahead, a backup, and a server-side API key he places himself).

### 2026-10-17: the Chronicle deployed (production change, owner approved in chat)
- Merged as PR #37 (`84ce78f`); `step6-rebuild` moved to the same commit. On the server: backup in `/root/dfl-backup-2026-10-17/` (`index.html`, `Caddyfile`, `prev-commit` = `5cd50ab`), then `update.sh --no-restart` (pages rebuilt; the league runner was NOT restarted and no gameplay code changed) and `deploy/enable-chronicle.sh` (new service `dfl-chronicle`, free template writer; no API key yet).
- Verified from outside: `https://diamondfootballleague.com/live/chronicle/index.json` lists year 1 (19 weeks, 4 playoff rounds) and year 2 week 1; the Chronicle page opens and shows the stories.
- Rollback: copy the backed-up `index.html` to `/var/www/dfl/index.html`, `systemctl disable --now dfl-chronicle`; the written files in `/var/www/dfl/live/chronicle` can stay or be deleted (nothing reads them but the page).
- AI writer: not on. The owner creates an Anthropic key with a $20 monthly limit and writes `/etc/dfl/chronicle.env` himself on the server (see `deploy/enable-chronicle.sh`), then `systemctl restart dfl-chronicle`.


### 2026-10-17: the chalkboard (branch `chalkboard`, not deployed)
- A new view on the game page ("View: Chalkboard"): the field flat and top-down, the 22 players as numbered dots in their club's colours (portraits can replace the numbers later), the blue and yellow lines kept. The existing sprite field and 3D views are unchanged and stay the default.
- After each run, pass, sack or try the board draws, after the fact, what the two coordinators most likely called: each player's route, block, rush, blitz, zone or man assignment, with a mark on the matchups the log decided, and one line naming the two calls and the situation.
- It is a **reconstruction, not a record**. The engine is untouched and still decides every result; `site/playcalls.js` picks, for the logged result, the most likely call consistent with it. Chances come from `data/playbook.json` (15 offensive and 9 defensive calls; formations; what each of the 22 is told to do), tilted by the situation (down, distance, field position, score, time, timeouts) and by the coordinator's archetype. The same play gives the same call on every machine (seeded, no clock). Nothing is stored on the server; the engine, media and coordinators never read it (`check_calls.py` fails if an engine file mentions it).
- Stated limits: the players the log names (carrier, passer, target, tackler, sacker) keep the old animation, so a route drawn for them is the call's, not always the path the dot ran; linemen and players who left injured earlier are filled in from the roster's best at each position; jersey numbers are a cosmetic depth order.
- Checks: `engine/check_calls.py` + `check_calls.js` run every one of the 50,537 runs, passes, sacks and tries of the founding league: a call that fits the result (a sack by a rusher, an interception by a defender in coverage, a target who has a route), repeatable, everyone on the field and apart, 22 assignments each, and the scene with the call ends where the log says with the same banners and name tags. Added to the fast tier.
