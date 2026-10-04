# Character cards: samples

Seed 1, after 14 seasons. Names, hometowns and backgrounds come from placeholder word lists (engine/card_pools.py) that you can replace. Ratings, archetypes and the coach effect are real: they come from the engine. Relationships and the decision log start empty on purpose; the Interaction system will fill them.

## How to read a card

- **Soul (archetypes)** is fixed for life. It is read from the rating profile she is born with: her best attribute names the positive archetype and her weakest the negative one. Her development is bent to stay true to it.
- **Personality** is how her soul shows up. Her archetype allows four personalities; which one she shows depends on her temperament and on how she rates herself. Her self-image lags the truth, so a declining veteran overrates herself and a rising rookie undersells herself. When her confidence moves enough, her personality can shift, but only inside the four her soul allows.
- **Pressure thresholds** (exile, contract, spotlight, loyalty) are how much each kind of pressure rattles her, 1 to 100. They do nothing yet; the Interaction system will use them.
- **Fanbases and outlets**: a fanbase has a culture (its personality), five ratings and two stores: approval of the owner and Fan Capital (goodwill built by sustained success, which only ever buffers a recall). Its expectations drift with what the team delivers, inside a bound set at birth. An outlet has a voice, five ratings and Credibility, which rises when its forecasts come true and falls when they miss; one that stays irrelevant folds and is replaced. The press can move an owner's approval by at most 3 points a year.
- **Coach ratings**: offense and defense lift the team (up to +/- 1.0 point of margin each); development adds up to 0.4 rating points a year to each young player. The other three are stored for later. Legends are the rare all-time greats.

## A franchise player at each position group

### Winona Hutchins  (QB, Team 37)
```yaml
IDENTITY: [Winona Hutchins, age 25, from Accra Ghana; Came up through the academy system]
SOUL (fixed): [+ Well-Rounded, - Reads Late]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is clear-eyed (+0.00)
RATINGS: [overall 91, Franchise player]
  - accuracy: 93  (sees herself at 94)
  - arm: 92  (sees herself at 91)
  - awareness: 88  (sees herself at 87)
  - pressure thresholds: exile 31, contract 41, spotlight 65, loyalty 51
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 12 (pick 30)]
DECISION_LOG: [none yet]
```
### Eden Flanagan  (WR, Team 01)
```yaml
IDENTITY: [Eden Flanagan, age 28, from Bozeman MT; Two-sport athlete]
SOUL (fixed): [+ Burner, - Drop-Prone]  temperament family: flash
PERSONALITY: [Showman] wants the spotlight and a signature moment; fears being ignored by the media
  - allowed by her soul: Showman, Free Spirit, Competitor, Mercenary; right now she is clear-eyed (+0.11)
RATINGS: [overall 88, Franchise player]
  - route: 85  (sees herself at 83, doubting)
  - hands: 83  (sees herself at 86, overrating)
  - speed: 95  (sees herself at 97, overrating)
  - pressure thresholds: exile 32, contract 48, spotlight 51, loyalty 57
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 8 (pick 3)]
DECISION_LOG: [none yet]
```
### Grace Pappas  (OL, Team 43)
```yaml
IDENTITY: [Grace Pappas, age 28, from Helsinki Finland; Late bloomer]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is full of doubt (-0.40)
RATINGS: [overall 90, Franchise player]
  - pass_block: 90  (sees herself at 88)
  - run_block: 90  (sees herself at 85, doubting)
  - pressure thresholds: exile 43, contract 65, spotlight 62, loyalty 58
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 9 (pick 6)]
DECISION_LOG: [none yet]
```
### Mirabel Pinkerton  (DL, Team 42)
```yaml
IDENTITY: [Mirabel Pinkerton, age 26, from Laredo TX; Small-college standout]
SOUL (fixed): [+ Run Stuffer, - Little Pressure]  temperament family: power
PERSONALITY: [Grinder] wants to earn every inch; fears being handed nothing and losing it anyway
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is full of doubt (-1.00)
RATINGS: [overall 93, Franchise player]
  - pass_rush: 88  (sees herself at 73, doubting)
  - run_stop: 99  (sees herself at 86, doubting)
  - pressure thresholds: exile 38, contract 64, spotlight 58, loyalty 47
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 10 (pick 8)]
DECISION_LOG: [none yet]
```
### Alba Gallagher  (CB, Team 23)
```yaml
IDENTITY: [Alba Gallagher, age 30, from Sacramento CA; Late bloomer]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Grinder] wants to earn every inch; fears being handed nothing and losing it anyway
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is clear-eyed (-0.16)
RATINGS: [overall 89, Franchise player]
  - coverage: 88  (sees herself at 85, doubting)
  - ball_skills: 93  (sees herself at 93)
  - tackling: 89  (sees herself at 88)
  - pressure thresholds: exile 44, contract 21, spotlight 48, loyalty 43
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 6 (pick 2)]
DECISION_LOG: [none yet]
```
### Wanda Dellinger  (K, Team 30)
```yaml
IDENTITY: [Wanda Dellinger, age 32, from Duluth MN; Small-college standout]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is full of doubt (-0.73)
RATINGS: [overall 90, Franchise player]
  - power: 91  (sees herself at 84, doubting)
  - accuracy: 89  (sees herself at 85, doubting)
  - pressure thresholds: exile 54, contract 58, spotlight 20, loyalty 45
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```

