# Fair competitiveness report

Standard (the Commissioner, 2026-10-04): a trend is a problem when it falls outside the expected / accepted range of "fair competitiveness". The numeric ranges below were proposed by the AI and are accepted by the Commissioner as the working limits (`FAIR_COMPETITION_BANDS` in `engine/rules.py`; the rulebook's "fair" basis). Each league runs 48 seasons; the first 8 are thrown away while the league settles. Values are averaged over the leagues; the last column shows the spread.

## fast engine, 12 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.148 | 0.130 to 0.190 | yes | 0.142 to 0.151 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.170 | 0.100 to 0.500 | yes | 0.133 to 0.220 |
| share of games decided by 8 points or fewer | 0.477 | 0.350 to 0.550 | yes | 0.472 to 0.488 |
| share of seasons in which the champion is the previous champion | 0.058 | 0.000 to 0.120 | yes | 0.000 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 2.92 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.185 | 0.080 to 0.250 | yes | 0.075 to 0.300 |
| average division finish of a team back from exile (3.0 = league average) | 3.26 | 2.80 to 3.40 | yes | 3.14 to 3.41 |
| share of returning teams that win their division | 0.152 | 0.100 to 0.300 | yes | 0.134 to 0.181 |
| share of returning teams that finish 5th again | 0.259 | 0.100 to 0.300 | yes | 0.228 to 0.319 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | -0.13 | -0.50 to 0.50 | yes | -0.38 to 0.20 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.084 | 0.000 to 0.100 | yes | 0.073 to 0.094 |

All trends inside the bands.

## drives engine, 6 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.144 to 0.148 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.158 | 0.100 to 0.500 | yes | 0.118 to 0.173 |
| share of games decided by 8 points or fewer | 0.511 | 0.350 to 0.550 | yes | 0.504 to 0.517 |
| share of seasons in which the champion is the previous champion | 0.056 | 0.000 to 0.120 | yes | 0.000 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.17 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.142 | 0.080 to 0.250 | yes | 0.100 to 0.200 |
| average division finish of a team back from exile (3.0 = league average) | 3.23 | 2.80 to 3.40 | yes | 3.16 to 3.30 |
| share of returning teams that win their division | 0.158 | 0.100 to 0.300 | yes | 0.128 to 0.172 |
| share of returning teams that finish 5th again | 0.260 | 0.100 to 0.300 | yes | 0.216 to 0.303 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.03 | -0.50 to 0.50 | yes | -0.28 to 0.44 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.085 | 0.000 to 0.100 | yes | 0.069 to 0.095 |

All trends inside the bands.
