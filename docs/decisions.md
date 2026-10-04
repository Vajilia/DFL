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
| Tiebreakers | All tie-breaking mirrors the NFL, at least for now (division, wild card and seeding, draft order). Procedures in `engine/tiebreak.py`, checked against nfl.com on 2026-10-04 | Jeph, 2026-10-04 |
| Lottery format | 8 teams, the ones that just finished 5th. The best record of the eight holds 1 ball, the next best 2, and so on up to 8 balls for the worst record (36 balls). Four balls are drawn for picks 1-4; the other four teams pick 5-8 in order of record (worst first), so the worst team falls no lower than 5th. Chance of pick 1, worst to best: 22.2 / 19.4 / 16.7 / 13.9 / 11.1 / 8.3 / 5.6 / 2.8 percent; chance of a top-4 pick: 75 / 71 / 65 / 58 / 50 / 39 / 28 / 15 percent | Jeph, 2026-10-04 |
| The final | Named the **Diamond Coronation**. The champion is presented with a **Diamond Tiara** instead of a trophy. "Super Bowl" is the old name from the rules text and may still be used in conversation | Jeph, 2026-10-04 |
| Priority | Fairness comes before narrative. The narrative (fan and media story) is derived from the fanbase and media, not designed in | Jeph, 2026-10-04 |
| Exile and the two drafts | Lottery pick as a new exile, then a block pick at the end of the 9-34 band (picks 27-34, ordered by Ambassador Season record) when back from exile. Accepted as the working design | Jeph, 2026-10-04 |
| Test standard | Every test asks one question: does the trend fall outside the expected / accepted range of "fair competitiveness"? | Jeph, 2026-10-04 |
| How exile shows up in the story | Not set by rules. It emerges from how the local and national media and fanbase react (a long-suffering Cleveland-style market versus a cutthroat "he's not Montana or Young" market give very different stories). That belongs to the character, media and fan layer built later | Jeph, 2026-10-04 |
| How much help | Modest. A returning team should have the potential to compete for 3rd place in its division, sometimes succeeding, sometimes not. Promotes fair competitiveness. | Jeph, 2026-10-04 |

## Assumed (provisional, can be changed)

| Item | Working default |
| --- | --- |
| Lottery draw | The four draws are made one ball at a time; a team already drawn is skipped (same as drawing without replacement) |
| How tiers are earned | Last season's finish in the division: 1st = Tier 1 ... 4th = Tier 4; the team back from exile = Tier 5 |
| NFL tiebreak adaptations | The NFL restart rule is used to rank every team, not just pick a winner; wild-card ties inside one division are settled by the division procedure first; the Ambassador Season uses head-to-head, strength of victory and schedule, net points, net touchdowns, coin toss; where touchdowns were not kept they are estimated as points // 7 |
| 5th-place teams and the playoffs | A 5th-place team cannot take a wild card (it is exiled) |
| Tied games | None; overtime always produces a winner |
| Division games inside weeks 5-14 | Weeks 5, 7, 9, 11, 13 |
| Home/away | Each team 9 home, 9 away |
| Draft order inside bands | Worst record picks first, NFL tiebreakers (lower strength of schedule picks first) |
| Ambassador Season | Weeks 1-7, Ambassador Bowl in week 8 between the two best records |
| Owner-recall order | Divisions come up in a fixed rotation, one per year |
| Starting league | Random strengths; one random team per division starts in exile |
| Roster | 47 players per team: QB 3, RB 4, WR 6, TE 3, OL 8, DL 7, LB 5, CB 5, S 4, K 1, P 1 (structural choice for the game engine) |
| Starters | QB 1, RB 1, WR 3, TE 1, OL 5, DL 4, LB 2, CB 3, S 2, K, P (the rating of a unit is built from these) |
| Game detail | Games are played play by play inside the engine but only drive-level results are kept (box score, drives, team and player stats). Full play-by-play is built in and switched off (`record_plays`); you chose "option 2, with option 3 later" |
| Injuries | Decided by the engine, not the AI. Counted in weeks; every injured player heals during the offseason. None are rolled in the playoffs (injured players stay out, nobody new is hurt) |
| Aging and retirement | Players improve until their mid-twenties, hold, then decline; kickers, punters and quarterbacks last longer. Retirement chance rises from about 31 |
| Contracts and free agency | About 15% of each roster reaches the market every year (stars are re-signed more often). Worst teams pick first. Open slots are filled from the market |
| Rookies | One per team per year, quality set by the pick. Position chosen by team need |
| Exile relief in free agency | A team returning from exile gets an extra top-of-market signing 5% of the time on average (0.05 per year; it was 0.25 before the two-draft study), standing in for the 50% cap relief. It does not pick first in free agency (that tested as too strong) |
| Numeric bands for "fair competitiveness" | Thirteen measured trends with low/high limits (win-percentage spread 0.13-0.19, repeat champion at most 12% of seasons, title concentration no worse than pure luck among the 14 playoff teams (an average of 4.7 titles for the top franchise in any 20 years, and no single league above 7), exile never worth more than half a rating point, a returner averages 2.8-3.4 in its division, and so on). Defined in `rules.FAIR_COMPETITION_BANDS`, measured by `engine/fairness.py`, reported in `reports/fairness_report.md`. The AI's first proposal; Jeph may change any limit |
| Game engine modes | `drives` (full game), `fast` (power rating to score, no box score, for long studies), `placeholder` (Phase 1 scalar model) |

## Placeholder model (not rules)

How ratings turn into scores, how the draft changes team strength and how strength drifts between seasons are stand-ins so the league can run. The exile-related dials (pick-1 value 1.0, cap relief 0.5) were calibrated on 2026-10-04 so a returning team averages about a 3.2 division finish on the Phase 1 scalar model, in line with the confirmed exile intent. They live in `engine/placeholder_model.py` and must not be read as design decisions.

On the roster model (Phase 2) the same target was re-calibrated: the dials are in `engine/roster_model.py` and `engine/players.py`. A returning team now averages a 3.0 to 3.1 division finish (a league-average team is 3.0), with about 19% finishing 1st and about 22% falling to 5th again. See `reports/phase2_report.md`. Free-agency priority for returners was tried and dropped because it pushed the average to about 2.7.

## Notes

- The Phase 1 reports built on the placeholder model (`reports/exile_study.md`, `exile_calibration.md`, `league_summary_seed1.md`) were produced before the NFL tiebreakers and the new lottery format and have not been re-run. The roster-model reports (`phase2_report.md`, `fairness_report.md`, `exile_two_draft_study.md`) supersede them.

- The Foreword in the rules text is a vestige of an earlier design (Jeph, 2026-10-04). It is not authoritative. Where it conflicts with the confirmed rules above (for example it frames exile as erasure and punishment), the confirmed rules win.

## Open questions for Jeph

None right now. Answered on 2026-10-04: the lottery covers teams that just finished 5th, the fair-competitiveness bands are accepted as proposed, and the ball counts run 1 to 8. The bands are still the AI's numbers; Jeph accepted them as the working limits and can change any of them in `rules.FAIR_COMPETITION_BANDS`.