## A young rookie and a veteran

### Anneke Chandler  (DL, Team 18)
```yaml
IDENTITY: [Anneke Chandler, age 23, from Helsinki Finland; Late bloomer]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is overconfident (+0.70)
RATINGS: [overall 64, Starter]
  - pass_rush: 63  (sees herself at 70, overrating)
  - run_stop: 66  (sees herself at 70, overrating)
  - pressure thresholds: exile 40, contract 79, spotlight 44, loyalty 41
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 14 (pick 1)]
DECISION_LOG: [none yet]
```
### Wanda Dellinger  (K, Team 30)
```yaml
IDENTITY: [Wanda Dellinger, age 32, from Duluth MN; Small-college standout]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is full of doubt (-0.73)
RATINGS: [overall 90, Franchise player]
  - power: 91  (sees herself at 84, doubting)
  - accuracy: 89  (sees herself at 85, doubting)
  - pressure thresholds: exile 54, contract 58, spotlight 20, loyalty 45
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```

## A player whose personality changed (her soul stayed the same)

### Eva Quillen  (DL, Team 01)
```yaml
IDENTITY: [Eva Quillen, age 29, from Richmond VA; Came up through the academy system]
SOUL (fixed): [+ Edge Terror, - Gets Washed Out]  temperament family: power
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is clear-eyed (+0.16)
RATINGS: [overall 62, Starter]
  - pass_rush: 69  (sees herself at 71)
  - run_stop: 54  (sees herself at 55)
  - pressure thresholds: exile 80, contract 56, spotlight 48, loyalty 55
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [became Grinder (was Competitor) 9; became Competitor (was Grinder) 10]
DECISION_LOG: [none yet]
```

## A retired player (cards are kept for the Archive)

### Kyra Kaplan  (QB, retired)
```yaml
IDENTITY: [Kyra Kaplan, age 34, from Charleston SC; Power-conference star]
SOUL (fixed): [+ Surgeon, - Short-Armed]  temperament family: precision
PERSONALITY: [Grinder] wants to earn every inch; fears being handed nothing and losing it anyway
  - allowed by her soul: Perfectionist, Quiet Leader, Grinder, Diplomat; right now she is clear-eyed (+0.08)
RATINGS: [overall 91, Franchise player]
  - accuracy: 96  (sees herself at 95)
  - arm: 88  (sees herself at 86)
  - awareness: 84  (sees herself at 88, overrating)
  - pressure thresholds: exile 69, contract 70, spotlight 52, loyalty 78
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [retired 10]
DECISION_LOG: [none yet]
```

## Head coaches: a legend, a typical coach and a weak one

