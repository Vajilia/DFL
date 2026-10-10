# Agents in the CEOs' seats: fairness with a stand-in agent

A stand-in agent (agents.py) reads only the view a real agent would be shown (the deciding card, her notes, the options with the ratings she perceives) and chooses from the engine's options; CEOs with different personalities choose differently. It is a rulebook, not a model, so this tests the machinery and the bands, not the quality of a real agent's judgment. Rows: all 48 seats, a dozen seats, and an agent whose answers are often lost or invalid.

## A. Autopilot (the rules as they were before agents)

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.145 to 0.151 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.174 | 0.100 to 0.500 | yes | 0.150 to 0.201 |
| share of games decided by 8 points or fewer | 0.478 | 0.350 to 0.550 | yes | 0.469 to 0.485 |
| share of seasons in which the champion is the previous champion | 0.081 | 0.000 to 0.120 | yes | 0.000 to 0.179 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.00 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.192 | 0.080 to 0.250 | yes | 0.100 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.29 | 2.80 to 3.40 | yes | 3.21 to 3.38 |
| share of returning teams that win their division | 0.140 | 0.100 to 0.300 | yes | 0.122 to 0.172 |
| share of returning teams that finish 5th again | 0.272 | 0.100 to 0.300 | yes | 0.219 to 0.303 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | -0.24 | -0.50 to 0.50 | yes | -0.45 to -0.01 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.087 | 0.000 to 0.100 | yes | 0.074 to 0.099 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 12 team-seasons per league (about 0.3 on the field at a time). They won 52.0% of their games (league average 50%), made the playoffs 41% of the time (14 of 40 teams = 35% on average) and won the title in 5.8% of seasons (1 in 40 = 2.5% on average).

## I. A stand-in agent in all 48 CEOs' seats (cards decide, a dozen at a time)

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.140 | 0.130 to 0.190 | yes | 0.138 to 0.143 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.136 | 0.100 to 0.500 | yes | 0.123 to 0.167 |
| share of games decided by 8 points or fewer | 0.486 | 0.350 to 0.550 | yes | 0.483 to 0.490 |
| share of seasons in which the champion is the previous champion | 0.060 | 0.000 to 0.120 | yes | 0.026 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.67 | 0.00 to 4.70 | yes | 3.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 5 | 0 to 7 | yes | 3 to 5 |
| how often the strongest team on paper wins the title | 0.163 | 0.080 to 0.250 | yes | 0.125 to 0.225 |
| average division finish of a team back from exile (3.0 = league average) | 3.19 | 2.80 to 3.40 | yes | 3.11 to 3.33 |
| share of returning teams that win their division | 0.172 | 0.100 to 0.300 | yes | 0.150 to 0.197 |
| share of returning teams that finish 5th again | 0.259 | 0.100 to 0.300 | yes | 0.209 to 0.300 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | -0.04 | -0.50 to 0.50 | yes | -0.38 to 0.19 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.082 | 0.000 to 0.100 | yes | 0.076 to 0.086 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 5 team-seasons per league (about 0.1 on the field at a time). They won 52.7% of their games (league average 50%), made the playoffs 29% of the time (14 of 40 teams = 35% on average) and won the title in 3.2% of seasons (1 in 40 = 2.5% on average).

## J. Agents in 12 seats (every fourth team), the autopilot in the other 36

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.146 | 0.130 to 0.190 | yes | 0.143 to 0.149 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.143 | 0.100 to 0.500 | yes | 0.122 to 0.196 |
| share of games decided by 8 points or fewer | 0.480 | 0.350 to 0.550 | yes | 0.472 to 0.484 |
| share of seasons in which the champion is the previous champion | 0.051 | 0.000 to 0.120 | yes | 0.000 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.17 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.150 | 0.080 to 0.250 | yes | 0.075 to 0.225 |
| average division finish of a team back from exile (3.0 = league average) | 3.31 | 2.80 to 3.40 | yes | 3.25 to 3.35 |
| share of returning teams that win their division | 0.156 | 0.100 to 0.300 | yes | 0.138 to 0.197 |
| share of returning teams that finish 5th again | 0.268 | 0.100 to 0.300 | yes | 0.256 to 0.303 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | -0.28 | -0.50 to 0.50 | yes | -0.56 to 0.12 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.087 | 0.000 to 0.100 | yes | 0.086 to 0.093 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 7 team-seasons per league (about 0.2 on the field at a time). They won 51.0% of their games (league average 50%), made the playoffs 36% of the time (14 of 40 teams = 35% on average) and won the title in 2.4% of seasons (1 in 40 = 2.5% on average).

