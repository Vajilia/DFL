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

## Placeholder model (not rules)

How ratings turn into scores, how the draft changes team strength and how strength drifts between seasons are stand-ins so the league can run. They live in `engine/placeholder_model.py` and must not be read as design decisions.

## Open questions for Jeph

1. Do the lottery weights suit you, and should the lottery cover teams that just finished 5th or teams that just served their exile year?
2. Does exile need a real cost beyond the lost season? Phase 1 reports show how exile compares with finishing 4th.
3. "Super Bowl" is an NFL trademark. Keep it or rename it with the other NFL-style names?
4. Do you want returning exiled teams ranked into the 9-34 draft band by Ambassador record, or placed some other way?
