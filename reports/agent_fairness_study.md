# Agents in the owners' seats and at the interview table: fairness with a stand-in agent

A stand-in agent (agents.py) reads only the view a real agent would be shown (the deciding card, her notes, the options with the ratings she perceives) and chooses from the engine's options; owners with different personalities choose differently, and candidates ask for more guaranteed seasons or walk depending on how the owner and the team look to them. It is a rulebook, not a model, so this tests the machinery and the bands, not the quality of a real agent's judgment.

Rows A, I, J and K are the autopilot, agents in all 48 owners' seats (yearly reviews, hires and interviews), agents in 12 seats, and an agent whose answers are often lost or invalid. Rows L, M and N are worst cases at the interview table: contracts used to widen the gap as far as the rules allow (the strongest teams lock in the best coach for three seasons, the weakest hire the worst), every candidate refusing every job, and hard bargaining on both sides. In M and N the league office fills every seat by the old rule, so those leagues must be, and are, the autopilot league (identical numbers to row A): they test that the fallback holds, not the bands.

**Every row is inside every band.** One thing to know about the edge of the dynasty band: in row K (8 leagues) one league had a team win 7 titles in 20 seasons, which is the most the band allows. It was not a guarantee effect (the team's staff had no guarantees in that stretch and the same league on the autopilot gives 4), so I checked it against 24 fresh leagues for the autopilot and for row K: the worst league in each 24 was 6 (autopilot) and 5 (row K), with the same spread of 2 to 5 titles in most leagues. It was a tail event of the same size the autopilot also produces, not a tilt.

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
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.145 to 0.149 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.161 | 0.100 to 0.500 | yes | 0.108 to 0.211 |
| share of games decided by 8 points or fewer | 0.479 | 0.350 to 0.550 | yes | 0.475 to 0.484 |
| share of seasons in which the champion is the previous champion | 0.058 | 0.000 to 0.120 | yes | 0.000 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.38 | 0.00 to 4.70 | yes | 3.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 5 | 0 to 7 | yes | 3 to 5 |
| how often the strongest team on paper wins the title | 0.188 | 0.080 to 0.250 | yes | 0.100 to 0.250 |
| average division finish of a team back from exile (3.0 = league average) | 3.19 | 2.80 to 3.40 | yes | 3.12 to 3.31 |
| share of returning teams that win their division | 0.167 | 0.100 to 0.300 | yes | 0.144 to 0.197 |
| share of returning teams that finish 5th again | 0.256 | 0.100 to 0.300 | yes | 0.209 to 0.294 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.26 | -0.50 to 0.50 | yes | -0.28 to 0.60 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.084 | 0.000 to 0.100 | yes | 0.076 to 0.091 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 12 team-seasons per league (about 0.3 on the field at a time). They won 53.5% of their games (league average 50%), made the playoffs 42% of the time (14 of 40 teams = 35% on average) and won the title in 6.3% of seasons (1 in 40 = 2.5% on average).


## J. Agents in 12 seats (every fourth team), the autopilot in the other 36

fast engine, 8 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.144 to 0.154 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.171 | 0.100 to 0.500 | yes | 0.128 to 0.210 |
| share of games decided by 8 points or fewer | 0.484 | 0.350 to 0.550 | yes | 0.480 to 0.491 |
| share of seasons in which the champion is the previous champion | 0.077 | 0.000 to 0.120 | yes | 0.051 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.62 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.188 | 0.080 to 0.250 | yes | 0.125 to 0.300 |
| average division finish of a team back from exile (3.0 = league average) | 3.16 | 2.80 to 3.40 | yes | 3.08 to 3.24 |
| share of returning teams that win their division | 0.175 | 0.100 to 0.300 | yes | 0.153 to 0.209 |
| share of returning teams that finish 5th again | 0.230 | 0.100 to 0.300 | yes | 0.216 to 0.253 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.28 | -0.50 to 0.50 | yes | 0.04 to 0.48 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.085 | 0.000 to 0.100 | yes | 0.077 to 0.092 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 12 team-seasons per league (about 0.3 on the field at a time). They won 53.0% of their games (league average 50%), made the playoffs 43% of the time (14 of 40 teams = 35% on average) and won the title in 6.1% of seasons (1 in 40 = 2.5% on average).


## K. The same agent, but a quarter of its answers are lost or invalid (the autopilot steps in)

fast engine, 8 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.149 | 0.130 to 0.190 | yes | 0.144 to 0.154 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.185 | 0.100 to 0.500 | yes | 0.162 to 0.238 |
| share of games decided by 8 points or fewer | 0.482 | 0.350 to 0.550 | yes | 0.477 to 0.490 |
| share of seasons in which the champion is the previous champion | 0.080 | 0.000 to 0.120 | yes | 0.026 to 0.179 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.62 | 0.00 to 4.70 | yes | 3.00 to 7.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 7 | 0 to 7 | yes | 3 to 7 |
| how often the strongest team on paper wins the title | 0.209 | 0.080 to 0.250 | yes | 0.150 to 0.350 |
| average division finish of a team back from exile (3.0 = league average) | 3.14 | 2.80 to 3.40 | yes | 3.03 to 3.31 |
| share of returning teams that win their division | 0.178 | 0.100 to 0.300 | yes | 0.150 to 0.200 |
| share of returning teams that finish 5th again | 0.239 | 0.100 to 0.300 | yes | 0.200 to 0.278 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.44 | -0.50 to 0.50 | yes | 0.11 to 0.89 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.085 | 0.000 to 0.100 | yes | 0.076 to 0.104 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 14 team-seasons per league (about 0.3 on the field at a time). They won 56.5% of their games (league average 50%), made the playoffs 48% of the time (14 of 40 teams = 35% on average) and won the title in 10.0% of seasons (1 in 40 = 2.5% on average).


## L. Worst case at the interview table: the 8 strongest hire the best and guarantee her three seasons, the 8 weakest hire the worst on no guarantee

fast engine, 8 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.149 | 0.130 to 0.190 | yes | 0.145 to 0.155 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.190 | 0.100 to 0.500 | yes | 0.144 to 0.227 |
| share of games decided by 8 points or fewer | 0.481 | 0.350 to 0.550 | yes | 0.476 to 0.485 |
| share of seasons in which the champion is the previous champion | 0.071 | 0.000 to 0.120 | yes | 0.000 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.38 | 0.00 to 4.70 | yes | 2.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 5 | 0 to 7 | yes | 2 to 5 |
| how often the strongest team on paper wins the title | 0.175 | 0.080 to 0.250 | yes | 0.100 to 0.325 |
| average division finish of a team back from exile (3.0 = league average) | 3.15 | 2.80 to 3.40 | yes | 2.99 to 3.28 |
| share of returning teams that win their division | 0.182 | 0.100 to 0.300 | yes | 0.153 to 0.209 |
| share of returning teams that finish 5th again | 0.242 | 0.100 to 0.300 | yes | 0.206 to 0.278 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.33 | -0.50 to 0.50 | yes | 0.05 to 0.61 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.088 | 0.000 to 0.100 | yes | 0.081 to 0.098 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 6 team-seasons per league (about 0.2 on the field at a time). They won 54.9% of their games (league average 50%), made the playoffs 49% of the time (14 of 40 teams = 35% on average) and won the title in 3.9% of seasons (1 in 40 = 2.5% on average).


## M. Every candidate refuses every job (the league office fills every seat by the old rule)

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


## N. Hard bargaining: every candidate asks for the most and walks without it, every owner holds the line

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

