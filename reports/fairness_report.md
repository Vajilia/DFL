# Fair competitiveness report

Standard (Jeph, 2026-10-04): a trend is a problem when it falls outside the expected / accepted range of "fair competitiveness". The numeric ranges below are the AI's first proposal and are **assumed** until you set your own (`FAIR_COMPETITION_BANDS` in `engine/rules.py`). Each league runs 48 seasons; the first 8 are thrown away while the league settles. Values are averaged over the leagues; the last column shows the spread.

## fast engine, 8 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.149 | 0.130 to 0.190 | yes | 0.144 to 0.155 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.174 | 0.100 to 0.500 | yes | 0.130 to 0.230 |
| share of games decided by 8 points or fewer | 0.481 | 0.350 to 0.550 | yes | 0.471 to 0.490 |
| share of seasons in which the champion is the previous champion | 0.064 | 0.000 to 0.120 | yes | 0.026 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.62 | 0.00 to 4.70 | yes | 3.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 5 | 0 to 7 | yes | 3 to 5 |
| how often the strongest team on paper wins the title | 0.194 | 0.080 to 0.250 | yes | 0.125 to 0.325 |
| average division finish of a team back from exile (3.0 = league average) | 3.22 | 2.80 to 3.40 | yes | 3.11 to 3.29 |
| share of returning teams that win their division | 0.162 | 0.100 to 0.300 | yes | 0.131 to 0.216 |
| share of returning teams that finish 5th again | 0.258 | 0.100 to 0.300 | yes | 0.222 to 0.297 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.28 | -0.50 to 0.50 | yes | 0.07 to 0.56 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.090 | 0.000 to 0.100 | yes | 0.086 to 0.096 |

All trends inside the bands.

## drives engine, 5 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.146 | 0.130 to 0.190 | yes | 0.144 to 0.149 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.174 | 0.100 to 0.500 | yes | 0.158 to 0.213 |
| share of games decided by 8 points or fewer | 0.516 | 0.350 to 0.550 | yes | 0.511 to 0.521 |
| share of seasons in which the champion is the previous champion | 0.072 | 0.000 to 0.120 | yes | 0.051 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.20 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.195 | 0.080 to 0.250 | yes | 0.125 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.12 | 2.80 to 3.40 | yes | 3.02 to 3.22 |
| share of returning teams that win their division | 0.174 | 0.100 to 0.300 | yes | 0.134 to 0.206 |
| share of returning teams that finish 5th again | 0.223 | 0.100 to 0.300 | yes | 0.188 to 0.256 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.32 | -0.50 to 0.50 | yes | 0.05 to 0.69 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.083 | 0.000 to 0.100 | yes | 0.079 to 0.093 |

All trends inside the bands.
