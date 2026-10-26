# Phase 1 — Edition 8.15 reconciliation audit (working baseline)

Date: 2026-10-26  
Branch: `audit/ed8-15-phase1`  
Status: **NOT FROZEN; MATERIAL IMPLEMENTATION CONFLICTS**  
Authority: **DFL Living Design Document, Edition 8.15, 2026-10-23, SHA-256 declaration `6a77c043f6ca8fb89a5e17637f0e291d9ae8995ebf47a01a6bcd38d71a547454`**. This declaration has not been recomputed in this audit.

## Policy and authority

1. Edition 8.15 §§0–20 supersedes all old rulebooks, decisions, workbook and baseline tests. The existing `engine/rulebook.py` status report must not be used as evidence of Edition 8.15 compliance.
2. DFL rules take precedence; where Edition 8.15 is silent, use a versioned pre-founding NFL reference, not later live NFL changes. The initial NFL reference year is 2026, subject to explicit freeze documentation.
3. Do not silently replace Edition 8.15's deliberate NFL departures with current NFL procedure.
4. Keep *rules* distinct from *empirical rates* and *implementation dials*. Calibrate rates per appropriate exposure (play, snap, player-season, team-season), never force a season total.
5. Do not modify production `main`, archived results, or live clock while migrating. Preserve deterministic compatibility of legacy saves via an explicit versioned migration or isolated legacy runner. Do not translate old financial numbers by a global multiplier.
6. No governance action may silently change the frozen rulebook. The user's stated target is no post-founding rule modifications; later real NFL changes do not automatically apply.

## Observed conflicts (edition takes priority)

| Priority | Edition 8.15 | Existing `main` implementation / documentation | Migration target |
|---|---|---|---|
| P0 | §1 user is purely a viewer; no controlling vote | `engine/governance.py` and older commissioner controls/model governance | Audit all human/website control paths; prevent user-driven football outcomes |
| P0 | §2 27 calendar weeks; 19 numbered weeks with breaks after 4/9/14, byes 15–19 | `engine/rules.py` uses 19 consecutive weeks / 23 total game weeks; `calendar_dfl.py` is old | Rebuild calendar and fixture mapping; preserve 18 games and 9H/9A |
| P0 | §3 seeded beds rotate within four-bed blocks, conferences swap bed blocks every four seasons, cycle eight | `engine/identity.py` reuses first-year slot layout by conference/division/seed | Replace with bed-based eight-year generator and independent cycle tests |
| P0 | §3 sorted-once custom cascade; tied games excluded from standings win/loss/opponent denominators | `engine/rules.py` selects NFL tiebreaks; `transactions.py` uses half-win ties | Rewrite standings, tiebreaks, waiver priority and dependent accounting as specified |
| P0 | §11 cap $1,000, reserve $25, minimum $5, no bank, no floor, no cap relief in exile | `engine/economy.py`, `engine/rules.py`, `engine/rulebook.py` describe $100M hard cap, banking, 90% floor and exile absorption | Replace entire economy model after ledger/viability design, not simple currency conversion |
| P0 | §11 top **69 contracts** before cut; entire squad afterwards; dead ceiling $735 and future-year viability | Existing top-51 and multi-year cap calculations | Implement transactional forward-year viability checks including guaranteed money and bonus acceleration |
| P0 | §§11–12 remove tags, ERFA/RFA, June-1 designation, compensatory rounds 3–7; use one split release, post-round-seven comp picks | `engine/movement.py`, `engine/contracts.py`, `engine/transactions.py` implement older rights/tags, June-1, rounds 3–7 | Remove from Edition 8.15 execution path, retain only legacy history if needed; rewrite transactional tests |
| P0 | §12 equal-chance lottery for returning ambassadors, identity follows original pick | `engine/rules.py` uses weighted 36-ball lottery for just-exiled clubs | Replace lottery pool, weights, order and ownership semantics |
| P0 | §12 league trading Tue 00:01–Fri 23:59 during competition through Friday before numbered week 9 | `transactions.py` documents Tuesday after week 9 deadline | Rebuild interval-based trade eligibility using league UTC |
| P0 | §11 rookie deals: four-year fixed salary R1–R7; rookie reserve for unmade owned picks | Existing rookie scale and contract-bonus design | Rebuild draft signing and reservations with exact slots/years |
| P1 | §7 Ambassador Tour 7 rounds calendar weeks 1/4/8/11/15/18/22; all-star Bowl C−7 | `rules.py` sets Ambassador weeks 1–7 and Bowl week 8, two best clubs | Replace tour calendar, international venue draw and HC ranked-choice All-Stars |
| P1 | §3 Coronation venue seeded among nine eligible club stadia; 40-year no-repeat restriction | `rules.py` says neutral site | Implement site eligibility, June selection and potential finalist home ground |
| P1 | §10 home kicks first, away second, specific touchback and overtime conventions | `game_engine.py` legacy football model | Explicit rule version in game engine; verify special teams, penalties, possession |
| P1 | §11 48 position-specific required roster spots including LS; permanent position, legal jersey blocks and stewardship | `engine/positions.py` / `rosters.py` older 11-group abstraction | Expand positions and roster validation without losing player IDs |
| P1 | §13 creator-only female characters, hidden 1–99 attributes, no stored OVR, 672-draftee class, bounded pools | `engine/cards.py`, `players.py`, `prospects.py` create/derive cards in several places and use OVR | Separate creator module, public views, stable streams, quota/pool rules |
| P1 | §14 fan accountability and three-year CEO election, expected wins computed once after cuts from public production | Older `staff_cards.py`, `finance.py`, `ceo_card.py` use CEO tenure/recall arrangements | Rewrite decision windows and information visibility |
| P1 | §15 59 halls, Tiara 53+6 staff, eligibility five credited seasons | Older Hall/honours mechanisms | Align awards, participation and immutable historical record |
| P1 | §16 website six tabs, strictly read-only | Existing site has live pause/resume control | Remove public viewer control surfaces from official Edition 8.15 site; admin operations must remain separate |
| P1 | §17 full 0.05s traces, atomic handoff, reserve/commit, versioned event log | `engine/store.py` and `live.py` replay/reveal prior drives from seed | Define new authoritative event schema and do not leak future data |
| P1 | §18 Edition 8.15 reference validator and tests in separate `DFLv2` layout | `engine/check_rulebook.py` passes older 54-row rulebook | Import or independently reproduce Edition 8.15 validator before treating 'green' tests as compliance |

