# DFL rule decisions

Decided 2026-10-03. Change the number in `engine/rules.py`, then update this file.

| Decision | Setting |
| --- | --- |
| League name | Diamond Football League |
| Playoff field | 4 division winners + 3 wild cards per conference (7 seeds) |
| Lottery weights | 18 / 16 / 15 / 13 / 12 / 10 / 9 / 7, worst to best (default, to be tested) |
| Recall cycle | 1 division per conference per year, 4-year cycle (default) |
| Tier vs seed | "Tier" (1-5) for scheduling, "seed" (1-7) for playoffs |
| Lottery timing | The 8 teams that just finished 5th (default) |
| Tiebreakers | Head-to-head, division record, point differential, seeded coin flip (default) |
| Exile benefits | Top-8 pick, 50% cap relief, easier return schedule, kept as written; test in Phase 1 whether finishing 5th pays |

Notes
- Placeholder teams (Team 01 to Team 48) are used until real cities and nicknames are chosen.
- The first 5 slots in each division are active; slot 6 is the exile slot.
