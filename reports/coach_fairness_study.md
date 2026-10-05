# Coach effects and fair competitiveness

> **Historical (2026-10-05):** this study was run before coaches, GMs and owners became living cards and before designated legends were removed. It is kept for what it shows about sizing the dials. The current proof is `decision_fairness_study.md` (autopilot, random and worst-case choices) and `living_fairness_drives_engine.md` (full drive engine).


Each coach card has three levers: a lift to the team's offense and defense (a 50 rating is average and does nothing; a 100 is worth the stated points of margin), and a yearly boost to the development of each of her players (a 100 adds the stated rating points per year to every young player, half that to older ones; a 1 takes it away). Rare legends (5% of hires unless stated) have 90-plus ratings on all three. Coaches stay until they retire, so a great coach is a lasting edge. Same leagues and seeds in every row, 48 seasons each (first 8 thrown away). The question for every row: does any trend leave its band?

## What was chosen, and why

**Chosen: team lift 1.0 point, development 0.4 rating points a year, legends 5% of hires (variant E).**

- Development is the lever that matters. At 1.0 it breaks three bands (title concentration, worst league, and the strongest team on paper winning the title). At 0.6 it is inside but close to the title-concentration limit. At 0.4 there is room.
- The team lift is the smaller lever. 1.5 and 2.0 points were inside on the fast engine, but on the full drive engine, 10 leagues of 48 seasons, 1.5 pushed the strongest team on paper to a 21% title rate against a 25% limit and made repeat champions 9.7% of seasons against a 12% limit, so I stayed at 1.0.
- Legends twice as common (10%) also stays inside, so frequency is not the constraint. Size is.

**Full drive engine, 10 leagues x 48 seasons each (the check that decided it):**

| Setting | Most titles by one team in 20 seasons | Worst league | Strongest team wins title | Repeat champions | Legends: win % / playoffs / title |
| --- | --- | --- | --- | --- | --- |
| No coaches (limit) | 3.4 (4.7) | 5 (7) | 16% (25%) | 4.9% (12%) | n/a |
| Lift 1.5, development 0.4 | 3.7 | 5 | 21% | 9.7% | 59% / 58% / 8.4% |
| **Lift 1.0, development 0.4 (chosen)** | 3.3 | 5 | 19% | 7.7% | 57% / 54% / 6.0% |
| Lift 1.0, development 0.25 | 3.4 | 4 | 19% | 7.7% | 55% / 48% / 5.5% |

All inside the bands. For scale: a team led by a legend wins about 57% of its games (league average 50%), makes the playoffs about 54% of the time (the average team makes it 35% of the time) and wins the title about 6% of seasons (the average is 2.5%). That makes a legend a lasting, regular contender; it does not make a dynasty, because a dynasty would break the title-concentration bands.

# Every setting tried (fast engine, 8 leagues x 48 seasons)

## A. No coaches at all (souls only)

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.143 to 0.152 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.163 | 0.100 to 0.500 | yes | 0.136 to 0.225 |
| share of games decided by 8 points or fewer | 0.484 | 0.350 to 0.550 | yes | 0.477 to 0.493 |
| share of seasons in which the champion is the previous champion | 0.061 | 0.000 to 0.120 | yes | 0.026 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.12 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.172 | 0.080 to 0.250 | yes | 0.100 to 0.225 |
| average division finish of a team back from exile (3.0 = league average) | 3.18 | 2.80 to 3.40 | yes | 3.09 to 3.25 |
| share of returning teams that win their division | 0.180 | 0.100 to 0.300 | yes | 0.150 to 0.203 |
| share of returning teams that finish 5th again | 0.249 | 0.100 to 0.300 | yes | 0.225 to 0.275 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.40 | -0.50 to 0.50 | yes | 0.15 to 0.64 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.084 | 0.000 to 0.100 | yes | 0.074 to 0.090 |

All trends inside the bands.

