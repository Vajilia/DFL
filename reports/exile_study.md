# Does exile pay? Placeholder-model study

*40 simulated leagues x 30 seasons for each of 60 settings. Every number is a difference: **team that finished 5th (and was exiled) minus team that finished 4th**, comparing teams of similar strength. Positive means exile left the team better off.*

**Read this first.** Draft value and cap relief are placeholder guesses, so this report shows how the answer changes as those guesses change. It cannot say whether your final design is right. Owner recall, revenue and fan capital are not simulated yet, so the real cost of exile is larger than anything shown here.

## With the current placeholder settings

Lottery for teams that just finished 5th. A pick-1 draft pick is worth +1.0 points of team strength; coming back from exile is worth +0.5 points. These settings were calibrated so a returning team averages roughly 3rd-to-4th in its division (exile as help, not punishment; see exile_calibration.md).

| Measure (exiled minus 4th place) | Difference | 95% range |
| --- | --- | --- |
| Team strength two seasons later (points) | +0.66 | +0.57 to +0.76 |
| Regular-season wins over the next 4 seasons | -5.73 | -6.04 to -5.50 |
| Playoff appearances over the next 4 seasons | -0.09 | -0.13 to -0.07 |
| Championships over the next 4 seasons | -0.01 | -0.01 to -0.00 |
| Chance of being exiled again within 4 seasons | +0.007 | -0.008 to +0.026 |
| Seasons actually played out of the next 4 | -0.77 | -0.79 to -0.75 |

## How the answer changes with the placeholder guesses

## Lottery for the 8 teams that just finished 5th

### Playoff appearances over the next 4 seasons (exiled minus 4th)

Rows: how much a pick-1 draft pick is worth. Columns: how much cap relief is worth on return.

| pick-1 value \ cap relief | +0.0 | +0.5 | +1.0 | +2.0 | +3.0 |
| --- | --- | --- | --- | --- | --- |
| +0.0 | -0.18 * | -0.12 * | -0.03 * | +0.07 * | +0.18 * |
| +1.0 | -0.15 * | -0.09 * | +0.01 | +0.13 * | +0.23 * |
| +2.0 | -0.11 * | -0.04 * | +0.01 | +0.15 * | +0.28 * |
| +3.0 | -0.09 * | -0.02 | +0.03 | +0.18 * | +0.30 * |
| +4.5 | +0.02 | +0.09 * | +0.15 * | +0.26 * | +0.36 * |
| +6.0 | +0.09 * | +0.13 * | +0.17 * | +0.29 * | +0.41 * |

`*` = clearly different from zero (95% range excludes zero).

### Team strength two seasons later, in points (exiled minus 4th)

Rows: how much a pick-1 draft pick is worth. Columns: how much cap relief is worth on return.

| pick-1 value \ cap relief | +0.0 | +0.5 | +1.0 | +2.0 | +3.0 |
| --- | --- | --- | --- | --- | --- |
| +0.0 | -0.01 | +0.51 * | +1.05 * | +2.03 * | +2.96 * |
| +1.0 | +0.28 * | +0.66 * | +1.24 * | +2.23 * | +3.21 * |
| +2.0 | +0.59 * | +1.05 * | +1.47 * | +2.51 * | +3.40 * |
| +3.0 | +0.84 * | +1.23 * | +1.74 * | +2.73 * | +3.68 * |
| +4.5 | +1.32 * | +1.86 * | +2.22 * | +3.15 * | +4.04 * |
| +6.0 | +1.68 * | +2.20 * | +2.58 * | +3.45 * | +4.43 * |

`*` = clearly different from zero (95% range excludes zero).

### Chance of being exiled again within 4 seasons (exiled minus 4th)

Rows: how much a pick-1 draft pick is worth. Columns: how much cap relief is worth on return.

| pick-1 value \ cap relief | +0.0 | +0.5 | +1.0 | +2.0 | +3.0 |
| --- | --- | --- | --- | --- | --- |
| +0.0 | +0.030 * | +0.022 * | -0.020 * | -0.055 * | -0.100 * |
| +1.0 | +0.007 | +0.007 | -0.030 * | -0.082 * | -0.112 * |
| +2.0 | +0.012 | -0.013 | -0.034 * | -0.086 * | -0.127 * |
| +3.0 | -0.020 * | -0.037 * | -0.060 * | -0.110 * | -0.138 * |
| +4.5 | -0.043 * | -0.082 * | -0.090 * | -0.125 * | -0.166 * |
| +6.0 | -0.072 * | -0.085 * | -0.093 * | -0.143 * | -0.180 * |

`*` = clearly different from zero (95% range excludes zero).

