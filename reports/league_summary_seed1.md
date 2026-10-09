# DFL trial run: 20 seasons (seed 1)

This is the league running by itself with **no characters and no AI**. Game scores come from placeholder ratings (see `engine/placeholder_model.py`), so team names are placeholders and results show how the *machinery* behaves, not what the real league will feel like. Every season's schedule passed the full rule check.

## Champions

| Year | Champion | Record | Conference | Went into the year as |
| --- | --- | --- | --- | --- |
| 1 | Team 31 | 12-6 | Eastern | Tier 1 |
| 2 | Team 37 | 10-8 | Eastern | Tier 1 |
| 3 | Team 23 | 14-4 | Western | Tier 3 |
| 4 | Team 47 | 12-6 | Eastern | Tier 1 |
| 5 | Team 37 | 11-7 | Eastern | Tier 3 |
| 6 | Team 03 | 14-4 | Western | Tier 1 |
| 7 | Team 47 | 13-5 | Eastern | Tier 1 |
| 8 | Team 37 | 12-6 | Eastern | Tier 5 |
| 9 | Team 16 | 12-6 | Western | Tier 2 |
| 10 | Team 43 | 15-3 | Eastern | Tier 5 |
| 11 | Team 14 | 14-4 | Western | Tier 2 |
| 12 | Team 42 | 13-5 | Eastern | Tier 4 |
| 13 | Team 13 | 13-5 | Western | Tier 4 |
| 14 | Team 39 | 15-3 | Eastern | Tier 1 |
| 15 | Team 47 | 11-7 | Eastern | Tier 5 |
| 16 | Team 12 | 12-6 | Western | Tier 2 |
| 17 | Team 04 | 16-2 | Western | Tier 2 |
| 18 | Team 19 | 13-5 | Western | Tier 4 |
| 19 | Team 34 | 13-5 | Eastern | Tier 2 |
| 20 | Team 19 | 11-7 | Western | Tier 1 |

15 different teams won the title in 20 seasons. Most titles: Team 37 (3), Team 47 (3), Team 19 (2).

Back-to-back champions: 0.

## How even is the league?

The best regular-season record each year averaged 14.1-3.9 (range 12 to 16 wins). The worst averaged 3.3-14.7 (range 1 to 4 wins).

The gap between strong and weak teams (standard deviation of the placeholder ratings) stayed between 2.8 and 4.3 points, so the league neither collapsed into a few powers nor went completely flat.

## Exile

Eight teams are exiled every year, one per division. Across 20 years that is 160 exiles. Most exiles for one team: Team 09 (5), Team 22 (5), Team 33 (5). Every one of the 48 teams was exiled at least once.

After an exile, a team came back as Tier 5. 55 of 136 (40%) were exiled again within two seasons of coming back.

| Year | Exiled for the next season |
| --- | --- |
| 1 | 5, 9, 14, 22, 25, 33, 41, 45 |
| 2 | 6, 12, 16, 24, 29, 32, 40, 48 |
| 3 | 5, 9, 14, 20, 28, 35, 42, 43 |
| 4 | 4, 7, 16, 19, 29, 32, 38, 45 |
| 5 | 5, 12, 13, 22, 25, 31, 40, 43 |
| 6 | 4, 9, 15, 23, 27, 36, 37, 45 |
| 7 | 1, 12, 13, 19, 28, 31, 38, 44 |
| 8 | 4, 7, 18, 21, 25, 34, 41, 43 |
| 9 | 2, 8, 17, 22, 28, 33, 38, 45 |
| 10 | 4, 9, 18, 23, 30, 34, 40, 44 |
| 11 | 3, 10, 17, 21, 29, 36, 41, 48 |
| 12 | 1, 11, 14, 24, 30, 34, 38, 44 |
| 13 | 3, 10, 17, 20, 27, 31, 37, 47 |
| 14 | 2, 9, 16, 23, 29, 33, 40, 45 |
| 15 | 3, 10, 15, 22, 26, 34, 37, 43 |
| 16 | 1, 8, 16, 24, 28, 35, 41, 48 |
| 17 | 3, 11, 13, 23, 30, 33, 39, 44 |
| 18 | 6, 7, 17, 22, 28, 32, 38, 46 |
| 19 | 2, 12, 14, 23, 27, 35, 42, 48 |
| 20 | 4, 10, 18, 20, 29, 33, 39, 46 |

## Ties for 5th place (which now means exile)

The exile spot needed a tiebreaker in 37 of 160 division-seasons (23%). What finally settled it: head-to-head record (15), division record (13), point differential (9). The tiebreaker order is an assumption, so this tells you how often it will matter.

## The lottery

The lottery covers the 8 teams that just finished 5th, with weights 18 / 16 / 15 / 13 / 12 / 10 / 9 / 7 (placeholder). 
The worst-record team won pick 1 in 4 of 20 years; the best-record team of the eight won it 3 times. Average pick by record, worst to best: 4.3, 3.6, 3.9, 4.1, 4.2, 5.0, 5.7, 5.2 in this run, and 3.7, 3.9, 4.1, 4.3, 4.5, 4.9, 5.1, 5.5 expected over many lotteries. With these weights the worst team's edge over the best is only about two picks on average.

## CEO recall workload (for the AI budget)

Each year one division's CEOs come up for a vote (6 teams), and each exiled team's CEO also faces one. That is exactly 13 CEO votes a year. At 5 replacement candidates per vote that is at most about 65 generated CEO cards a year, if every recall succeeds.

## Does a team's tier predict how it does?

Over 40 separate leagues of 25 seasons each (1,000 seasons), by the tier a team started the year in. Tier 5 is where exiled teams return.

**With the placeholder exile benefits** (top-8 lottery pick plus cap relief):

| Tier | Average wins | Made the playoffs | Won the title |
| --- | --- | --- | --- |
| 1 | 9.6 | 44% | 4.1% |
| 2 | 9.1 | 36% | 2.8% |
| 3 | 8.9 | 33% | 2.1% |
| 4 | 8.7 | 30% | 1.8% |
| 5 | 8.7 | 31% | 1.7% |

**With the exile benefits switched off** (no draft value for anyone, no cap relief). What remains is the easier Tier 5 schedule and the fact that the weakest teams get exiled:

| Tier | Average wins | Made the playoffs | Won the title |
| --- | --- | --- | --- |
| 1 | 9.7 | 45% | 4.9% |
| 2 | 9.2 | 38% | 3.0% |
| 3 | 9.0 | 35% | 2.0% |
| 4 | 8.7 | 29% | 1.4% |
| 5 | 8.4 | 27% | 1.2% |

A league built as the rules text describes ("the 1s battle the 1s, the 5s fight to avoid the bottom") would show Tier 1 clearly ahead and Tier 5 clearly behind. Anything else means exile is working as a reward or a reset rather than a punishment. How steep the slope is depends on placeholder numbers, so treat it as a dial to tune later.

## What this run can and cannot tell you

It shows the rules interlock: the right 8 teams are exiled, return as Tier 5, draft in the right order and so on. It cannot say whether games feel right, because scores here are simple ratings plus noise. Nothing here involves characters, money or the Archive yet.