## B. Team lift only, as first built (1.0 point, no development)

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.148 | 0.130 to 0.190 | yes | 0.144 to 0.152 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.170 | 0.100 to 0.500 | yes | 0.143 to 0.225 |
| share of games decided by 8 points or fewer | 0.483 | 0.350 to 0.550 | yes | 0.476 to 0.489 |
| share of seasons in which the champion is the previous champion | 0.077 | 0.000 to 0.120 | yes | 0.026 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.75 | 0.00 to 4.70 | yes | 3.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 5 | 0 to 7 | yes | 3 to 5 |
| how often the strongest team on paper wins the title | 0.216 | 0.080 to 0.250 | yes | 0.150 to 0.300 |
| average division finish of a team back from exile (3.0 = league average) | 3.13 | 2.80 to 3.40 | yes | 3.08 to 3.17 |
| share of returning teams that win their division | 0.185 | 0.100 to 0.300 | yes | 0.159 to 0.212 |
| share of returning teams that finish 5th again | 0.232 | 0.100 to 0.300 | yes | 0.197 to 0.256 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.43 | -0.50 to 0.50 | yes | 0.08 to 0.64 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.081 | 0.000 to 0.100 | yes | 0.072 to 0.085 |

All trends inside the bands.

Legend-led teams: 89 team-seasons per league (about 2.2 legends on the field at a time). They won 54.1% of their games (league average 50%), made the playoffs 45% of the time (14 of 40 teams = 35% on average) and won the title in 6.3% of seasons (1 in 40 = 2.5% on average).

## C. Add player development at 0.15 rating points a year

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.148 | 0.130 to 0.190 | yes | 0.143 to 0.151 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.183 | 0.100 to 0.500 | yes | 0.115 to 0.252 |
| share of games decided by 8 points or fewer | 0.480 | 0.350 to 0.550 | yes | 0.476 to 0.484 |
| share of seasons in which the champion is the previous champion | 0.080 | 0.000 to 0.120 | yes | 0.026 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.38 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.197 | 0.080 to 0.250 | yes | 0.025 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.21 | 2.80 to 3.40 | yes | 3.13 to 3.30 |
| share of returning teams that win their division | 0.166 | 0.100 to 0.300 | yes | 0.141 to 0.206 |
| share of returning teams that finish 5th again | 0.248 | 0.100 to 0.300 | yes | 0.206 to 0.287 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.32 | -0.50 to 0.50 | yes | 0.03 to 0.71 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.089 | 0.000 to 0.100 | yes | 0.077 to 0.099 |

All trends inside the bands.

Legend-led teams: 90 team-seasons per league (about 2.2 legends on the field at a time). They won 54.9% of their games (league average 50%), made the playoffs 48% of the time (14 of 40 teams = 35% on average) and won the title in 4.1% of seasons (1 in 40 = 2.5% on average).

## D. Development 0.25

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.143 to 0.151 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.184 | 0.100 to 0.500 | yes | 0.160 to 0.241 |
| share of games decided by 8 points or fewer | 0.482 | 0.350 to 0.550 | yes | 0.480 to 0.485 |
| share of seasons in which the champion is the previous champion | 0.077 | 0.000 to 0.120 | yes | 0.051 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.75 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.212 | 0.080 to 0.250 | yes | 0.150 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.16 | 2.80 to 3.40 | yes | 3.07 to 3.26 |
| share of returning teams that win their division | 0.178 | 0.100 to 0.300 | yes | 0.156 to 0.194 |
| share of returning teams that finish 5th again | 0.231 | 0.100 to 0.300 | yes | 0.200 to 0.253 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.38 | -0.50 to 0.50 | yes | 0.15 to 0.59 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.088 | 0.000 to 0.100 | yes | 0.079 to 0.096 |

All trends inside the bands.

Legend-led teams: 89 team-seasons per league (about 2.2 legends on the field at a time). They won 54.8% of their games (league average 50%), made the playoffs 46% of the time (14 of 40 teams = 35% on average) and won the title in 3.6% of seasons (1 in 40 = 2.5% on average).

