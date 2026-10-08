# Phase 2 report: rosters and the drive-by-drive game engine

Seed 1, 10 seasons, drive engine. Players have names and cards (see card_samples.md). Every number here comes from placeholder dials, not from league rules.

## Sample box score: the season-1 championship game

### Team 38 at Team 01  -  week 23, playoff final
**Final: Team 38 33, Team 01 17**

| | Team 01 (home) | Team 38 (away) |
|---|---|---|
| Total yards | 303 | 432 |
| Plays | 55 | 68 |
| Passing | 26/38, 275 yds | 29/36, 327 yds |
| Rushing | 15 car, 39 yds | 32 car, 105 yds |
| First downs | 19 | 25 |
| 3rd down | 4/10 | 8/14 |
| Turnovers | 2 | 0 |
| Sacks by defense | 0 | 2 |
| Punts | 4 | 2 |
| Time of possession | 23:53 | 36:07 |

**Team 01**
- Passing: Simone Chavez (QB) 26/38, 275 yds, 1 TD, 1 INT, sacked 2
- Rushing: Haruka Montoya (RB) 9 car, 28 yds (3.1), 0 TD; Treasure Christensen (RB) 6 car, 11 yds (1.8), 1 TD
- Receiving: Haruka Montoya (RB) 6 rec on 6 tgt, 56 yds, 0 TD; Anneke Fontaine (WR) 6 rec on 9 tgt, 76 yds, 0 TD; Jasmine Morrow (WR) 5 rec on 7 tgt, 57 yds, 0 TD; Marguerite Schaefer (WR) 3 rec on 9 tgt, 47 yds, 1 TD; Carys Fuentes (TE) 6 rec on 7 tgt, 39 yds, 0 TD
- Kicking: Wanda Paddock (K) FG 1/1; Bianca Vandermeer (P) 4 punts, 43.0 avg
- Defense: Kaia Kincaid (DL) 6 tkl, 0 sack, 0 INT; Mika Nolan (DL) 5 tkl, 0 sack, 0 INT; Adriana Baptiste (DL) 5 tkl, 0 sack, 0 INT; Paloma Oakley (DL) 4 tkl, 0 sack, 0 INT; Tove Tavares (LB) 8 tkl, 0 sack, 0 INT; Elise Danforth (LB) 6 tkl, 0 sack, 0 INT; Zadie Tillman (CB) 4 tkl, 0 sack, 0 INT; Natalia Landry (CB) 7 tkl, 0 sack, 0 INT; Alina Underhill (S) 9 tkl, 0 sack, 0 INT; Laila Duarte (CB) 2 tkl, 0 sack, 0 INT; Jamila Briggs (S) 5 tkl, 0 sack, 0 INT

**Team 38**
- Passing: Felicity Medina (QB) 29/36, 327 yds, 3 TD, 0 INT, sacked 0
- Rushing: Simone Chambers (RB) 19 car, 52 yds (2.7), 0 TD; Concetta Jarrett (RB) 13 car, 53 yds (4.1), 0 TD
- Receiving: Simone Chambers (RB) 5 rec on 8 tgt, 41 yds, 1 TD; Layla Rutledge (WR) 10 rec on 11 tgt, 108 yds, 0 TD; Paulina Ahlberg (WR) 5 rec on 5 tgt, 38 yds, 1 TD; Treasure Chavez (WR) 4 rec on 6 tgt, 78 yds, 1 TD; P02568 (TE) 5 rec on 6 tgt, 62 yds, 0 TD
- Kicking: Ines Dellinger (K) FG 4/4; Lola Greer (P) 2 punts, 41.5 avg
- Defense: Willa Aoki (DL) 6 tkl, 0 sack, 0 INT; Fatima Galloway (DL) 2 tkl, 1 sack, 0 INT; Kaia Kendrick (DL) 4 tkl, 1 sack, 0 INT; Adriana Atwood (DL) 4 tkl, 0 sack, 0 INT; Lara Kincaid (LB) 6 tkl, 0 sack, 0 INT; Tove Stratton (LB) 6 tkl, 0 sack, 0 INT; Malia Kowalski (CB) 0 tkl, 0 sack, 1 INT; Zadie Tavares (CB) 4 tkl, 0 sack, 0 INT; Sylvie Okafor (S) 3 tkl, 0 sack, 0 INT; Delphine Bellamy (S) 3 tkl, 0 sack, 0 INT; Adaeze Palmieri (CB) 3 tkl, 0 sack, 0 INT

