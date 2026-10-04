# Phase 2 report: rosters and the drive-by-drive game engine

Seed 1, 10 seasons, drive engine. Player names are placeholders (P00123) until the character cards exist. Every number here comes from placeholder dials, not from league rules.

## Sample box score: the season-1 championship game

### Team 27 at Team 22  -  week 23, playoff final
**Final: Team 27 20, Team 22 30**

| | Team 22 (home) | Team 27 (away) |
|---|---|---|
| Total yards | 384 | 299 |
| Plays | 68 | 60 |
| Passing | 29/41, 309 yds | 19/31, 238 yds |
| Rushing | 23 car, 98 yds | 23 car, 98 yds |
| First downs | 25 | 18 |
| 3rd down | 7/14 | 3/11 |
| Turnovers | 3 | 1 |
| Sacks by defense | 6 | 4 |
| Punts | 3 | 5 |
| Time of possession | 32:15 | 27:45 |

**Team 22**
- Passing: P00988 (QB) 29/41, 309 yds, 2 TD, 1 INT, sacked 4
- Rushing: P00991 (RB) 16 car, 87 yds (5.4), 1 TD; P00993 (RB) 7 car, 11 yds (1.6), 0 TD
- Receiving: P00991 (RB) 5 rec on 6 tgt, 52 yds, 0 TD; P00995 (WR) 5 rec on 8 tgt, 36 yds, 0 TD; P00996 (WR) 4 rec on 7 tgt, 56 yds, 1 TD; P00997 (WR) 8 rec on 11 tgt, 78 yds, 0 TD; P01001 (TE) 7 rec on 9 tgt, 87 yds, 1 TD
- Kicking: P01033 (K) FG 3/3; P01034 (P) 3 punts, 49.3 avg
- Defense: P01012 (DL) 3 tkl, 0 sack, 0 INT; P01013 (DL) 2 tkl, 1 sack, 0 INT; P01014 (DL) 2 tkl, 3 sack, 0 INT; P01018 (DL) 2 tkl, 2 sack, 0 INT; P01019 (LB) 7 tkl, 0 sack, 0 INT; P01022 (LB) 6 tkl, 0 sack, 0 INT; P01025 (CB) 4 tkl, 0 sack, 1 INT; P01026 (CB) 2 tkl, 0 sack, 0 INT; P01028 (CB) 4 tkl, 0 sack, 0 INT; P01029 (S) 5 tkl, 0 sack, 0 INT; P01030 (S) 5 tkl, 0 sack, 0 INT

**Team 27**
- Passing: P01223 (QB) 19/31, 238 yds, 2 TD, 1 INT, sacked 6
- Rushing: P01226 (RB) 16 car, 69 yds (4.3), 0 TD; P01227 (RB) 7 car, 29 yds (4.1), 0 TD
- Receiving: P01226 (RB) 3 rec on 6 tgt, 33 yds, 0 TD; P01231 (WR) 3 rec on 6 tgt, 36 yds, 1 TD; P01232 (WR) 6 rec on 9 tgt, 65 yds, 0 TD; P01235 (WR) 5 rec on 6 tgt, 86 yds, 0 TD; P01236 (TE) 2 rec on 4 tgt, 18 yds, 1 TD
- Kicking: P01268 (K) FG 2/3; P01269 (P) 5 punts, 42.2 avg
- Defense: P01247 (DL) 4 tkl, 0 sack, 0 INT; P01250 (DL) 2 tkl, 1 sack, 0 INT; P01251 (DL) 6 tkl, 1 sack, 0 INT; P01254 (LB) 9 tkl, 2 sack, 0 INT; P01256 (LB) 10 tkl, 0 sack, 0 INT; P01260 (CB) 5 tkl, 0 sack, 0 INT; P01261 (CB) 3 tkl, 0 sack, 0 INT; P01264 (S) 6 tkl, 0 sack, 1 INT; P01265 (S) 7 tkl, 0 sack, 0 INT

**Drive log**

| # | Team | Qtr | Start | Plays | Yds | Time | Result |
|---|---|---|---|---|---|---|---|
| 1 | Team 27 | 1 | own 26 | 3 | -1 | 0:50 | PUNT |
| 2 | Team 22 | 1 | own 39 | 7 | 53 | 2:47 | FG |
| 3 | Team 27 | 1 | own 33 | 3 | 5 | 0:43 | PUNT |
| 4 | Team 22 | 1 | own 19 | 5 | 19 | 2:52 | PUNT |
| 5 | Team 27 | 1 | own 16 | 7 | 28 | 2:38 | PUNT |
| 6 | Team 22 | 1 | own 25 | 10 | 42 | 4:50 | FG |
| 7 | Team 27 | 1 | own 31 | 11 | 69 | 6:21 | TD |
| 8 | Team 22 | 2 | own 31 | 2 | 1 | 0:49 | INT |
| 9 | Team 27 | 2 | own 78 | 3 | 3 | 2:27 | FG |
| 10 | Team 22 | 2 | own 31 | 10 | 69 | 4:36 | TD |
| 11 | Team 27 | 2 | own 31 | 2 | 0 | 0:10 | INT |
| 12 | Team 22 | 2 | own 75 | 3 | -6 | 0:51 | FUMBLE |
| 13 | Team 22 | 3 | own 28 | 7 | 53 | 3:08 | FG |
| 14 | Team 27 | 3 | own 20 | 6 | 65 | 3:04 | MISSED_FG |
| 15 | Team 22 | 3 | own 22 | 12 | 78 | 6:14 | TD |
| 16 | Team 27 | 3 | own 31 | 11 | 69 | 5:23 | TD |
| 17 | Team 22 | 4 | own 31 | 3 | 2 | 1:29 | PUNT |
| 18 | Team 27 | 4 | own 27 | 5 | 31 | 2:44 | PUNT |
| 19 | Team 22 | 4 | own 20 | 1 | 9 | 0:33 | FUMBLE |
| 20 | Team 27 | 4 | own 71 | 3 | 9 | 1:49 | FG |
| 21 | Team 22 | 4 | own 23 | 4 | 17 | 1:38 | PUNT |
| 22 | Team 27 | 4 | own 9 | 3 | -7 | 0:53 | PUNT |
| 23 | Team 22 | 4 | own 53 | 4 | 47 | 2:22 | TD |
| 24 | Team 27 | 4 | own 21 | 3 | 28 | 0:36 | END_PERIOD |