## E. Development 0.40

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.149 | 0.130 to 0.190 | yes | 0.146 to 0.155 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.187 | 0.100 to 0.500 | yes | 0.166 to 0.214 |
| share of games decided by 8 points or fewer | 0.483 | 0.350 to 0.550 | yes | 0.477 to 0.492 |
| share of seasons in which the champion is the previous champion | 0.099 | 0.000 to 0.120 | yes | 0.051 to 0.179 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.38 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.219 | 0.080 to 0.250 | yes | 0.125 to 0.300 |
| average division finish of a team back from exile (3.0 = league average) | 3.19 | 2.80 to 3.40 | yes | 3.06 to 3.30 |
| share of returning teams that win their division | 0.164 | 0.100 to 0.300 | yes | 0.119 to 0.209 |
| share of returning teams that finish 5th again | 0.241 | 0.100 to 0.300 | yes | 0.206 to 0.281 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.27 | -0.50 to 0.50 | yes | -0.17 to 0.55 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.089 | 0.000 to 0.100 | yes | 0.084 to 0.097 |

All trends inside the bands.

Legend-led teams: 89 team-seasons per league (about 2.2 legends on the field at a time). They won 56.5% of their games (league average 50%), made the playoffs 52% of the time (14 of 40 teams = 35% on average) and won the title in 5.8% of seasons (1 in 40 = 2.5% on average).

## F. Development 0.60

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.150 | 0.130 to 0.190 | yes | 0.142 to 0.156 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.193 | 0.100 to 0.500 | yes | 0.140 to 0.213 |
| share of games decided by 8 points or fewer | 0.479 | 0.350 to 0.550 | yes | 0.471 to 0.490 |
| share of seasons in which the champion is the previous champion | 0.077 | 0.000 to 0.120 | yes | 0.026 to 0.154 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 4.25 | 0.00 to 4.70 | yes | 2.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 5 | 0 to 7 | yes | 2 to 5 |
| how often the strongest team on paper wins the title | 0.200 | 0.080 to 0.250 | yes | 0.050 to 0.375 |
| average division finish of a team back from exile (3.0 = league average) | 3.18 | 2.80 to 3.40 | yes | 3.16 to 3.22 |
| share of returning teams that win their division | 0.168 | 0.100 to 0.300 | yes | 0.144 to 0.191 |
| share of returning teams that finish 5th again | 0.243 | 0.100 to 0.300 | yes | 0.216 to 0.263 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.43 | -0.50 to 0.50 | yes | 0.11 to 0.68 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.084 | 0.000 to 0.100 | yes | 0.074 to 0.093 |

All trends inside the bands.

Legend-led teams: 92 team-seasons per league (about 2.3 legends on the field at a time). They won 57.8% of their games (league average 50%), made the playoffs 55% of the time (14 of 40 teams = 35% on average) and won the title in 7.6% of seasons (1 in 40 = 2.5% on average).

## G. Development 1.00

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.154 | 0.130 to 0.190 | yes | 0.149 to 0.157 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.209 | 0.100 to 0.500 | yes | 0.161 to 0.249 |
| share of games decided by 8 points or fewer | 0.477 | 0.350 to 0.550 | yes | 0.471 to 0.485 |
| share of seasons in which the champion is the previous champion | 0.077 | 0.000 to 0.120 | yes | 0.026 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 4.88 | 0.00 to 4.70 | **NO** | 3.00 to 8.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 8 | 0 to 7 | **NO** | 3 to 8 |
| how often the strongest team on paper wins the title | 0.253 | 0.080 to 0.250 | **NO** | 0.200 to 0.325 |
| average division finish of a team back from exile (3.0 = league average) | 3.23 | 2.80 to 3.40 | yes | 3.15 to 3.37 |
| share of returning teams that win their division | 0.164 | 0.100 to 0.300 | yes | 0.131 to 0.191 |
| share of returning teams that finish 5th again | 0.263 | 0.100 to 0.300 | yes | 0.228 to 0.312 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.12 | -0.50 to 0.50 | yes | 0.01 to 0.21 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.093 | 0.000 to 0.100 | yes | 0.081 to 0.099 |

**Outside the bands:** max_titles_in_20, worst_league_titles, best_team_title_odds.

Legend-led teams: 95 team-seasons per league (about 2.4 legends on the field at a time). They won 61.1% of their games (league average 50%), made the playoffs 62% of the time (14 of 40 teams = 35% on average) and won the title in 9.5% of seasons (1 in 40 = 2.5% on average).

