# DFL rule decisions

Change a number in `engine/rules.py`, then update this file.
Every rule is tagged **confirmed** (Jeph stated it) or **assumed** (the AI filled a gap). Assumed rules are working defaults only. They are never treated as settled.

## Confirmed

| Decision | Setting | Source |
| --- | --- | --- |
| League name | Diamond Football League | Jeph, 2026-10-03 |
| Structure | 48 teams, 2 conferences, 8 divisions, each division 5 active teams + 1 exile slot | rules text |
| Schedule | 18 games over 19 weeks (1 bye): 4 non-conference same-tier, 4+4 division, 6 tier-based | rules text |
| Tier opponents | 1s play 1s and 2s; 2s play 1s and 3s; 3s play 2s and 4s; 4s play 3s and 5s; 5s play 4s and 5s | rules text |
| Tier vs seed | "Tier" (1-5) for scheduling, "seed" (1-7) for playoffs | rules text |
| Exile | Finish 5th in the division; one season; returns as Tier 5; Ambassador Season (7-game round-robin + Ambassador Bowl) | rules text |
| Playoff field | 4 division winners + 3 wild cards per conference (7 seeds); seed 1 has a bye | Jeph, 2026-10-03 |
| Draft bands | Picks 1-8 exiled lottery, 9-34 active non-playoff, 35-48 playoff teams | rules text |
| Lottery size | 8 teams | Jeph, 2026-10-04 |
| Recall cycle | One division league-wide per year, so every owner is voted on once every 8 years | Jeph, 2026-10-04 (replaces an earlier wrong "4-year" change) |
| Recall also triggers on exile | Yes | rules text |
| What exile is | The league treats exile as help for a distressed team, not punishment: relief plus play in exotic locations around the world while it rebuilds. Media and fans may see it differently. | Jeph, 2026-10-04 |
| Test standard | Every test asks one question: does the trend fall outside the expected / accepted range of "fair competitiveness"? | Jeph, 2026-10-04 |
| How exile shows up in the story | Not set by rules. It emerges from how the local and national media and fanbase react (a long-suffering Cleveland-style market versus a cutthroat "he's not Montana or Young" market give very different stories). That belongs to the character, media and fan layer built later | Jeph, 2026-10-04 |
| How much help | Modest. A returning team should have the potential to compete for 3rd place in its division, sometimes succeeding, sometimes not. Promotes fair competitiveness. | Jeph, 2026-10-04 |

## Assumed (provisional, awaiting Jeph)

| Item | Working default |
| --- | --- |
| Lottery weights | 18 / 16 / 15 / 13 / 12 / 10 / 9 / 7, worst record to best. The old 14%/6% figures were left over from an earlier design. |
| Lottery timing | The 8 teams that just finished 5th. Switchable in `rules.py` (`LOTTERY_POOL`). |
| Lottery draw | Each pick drawn one at a time by weight, without replacement |
| How tiers are earned | Last season's finish in the division: 1st = Tier 1 ... 4th = Tier 4; the team back from exile = Tier 5 |
| Tiebreakers (division) | Head-to-head, division record, point differential, seeded coin flip |
| Tiebreakers (seeding across divisions) | Conference record, point differential, seeded coin flip |
| 5th-place teams and the playoffs | A 5th-place team cannot take a wild card (it is exiled) |
| Tied games | None; overtime always produces a winner |
| Division games inside weeks 5-14 | Weeks 5, 7, 9, 11, 13 |
| Home/away | Each team 9 home, 9 away |
| Draft order inside bands | Worst record picks first; teams back from exile ranked by their Ambassador Season record |
| Ambassador Season | Weeks 1-7, Ambassador Bowl in week 8 between the two best records |
| Owner-recall order | Divisions come up in a fixed rotation, one per year |
| Starting league | Random strengths; one random team per division starts in exile |
| Final's name | "Super Bowl" kept from the rules text (NFL trademark; see open questions) |
| Roster | 47 players per team: QB 3, RB 4, WR 6, TE 3, OL 8, DL 7, LB 5, CB 5, S 4, K 1, P 1 (structural choice for the game engine) |
| Starters | QB 1, RB 1, WR 3, TE 1, OL 5, DL 4, LB 2, CB 3, S 2, K, P (the rating of a unit is built from these) |
| Game detail | Games are played play by play inside the engine but only drive-level results are kept (box score, drives, team and player stats). Full play-by-play is built in and switched off (`record_plays`); you chose "option 2, with option 3 later" |
| Injuries | Decided by the engine, not the AI. Counted in weeks; every injured player heals during the offseason. None are rolled in the playoffs (injured players stay out, nobody new is hurt) |
| Aging and retirement | Players improve until their mid-twenties, hold, then decline; kickers, punters and quarterbacks last longer. Retirement chance rises from about 31 |
| Contracts and free agency | About 15% of each roster reaches the market every year (stars are re-signed more often). Worst teams pick first. Open slots are filled from the market |
| Rookies | One per team per year, quality set by the pick. Position chosen by team need |
| Exile relief in free agency | A team returning from exile gets a few extra top-of-market signings on average (0.25 per year in the current setting), standing in for the 50% cap relief. It does not pick first in free agency (that tested as too strong) |
| Numeric bands for "fair competitiveness" | Ten measured trends with low/high limits (win-percentage spread 0.13-0.19, repeat champion at most 12% of seasons, no franchise with 5+ titles in 20 years, a returner averages 2.8-3.4 in its division, and so on). Defined in `rules.FAIR_COMPETITION_BANDS`, measured by `engine/fairness.py`, reported in `reports/fairness_report.md`. The AI's first proposal; Jeph may change any limit |
| Game engine modes | `drives` (full game), `fast` (power rating to score, no box score, for long studies), `placeholder` (Phase 1 scalar model) |

## Placeholder model (not rules)

How ratings turn into scores, how the draft changes team strength and how strength drifts between seasons are stand-ins so the league can run. The exile-related dials (pick-1 value 1.0, cap relief 0.5) were calibrated on 2026-10-04 so a returning team averages about a 3.2 division finish on the Phase 1 scalar model, in line with the confirmed exile intent. They live in `engine/placeholder_model.py` and must not be read as design decisions.

On the roster model (Phase 2) the same target was re-calibrated: the dials are in `engine/roster_model.py` and `engine/players.py`. A returning team now averages a 3.0 to 3.1 division finish (a league-average team is 3.0), with about 19% finishing 1st and about 22% falling to 5th again. See `reports/phase2_report.md`. Free-agency priority for returners was tried and dropped because it pushed the average to about 2.7.

## Notes

- The Foreword in the rules text is a vestige of an earlier design (Jeph, 2026-10-04). It is not authoritative. Where it conflicts with the confirmed rules above (for example it frames exile as erasure and punishment), the confirmed rules win.

## Open questions for Jeph

1. Do the lottery weights suit you, and should the lottery cover teams that just finished 5th or teams that just served their exile year?
2. Exile is now defined as modest relief aimed at a 3rd-place-level return (see `reports/exile_calibration.md`). Where should the help come from: the lottery pick, cap relief, or a mix?
3. "Super Bowl" is an NFL trademark. Keep it or rename it with the other NFL-style names?
4. Do you want returning exiled teams ranked into the 9-34 draft band by Ambassador record, or placed some other way?
5. Are the proposed fair-competitiveness bands (see `rules.FAIR_COMPETITION_BANDS`) the right limits? The one to watch is how often the strongest team on paper wins the title (about 22-24% now, band tops out at 25%).