### Coach Xiomara Aoki  (Team 21)  -  LEGEND
```yaml
IDENTITY: [Xiomara Aoki, age 66, from Winnipeg MB; Coordinator who got her first shot]
PERSONALITY: [Survivor] wants another contract year; fears the owner's phone call
ARCHETYPES: [+ Legend: Talent Developer, - Undisciplined]
RATINGS:
  - offense: 92   -> +0.83 points of margin
  - defense: 96   -> +0.92 points of margin
  - development: 99   -> +0.39 rating points per year to each young player
  - gamecraft: 88   (no on-field effect yet)
  - discipline: 81   (no on-field effect yet)
  - motivation: 85   (no on-field effect yet)
  - pressure thresholds: exile 55, contract 78, spotlight 64, loyalty 33
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [hired 0]
DECISION_LOG: [none yet]
```
### Coach Stella Landry  (Team 44)
```yaml
IDENTITY: [Stella Landry, age 56, from Miami FL; Came over from another league]
PERSONALITY: [Steady Hand] wants sustained quiet success; fears a collapse nobody saw coming
ARCHETYPES: [+ Taskmaster, - Stunts Growth]
RATINGS:
  - offense: 48   -> -0.04 points of margin
  - defense: 50   -> -0.01 points of margin
  - development: 32   -> -0.14 rating points per year to each young player
  - gamecraft: 41   (no on-field effect yet)
  - discipline: 60   (no on-field effect yet)
  - motivation: 57   (no on-field effect yet)
  - pressure thresholds: exile 47, contract 58, spotlight 45, loyalty 78
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [hired 14]
DECISION_LOG: [none yet]
```
### Coach Angela Clairmont  (Team 10)
```yaml
IDENTITY: [Angela Clairmont, age 47, from Corpus Christi TX; Rose through the assistant ranks]
PERSONALITY: [Developer] wants to turn raw talent into stars; fears wasting a prospect
ARCHETYPES: [+ Inspirer, - Leaky Defense]
RATINGS:
  - offense: 31   -> -0.38 points of margin
  - defense: 17   -> -0.66 points of margin
  - development: 52   -> +0.02 rating points per year to each young player
  - gamecraft: 43   (no on-field effect yet)
  - discipline: 39   (no on-field effect yet)
  - motivation: 56   (no on-field effect yet)
  - pressure thresholds: exile 50, contract 86, spotlight 56, loyalty 86
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [hired 10]
DECISION_LOG: [none yet]
```

## An owner, a GM, and the Archive's first entries

### Owner Sofia Atwood  (Team 01, owner)
```yaml
IDENTITY: [Sofia Atwood, age 66, from Sacramento CA; Media heiress]
PERSONALITY: [Meddler] wants a hand in every decision; fears being irrelevant
ARCHETYPES: [+ Shrewd Operator, - Absentee Owner]
RATINGS:
  - patience: 56
  - ambition: 60
  - involvement: 50
  - popularity: 58
  - business: 64
  - fan approval right now: 66%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 62, media 69, losing 51, subsidy 48
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [bought 0]
DECISION_LOG: [none yet]
```
### Owner Junie Gentry  (Team 29, recalled)
```yaml
IDENTITY: [Junie Gentry, age 65, from Compton CA; Media heiress]
PERSONALITY: [Meddler] wants a hand in every decision; fears being irrelevant
ARCHETYPES: [+ Fan Favorite, - Absentee Owner]
RATINGS:
  - patience: 55
  - ambition: 73
  - involvement: 40
  - popularity: 82
  - business: 41
  - fan approval right now: 28%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 46, media 51, losing 68, subsidy 42
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [elected 11; recalled 14]
DECISION_LOG: [none yet]
```
### GM Treasure Wagner  (Team 28, gm)
```yaml
IDENTITY: [Treasure Wagner, age 64, from Lubbock TX; Longtime scout]
PERSONALITY: [Planner] wants a five-year roster plan; fears a short-term panic
ARCHETYPES: [+ Draft Whisperer, - Gets Fleeced]
RATINGS:
  - scouting: 90   -> +1.19 rating points on her team's rookie each year
  - negotiation: 84   -> 20% fewer contract expiries
  - evaluation: 63   (no on-field effect yet)
  - trades: 12   (no on-field effect yet)
  - cap_sense: 61   (no on-field effect yet)
  - pressure thresholds: exile 63, contract 61, spotlight 46, loyalty 70
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [hired 0]
DECISION_LOG: [none yet]
```
**A recall vote as the Archive logs it:**

