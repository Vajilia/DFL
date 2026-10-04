# Phase 2 report: rosters and the drive-by-drive game engine

Seed 1, 10 seasons, drive engine. Players have names and cards (see card_samples.md). Every number here comes from placeholder dials, not from league rules.

## Sample box score: the season-1 championship game

### Team 39 at Team 22  -  week 23, playoff final
**Final: Team 39 17, Team 22 24**

| | Team 22 (home) | Team 39 (away) |
|---|---|---|
| Total yards | 392 | 319 |
| Plays | 69 | 64 |
| Passing | 28/39, 269 yds | 21/40, 220 yds |
| Rushing | 29 car, 125 yds | 21 car, 111 yds |
| First downs | 28 | 22 |
| 3rd down | 7/12 | 7/14 |
| Turnovers | 3 | 1 |
| Sacks by defense | 3 | 1 |
| Punts | 2 | 4 |
| Time of possession | 34:54 | 25:06 |

**Team 22**
- Passing: Vera Crenshaw (QB) 28/39, 269 yds, 2 TD, 1 INT, sacked 1
- Rushing: Josie Novak (RB) 18 car, 73 yds (4.1), 1 TD; Matilda Sutherland (RB) 11 car, 52 yds (4.7), 0 TD
- Receiving: Josie Novak (RB) 4 rec on 4 tgt, 19 yds, 1 TD; Celeste Goldberg (WR) 1 rec on 4 tgt, 5 yds, 0 TD; Greta Kruger (WR) 11 rec on 13 tgt, 115 yds, 0 TD; Kora Obuya (WR) 8 rec on 11 tgt, 88 yds, 1 TD; Echo Grantham (TE) 4 rec on 7 tgt, 42 yds, 0 TD
- Kicking: Xiomara Pruitt (K) FG 1/1; Britta Winslow (P) 2 punts, 47.5 avg
- Defense: Dahlia Dietrich (DL) 2 tkl, 1 sack, 0 INT; Hazel Gunnarsson (DL) 2 tkl, 0 sack, 0 INT; Liesel Leclair (DL) 5 tkl, 1 sack, 0 INT; Emilia Dubois (DL) 5 tkl, 0 sack, 0 INT; Jocelyn Hallett (LB) 6 tkl, 0 sack, 0 INT; Zoe Vickers (LB) 6 tkl, 1 sack, 0 INT; Kirsten Hargrove (CB) 2 tkl, 0 sack, 0 INT; Noor Lovett (CB) 2 tkl, 0 sack, 0 INT; Amelia Waller (CB) 4 tkl, 0 sack, 0 INT; Dorothea Brightwater (S) 4 tkl, 0 sack, 0 INT; Isabel Eberhardt (S) 4 tkl, 0 sack, 1 INT

**Team 39**
- Passing: Julia Mangum (QB) 21/40, 220 yds, 0 TD, 1 INT, sacked 3
- Rushing: Abigail Caldwell (RB) 16 car, 84 yds (5.2), 0 TD; Hadley Holloway (RB) 5 car, 27 yds (5.4), 1 TD
- Receiving: Abigail Caldwell (RB) 3 rec on 7 tgt, 26 yds, 0 TD; Thea Zamora (WR) 6 rec on 12 tgt, 87 yds, 0 TD; Andrea Camacho (WR) 7 rec on 10 tgt, 58 yds, 0 TD; Jada Hutchins (WR) 1 rec on 4 tgt, 1 yds, 0 TD; Rosario Rivas (TE) 4 rec on 7 tgt, 48 yds, 0 TD
- Kicking: Kasey Contreras (K) FG 1/2; Monique Gallagher (P) 4 punts, 44.0 avg
- Defense: Priya Merrick (DL) 1 tkl, 1 sack, 0 INT; Vesper Rourke (DL) 3 tkl, 0 sack, 0 INT; Ayana Ahlberg (DL) 3 tkl, 0 sack, 0 INT; Juana Ferreira (DL) 3 tkl, 0 sack, 0 INT; Aaliyah Sandoval (LB) 8 tkl, 0 sack, 0 INT; Chiara Alderman (LB) 11 tkl, 0 sack, 0 INT; Thalia Moreau (CB) 3 tkl, 0 sack, 0 INT; Eden Amundsen (CB) 7 tkl, 0 sack, 0 INT; Ivy Coleridge (CB) 7 tkl, 0 sack, 0 INT; Rosalind Kasprzak (S) 8 tkl, 0 sack, 1 INT; Yasmin Mulvaney (S) 3 tkl, 0 sack, 0 INT