## Areas provisionally retained

- 48 clubs, two conferences, eight divisions, 40 active and 8 in exile.
- 18 regular-season games per active club and 360 total, with 9 home and 9 away.
- Seven postseason teams per conference and a 13-game playoff.
- Seven-game Ambassador round robin and 28 Tour games, though venues/timing/Bowl are changed.
- 53-person main roster, 16 practice squad, 90 preseason ceiling and seven draft rounds, though composition, pricing and rights are changed.
- Seeded deterministic execution and persistent character identities as architectural goals. Existing implementations require verification under the new schema.

## What is verified vs not

**Verified by source inspection:** Edition 8.15 explicitly says it supersedes older artifacts. The named `main` files contain conflicting rules and mechanisms. The older `reports/rulebook_status.md` reports 54 built/0 differing/0 missing only against its own 2026-10-06 rulebook, not Edition 8.15.

**Not verified:** execution of any checks, full source-tree audit, correctness of the separately referenced DFLv2 validator, complete monetary migration, deterministic save compatibility, statistical calibration, venue availability, official production safety, Edition 8.15 document checksum. All are required for a release-quality baseline.

## Explicit open-item register from Edition 8.15 §20

There are 18 recorded items. They are not licenses for the builder to silently add constitutional rules. Distinguish:
- **May remain model/calibration open while rulebook freezes:** analytics definitions, play/physics catalogue details, market-clearing and aging curves, Bowl repair mechanism, real/sim clock pacing, tie rate, cap pre-cut count calibration, exile-return fairness, attribute distributions, visible aging.
- **Requires explicit normative resolution or acceptance of existing provisional rule:** stable IDs (§19); NFL-derived emergency fill-in parameters; assumptions in standings cascade; offseason dates; the rule/contract effect of fan sentiment/recall; leader pool and hiring.
- **Closed:** jersey-number defaults as recorded in §20 item 18 unless deliberately amended.

The user's current instruction that real NFL changes never alter DFL resolves the *future NFL amendment* question; it does **not** itself close these other items.

## Recommended executable migration order and gates

