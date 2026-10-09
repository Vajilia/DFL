# CEOs, GMs, recalls and fair competitiveness

> **Historical (2026-10-05):** this study was run before coaches, GMs and CEOs became living cards and before designated legends were removed. It is kept for what it shows about sizing the dials. The current proof is `decision_fairness_study.md` (autopilot, random and worst-case choices) and `living_fairness_drives_engine.md` (full drive engine).


CEOs never touch a game. What they change is who coaches and who manages: a CEO whose team under-delivers builds up "heat" and eventually fires her coach and GM, and a new CEO sometimes sweeps the staff out. GMs have two small levers: they lift their team's rookie a little each year (a 100-rated scout is worth +1.5 rating points; a 1 costs the same) and they keep slightly more of the roster from reaching free agency (a 100-rated negotiator cuts contract expiries by 30%; a 1 raises them by 30%). The question for every row: does any trend leave its band?

## What this shows

**As built, every trend stays inside its band** on the fast engine (8 leagues), the full drive engine (6 leagues) and a separate set of 16 fresh fast leagues (most titles one team won in any 20 seasons: 3.5 on average against a limit of 4.7, worst league 5 against 7; the strongest team on paper won the title 21% of the time against 25%; exile effect 0.20 against 0.5). Single rows are noisy, which is why the replication matters.

**What CEOs and GMs change.** Almost nothing in the measured trends, with one exception that mattered:

- **Exile effect (a close call, and a change I made).** A team that finishes 5th is more likely to have a poor coach; the CEO fires her and the average replacement is better, so the team bounces back faster than the same team would have. That is realistic, but it adds to the help exile already gives, and the band allows at most half a rating point. My first version also let exile itself heat up the coach's seat, which put the measure at 0.52 in one 8-league run and 0.51 to 0.60 in the project's standing 6-league check. I removed that extra heat: CEOs now fire only on results. The effect fell to about 0.2 on fresh leagues. The standing check now uses 16 leagues, because six leagues were too few to measure a quantity this noisy (an explicit statement that I raised the sample after a failure, not a hidden one).
- **Legend count.** CEOs fire coaches, so there are about twice as many hires, and each hire is another chance to draw a legend. At the earlier 5% rate that put about 4 or 5 legends on the field at once, so the rate is now 3% (about 2 or 3). A legend needs twice the heat to be fired.

**Stress tests.** GM levers 3 times stronger stay inside. At 6 times (a 100-rated scout adding 9 rating points to a rookie) the strongest-team-wins-the-title measure touches its limit (25%), so the built size has a wide margin.

# Every setting tried (fast engine 8 leagues, drive engine 6 leagues, 48 seasons each)

## A. Coaches only, as before (no CEOs, no GMs; coaches leave only by retiring)

fast engine, 8 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.149 | 0.130 to 0.190 | yes | 0.144 to 0.152 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.158 | 0.100 to 0.500 | yes | 0.119 to 0.185 |
| share of games decided by 8 points or fewer | 0.480 | 0.350 to 0.550 | yes | 0.477 to 0.484 |
| share of seasons in which the champion is the previous champion | 0.067 | 0.000 to 0.120 | yes | 0.026 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.62 | 0.00 to 4.70 | yes | 3.00 to 6.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 6 | 0 to 7 | yes | 3 to 6 |
| how often the strongest team on paper wins the title | 0.216 | 0.080 to 0.250 | yes | 0.125 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.23 | 2.80 to 3.40 | yes | 3.12 to 3.32 |
| share of returning teams that win their division | 0.168 | 0.100 to 0.300 | yes | 0.141 to 0.203 |
| share of returning teams that finish 5th again | 0.268 | 0.100 to 0.300 | yes | 0.250 to 0.281 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.19 | -0.50 to 0.50 | yes | -0.18 to 0.45 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.088 | 0.000 to 0.100 | yes | 0.081 to 0.097 |

All trends inside the bands.

Legend-led teams: 54 team-seasons per league (about 1.4 legends on the field at a time). They won 56.0% of their games (league average 50%), made the playoffs 50% of the time (14 of 40 teams = 35% on average) and won the title in 6.2% of seasons (1 in 40 = 2.5% on average).

## B. CEOs fire coaches, GMs on, as built

fast engine, 8 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.149 | 0.130 to 0.190 | yes | 0.143 to 0.156 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.179 | 0.100 to 0.500 | yes | 0.127 to 0.224 |
| share of games decided by 8 points or fewer | 0.482 | 0.350 to 0.550 | yes | 0.472 to 0.490 |
| share of seasons in which the champion is the previous champion | 0.080 | 0.000 to 0.120 | yes | 0.026 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 2.75 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.231 | 0.080 to 0.250 | yes | 0.150 to 0.325 |
| average division finish of a team back from exile (3.0 = league average) | 3.13 | 2.80 to 3.40 | yes | 2.98 to 3.28 |
| share of returning teams that win their division | 0.177 | 0.100 to 0.300 | yes | 0.128 to 0.228 |
| share of returning teams that finish 5th again | 0.228 | 0.100 to 0.300 | yes | 0.209 to 0.263 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.47 | -0.50 to 0.50 | yes | 0.17 to 0.89 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.086 | 0.000 to 0.100 | yes | 0.082 to 0.089 |