**Drive log**

| # | Team | Qtr | Start | Plays | Yds | Time | Result |
|---|---|---|---|---|---|---|---|
| 1 | Team 22 | 1 | own 25 | 10 | 75 | 4:53 | TD |
| 2 | Team 39 | 1 | own 31 | 5 | 31 | 2:25 | PUNT |
| 3 | Team 22 | 1 | own 10 | 4 | 25 | 2:09 | FUMBLE_TD |
| 4 | Team 22 | 1 | own 26 | 12 | 49 | 4:52 | FG |
| 5 | Team 39 | 1 | own 31 | 8 | 49 | 4:20 | FG |
| 6 | Team 22 | 2 | own 31 | 10 | 69 | 6:05 | TD |
| 7 | Team 39 | 2 | own 19 | 4 | 20 | 1:27 | INT |
| 8 | Team 22 | 2 | own 43 | 3 | -2 | 1:15 | INT |
| 9 | Team 39 | 2 | own 60 | 8 | 40 | 2:16 | TD |
| 10 | Team 22 | 2 | own 31 | 1 | 6 | 0:14 | END_PERIOD |
| 11 | Team 39 | 3 | own 24 | 11 | 64 | 4:32 | MISSED_FG |
| 12 | Team 22 | 3 | own 20 | 4 | 14 | 1:48 | PUNT |
| 13 | Team 39 | 3 | own 18 | 3 | -1 | 1:04 | PUNT |
| 14 | Team 22 | 3 | own 35 | 3 | 9 | 1:20 | PUNT |
| 15 | Team 39 | 3 | own 11 | 6 | 31 | 2:57 | PUNT |
| 16 | Team 22 | 3 | own 17 | 9 | 50 | 5:06 | FUMBLE |
| 17 | Team 39 | 4 | own 33 | 7 | 28 | 2:29 | PUNT |
| 18 | Team 22 | 4 | own 20 | 10 | 80 | 5:27 | TD |
| 19 | Team 39 | 4 | own 28 | 12 | 57 | 3:31 | DOWNS |
| 20 | Team 22 | 4 | own 15 | 3 | 17 | 1:39 | END_PERIOD |

## League stats over 10 seasons (8040 team-games, regular season, Ambassador and playoffs)

| Measure (per team per game unless noted) | This league | Football-like target | Within range? |
| --- | --- | --- | --- |
| points | 21.80 | 22.00 (+/- 1.5) | yes |
| plays | 62.85 | 63.50 (+/- 3.0) | yes |
| pass att | 33.47 | 33.50 (+/- 2.0) | yes |
| completion pct | 67.73 | 65.00 (+/- 2.0) | NO |
| yards per attempt | 7.32 | 6.90 (+/- 0.5) | yes |
| rush att | 27.04 | 26.50 (+/- 2.0) | yes |
| yards per carry | 4.20 | 4.30 (+/- 0.3) | yes |
| total yards | 344.45 | 340.00 (+/- 25.0) | yes |
| sacks taken | 2.34 | 2.50 (+/- 0.5) | yes |
| punts | 4.16 | 4.30 (+/- 0.8) | yes |
| first downs | 20.32 | 20.00 (+/- 2.5) | yes |
| third down pct | 43.53 | 40.00 (+/- 4.0) | yes |
| fg attempts | 2.13 | 1.90 (+/- 0.5) | yes |
| fg pct | 85.89 | 84.00 (+/- 5.0) | yes |
| drives | 10.78 | 11.00 (+/- 1.2) | yes |
| time of possession min | 30.31 | 30.00 (+/- 1.5) | yes |
| game margin sd | 12.86 | 13.50 (+/- 1.5) | yes |
| home win pct | 56.81 | 54.00 (+/- 3.0) | yes |