1. **Guard:** pin Edition 8.15 source, hash, and reference NFL snapshot; add compliance manifest with every rule ID/source/implementation/test. No green badge may derive solely from legacy rulebook.
2. **Pure rules:** implement Edition 8.15 tables, calendar, standings, eight-year beds, Tour and venue fixtures with golden tests independent of games. Verify 150 seasons plus eight-year cyclicity.
3. **Economy/transactions:** replace old cap/rights/trading/draft/waivers atomically, with conservation, viability and no-double-spend tests; keep legacy save migration isolated.
4. **Character/authority:** align creator, role permissions, election/recall, roster positions, jersey IDs and visibility tests.
5. **Game interface/persistence:** align football rule hooks, season handoff and event visibility before any official public release.
6. **Re-run entire FAST and SLOW tiers, rewrite outdated assertions to Edition 8.15 and identify uncovered rules. Keep historical test results separately labelled 'legacy.'**

## Phase 1 completion criteria — NOT YET MET

- [x] Identify authoritative edition and its supersession order.
- [x] Identify major source-confirmed conflicts and a migration sequence.
- [x] Record NFL freeze and normalization policy.
- [ ] Produce a complete stable-ID rule manifest for every normative requirement in §§0–20.
- [ ] Resolve normative open items or explicitly accept provisional values.
- [ ] Replace/disable contradictory legacy execution paths.
- [ ] Implement independent Edition 8.15 structural validation; rerun passing tests.
- [ ] Freeze Edition 8.15 baseline with reproducible hash and CI evidence.

**Release gate: blocked.** This audit is a migration blueprint, not a claim that Phase 1 or Edition 8.15 is implemented. Do not merge into production until audited changes and tests actually match the design.

## Progress checkpoint — 2026-10-26

- Pinned exact 82,148-byte Edition 8.15 source as `docs/DFL_Design_Document_Ed8.15.md`; independently recomputed its declared SHA-256 and obtained the exact declared `6a77c043...` digest.
- Created `docs/ed815_rule_register.json` with 158 source-anchored **coarse** clauses across §0 and §§1–19, plus `tools/check_ed815_register.py` to reject missing/altered anchors and source checksum drift. The checker syntax was parsed successfully. Full execution against a local working checkout is still pending.
- The register is **not yet atomic**: some entries include several independently enforceable requirements. §5/§6/§7/§8's tabular reference data remain pinned in the document but are not each separately identified as rule IDs; §20's open items remain unresolved.
- No legacy executable rules were replaced and no engine regression suite was run. The new validator is not yet wired into CI. `main` remains unchanged.

**Rule status:** constitutional source pinned, early compliance map created; Edition 8.15 engine compliance **not established**. Do not declare Phase 1 frozen.

## Second checkpoint — isolated standings kernel

- Added `engine/ed815_standings.py`: tie games contribute to statistical games/points/differential but not wins/losses or opponent lists; wins before win percentage; context-dependent division/conference steps; SOS, point differential, SOV and seeded deterministic terminal draw; playoff seeds and next-year exile seed handoff.
- Added `engine/check_ed815_standings.py` with focused tests for those behaviors. An initial test fixture incorrectly assigned a read-only calculated field; the fixture was corrected, and the checks passed when run against the new source in an isolated Python process.
- Added `engine/check_ed815_reference.py` and enrolled both new checks into the fast-test tier in `engine/run_checks.py`.
- **Not integrated** into `engine/standings.py`, `engine/tiebreak.py`, `engine/season.py`, or the live runner. Existing simulation output still uses older rules until an explicit migration. Focused tests are not a substitute for independent historical/schedule/cycle and multiseason checks.

## Third checkpoint — calendar, bed rotation and fixture template

- Added `engine/ed815_calendar.py` with last-Sunday Coronation anchoring, 27-week calendar, three active-club breaks, 19 numbered fixture weeks, postseason offsets, seven international Tour windows, canonical eight-year bed rotation and seed-to-bed assignment.
- Extracted `data/ed815_fixture_beds.csv`: the exact 360 games in §6 rewritten from Season 1 city labels into permanent home/away bed-rank IDs, so later years substitute each season's divisions and ranks without inventing new matchups.
- Added `engine/check_ed815_calendar.py`, enrolled in the fast tier. In a memory-backed Python test (without modifying a local checkout), verified 300 calendar years, 400 successive bed rotations, and 16 seasons of fixture totals, division/conference composition, four double-played divisional opponents, one bye in weeks 15–19 and kickoff-slot points of 33–38. Tests passed after correcting one incorrect test assertion about the distance of the conference-block flip.
- **Not yet verified:** the full independent Edition 8.15 validator; random reseeding across 150 realistic season standings; local runner integration; live/website timing and pending offseason transactions. The new calendar/fixtures are isolated reference implementation, not production wiring.

