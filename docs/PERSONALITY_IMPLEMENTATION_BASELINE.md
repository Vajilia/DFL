# Personality implementation baseline (Phase Zero)

**Status:** investigation report. Documentation only. **No personality mechanics are implemented by this document or its pull request, and no gameplay behavior, rulebook line, fairness band or production state was changed.**

**Base commit:** `84ce78f8d6c969448f6914894a3bc94827ca5c8d` (`main`, merge of PR #37; `step6-rebuild` points at the same commit). Report written 2026-10-17 on branch `personality-baseline`.

**Labels used throughout.** **Verified** = read in the source at the base commit, or a command that was run (with its result recorded in section 9). **Untested** = read but not exercised. **Proposed** = a recommendation that needs the Commissioner's approval. Where this report disagrees with an older document, the source wins and the disagreement is listed in section 1.

**The five meters are not named here.** Their names and meanings are not approved. Everything below refers to them as "the five meters" or `meter[1..5]`. The candidate names mentioned in the brief (Ambition, Risk Appetite, Loyalty, Self-Control, Adaptability) are discussion candidates only and are not used as identifiers anywhere in this plan.

---

## 0. The short version

1. **Nothing in the repository today implements the new contract.** Every person has an older personality system: a soul (two archetype labels plus a "family"), a one-of-four `trait` string, `wants`/`fears` text, `pressure` thresholds, plus a self-image (`ego`, `perceived`, `temper`). None of it is five numbers from 1 to 100.
2. **The production autopilot uses almost none of it.** Of the 25 decision kinds, the autopilot's default rule reads personality-like numbers in exactly two places, both for CEOs (`OwnerCard.ratings`: patience sets the firing threshold, ambition sets the boycott reply and reinvestment share). Players, coaches, GMs, fans and media have no personality in their autopilot. The only code that keys behavior on trait *words* is the test stand-in agent (`agents.py`) and a few text/relationship tables. **Verified.**
3. **The hidden-information boundary is good at the agent door and weak everywhere else.** `DecisionPoint.public()` is a clean allowlist of one bounded card view. But the `trait` word is published to every spectator in the live feed and the site, it is shown to other characters in several contexts, and the whole card is written to disk with `dataclasses.asdict`. A hidden value stored as a card field would be saved, exported and (if anyone widened a serializer) published automatically.
4. **A hidden X-factor cannot be derived from the seed alone.** The repository is public, `/live/meta.json` publishes the league seed (verified live: seed 7, rules 5), and every card is a pure function of that seed. Anyone can clone the repo, run the generator, and read every X-factor, including those of players not yet drafted. Principle 5 needs a **secret salt** that is never in the repo or the feed. This is the largest design finding and it must be approved before coding.
5. **The test baseline is in section 9 with the numbers actually obtained.** The brief and PR #40 both say "13 fairness bands"; the code defines **15** (`rules.FAIR_COMPETITION_BANDS`). The fast-engine bands are asserted by `check_phase2.py` inside the slow tier (16 leagues × 48 seasons); the drive-engine bands and the error-bar verdict table exist only in the separate `fairness.py --write` study, which is in neither tier.
6. **Phase One can be done without changing a single game result**, because cards draw only from private streams. The proof is the existing golden fingerprints, which must stay byte-identical.

---

## 1. Repository state (verified 2026-10-17)

| Item | Finding |
| --- | --- |
| Repository | `Vajilia/DFL`, **public** (`gh api` reports `private: false`) |
| `main` / `step6-rebuild` | both `84ce78f`; `step6-rebuild` is still the branch the deploy scripts default to |
| Open pull requests | #38 (WORK_LOG for the Chronicle deployment), #39 (chalkboard view), #40 (personality contract audit). None merged by this work |
| Branches on origin | 19, including `chalkboard`, `chronicle`, `audit/personality-decision-contract-20261017` and a number of `log-*`/`fix-*` branches that look like finished housekeeping work (whether each is merged was not checked) |
| Production (public feed) | `/live/meta.json` returns `seed 7, rules 5, engine_commit fd6555f, pacing blocks, parity tight` (the commit recorded when the league was created). The server checkout and any later update are not verified here; `main` has moved on since (Chronicle, checks) |
| Live driver | `live.py` never sets `lg.driver`, so the live league runs on the **autopilot** (`PolicyDriver`). No `StandIn` or other agent is in the live path |
| Live restart behavior | a restart **replays every past year from the seed**; it does not load a saved state. Any change to an engine draw or an autopilot rule changes the replayed history unless gated by a `rules` version (the feed's `rules: 5`) |

**Stale documents found (do not rely on them):**
- `PROJECT_STATUS.md` says `main` is at `fd6555f` (orientation snapshot of 2026-10-15). It is `84ce78f`.
- `docs/WORK_LOG.md` says "Last updated … on `main` at `9961ff6`", "the fast tier passes (31 of 31)", and "13 fairness bands". The fast tier now lists **32** scripts, the slow tier **24** (56 `check_*.py` files in all, plus `check_stage.js`), and the code defines **15** bands.
- `reports/verification_step6*.md` say "all 13 fairness bands inside". That was probably true when written; the WORK_LOG entry for 2026-10-12 records "the Commissioner's exile standard as two measured fairness bands", which matches `returner_top3_in_3` and `returner_playoff_first` being the two extra bands (inferred; not traced through git history).
- `docs/WORK_LOG.md` open item 0 says the fairness bands are "not part of either check tier" and have not been run since PR #14. Partly stale: `check_phase2.py` (slow tier) runs `fairness.run("fast", range(100, 116), 48)` and asserts all 15 bands, and the slow tier passed 24 of 24 on PR #30's branch after PR #14 according to the log. What is still not covered by a tier is the drive-engine study (`fairness.py --write`, 6 more leagues) and its verdict table.

---

## 2. Critical review of PR #40 (`docs/PERSONALITY_DECISION_AUDIT.md`)

PR #40 is a 66-line, documentation-only proposal. It is honest about its scope ("a scoped source audit, not a claim that every repository file has been inspected"), correctly says the five meters must not be invented, and correctly says legacy rules should not be kept for their own sake. Its four-step outline (inventory, safe creation, decision integration, falsification) is a reasonable skeleton. Where it falls short, verified against the source:

| # | Gap or error in PR #40 | What the source shows |
| --- | --- | --- |
| 1 | "the 13 fairness bands" | The dict has **15** entries (`python -c "import rules; print(len(rules.FAIR_COMPETITION_BANDS))"` → 15). Its acceptance criterion cannot be checked as written |
| 2 | Treats "agent policies" as the place personality lives and the "stand-in" as the thing to replace | The stand-in (`agents.py`) is test-only. The live autopilot is a different code path (`PolicyDriver` returns `dp.default`, computed by each builder). The only personality-like inputs the autopilot reads are `OwnerCard.ratings` for CEOs. PR #40 never mentions this |
| 3 | Says nothing about the public seed | The whole league, and any future hidden value derived the usual way, is reproducible from the public repo and the public `seed`. "Neither the X-factor flag nor its number may be exposed" is unachievable with seed-derived generation |
| 4 | "Durable historical persistence is an Alpha concern" | Persistence already exists and is the main leak path: `store.py` writes every dataclass field of every card into the `cards` table, into whole-league pickles, and into `export_card`. A new card field is persisted on day one |
| 5 | Lists "P2: safe creation" and "replace superseded rules" together | Those are different risk classes. Creation is zero-behavior-change and provable by the golden fingerprints; replacing rules changes outcomes and needs the fairness study. They must be separate pull requests (section 8) |
| 6 | "Rerun … the 13 fairness bands after any behavioral change" | Only part of the bands is covered by the tiers: `check_phase2.py` (slow tier) asserts all 15 on the fast engine. The drive-engine run (6 leagues) and the "inside / edge / outside" error-bar verdicts live in `fairness.py --write`, which no tier runs. Which of the two a change must rerun should be named in the PR |
| 7 | Does not distinguish "character" from "decision-maker" | Fanbases and media outlets are cards with `wants`, `fears`, `ratings`, `pressure`; the DFLPA representative, Commissioner and Competition Committee are not cards. "Every in-world character" needs a definition (section 3.3) |
| 8 | "X-factor 1–200, 100 normal" | This implies an X-factor could lower a meter (below 100). The brief says it *amplifies*. These are different designs and the choice changes the distribution and the "harmful" mechanism. Needs a ruling (section 7, question 5) |
| 9 | No mention of lazy card creation | Player cards are not created with the player. `cards._touch` builds them the first time `ensure_cards` runs. "At creation" must be defined (section 3.2) |
| 10 | No mention of determinism hazards | `card_seed = hash(rng.getstate()[1]) % 2**31` (`league.py:168`) relies on CPython's tuple hash. It is stable today but is not a documented guarantee across Python versions |
| 11 | No hidden-information test design | A canary test (plant a recognizable hidden value, search every output for it) is the only way to prove "no leak"; PR #40 only lists "no hidden-field serialization" as an invariant |

Verdict: keep PR #40 as the statement of intent; do not treat it as the inventory. This report replaces its inventory and its sequencing. PR #40 was not modified and not merged.

---

## 3. Character inventory

### 3.1 Character-type matrix (verified)

| Category | Class (file) | Constructor | Identity | Created | Ends | Persistence | Agent-facing view | Public (site/feed) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Player | `PlayerCard` (`cards.py`) hung on `Player.card` | `make_player_card(seed, p, year)` via `cards._touch` ← `ensure_cards` | `pid` (league id source `IdSource`), card stream key `(card_seed, "player", pid)` | **Lazily**: `init_league_cards` gives every founding player a card when the league is wired; after that `ensure_cards` (called from `season.py` at each season end) gives a card to every player who has appeared since. Not at `Player` construction | `retired` flag; card kept in `lg.retired_players` | `cards` table row (`asdict` JSON), pickle snapshots, `people` row incl. `trait` | only when the player is a decider: `_PlayerSeat` (contract tables) and interview candidate views | name, age, hometown, **trait**, bio (roster rows, `site_export._player`) |
| Head coach and coordinators (one pool) | `CoachCard` (`cards.py`) | `make_coach_card(seed, cid, team_id, age)` | `cid`; stream `(card_seed, "coach", cid)`; non-hired candidates numbered from 20000 | at league founding, hiring slate, character creator | `retired`; between jobs they sit in `lg.free_coaches` | `cards` row, pickle, `people` row | full `card_view` as decider; `_perceived` blurred views as candidate/subordinate | name, **trait**, hometown, age (club page staff list) |
| CEO / owner (and recall candidates) | `OwnerCard` (`staff_cards.py`) | `make_owner_card(seed, oid, team_id, age, …)`; `fan_media_cards.new_ceo` | `oid` | founding, recall elections, candidate slates | `status`, tenure end, recall, sale | `cards` row, pickle, `people` row | full `card_view`; shown to candidates in interviews with **trait** and a noisy `patience` | name, **trait**, hometown, age |
| GM | `GMCard` (`staff_cards.py`) | `make_gm_card(seed, gid, team_id)` | `gid` | founding, hiring slate | `status`, retirement; pool `lg.free_gms` | `cards` row, pickle, `people` row | full `card_view`; head coach sees `personality=g.trait` (`relations.gm_note`) | name, **trait**, hometown, age |
| Fanbase | `FanbaseCard` (`fan_media_cards.py`) | `make_fanbase(seed, team_id)` | `team_id` (one per club) | founding, one per club | never (club-bound) | `cards` row, pickle | `card_view` for `fan_demand` | not directly; approval/boycott shown on club pages |
| Media outlet | `MediaCard` | `make_outlet(seed, mid, kind, team_id, team_name)` | `mid` | founding; outlets are founded and fold | `status` (folded) | `cards` row, pickle | none (media do not decide; they act through the engine's deterministic press model) | outlet name and stories only |
| DFLPA representative | **no card** | a guard inside `contracts` tables (`self.rep`) | none | n/a | n/a | not persisted | not a decider | named in table text |
| Commissioner | human operator | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| Competition Committee | seats held by CEO cards | `governance.annual_meeting` | uses `oid` | yearly | yearly | in league state | n/a | n/a |
| Prospect (draft class) | a dict `Player.origin` from `prospects.make_origin`, not a card | `PR.ensure_origin` | `pid` | with the player | with the player | in the pickle / player row | GM sees blurred grade and stat line only | college, hometown shown after draft |

All persons that decide, plus fanbases and media, are therefore **six card classes in four modules**, built by six constructors that each take the league `card_seed` and use their own `random.Random("-".join((seed,)+key))` stream. **Verified**: the card constructors never touch `league.rng`.

### 3.2 When is "creation"? (design-critical)

- Coaches, CEOs and GMs are generated whole, at the moment they enter the world, from their own id.
- **Players are not.** `Player` objects are made by the player generator, the draft and founding using the engine's stream; the card is attached later by `ensure_cards` (`cards._touch`): at league wiring for founding players (`init_league_cards`), and at each season end (`season.py:177`) for everyone who has appeared since. A player drafted in year 5 gets her card in that year's end-of-season sweep, not when she is drafted.
- "Roughly 5% of characters get an X-factor at creation" therefore needs a rule for players: attach it in `make_player_card` (the first moment the person exists as a character), keyed by `pid` only, never by call order. **Proposed.**

### 3.3 What counts as a "character" for the five-meter contract (needs a ruling)

The brief says "every in-world character". The code has three kinds of thing that could be called characters:
- **Individuals who make choices** (players, coaches, CEOs, GMs): clear.
- **Collective actors** (a club's fanbase, a media outlet): cards with their own `wants`, `fears`, `ratings`, `meters`, and a decision (`fan_demand`). They are not individuals, but they are treated as decision-makers by the guard.
- **Non-card roles** (DFLPA representative, Committee): not characters today.

Recommendation: apply the five-meter contract to the four individual types; treat fanbases and media as *institutions* with their existing `ratings`/`meters` unless the Commissioner says otherwise. If the answer is "fans are characters too", a fanbase would get five meters and a 5% chance of an X-factor like anyone else, which is a strange thing for a crowd. **Question 4, section 7.**

### 3.4 Personality versus everything else (field classification, verified)

| Field(s) | On | What it is | Class | Consumed by the engine or autopilot? |
| --- | --- | --- | --- | --- |
| `archetype_pos`, `archetype_neg` (players); `soul_pos`, `soul_neg` (staff) | all individuals | the best and worst of the person's attributes at birth, used as labels | **identity / skill shape** (athletic or professional archetype) | `apply_soul` pulls ratings back toward the soul shape (skill development) |
| `shape`, `anchor` | all individuals | the person's fixed profile of strengths around her overall | **skill shape** | yes: growth and `apply_soul` |
| `potential` (staff) | staff | ceiling for growth | **skill** | yes: `living.grow` |
| `family` | all individuals | one of the temperament families; fixes which four `trait`s are allowed | **legacy personality constraint** | indirectly: gates `trait` |
| `trait` | all individuals | one word chosen from four allowed by the family (`express`/`trait_scores`; can shift between seasons, `personality_shift`) | **legacy personality** | autopilot: only through `pressure`; stand-in: heavily; `relations` CLICK/GRATE; interaction quotes; GM–coach pairing |
| `wants`, `fears` | individuals, fans, media | lookup text from `card_pools.TRAITS[trait]` | **legacy personality (presentation)** | text in prompts and scenes; not read by rules |
| `pressure` (dict of thresholds) | individuals, fans, media | per-situation stress limits derived from `trait` (`_pressure`) | **legacy personality (behavioral)** | **yes**: `finance.subsidy_willing`, sale votes (`finance.py:265`), `interactions` relationship scaling (`pressure["loyalty"]`, `["media"]`, `["recall"]`) |
| `ego`, `temper` | individuals | self-image offset; per-trait mood jitter | **legacy self-perception** | `perceived` ratings; `temper` jitters `trait_scores` |
| `perceived` | individuals | how she sees her own attributes (truth plus ego plus noise) | **knowledge / belief** (not personality) | shown on cards ("sees herself at"); `confidence_gap` |
| `ratings` (staff, owners, fans, media) | staff and collectives | attribute scores. For coaches/GMs these are **skills**. For CEOs they are patience / ambition / involvement / popularity / business, which behave like personality (below) | **skill** (coach, GM, media); **mixed** (CEO); **expectations** (fans) | yes, heavily |
| Player ratings | `Player.ratings` (not on the card) | football attributes | **skill** | yes: the game engine |
| `esteem`, `standing`, `honors`, `history` | individuals | reputation, Hall of Fame record | **reputation** | yes: recognition, hiring halos, hall votes |
| `relationships` | individuals, fans, media | per-pair feelings, −100..+100 | **relationship state** | inform only ("No engine rule reads them"), except `relations.CLICK/GRATE` seeds them from trait pairs |
| `heat`, `approval`, `capital`, `boycott`, `memories`, `lean_years`, `exile_press` | coaches, GMs, owners, fans | pressure on the job, fan mood | **situational state** | yes |
| `OwnerCard.meters` (`rapport`, `standing`, `legacy`; `ceo_card.METERS`) | CEOs | the CEO's relationship with the fans and board, scoped to a tenure | **CEO-specific situational state** | yes: `ceo_pledge`, `ceo_boycott` |
| `FanbaseCard.meters` | fans | evolving, fading franchise moods | **collective state** | yes |
| `career`, `decision_log`, `notes` | individuals | event history; actions taken; agent's own notes | **history** | `notes` shown back to the same agent; never read by the engine |
| `bio`, `profile`, `enriched` | players | written backstory | **presentation** | public |

**Key point on `OwnerCard.meters`.** The three CEO meters (rapport, standing, legacy) are not personality. They are tenure-scoped situation measures, so they should **stay** and must not be silently renamed into, or counted as, the five meters. The thing that *is* personality-like on a CEO is `OwnerCard.ratings` (patience, ambition, involvement, popularity, business). Those five are the closest existing analogue to "decision-driving personality meters". Because they are literally five and are read by the autopilot, a decision is needed on whether they are *replaced by*, *mapped onto* or *kept beside* the new five. Keeping both would give CEOs ten personality-like numbers and break "exactly five". **Question 6, section 7.**

A naming hazard: `OwnerCard.ratings` already has a key called `ambition`. If any of the approved meters is also called Ambition, there will be two different numbers with the same name on the same card.

---

## 4. Decision-architecture inventory

### 4.1 Machinery (verified)

- A choice is a `DecisionPoint(kind, year, team_id, actor_kind, actor, context, options, default, internal)` (`decisions.py:41`). `default` must be one of the option ids (assert). `internal` holds the true state and is never shown to an agent.
- `decide_many` assigns ids, picks the driver (`lg.driver`, default `PolicyDriver` = the autopilot returning `default`), calls it, and **applies the guard**: an exception, timeout, non-string or unlisted id becomes the `default` with `status` `driver_error:*`, `no_answer` or `invalid_choice`. Agent text is trimmed (`_plain`). Nothing the driver says can create an option the engine did not offer. **Legality is enforced in the builder (it only offers legal options) and re-checked by the guard.**
- The record: `lg.choice_log` (canonical; entry has `id, year, kind, team, actor, options, default, chosen, driver, status, reason, note?`), the SQLite `choices` table, the actor's `decision_log` (set by each caller) and `notes` (agent's own text, capped, shown back to that agent only).
- `AgentDriver` calls `ask(dp.public())`. `public()` returns `top_priority, id, kind, year, team, decider=card_view(...), context, options, instructions`. It omits `default` and `internal`. **Weakness noted:** `context` is the builder's own dict object, not a copy, so an in-process agent could mutate it; and `options` is a shallow copy of the list of copied dicts. This does not leak anything today, but a hidden value placed in `context` (even by mistake) would go straight to the agent.
- Other drivers: `RandomLegalDriver`, `ReplayDriver`, `PerTeamDriver`, `StaffDriver` (routine calls delegated to staff), and `adversaries.py` drivers that read `dp.internal` (live card objects). Adversaries are test code; they *should* be able to see everything. They are the right place for developer-only diagnostics.

### 4.2 Decision-type matrix (25 kinds, verified)

"Default rule" is what the **autopilot** does (what the live league does today). "Stand-in" is `agents.StandIn`, test-only. "Trait-keyed" marks anything that reads a trait *word*.

| # | Kind | Owner (actor) | Source | What the actor is shown (beyond its card) | Autopilot default rule | Stand-in policy | Legal set enforced by | Recorded |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `staff_review` | CEO | `staff_cards._review_point` | team record, fan approval, coach/GM heat and perceived ratings, `relations.gm_note` | fire if clean-sweep or `heat > _fire_threshold(owner)`; **threshold uses `OwnerCard.ratings["patience"]`** (`staff_cards.py:258`) | **trait-keyed**: `PATIENCE[trait]` + patience rating | builder offers only legal firings (protected contracts excluded) | choice_log, archive `coach_fired`/`gm_fired`, decision_log |
| 2 | `hire_coach`, 3 `hire_gm` | CEO | `staff_cards._hire_point` | 3 candidates through `_person_view` (perceived ratings, **trait**, age, career) | first candidate | **trait-keyed**: `LOOKS_FOR[trait]`, `trait` in ("Showwoman","Glory Hunter"), ("Penny-Pincher","Patient Steward") | options = remaining candidates | choice_log, decision_log, archive |
| 4 | `interview_offer`, 5 `interview_counter` | CEO | `interviews.Interview` | candidate view; `said_so_far` | `offer_0`; counter: `accept` | **trait-keyed**: `OFFER_OPEN`, `OFFER_LIMIT`, `cheap = trait in (...)` | 0..MAX_GUARANTEE seasons | choice_log, table steps, decision_log |
| 6 | `interview_reply`, 7 `interview_final` | candidate (coach/GM) | same | job view incl. CEO **trait** and a noisy `patience`, fires in last 5 years | `accept` | **pressure-keyed**: wants N guaranteed seasons from the CEO's noisy patience, her fire count, the team's record and the candidate's own `pressure["contract"]` (`agents._wants`) | counter ≤ MAX_GUARANTEE | same |
| 8 | `contract_offer`, 9 `contract_counter` | club seat (GM or coach) | `contracts.ContractTable` | player position, rating, age, market salary, DFLPA rep's removals | `offer_100_<standard years>`; counter `accept` | **trait-keyed** (offer): `cheap = trait in ("Penny-Pincher","Opportunist")` opens at 90%; counter: accept if the ask ≤ 100% | `pays()`/`lengths()` from rules, cap and service | choice_log, table steps |
| 10 | `contract_reply`, 11 `contract_final` | player (`_PlayerSeat`) | same | offer on the table, history of the exchange | `accept` unless `pct<100` and 100 offered → `counter_100` | **pressure-keyed**: with an offer ≤ 90% and `pressure["contract"] >= 70`, a 20% chance to walk; otherwise counter; final: accept if the offer ≥ 90% | options derived from the legal set | same |
| 12 | `ceo_pledge` | CEO | `ceo_card.pledge_decisions` | fan approval, meters (`rapport`, `standing`, `legacy`) | `standard` | `rt["ambition"] >= 65`, `rt["business"] >= 70` (CEO ratings, **not trait**) | three fixed shares | choice_log, decision_log |
| 13 | `ceo_boycott` | CEO | `ceo_card.boycott_decisions` | boycott level, fan memories, `your_meters` | `concede` if `ratings["ambition"] >= CONCEDE_AMBITION` else `hold` (**autopilot reads CEO ambition**, `ceo_card.py:115`) | `step_aside` if tenure ≤2, else ambition ≥50 → concede | hold / concede / step_aside | choice_log, decision_log |
| 14 | `fan_demand` | fanbase | `finance._fan_demands` | CEO approval | `fair` | approval thresholds (0.45 / 0.70) | modest / fair / demanding | choice_log, fan decision_log |
| 15 | `coord_scheme` | coordinator | `coordinators.coord_scheme` | perceived roster lean per scheme (blurred by `gamecraft`) | the truly best-fit scheme with probability `VISION_BASE + VISION_SPAN·gamecraft/100`, else a random other | pick max `perceived_fit` | `SCHEMES[side]` | choice_log, decision_log |
| 16 | `scheme_veto` | head coach | `coordinators._veto_point` | head coach's blurred view of fit, `relations.gm_note` | `veto` if view < `VETO_BAR` | same threshold | approve / veto | choice_log, both decision_logs |
| 17 | `coord_review` | head coach | `coordinators._review_point` | heat and perceived ratings of each coordinator | per-coordinator heat thresholds | fire if heat > 0.3 | keep_both / fire_oc / fire_dc / fire_both | choice_log, decision_log |
| 18 | `hire_coordinator` | head coach | `coordinators` (~line 385) | candidate perceived ratings, former-head-coach flag, `gm_note` | `candidate_0` | best `playcalling + vision` | slate | choice_log, decision_log |
| 19 | `gm_draft_focus` | GM | `gm_plan` | short positions, team rank | `needs` | `needs` | needs / best_player | choice_log, decision_log |
| 20 | `gm_cap_plan` | GM | `gm_plan` | banked room, last payroll, rank | `balanced` | `all_in` if rank ≤12 else balanced | tight / balanced / all_in (small, capped margins) | choice_log, decision_log |
| 21 | `gm_draft_pick` | GM | `gm_roster` | board with blurred grades, role utility, stat lines | the autopilot's board pick (drawn id) | max role utility | the actual pick list for the slot | choice_log, decision_log; rounds ≥3 delegated to staff |
| 22 | `gm_resign` | GM | `gm_roster` | rating as she sees it, price, role utility | re-sign if she would start | utility > 0 | re_sign / let_walk (cap allows) | same |
| 23 | `gm_free_agent` | GM | `gm_roster` | top fits she can afford, blurred ratings | best by the rule | max role utility | the offered list | same |
| 24 | `gm_trade_sell`, 25 `gm_trade_buy` | GM | `gm_roster` / `autotrade` | players/picks both sides, chart points, role utility lost and gained | `accept` | accept if get ≥ 0.9·give | accept / decline (market already built the trade legally) | same |

**Counted:** 25 kinds. (My earlier working note said 24; the two trade kinds are separate strings.) By actor: CEO 7 (`staff_review`, `hire_coach`, `hire_gm`, `interview_offer`, `interview_counter`, `ceo_pledge`, `ceo_boycott`), GM 7, head coach 3, coordinator 1, candidate or player 4 (`interview_reply`, `interview_final`, `contract_reply`, `contract_final`), club seat (GM or coach) 2 (`contract_offer`, `contract_counter`), fanbase 1 = 25.

### 4.3 Where behavior is keyed on a hard-coded trait word or other legacy personality rule

| Location | What it does | Live effect? |
| --- | --- | --- |
| `agents.py:20-30` `PATIENCE`, `LOOKS_FOR`, `OFFER_OPEN`, `OFFER_LIMIT` (8 CEO trait words), the inline trait tests (`agents.py:163,166,185`) and reads of `pressure["contract"]` (`agents._wants`, `_contract_reply`) | stand-in's whole CEO, candidate and player psychology | **No** (test agent only) |
| `relations.py:35-40` `CLICK`, `GRATE` (coach/GM trait-word pairs) → `_affinity` → starting feeling | seeds the GM–head-coach relationship meters | Indirect; meters only inform, no rule reads them |
| `interactions.py:276` `OPTIMISTIC_OWNERS[owner.trait]` | how far a CEO shades her self-assessment in a press scene | Text/scene only |
| `interactions.py:186-348` quotes interpolating `{trait}`, `{wants}` | narrative lines | Text only |
| `cards.py` / `living.py` `express`, `trait_scores`, `TRAIT_SWITCH_MARGIN`, `personality_shift` | the trait word itself, which can change between seasons | Yes, changes the card |
| `cards._pressure(r, trait, …)` and `staff_cards.py:181,198` | thresholds built from trait | **Yes** (`finance.py:103,265`, `interactions.py:249-310`) |
| `OwnerCard.ratings` read by `staff_cards._fire_threshold` (patience), `finance.reinvest_share` (ambition), `ceo_card.py:115` (ambition), `governance.owner_vote` (ambition ±10%) and committee seating (popularity, business), `fan_media_cards.py:479` (popularity) | CEO "personality" actually moves money and votes | **Yes, in the live autopilot** |
| `gm_roster.py:60` `personality=c.trait` and `relations.py:93` `personality=g.trait` | shows the other staff member's trait word in context | Information given to deciders |
| `interviews.py:61` `owner=dict(trait=o.trait, …)` | the candidate sees the CEO's trait word | Information given to deciders |
| `enrichment.py:70` `facts()` | gives `personality`, `wants`, `fears`, `path`, `level` to the bio writer | Public text (bios) |
| `site_export.py:32-57` | `trait` in every person and roster row | **Public** |

Nothing in the football game engine reads a card. **Verified:** searching `game_engine.py`, `sim.py`, `lineup.py`, `boxscore.py` and `injuries.py` for `trait`, `pressure`, `perceived` and `.card` finds only `game_engine.comp_press`, a football parameter ("pressure lowers completions") that has nothing to do with the cards' `pressure`.

---

## 5. Hidden-information audit

### 5.1 Exposure paths today (verified)

| # | Path | Carries | Who can read it | Status for a future hidden value |
| --- | --- | --- | --- | --- |
| 1 | `DecisionPoint.public()` → `card_view` (`decisions.py:60,91`) | `trait, wants, fears, ratings, pressure, age, reputation, honors, career summary, recent decisions, own notes` | any agent, including a remote LLM (the payload leaves the machine) | **Allowlist: safe** if the hidden value is not a card attribute read by `card_view`. Note `ratings=dict(a.ratings)` and `pressure=dict(a.pressure)` copy whole dicts: a hidden key added to either would pass straight through |
| 2 | `DecisionPoint.context` | each builder's own dict | the same agents | **No allowlist.** Safe only by convention. `_person_view` (`staff_cards.py:282`), `interviews._job` (`:61`), `gm_roster:60`, `relations.gm_note` (`:93`) already put *other people's* `trait` in context |
| 3 | `DecisionPoint.options` (labels, `tags`, order) | tags such as `perceived_fit`, `role_utility`, `grade_as_you_see_her` | agents | Safe today because tags are blurred by design. **Rule needed:** option order and tags must never be derived from private state, and `default` must stay out of `public()` (it is) |
| 4 | Live feed `/live/*.json` (static files served by Caddy) | `season_<y>.json` → `teams` = `SE.snapshot`: every club's owner/GM/coach/OC/DC as `[name, trait, hometown, age]` and each roster row `[…, trait, bio?]`; box scores; results; `meta.json` with **`seed`** | everyone, no login | **Public by design.** Anything added to `snapshot` is published |
| 5 | The HTML page | `site/template.html:204,440,471` render `trait` | everyone | Public. The client has no private data beyond the feed |
| 6 | Chronicle | `chronicle.py` reads `season_<y>.json`, `results_<y>.json`, `g/*.json` | writes public prose | **Verified**: it never reads or mentions `trait`; it uses names, positions, ratings (row indices 1, 2, 4). The only way a hidden value reaches it is if the feed contains one. LLM writer is off unless a key is set; if on, its prompt is the closed fact sheet |
| 7 | `control_server.py` (`127.0.0.1:8081`, behind Caddy basic auth) | `GET /api/state`, `POST /api/pause|resume` only | the Commissioner | **No debug or card endpoint exists.** Verified from the handler: only those three paths |
| 8 | Caddy | `/api/*` behind login, everything else public file server over `/var/www/dfl`; `X-Robots-Tag noindex` | everyone | Anything written into `/var/www/dfl/**` is public. A stray `dfl-frontend-review.tar.gz` is already there (WORK_LOG) |
| 9 | `store.py` | `cards` table `json` column = `dataclasses.asdict(card)` for every card; `people` table (name, **trait**, souls); pickle snapshots of the whole league; `export_card`/`import_card` | whoever has the DB file | **A new card field is saved automatically.** Not reachable from the web unless someone serves the DB |
| 10 | Text renderers `render_player/coach/owner/gm` and `card_report.py` | whole card including trait, wants, fears, pressure | developer CLI only | Developer-only today; keep it so |
| 11 | `lg.choice_log` and the `choices` table | `default`, `options`, `chosen`, free-text `reason`/`note` | developers | `default` is the autopilot's answer: if autopilot defaults ever read hidden state, `default` becomes a side channel to it. Keep it out of every public path |
| 12 | Public GitHub repo, CI logs, `golden_fingerprints.json`, `reports/` | all code, all tests, every CI run's stdout | everyone | **Anything printed in CI is public.** Code and the seed also make every generated value recomputable (5.2) |
| 13 | LLM agents (future) | the `public()` payload goes to a third-party API | provider and logs | Another reason the agent door must remain an allowlist |

### 5.2 The seed problem (new, important)

1. The repository is public (verified).
2. `/live/meta.json` is public and contains `"seed": 7` (verified by fetching `https://diamondfootballleague.com/live/meta.json` on 2026-10-17).
3. Every card draws from `random.Random(f"{card_seed}-{kind}-{id}…")`, with `card_seed` derived from the league seed (`league.py:168`). The football engine is also a pure function of the seed (that is why a restart can replay the years).
4. Therefore a visitor can clone the repo, run `live.py` or `founding.open_league(7)`, and read any value the code computes, including values the site never publishes, and including seasons that have not been revealed on the clock yet.

**Verified reproduction (2026-10-17).** Running `founding.open_league(7)` and `site_export.snapshot` from this repository on a fresh machine took about one second and reproduced the live feed's `season_1.json` exactly for clubs 1 and 2: all ten staff entries (name, trait, hometown, age) and each club's first roster row (for example player 1 `Yasmin Coleridge, QB, 21, 63, Wisconsin, Baton Rouge LA, 5.97, 1, Diplomat` and player 70 `Emani Redfern, … Competitor`). This was a read-only fetch of a public file compared with a local computation; it shows that the generator is reproducible from public inputs. Later years were not compared, but the live runner itself rebuilds them from the same seed on every restart.

For ordinary cards this is accepted (and it is the existing "spoiler" property of the live league). For an X-factor it defeats principle 5 outright. **Proposed fix:** the X-factor stream and the X-factor's *effect* are keyed on a **secret salt** that lives only on the server (and in the operator's backups), never in the repo, `meta.json`, snapshots served to the web, or CI. Consequences to approve:
- The visible five meters stay reproducible from the public seed (fine, they are public to the engine's own characters anyway).
- X-factors are reproducible only with the salt. Tests use a fixed test salt. A league that is replayed without its salt gets *different* X-factors and therefore, once X-factors move outcomes, a different history. The salt must be written down at league creation and backed up with `meta.json` (a new private file such as `/etc/dfl/xfactor_salt`, read by the runner, never copied into the web root).
- Side benefit: once X-factors measurably move results, the future is no longer computable from public information.
- Cost: a lost salt means the observational league can no longer be replayed from seed.

This is the main reason the plan below ends Phase One with X-factors assigned but *not yet moving any outcome*.

### 5.3 Boundaries needed (proposed)

1. **Engine-private registry, not a card field.** Keep the X-factor outside every dataclass that `asdict` serializes (`lg.xfactors`, or a function of `(salt, kind, id)` computed on demand). Never put it on `PlayerCard`, `CoachCard`, `OwnerCard`, `GMCard`.
2. **One narrow accessor** (`persona.effective(kind, id, meter)`) that only engine rule code may import. An import-graph test forbids importing it from `decisions.py` (`public`/`card_view`), `site_export.py`, `enrichment.py`, `agents.py`, `chronicle.py`, `control_server.py`, `build_site.py`, `store.py` serializers and any `check_*` that prints.
3. **Allowlist serializers.** Replace `ratings=dict(a.ratings)`/`pressure=dict(a.pressure)` in `card_view` and the person dicts in `site_export` with explicit key lists, and give `public()` a deep copy of `context`.
4. **Canary test.** Run a league with a forced X-factor on known people (a deliberately recognizable value such as 187 on a named meter), serialize every public surface (`public()` for every decision kind in a full season, every feed file the live runner writes, the built page, `export_card` text, `site_export.snapshot`, `render_*`, enrichment `facts()`, Chronicle fact sheets), and assert that neither the number, the meter identity, nor the flag appears.
5. **Developer-only diagnostics** live in a module that refuses to import in the live runner (`live.py`) and writes only to a path outside the web root.
6. **Persistence.** The store writes the registry into its own table (or not at all if the value is a pure function of `(salt, kind, id)`); `export_card` carries it only inside an explicitly engine-private envelope; pickles are already engine-private.
7. **Statistical inference is allowed, not leaks.** An observer may notice that one player behaves oddly. That is the design. What is forbidden is any field, order, tag, default or log line that names the meter or value.

---

## 6. Legacy compatibility assessment

Rule used: do not keep a superseded personality rule merely for backward compatibility; do keep infrastructure that is useful regardless.

### 6.1 Keep (useful infrastructure, independent of the personality contract)

| Mechanism | Why it stays |
| --- | --- |
| Private per-card random streams `random.Random("-".join((card_seed,)+key))` | This is exactly the determinism pattern Phase One needs: a new `("persona", kind, id)` stream leaves every existing draw unchanged |
| The Decision Point door, `decide_many`, the guard and `choice_log` | The authoritative legality and fallback layer; the brief requires it be preserved |
| `DecisionPoint.public()` as the single agent door and `internal` for engine truth | Right idea; tighten with allowlists |
| `perceived` vs true ratings, `_perceived` blurs, `confidence_gap` | Imperfect information is principle 7; this is knowledge, not personality, and it already works |
| Soul/shape/`anchor`/`potential`, `apply_soul`, `living.grow` | These are **skill development**. The brief says do not assume athletic archetypes or skill growth must go. They shape ratings, not choices |
| Athletic archetype labels (`ARCHETYPES`, `birth_archetypes`) for players | Labels for what a player is good at; not psychology |
| Reputation (`esteem`, `standing`, `honors`), career/history logs, Hall | Not personality |
| `pressure` machinery as a *concept* (situational stress thresholds) | Likely still wanted, but it is trait-derived today; see below |
| `relationships` | Pair state; keep, but its trait-pair seeding must be replaced |
| `OwnerCard.meters` (rapport/standing/legacy) | CEO situational state, not personality; keep and do not count as one of the five |
| `FanbaseCard.meters`/`ratings` | Collective state |
| `store.py` round-trips, `export_card` | Keep; must be taught about the private registry |
| Golden fingerprints, fairness bands, tiered checks, CI | The regression net |

### 6.2 Conflicts with the five-meter contract (replace, do not preserve)

| Mechanism | Conflict | Notes |
| --- | --- | --- |
| `family` (constrains which four traits a person can have, derived from the athletic archetype) | Personality should not be a function of a player's athletic archetype. The five meters must be independent of the archetype | Separate the "what kind of athlete" label from personality. `ARCHETYPE_FAMILY` is the link to cut |
| `trait` word (8 CEO words, 4 per family elsewhere) and `express`/`trait_scores`/`personality_shift` | Replaced by five numbers. A word can be *derived for display* from the numbers, but must not be the cause of anything | The "shift between seasons" mechanic needs a lifecycle decision for the new meters |
| `wants`/`fears` lookups keyed by trait | They would become derived text or go away | They are shown to agents and used in quotes |
| `_pressure(r, trait, …)` | Thresholds currently come from trait | Decide whether pressure becomes a function of the five meters or stays situational |
| `ego`/`temper` | `temper` jitters trait scores; `ego` is self-image. Self-image is knowledge and can stay, but must not become a sixth personality meter | Name this in the schema as "belief", not "personality" |
| `OwnerCard.ratings` (patience, ambition, involvement, popularity, business) | They are five decision-driving numbers on CEOs, already read by the autopilot. They duplicate the intended role of the five meters and would leave CEOs with two sets | Decide: map, replace or keep as skills. `popularity` and `business` are arguably ability/standing, not temperament |
| `agents.py` trait tables and inline trait tests | The stand-in's entire personality model; test-only | Rewrite against meters when the semantics exist, or retire |
| `relations.CLICK/GRATE` | Trait-pair table | Replace with a function of meter differences |
| `interactions.OPTIMISTIC_OWNERS`, trait-in-quote text | Same | Text layer only |
| Public `trait` in the feed, site and `people` table | The word leaks the old system; also the trait is the only personality information spectators have | Decide what spectators may see of visible meters (question 3) |
| `CONFIDENCE_LOAD`, `PHYSICAL_FLAWS` and the confidence terms in `trait_scores` | Part of how `trait` is expressed | Go with `trait` |

### 6.3 Classification of the autopilot's "personality"

The live league's behavior depends on personality only through (1) CEO ratings and (2) trait-derived `pressure`. Replacing those changes live outcomes, so it is Phase Two work and has to be version-gated (section 8).

---

## 7. Design decisions that need the Commissioner's approval before code

1. **The five meters:** names, one-sentence meaning of high and low, and which decision kinds each is meant to govern. Phase One schema code takes the names from a data file so it does not hard-code them, but the later wiring cannot.
2. **X-factor representation.** (a) One of the five meters carries a second, private value from 101 to 200 that replaces the ordinary one in engine rules, or (b) a private multiplier applied to that meter. Neither adds a sixth meter. Recommendation: (a), because it is one number per affected person. And: **can an X-factor ever lower a meter** (PR #40's "1–200, 100 normal" implies yes; the brief says amplify)? Recommendation: amplify only; "harmful" comes from consequences (an extreme value pushes a decision into a bad region), not from a sign flip.
3. **What anyone may see of the *ordinary* meters.** Today the trait word is public. Options: (i) fully private to the engine, characters infer from behavior; (ii) the owner of a card sees her own five; (iii) other characters see a blurred read (as with `patience_as_you_read_her`); (iv) spectators see them on the site. This decides what `card_view`, `_person_view`, the feed and the page publish. Recommendation: self sees exact, others see noisy reads, spectators see a coarse band, and the X-factor is visible to nobody.
4. **Who counts as a character** (section 3.3): individuals only, or fans and media too.
5. **The 5% rule:** independent coin per character (recommended; "approximately 5%") or an exact quota per generated cohort. Independent means a league of ~3,000 people has about 150 ± 12 X-factors; a 53-player roster has no X-factor player about 7% of the time (0.95^53) and three or more about half the time (50%), which is what "approximately 5%" means.
6. **CEO `ratings` and `meters`:** replace `OwnerCard.ratings` with the new five, map them, or keep them as non-personality fields; `OwnerCard.meters` stays as situational state.
7. **Secret salt** (section 5.2): approve a server-held salt for X-factors, accept that X-factors are not reproducible from the public seed, and accept the backup duty.
8. **Existing history:** regenerate the observational season with the new contract (it is allowed to be regenerated) or keep seed 7 as it is and only apply the new personalities from a new `rules` version. Either way the running league must not be restarted by this work.
9. **Who applies a hidden meter to a real agent's choice.** A real agent reads its card and chooses; an X-factor it cannot see cannot be in its reasoning. So the effect must come from the engine, for example by filtering or ranking legal options, biasing which option an impulsive person "gets drawn to", or changing outcome odds. The approved principles (6 and 7) need an explicit mechanism here before any wiring PR.
10. **Autopilot and fairness:** if personality is to affect the live (autopilot) decisions, the fairness study must be run again and the bands must be inside with personality on. This costs hours per run and cannot be skipped.

---

## 8. Phase One plan: the smallest safe sequence

Principles for all pull requests: documentation or additive code only until PR 5; no change to `golden_fingerprints.json`; no use of `league.rng`; no change to the rulebook, fairness bands or any threshold; fast tier green on every PR; each PR small enough to review in one sitting.

### PR 1: Contract and approval record (docs only; blocked on questions 1–8)
- **Files:** `docs/PERSONALITY_CONTRACT.md` (the approved meter names and meanings, the X-factor representation, visibility table, character scope, salt policy), `data/personality_meters.json` (names, labels, bounds, version; the only place the names live).
- **Why first:** every later PR reads the names from this file; nothing else can be reviewed against an unapproved contract.
- **Acceptance:** the Commissioner approves the text in chat; the file lists exactly five keys.

### PR 2: Persona schema and deterministic generator, attached to nothing
- **Files (new):** `engine/persona.py`, `engine/check_persona.py` (added to the FAST list in `run_checks.py`).
- **Contents:** `Persona` (frozen dataclass, `meters: dict[str,int]`, exactly the keys in `data/personality_meters.json`, `version`); `make_persona(card_seed, kind, ident)` using `random.Random("-".join((card_seed, "persona", kind, ident)))`; `make_xfactor(salt, kind, ident)` using a separate stream that includes the salt; `Persona.public()` (ordinary meters only); the accessor `effective(...)` kept in a separate private module so the import test can ban it. Distribution parameters come from the approved contract (until then the check uses a placeholder distribution marked as such).
- **Tests (`check_persona.py`):** exactly five keys; all in 1..100; same inputs → same output; order independence (generate in shuffled order); different `kind`/`id` → different streams; `league.rng` state identical before and after (the fingerprint of `random.getstate()`); X-factor independent of visible values; empirical rate within a binomial interval of 5% over 20,000 draws; at most one amplified meter per person; amplified value within the approved range; `repr`, `asdict` and `public()` contain no X-factor.
- **Dependencies:** PR 1. **Behavior change:** none (nothing calls it).

### PR 3: Attach visible meters to the cards, behind the existing API
- **Files:** `engine/cards.py` (`PlayerCard`, `CoachCard`: new `persona` field filled in `make_player_card`/`make_coach_card`), `engine/staff_cards.py` (`OwnerCard`, `GMCard`), `engine/store.py` (round-trip of the new field; old saves load with the field derived on the fly), `engine/check_cards.py`, `check_living.py`, `check_store.py`.
- **Not touched:** `trait`, `family`, `pressure`, `ratings`, any decision builder, `card_view`, `site_export`.
- **Acceptance:** `engine/golden_fingerprints.json` and every hash in `check_parity`/`check_tables` unchanged (zero regenerated); the fast tier and the slow tier pass exactly as at baseline; founding a league twice gives identical personas; a player created later gets her persona at her first `ensure_cards` pass, same as if created at founding.
- **Risk:** adding a dataclass field changes `asdict` output and the pickle, so old snapshots must still load (test).

### PR 4: The private X-factor registry and the leak harness
- **Files:** `engine/persona.py` (registry `lg.xfactors` or on-demand function), `engine/store.py` (separate private table or none), `engine/decisions.py` (allowlist in `card_view`; deep copy of `context` in `public()`), `engine/site_export.py` (explicit person/roster row builders), `engine/live.py` (reads the salt from a path outside the web root; never writes it to the feed), `engine/check_hidden.py` (new, FAST).
- **Tests:** the canary test (section 5.3 item 4) across every decision kind in a full simulated season, every live-feed file, `export_card`, the built page and Chronicle fact sheets; an import-graph test banning the private accessor outside engine rule modules; a test that `meta.json` contains no salt-derived value; a test that two runs with different salts give identical game results (X-factors still do not move anything).
- **Acceptance:** canary absent from all public surfaces; goldens unchanged; no new file in the web root.

### PR 5 (Phase Two preview, not Phase One): wire one small decision category
Listed for ordering only. Only after the meter semantics, mechanism (question 9) and version gate exist: pick one decision kind (a CEO decision is the natural first, since the autopilot already reads CEO numbers), bind it to meters through the stand-in and the autopilot, put the change behind a new `rules` version so seed 7's replay is unchanged, add falsification tests (low vs high meter under identical context changes the choice; hold personality fixed and change only perceived information), and run the fairness study with the result recorded. This PR is where goldens may legitimately change, with the Commissioner's approval.

### Not in Phase One
Removal of `trait`, `family`, `wants`/`fears`, `CLICK/GRATE` and the stand-in tables; migration of `OwnerCard.ratings`; X-factor effects; any change to what the site shows. Each of these changes behavior or the public face and needs its own approval.

### First coding task once the contract is approved
PR 2: `engine/persona.py` plus `engine/check_persona.py`, reading names and bounds from `data/personality_meters.json`.

---

## 9. Verified test baseline

*(See the results block below. Commands, environment, durations and every failure are recorded exactly as observed. A test that was not run is marked not run.)*

RESULTS_PLACEHOLDER

---

## 10. What remains uncertain

- Whether the live server's `fd6555f` engine and `main` differ in any way that matters here: the WORK_LOG records the only engine change between them as one rulebook exemption line, but this report did not diff them.
- The slow tier's and the fairness study's runtimes on this machine (see section 9).
- Whether `hash(tuple)`-based `card_seed` is stable across Python versions: not tested; reported as a risk only.
- Whether any consumer reads `p.card.trait` that grep could not find (for example dynamic attribute access). The search covered `trait` as `.trait`, `"trait"`, `'trait'` and `trait=` in every engine module outside `check_*`.
- Behavior of the `chalkboard` branch (PR #39) with respect to hidden information: it draws only from the public play log and the static playbook, but this report did not audit it.
