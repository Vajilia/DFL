# Diamond Football League (DFL)

A fictional 48-team football simulation. Rules live in `engine/rules.py`; the rule text is in `docs/`.

## What exists (Phases 0, 1, 2 and the first character cards)

A seeded league engine with 53-player rosters, character cards, a drive-by-drive game engine, injuries and a roster offseason (run it with `new_league(rng, rosters=True)`). Agent decision machinery exists, with stand-in policies; a real-model integration is still pending. It builds legal 18-game schedules, plays them with a placeholder game model, ranks divisions with tiebreakers, runs the playoffs, exiles the five-place teams, plays the Ambassador Season, runs the lottery, drafts and sets up next year.

| File | What it does |
| --- | --- |
| `engine/rules.py` | Every rule number, each tagged **confirmed** or **assumed** |
| `engine/placeholder_model.py` | Stand-in numbers (game scores, talent, draft value). Not rules. |
| `engine/league.py` | The 48 teams and their state |
| `engine/schedule.py` | Schedule generator and schedule checker |
| `engine/sim.py` | Game front end: placeholder, fast or drive-by-drive; injuries and stat totals |
| `engine/game_engine.py` | The drive-by-drive football engine (box scores; play-by-play switch for later) |
| `engine/positions.py`, `players.py`, `lineup.py` | Rosters, players, depth charts and unit ratings |
| `engine/injuries.py` | Injury rates and clock |
| `engine/offseason.py`, `roster_model.py` | Aging, retirement, draft rookies, free agency, exile relief |
| `engine/power_rating.py` | Generated: team rating to expected margin (made by `fit_power_rating.py`) |
| `engine/boxscore.py` | Readable box score |
| `engine/calibrate_engine.py` | Checks the engine looks like football |
| `engine/phase2_report.py` | Writes `reports/phase2_report.md` |
| `engine/cards.py`, `card_pools.py` | Character cards: player souls (archetypes), perception and personality; head coaches who develop players |
| `engine/living.py` | The living bones shared by coaches, GMs and CEOs: souls, careers, perception, personality inside the soul's family, the league reference, free agents |
| `engine/recognition.py` | Honors, esteem, what the media calls people (legends emerge, nobody is designated) and the league Hall of Fame |
| `engine/store.py` | Persistence: the cards are the save (one SQLite file, rebuilt from the cards, resumes exactly); optional yearly snapshots; export/import one coach or GM |
| `engine/emergence_study.py` | Plays long leagues and reports how legends and the Hall of Fame emerge; writes `reports/emergence_study.md` |
| `engine/staff_cards.py` | CEO and GM cards; recall votes, hiring and firing; the Archive's first entries |
| `engine/service.py`, `engine/check_service.py` | Earned accrued/credited service, expiration classification, boundary and save/resume checks; service now controls salary/PS eligibility |
| `engine/movement.py`, `engine/check_movement.py` | Step 6c/6d: the draft-pick ledger (original club, owner, slot, reservation, selection), tenders and rights, funded offers with five-day matching and compensation, their own SQLite tables (save format 3), and twelve checks including atomicity, boundaries, migration and save/resume |
| `engine/transactions.py`, `engine/check_transactions.py` | Step 6e to 6h: the waiver wire and in-season records for priority, full trades (cap, bonus acceleration, roster limits, deadline), compensatory-pick awards; with `movement.py` (franchise and transition tags) and `contracts.py`, 56 checks |
| `engine/finance.py`, `engine/check_finance.py`, `engine/finance_report.py` | Step 7: club revenue (national pool, the 34% ticket pool, local money by market, fans and success), the CEO's draw capped at $100M with the excess to the Equalization Fund, subsidies from CEOs' draws, the fans' say on spending as a capped approval nudge, 10 to 20 year CEO tenure and the forced-sale vote; writes `reports/finance_report.md` |
| `engine/injuries.py`, `engine/check_injuries.py` | Step 8a: injury kinds, NFL-scale rates and lengths, concussion protocol, the weekly injury report |
| `engine/staff_pay.py`, `engine/check_hiring.py` | Step 8b: football-staff pay inside two limits (one contract 8% of the cap, the staff 20%), the two-interview hiring rule and the demographics audit (schema scan plus a name-blind replay) |
| `engine/governance.py`, `engine/dflpa.py`, `engine/discipline.py`, `engine/check_governance.py` | Step 8c: the CEOs' votes (36 of 48 for rules, 32 for a Commissioner's successor), the Competition Committee, the Commissioner's shrink-only powers, the DFLPA representative as a character at every contract table, player suspensions and club fines |
| `engine/autotrade.py`, `engine/check_autotrade.py` | Step 9a: the autopilot's trade market (veterans for picks, pick swaps) on a draft-value chart, before the draft and at weeks 3 and 6, always legal and open to the Commissioner's reject-only review |
| `engine/check_elevations.py`, `engine/check_extensions.py` | Step 9a: practice-squad elevations to game day (up to 2 a game, 3 a season each) and mid-contract extensions for good players with a year left |
| `engine/contracts.py` | Step 6i: the contract table (club general manager, player, DFLPA representative guard) and the club's value-to-price rule that replaced the re-signing dice |
| `engine/economy.py` | Pay and the salary cap: contracts with signing bonuses, guarantees and dead money, the minimum scale, the $100M cap, banking up to $125M, the 51 rule, the four-season 90% floor, exile absorption, the Equalization Fund |
| `engine/tables.py`, `engine/interviews.py` | Negotiation tables (a bounded conversation of Decision Points where each party has her own say) and the first one, the job interview with guaranteed seasons |
| `engine/decisions.py` | Decision Points: the one door for every choice (options, drivers, guard, choice log) |
| `engine/agents.py` | A stand-in agent (reads only the public view), a flaky wrapper and seats for agents in some chairs, to rehearse the machinery without a model |
| `engine/adversaries.py` | Worst-case drivers used to test the fairness bands |
| `engine/interactions.py` | The Interaction system, first slice: firing, recall vote and exile determination scenes (claims, evidence, relationships, decision logs) |
| `engine/fan_media_cards.py` | Fanbase cards (the franchise's permanent card: culture, ratings, approval of the CEO, Fan Capital, its own evolving meters, fading memories, a boycott level) and media outlet cards (voice, ratings, Credibility, forecasts) |
| `engine/staff_sweep.py` | Tests CEOs, firings and the GM levers (and 3x, 6x stress versions) against the fairness bands; writes `reports/staff_fairness_study.md` |
| `engine/card_report.py` | Writes `reports/card_samples.md` |
| `engine/coach_sweep.py` | Sweeps the coach dials (team lift, player development) against the fairness bands; writes `reports/coach_fairness_study.md` |
| `engine/tiebreak.py` | NFL-style tiebreaking procedures (division, wild card, draft order) |
| `engine/exile_fairness_study.py` | Compares ways to handle an exiled team's two drafts; writes `reports/exile_two_draft_study.md` |
| `engine/fairness.py` | Measures trends against the "fair competitiveness" bands in `rules.py`; writes `reports/fairness_report.md` |
| `engine/standings.py` | Records and tiebreakers |
| `engine/playoffs.py` | Seeding and bracket |
| `engine/draft.py` | Lottery and 48-pick draft order |
| `engine/season.py` | One full year, including the offseason |
| `engine/run_sim.py` | Run many seasons |
| `engine/league_report.py` | Plain-language report on a run |
| `engine/exile_study.py` | Does exile pay? Sensitivity study |
| `engine/calibrate_exile.py` | Tunes the placeholder exile benefits to the design intent (a returning team can compete for about 3rd) |
| `reports/` | Output of the two reports above |
| `docs/decisions.md` | Decision log and build log; the authority is the Rulebook (living doc, `engine/rulebook.py`). The old decisions are archived in `docs/decisions_pre_rebase.md` |

## Commands

    python engine/check_service.py         # earned service, expiration classes, paid lists, save/resume
    python engine/check_movement.py        # pick ownership, tenders, funded offers, five-day match, compensation, format 3 save and migration
    python engine/check_transactions.py    # waivers, tags, trades, compensatory picks, contract tables
    python engine/check_autotrade.py       # the trade market: chart, pricing, legality, Commissioner rejection
    python engine/check_elevations.py      # practice-squad elevations
    python engine/check_extensions.py      # mid-contract extensions
    python engine/check_governance.py      # votes, committee, shrink-only Commissioner, DFLPA representative, discipline
    python engine/check_hiring.py          # two-interview rule, name-blind audit, staff pay limits
    python engine/check_injuries.py        # injury kinds, NFL-scale rates, concussions, the weekly report
    python engine/check_finance.py         # CEO draw cap, tenure, ticket pool, subsidies, forced sales, the books
    python engine/check_phase0.py          # do the rules agree with each other?
    python engine/check_tiebreaks.py       # NFL tiebreakers
    python engine/check_cards.py           # character cards and the coach effect
    python engine/check_staff.py           # CEOs, GMs, recall votes, firings
    python engine/check_fans.py            # fanbase and media cards
    python engine/check_decisions.py       # decision points, the guard, replay, the autopilot's exactness
    python engine/check_living.py          # living cards, recognition, the Hall of Fame, saving and resuming a league
    python engine/check_store.py           # the cards are the save: rebuild, resume exactly, export/import a card
    python engine/economy_report.py        # writes reports/cap_report.md: payrolls, banked room, dead money, the Equalization Fund, what the cap costs teams
    python engine/check_economy.py         # pay and the cap: banking, forfeits, the floor, exile absorption, the hard limit over 40 seasons, saving
    python engine/check_rulebook.py        # the code against the DFL Rulebook (engine/rulebook.py): every rule built / differs / missing; writes reports/rulebook_status.md
    python engine/check_tables.py          # the interview table: guarantees, walking away, what each side sees, parallel tables
    python engine/check_agents.py          # a dozen agents at once, notes to self, bounded views, a stand-in agent, seats
    python engine/decision_sweep.py        # fairness under random and worst-case choices (slow)
    python engine/check_interactions.py    # firing, recall and exile scenes (and proof they change no outcome)
    python engine/fan_media_sweep.py       # fairness study for the fan and media cards (slow)
    python engine/check_rosters.py         # 53/48/16 rosters, injured reserve, the 90-man camp, the seven-round draft and rookie scale
    python engine/check_contracts.py       # signing bonuses, guarantees, dead money, the minimum scale, the 51 rule, the four-season floor, the Equalization Fund
    python engine/check_phase2.py          # rosters, game engine, injuries, offseason
    python engine/calibrate_engine.py      # does the game look like football?
    python engine/phase2_report.py         # sample box score, league stats, exile target (about 2 minutes)
    python engine/check_phase1.py          # does the engine obey the rules? (add --long for more)
    python engine/run_sim.py --seasons 20 --seed 1
    python engine/league_report.py --seed 1 --seasons 20
    python engine/exile_study.py           # a few minutes; needs numpy

Same seed gives the same league every time.

## Layout
- `engine/` code
- `data/` team and season data (empty so far)
- `archive/` event log (the Archive, empty so far)
- `docs/` rules text and decisions
- `reports/` generated reports

## Step 6 verification and handoff

See [verification results](reports/verification_step6a.md) for baseline and changed-branch check coverage, and [handoff](docs/step6a_handoff.md) for recovery, publication state and the remaining player-movement work. Matching rulebook constants do not imply complete rights enforcement.

Step 6b integrates service into minimum base pay and practice-squad eligibility, with checks in `engine/check_service_pay.py`. Step 6c/6d (rebuilt on branch `step6-rebuild`) adds pick ownership, tenders, funded offers, matching and compensation in `engine/movement.py`. See [current verification](reports/verification_step6cd.md), [decision rationale](docs/decisions.md) and [remaining implementation order](docs/step6_remaining_plan.md). Step 6e to 6i (same branch) finishes the player-movement rules: waivers, franchise and transition tags, full trades, compensatory picks and contract tables, with a value-to-price re-signing rule replacing the old dice. See [Step 6e to 6i verification](reports/verification_step6e_i.md) and the matching section of [decision rationale](docs/decisions.md). What is still open in Step 6 is listed there honestly (extensions mid-contract, trades by the autopilot, parallel tables for agents are not built).

Step 7 (same branch) adds the money layer in `engine/finance.py`: every club earns national, ticket-pool and local revenue; its CEO (10 to 20 year tenure) reinvests part of a profit, saves a little and takes the rest as a draw capped at $100M, with the excess sent to the Equalization Fund; CEOs' draws pay subsidies to clubs whose losses the reserve cannot cover; two subsidised quarters can put a CEO up for a forced-sale vote. Money never touches the cap or a game. See [the design note](docs/step7_design.md), the matching section of [decision rationale](docs/decisions.md) and `reports/finance_report.md`.