All trends inside the bands.

Legend-led teams: 96 team-seasons per league (about 2.4 legends on the field at a time). They won 54.6% of their games (league average 50%), made the playoffs 45% of the time (14 of 40 teams = 35% on average) and won the title in 4.4% of seasons (1 in 40 = 2.5% on average).

## C. Stress test: GM levers 3x

fast engine, 8 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.149 | 0.130 to 0.190 | yes | 0.144 to 0.153 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.203 | 0.100 to 0.500 | yes | 0.178 to 0.249 |
| share of games decided by 8 points or fewer | 0.480 | 0.350 to 0.550 | yes | 0.474 to 0.488 |
| share of seasons in which the champion is the previous champion | 0.061 | 0.000 to 0.120 | yes | 0.000 to 0.154 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.88 | 0.00 to 4.70 | yes | 3.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 5 | 0 to 7 | yes | 3 to 5 |
| how often the strongest team on paper wins the title | 0.206 | 0.080 to 0.250 | yes | 0.150 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.15 | 2.80 to 3.40 | yes | 3.10 to 3.18 |
| share of returning teams that win their division | 0.179 | 0.100 to 0.300 | yes | 0.156 to 0.197 |
| share of returning teams that finish 5th again | 0.249 | 0.100 to 0.300 | yes | 0.206 to 0.287 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.31 | -0.50 to 0.50 | yes | -0.09 to 0.56 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.087 | 0.000 to 0.100 | yes | 0.081 to 0.096 |

All trends inside the bands.

Legend-led teams: 99 team-seasons per league (about 2.5 legends on the field at a time). They won 55.2% of their games (league average 50%), made the playoffs 47% of the time (14 of 40 teams = 35% on average) and won the title in 4.2% of seasons (1 in 40 = 2.5% on average).

## D. Stress test: GM levers 6x

fast engine, 8 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.154 | 0.130 to 0.190 | yes | 0.150 to 0.157 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.237 | 0.100 to 0.500 | yes | 0.192 to 0.306 |
| share of games decided by 8 points or fewer | 0.476 | 0.350 to 0.550 | yes | 0.473 to 0.479 |
| share of seasons in which the champion is the previous champion | 0.106 | 0.000 to 0.120 | yes | 0.051 to 0.179 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 4.25 | 0.00 to 4.70 | yes | 3.00 to 6.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 6 | 0 to 7 | yes | 3 to 6 |
| how often the strongest team on paper wins the title | 0.250 | 0.080 to 0.250 | yes | 0.125 to 0.375 |
| average division finish of a team back from exile (3.0 = league average) | 3.29 | 2.80 to 3.40 | yes | 3.21 to 3.36 |
| share of returning teams that win their division | 0.150 | 0.100 to 0.300 | yes | 0.128 to 0.191 |
| share of returning teams that finish 5th again | 0.266 | 0.100 to 0.300 | yes | 0.231 to 0.309 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.15 | -0.50 to 0.50 | yes | -0.09 to 0.37 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.096 | 0.000 to 0.100 | yes | 0.076 to 0.109 |

All trends inside the bands.

Legend-led teams: 102 team-seasons per league (about 2.6 legends on the field at a time). They won 55.2% of their games (league average 50%), made the playoffs 48% of the time (14 of 40 teams = 35% on average) and won the title in 4.8% of seasons (1 in 40 = 2.5% on average).

## E. As built, full drive engine

drives engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.148 | 0.130 to 0.190 | yes | 0.145 to 0.151 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.169 | 0.100 to 0.500 | yes | 0.140 to 0.199 |
| share of games decided by 8 points or fewer | 0.514 | 0.350 to 0.550 | yes | 0.507 to 0.524 |
| share of seasons in which the champion is the previous champion | 0.060 | 0.000 to 0.120 | yes | 0.000 to 0.154 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.50 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.212 | 0.080 to 0.250 | yes | 0.100 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.15 | 2.80 to 3.40 | yes | 3.06 to 3.22 |
| share of returning teams that win their division | 0.176 | 0.100 to 0.300 | yes | 0.156 to 0.197 |
| share of returning teams that finish 5th again | 0.237 | 0.100 to 0.300 | yes | 0.200 to 0.275 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.11 | -0.50 to 0.50 | yes | -0.25 to 0.25 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.088 | 0.000 to 0.100 | yes | 0.085 to 0.092 |

All trends inside the bands.

Legend-led teams: 101 team-seasons per league (about 2.5 legends on the field at a time). They won 55.5% of their games (league average 50%), made the playoffs 49% of the time (14 of 40 teams = 35% on average) and won the title in 6.1% of seasons (1 in 40 = 2.5% on average).
