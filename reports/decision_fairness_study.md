# Whatever the agents choose: fairness under the worst legal play

The principle: the road has guardrails and traffic controls, the character card is the driver, and what the driver does with the car always stays inside the fair-competitiveness bands. The first CEO choice to go through a Decision Point is keep, fire or hire for the coach and the GM (the hire is one of three candidates). The autopilot row reproduces the league as it was before agents. The other rows replace the CEOs' choices with random play and with adversaries that see the TRUE ratings of every candidate (no real agent can) and play the legal limit. Everything they do is a legal option; the guard would reject anything else.

*Re-run on 2026-10-05 with pay and the salary cap in place (6 leagues x 48 seasons per row).*

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

## B. Random legal choices

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.144 | 0.130 to 0.190 | yes | 0.142 to 0.144 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.122 | 0.100 to 0.500 | yes | 0.089 to 0.149 |
| share of games decided by 8 points or fewer | 0.480 | 0.350 to 0.550 | yes | 0.471 to 0.488 |
| share of seasons in which the champion is the previous champion | 0.047 | 0.000 to 0.120 | yes | 0.000 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.67 | 0.00 to 4.70 | yes | 3.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 5 | 0 to 7 | yes | 3 to 5 |
| how often the strongest team on paper wins the title | 0.121 | 0.080 to 0.250 | yes | 0.075 to 0.175 |
| average division finish of a team back from exile (3.0 = league average) | 3.08 | 2.80 to 3.40 | yes | 2.98 to 3.17 |
| share of returning teams that win their division | 0.190 | 0.100 to 0.300 | yes | 0.166 to 0.228 |
| share of returning teams that finish 5th again | 0.218 | 0.100 to 0.300 | yes | 0.200 to 0.237 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.76 | -0.50 to 0.50 | **NO** | 0.53 to 1.09 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.074 | 0.000 to 0.100 | yes | 0.070 to 0.079 |

**Outside the bands:** exile_effect.

Note (2026-10-10, GM roster step): this row was re-run after the GM's roster decisions were added. Only the exile-return effect is outside (0.76 against a cap of 0.50). With the new GM decisions left on the autopilot and everything else random it is already 0.58, so the excess predates this step (it is not in the 2026-10-08 run of this row, which gave 0.29); the GM's roster decisions alone, chosen at random, stay inside every band (repeat 0.129, exile effect 0.37). Each earlier group of decisions chosen at random alone also stays inside (coordinators and schemes -0.38, the GM plan 0.16, fans and CEOs -0.21), so the excess comes from random play across many groups at once. Open: find which group combination drives it.

Teams led by a coach the media calls a legend: 0 team-seasons per league (about 0.0 on the field at a time). They won 66.7% of their games (league average 50%), made the playoffs 100% of the time (14 of 40 teams = 35% on average) and won the title in 0.0% of seasons (1 in 40 = 2.5% on average).

## C. Nobody is ever fired

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.142 | 0.130 to 0.190 | yes | 0.139 to 0.147 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.130 | 0.100 to 0.500 | yes | 0.103 to 0.173 |
| share of games decided by 8 points or fewer | 0.487 | 0.350 to 0.550 | yes | 0.483 to 0.491 |
| share of seasons in which the champion is the previous champion | 0.030 | 0.000 to 0.120 | yes | 0.000 to 0.077 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.17 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.154 | 0.080 to 0.250 | yes | 0.100 to 0.225 |
| average division finish of a team back from exile (3.0 = league average) | 3.10 | 2.80 to 3.40 | yes | 3.03 to 3.16 |
| share of returning teams that win their division | 0.176 | 0.100 to 0.300 | yes | 0.163 to 0.206 |
| share of returning teams that finish 5th again | 0.215 | 0.100 to 0.300 | yes | 0.203 to 0.228 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.25 | -0.50 to 0.50 | yes | 0.05 to 0.56 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.079 | 0.000 to 0.100 | yes | 0.068 to 0.087 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 4 team-seasons per league (about 0.1 on the field at a time). They won 53.0% of their games (league average 50%), made the playoffs 45% of the time (14 of 40 teams = 35% on average) and won the title in 4.5% of seasons (1 in 40 = 2.5% on average).