**Drive log**

| # | Team | Qtr | Start | Plays | Yds | Time | Result |
|---|---|---|---|---|---|---|---|
| 1 | Team 38 | 1 | own 34 | 10 | 66 | 4:46 | TD |
| 2 | Team 01 | 1 | own 31 | 5 | 69 | 2:45 | TD |
| 3 | Team 38 | 1 | own 31 | 6 | 69 | 2:49 | TD |
| 4 | Team 01 | 1 | own 31 | 3 | -1 | 1:55 | PUNT |
| 5 | Team 38 | 1 | own 31 | 9 | 69 | 5:42 | TD |
| 6 | Team 01 | 2 | own 31 | 11 | 61 | 4:57 | FG |
| 7 | Team 38 | 2 | own 24 | 6 | 53 | 2:23 | FG |
| 8 | Team 01 | 2 | own 31 | 6 | 60 | 2:41 | FUMBLE |
| 9 | Team 38 | 2 | own 9 | 4 | 12 | 1:57 | END_PERIOD |
| 10 | Team 01 | 3 | own 31 | 3 | 9 | 1:16 | PUNT |
| 11 | Team 38 | 3 | own 15 | 7 | 44 | 3:34 | PUNT |
| 12 | Team 01 | 3 | own 13 | 3 | 4 | 1:42 | PUNT |
| 13 | Team 38 | 3 | own 37 | 12 | 60 | 6:44 | FG |
| 14 | Team 01 | 3 | own 18 | 3 | -1 | 1:03 | PUNT |
| 15 | Team 38 | 3 | own 39 | 4 | 30 | 2:40 | FG |
| 16 | Team 01 | 4 | own 31 | 2 | 0 | 0:13 | INT |
| 17 | Team 38 | 4 | own 57 | 4 | 17 | 1:41 | FG |
| 18 | Team 01 | 4 | own 31 | 10 | 69 | 5:04 | TD |
| 19 | Team 38 | 4 | own 17 | 5 | 10 | 3:25 | PUNT |
| 20 | Team 01 | 4 | own 31 | 9 | 33 | 2:12 | DOWNS |
| 21 | Team 38 | 4 | own 36 | 1 | 2 | 0:21 | END_PERIOD |

## League stats over 10 seasons (8040 team-games, regular season, Ambassador and playoffs)

| Measure (per team per game unless noted) | This league | Football-like target | Within range? |
| --- | --- | --- | --- |
| points | 21.21 | 22.00 (+/- 1.5) | yes |
| plays | 62.95 | 63.50 (+/- 3.0) | yes |
| pass att | 33.55 | 33.50 (+/- 2.0) | yes |
| completion pct | 66.90 | 65.00 (+/- 2.0) | yes |
| yards per attempt | 7.15 | 6.90 (+/- 0.5) | yes |
| rush att | 27.00 | 26.50 (+/- 2.0) | yes |
| yards per carry | 4.20 | 4.30 (+/- 0.3) | yes |
| total yards | 338.69 | 340.00 (+/- 25.0) | yes |
| sacks taken | 2.39 | 2.50 (+/- 0.5) | yes |
| punts | 4.25 | 4.30 (+/- 0.8) | yes |
| first downs | 20.03 | 20.00 (+/- 2.5) | yes |
| third down pct | 42.57 | 40.00 (+/- 4.0) | yes |
| fg attempts | 2.17 | 1.90 (+/- 0.5) | yes |
| fg pct | 85.55 | 84.00 (+/- 5.0) | yes |
| drives | 10.88 | 11.00 (+/- 1.2) | yes |
| time of possession min | 30.28 | 30.00 (+/- 1.5) | yes |
| game margin sd | 12.64 | 13.50 (+/- 1.5) | yes |
| home win pct | 55.64 | 54.00 (+/- 3.0) | yes |