## Fourth checkpoint — recursive 150-season structural test

- Added `engine/ed815_cycle.py`: a strict season boundary that consumes exactly one result for each of 360 immutable fixtures, checks participants, computes §3 records, playoff seeds and division rankings, then assigns returning ambassadors to seed 5 and exiles the fifth-place active clubs. The following season is rebuilt through the eight-year bed rotation.
- Added `engine/check_ed815_cycle.py` to the FAST tier. Tested incomplete/invalid scores and mismatched results are rejected, reversed result input produces identical seeds and playoff qualification, and a 150-season synthetic score sequence passes 48-club identity conservation, eight division exchanges each year, 40 active/8 exiled invariant, fixture legality and seven playoff slots per conference.
- Test scores are deterministic *fixtures* and carry no NFL statistical calibration claim. The handoff currently covers only structural state, **not** people, contracts, money, injuries, honors, event persistence, simulated time or a true football engine.
- Focused in-memory Python execution passed. A full branch checkout, complete FAST/SLOW suites, integrated historical archive comparisons and production clock tests have not been run.

**Phase 1 still blocked:** contradictory legacy systems exist; source register is coarse; Edition 8.15 has normative open items. Structural reference modules cannot be substituted into production until remaining domains are reconciled.

## Fifth checkpoint — financial guardrails and trading intervals

- Added isolated `engine/ed815_cap.py`: decimal-precise cap projections at $1,000/year, highest 69 contract hits until cut and all afterward, $25 reserve, $5 minimum replacement cost, strict-dead ceiling $735 (prorated current-year minimum), rookie-pick cap holds, future-year transaction guards and no rollover.
- Added `engine/check_ed815_cap.py`, focused boundary/invalid-input testing and 10,000 deterministic randomized cap cases; passed after fixing a test fixture whose booked-dead balance had been incorrectly excluded from its strict liability.
- Added `engine/ed815_market.py`: UTC-only off-season trade opening and the Tuesday 00:01–Friday 23:59 competition window ending before numbered week 9. The end minute is treated inclusively; added `engine/check_ed815_market.py` and passed 300 years of boundary cases.
- All four new files are reference modules and their checks are enrolled in FAST. Full branch execution of the entire FAST tier remains outstanding.
- **Not built here:** actual per-player contract-year ledger, signing bonus proration/acceleration, guarantees, release/restructure and split-release generation, two-phase reserve/commit, minimum-positional lineup, rookie ownership reservation updates, waivers, draft compensatory picks and real trade settlement. Inputs to `ed815_cap.YearProjection` must come from those future mechanisms, so its green checks are not evidence that club finances are now correct.

## Sixth checkpoint — contract ledger and bonus conservation

- Added isolated `engine/ed815_contracts.py` covering 1–5-year contract shapes, minimum base salary, year-specific guarantees, signing-bonus proration, pre-payment-year releases, the one split-release choice, and transfers in which the receiving club takes unpaid base/guarantees but **never** the already-paid original signing bonus. Both clubs' cap/future-year projections must validate before a trade result is returned.
- Added `engine/check_ed815_contracts.py` to FAST. Tests check release and trade dead-money charges, split release exclusivity, minimum and maximum term boundaries, cap/viability rejection, invalid future-year commitments, input immutability and 5,000 randomized signing-bonus conservation cases.
- First run exposed a genuine numeric accounting problem: equal annual bonus divisions involving repeating decimals did not always add exactly to the original amount. Fixed by assigning the exact residual to the final contract year; rerun passed. This is an implementation rounding policy, not a new DFL rule.
- The contract reference operates at the beginning of a payment year. **Not yet implemented:** paid-week accrual and midseason prorating, year-crossing transaction clock, guaranteed-base offsets on midseason release, any negotiated market, contract-year shape escalation by season, full 53/16 roster counts, real rookie scale contracts and holds, waiver claims, pick compensation, persisted atomic reserve/commit, or production engine replacement.
- This is an isolated submodule with limited focused tests, not proof that the production financial system complies with Edition 8.15.

