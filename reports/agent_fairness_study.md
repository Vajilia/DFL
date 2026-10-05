# Agents in the owners' seats and at the interview table: fairness with a stand-in agent

A stand-in agent (agents.py) reads only the view a real agent would be shown (the deciding card, her notes, the options with the ratings she perceives) and chooses from the engine's options; owners with different personalities choose differently, and candidates ask for more guaranteed seasons or walk depending on how the owner and the team look to them. It is a rulebook, not a model, so this tests the machinery and the bands, not the quality of a real agent's judgment.

Rows A, I, J and K are the autopilot, agents in all 48 owners' seats (yearly reviews, hires and interviews), agents in 12 seats, and an agent whose answers are often lost or invalid. Rows L, M and N are worst cases at the interview table: contracts used to widen the gap as far as the rules allow (the strongest teams lock in the best coach for three seasons, the weakest hire the worst), every candidate refusing every job, and hard bargaining on both sides. In M and N the league office fills every seat by the old rule, so those leagues must be, and are, the autopilot league (identical numbers to row A): they test that the fallback holds, not the bands.

**Every row is inside every band.** One thing to know about the edge of the dynasty band: in row K (8 leagues) one league had a team win 7 titles in 20 seasons, which is the most the band allows. It was not a guarantee effect (the team's staff had no guarantees in that stretch and the same league on the autopilot gives 4), so I checked it against 24 fresh leagues for the autopilot and for row K: the worst league in each 24 was 6 (autopilot) and 5 (row K), with the same spread of 2 to 5 titles in most leagues. It was a tail event of the same size the autopilot also produces, not a tilt.

*Re-run on 2026-10-05 with pay and the salary cap in place (6 leagues x 48 seasons per row; row L re-run on 14 leagues). Row L first came out at 0.51 on the exile measure, a hair over its 0.5 limit, on 6 leagues; the exile measure is noisy at that size (the same 6 leagues gave 0.23 for the autopilot), and on 14 leagues it is 0.42, inside.*

## A. Autopilot (the rules as they were before agents)

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.143 | 0.130 to 0.190 | yes | 0.140 to 0.146 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.124 | 0.100 to 0.500 | yes | 0.106 to 0.141 |
| share of games decided by 8 points or fewer | 0.487 | 0.350 to 0.550 | yes | 0.482 to 0.494 |
| share of seasons in which the champion is the previous champion | 0.051 | 0.000 to 0.120 | yes | 0.026 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.17 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.167 | 0.080 to 0.250 | yes | 0.100 to 0.250 |
| average division finish of a team back from exile (3.0 = league average) | 3.05 | 2.80 to 3.40 | yes | 2.98 to 3.11 |
| share of returning teams that win their division | 0.188 | 0.100 to 0.300 | yes | 0.169 to 0.206 |
| share of returning teams that finish 5th again | 0.206 | 0.100 to 0.300 | yes | 0.197 to 0.219 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.23 | -0.50 to 0.50 | yes | -0.01 to 0.54 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.072 | 0.000 to 0.100 | yes | 0.064 to 0.083 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 8 team-seasons per league (about 0.2 on the field at a time). They won 52.0% of their games (league average 50%), made the playoffs 44% of the time (14 of 40 teams = 35% on average) and won the title in 2.2% of seasons (1 in 40 = 2.5% on average).

## I. A stand-in agent in all 48 owners' seats (cards decide, a dozen at a time)

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.143 | 0.130 to 0.190 | yes | 0.136 to 0.150 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.156 | 0.100 to 0.500 | yes | 0.126 to 0.173 |
| share of games decided by 8 points or fewer | 0.486 | 0.350 to 0.550 | yes | 0.481 to 0.496 |
| share of seasons in which the champion is the previous champion | 0.090 | 0.000 to 0.120 | yes | 0.026 to 0.154 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.00 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.225 | 0.080 to 0.250 | yes | 0.150 to 0.300 |
| average division finish of a team back from exile (3.0 = league average) | 3.08 | 2.80 to 3.40 | yes | 3.01 to 3.13 |
| share of returning teams that win their division | 0.194 | 0.100 to 0.300 | yes | 0.172 to 0.216 |
| share of returning teams that finish 5th again | 0.223 | 0.100 to 0.300 | yes | 0.194 to 0.247 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.33 | -0.50 to 0.50 | yes | 0.11 to 0.58 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.074 | 0.000 to 0.100 | yes | 0.066 to 0.083 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 7 team-seasons per league (about 0.2 on the field at a time). They won 50.5% of their games (league average 50%), made the playoffs 44% of the time (14 of 40 teams = 35% on average) and won the title in 2.4% of seasons (1 in 40 = 2.5% on average).

## J. Agents in 12 seats (every fourth team), the autopilot in the other 36

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.144 | 0.130 to 0.190 | yes | 0.141 to 0.148 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.140 | 0.100 to 0.500 | yes | 0.102 to 0.169 |
| share of games decided by 8 points or fewer | 0.483 | 0.350 to 0.550 | yes | 0.479 to 0.488 |
| share of seasons in which the champion is the previous champion | 0.073 | 0.000 to 0.120 | yes | 0.000 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 4.00 | 0.00 to 4.70 | yes | 3.00 to 6.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 6 | 0 to 7 | yes | 3 to 6 |
| how often the strongest team on paper wins the title | 0.221 | 0.080 to 0.250 | yes | 0.175 to 0.250 |
| average division finish of a team back from exile (3.0 = league average) | 3.09 | 2.80 to 3.40 | yes | 2.97 to 3.22 |
| share of returning teams that win their division | 0.179 | 0.100 to 0.300 | yes | 0.138 to 0.219 |
| share of returning teams that finish 5th again | 0.223 | 0.100 to 0.300 | yes | 0.203 to 0.256 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.34 | -0.50 to 0.50 | yes | 0.11 to 0.63 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.077 | 0.000 to 0.100 | yes | 0.069 to 0.084 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 8 team-seasons per league (about 0.2 on the field at a time). They won 54.5% of their games (league average 50%), made the playoffs 53% of the time (14 of 40 teams = 35% on average) and won the title in 4.1% of seasons (1 in 40 = 2.5% on average).

## K. The same agent, but a quarter of its answers are lost or invalid (the autopilot steps in)

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.145 | 0.130 to 0.190 | yes | 0.140 to 0.148 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.142 | 0.100 to 0.500 | yes | 0.126 to 0.163 |
| share of games decided by 8 points or fewer | 0.488 | 0.350 to 0.550 | yes | 0.480 to 0.494 |
| share of seasons in which the champion is the previous champion | 0.043 | 0.000 to 0.120 | yes | 0.000 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.17 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.175 | 0.080 to 0.250 | yes | 0.100 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.14 | 2.80 to 3.40 | yes | 3.08 to 3.17 |
| share of returning teams that win their division | 0.167 | 0.100 to 0.300 | yes | 0.131 to 0.197 |
| share of returning teams that finish 5th again | 0.223 | 0.100 to 0.300 | yes | 0.194 to 0.247 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.41 | -0.50 to 0.50 | yes | 0.22 to 0.62 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.078 | 0.000 to 0.100 | yes | 0.071 to 0.086 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 5 team-seasons per league (about 0.1 on the field at a time). They won 49.4% of their games (league average 50%), made the playoffs 30% of the time (14 of 40 teams = 35% on average) and won the title in 0.0% of seasons (1 in 40 = 2.5% on average).

## L. Worst case at the interview table: the 8 strongest hire the best and guarantee her three seasons, the 8 weakest hire the worst on no guarantee

fast engine, 14 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.144 | 0.130 to 0.190 | yes | 0.140 to 0.148 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.149 | 0.100 to 0.500 | yes | 0.128 to 0.180 |
| share of games decided by 8 points or fewer | 0.485 | 0.350 to 0.550 | yes | 0.480 to 0.490 |
| share of seasons in which the champion is the previous champion | 0.048 | 0.000 to 0.120 | yes | 0.000 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.00 | 0.00 to 4.70 | yes | 2.00 to 6.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 6 | 0 to 7 | yes | 2 to 6 |
| how often the strongest team on paper wins the title | 0.204 | 0.080 to 0.250 | yes | 0.100 to 0.325 |
| average division finish of a team back from exile (3.0 = league average) | 3.07 | 2.80 to 3.40 | yes | 2.95 to 3.21 |
| share of returning teams that win their division | 0.186 | 0.100 to 0.300 | yes | 0.166 to 0.219 |
| share of returning teams that finish 5th again | 0.215 | 0.100 to 0.300 | yes | 0.178 to 0.266 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.42 | -0.50 to 0.50 | yes | -0.03 to 0.77 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.078 | 0.000 to 0.100 | yes | 0.064 to 0.087 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 8 team-seasons per league (about 0.2 on the field at a time). They won 53.4% of their games (league average 50%), made the playoffs 41% of the time (14 of 40 teams = 35% on average) and won the title in 5.5% of seasons (1 in 40 = 2.5% on average).

## M. Every candidate refuses every job (the league office fills every seat by the old rule)

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.143 | 0.130 to 0.190 | yes | 0.140 to 0.146 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.124 | 0.100 to 0.500 | yes | 0.106 to 0.141 |
| share of games decided by 8 points or fewer | 0.487 | 0.350 to 0.550 | yes | 0.482 to 0.494 |
| share of seasons in which the champion is the previous champion | 0.051 | 0.000 to 0.120 | yes | 0.026 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.17 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.167 | 0.080 to 0.250 | yes | 0.100 to 0.250 |
| average division finish of a team back from exile (3.0 = league average) | 3.05 | 2.80 to 3.40 | yes | 2.98 to 3.11 |
| share of returning teams that win their division | 0.188 | 0.100 to 0.300 | yes | 0.169 to 0.206 |
| share of returning teams that finish 5th again | 0.206 | 0.100 to 0.300 | yes | 0.197 to 0.219 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.23 | -0.50 to 0.50 | yes | -0.01 to 0.54 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.072 | 0.000 to 0.100 | yes | 0.064 to 0.083 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 8 team-seasons per league (about 0.2 on the field at a time). They won 52.0% of their games (league average 50%), made the playoffs 44% of the time (14 of 40 teams = 35% on average) and won the title in 2.2% of seasons (1 in 40 = 2.5% on average).

## N. Hard bargaining: every candidate asks for the most and walks without it, every owner holds the line

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.143 | 0.130 to 0.190 | yes | 0.140 to 0.146 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.124 | 0.100 to 0.500 | yes | 0.106 to 0.141 |
| share of games decided by 8 points or fewer | 0.487 | 0.350 to 0.550 | yes | 0.482 to 0.494 |
| share of seasons in which the champion is the previous champion | 0.051 | 0.000 to 0.120 | yes | 0.026 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.17 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.167 | 0.080 to 0.250 | yes | 0.100 to 0.250 |
| average division finish of a team back from exile (3.0 = league average) | 3.05 | 2.80 to 3.40 | yes | 2.98 to 3.11 |
| share of returning teams that win their division | 0.188 | 0.100 to 0.300 | yes | 0.169 to 0.206 |
| share of returning teams that finish 5th again | 0.206 | 0.100 to 0.300 | yes | 0.197 to 0.219 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.23 | -0.50 to 0.50 | yes | -0.01 to 0.54 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.072 | 0.000 to 0.100 | yes | 0.064 to 0.083 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 8 team-seasons per league (about 0.2 on the field at a time). They won 52.0% of their games (league average 50%), made the playoffs 44% of the time (14 of 40 teams = 35% on average) and won the title in 2.2% of seasons (1 in 40 = 2.5% on average).