## K. The same agent, but a quarter of its answers are lost or invalid (the autopilot steps in)

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.143 | 0.130 to 0.190 | yes | 0.139 to 0.145 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.145 | 0.100 to 0.500 | yes | 0.133 to 0.181 |
| share of games decided by 8 points or fewer | 0.481 | 0.350 to 0.550 | yes | 0.474 to 0.484 |
| share of seasons in which the champion is the previous champion | 0.060 | 0.000 to 0.120 | yes | 0.000 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.17 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.108 | 0.080 to 0.250 | yes | 0.025 to 0.225 |
| average division finish of a team back from exile (3.0 = league average) | 3.22 | 2.80 to 3.40 | yes | 3.12 to 3.38 |
| share of returning teams that win their division | 0.169 | 0.100 to 0.300 | yes | 0.134 to 0.200 |
| share of returning teams that finish 5th again | 0.252 | 0.100 to 0.300 | yes | 0.228 to 0.272 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | -0.22 | -0.50 to 0.50 | yes | -0.45 to 0.01 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.081 | 0.000 to 0.100 | yes | 0.071 to 0.094 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 5 team-seasons per league (about 0.1 on the field at a time). They won 54.0% of their games (league average 50%), made the playoffs 53% of the time (14 of 40 teams = 35% on average) and won the title in 9.4% of seasons (1 in 40 = 2.5% on average).

## L. Worst case at the interview table: the 8 strongest hire the best and guarantee her three seasons, the 8 weakest hire the worst on no guarantee

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.149 | 0.130 to 0.190 | yes | 0.144 to 0.151 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.191 | 0.100 to 0.500 | yes | 0.149 to 0.231 |
| share of games decided by 8 points or fewer | 0.476 | 0.350 to 0.550 | yes | 0.473 to 0.480 |
| share of seasons in which the champion is the previous champion | 0.068 | 0.000 to 0.120 | yes | 0.026 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.00 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.125 | 0.080 to 0.250 | yes | 0.075 to 0.225 |
| average division finish of a team back from exile (3.0 = league average) | 3.23 | 2.80 to 3.40 | yes | 3.15 to 3.26 |
| share of returning teams that win their division | 0.153 | 0.100 to 0.300 | yes | 0.128 to 0.175 |
| share of returning teams that finish 5th again | 0.252 | 0.100 to 0.300 | yes | 0.237 to 0.275 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | -0.10 | -0.50 to 0.50 | yes | -0.36 to 0.29 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.085 | 0.000 to 0.100 | yes | 0.076 to 0.094 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 8 team-seasons per league (about 0.2 on the field at a time). They won 52.1% of their games (league average 50%), made the playoffs 40% of the time (14 of 40 teams = 35% on average) and won the title in 6.4% of seasons (1 in 40 = 2.5% on average).

## M. Every candidate refuses every job (the league office fills every seat by the old rule)

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.145 to 0.151 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.174 | 0.100 to 0.500 | yes | 0.150 to 0.201 |
| share of games decided by 8 points or fewer | 0.478 | 0.350 to 0.550 | yes | 0.469 to 0.485 |
| share of seasons in which the champion is the previous champion | 0.081 | 0.000 to 0.120 | yes | 0.000 to 0.179 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.00 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.192 | 0.080 to 0.250 | yes | 0.100 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.29 | 2.80 to 3.40 | yes | 3.21 to 3.38 |
| share of returning teams that win their division | 0.140 | 0.100 to 0.300 | yes | 0.122 to 0.172 |
| share of returning teams that finish 5th again | 0.272 | 0.100 to 0.300 | yes | 0.219 to 0.303 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | -0.24 | -0.50 to 0.50 | yes | -0.45 to -0.01 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.087 | 0.000 to 0.100 | yes | 0.074 to 0.099 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 12 team-seasons per league (about 0.3 on the field at a time). They won 52.0% of their games (league average 50%), made the playoffs 41% of the time (14 of 40 teams = 35% on average) and won the title in 5.8% of seasons (1 in 40 = 2.5% on average).

## N. Hard bargaining: every candidate asks for the most and walks without it, every CEO holds the line

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.145 to 0.151 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.174 | 0.100 to 0.500 | yes | 0.150 to 0.201 |
| share of games decided by 8 points or fewer | 0.478 | 0.350 to 0.550 | yes | 0.469 to 0.485 |
| share of seasons in which the champion is the previous champion | 0.081 | 0.000 to 0.120 | yes | 0.000 to 0.179 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.00 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.192 | 0.080 to 0.250 | yes | 0.100 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.29 | 2.80 to 3.40 | yes | 3.21 to 3.38 |
| share of returning teams that win their division | 0.140 | 0.100 to 0.300 | yes | 0.122 to 0.172 |
| share of returning teams that finish 5th again | 0.272 | 0.100 to 0.300 | yes | 0.219 to 0.303 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | -0.24 | -0.50 to 0.50 | yes | -0.45 to -0.01 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.087 | 0.000 to 0.100 | yes | 0.074 to 0.099 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 12 team-seasons per league (about 0.3 on the field at a time). They won 52.0% of their games (league average 50%), made the playoffs 41% of the time (14 of 40 teams = 35% on average) and won the title in 5.8% of seasons (1 in 40 = 2.5% on average).