## Seventh checkpoint — waivers and draft-pick identity

- Added `engine/ed815_waivers.py`: releases after fewer than four credited seasons enter a one-day waiver claim interval; vested veterans enter free agency directly; claimant priority stays at last draft order through four league weeks, then is supplied by current Edition 8.15 standings/Tour ordering. Claim settlement follows priority and skips failing legal-eligibility checks. It does not mutate a club ledger.
- Added `engine/check_ed815_waivers.py`: clock and service boundary cases plus 10,000 randomized claim scenarios passed.
- Added `engine/ed815_picks.py`: 7×48 ordinary pick ledger retaining original-club identity, owner, slot, reserved/used status; transfer restricted to the next three incomplete drafts; deterministic equal-chance eight-returning-Ambassador lottery independent of pick ownership.
- Added `engine/check_ed815_picks.py`: 10,000 seeded lottery permutations and 10,000 randomized transfers, plus reservation/selection boundary checks, passed. Lottery frequencies were checked as a sanity bound, not a formal randomness proof.
- Both suites added to the FAST tier. These are provisional pure rule kernels only.
- **Pending:** the standings-to-waiver ranking (including Tour clubs in prior draft bands), an atomic claim that transfers an actual player/contract and cap reservation, exact 336-pick class signing and rookie cap holds, two-per-club post-R7 compensatory awards, trading windows combined with financial settlement, and full production integration.

## Eighth checkpoint — post-round-seven compensation and rookie holds

- Added `engine/ed815_compensation.py` and `engine/check_ed815_compensation.py`. A qualifying free-agent move requires first-year base ≥$75, and a qualifying loss additionally requires top-quarter snap share at the departing club. Qualifying signings net against departures highest-first. Unmatched losses compete for at most 2 post-round-seven compensatory selections per club and 48 league-wide, ranked by qualifying first-year base with previous draft order breaking club ties.
- Seven ordinary rookie salary rates are $25/$18/$14/$11/$9/$7/$5, with $5 for compensation and a recorded $35 first-round option. Unmade picks reserve the relevant current-year cap number for their **current owner**, not original club; transfers move the reservation.
- Added `select_and_sign_rookie`: one pure validated action changes a pick from unmade to selected and replaces its reservation with the actual four-year fixed rookie contract. Extended `ed815_contracts.sign` to compare before/after cap holds rather than double counting during replacement.
- Focused test suites passed: 2,000 randomized movement sets, netting/ordering/cap bounds, cap-neutral selection at exactly $1,000, and previous 5,000 contract-conservation tests after signature change.
- **Document wording conflict:** §11's rookie-reserve passage mentions “rounds 8 and 9 at the round-7 scale,” while §§0/12 repeatedly define exactly seven ordinary rounds and compensation after round seven. No new eighth/ninth ordinary rounds were created; the reference maps post-R7 compensation to the $5 rate. This is a recorded source ambiguity to resolve at freeze.
- Still missing: salary-year market settlement, athlete eligibility and actual snap-share computations, compensatory award entry into the permanent tradable pick ledger, selection/reservation processing for compensatory picks, first-round option exercise, and all production integration.


## Ninth checkpoint — atomic roster and trade settlement

