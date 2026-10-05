# Fanbase and media cards, and fair competitiveness

> **Historical (2026-10-05):** this study was run before coaches, GMs and owners became living cards and before designated legends were removed. It is kept for what it shows about sizing the dials. The current proof is `decision_fairness_study.md` (autopilot, random and worst-case choices) and `living_fairness_drives_engine.md` (full drive engine).


Fans and the press never touch a game. A fanbase's culture and ratings decide how an owner's approval responds to a season (how patient, how demanding, how moody, how much it believes the press). The press moves approval by at most 3 points a year (more in a big market, to a trusting fanbase). Fan Capital, the slow store of goodwill, only ever buffers a recall vote. Approval decides recalls, and a recall can lead to a coach or GM being fired, so the only road to the field is long. The question for every row: does any trend leave its band?

## A. Old placeholder approval model (owners, GMs and coaches, no fan or media cards)

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

## B. Fanbase and media cards, as built

fast engine, 8 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.150 | 0.130 to 0.190 | yes | 0.146 to 0.155 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.165 | 0.100 to 0.500 | yes | 0.134 to 0.222 |
| share of games decided by 8 points or fewer | 0.478 | 0.350 to 0.550 | yes | 0.474 to 0.481 |
| share of seasons in which the champion is the previous champion | 0.071 | 0.000 to 0.120 | yes | 0.026 to 0.154 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.00 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.216 | 0.080 to 0.250 | yes | 0.125 to 0.425 |
| average division finish of a team back from exile (3.0 = league average) | 3.23 | 2.80 to 3.40 | yes | 3.12 to 3.38 |
| share of returning teams that win their division | 0.157 | 0.100 to 0.300 | yes | 0.131 to 0.194 |
| share of returning teams that finish 5th again | 0.258 | 0.100 to 0.300 | yes | 0.231 to 0.294 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.22 | -0.50 to 0.50 | yes | -0.14 to 0.52 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.088 | 0.000 to 0.100 | yes | 0.084 to 0.099 |

All trends inside the bands.

Legend-led teams: 101 team-seasons per league (about 2.5 legends on the field at a time). They won 56.6% of their games (league average 50%), made the playoffs 50% of the time (14 of 40 teams = 35% on average) and won the title in 5.7% of seasons (1 in 40 = 2.5% on average).

## C. Stress test: the press 3x stronger and Fan Capital 3x stronger

fast engine, 8 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.150 | 0.130 to 0.190 | yes | 0.147 to 0.155 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.167 | 0.100 to 0.500 | yes | 0.151 to 0.188 |
| share of games decided by 8 points or fewer | 0.484 | 0.350 to 0.550 | yes | 0.480 to 0.491 |
| share of seasons in which the champion is the previous champion | 0.061 | 0.000 to 0.120 | yes | 0.026 to 0.179 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.38 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.191 | 0.080 to 0.250 | yes | 0.125 to 0.325 |
| average division finish of a team back from exile (3.0 = league average) | 3.17 | 2.80 to 3.40 | yes | 3.11 to 3.29 |
| share of returning teams that win their division | 0.163 | 0.100 to 0.300 | yes | 0.153 to 0.172 |
| share of returning teams that finish 5th again | 0.234 | 0.100 to 0.300 | yes | 0.203 to 0.259 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.24 | -0.50 to 0.50 | yes | 0.01 to 0.53 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.087 | 0.000 to 0.100 | yes | 0.076 to 0.094 |

All trends inside the bands.

Legend-led teams: 99 team-seasons per league (about 2.5 legends on the field at a time). They won 55.9% of their games (league average 50%), made the playoffs 50% of the time (14 of 40 teams = 35% on average) and won the title in 4.0% of seasons (1 in 40 = 2.5% on average).

## D. Stress test: the press 6x stronger and Fan Capital 6x stronger

fast engine, 8 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.150 | 0.130 to 0.190 | yes | 0.148 to 0.155 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.161 | 0.100 to 0.500 | yes | 0.122 to 0.217 |
| share of games decided by 8 points or fewer | 0.481 | 0.350 to 0.550 | yes | 0.474 to 0.488 |
| share of seasons in which the champion is the previous champion | 0.038 | 0.000 to 0.120 | yes | 0.000 to 0.154 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.38 | 0.00 to 4.70 | yes | 2.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 5 | 0 to 7 | yes | 2 to 5 |
| how often the strongest team on paper wins the title | 0.253 | 0.080 to 0.250 | **NO** | 0.200 to 0.350 |
| average division finish of a team back from exile (3.0 = league average) | 3.17 | 2.80 to 3.40 | yes | 3.06 to 3.25 |
| share of returning teams that win their division | 0.175 | 0.100 to 0.300 | yes | 0.144 to 0.212 |
| share of returning teams that finish 5th again | 0.238 | 0.100 to 0.300 | yes | 0.203 to 0.263 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.36 | -0.50 to 0.50 | yes | -0.02 to 0.67 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.082 | 0.000 to 0.100 | yes | 0.071 to 0.088 |

**Outside the bands:** best_team_title_odds.

Legend-led teams: 102 team-seasons per league (about 2.6 legends on the field at a time). They won 55.7% of their games (league average 50%), made the playoffs 46% of the time (14 of 40 teams = 35% on average) and won the title in 5.4% of seasons (1 in 40 = 2.5% on average).

## E. As built, full drive engine

drives engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.145 to 0.150 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.178 | 0.100 to 0.500 | yes | 0.118 to 0.204 |
| share of games decided by 8 points or fewer | 0.512 | 0.350 to 0.550 | yes | 0.507 to 0.518 |
| share of seasons in which the champion is the previous champion | 0.081 | 0.000 to 0.120 | yes | 0.026 to 0.154 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.17 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.183 | 0.080 to 0.250 | yes | 0.125 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.20 | 2.80 to 3.40 | yes | 3.05 to 3.34 |
| share of returning teams that win their division | 0.172 | 0.100 to 0.300 | yes | 0.125 to 0.209 |
| share of returning teams that finish 5th again | 0.259 | 0.100 to 0.300 | yes | 0.222 to 0.300 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.28 | -0.50 to 0.50 | yes | 0.09 to 0.55 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.084 | 0.000 to 0.100 | yes | 0.073 to 0.099 |

All trends inside the bands.

Legend-led teams: 100 team-seasons per league (about 2.5 legends on the field at a time). They won 57.1% of their games (league average 50%), made the playoffs 54% of the time (14 of 40 teams = 35% on average) and won the title in 6.3% of seasons (1 in 40 = 2.5% on average).

## What this shows

As built (rows B and E) every trend is inside its band, on the fast engine (8 leagues of 48 seasons) and the full drive engine (6 leagues).
Tripling the press and Fan Capital (row C) is still inside. At six times (row D) one trend, how often the strongest team on paper wins the title,
reaches 0.253 against a band edge of 0.25, so the built dial sits well short of where it starts to matter. The road from fans and media to the
field is long (press, approval, recall, a new owner, a fired coach), which is why the effect is small.

Two things to keep in view. First, these are samples of 6 to 8 leagues; row A (the old model, no fan cards) showed an exile effect of 0.47 here
against 0.22 for row B, and the two models should not differ that much, so the exile effect is noisy in a sample this size (its band edge is 0.5). Second,
the recall rate moved a little: about 4.3 recalls a year with the fan cards against 3.9 with the old formula, and average owner tenure about 5.3 years
against 5.6. Both stay close to what the old formula gave.
