# Phase 2 report: rosters and the drive-by-drive game engine

Seed 1, 10 seasons, drive engine. Players have names and cards (see card_samples.md). Every number here comes from placeholder dials, not from league rules.

## Sample box score: the season-1 championship game

### Team 15 at Team 31  -  week 23, playoff final
**Final: Team 15 20, Team 31 31**

| | Team 31 (home) | Team 15 (away) |
|---|---|---|
| Total yards | 488 | 269 |
| Plays | 76 | 52 |
| Passing | 29/43, 350 yds | 22/36, 217 yds |
| Rushing | 31 car, 151 yds | 16 car, 52 yds |
| First downs | 32 | 15 |
| 3rd down | 9/12 | 5/12 |
| Turnovers | 2 | 1 |
| Sacks by defense | 0 | 2 |
| Punts | 2 | 6 |
| Time of possession | 37:33 | 22:27 |

**Team 31**
- Passing: Helena Garrison (QB) 29/43, 350 yds, 1 TD, 0 INT, sacked 2
- Rushing: Vera Stanhope (RB) 14 car, 69 yds (4.9), 1 TD; Astrid Avery (RB) 17 car, 82 yds (4.8), 2 TD
- Receiving: Vera Stanhope (RB) 4 rec on 6 tgt, 65 yds, 1 TD; Matilda Kirkland (WR) 7 rec on 9 tgt, 91 yds, 0 TD; Saoirse Novak (WR) 8 rec on 15 tgt, 90 yds, 0 TD; Greta Dalton (WR) 5 rec on 6 tgt, 58 yds, 0 TD; Nova Kruger (TE) 5 rec on 7 tgt, 46 yds, 0 TD
- Kicking: Isabel Waller (K) FG 1/1; Lupe Brightwater (P) 2 punts, 45.0 avg
- Defense: Alana Paddock (DL) 1 tkl, 0 sack, 0 INT; Dahlia Valdez (DL) 1 tkl, 0 sack, 0 INT; Liesel Dietrich (DL) 1 tkl, 0 sack, 0 INT; Petra Gunnarsson (DL) 5 tkl, 0 sack, 0 INT; Valentina Leclair (LB) 5 tkl, 0 sack, 0 INT; Aria Pappas (LB) 3 tkl, 0 sack, 0 INT; Zoe Lockhart (CB) 5 tkl, 0 sack, 0 INT; Catalina Peralta (CB) 3 tkl, 0 sack, 0 INT; Grace Villanueva (CB) 6 tkl, 0 sack, 0 INT; Noor Dunmore (S) 4 tkl, 0 sack, 0 INT; Tatiana Hargrove (S) 4 tkl, 0 sack, 1 INT

**Team 15**
- Passing: Destiny Solberg (QB) 22/36, 217 yds, 2 TD, 1 INT, sacked 0
- Rushing: Rafaela Galloway (RB) 9 car, 29 yds (3.2), 1 TD; Brenna Nightingale (RB) 7 car, 23 yds (3.3), 0 TD
- Receiving: Rafaela Galloway (RB) 6 rec on 8 tgt, 52 yds, 1 TD; Kaia Atwood (WR) 4 rec on 8 tgt, 41 yds, 0 TD; Mika Crenshaw (WR) 5 rec on 9 tgt, 83 yds, 1 TD; Adriana Kirkland (WR) 2 rec on 4 tgt, 16 yds, 0 TD; Lara Baptiste (TE) 5 rec on 7 tgt, 25 yds, 0 TD
- Kicking: Jamila Lovett (P) 6 punts, 46.2 avg
- Defense: Kenna Toussaint (DL) 5 tkl, 0 sack, 0 INT; Natalia Bellamy (DL) 5 tkl, 0 sack, 0 INT; Sylvie Dellinger (DL) 3 tkl, 1 sack, 0 INT; Alina Griffith (DL) 4 tkl, 0 sack, 0 INT; Rachelle Bergstrom (LB) 7 tkl, 1 sack, 0 INT; Wanda Devereux (LB) 12 tkl, 0 sack, 0 INT; Mercy Vandermeer (CB) 7 tkl, 0 sack, 0 INT; Sienna Boateng (CB) 4 tkl, 0 sack, 0 INT; Adaeze Dubois (CB) 3 tkl, 0 sack, 0 INT; Oona Vickers (S) 7 tkl, 0 sack, 0 INT; Angela Dunmore (S) 3 tkl, 0 sack, 0 INT

