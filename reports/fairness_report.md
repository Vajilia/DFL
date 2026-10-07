# Fair competitiveness report

Corrected Step 6b study: earned-service pay and practice-squad integration, including the CBA IR salary-credit exclusion. Model dials and fairness limits are unchanged.

Standard (the Commissioner, 2026-10-04): a trend is a problem when it falls outside the expected / accepted range of "fair competitiveness". The numeric ranges below were proposed by the AI and are accepted by the Commissioner as the working limits (`FAIR_COMPETITION_BANDS` in `engine/rules.py`; the rulebook's "fair" basis). Each league runs 48 seasons; the first 8 are thrown away while the league settles. Values are averaged over the leagues; the last column shows the spread.

## fast engine, 12 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.143 | 0.130 to 0.190 | yes | 0.140 to 0.149 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.143 | 0.100 to 0.500 | yes | 0.091 to 0.181 |
| share of games decided by 8 points or fewer | 0.489 | 0.350 to 0.550 | yes | 0.478 to 0.495 |
| share of seasons in which the champion is the previous champion | 0.045 | 0.000 to 0.120 | yes | 0.026 to 0.128 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 2.92 | 0.00 to 4.70 | yes | 2.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.185 | 0.080 to 0.250 | yes | 0.075 to 0.300 |
| average division finish of a team back from exile (3.0 = league average) | 3.09 | 2.80 to 3.40 | yes | 2.96 to 3.17 |
| share of returning teams that win their division | 0.192 | 0.100 to 0.300 | yes | 0.163 to 0.222 |
| share of returning teams that finish 5th again | 0.226 | 0.100 to 0.300 | yes | 0.197 to 0.244 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.27 | -0.50 to 0.50 | yes | -0.09 to 0.90 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.080 | 0.000 to 0.100 | yes | 0.075 to 0.088 |

All trends inside the bands.

## drives engine, 6 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.140 | 0.130 to 0.190 | yes | 0.138 to 0.142 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.130 | 0.100 to 0.500 | yes | 0.089 to 0.158 |
| share of games decided by 8 points or fewer | 0.523 | 0.350 to 0.550 | yes | 0.518 to 0.527 |
| share of seasons in which the champion is the previous champion | 0.047 | 0.000 to 0.120 | yes | 0.000 to 0.077 |
| most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14 | 3.50 | 0.00 to 4.70 | yes | 3.00 to 4.00 |
| most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty) | 4 | 0 to 7 | yes | 3 to 4 |
| how often the strongest team on paper wins the title | 0.192 | 0.080 to 0.250 | yes | 0.150 to 0.250 |
| average division finish of a team back from exile (3.0 = league average) | 3.12 | 2.80 to 3.40 | yes | 3.05 to 3.17 |
| share of returning teams that win their division | 0.186 | 0.100 to 0.300 | yes | 0.150 to 0.222 |
| share of returning teams that finish 5th again | 0.231 | 0.100 to 0.300 | yes | 0.200 to 0.259 |
| extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th | 0.33 | -0.50 to 0.50 | yes | -0.09 to 0.68 |
| share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft | 0.000 | 0.000 to 0.100 | yes | 0.000 to 0.000 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.081 | 0.000 to 0.100 | yes | 0.072 to 0.090 |

All trends inside the bands.