## H. Development 0.40 and team lift 1.5 points

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.149 | 0.130 to 0.190 | yes | 0.146 to 0.155 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.186 | 0.100 to 0.500 | yes | 0.165 to 0.201 |
| share of games decided by 8 points or fewer | 0.482 | 0.350 to 0.550 | yes | 0.476 to 0.489 |
| share of seasons in which the champion is the previous champion | 0.083 | 0.000 to 0.120 | yes | 0.026 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.38 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.188 | 0.080 to 0.250 | yes | 0.150 to 0.325 |
| average division finish of a team back from exile (3.0 = league average) | 3.20 | 2.80 to 3.40 | yes | 3.13 to 3.29 |
| share of returning teams that win their division | 0.161 | 0.100 to 0.300 | yes | 0.131 to 0.194 |
| share of returning teams that finish 5th again | 0.248 | 0.100 to 0.300 | yes | 0.206 to 0.287 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.33 | -0.50 to 0.50 | yes | 0.09 to 0.52 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.091 | 0.000 to 0.100 | yes | 0.079 to 0.099 |

All trends inside the bands.

Legend-led teams: 93 team-seasons per league (about 2.3 legends on the field at a time). They won 57.9% of their games (league average 50%), made the playoffs 56% of the time (14 of 40 teams = 35% on average) and won the title in 6.0% of seasons (1 in 40 = 2.5% on average).

## I. Development 0.40 and team lift 2.0 points

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.151 | 0.130 to 0.190 | yes | 0.148 to 0.155 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.198 | 0.100 to 0.500 | yes | 0.170 to 0.236 |
| share of games decided by 8 points or fewer | 0.482 | 0.350 to 0.550 | yes | 0.470 to 0.490 |
| share of seasons in which the champion is the previous champion | 0.058 | 0.000 to 0.120 | yes | 0.026 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.88 | 0.00 to 4.70 | yes | 3.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 5 | 0 to 7 | yes | 3 to 5 |
| how often the strongest team on paper wins the title | 0.222 | 0.080 to 0.250 | yes | 0.150 to 0.325 |
| average division finish of a team back from exile (3.0 = league average) | 3.17 | 2.80 to 3.40 | yes | 3.02 to 3.26 |
| share of returning teams that win their division | 0.168 | 0.100 to 0.300 | yes | 0.138 to 0.216 |
| share of returning teams that finish 5th again | 0.239 | 0.100 to 0.300 | yes | 0.191 to 0.278 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.22 | -0.50 to 0.50 | yes | -0.01 to 0.44 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.083 | 0.000 to 0.100 | yes | 0.069 to 0.093 |

All trends inside the bands.

Legend-led teams: 94 team-seasons per league (about 2.3 legends on the field at a time). They won 60.3% of their games (league average 50%), made the playoffs 60% of the time (14 of 40 teams = 35% on average) and won the title in 8.3% of seasons (1 in 40 = 2.5% on average).

## J. Development 0.40, lift 1.0, legends twice as common (10%)

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.150 | 0.130 to 0.190 | yes | 0.147 to 0.153 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.176 | 0.100 to 0.500 | yes | 0.150 to 0.206 |
| share of games decided by 8 points or fewer | 0.480 | 0.350 to 0.550 | yes | 0.475 to 0.485 |
| share of seasons in which the champion is the previous champion | 0.087 | 0.000 to 0.120 | yes | 0.026 to 0.179 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.62 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.212 | 0.080 to 0.250 | yes | 0.100 to 0.300 |
| average division finish of a team back from exile (3.0 = league average) | 3.16 | 2.80 to 3.40 | yes | 3.10 to 3.23 |
| share of returning teams that win their division | 0.173 | 0.100 to 0.300 | yes | 0.128 to 0.197 |
| share of returning teams that finish 5th again | 0.245 | 0.100 to 0.300 | yes | 0.206 to 0.291 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.44 | -0.50 to 0.50 | yes | 0.06 to 0.84 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.084 | 0.000 to 0.100 | yes | 0.077 to 0.094 |

All trends inside the bands.

Legend-led teams: 172 team-seasons per league (about 4.3 legends on the field at a time). They won 56.1% of their games (league average 50%), made the playoffs 50% of the time (14 of 40 teams = 35% on average) and won the title in 5.4% of seasons (1 in 40 = 2.5% on average).
