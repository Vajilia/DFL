# Fair competitiveness report

Standard (Jeph, 2026-10-04): a trend is a problem when it falls outside the expected / accepted range of "fair competitiveness". The numeric ranges below are the AI's first proposal and are **assumed** until you set your own (`FAIR_COMPETITION_BANDS` in `engine/rules.py`). Each league runs 48 seasons; the first 8 are thrown away while the league settles. Values are averaged over the leagues; the last column shows the spread.

## fast engine, 8 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.143 to 0.152 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.185 | 0.100 to 0.500 | yes | 0.148 to 0.214 |
| share of games decided by 8 points or fewer | 0.483 | 0.350 to 0.550 | yes | 0.479 to 0.489 |
| share of seasons in which the champion is the previous champion | 0.087 | 0.000 to 0.120 | yes | 0.051 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.75 | 0.00 to 4.70 | yes | 3.00 to 6.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 6 | 0 to 7 | yes | 3 to 6 |
| how often the strongest team on paper wins the title | 0.216 | 0.080 to 0.250 | yes | 0.125 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.13 | 2.80 to 3.40 | yes | 2.99 to 3.23 |
| share of returning teams that win their division | 0.182 | 0.100 to 0.300 | yes | 0.163 to 0.209 |
| share of returning teams that finish 5th again | 0.234 | 0.100 to 0.300 | yes | 0.203 to 0.256 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.31 | -0.50 to 0.50 | yes | 0.10 to 0.49 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.084 | 0.000 to 0.100 | yes | 0.074 to 0.091 |

All trends inside the bands.

## drives engine, 5 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.145 | 0.130 to 0.190 | yes | 0.142 to 0.150 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.160 | 0.100 to 0.500 | yes | 0.129 to 0.186 |
| share of games decided by 8 points or fewer | 0.514 | 0.350 to 0.550 | yes | 0.509 to 0.519 |
| share of seasons in which the champion is the previous champion | 0.092 | 0.000 to 0.120 | yes | 0.026 to 0.154 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.80 | 0.00 to 4.70 | yes | 3.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 5 | 0 to 7 | yes | 3 to 5 |
| how often the strongest team on paper wins the title | 0.180 | 0.080 to 0.250 | yes | 0.150 to 0.250 |
| average division finish of a team back from exile (3.0 = league average) | 3.10 | 2.80 to 3.40 | yes | 3.02 to 3.14 |
| share of returning teams that win their division | 0.189 | 0.100 to 0.300 | yes | 0.172 to 0.212 |
| share of returning teams that finish 5th again | 0.231 | 0.100 to 0.300 | yes | 0.209 to 0.256 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.37 | -0.50 to 0.50 | yes | 0.19 to 0.58 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.084 | 0.000 to 0.100 | yes | 0.071 to 0.094 |

All trends inside the bands.