## D. Worst case: every CEO fires everyone every year and hires the truly best candidate

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.143 | 0.130 to 0.190 | yes | 0.138 to 0.147 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.136 | 0.100 to 0.500 | yes | 0.073 to 0.184 |
| share of games decided by 8 points or fewer | 0.485 | 0.350 to 0.550 | yes | 0.475 to 0.489 |
| share of seasons in which the champion is the previous champion | 0.038 | 0.000 to 0.120 | yes | 0.000 to 0.077 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.00 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.179 | 0.080 to 0.250 | yes | 0.150 to 0.225 |
| average division finish of a team back from exile (3.0 = league average) | 3.07 | 2.80 to 3.40 | yes | 2.94 to 3.19 |
| share of returning teams that win their division | 0.184 | 0.100 to 0.300 | yes | 0.147 to 0.216 |
| share of returning teams that finish 5th again | 0.217 | 0.100 to 0.300 | yes | 0.169 to 0.269 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.42 | -0.50 to 0.50 | yes | 0.18 to 0.63 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.073 | 0.000 to 0.100 | yes | 0.068 to 0.084 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 0 team-seasons per league (about 0.0 on the field at a time). They won 36.1% of their games (league average 50%), made the playoffs 0% of the time (14 of 40 teams = 35% on average) and won the title in 0.0% of seasons (1 in 40 = 2.5% on average).

## E. Worst case: only the 8 strongest teams churn and hire perfectly

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.145 | 0.130 to 0.190 | yes | 0.143 to 0.150 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.155 | 0.100 to 0.500 | yes | 0.132 to 0.171 |
| share of games decided by 8 points or fewer | 0.486 | 0.350 to 0.550 | yes | 0.483 to 0.491 |
| share of seasons in which the champion is the previous champion | 0.030 | 0.000 to 0.120 | yes | 0.000 to 0.077 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.67 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.183 | 0.080 to 0.250 | yes | 0.125 to 0.250 |
| average division finish of a team back from exile (3.0 = league average) | 3.07 | 2.80 to 3.40 | yes | 3.00 to 3.16 |
| share of returning teams that win their division | 0.188 | 0.100 to 0.300 | yes | 0.156 to 0.219 |
| share of returning teams that finish 5th again | 0.218 | 0.100 to 0.300 | yes | 0.200 to 0.244 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.25 | -0.50 to 0.50 | yes | 0.00 to 0.50 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.081 | 0.000 to 0.100 | yes | 0.070 to 0.098 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 1 team-seasons per league (about 0.0 on the field at a time). They won 52.8% of their games (league average 50%), made the playoffs 38% of the time (14 of 40 teams = 35% on average) and won the title in 0.0% of seasons (1 in 40 = 2.5% on average).

## F. Worst case: the 8 strongest hire the best, the 8 weakest the worst, every year

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.146 | 0.130 to 0.190 | yes | 0.140 to 0.150 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.167 | 0.100 to 0.500 | yes | 0.138 to 0.200 |
| share of games decided by 8 points or fewer | 0.485 | 0.350 to 0.550 | yes | 0.481 to 0.489 |
| share of seasons in which the champion is the previous champion | 0.051 | 0.000 to 0.120 | yes | 0.000 to 0.154 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.00 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.154 | 0.080 to 0.250 | yes | 0.050 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.09 | 2.80 to 3.40 | yes | 3.05 to 3.19 |
| share of returning teams that win their division | 0.179 | 0.100 to 0.300 | yes | 0.153 to 0.200 |
| share of returning teams that finish 5th again | 0.215 | 0.100 to 0.300 | yes | 0.200 to 0.247 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.24 | -0.50 to 0.50 | yes | 0.03 to 0.37 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.072 | 0.000 to 0.100 | yes | 0.062 to 0.084 |

All trends inside the bands.

No team was led by a media-recognized legend.

