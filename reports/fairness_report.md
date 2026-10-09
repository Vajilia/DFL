# Fair competitiveness report

Standard (the Commissioner, 2026-10-04): a trend is a problem when it falls outside the expected / accepted range of "fair competitiveness". The numeric ranges below were proposed by the AI and are accepted by the Commissioner as the working limits (`FAIR_COMPETITION_BANDS` in `engine/rules.py`; the rulebook's "fair" basis). Each league runs 48 seasons; the first 8 are thrown away while the league settles. Values are averaged over the leagues; the last column shows the spread.

## fast engine, 12 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.148 | 0.130 to 0.190 | yes | 0.144 to 0.153 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.178 | 0.100 to 0.500 | yes | 0.114 to 0.228 |
| share of games decided by 8 points or fewer | 0.480 | 0.350 to 0.550 | yes | 0.474 to 0.486 |
| share of seasons in which the champion is the previous champion | 0.051 | 0.000 to 0.120 | yes | 0.000 to 0.154 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.00 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.154 | 0.080 to 0.250 | yes | 0.075 to 0.250 |
| average division finish of a team back from exile (3.0 = league average) | 3.28 | 2.80 to 3.40 | yes | 3.15 to 3.40 |
| share of returning teams that win their division | 0.154 | 0.100 to 0.300 | yes | 0.125 to 0.178 |
| share of returning teams that finish 5th again | 0.268 | 0.100 to 0.300 | yes | 0.244 to 0.297 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | -0.20 | -0.50 to 0.50 | yes | -0.69 to 0.44 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.091 | 0.000 to 0.100 | yes | 0.078 to 0.103 |

All trends inside the bands.

## drives engine, 6 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.148 | 0.130 to 0.190 | yes | 0.144 to 0.152 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.173 | 0.100 to 0.500 | yes | 0.115 to 0.216 |
| share of games decided by 8 points or fewer | 0.510 | 0.350 to 0.550 | yes | 0.507 to 0.516 |
| share of seasons in which the champion is the previous champion | 0.038 | 0.000 to 0.120 | yes | 0.026 to 0.051 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.33 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.138 | 0.080 to 0.250 | yes | 0.050 to 0.250 |
| average division finish of a team back from exile (3.0 = league average) | 3.28 | 2.80 to 3.40 | yes | 3.20 to 3.33 |
| share of returning teams that win their division | 0.165 | 0.100 to 0.300 | yes | 0.144 to 0.188 |
| share of returning teams that finish 5th again | 0.267 | 0.100 to 0.300 | yes | 0.216 to 0.294 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | -0.20 | -0.50 to 0.50 | yes | -0.46 to 0.16 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.088 | 0.000 to 0.100 | yes | 0.079 to 0.092 |

All trends inside the bands.
