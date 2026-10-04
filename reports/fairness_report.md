# Fair competitiveness report

Standard (Jeph, 2026-10-04): a trend is a problem when it falls outside the expected / accepted range of "fair competitiveness". The numeric ranges below are the AI's first proposal and are **assumed** until you set your own (`FAIR_COMPETITION_BANDS` in `engine/rules.py`). Each league runs 48 seasons; the first 8 are thrown away while the league settles. Values are averaged over the leagues; the last column shows the spread.

## fast engine, 12 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.149 | 0.130 to 0.190 | yes | 0.143 to 0.156 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.186 | 0.100 to 0.500 | yes | 0.127 to 0.226 |
| share of games decided by 8 points or fewer | 0.482 | 0.350 to 0.550 | yes | 0.470 to 0.490 |
| share of seasons in which the champion is the previous champion | 0.075 | 0.000 to 0.120 | yes | 0.026 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.17 | 0.00 to 4.70 | yes | 2.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 5 | 0 to 7 | yes | 2 to 5 |
| how often the strongest team on paper wins the title | 0.229 | 0.080 to 0.250 | yes | 0.150 to 0.325 |
| average division finish of a team back from exile (3.0 = league average) | 3.15 | 2.80 to 3.40 | yes | 2.98 to 3.28 |
| share of returning teams that win their division | 0.180 | 0.100 to 0.300 | yes | 0.128 to 0.228 |
| share of returning teams that finish 5th again | 0.234 | 0.100 to 0.300 | yes | 0.209 to 0.263 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.35 | -0.50 to 0.50 | yes | -0.09 to 0.89 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.088 | 0.000 to 0.100 | yes | 0.082 to 0.104 |

All trends inside the bands.

## drives engine, 6 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.148 | 0.130 to 0.190 | yes | 0.145 to 0.151 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.169 | 0.100 to 0.500 | yes | 0.140 to 0.199 |
| share of games decided by 8 points or fewer | 0.514 | 0.350 to 0.550 | yes | 0.507 to 0.524 |
| share of seasons in which the champion is the previous champion | 0.060 | 0.000 to 0.120 | yes | 0.000 to 0.154 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.50 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.212 | 0.080 to 0.250 | yes | 0.100 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.15 | 2.80 to 3.40 | yes | 3.06 to 3.22 |
| share of returning teams that win their division | 0.176 | 0.100 to 0.300 | yes | 0.156 to 0.197 |
| share of returning teams that finish 5th again | 0.237 | 0.100 to 0.300 | yes | 0.200 to 0.275 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.11 | -0.50 to 0.50 | yes | -0.25 to 0.25 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.088 | 0.000 to 0.100 | yes | 0.085 to 0.092 |

All trends inside the bands.
