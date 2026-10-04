# Fair competitiveness report

Standard (Jeph, 2026-10-04): a trend is a problem when it falls outside the expected / accepted range of "fair competitiveness". The numeric ranges below are the AI's first proposal and are **assumed** until you set your own (`FAIR_COMPETITION_BANDS` in `engine/rules.py`). Each league runs 48 seasons; the first 8 are thrown away while the league settles. Values are averaged over the leagues; the last column shows the spread.

## fast engine, 8 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.149 | 0.130 to 0.190 | yes | 0.146 to 0.155 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.187 | 0.100 to 0.500 | yes | 0.166 to 0.214 |
| share of games decided by 8 points or fewer | 0.483 | 0.350 to 0.550 | yes | 0.477 to 0.492 |
| share of seasons in which the champion is the previous champion | 0.099 | 0.000 to 0.120 | yes | 0.051 to 0.179 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.38 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.219 | 0.080 to 0.250 | yes | 0.125 to 0.300 |
| average division finish of a team back from exile (3.0 = league average) | 3.19 | 2.80 to 3.40 | yes | 3.06 to 3.30 |
| share of returning teams that win their division | 0.164 | 0.100 to 0.300 | yes | 0.119 to 0.209 |
| share of returning teams that finish 5th again | 0.241 | 0.100 to 0.300 | yes | 0.206 to 0.281 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.27 | -0.50 to 0.50 | yes | -0.17 to 0.55 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.089 | 0.000 to 0.100 | yes | 0.084 to 0.097 |

All trends inside the bands.

## drives engine, 5 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.146 | 0.130 to 0.190 | yes | 0.144 to 0.148 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.157 | 0.100 to 0.500 | yes | 0.129 to 0.173 |
| share of games decided by 8 points or fewer | 0.519 | 0.350 to 0.550 | yes | 0.514 to 0.525 |
| share of seasons in which the champion is the previous champion | 0.051 | 0.000 to 0.120 | yes | 0.026 to 0.077 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.60 | 0.00 to 4.70 | yes | 3.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 5 | 0 to 7 | yes | 3 to 5 |
| how often the strongest team on paper wins the title | 0.190 | 0.080 to 0.250 | yes | 0.100 to 0.300 |
| average division finish of a team back from exile (3.0 = league average) | 3.19 | 2.80 to 3.40 | yes | 3.10 to 3.30 |
| share of returning teams that win their division | 0.171 | 0.100 to 0.300 | yes | 0.150 to 0.184 |
| share of returning teams that finish 5th again | 0.246 | 0.100 to 0.300 | yes | 0.222 to 0.278 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.34 | -0.50 to 0.50 | yes | 0.02 to 0.69 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.086 | 0.000 to 0.100 | yes | 0.081 to 0.094 |

All trends inside the bands.
