# Fair competitiveness report

Standard (Jeph, 2026-10-04): a trend is a problem when it falls outside the expected / accepted range of "fair competitiveness". The numeric ranges below are the AI's first proposal and are **assumed** until you set your own (`FAIR_COMPETITION_BANDS` in `engine/rules.py`). Each league runs 48 seasons; the first 8 are thrown away while the league settles. Values are averaged over the leagues; the last column shows the spread.

## fast engine, 8 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.147 | 0.130 to 0.190 | yes | 0.145 to 0.150 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.167 | 0.100 to 0.500 | yes | 0.132 to 0.203 |
| share of games decided by 8 points or fewer | 0.482 | 0.350 to 0.550 | yes | 0.472 to 0.486 |
| share of seasons in which the champion is the previous champion | 0.054 | 0.000 to 0.120 | yes | 0.000 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues (the luckiest of 40 equal teams gets 2-3; a 14-team playoff field gives 3-5) | 3.25 | 0.00 to 4.00 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (6 or more is a dynasty) | 4 | 0 to 5 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.206 | 0.080 to 0.250 | yes | 0.125 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.15 | 2.80 to 3.40 | yes | 3.05 to 3.27 |
| share of returning teams that win their division | 0.163 | 0.100 to 0.300 | yes | 0.147 to 0.178 |
| share of returning teams that finish 5th again | 0.225 | 0.100 to 0.300 | yes | 0.203 to 0.244 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.41 | -0.50 to 0.50 | yes | 0.15 to 0.77 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.084 | 0.000 to 0.100 | yes | 0.076 to 0.091 |

All trends inside the bands.

## drives engine, 3 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.144 | 0.130 to 0.190 | yes | 0.143 to 0.147 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.158 | 0.100 to 0.500 | yes | 0.147 to 0.172 |
| share of games decided by 8 points or fewer | 0.522 | 0.350 to 0.550 | yes | 0.520 to 0.523 |
| share of seasons in which the champion is the previous champion | 0.094 | 0.000 to 0.120 | yes | 0.026 to 0.154 |
| most titles one team wins in any 20-season stretch, averaged over leagues (the luckiest of 40 equal teams gets 2-3; a 14-team playoff field gives 3-5) | 3.67 | 0.00 to 4.00 | yes | 3.00 to 5.00 |
| most titles one team wins in any 20 seasons in the single worst league (6 or more is a dynasty) | 5 | 0 to 5 | yes | 3 to 5 |
| how often the strongest team on paper wins the title | 0.142 | 0.080 to 0.250 | yes | 0.050 to 0.225 |
| average division finish of a team back from exile (3.0 = league average) | 3.11 | 2.80 to 3.40 | yes | 3.05 to 3.19 |
| share of returning teams that win their division | 0.188 | 0.100 to 0.300 | yes | 0.175 to 0.203 |
| share of returning teams that finish 5th again | 0.229 | 0.100 to 0.300 | yes | 0.209 to 0.253 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.25 | -0.50 to 0.50 | yes | -0.04 to 0.48 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.081 | 0.000 to 0.100 | yes | 0.074 to 0.084 |

All trends inside the bands.
