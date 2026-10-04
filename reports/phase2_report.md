# Phase 2 report: rosters and the drive-by-drive game engine

Seed 1, 10 seasons, drive engine. Players have names and cards (see card_samples.md). Every number here comes from placeholder dials, not from league rules.

## Sample box score: the season-1 championship game

### Team 27 at Team 22  -  week 23, playoff final
**Final: Team 27 27, Team 22 19**

| | Team 22 (home) | Team 27 (away) |
|---|---|---|
| Total yards | 326 | 435 |
| Plays | 52 | 70 |
| Passing | 22/26, 249 yds | 26/44, 327 yds |
| Rushing | 25 car, 81 yds | 23 car, 126 yds |
| First downs | 15 | 28 |
| 3rd down | 5/11 | 7/12 |
| Turnovers | 0 | 0 |
| Sacks by defense | 3 | 1 |
| Punts | 4 | 3 |
| Time of possession | 28:18 | 31:42 |

**Team 22**
- Passing: Vera Crenshaw (QB) 22/26, 249 yds, 2 TD, 0 INT, sacked 1
- Rushing: Josie Novak (RB) 18 car, 57 yds (3.2), 0 TD; Matilda Sutherland (RB) 7 car, 24 yds (3.4), 0 TD
- Receiving: Josie Novak (RB) 7 rec on 7 tgt, 75 yds, 0 TD; Celeste Goldberg (WR) 2 rec on 3 tgt, 18 yds, 0 TD; Greta Kruger (WR) 4 rec on 6 tgt, 56 yds, 1 TD; Kora Obuya (WR) 5 rec on 6 tgt, 55 yds, 0 TD; Echo Grantham (TE) 4 rec on 4 tgt, 45 yds, 1 TD
- Kicking: Xiomara Pruitt (K) FG 2/2; Britta Winslow (P) 4 punts, 47.2 avg
- Defense: Dahlia Dietrich (DL) 2 tkl, 0 sack, 0 INT; Hazel Gunnarsson (DL) 6 tkl, 1 sack, 0 INT; Liesel Leclair (DL) 0 tkl, 2 sack, 0 INT; Emilia Dubois (DL) 3 tkl, 0 sack, 0 INT; Jocelyn Hallett (LB) 4 tkl, 0 sack, 0 INT; Zoe Vickers (LB) 8 tkl, 0 sack, 0 INT; Noor Lovett (CB) 5 tkl, 0 sack, 0 INT; Tatiana Pettigrew (CB) 4 tkl, 0 sack, 0 INT; Amelia Waller (CB) 6 tkl, 0 sack, 0 INT; Dorothea Brightwater (S) 4 tkl, 0 sack, 0 INT; Isabel Eberhardt (S) 7 tkl, 0 sack, 0 INT

**Team 27**
- Passing: Sofia Ostrander (QB) 26/44, 327 yds, 3 TD, 0 INT, sacked 3
- Rushing: Hazel Dietrich (RB) 16 car, 75 yds (4.7), 0 TD; Liesel Gunnarsson (RB) 7 car, 51 yds (7.3), 0 TD
- Receiving: Hazel Dietrich (RB) 5 rec on 9 tgt, 81 yds, 0 TD; Emilia Boudreaux (WR) 7 rec on 12 tgt, 104 yds, 1 TD; Jocelyn Dubois (WR) 5 rec on 9 tgt, 46 yds, 2 TD; Zoe Pemberton (WR) 7 rec on 9 tgt, 69 yds, 0 TD; Catalina Villanueva (TE) 2 rec on 5 tgt, 27 yds, 0 TD
- Kicking: Tasha Espinoza (K) FG 2/2; Amara Iverson (P) 3 punts, 42.0 avg
- Defense: Britta Quillen (DL) 5 tkl, 0 sack, 0 INT; Mirabel Edmonds (DL) 1 tkl, 0 sack, 0 INT; Sloane Hendricks (DL) 4 tkl, 1 sack, 0 INT; Aiko Mangum (DL) 6 tkl, 0 sack, 0 INT; Hattie Yamada (LB) 8 tkl, 0 sack, 0 INT; Penelope Ellison (LB) 6 tkl, 0 sack, 0 INT; Jelena Zamora (CB) 3 tkl, 0 sack, 0 INT; Maribel Calloway (CB) 4 tkl, 0 sack, 0 INT; Zelda Holmgren (CB) 2 tkl, 0 sack, 0 INT; Cassidy Maynard (S) 5 tkl, 0 sack, 0 INT; Nina Cardenas (S) 3 tkl, 0 sack, 0 INT

**Drive log**

| # | Team | Qtr | Start | Plays | Yds | Time | Result |
|---|---|---|---|---|---|---|---|
| 1 | Team 22 | 1 | own 29 | 3 | 5 | 1:06 | PUNT |
| 2 | Team 27 | 1 | own 17 | 12 | 83 | 6:40 | TD |
| 3 | Team 22 | 1 | own 31 | 11 | 69 | 6:12 | TD |
| 4 | Team 27 | 1 | own 31 | 3 | -2 | 1:28 | PUNT |
| 5 | Team 22 | 2 | own 40 | 4 | 36 | 2:11 | FG |
| 6 | Team 27 | 2 | own 31 | 13 | 56 | 5:19 | FG |
| 7 | Team 22 | 2 | own 31 | 9 | 62 | 5:28 | FG |
| 8 | Team 27 | 2 | own 28 | 5 | 61 | 1:32 | END_PERIOD |
| 9 | Team 27 | 3 | own 25 | 6 | 34 | 2:09 | PUNT |
| 10 | Team 22 | 3 | own 20 | 4 | 21 | 2:29 | PUNT |
| 11 | Team 27 | 3 | own 37 | 9 | 63 | 3:29 | TD |
| 12 | Team 22 | 3 | own 31 | 3 | 6 | 2:25 | PUNT |
| 13 | Team 27 | 3 | own 10 | 7 | 34 | 3:17 | PUNT |
| 14 | Team 22 | 3 | own 9 | 3 | 6 | 1:54 | PUNT |
| 15 | Team 27 | 4 | own 36 | 5 | 32 | 2:39 | FG |
| 16 | Team 22 | 4 | own 20 | 9 | 80 | 4:50 | TD |
| 17 | Team 27 | 4 | own 26 | 10 | 74 | 5:05 | TD |
| 18 | Team 22 | 4 | own 31 | 6 | 41 | 1:38 | END_PERIOD |