```
year: 14
event: recall_vote
team: 47
trigger: approval
approval: 0.299
recall_share: 0.584
result: recalled
owner: Paloma Saunders
replacement: Mabel Rochester
candidates: ['Thalia Cardenas', 'Ananya Everhart', 'Eden Iverson', 'Ivy McBride', 'Mabel Rochester']
capital: 0.414
```


## A fanbase and the press that covers it

### Fanbase of Team 08  (Entitled)
```yaml
IDENTITY: [Team 08 fans; market size 64 of 100]
PERSONALITY: [Entitled] wants a title every year; fears being ignored; picks owners who are strong on ambition
ARCHETYPES: [+ Demanding, - Indifferent]
RATINGS:
  - loyalty: 70
  - expectations: 97   (born at 82; drifts with results, within +/-15)
  - passion: 36
  - volatility: 50
  - media_trust: 43
  - approval of the owner: 53%
  - Fan Capital: 0.67  (recall immunity; worth 5.2 points on a recall vote)
  - what the press did to approval last season: +0.1 points
  - pressure thresholds: exile 40, losing 22, scandal 62, spotlight 47
RELATIONSHIPS: {}  # none yet; filled by Interactions
DECISION_LOG: [none yet]
```
### Fanbase of Team 48  (Gloomy Realists)
```yaml
IDENTITY: [Team 48 fans; market size 34 of 100]
PERSONALITY: [Gloomy Realists] wants honesty; fears being fooled again; picks owners who are strong on business
ARCHETYPES: [+ Mood Swings, - Easily Pleased]
RATINGS:
  - loyalty: 49
  - expectations: 23   (born at 38; drifts with results, within +/-15)
  - passion: 33
  - volatility: 70
  - media_trust: 44
  - approval of the owner: 46%
  - Fan Capital: 0.38  (recall immunity; worth 0.0 points on a recall vote)
  - what the press did to approval last season: -1.6 points
  - pressure thresholds: exile 59, losing 59, scandal 60, spotlight 53
RELATIONSHIPS: {}  # none yet; filled by Interactions
DECISION_LOG: [none yet]
```
### Fanbase of Team 40  (Die-Hards)
```yaml
IDENTITY: [Team 40 fans; market size 51 of 100]
PERSONALITY: [Die-Hards] wants a team that is theirs; fears a sale or a move; picks owners who are strong on popularity
ARCHETYPES: [+ Fanatical, - Distrust the Press]
RATINGS:
  - loyalty: 61
  - expectations: 61   (born at 48; drifts with results, within +/-15)
  - passion: 84
  - volatility: 62
  - media_trust: 30
  - approval of the owner: 55%
  - Fan Capital: 0.71  (recall immunity; worth 6.3 points on a recall vote)
  - what the press did to approval last season: +0.1 points
  - pressure thresholds: exile 63, losing 32, scandal 45, spotlight 67
RELATIONSHIPS: {}  # none yet; filled by Interactions
DECISION_LOG: [none yet]
```
### The Tiara Times  (national, league-wide; active)
```yaml
IDENTITY: [The Tiara Times, national outlet; byline Rosalind Stanhope]
PERSONALITY: [Watchdog] wants the story behind the story; fears being scooped
ARCHETYPES: [+ Everywhere, - Locked Out]
RATINGS:
  - accuracy: 58
  - sensationalism: 43
  - reach: 67
  - access: 41
  - independence: 63
  - Credibility: 42  (the currency: it weights this outlet's say in a team's coverage)
  - forecast record (mean miss, win%): 9: 0.14, 10: 0.12, 11: 0.12, 12: 0.11, 13: 0.11, 14: 0.14
  - pressure thresholds: spotlight 62, access 27, irrelevance 81
RELATIONSHIPS: {}  # none yet; filled by Interactions
DECISION_LOG: [none yet]
```
### The Draft Room  (national, league-wide; active)
```yaml
IDENTITY: [The Draft Room, national outlet; byline Ananya Crawley]
PERSONALITY: [Watchdog] wants the story behind the story; fears being scooped
ARCHETYPES: [+ Everywhere, - Dry as Dust]
RATINGS:
  - accuracy: 38
  - sensationalism: 34
  - reach: 63
  - access: 44
  - independence: 39
  - Credibility: 31  (the currency: it weights this outlet's say in a team's coverage)
  - forecast record (mean miss, win%): 9: 0.14, 10: 0.13, 11: 0.10, 12: 0.13, 13: 0.13, 14: 0.15
  - pressure thresholds: spotlight 59, access 43, irrelevance 45
RELATIONSHIPS: {}  # none yet; filled by Interactions
DECISION_LOG: [none yet]
```
### Team 24 Insider  (local, Team 24; active)
```yaml
IDENTITY: [Team 24 Insider, local outlet; byline Elena Merrick]
PERSONALITY: [Hype Machine] wants clicks and a roaring crowd; fears irrelevance
ARCHETYPES: [+ Headline Chaser, - Chronically Wrong]
RATINGS:
  - accuracy: 37
  - sensationalism: 81
  - reach: 55
  - access: 52
  - independence: 38
  - Credibility: 65  (the currency: it weights this outlet's say in a team's coverage)
  - forecast record (mean miss, win%): 9: 0.10, 10: 0.25, 11: 0.04, 12: 0.01, 13: 0.08, 14: 0.01
  - pressure thresholds: spotlight 37, access 48, irrelevance 41
RELATIONSHIPS: {}  # none yet; filled by Interactions
DECISION_LOG: [none yet]
```
**An outlet that folded (the Archive keeps the card):**

