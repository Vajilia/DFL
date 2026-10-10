# Agents in the CEOs' seats: fairness with a stand-in agent

A stand-in agent (agents.py) reads only the view a real agent would be shown (the deciding card, her notes, the options with the ratings she perceives) and chooses from the engine's options; CEOs with different personalities choose differently. It is a rulebook, not a model, so this tests the machinery and the bands, not the quality of a real agent's judgment. Rows: all 48 seats, a dozen seats, and an agent whose answers are often lost or invalid.

## A. Autopilot (the rules as they were before agents)

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.145 to 0.149 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.190 | 0.100 to 0.500 | yes | 0.152 to 0.233 |
| share of games decided by 8 points or fewer | 0.478 | 0.350 to 0.550 | yes | 0.472 to 0.486 |
| share of seasons in which the champion is the previous champion | 0.081 | 0.000 to 0.120 | yes | 0.051 to 0.154 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.50 | 0.00 to 4.70 | yes | 2.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 5 | 0 to 7 | yes | 2 to 5 |
| how often the strongest team on paper wins the title | 0.150 | 0.080 to 0.250 | yes | 0.100 to 0.225 |
| average division finish of a team back from exile (3.0 = league average) | 3.20 | 2.80 to 3.40 | yes | 3.10 to 3.29 |
| share of returning teams that win their division | 0.164 | 0.100 to 0.300 | yes | 0.150 to 0.175 |
| share of returning teams that finish 5th again | 0.244 | 0.100 to 0.300 | yes | 0.222 to 0.269 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.20 | -0.50 to 0.50 | yes | -0.36 to 0.52 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.084 | 0.000 to 0.100 | yes | 0.069 to 0.091 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 6 team-seasons per league (about 0.1 on the field at a time). They won 48.4% of their games (league average 50%), made the playoffs 34% of the time (14 of 40 teams = 35% on average) and won the title in 0.0% of seasons (1 in 40 = 2.5% on average).

## I. A stand-in agent in all 48 CEOs' seats (cards decide, a dozen at a time)

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.141 | 0.130 to 0.190 | yes | 0.139 to 0.143 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.147 | 0.100 to 0.500 | yes | 0.116 to 0.175 |
| share of games decided by 8 points or fewer | 0.483 | 0.350 to 0.550 | yes | 0.479 to 0.488 |
| share of seasons in which the champion is the previous champion | 0.038 | 0.000 to 0.120 | yes | 0.026 to 0.077 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.00 | 0.00 to 4.70 | yes | 3.00 to 3.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 3 | 0 to 7 | yes | 3 to 3 |
| how often the strongest team on paper wins the title | 0.129 | 0.080 to 0.250 | yes | 0.050 to 0.175 |
| average division finish of a team back from exile (3.0 = league average) | 3.14 | 2.80 to 3.40 | yes | 3.04 to 3.25 |
| share of returning teams that win their division | 0.178 | 0.100 to 0.300 | yes | 0.159 to 0.212 |
| share of returning teams that finish 5th again | 0.226 | 0.100 to 0.300 | yes | 0.203 to 0.256 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.23 | -0.50 to 0.50 | yes | -0.05 to 0.45 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.082 | 0.000 to 0.100 | yes | 0.076 to 0.090 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 3 team-seasons per league (about 0.1 on the field at a time). They won 49.2% of their games (league average 50%), made the playoffs 35% of the time (14 of 40 teams = 35% on average) and won the title in 0.0% of seasons (1 in 40 = 2.5% on average).

## J. Agents in 12 seats (every fourth team), the autopilot in the other 36

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.146 | 0.130 to 0.190 | yes | 0.143 to 0.149 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.158 | 0.100 to 0.500 | yes | 0.135 to 0.179 |
| share of games decided by 8 points or fewer | 0.481 | 0.350 to 0.550 | yes | 0.474 to 0.492 |
| share of seasons in which the champion is the previous champion | 0.038 | 0.000 to 0.120 | yes | 0.026 to 0.051 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.17 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.146 | 0.080 to 0.250 | yes | 0.075 to 0.250 |
| average division finish of a team back from exile (3.0 = league average) | 3.19 | 2.80 to 3.40 | yes | 3.12 to 3.25 |
| share of returning teams that win their division | 0.157 | 0.100 to 0.300 | yes | 0.144 to 0.172 |
| share of returning teams that finish 5th again | 0.232 | 0.100 to 0.300 | yes | 0.212 to 0.244 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.26 | -0.50 to 0.50 | yes | -0.03 to 0.46 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.083 | 0.000 to 0.100 | yes | 0.072 to 0.090 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 6 team-seasons per league (about 0.2 on the field at a time). They won 53.4% of their games (league average 50%), made the playoffs 46% of the time (14 of 40 teams = 35% on average) and won the title in 2.6% of seasons (1 in 40 = 2.5% on average).

