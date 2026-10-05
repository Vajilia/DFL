# Agents in the owners' seats: fairness with a stand-in agent

A stand-in agent (agents.py) reads only the view a real agent would be shown (the deciding card, her notes, the options with the ratings she perceives) and chooses from the engine's options; owners with different personalities choose differently. It is a rulebook, not a model, so this tests the machinery and the bands, not the quality of a real agent's judgment. Rows: all 48 seats, a dozen seats, and an agent whose answers are often lost or invalid.

## A. Autopilot (the rules as they were before agents)

fast engine, 8 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.143 to 0.151 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.172 | 0.100 to 0.500 | yes | 0.136 to 0.228 |
| share of games decided by 8 points or fewer | 0.483 | 0.350 to 0.550 | yes | 0.477 to 0.489 |
| share of seasons in which the champion is the previous champion | 0.067 | 0.000 to 0.120 | yes | 0.026 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.25 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.181 | 0.080 to 0.250 | yes | 0.150 to 0.225 |
| average division finish of a team back from exile (3.0 = league average) | 3.20 | 2.80 to 3.40 | yes | 3.09 to 3.31 |
| share of returning teams that win their division | 0.173 | 0.100 to 0.300 | yes | 0.141 to 0.194 |
| share of returning teams that finish 5th again | 0.250 | 0.100 to 0.300 | yes | 0.197 to 0.278 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.29 | -0.50 to 0.50 | yes | 0.05 to 0.71 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.087 | 0.000 to 0.100 | yes | 0.075 to 0.092 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 14 team-seasons per league (about 0.4 on the field at a time). They won 53.6% of their games (league average 50%), made the playoffs 45% of the time (14 of 40 teams = 35% on average) and won the title in 4.4% of seasons (1 in 40 = 2.5% on average).

## I. A stand-in agent in all 48 owners' seats (cards decide, a dozen at a time)

fast engine, 8 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.148 | 0.130 to 0.190 | yes | 0.144 to 0.150 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.209 | 0.100 to 0.500 | yes | 0.198 to 0.230 |
| share of games decided by 8 points or fewer | 0.483 | 0.350 to 0.550 | yes | 0.476 to 0.486 |
| share of seasons in which the champion is the previous champion | 0.099 | 0.000 to 0.120 | yes | 0.026 to 0.179 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 4.12 | 0.00 to 4.70 | yes | 3.00 to 6.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 6 | 0 to 7 | yes | 3 to 6 |
| how often the strongest team on paper wins the title | 0.228 | 0.080 to 0.250 | yes | 0.075 to 0.350 |
| average division finish of a team back from exile (3.0 = league average) | 3.19 | 2.80 to 3.40 | yes | 3.06 to 3.38 |
| share of returning teams that win their division | 0.165 | 0.100 to 0.300 | yes | 0.119 to 0.191 |
| share of returning teams that finish 5th again | 0.242 | 0.100 to 0.300 | yes | 0.212 to 0.275 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.28 | -0.50 to 0.50 | yes | -0.10 to 0.53 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.088 | 0.000 to 0.100 | yes | 0.079 to 0.102 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 13 team-seasons per league (about 0.3 on the field at a time). They won 58.6% of their games (league average 50%), made the playoffs 57% of the time (14 of 40 teams = 35% on average) and won the title in 7.6% of seasons (1 in 40 = 2.5% on average).

## J. Agents in 12 seats (every fourth team), the autopilot in the other 36

fast engine, 8 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.149 | 0.130 to 0.190 | yes | 0.145 to 0.155 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.184 | 0.100 to 0.500 | yes | 0.151 to 0.219 |
| share of games decided by 8 points or fewer | 0.484 | 0.350 to 0.550 | yes | 0.479 to 0.490 |
| share of seasons in which the champion is the previous champion | 0.061 | 0.000 to 0.120 | yes | 0.026 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.12 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.209 | 0.080 to 0.250 | yes | 0.125 to 0.300 |
| average division finish of a team back from exile (3.0 = league average) | 3.22 | 2.80 to 3.40 | yes | 3.05 to 3.34 |
| share of returning teams that win their division | 0.143 | 0.100 to 0.300 | yes | 0.109 to 0.175 |
| share of returning teams that finish 5th again | 0.249 | 0.100 to 0.300 | yes | 0.231 to 0.272 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.13 | -0.50 to 0.50 | yes | -0.19 to 0.42 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.083 | 0.000 to 0.100 | yes | 0.072 to 0.096 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 11 team-seasons per league (about 0.3 on the field at a time). They won 57.2% of their games (league average 50%), made the playoffs 56% of the time (14 of 40 teams = 35% on average) and won the title in 11.4% of seasons (1 in 40 = 2.5% on average).

## K. The same agent, but a quarter of its answers are lost or invalid (the autopilot steps in)

fast engine, 8 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.148 | 0.130 to 0.190 | yes | 0.144 to 0.153 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.170 | 0.100 to 0.500 | yes | 0.092 to 0.210 |
| share of games decided by 8 points or fewer | 0.480 | 0.350 to 0.550 | yes | 0.471 to 0.485 |
| share of seasons in which the champion is the previous champion | 0.074 | 0.000 to 0.120 | yes | 0.026 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.12 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.191 | 0.080 to 0.250 | yes | 0.125 to 0.250 |
| average division finish of a team back from exile (3.0 = league average) | 3.16 | 2.80 to 3.40 | yes | 3.08 to 3.25 |
| share of returning teams that win their division | 0.175 | 0.100 to 0.300 | yes | 0.150 to 0.200 |
| share of returning teams that finish 5th again | 0.244 | 0.100 to 0.300 | yes | 0.206 to 0.291 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.25 | -0.50 to 0.50 | yes | 0.08 to 0.54 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.083 | 0.000 to 0.100 | yes | 0.073 to 0.102 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 14 team-seasons per league (about 0.3 on the field at a time). They won 59.2% of their games (league average 50%), made the playoffs 57% of the time (14 of 40 teams = 35% on average) and won the title in 4.5% of seasons (1 in 40 = 2.5% on average).
