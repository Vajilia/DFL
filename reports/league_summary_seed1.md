# DFL trial run: 20 seasons (seed 1)

This is the league running by itself with **no characters and no AI**. Game scores come from placeholder ratings (see `engine/placeholder_model.py`), so team names are placeholders and results show how the *machinery* behaves, not what the real league will feel like. Every season's schedule passed the full rule check.

## Champions

| Year | Champion | Record | Conference | Went into the year as |
| --- | --- | --- | --- | --- |
| 1 | Team 31 | 12-6 | Eastern | Tier 1 |
| 2 | Team 01 | 13-5 | Western | Tier 3 |
| 3 | Team 34 | 12-6 | Eastern | Tier 3 |
| 4 | Team 01 | 12-6 | Western | Tier 1 |
| 5 | Team 41 | 14-4 | Eastern | Tier 1 |
| 6 | Team 05 | 12-6 | Western | Tier 5 |
| 7 | Team 24 | 11-7 | Western | Tier 1 |
| 8 | Team 12 | 10-8 | Western | Tier 2 |
| 9 | Team 35 | 11-7 | Eastern | Tier 1 |
| 10 | Team 20 | 11-7 | Western | Tier 4 |
| 11 | Team 48 | 11-7 | Eastern | Tier 1 |
| 12 | Team 31 | 15-3 | Eastern | Tier 5 |
| 13 | Team 10 | 12-6 | Western | Tier 1 |
| 14 | Team 17 | 11-7 | Western | Tier 5 |
| 15 | Team 34 | 11-7 | Eastern | Tier 1 |
| 16 | Team 03 | 12-6 | Western | Tier 5 |
| 17 | Team 30 | 11-7 | Eastern | Tier 5 |
| 18 | Team 23 | 11-7 | Western | Tier 2 |
| 19 | Team 04 | 12-6 | Western | Tier 5 |
| 20 | Team 04 | 12-6 | Western | Tier 1 |

16 different teams won the title in 20 seasons. Most titles: Team 31 (2), Team 01 (2), Team 34 (2).

Back-to-back champions: 1.

## How even is the league?

The best regular-season record each year averaged 14.5-3.5 (range 12 to 17 wins). The worst averaged 3.6-14.4 (range 2 to 5 wins).

The gap between strong and weak teams (standard deviation of the placeholder ratings) stayed between 2.4 and 4.0 points, so the league neither collapsed into a few powers nor went completely flat.

## Exile

Eight teams are exiled every year, one per division. Across 20 years that is 160 exiles. Most exiles for one team: Team 32 (6), Team 05 (5), Team 09 (5). Every one of the 48 teams was exiled at least once.

After an exile, a team came back as Tier 5. 46 of 136 (34%) were exiled again within two seasons of coming back.

| Year | Exiled for the next season |
| --- | --- |
| 1 | 5, 9, 14, 22, 25, 33, 41, 45 |
| 2 | 6, 12, 16, 20, 29, 32, 42, 48 |
| 3 | 2, 11, 14, 23, 27, 33, 38, 43 |
| 4 | 5, 7, 16, 24, 26, 35, 42, 48 |
| 5 | 2, 11, 15, 21, 25, 31, 40, 45 |
| 6 | 3, 10, 18, 20, 26, 32, 38, 46 |
| 7 | 4, 7, 13, 22, 28, 34, 37, 44 |
| 8 | 6, 10, 18, 24, 27, 33, 39, 45 |
| 9 | 3, 9, 16, 22, 26, 32, 41, 43 |
| 10 | 2, 11, 18, 21, 27, 31, 39, 46 |
| 11 | 3, 9, 15, 24, 30, 32, 40, 44 |
| 12 | 2, 8, 17, 20, 28, 34, 38, 43 |
| 13 | 5, 7, 15, 23, 29, 33, 40, 47 |
| 14 | 3, 10, 18, 22, 28, 32, 39, 45 |
| 15 | 1, 12, 13, 23, 30, 31, 42, 46 |
| 16 | 5, 11, 14, 21, 28, 33, 41, 47 |
| 17 | 4, 8, 18, 22, 25, 32, 38, 46 |
| 18 | 2, 9, 13, 20, 27, 34, 39, 47 |
| 19 | 6, 10, 16, 19, 25, 36, 41, 46 |
| 20 | 5, 9, 17, 24, 27, 35, 39, 47 |

## Ties for 5th place (which now means exile)

The exile spot needed a tiebreaker in 24 of 160 division-seasons (15%). What finally settled it: head-to-head record (14), division record (8), point differential (2). The tiebreaker order is an assumption, so this tells you how often it will matter.

## The lottery

The lottery covers the 8 teams that just finished 5th, with weights 18 / 16 / 15 / 13 / 12 / 10 / 9 / 7 (placeholder). 
The worst-record team won pick 1 in 5 of 20 years; the best-record team of the eight won it 4 times. Average pick by record, worst to best: 3.0, 3.4, 4.5, 5.2, 4.2, 5.0, 5.7, 5.0 in this run, and 3.7, 3.9, 4.1, 4.3, 4.5, 4.9, 5.1, 5.5 expected over many lotteries. With these weights the worst team's edge over the best is only about two picks on average.

## Owner recall workload (for the AI budget)

Each year one division's owners come up for a vote (6 teams), and each exiled team's owner also faces one. That is exactly 13 owner votes a year. At 5 replacement candidates per vote that is at most about 65 generated owner cards a year, if every recall succeeds.

## Does a team's tier predict how it does?

Over 40 separate leagues of 25 seasons each (1,000 seasons), by the tier a team started the year in. Tier 5 is where exiled teams return.

**With the placeholder exile benefits** (top-8 lottery pick plus cap relief):

| Tier | Average wins | Made the playoffs | Won the title |
| --- | --- | --- | --- |
| 1 | 9.4 | 41% | 3.3% |
| 2 | 9.0 | 35% | 2.4% |
| 3 | 8.8 | 32% | 2.0% |
| 4 | 8.6 | 28% | 1.7% |
| 5 | 9.2 | 39% | 3.0% |

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