## League stats over 10 seasons (8040 team-games, regular season, Ambassador and playoffs)

| Measure (per team per game unless noted) | This league | Football-like target | Within range? |
| --- | --- | --- | --- |
| points | 22.49 | 22.00 (+/- 1.5) | yes |
| plays | 62.40 | 63.50 (+/- 3.0) | yes |
| pass att | 33.10 | 33.50 (+/- 2.0) | yes |
| completion pct | 68.92 | 65.00 (+/- 2.0) | NO |
| yards per attempt | 7.52 | 6.90 (+/- 0.5) | NO |
| rush att | 26.98 | 26.50 (+/- 2.0) | yes |
| yards per carry | 4.26 | 4.30 (+/- 0.3) | yes |
| total yards | 349.94 | 340.00 (+/- 25.0) | yes |
| sacks taken | 2.32 | 2.50 (+/- 0.5) | yes |
| punts | 3.97 | 4.30 (+/- 0.8) | yes |
| first downs | 20.67 | 20.00 (+/- 2.5) | yes |
| third down pct | 44.24 | 40.00 (+/- 4.0) | NO |
| fg attempts | 2.07 | 1.90 (+/- 0.5) | yes |
| fg pct | 85.75 | 84.00 (+/- 5.0) | yes |
| drives | 10.62 | 11.00 (+/- 1.2) | yes |
| time of possession min | 30.26 | 30.00 (+/- 1.5) | yes |
| game margin sd | 12.93 | 13.50 (+/- 1.5) | yes |
| home win pct | 56.47 | 54.00 (+/- 3.0) | yes |

Targets are rough NFL-style figures chosen by the AI as a stand-in for "looks like football". They are not rules and not your decisions.

## Career leaders in the simulated seasons

**Passing yards** (all 10 seasons combined, per player id)

- P00988 (QB): 50797  (369 TD, 48 INT, 186 games)
- P01740 (QB): 49126  (365 TD, 72 INT, 183 games)
- P02452 (QB): 47384  (324 TD, 99 INT, 171 games)
- P01223 (QB): 45891  (314 TD, 51 INT, 176 games)
- P02116 (QB): 45365  (321 TD, 74 INT, 173 games)

**Rushing yards** (all 10 seasons combined, per player id)

- P02025 (RB): 15382  (3418 carries, 4.5 avg)
- P01790 (RB): 13475  (3098 carries, 4.3 avg)
- P00380 (RB): 13244  (2962 carries, 4.5 avg)
- P01088 (RB): 12058  (2793 carries, 4.3 avg)
- P01696 (RB): 11823  (2628 carries, 4.5 avg)

**Receiving yards** (all 10 seasons combined, per player id)

- P01184 (WR): 15032  (1356 catches, 107 TD)
- P01136 (WR): 13307  (1213 catches, 91 TD)
- P00948 (WR): 13230  (1149 catches, 92 TD)
- P00949 (WR): 12871  (1165 catches, 79 TD)
- P01232 (WR): 12752  (1172 catches, 79 TD)

**Sacks** (all 10 seasons combined, per player id)

- P01297 (DL): 141  
- P02049 (DL): 135  
- P00216 (DL): 133  
- P01765 (DL): 113  
- P01012 (DL): 113  

**Interceptions** (all 10 seasons combined, per player id)

- P00272 (CB): 34  
- P00462 (CB): 33  
- P02247 (CB): 32  
- P01589 (CB): 32  
- P01590 (CB): 29  

## Parity

- Team strength spread (standard deviation of team power ratings, points): 3.2 on average (range 2.7 to 3.5).
- Regular-season win percentage of the 40 active teams: sd 0.146; best 5% about 0.722, worst 5% about 0.278.

## Injuries

- About 280 injuries per season league-wide, roughly 5.8 per team. Rates and lengths are placeholder dials in injuries.py.

## Roster offseason (per year, whole league)

| Retirements | Contracts ended | Free-agent signings | Premium (exile relief) signings | Rookies drafted | Street free agents needed |
| --- | --- | --- | --- | --- | --- |
| 209 | 284 | 392 | 0.5 | 48 | 2 |

## Exile target on the roster model

Where a team that has just come back from exile finishes in its division. Your target: it should have the potential to compete for about 3rd, sometimes succeeding and sometimes not. A league-average team finishes 3.0 on average, so about 3.0 to 3.3 hits the target.

| Engine | Leagues x seasons | Average finish | 1st | 2nd | 3rd | 4th | 5th (exiled again) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fast | 8 x 40 | 3.16 (+/- 0.06) | 17% | 18% | 19% | 21% | 24% |
| drives | 4 x 40 | 3.25 (+/- 0.08) | 16% | 16% | 20% | 25% | 23% |

`fast` decides a game from the two teams' power ratings; `drives` plays the whole game. They agree, which is the point of the fast mode: long studies can use it.