**Drive log**

| # | Team | Qtr | Start | Plays | Yds | Time | Result |
|---|---|---|---|---|---|---|---|
| 1 | Team 15 | 1 | own 31 | 8 | 69 | 3:50 | TD |
| 2 | Team 31 | 1 | own 31 | 5 | 15 | 2:00 | PUNT |
| 3 | Team 15 | 1 | own 18 | 3 | 4 | 0:59 | PUNT |
| 4 | Team 31 | 1 | own 39 | 10 | 61 | 6:00 | TD |
| 5 | Team 15 | 1 | own 31 | 5 | 18 | 2:34 | PUNT |
| 6 | Team 31 | 2 | own 3 | 5 | 22 | 2:08 | PUNT |
| 7 | Team 15 | 2 | own 38 | 4 | 16 | 1:42 | PUNT |
| 8 | Team 31 | 2 | own 12 | 4 | 4 | 2:13 | FUMBLE |
| 9 | Team 15 | 2 | own 84 | 3 | 16 | 1:43 | TD |
| 10 | Team 31 | 2 | own 31 | 10 | 69 | 4:15 | TD |
| 11 | Team 15 | 2 | own 31 | 3 | 5 | 1:14 | PUNT |
| 12 | Team 31 | 2 | own 19 | 4 | 23 | 1:17 | END_PERIOD |
| 13 | Team 31 | 3 | own 29 | 6 | 71 | 3:15 | TD |
| 14 | Team 15 | 3 | own 31 | 3 | 8 | 2:16 | PUNT |
| 15 | Team 31 | 3 | own 23 | 8 | 61 | 4:45 | FUMBLE |
| 16 | Team 15 | 3 | own 16 | 6 | 16 | 2:27 | PUNT |
| 17 | Team 31 | 3 | own 30 | 8 | 54 | 3:54 | FG |
| 18 | Team 15 | 4 | own 31 | 8 | 69 | 3:36 | TD |
| 19 | Team 31 | 4 | own 22 | 11 | 78 | 4:52 | TD |
| 20 | Team 15 | 4 | own 31 | 9 | 48 | 2:01 | INT |
| 21 | Team 31 | 4 | own 16 | 5 | 30 | 2:49 | END_PERIOD |

## League stats over 10 seasons (8040 team-games, regular season, Ambassador and playoffs)

| Measure (per team per game unless noted) | This league | Football-like target | Within range? |
| --- | --- | --- | --- |
| points | 21.65 | 22.00 (+/- 1.5) | yes |
| plays | 62.80 | 63.50 (+/- 3.0) | yes |
| pass att | 33.46 | 33.50 (+/- 2.0) | yes |
| completion pct | 67.34 | 65.00 (+/- 2.0) | NO |
| yards per attempt | 7.28 | 6.90 (+/- 0.5) | yes |
| rush att | 26.99 | 26.50 (+/- 2.0) | yes |
| yards per carry | 4.19 | 4.30 (+/- 0.3) | yes |
| total yards | 342.76 | 340.00 (+/- 25.0) | yes |
| sacks taken | 2.35 | 2.50 (+/- 0.5) | yes |
| punts | 4.19 | 4.30 (+/- 0.8) | yes |
| first downs | 20.23 | 20.00 (+/- 2.5) | yes |
| third down pct | 43.10 | 40.00 (+/- 4.0) | yes |
| fg attempts | 2.14 | 1.90 (+/- 0.5) | yes |
| fg pct | 85.82 | 84.00 (+/- 5.0) | yes |
| drives | 10.81 | 11.00 (+/- 1.2) | yes |
| time of possession min | 30.29 | 30.00 (+/- 1.5) | yes |
| game margin sd | 12.98 | 13.50 (+/- 1.5) | yes |
| home win pct | 55.83 | 54.00 (+/- 3.0) | yes |

