# Fair competitiveness report

Standard (Jeph, 2026-10-04): a trend is a problem when it falls outside the expected / accepted range of "fair competitiveness". The numeric ranges below are the AI's first proposal and are **assumed** until you set your own (`FAIR_COMPETITION_BANDS` in `engine/rules.py`). Each league runs 48 seasons; the first 8 are thrown away while the league settles. Values are averaged over the leagues; the last column shows the spread.

## fast engine, 12 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.149 | 0.130 to 0.190 | yes | 0.142 to 0.155 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.171 | 0.100 to 0.500 | yes | 0.134 to 0.222 |
| share of games decided by 8 points or fewer | 0.480 | 0.350 to 0.550 | yes | 0.474 to 0.490 |
| share of seasons in which the champion is the previous champion | 0.060 | 0.000 to 0.120 | yes | 0.000 to 0.154 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 2.92 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.204 | 0.080 to 0.250 | yes | 0.125 to 0.425 |
| average division finish of a team back from exile (3.0 = league average) | 3.21 | 2.80 to 3.40 | yes | 3.04 to 3.38 |
| share of returning teams that win their division | 0.160 | 0.100 to 0.300 | yes | 0.131 to 0.194 |
| share of returning teams that finish 5th again | 0.249 | 0.100 to 0.300 | yes | 0.197 to 0.294 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.31 | -0.50 to 0.50 | yes | -0.14 to 0.99 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.087 | 0.000 to 0.100 | yes | 0.077 to 0.099 |

All trends inside the bands.

## drives engine, 6 leagues x 48 seasons

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
