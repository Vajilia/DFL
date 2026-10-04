# Fair competitiveness report

Standard (Jeph, 2026-10-04): a trend is a problem when it falls outside the expected / accepted range of "fair competitiveness". The numeric ranges below are the AI's first proposal and are **assumed** until you set your own (`FAIR_COMPETITION_BANDS` in `engine/rules.py`). Each league runs 48 seasons; the first 8 are thrown away while the league settles. Values are averaged over the leagues; the last column shows the spread.

## fast engine, 8 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.149 | 0.130 to 0.190 | yes | 0.146 to 0.153 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.202 | 0.100 to 0.500 | yes | 0.177 to 0.229 |
| share of games decided by 8 points or fewer | 0.479 | 0.350 to 0.550 | yes | 0.473 to 0.484 |
| share of seasons in which the champion is the previous champion | 0.067 | 0.000 to 0.120 | yes | 0.026 to 0.103 |
| most titles one team wins in any 20-season stretch (the luckiest of 40 equal teams gets 2-3, a 14-team field gives 3-5; 5 or more is a dynasty) | 4 | 0 to 4 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.219 | 0.080 to 0.250 | yes | 0.150 to 0.275 |
| average division finish of a team back from exile (3.0 = league average) | 3.01 | 2.80 to 3.40 | yes | 2.94 to 3.09 |
| share of returning teams that win their division | 0.206 | 0.100 to 0.300 | yes | 0.169 to 0.244 |
| share of returning teams that finish 5th again | 0.198 | 0.100 to 0.300 | yes | 0.184 to 0.237 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.081 | 0.000 to 0.100 | yes | 0.072 to 0.092 |

All trends inside the bands.

## drives engine, 3 leagues x 48 seasons

| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |
| --- | --- | --- | --- | --- |
| spread of regular-season win percentage across teams (pure luck alone is about 0.12) | 0.145 | 0.130 to 0.190 | yes | 0.144 to 0.147 |
| how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed) | 0.159 | 0.100 to 0.500 | yes | 0.154 to 0.163 |
| share of games decided by 8 points or fewer | 0.513 | 0.350 to 0.550 | yes | 0.504 to 0.518 |
| share of seasons in which the champion is the previous champion | 0.068 | 0.000 to 0.120 | yes | 0.026 to 0.103 |
| most titles one team wins in any 20-season stretch (the luckiest of 40 equal teams gets 2-3, a 14-team field gives 3-5; 5 or more is a dynasty) | 4 | 0 to 4 | yes | 2 to 4 |
| how often the strongest team on paper wins the title | 0.242 | 0.080 to 0.250 | yes | 0.200 to 0.300 |
| average division finish of a team back from exile (3.0 = league average) | 3.11 | 2.80 to 3.40 | yes | 3.07 to 3.14 |
| share of returning teams that win their division | 0.170 | 0.100 to 0.300 | yes | 0.163 to 0.178 |
| share of returning teams that finish 5th again | 0.227 | 0.100 to 0.300 | yes | 0.219 to 0.244 |
| share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped) | 0.076 | 0.000 to 0.100 | yes | 0.072 to 0.082 |

All trends inside the bands.
