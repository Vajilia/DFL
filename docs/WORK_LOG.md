# DFL technical work log

A running record of what has been built, what has been verified, and what is still open. It complements, and does not replace, `docs/decisions.md` (rule rationale), `docs/DECISION_LOG.md` (decision register), `PROJECT_STATUS.md` (navigation) and the `reports/verification_*.md` files (evidence).

**How to keep it current.** Add a dated entry at the bottom of the Timeline when a milestone lands, and move items between *Open work* and the Timeline as they close. Label claims **verified** (a command was run on a named commit), **untested**, or **proposed**. Do not record a decision here as approved unless the project owner said so.

Last updated: 2026-10-15, on `main` at `fd6555f`.

## Where things stand

- `main` and `step6-rebuild` point at the same commit (`fd6555f`). `main` was fast-forwarded on 2026-10-15; before that it had stopped at `02490ab` (2026-10-05).
- `step6-rebuild` is **kept as a mirror of `main` on purpose**: `deploy/setup.sh`, `deploy/update.sh` and `deploy/start-live.sh` all default to it (override with `DFL_BRANCH`), and `PROJECT_STATUS.md` records it as the deployed branch. Do not delete it until the server is switched to `main`. Until then, any commit to `main` must also be pushed to `step6-rebuild`, or the server will not receive it.
- Check results on `fd6555f` are in the section **Verification on `fd6555f`** below: 29 of 31 fast checks pass; 2 fail; the slow tier is untested.
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
- This log was added, and `AGENTS.md`, `PROJECT_STATUS.md` and `docs/DECISION_LOG.md` were updated to reflect the branch change, through pull request #24.

## Open work

Sources are named so each item can be checked. Nothing here is an approved decision unless the cited document says so.

### 0. Failing checks on `main` (see Verification below)
Fix or consciously accept `check_rulebook` (`economy.REGULATED`, PR #6) and `check_coordinators` (PR #14); then run the slow tier on the fixed revision, which has not been run.

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

## Verification on `fd6555f`

Run 2026-10-15 with `python3 engine/run_checks.py -j 2` (the fast tier, Python 3.13, numpy 2.5.3) on `main` at `fd6555f`, before this documentation was added.

- **Result: 29 of 31 scripts passed, 2 failed.** Total 1,392 s of script time on two cores.
- **The slow tier (24 scripts: fairness, drive engine, decisions, store round trips and others) has not been run on this revision.** It is untested.
- Both failures were absent at commit `2621f79` (2026-10-12, before pull requests #2 to #23) and were traced by re-running the failing script at each merge.

| Script | Failure | First failing merge | Notes |
| --- | --- | --- | --- |
| `check_rulebook.py` | "every constant in economy.py is in a rulebook row" (`economy.REGULATED`) | PR #6, `parity` (`25e7d82`) | The parity profile "none" switches `economy.REGULATED` off, but the constant has no rulebook row and no entry in `rulebook.EXEMPT`. Passing needs a row or an exemption with a reason. **Proposed:** an `EXEMPT` entry saying it is a parity-profile switch, not a rule. Needs the owner, because it classifies a constant in the rulebook. |
| `check_coordinators.py` | "a GM who keeps extra room back banks more of it than one who spends to the limit" (9.53 versus 10.21, expected the first to be larger) | PR #14, `tiebreak-order` (`d32a88f`) | Fails the same way on a second run (deterministic). The assertion compares two simulated averages, so one hypothesis is that a legitimate tiebreak change shifted outcomes and the assertion is fragile; the other is that GM banking behavior really changed. **Untested which.** Check whether PR #14 regenerated the golden fingerprints before deciding. |

Both failures have been on `step6-rebuild` since the merges (2026-10-13 for PR #6, 2026-10-14 for PR #14). Whether the checks were run before those merges is not recorded in the repository.