## Lottery for the 8 teams that just served their exile year

### Playoff appearances over the next 4 seasons (exiled minus 4th)

Rows: how much a pick-1 draft pick is worth. Columns: how much cap relief is worth on return.

| pick-1 value \ cap relief | +0.0 | +0.5 | +1.0 | +2.0 | +3.0 |
| --- | --- | --- | --- | --- | --- |
| +0.0 | -0.19 * | -0.11 * | -0.03 * | +0.05 * | +0.17 * |
| +1.0 | -0.15 * | -0.09 * | +0.01 | +0.14 * | +0.31 * |
| +2.0 | -0.03 | +0.02 | +0.11 * | +0.25 * | +0.35 * |
| +3.0 | +0.07 * | +0.10 * | +0.19 * | +0.31 * | +0.40 * |
| +4.5 | +0.20 * | +0.25 * | +0.31 * | +0.42 * | +0.50 * |
| +6.0 | +0.32 * | +0.39 * | +0.40 * | +0.48 * | +0.57 * |

`*` = clearly different from zero (95% range excludes zero).

### Team strength two seasons later, in points (exiled minus 4th)

Rows: how much a pick-1 draft pick is worth. Columns: how much cap relief is worth on return.

| pick-1 value \ cap relief | +0.0 | +0.5 | +1.0 | +2.0 | +3.0 |
| --- | --- | --- | --- | --- | --- |
| +0.0 | +0.01 | +0.51 * | +1.04 * | +1.97 * | +2.95 * |
| +1.0 | +0.63 * | +1.04 * | +1.64 * | +2.60 * | +3.74 * |
| +2.0 | +1.34 * | +1.84 * | +2.26 * | +3.41 * | +4.26 * |
| +3.0 | +2.02 * | +2.41 * | +2.92 * | +3.91 * | +4.94 * |
| +4.5 | +3.03 * | +3.48 * | +4.06 * | +4.89 * | +5.98 * |
| +6.0 | +3.99 * | +4.46 * | +4.91 * | +5.86 * | +6.83 * |

`*` = clearly different from zero (95% range excludes zero).

### Chance of being exiled again within 4 seasons (exiled minus 4th)

Rows: how much a pick-1 draft pick is worth. Columns: how much cap relief is worth on return.

| pick-1 value \ cap relief | +0.0 | +0.5 | +1.0 | +2.0 | +3.0 |
| --- | --- | --- | --- | --- | --- |
| +0.0 | +0.047 * | +0.021 * | -0.020 * | -0.062 * | -0.078 * |
| +1.0 | +0.006 | -0.000 | -0.044 * | -0.080 * | -0.134 * |
| +2.0 | -0.030 * | -0.055 * | -0.073 * | -0.136 * | -0.167 * |
| +3.0 | -0.076 * | -0.077 * | -0.100 * | -0.148 * | -0.180 * |
| +4.5 | -0.097 * | -0.127 * | -0.153 * | -0.168 * | -0.230 * |
| +6.0 | -0.153 * | -0.177 * | -0.176 * | -0.189 * | -0.223 * |

`*` = clearly different from zero (95% range excludes zero).

## What this means

- **Scale.** One point of team strength is worth about 0.5 wins over an 18-game season, so a pick-1 value of 3 points is about 1.6 extra wins a year.
- **With today's placeholder settings**, a team that finishes 5th comes out behind against one that finishes 4th on playoff appearances over four seasons (-0.09, range -0.13 to -0.07), even though it sits out a whole season. It returns 0.7 points stronger and is 1 percentage point more likely to be exiled again.
- **With both benefits at zero**, exile costs 0.18 playoff appearances per four seasons. That is the true price of the lost season on the field.
- **Break-even (lottery for teams that just finished 5th).** Exile matches finishing 4th on playoff appearances when cap relief +0.0: pick-1 worth about 4.3; cap relief +0.5: pick-1 worth about 3.3; cap relief +1.0: pick-1 worth about 0.8; cap relief +2.0: none needed; cap relief +3.0: none needed.
- **Break-even (lottery for teams that just served exile).** Exile matches finishing 4th on playoff appearances when cap relief +0.0: pick-1 worth about 2.3; cap relief +0.5: pick-1 worth about 1.8; cap relief +1.0: pick-1 worth about 0.7; cap relief +2.0: none needed; cap relief +3.0: none needed.
- **The dial that matters** is how big the draft and cap-relief benefits are compared with the cost of a lost season. Nothing here says which setting is right; it shows where the line is.
- **Not modelled yet:** owner recall, lost revenue and fan capital, and what characters choose to do. Those are the real costs of exile and they only appear once the character cards exist.