## K. The same agent, but a quarter of its answers are lost or invalid (the autopilot steps in)

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.141 | 0.130 to 0.190 | yes | 0.138 to 0.144 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.125 | 0.100 to 0.500 | yes | 0.079 to 0.164 |
| share of games decided by 8 points or fewer | 0.482 | 0.350 to 0.550 | yes | 0.474 to 0.487 |
| share of seasons in which the champion is the previous champion | 0.038 | 0.000 to 0.120 | yes | 0.000 to 0.077 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.00 | 0.00 to 4.70 | yes | 3.00 to 3.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 3 | 0 to 7 | yes | 3 to 3 |
| how often the strongest team on paper wins the title | 0.154 | 0.080 to 0.250 | yes | 0.125 to 0.175 |
| average division finish of a team back from exile (3.0 = league average) | 3.16 | 2.80 to 3.40 | yes | 3.11 to 3.22 |
| share of returning teams that win their division | 0.174 | 0.100 to 0.300 | yes | 0.159 to 0.194 |
| share of returning teams that finish 5th again | 0.243 | 0.100 to 0.300 | yes | 0.216 to 0.266 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.13 | -0.50 to 0.50 | yes | -0.17 to 0.30 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.077 | 0.000 to 0.100 | yes | 0.072 to 0.081 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 4 team-seasons per league (about 0.1 on the field at a time). They won 49.2% of their games (league average 50%), made the playoffs 32% of the time (14 of 40 teams = 35% on average) and won the title in 0.0% of seasons (1 in 40 = 2.5% on average).

## L. Worst case at the interview table: the 8 strongest hire the best and guarantee her three seasons, the 8 weakest hire the worst on no guarantee

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.148 | 0.130 to 0.190 | yes | 0.144 to 0.151 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.162 | 0.100 to 0.500 | yes | 0.128 to 0.204 |
| share of games decided by 8 points or fewer | 0.478 | 0.350 to 0.550 | yes | 0.475 to 0.478 |
| share of seasons in which the champion is the previous champion | 0.060 | 0.000 to 0.120 | yes | 0.000 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 2.83 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.150 | 0.080 to 0.250 | yes | 0.100 to 0.200 |
| average division finish of a team back from exile (3.0 = league average) | 3.25 | 2.80 to 3.40 | yes | 3.19 to 3.31 |
| share of returning teams that win their division | 0.155 | 0.100 to 0.300 | yes | 0.147 to 0.169 |
| share of returning teams that finish 5th again | 0.253 | 0.100 to 0.300 | yes | 0.237 to 0.272 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.12 | -0.50 to 0.50 | yes | 0.03 to 0.33 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.084 | 0.000 to 0.100 | yes | 0.078 to 0.091 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 9 team-seasons per league (about 0.2 on the field at a time). They won 49.4% of their games (league average 50%), made the playoffs 36% of the time (14 of 40 teams = 35% on average) and won the title in 0.0% of seasons (1 in 40 = 2.5% on average).

## M. Every candidate refuses every job (the league office fills every seat by the old rule)

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.145 to 0.149 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.190 | 0.100 to 0.500 | yes | 0.152 to 0.233 |
| share of games decided by 8 points or fewer | 0.478 | 0.350 to 0.550 | yes | 0.472 to 0.486 |
| share of seasons in which the champion is the previous champion | 0.081 | 0.000 to 0.120 | yes | 0.051 to 0.154 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.50 | 0.00 to 4.70 | yes | 2.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 5 | 0 to 7 | yes | 2 to 5 |
| how often the strongest team on paper wins the title | 0.150 | 0.080 to 0.250 | yes | 0.100 to 0.225 |
| average division finish of a team back from exile (3.0 = league average) | 3.20 | 2.80 to 3.40 | yes | 3.10 to 3.29 |
| share of returning teams that win their division | 0.164 | 0.100 to 0.300 | yes | 0.150 to 0.175 |
| share of returning teams that finish 5th again | 0.244 | 0.100 to 0.300 | yes | 0.222 to 0.269 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.20 | -0.50 to 0.50 | yes | -0.36 to 0.52 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.084 | 0.000 to 0.100 | yes | 0.069 to 0.091 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 6 team-seasons per league (about 0.1 on the field at a time). They won 48.4% of their games (league average 50%), made the playoffs 34% of the time (14 of 40 teams = 35% on average) and won the title in 0.0% of seasons (1 in 40 = 2.5% on average).

## N. Hard bargaining: every candidate asks for the most and walks without it, every CEO holds the line

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.145 to 0.149 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.190 | 0.100 to 0.500 | yes | 0.152 to 0.233 |
| share of games decided by 8 points or fewer | 0.478 | 0.350 to 0.550 | yes | 0.472 to 0.486 |
| share of seasons in which the champion is the previous champion | 0.081 | 0.000 to 0.120 | yes | 0.051 to 0.154 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.50 | 0.00 to 4.70 | yes | 2.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 5 | 0 to 7 | yes | 2 to 5 |
| how often the strongest team on paper wins the title | 0.150 | 0.080 to 0.250 | yes | 0.100 to 0.225 |
| average division finish of a team back from exile (3.0 = league average) | 3.20 | 2.80 to 3.40 | yes | 3.10 to 3.29 |
| share of returning teams that win their division | 0.164 | 0.100 to 0.300 | yes | 0.150 to 0.175 |
| share of returning teams that finish 5th again | 0.244 | 0.100 to 0.300 | yes | 0.222 to 0.269 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.20 | -0.50 to 0.50 | yes | -0.36 to 0.52 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.084 | 0.000 to 0.100 | yes | 0.069 to 0.091 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 6 team-seasons per league (about 0.1 on the field at a time). They won 48.4% of their games (league average 50%), made the playoffs 34% of the time (14 of 40 teams = 35% on average) and won the title in 0.0% of seasons (1 in 40 = 2.5% on average).