### Team 14 Sideline  (local, Team 14; folded)
```yaml
IDENTITY: [Team 14 Sideline, local outlet; byline Julia Ziegler]
PERSONALITY: [Hype Machine] wants clicks and a roaring crowd; fears irrelevance
ARCHETYPES: [+ Headline Chaser, - Owner's Mouthpiece]
RATINGS:
  - accuracy: 41
  - sensationalism: 72
  - reach: 50
  - access: 66
  - independence: 40
  - Credibility: 12  (the currency: it weights this outlet's say in a team's coverage)
  - forecast record (mean miss, win%): 1: 0.18, 2: 0.32, 3: 0.28, 4: 0.23
  - pressure thresholds: spotlight 36, access 68, irrelevance 49
RELATIONSHIPS: {}  # none yet; filled by Interactions
DECISION_LOG: [none yet]
```
```
year: 4
event: outlet_folded
outlet: Team 14 Sideline
kind: local
team: 14
credibility: 11.6
replacement: Team 14 Sports Desk
```


## How the cards spread across the league

**Core personalities (all rostered players):** Diplomat 507, Competitor 407, Perfectionist 372, Grinder 355, Showman 196, Quiet Leader 134, Free Spirit 132, Hothead 91, Mercenary 46, Loyalist 16

**Most common positive archetypes:** Well-Rounded 675, Pass-Pro Wall 123, Ballhawk 100, Edge Terror 90, Run Stuffer 89, Road Grader 87, Glue Hands 81, Route Technician 79

**Coach effect across the 48 teams:** average -0.13, spread (sd) 0.52, best +1.76, worst -1.04 points of expected margin. For scale, team talent has a spread of about 3 to 4 points.

**Personality shifts:** 802 of 5282 players have changed personality at least once in 14 seasons.

**Legends:** 5 of 156 coaches hired so far are legends; 1 on the field now.

**Fan cultures:** Die-Hards 13, Entitled 11, Party Crowd 9, Gloomy Realists 7, Long-Suffering 5, Front-Runners 3

**Fan Capital:** average 0.53, from 0.37 to 0.71; the most it can buffer a recall vote is 15 points.

**The press on approval, last season:** average 1.0 points either way, largest 3.8 (the cap is 3 before market size and trust).

**Outlets:** 52 active (4 national, one local beat per team); credibility averages 40, from 18 to 65; 9 have folded and been replaced in 14 seasons.

**Recall votes:** 195 in 14 seasons (13.9 a year); 61 owners recalled (4.4 a year), 31% of votes. Owners retire on their own too: 46 so far.

**Firings:** 49 coaches and 30 GMs fired in 14 seasons.

**Coaches so far:** 156 hired and 108 retired in 14 seasons.

**Players with cards:** 2345 active or unsigned, 3026 retired.