Targets are rough NFL-style figures chosen by the AI as a stand-in for "looks like football". They are not rules and not your decisions.

## Career leaders in the simulated seasons

**Passing yards** (all 10 seasons combined)

- Chiara Moreau (QB): 42572  (289 TD, 81 INT, 164 games)
- Dominique Ibarra (QB): 39058  (254 TD, 70 INT, 155 games)
- Serena Rasmussen (QB): 37773  (266 TD, 63 INT, 137 games)
- Helena Crenshaw (QB): 37674  (248 TD, 74 INT, 147 games)
- Laila Boateng (QB): 36979  (198 TD, 94 INT, 158 games)

**Rushing yards** (all 10 seasons combined)

- Josie Gaudet (RB): 11031  (2523 carries, 4.4 avg)
- Xiomara Macalister (RB): 10506  (2269 carries, 4.6 avg)
- Gabriela Solberg (RB): 10443  (2467 carries, 4.2 avg)
- Helena Cordero (RB): 10225  (2377 carries, 4.3 avg)
- Roxanne Eastwood (RB): 10133  (2356 carries, 4.3 avg)

**Receiving yards** (all 10 seasons combined)

- Kaia Ashby (WR): 10715  (1009 catches, 61 TD)
- Helena Arceneaux (WR): 10659  (1005 catches, 61 TD)
- Esperanza Jefferson (WR): 10378  (964 catches, 67 TD)
- Lupe Brightwater (WR): 9444  (914 catches, 46 TD)
- Ivy Sheridan (WR): 9248  (860 catches, 45 TD)

**Sacks** (all 10 seasons combined)

- Phoebe Stanhope (DL): 118  
- Julia Maldonado (DL): 113  
- Esme Gentry (DL): 108  
- Sabine Kaplan (DL): 101  
- Freya Ostrander (DL): 96  

**Interceptions** (all 10 seasons combined)

- Hadley Calloway (CB): 25  
- Jelena Emerson (CB): 24  
- Olive Holmgren (CB): 24  
- Imani Brightwater (CB): 24  
- Mika Crenshaw (CB): 22  

## Parity

- Team strength spread (standard deviation of team power ratings, points): 2.7 on average (range 2.2 to 3.1).
- Regular-season win percentage of the 40 active teams: sd 0.137; best 5% about 0.722, worst 5% about 0.278.

## Injuries

- About 1586 injuries per season league-wide, roughly 33.0 per team. Rates and lengths are model dials in injuries.py (about the NFL's, Step 8).

## Roster offseason (per year, whole league)

| Retirements | Contracts ended | Free-agent signings | Premium (exile relief) signings | Rookies drafted | Street free agents needed |
| --- | --- | --- | --- | --- | --- |
| 109 | 1100 | 573 | 0.0 | 338 | 189 |

## Exile target on the roster model

Where a team that has just come back from exile finishes in its division. Your target: it should have the potential to compete for about 3rd, sometimes succeeding and sometimes not. A league-average team finishes 3.0 on average, so about 3.0 to 3.3 hits the target.

| Engine | Leagues x seasons | Average finish | 1st | 2nd | 3rd | 4th | 5th (exiled again) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fast | 8 x 40 | 3.17 (+/- 0.06) | 17% | 18% | 19% | 21% | 24% |
| drives | 4 x 40 | 3.19 (+/- 0.09) | 17% | 19% | 18% | 23% | 24% |

`fast` decides a game from the two teams' power ratings; `drives` plays the whole game. They agree, which is the point of the fast mode: long studies can use it.
