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
| `engine/cards.py`, `card_pools.py` | Character cards: player souls (archetypes), perception and personality; head coaches who develop players, with rare legends |
| `engine/staff_cards.py` | Owner and GM cards; fan approval, recall votes, hiring and firing; the Archive's first entries |
| `engine/staff_sweep.py` | Tests owners, firings and the GM levers (and 3x, 6x stress versions) against the fairness bands; writes `reports/staff_fairness_study.md` |
| `engine/card_report.py` | Writes `reports/card_samples.md` |
| `engine/coach_sweep.py` | Sweeps the coach dials (team lift, player development, legend rate) against the fairness bands; writes `reports/coach_fairness_study.md` |
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