## G. Worst case: everyone hunts for the most famous coach

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.143 | 0.130 to 0.190 | yes | 0.141 to 0.146 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.134 | 0.100 to 0.500 | yes | 0.105 to 0.166 |
| share of games decided by 8 points or fewer | 0.485 | 0.350 to 0.550 | yes | 0.478 to 0.491 |
| share of seasons in which the champion is the previous champion | 0.043 | 0.000 to 0.120 | yes | 0.026 to 0.077 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 2.83 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.171 | 0.080 to 0.250 | yes | 0.125 to 0.225 |
| average division finish of a team back from exile (3.0 = league average) | 3.07 | 2.80 to 3.40 | yes | 3.02 to 3.15 |
| share of returning teams that win their division | 0.183 | 0.100 to 0.300 | yes | 0.159 to 0.200 |
| share of returning teams that finish 5th again | 0.211 | 0.100 to 0.300 | yes | 0.203 to 0.225 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.38 | -0.50 to 0.50 | yes | 0.08 to 0.64 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.074 | 0.000 to 0.100 | yes | 0.071 to 0.077 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 1 team-seasons per league (about 0.0 on the field at a time). They won 46.5% of their games (league average 50%), made the playoffs 25% of the time (14 of 40 teams = 35% on average) and won the title in 0.0% of seasons (1 in 40 = 2.5% on average).

## H. Worst case: every CEO recycles the same people between jobs

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.142 | 0.130 to 0.190 | yes | 0.139 to 0.144 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.155 | 0.100 to 0.500 | yes | 0.139 to 0.169 |
| share of games decided by 8 points or fewer | 0.488 | 0.350 to 0.550 | yes | 0.480 to 0.493 |
| share of seasons in which the champion is the previous champion | 0.073 | 0.000 to 0.120 | yes | 0.051 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.50 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.237 | 0.080 to 0.250 | yes | 0.100 to 0.300 |
| average division finish of a team back from exile (3.0 = league average) | 3.12 | 2.80 to 3.40 | yes | 3.06 to 3.19 |
| share of returning teams that win their division | 0.178 | 0.100 to 0.300 | yes | 0.159 to 0.203 |
| share of returning teams that finish 5th again | 0.233 | 0.100 to 0.300 | yes | 0.222 to 0.253 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.18 | -0.50 to 0.50 | yes | 0.00 to 0.53 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.077 | 0.000 to 0.100 | yes | 0.069 to 0.080 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 14 team-seasons per league (about 0.3 on the field at a time). They won 52.6% of their games (league average 50%), made the playoffs 43% of the time (14 of 40 teams = 35% on average) and won the title in 4.9% of seasons (1 in 40 = 2.5% on average).

## O. Worst case at the GM's desk: the 8 strongest GMs choose every draft position, re-signing, signing and trade with perfect sight, the 8 weakest choose the worst

fast engine, 6 leagues x 48 seasons.

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.149 | 0.130 to 0.190 | yes | 0.143 to 0.153 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.183 | 0.100 to 0.500 | yes | 0.152 to 0.221 |
| share of games decided by 8 points or fewer | 0.478 | 0.350 to 0.550 | yes | 0.474 to 0.483 |
| share of seasons in which the champion is the previous champion | 0.038 | 0.000 to 0.120 | yes | 0.000 to 0.077 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 2.83 | 0.00 to 4.70 | yes | 2.00 to 3.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 3 | 0 to 7 | yes | 2 to 3 |
| how often the strongest team on paper wins the title | 0.171 | 0.080 to 0.250 | yes | 0.125 to 0.250 |
| average division finish of a team back from exile (3.0 = league average) | 3.24 | 2.80 to 3.40 | yes | 3.12 to 3.39 |
| share of returning teams that win their division | 0.161 | 0.100 to 0.300 | yes | 0.128 to 0.194 |
| share of returning teams that finish 5th again | 0.253 | 0.100 to 0.300 | yes | 0.219 to 0.291 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | -0.09 | -0.50 to 0.50 | yes | -0.43 to 0.30 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.093 | 0.000 to 0.100 | yes | 0.083 to 0.101 |

All trends inside the bands.

Teams led by a coach the media calls a legend: 5 team-seasons per league (about 0.1 on the field at a time). They won 48.4% of their games (league average 50%), made the playoffs 37% of the time (14 of 40 teams = 35% on average) and won the title in 0.0% of seasons (1 in 40 = 2.5% on average).
