# Diamond Football League (DFL)

A fictional 48-team football simulation. Rules live in `engine/rules.py`; the rule text is in `docs/`.

## What exists (Phases 0, 1, 2 and the first character cards)

A league engine with no AI (Phase 2 adds 47-player rosters, a drive-by-drive game engine, injuries and a roster offseason; run it with `new_league(rng, rosters=True)`) and no characters. It builds legal 18-game schedules, plays them with a placeholder game model, ranks divisions with tiebreakers, runs the playoffs, exiles the five-place teams, plays the Ambassador Season, runs the lottery, drafts and sets up next year.

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
| `engine/living.py` | The living bones shared by coaches, GMs and owners: souls, careers, perception, personality inside the soul's family, the league reference, free agents |
| `engine/recognition.py` | Honors, esteem, what the media calls people (legends emerge, nobody is designated) and the league Hall of Fame |
| `engine/store.py` | Persistence: the cards are the save (one SQLite file, rebuilt from the cards, resumes exactly); optional yearly snapshots; export/import one coach or GM |
| `engine/emergence_study.py` | Plays long leagues and reports how legends and the Hall of Fame emerge; writes `reports/emergence_study.md` |
| `engine/staff_cards.py` | Owner and GM cards; recall votes, hiring and firing; the Archive's first entries |
| `engine/economy.py` | Pay and the salary cap: contracts, the $100M cap, banking up to $125M, forfeits to the pool, the 90% floor, exile absorption |
| `engine/tables.py`, `engine/interviews.py` | Negotiation tables (a bounded conversation of Decision Points where each party has her own say) and the first one, the job interview with guaranteed seasons |
| `engine/decisions.py` | Decision Points: the one door for every choice (options, drivers, guard, choice log) |
| `engine/agents.py` | A stand-in agent (reads only the public view), a flaky wrapper and seats for agents in some chairs, to rehearse the machinery without a model |
| `engine/adversaries.py` | Worst-case drivers used to test the fairness bands |
| `engine/interactions.py` | The Interaction system, first slice: firing, recall vote and exile determination scenes (claims, evidence, relationships, decision logs) |
| `engine/fan_media_cards.py` | Fanbase cards (culture, ratings, approval, Fan Capital) and media outlet cards (voice, ratings, Credibility, forecasts) |
| `engine/staff_sweep.py` | Tests owners, firings and the GM levers (and 3x, 6x stress versions) against the fairness bands; writes `reports/staff_fairness_study.md` |
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
| `docs/decisions.md` | Confirmed rules, assumed rules, open questions |

## Commands

    python engine/check_phase0.py          # do the rules agree with each other?
    python engine/check_tiebreaks.py       # NFL tiebreakers
    python engine/check_cards.py           # character cards and the coach effect
    python engine/check_staff.py           # owners, GMs, recall votes, firings
    python engine/check_fans.py            # fanbase and media cards
    python engine/check_decisions.py       # decision points, the guard, replay, the autopilot's exactness
    python engine/check_living.py          # living cards, recognition, the Hall of Fame, saving and resuming a league
    python engine/check_store.py           # the cards are the save: rebuild, resume exactly, export/import a card
    python engine/economy_report.py        # writes reports/cap_report.md: payrolls, banked room, the pool, what the cap costs teams
    python engine/check_economy.py         # pay and the cap: banking, forfeits, the floor, exile absorption, the hard limit over 40 seasons, saving
    python engine/check_tables.py          # the interview table: guarantees, walking away, what each side sees, parallel tables
    python engine/check_agents.py          # a dozen agents at once, notes to self, bounded views, a stand-in agent, seats
    python engine/decision_sweep.py        # fairness under random and worst-case choices (slow)
    python engine/check_interactions.py    # firing, recall and exile scenes (and proof they change no outcome)
    python engine/fan_media_sweep.py       # fairness study for the fan and media cards (slow)
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
