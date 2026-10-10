# Fair competitiveness report

Standard (the Commissioner, 2026-10-04): a trend is a problem when it falls outside the expected / accepted range of "fair competitiveness". The numeric ranges below were proposed by the AI and are accepted by the Commissioner as the working limits (`FAIR_COMPETITION_BANDS` in `engine/rules.py`; the rulebook's "fair" basis). Each league runs 48 seasons; the first 8 are thrown away while the league settles. Values are averaged over the leagues; the last column shows the spread.

## fast engine, 12 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.144 to 0.152 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.180 | 0.100 to 0.500 | yes | 0.146 to 0.213 |
| share of games decided by 8 points or fewer | 0.477 | 0.350 to 0.550 | yes | 0.469 to 0.485 |
| share of seasons in which the champion is the previous champion | 0.079 | 0.000 to 0.120 | yes | 0.000 to 0.179 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.08 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.173 | 0.080 to 0.250 | yes | 0.075 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.28 | 2.80 to 3.40 | yes | 3.21 to 3.38 |
| share of returning teams that win their division | 0.145 | 0.100 to 0.300 | yes | 0.122 to 0.181 |
| share of returning teams that finish 5th again | 0.258 | 0.100 to 0.300 | yes | 0.219 to 0.303 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | -0.24 | -0.50 to 0.50 | yes | -0.51 to 0.07 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.088 | 0.000 to 0.100 | yes | 0.074 to 0.099 |

All trends inside the bands.

## drives engine, 6 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.144 to 0.152 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.188 | 0.100 to 0.500 | yes | 0.166 to 0.233 |
| share of games decided by 8 points or fewer | 0.506 | 0.350 to 0.550 | yes | 0.504 to 0.508 |
| share of seasons in which the champion is the previous champion | 0.056 | 0.000 to 0.120 | yes | 0.026 to 0.103 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.00 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.142 | 0.080 to 0.250 | yes | 0.075 to 0.225 |
| average division finish of a team back from exile (3.0 = league average) | 3.33 | 2.80 to 3.40 | yes | 3.18 to 3.43 |
| share of returning teams that win their division | 0.139 | 0.100 to 0.300 | yes | 0.106 to 0.188 |
| share of returning teams that finish 5th again | 0.269 | 0.100 to 0.300 | yes | 0.241 to 0.309 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | -0.05 | -0.50 to 0.50 | yes | -0.36 to 0.46 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.094 | 0.000 to 0.100 | yes | 0.086 to 0.103 |

All trends inside the bands.