- Added `engine/ed815_roster.py`: durable player IDs, immutable official positions, main/practice/camp/injured/suspended categories, 90-player ceiling, 53 main and 16 practice limits, maximum six practice-squad veterans with more than two credited seasons, and all 48 mandatory positional places (including the alternative HB 2 + FB 1 configuration). The exact positional coverage check is performed at final cuts, **not on every midseason trade**, because §11 explicitly permits temporary shortfalls.
- Added `engine/ed815_transactions.py`: pure, all-or-nothing two-club proposals containing multiple named players and ordinary draft picks. First stage builds both destination rosters, owned picks, incoming unpaid contracts and outgoing original-club uncharged-bonus acceleration; second stage validates both roster limits, cap reservations, current/future strict-dead viability, and the trade clock. No intermediate leg is committed or rejected for a transient cap spike when the complete bundle would pass.
- Fixed an integration bug found by a focused execution: `ed815_calendar` season **ordinal** (Season 1 = civil 2000) must be translated to calendar year before contract/draft accounting.
- Added `engine/check_ed815_transactions.py` to FAST and passed an isolated in-memory execution covering two-way swaps, unilateral eleven-player viability, duplicate/missing players, duplicate picks, draft holds, closed-market rejection, final-cut positional coverage, practice veteran limit, reversible original data and bundled cap enforcement. **This is not a full branch FAST-tier or engine integration run.**
- **Known limitations:** This transaction interface does not yet trade post-round-seven compensatory picks; it models start-of-contract-payment-year economics rather than weekly earned-base settlement; two-phase persistent locks/commit are not implemented. The off-season trade opening is still the earlier provisional February 1 proxy in `ed815_market`, pending the Bible's exact global close of leadership hiring. The normal 11-player check is optional at game-day validation, and cannot substitute for full position-specific on-field lineup checks.

**Phase 1 remains open.** The new reference components have not replaced the contradictory legacy production execution paths.


## Tenth checkpoint — compensatory trading and optimistic reserve/commit

- Expanded `engine/ed815_transactions.py` so a single trade bundle can move named players, ordinary picks **and** post-round-seven compensatory picks. The original compensation identity remains unchanged as its owner changes; reserved/used compensatory selections cannot transfer; duplicate picks are rejected. Cap projections include the post-trade rookie salary holds of both ordinary and compensation picks.
- Corrected a substantive calculation defect: the after-state rookie-hold projection previously tested `y == season` (a season ordinal) rather than `y == year` (the civil accounting year). A regression case now proves that a $25 incoming round-one reservation cannot quietly raise an over-cap club.
- Added `engine/ed815_settlement.py`: an isolated **in-memory optimistic** state machine for propose → reserve → commit or cancel. The snapshot's revision and SHA-256 fingerprint are compared at commit; replays, stale revisions and intervening mutations are rejected. The full bundle is financially and temporally revalidated at commit, which advances the revision and appends an event record only on success.
- Added `engine/check_ed815_settlement.py` and extended `engine/check_ed815_transactions.py`, both enrolled in FAST. Focused in-memory runs passed. No entire branch FAST/SLOW run, database fault-injection or concurrent process test was executed.
- **Important distinction:** This is NOT yet a true persistent atomic database commit or a durable lock. The snapshot contains in-memory dictionaries, so process crashes, multiple workers, or races require a transactional storage adapter with compare-and-swap and durable event append. Current trading clock also retains the provisional February 1 opening until leadership hiring completion is specified. The reference interface now returns (clubs, ordinary picks, compensation picks), and no production callers are connected to it.

**Phase 1 remains open; production `main` is not changed.**


## Eleventh checkpoint — SQLite-backed atomic transaction persistence

- Added `engine/ed815_storage.py`: explicit JSON serialization/deserialization of contract, roster, ordinary pick, compensatory pick, settlement reservation and event states, with a schema-version field and Decimal values represented exactly as strings.
- The store uses a single SQLite `BEGIN IMMEDIATE` transaction with a checked revision update. Reservation, commit and cancellation save complete snapshots. A successful commit appends a unique-token event record in the **same SQLite transaction** as the state update. For file-backed databases the adapter requests WAL journal mode and `synchronous=FULL`.
- Added `engine/check_ed815_storage.py` to FAST. An isolated **in-memory SQLite** run passed JSON round trips, reservation replay/stale revision rejection, event uniqueness, and rollback when a deliberately failing SQL trigger aborts the event insert after the state update. Both state and event records remained unchanged after that failure.
- A **real on-disk close/reopen test** is checked in but **could not execute in this sandbox**: the execution environment blocks temporary-file creation. The full check thus has NOT been observed to pass end-to-end here; only the in-memory subset was executed. Re-run on writable CI/checkout before any production claim.
- This adapter remains deliberately isolated and scoped to a two-club trade snapshot; it is **not connected to the live league state**, is not a global 48-club transaction database, does not verify real multi-process races, and does not solve recovery/orphan-reservation policy or leaguewide draft/character locking. The trading-opening timestamp is still provisional pending global hiring-close rule wiring.

**Phase 1 remains unfrozen.** No changes were made to production `main`.
