# Diamond Football League (DFL)

A fictional 48-team football simulation. Rules live in `engine/rules.py`; the rule text is in `docs/`.

## What exists (Phase 0 and Phase 1)

A league engine with no AI and no characters. It builds legal 18-game schedules, plays them with a placeholder game model, ranks divisions with tiebreakers, runs the playoffs, exiles the five-place teams, plays the Ambassador Season, runs the lottery, drafts and sets up next year.

| File | What it does |
| --- | --- |
| `engine/rules.py` | Every rule number, each tagged **confirmed** or **assumed** |
| `engine/placeholder_model.py` | Stand-in numbers (game scores, talent, draft value). Not rules. |
| `engine/league.py` | The 48 teams and their state |
| `engine/schedule.py` | Schedule generator and schedule checker |
| `engine/sim.py` | Placeholder game simulation |
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