## League stats over 10 seasons (8040 team-games, regular season, Ambassador and playoffs)

| Measure (per team per game unless noted) | This league | Football-like target | Within range? |
| --- | --- | --- | --- |
| points | 22.55 | 22.00 (+/- 1.5) | yes |
| plays | 62.45 | 63.50 (+/- 3.0) | yes |
| pass att | 33.17 | 33.50 (+/- 2.0) | yes |
| completion pct | 68.80 | 65.00 (+/- 2.0) | NO |
| yards per attempt | 7.49 | 6.90 (+/- 0.5) | NO |
| rush att | 26.99 | 26.50 (+/- 2.0) | yes |
| yards per carry | 4.25 | 4.30 (+/- 0.3) | yes |
| total yards | 349.44 | 340.00 (+/- 25.0) | yes |
| sacks taken | 2.30 | 2.50 (+/- 0.5) | yes |
| punts | 3.98 | 4.30 (+/- 0.8) | yes |
| first downs | 20.67 | 20.00 (+/- 2.5) | yes |
| third down pct | 44.39 | 40.00 (+/- 4.0) | NO |
| fg attempts | 2.08 | 1.90 (+/- 0.5) | yes |
| fg pct | 86.01 | 84.00 (+/- 5.0) | yes |
| drives | 10.63 | 11.00 (+/- 1.2) | yes |
| time of possession min | 30.28 | 30.00 (+/- 1.5) | yes |
| game margin sd | 12.80 | 13.50 (+/- 1.5) | yes |
| home win pct | 55.17 | 54.00 (+/- 3.0) | yes |

Targets are rough NFL-style figures chosen by the AI as a stand-in for "looks like football". They are not rules and not your decisions.

## Career leaders in the simulated seasons

**Passing yards** (all 10 seasons combined)

- Vera Crenshaw (QB): 54579  (416 TD, 54 INT, 198 games)
- Helena Garrison (QB): 51809  (387 TD, 88 INT, 191 games)
- Hazel Leclair (QB): 50207  (333 TD, 51 INT, 191 games)
- Honor Chambers (QB): 45940  (290 TD, 86 INT, 176 games)
- Anika Oakley (QB): 44439  (305 TD, 67 INT, 169 games)

**Rushing yards** (all 10 seasons combined)

- Vesper Merrick (RB): 15691  (3315 carries, 4.7 avg)
- Amina Toussaint (RB): 12909  (2878 carries, 4.5 avg)
- Jocelyn Vickers (RB): 12091  (2592 carries, 4.7 avg)
- Abigail Caldwell (RB): 12023  (2702 carries, 4.4 avg)
- Penelope Herrera (RB): 11873  (2770 carries, 4.3 avg)

**Receiving yards** (all 10 seasons combined)

- Eliana Hammond (WR): 14062  (1241 catches, 105 TD)
- Catalina Lovett (WR): 13219  (1190 catches, 86 TD)
- Destiny Sinclair (WR): 12946  (1166 catches, 82 TD)
- Saoirse Novak (WR): 12767  (1116 catches, 81 TD)
- Luna Everhart (WR): 12393  (1128 catches, 85 TD)

**Sacks** (all 10 seasons combined)

- Zadie Barrientos (DL): 147  
- Daniela Nettles (DL): 126  
- Zara Saunders (DL): 124  
- Sylvie Dellinger (DL): 123  
- Juana Ferreira (DL): 107  

**Interceptions** (all 10 seasons combined)

- Mika Nightingale (CB): 31  
- Alba Atwood (CB): 28  
- Mercy Vandermeer (CB): 28  
- Harlow Novak (CB): 28  
- Cleo Pemberton (CB): 27  

## Parity

- Team strength spread (standard deviation of team power ratings, points): 3.3 on average (range 3.1 to 3.7).
- Regular-season win percentage of the 40 active teams: sd 0.151; best 5% about 0.722, worst 5% about 0.278.

## Injuries

- About 272 injuries per season league-wide, roughly 5.7 per team. Rates and lengths are placeholder dials in injuries.py.

## Roster offseason (per year, whole league)

| Retirements | Contracts ended | Free-agent signings | Premium (exile relief) signings | Rookies drafted | Street free agents needed |
| --- | --- | --- | --- | --- | --- |
| 211 | 280 | 394 | 0.2 | 48 | 2 |

## Exile target on the roster model

Where a team that has just come back from exile finishes in its division. Your target: it should have the potential to compete for about 3rd, sometimes succeeding and sometimes not. A league-average team finishes 3.0 on average, so about 3.0 to 3.3 hits the target.

| Engine | Leagues x seasons | Average finish | 1st | 2nd | 3rd | 4th | 5th (exiled again) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fast | 8 x 40 | 3.21 (+/- 0.06) | 16% | 17% | 19% | 23% | 24% |
| drives | 4 x 40 | 3.21 (+/- 0.09) | 16% | 20% | 16% | 23% | 25% |

`fast` decides a game from the two teams' power ratings; `drives` plays the whole game. They agree, which is the point of the fast mode: long studies can use it.