Targets are rough NFL-style figures chosen by the AI as a stand-in for "looks like football". They are not rules and not your decisions.

## Career leaders in the simulated seasons

**Passing yards** (all 10 seasons combined)

- Vera Crenshaw (QB): 48198  (326 TD, 67 INT, 176 games)
- Hattie Redfern (QB): 47649  (309 TD, 58 INT, 179 games)
- Helena Garrison (QB): 47194  (308 TD, 104 INT, 178 games)
- Kyra Kaplan (QB): 45373  (322 TD, 80 INT, 178 games)
- Marguerite Flanagan (QB): 44096  (249 TD, 81 INT, 172 games)

**Rushing yards** (all 10 seasons combined)

- Jocelyn Vickers (RB): 14055  (3152 carries, 4.5 avg)
- Maeve McAllister (RB): 12791  (3109 carries, 4.1 avg)
- Vesper Merrick (RB): 12715  (2910 carries, 4.4 avg)
- Amina Toussaint (RB): 12517  (2727 carries, 4.6 avg)
- Hattie Hightower (RB): 12332  (2702 carries, 4.6 avg)

**Receiving yards** (all 10 seasons combined)

- Eliana Hammond (WR): 13259  (1211 catches, 93 TD)
- Jocelyn Dubois (WR): 12667  (1154 catches, 74 TD)
- Matilda Kirkland (WR): 12454  (1053 catches, 67 TD)
- Andrea Camacho (WR): 12252  (1110 catches, 92 TD)
- Mabel Colburn (WR): 11892  (1073 catches, 75 TD)

**Sacks** (all 10 seasons combined)

- Daniela Nettles (DL): 132  
- Kalani Fennimore (DL): 122  
- Bridget Farrow (DL): 114  
- Dahlia Dietrich (DL): 114  
- Zadie Barrientos (DL): 108  

**Interceptions** (all 10 seasons combined)

- Galina Iverson (CB): 38  
- Kyra Alderman (CB): 32  
- Monique Galloway (CB): 29  
- Yasmin Fuentes (CB): 28  
- Bianca Blackwood (CB): 28  

## Parity

- Team strength spread (standard deviation of team power ratings, points): 3.3 on average (range 2.7 to 3.9).
- Regular-season win percentage of the 40 active teams: sd 0.151; best 5% about 0.778, worst 5% about 0.222.

## Injuries

- About 276 injuries per season league-wide, roughly 5.7 per team. Rates and lengths are placeholder dials in injuries.py.

## Roster offseason (per year, whole league)

| Retirements | Contracts ended | Free-agent signings | Premium (exile relief) signings | Rookies drafted | Street free agents needed |
| --- | --- | --- | --- | --- | --- |
| 209 | 290 | 398 | 0.4 | 48 | 2 |

## Exile target on the roster model

Where a team that has just come back from exile finishes in its division. Your target: it should have the potential to compete for about 3rd, sometimes succeeding and sometimes not. A league-average team finishes 3.0 on average, so about 3.0 to 3.3 hits the target.

| Engine | Leagues x seasons | Average finish | 1st | 2nd | 3rd | 4th | 5th (exiled again) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fast | 8 x 40 | 3.12 (+/- 0.06) | 18% | 19% | 19% | 20% | 23% |
| drives | 4 x 40 | 3.12 (+/- 0.09) | 19% | 17% | 20% | 20% | 24% |

`fast` decides a game from the two teams' power ratings; `drives` plays the whole game. They agree, which is the point of the fast mode: long studies can use it.