Targets are rough NFL-style figures chosen by the AI as a stand-in for "looks like football". They are not rules and not your decisions.

## Career leaders in the simulated seasons

**Passing yards** (all 10 seasons combined)

- Cassidy Zeller (QB): 47913  (336 TD, 109 INT, 174 games)
- Vera Crenshaw (QB): 46861  (301 TD, 54 INT, 175 games)
- Hazel Leclair (QB): 46842  (309 TD, 73 INT, 185 games)
- Kyra Kaplan (QB): 46728  (291 TD, 73 INT, 174 games)
- Honor Chambers (QB): 46163  (323 TD, 69 INT, 175 games)

**Rushing yards** (all 10 seasons combined)

- Jocelyn Vickers (RB): 14465  (3057 carries, 4.7 avg)
- Rachelle Lazarus (RB): 12958  (2950 carries, 4.4 avg)
- Vesper Merrick (RB): 12448  (2925 carries, 4.3 avg)
- Esme Cruz (RB): 12112  (2967 carries, 4.1 avg)
- Dominique Everhart (RB): 12040  (2879 carries, 4.2 avg)

**Receiving yards** (all 10 seasons combined)

- Eliana Hammond (WR): 13478  (1229 catches, 97 TD)
- Luna Everhart (WR): 12688  (1097 catches, 90 TD)
- Thalia Clairmont (WR): 12512  (1147 catches, 83 TD)
- Genevieve Brightwater (WR): 12151  (1113 catches, 70 TD)
- Fatima Kimura (WR): 12060  (1101 catches, 71 TD)

**Sacks** (all 10 seasons combined)

- Zadie Barrientos (DL): 152  
- Juana Ferreira (DL): 117  
- Daniela Nettles (DL): 108  
- Concetta Fitzgerald (DL): 105  
- Kenna Lambert (DL): 105  

**Interceptions** (all 10 seasons combined)

- Cleo Pemberton (CB): 33  
- Alba Atwood (CB): 31  
- Jasmine Clairmont (CB): 29  
- Galina Iverson (CB): 29  
- Adriana Avery (CB): 27  

## Parity

- Team strength spread (standard deviation of team power ratings, points): 3.1 on average (range 2.7 to 3.3).
- Regular-season win percentage of the 40 active teams: sd 0.155; best 5% about 0.722, worst 5% about 0.278.

## Injuries

- About 283 injuries per season league-wide, roughly 5.9 per team. Rates and lengths are placeholder dials in injuries.py.

## Roster offseason (per year, whole league)

| Retirements | Contracts ended | Free-agent signings | Premium (exile relief) signings | Rookies drafted | Street free agents needed |
| --- | --- | --- | --- | --- | --- |
| 210 | 289 | 399 | 0.1 | 48 | 4 |

## Exile target on the roster model

Where a team that has just come back from exile finishes in its division. Your target: it should have the potential to compete for about 3rd, sometimes succeeding and sometimes not. A league-average team finishes 3.0 on average, so about 3.0 to 3.3 hits the target.

| Engine | Leagues x seasons | Average finish | 1st | 2nd | 3rd | 4th | 5th (exiled again) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fast | 8 x 40 | 3.17 (+/- 0.06) | 17% | 18% | 20% | 21% | 24% |
| drives | 4 x 40 | 3.16 (+/- 0.09) | 17% | 17% | 20% | 21% | 23% |

`fast` decides a game from the two teams' power ratings; `drives` plays the whole game. They agree, which is the point of the fast mode: long studies can use it.
