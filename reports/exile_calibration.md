# Calibrating exile to the design intent

**Design intent (the Commissioner):** exile is relief, not punishment. A team coming back should have the potential to compete for **3rd place in its division**. Sometimes it gets there, sometimes it doesn't. Not a lock to contend, not a lock to flop.

**Target used:** average first-season-back division finish close to 3.0 (between 2.8 and 3.2), with every finish from 1st to 5th still possible. For reference, a team picked at random finishes 3.0 on average and gets exiled 20% of the time.

All numbers below use the placeholder draft-value and cap-relief settings (`engine/placeholder_model.py`). They are tuning dials, not rules. Each cell is the average first-season-back division finish (1 = division winner, 5 = exiled again).

## Lottery for the 8 teams that just finished 5th

| pick-1 value \ cap relief | +0.0 | +0.5 | +1.0 | +1.5 | +2.0 | +3.0 |
| --- | --- | --- | --- | --- | --- | --- |
| +0.0 | 3.36 | 3.21 | **3.16** | **3.09** | **3.02** | **2.86** |
| +1.0 | 3.24 | **3.16** | **3.06** | **2.98** | **2.93** | **2.81** |
| +2.0 | **3.13** | **3.03** | **3.00** | **2.91** | **2.83** | 2.73 |
| +3.0 | **3.07** | **2.95** | **2.88** | **2.83** | 2.76 | 2.65 |
| +4.0 | **2.93** | **2.89** | **2.82** | 2.74 | 2.67 | 2.56 |
| +5.0 | **2.89** | **2.82** | 2.73 | 2.68 | 2.60 | 2.47 |
| +6.0 | **2.81** | 2.72 | 2.69 | 2.59 | 2.54 | 2.45 |

Bold = inside the 2.8 to 3.2 target.

## Lottery for the 8 teams that just served their exile year

| pick-1 value \ cap relief | +0.0 | +0.5 | +1.0 | +1.5 | +2.0 | +3.0 |
| --- | --- | --- | --- | --- | --- | --- |
| +0.0 | 3.34 | 3.22 | **3.15** | **3.07** | **3.03** | **2.88** |
| +1.0 | **3.18** | **3.13** | **3.02** | **2.96** | **2.89** | 2.75 |
| +2.0 | **3.06** | **2.99** | **2.91** | **2.82** | 2.77 | 2.65 |
| +3.0 | **2.92** | **2.83** | 2.79 | 2.71 | 2.63 | 2.54 |
| +4.0 | **2.82** | 2.76 | 2.67 | 2.62 | 2.55 | 2.45 |
| +5.0 | 2.70 | 2.64 | 2.59 | 2.51 | 2.47 | 2.38 |
| +6.0 | 2.62 | 2.54 | 2.50 | 2.42 | 2.39 | 2.26 |

Bold = inside the 2.8 to 3.2 target.

## Where the target is met (lottery for teams that just finished 5th)

| pick-1 value | cap relief | Average finish | 1st | 2nd | 3rd | 4th | 5th (exiled again) | Made playoffs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| +2.0 | +1.0 | 3.00 | 20% | 20% | 19% | 20% | 20% | 35% |
| +1.0 | +1.5 | 2.98 | 20% | 20% | 20% | 20% | 20% | 36% |
| +0.0 | +2.0 | 3.02 | 20% | 19% | 20% | 20% | 21% | 35% |
| +2.0 | +0.5 | 3.03 | 20% | 20% | 20% | 20% | 21% | 34% |
| +3.0 | +0.5 | 2.95 | 22% | 19% | 20% | 19% | 19% | 37% |
| +1.0 | +1.0 | 3.06 | 19% | 19% | 19% | 21% | 21% | 34% |

## Where the target is met (lottery for teams that just served exile)

| pick-1 value | cap relief | Average finish | 1st | 2nd | 3rd | 4th | 5th (exiled again) | Made playoffs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| +2.0 | +0.5 | 2.99 | 21% | 19% | 20% | 20% | 20% | 35% |
| +1.0 | +1.0 | 3.02 | 20% | 21% | 19% | 20% | 20% | 35% |
| +0.0 | +2.0 | 3.03 | 20% | 19% | 20% | 20% | 21% | 35% |
| +1.0 | +1.5 | 2.96 | 22% | 19% | 20% | 20% | 20% | 37% |
| +2.0 | +0.0 | 3.06 | 19% | 19% | 20% | 20% | 22% | 33% |
| +0.0 | +1.5 | 3.07 | 19% | 19% | 20% | 21% | 22% | 33% |

## Settings now in use

The placeholder model currently uses a pick-1 value of +1.0 and cap relief of +0.5. A returning team then averages a 3.16 finish in its division: 1st 17%, 2nd 18%, 3rd 19%, 4th 22%, 5th 24%. It finishes 3rd or better 55% of the time and makes the playoffs 31% of the time. That is a team with a real chance at 3rd or better but no guarantee, which is how I read the design intent. Say "a bit more help" or "a bit less" and I will move the dials.

## Reading this

Many combinations hit the same target, because draft value and cap relief both just add talent. The choice between them is a story choice, not a math one: put the help in the lottery pick, in cap relief, or split it. The simulation only needs the total help to be about right.

