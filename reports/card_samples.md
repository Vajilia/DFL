# Character cards: samples

Seed 1, after 40 seasons. Names, hometowns and backgrounds come from placeholder word lists (engine/card_pools.py) that you can replace. Ratings, archetypes and the coach effect are real: they come from the engine. Relationships and the decision log start empty and fill as the Interaction system plays scenes (firings, recall votes and exile determinations so far).

## How to read a card

- **Soul (archetypes)** is fixed for life. It is read from the rating profile she is born with: her best attribute names the positive archetype and her weakest the negative one. Her development is bent to stay true to it.
- **Personality** is how her soul shows up. Her archetype allows four personalities; which one she shows depends on her temperament and on how she rates herself. Her self-image lags the truth, so a declining veteran overrates herself and a rising rookie undersells herself. When her confidence moves enough, her personality can shift, but only inside the four her soul allows.
- **Pressure thresholds** (exile, contract, spotlight, loyalty) are how much each kind of pressure rattles her, 1 to 100. They do nothing yet; the Interaction system will use them.
- **Fanbases and outlets**: a fanbase has a culture (its personality), five ratings and two stores: approval of the CEO and Fan Capital (goodwill built by sustained success, which only ever buffers a recall). Its expectations drift with what the team delivers, inside a bound set at birth. It also has its own few meters (the franchise's permanent identity), fading memories and a boycott level. The press is the voice and the eyes and ears of the fans: an outlet has a voice and two ratings (reach and sensationalism), it always reports the facts accurately, a national outlet tells a team's year as it was and a local outlet frames the same year the way its own fans prefer (by a capped amount). The press can move a CEO's approval by at most 3 points a year.
- **Coach ratings**: offense and defense lift the team (up to +/- 1.0 point of margin each); development adds up to 0.4 rating points a year to each young player. The other three are stored for later. Effects are measured against the league's current average coach, so the average coach does nothing.
- **Living cards**: coaches, GMs and CEOs grow and fade over their careers (ratings move inside the shape their soul gave them), rate themselves with a lag, and can change personality inside the four traits their soul allows. People between jobs live on and can be offered to CEOs again. The TRAJECTORY line is their overall level by age.
- **Recognition**: nobody is a legend by birth. Honors (titles, All-League, Coach of the Year...) build a career esteem; the 52 outlets read it with their own noise, and a credibility-weighted share calling someone a legend makes it so (or the media splits and she is *contested*). The Hall of Fame (outlets and CEOs) votes on people who retired a few years ago. There is no cap on either.

## A franchise player at each position group

### Vesper McAllister II  (QB, Team 28)
```yaml
IDENTITY: [Vesper McAllister II, age 27, from Perth Australia; Small-college standout]
SOUL (fixed): [+ Cannon, - Wild Arm]  temperament family: power
PERSONALITY: [Grinder] wants to earn every inch; fears being handed nothing and losing it anyway
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is clear-eyed (-0.15)
RATINGS: [overall 89, Franchise player]
  - accuracy: 80  (sees herself at 78, doubting)
  - arm: 96  (sees herself at 96)
  - awareness: 95  (sees herself at 94)
  - pressure thresholds: exile 59, contract 55, spotlight 51, loyalty 80
RECOGNITION: [known; esteem 4.8; honors: All-League x2]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 35 (pick 4)]
DECISION_LOG: [none yet]
```
### Priya Ibarra II  (WR, Team 01)
```yaml
IDENTITY: [Priya Ibarra II, age 27, from Sao Paulo Brazil; Coach's daughter]
SOUL (fixed): [+ Glue Hands, - Lacks Burst]  temperament family: precision
PERSONALITY: [Perfectionist] wants flawless execution; fears the one mistake everyone remembers
  - allowed by her soul: Perfectionist, Quiet Leader, Grinder, Diplomat; right now she is full of doubt (-1.00)
RATINGS: [overall 97, Franchise player]
  - route: 98  (sees herself at 90, doubting)
  - hands: 100  (sees herself at 91, doubting)
  - speed: 93  (sees herself at 85, doubting)
  - pressure thresholds: exile 46, contract 35, spotlight 41, loyalty 49
RECOGNITION: [respected; esteem 15.1; honors: All-League x5, Player of the Year]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 35 (pick 3)]
DECISION_LOG: [none yet]
```
### Honor Cardenas II  (OL, Team 28)
```yaml
IDENTITY: [Honor Cardenas II, age 28, from Mobile AL; Walk-on turned starter]
SOUL (fixed): [+ Road Grader, - Turnstile]  temperament family: power
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is overconfident (+0.70)
RATINGS: [overall 90, Franchise player]
  - pass_block: 86  (sees herself at 91, overrating)
  - run_block: 94  (sees herself at 100, overrating)
  - pressure thresholds: exile 31, contract 78, spotlight 57, loyalty 23
RECOGNITION: [respected; esteem 9.1; honors: All-League x4]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 35 (pick 1)]
DECISION_LOG: [none yet]
```
### Willa Flanagan II  (DL, Team 26)
```yaml
IDENTITY: [Willa Flanagan II, age 26, from Montreal QC; Small-college standout]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is full of doubt (-0.54)
RATINGS: [overall 92, Franchise player]
  - pass_rush: 89  (sees herself at 86, doubting)
  - run_stop: 94  (sees herself at 89, doubting)
  - pressure thresholds: exile 46, contract 44, spotlight 52, loyalty 54
RECOGNITION: [respected; esteem 9.1; honors: All-League x4]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 36 (pick 3)]
DECISION_LOG: [none yet]
```
### Selah Alvarado  (CB, Team 06)
```yaml
IDENTITY: [Selah Alvarado, age 32, from Miami FL; Coach's daughter]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is clear-eyed (+0.13)
RATINGS: [overall 92, Franchise player]
  - coverage: 93  (sees herself at 96, overrating)
  - ball_skills: 91  (sees herself at 91)
  - tackling: 87  (sees herself at 88)
  - pressure thresholds: exile 52, contract 81, spotlight 45, loyalty 26
RECOGNITION: [star; esteem 21.6; honors: All-League x9, Player of the Year]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 30 (pick 1)]
DECISION_LOG: [none yet]
```
### Yasmin Tavares  (K, Team 05)
```yaml
IDENTITY: [Yasmin Tavares, age 36, from Juneau AK; International pathway]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is full of doubt (-1.00)
RATINGS: [overall 91, Franchise player]
  - power: 92  (sees herself at 81, doubting)
  - accuracy: 90  (sees herself at 79, doubting)
  - pressure thresholds: exile 44, contract 65, spotlight 29, loyalty 43
RECOGNITION: [known; esteem 4.8; honors: All-League x2]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```

## A young rookie and a veteran

### Tove Sandoval II  (OL, Team 14)
```yaml
IDENTITY: [Tove Sandoval II, age 22, from Nashville TN; Coach's daughter]
SOUL (fixed): [+ Road Grader, - Turnstile]  temperament family: power
PERSONALITY: [Grinder] wants to earn every inch; fears being handed nothing and losing it anyway
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is full of doubt (-0.46)
RATINGS: [overall 78, Star]
  - pass_block: 68  (sees herself at 64, doubting)
  - run_block: 88  (sees herself at 84, doubting)
  - pressure thresholds: exile 60, contract 54, spotlight 63, loyalty 68
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 40 (pick 1)]
DECISION_LOG: [none yet]
```
### Selah Alvarado  (CB, Team 06)
```yaml
IDENTITY: [Selah Alvarado, age 32, from Miami FL; Coach's daughter]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is clear-eyed (+0.13)
RATINGS: [overall 92, Franchise player]
  - coverage: 93  (sees herself at 96, overrating)
  - ball_skills: 91  (sees herself at 91)
  - tackling: 87  (sees herself at 88)
  - pressure thresholds: exile 52, contract 81, spotlight 45, loyalty 26
RECOGNITION: [star; esteem 21.6; honors: All-League x9, Player of the Year]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 30 (pick 1)]
DECISION_LOG: [none yet]
```

## A player whose personality changed (her soul stayed the same)

### Jamila Hightower  (QB, Team 02)
```yaml
IDENTITY: [Jamila Hightower, age 36, from Corpus Christi TX; Overlooked recruit]
SOUL (fixed): [+ Field General, - No Glaring Weakness]  temperament family: command
PERSONALITY: [Quiet Leader] wants her teammates' respect; fears letting the locker room down
  - allowed by her soul: Quiet Leader, Competitor, Diplomat, Perfectionist; right now she is overconfident (+0.26)
RATINGS: [overall 76, Star]
  - accuracy: 75  (sees herself at 76)
  - arm: 75  (sees herself at 77, overrating)
  - awareness: 80  (sees herself at 82, overrating)
  - pressure thresholds: exile 40, contract 33, spotlight 57, loyalty 35
RECOGNITION: [unknown; esteem 2.0; honors: All-League]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 26 (pick 5); became Perfectionist (was Quiet Leader) 33; became Quiet Leader (was Perfectionist) 37]
DECISION_LOG: [none yet]
```

## A retired player (cards are kept for the Archive)

### Celeste Kincaid  (WR, retired)
```yaml
IDENTITY: [Celeste Kincaid, age 31, from Buffalo NY; Junior-college transfer]
SOUL (fixed): [+ Route Technician, - Lacks Burst]  temperament family: precision
PERSONALITY: [Perfectionist] wants flawless execution; fears the one mistake everyone remembers
  - allowed by her soul: Perfectionist, Quiet Leader, Grinder, Diplomat; right now she is overconfident (+0.28)
RATINGS: [overall 93, Franchise player]
  - route: 96  (sees herself at 99, overrating)
  - hands: 91  (sees herself at 93)
  - speed: 90  (sees herself at 92, overrating)
  - pressure thresholds: exile 47, contract 46, spotlight 55, loyalty 58
RECOGNITION: [star; esteem 18.4; honors: All-League x7, Player of the Year]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 1 (pick 4); retired 9; hof_ballot 12; hof_ballot 13; hof_ballot 14; hof_ballot 15; hof_ballot 16; hof_ballot 17]
DECISION_LOG: [none yet]
```

## Head coaches: the most esteemed ever, a typical coach and a weak one

### Coach Hazel Jarrett  (retired)  -  HALL OF FAMER
```yaml
IDENTITY: [Hazel Jarrett, age 64, from Honolulu HI; Analytics-minded newcomer]
SOUL (fixed): [+ Offensive Mastermind, - Undisciplined]
PERSONALITY: [Steady Hand] wants sustained quiet success; fears a collapse nobody saw coming
  - allowed by her soul: Tactician, Innovator, Gambler, Steady Hand; right now she is full of doubt (-0.38)
RATINGS:
  - offense: 73  (sees herself at 69, doubting)   -> +0.35 points of margin
  - defense: 40  (sees herself at 38, doubting)   -> -0.17 points of margin
  - development: 38  (sees herself at 35, doubting)   -> -0.10 rating points per year to each young player
  - gamecraft: 36  (sees herself at 32, doubting)   (no on-field effect yet)
  - discipline: 20  (sees herself at 19)   (no on-field effect yet)
  - motivation: 54  (sees herself at 50, doubting)   (no on-field effect yet)
  - pressure thresholds: exile 33, contract 75, spotlight 27, loyalty 85
TRAJECTORY: [age 53: 49; age 55: 49; age 57: 49; age 59: 50; age 61: 47; age 63: 46; peak 50 at 59; now 44]
RECOGNITION: [Hall of Famer; esteem 23.3; honors: Champion x2, Coach of the Year, Hall of Fame]
RELATIONSHIPS: {Freya Ashby (CEO): -5, Maeve Waller (CEO): -1}
CAREER: [hired 23; retired 35; hof_ballot 38]
DECISION_LOG: [6 earlier; 27: vetoed Wanda Jankowski's pass scheme; 27: vetoed Ingrid Echeverria's blitz scheme; 30: vetoed Wanda Jankowski's pass scheme; 30: vetoed Ingrid Echeverria's blitz scheme; 33: vetoed Wanda Jankowski's run scheme; 34: hired Lara Caldwell as offensive coordinator]
```
### Coach Corinne Atwood  (Team 37)
```yaml
IDENTITY: [Corinne Atwood, age 53, from Milwaukee WI; Small-college head coach promoted]
SOUL (fixed): [+ Talent Developer, - Leaky Defense]
PERSONALITY: [Developer] wants to turn raw talent into stars; fears wasting a prospect
  - allowed by her soul: Developer, Players' Coach, Steady Hand, Innovator; right now she is clear-eyed (+0.03)
RATINGS:
  - offense: 55  (sees herself at 55)   -> +0.02 points of margin
  - defense: 38  (sees herself at 39)   -> -0.30 points of margin
  - development: 82  (sees herself at 80)   -> +0.25 rating points per year to each young player
  - gamecraft: 52  (sees herself at 54, overrating)   (no on-field effect yet)
  - discipline: 79  (sees herself at 78)   (no on-field effect yet)
  - motivation: 46  (sees herself at 46)   (no on-field effect yet)
  - pressure thresholds: exile 67, contract 21, spotlight 57, loyalty 34
TRAJECTORY: [age 40: 55; age 42: 58; age 44: 58; age 46: 59; age 48: 59; age 50: 58; age 52: 59; peak 60 at 51; now 59]
RECOGNITION: [known; esteem 4.9; honors: none yet]
RELATIONSHIPS: {Tasha Brightwater (CEO): -1}
CAREER: [hired 26]
DECISION_LOG: [3 earlier; 26: hired Serena Avery as defensive coordinator; 28: vetoed Serena Avery's coverage scheme; 28: was exiled with her team; 29: vetoed Mei Stratton's pass scheme; 31: vetoed Mei Stratton's pass scheme; 32: vetoed Mei Stratton's pass scheme]
```
### Coach Julia Crenshaw  (Team 12)
```yaml
IDENTITY: [Julia Crenshaw, age 41, from Green Bay WI; Coordinator who got her first shot]
SOUL (fixed): [+ Taskmaster, - Leaky Defense]
PERSONALITY: [Disciplinarian] wants order, rules and no excuses; fears chaos and ego
  - allowed by her soul: Disciplinarian, Steady Hand, Survivor, Tactician; right now she is clear-eyed (-0.09)
RATINGS:
  - offense: 39  (sees herself at 39)   -> -0.32 points of margin
  - defense: 28  (sees herself at 28)   -> -0.51 points of margin
  - development: 52  (sees herself at 52)   -> +0.01 rating points per year to each young player
  - gamecraft: 66  (sees herself at 64)   (no on-field effect yet)
  - discipline: 98  (sees herself at 94, doubting)   (no on-field effect yet)
  - motivation: 38  (sees herself at 37)   (no on-field effect yet)
  - pressure thresholds: exile 63, contract 23, spotlight 57, loyalty 56
TRAJECTORY: [age 41: 53; peak 53 at 41; now 53]
RECOGNITION: [unknown; esteem 1.0; honors: none yet]
RELATIONSHIPS: {Serena Boudreaux (CEO): +4}
CAREER: [hired 39]
DECISION_LOG: [39: fired Cassidy Danforth as offensive coordinator; 39: hired Rosalind Haskell as offensive coordinator]
```

**A coach between jobs (she lives on and may be offered to a CEO again):**

### Coach Layla Boateng  (between jobs)
```yaml
IDENTITY: [Layla Boateng, age 50, from Apia Samoa; Analytics-minded newcomer]
SOUL (fixed): [+ Inspirer, - Costly Decisions]
PERSONALITY: [Players' Coach] wants a locker room that plays hard for her; fears losing the room
  - allowed by her soul: Players' Coach, Developer, Innovator, Survivor; right now she is clear-eyed (-0.14)
RATINGS:
  - offense: 53  (sees herself at 51, doubting)   -> -0.03 points of margin
  - defense: 61  (sees herself at 60)   -> +0.15 points of margin
  - development: 58  (sees herself at 58)   -> +0.07 rating points per year to each young player
  - gamecraft: 49  (sees herself at 46, doubting)   (no on-field effect yet)
  - discipline: 51  (sees herself at 50)   (no on-field effect yet)
  - motivation: 80  (sees herself at 80)   (no on-field effect yet)
  - pressure thresholds: exile 52, contract 44, spotlight 58, loyalty 44
TRAJECTORY: [age 41: 49; age 42: 51; age 43: 52; age 44: 52; age 45: 54; age 46: 55; age 47: 55; age 48: 56; age 49: 57; age 50: 59; peak 59 at 50; now 59]
RECOGNITION: [respected; esteem 8.1; honors: none yet]
RELATIONSHIPS: {Soledad Jankowski (CEO): -29, Samira Colburn (gm): +0, Genevieve Orozco (CEO): +4}
CAREER: [hired 30; fired 40; interviewed 40]
DECISION_LOG: [3 earlier; 30: hired Amina McAllister as defensive coordinator; 31: vetoed Teagan Hutchins's run scheme; 32: vetoed Amina McAllister's coverage scheme; 34: vetoed Teagan Hutchins's pass scheme; 34: hired Mika Eklund as defensive coordinator; 40: was fired by Soledad Jankowski]
```

## Recognition: who the media called a legend, and the Hall of Fame

Nobody was made a legend. These are the Archive's own entries, in order:

```
year 6: legend recognized: Saoirse Crawley (player), esteem 28.8, 100% of outlets
year 9: legend contested: Emilia Jimenez (coach), esteem 21.3, 35% of outlets
year 9: legend contested: Iris Buchanan (owner), esteem 19.3, 35% of outlets
year 15: legend contested: Janelle Rinaldi (coach), esteem 23.6, 50% of outlets
year 15: legend contested: Bianca Moreau (gm), esteem 16.5, 33% of outlets
year 15: legend recognized: Keisha Griffith (owner), esteem 22.7, 100% of outlets
year 19: legend slipped: Keisha Griffith (owner), esteem 17.2, 23% of outlets
year 19: legend contested: Kenna Morrow (player), esteem 25.6, 59% of outlets
year 22: legend contested: Kenna Morrow (player), esteem 25.6, 44% of outlets
year 23: legend contested: Yelena Okafor (coach), esteem 22.8, 33% of outlets
year 23: legend recognized: Celeste Coleridge (owner), esteem 20.2, 61% of outlets
year 25: legend contested: Dominique Obuya (player), esteem 24.6, 39% of outlets
```

**The Hall of Fame so far:**

| Year | Kind | Name | Esteem | Vote | Honors |
|---|---|---|---|---|---|
| 14 | player | Saoirse Crawley | 35.0 | 100% | All-League x9, Player of the Year x6 |
| 22 | player | Kenna Morrow | 25.6 | 93% | All-League x8, Player of the Year x3 |
| 27 | gm | Elena Griffith | 16.3 | 76% | Champion x2 |
| 29 | owner | Carys Iverson | 18.4 | 77% | Champion x2 |
| 32 | player | Hadley Sorensen | 23.7 | 78% | All-League x8, Player of the Year x2, Champion x1 |
| 38 | coach | Hazel Jarrett | 23.3 | 93% | Champion x2, Coach of the Year x1 |
| 38 | gm | Liesel Alvarado | 16.6 | 80% | Champion x2, Executive of the Year x1 |

**The most esteemed player:**

### Saoirse Crawley  (LB, retired)
```yaml
IDENTITY: [Saoirse Crawley, age 32, from Memphis TN; Late bloomer]
SOUL (fixed): [+ Well-Rounded, - Lost in Space]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is overconfident (+0.59)
RATINGS: [overall 87, Franchise player]
  - pass_rush: 90  (sees herself at 95, overrating)
  - run_stop: 91  (sees herself at 93, overrating)
  - coverage: 82  (sees herself at 88, overrating)
  - pressure thresholds: exile 51, contract 33, spotlight 56, loyalty 76
RECOGNITION: [Hall of Famer; esteem 35.0; honors: All-League x9, Player of the Year x6, Hall of Fame]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 1 (pick 2); retired 11; hof_ballot 14]
DECISION_LOG: [none yet]
```

## A CEO, a GM, and the Archive's first entries

### CEO Phoebe Mikkelsen  (Team 10, CEO)
```yaml
IDENTITY: [Phoebe Mikkelsen, age 67, from Detroit MI; Local business CEO]
SOUL (fixed): [+ Shrewd Operator, - Despised]
PERSONALITY: [Opportunist] wants a quick profit; fears a long losing stretch
  - allowed by her soul: Penny-Pincher, Opportunist, Legacy Builder, Patient Steward; right now she is clear-eyed (+0.04)
RATINGS:
  - patience: 44  (sees herself at 47, overrating)
  - ambition: 49  (sees herself at 52, overrating)
  - involvement: 42  (sees herself at 43)
  - popularity: 36  (sees herself at 35)
  - business: 57  (sees herself at 53, doubting)
  - fan approval right now: 62%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 45, media 44, losing 50, subsidy 58
METERS (hers alone; they end with her tenure):
  - Fan Rapport: 68  (she knows exactly what these fans want)
  - Standing Among CEOs: 50  (somewhere in between)
  - Legacy: 66  (her name will be on the wall)
PLEDGE: [standard] the share of a profit she puts back into the club
TRAJECTORY: [age 52: 46; age 54: 46; age 56: 45; age 58: 47; age 60: 46; age 62: 46; age 64: 46; age 66: 46; peak 47 at 58; now 46]
RECOGNITION: [star; esteem 16.2; honors: Champion x2]
RELATIONSHIPS: {Eden Buchanan (gm): -15, Emani Grantham (gm): -11, Phoebe Burkhart (coach): -10, Zoe Alderman (coach): -6, Kenna Aguilar (gm): +4, Team 10 fans: +37}
CAREER: [elected 24]
DECISION_LOG: [18 earlier; 35: survived a recall vote; 36: pledged the standard share of profit to the club; 37: pledged the standard share of profit to the club; 38: pledged the standard share of profit to the club; 39: pledged the standard share of profit to the club; 40: pledged the standard share of profit to the club]
```
### CEO Selah Marlowe  (Team 48, recalled)
```yaml
IDENTITY: [Selah Marlowe, age 66, from Miami FL; Media heiress]
SOUL (fixed): [+ Shrewd Operator, - Content With Mediocrity]
PERSONALITY: [Penny-Pincher] wants a profitable franchise; fears a league subsidy
  - allowed by her soul: Penny-Pincher, Opportunist, Legacy Builder, Patient Steward; right now she is clear-eyed (+0.08)
RATINGS:
  - patience: 24  (sees herself at 24)
  - ambition: 11  (sees herself at 11)
  - involvement: 33  (sees herself at 35, overrating)
  - popularity: 52  (sees herself at 52)
  - business: 59  (sees herself at 59)
  - fan approval right now: 39%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 57, media 39, losing 39, subsidy 50
METERS (hers alone; they end with her tenure):
  - Fan Rapport: 47  (somewhere in between)
  - Standing Among CEOs: 50  (somewhere in between)
  - Legacy: 12  (she will be forgotten)
PLEDGE: [standard] the share of a profit she puts back into the club
TRAJECTORY: [age 66: 36; peak 36 at 66; now 36]
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {Team 48 fans: -43, Sabine Duarte (coach): -10, Andrea Obuya (coach): +4}
CAREER: [elected 39; recalled 40]
DECISION_LOG: [39: fired coach Sabine Duarte (results); 40: pledged the standard share of profit to the club; 40: was recalled]
```
### GM Lola Akana  (Team 44, gm)
```yaml
IDENTITY: [Lola Akana, age 60, from Columbus OH; Came up through the personnel department]
SOUL (fixed): [+ Master Trader, - Draft-Day Disaster]
PERSONALITY: [Dealmaker] wants the best contract in every negotiation; fears being outmaneuvered
  - allowed by her soul: Dealmaker, Gambler, Cold Realist, Talent Hawk; right now she is clear-eyed (-0.20)
RATINGS:
  - scouting: 19  (sees herself at 18)   -> -0.95 rating points on her team's rookie each year
  - negotiation: 52  (sees herself at 51)   -> 2% fewer contract expiries
  - evaluation: 56  (sees herself at 55)   (no on-field effect yet)
  - trades: 68  (sees herself at 68)   (no on-field effect yet)
  - cap_sense: 48  (sees herself at 45, doubting)   (no on-field effect yet)
  - pressure thresholds: exile 65, contract 72, spotlight 27, loyalty 42
TRAJECTORY: [age 60: 49; peak 49 at 60; now 49]
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {Esperanza Caldwell (CEO): +4}
CAREER: [hired 39]
DECISION_LOG: [none yet]
```
**A recall vote as the Archive logs it:**

```
year: 40
event: recall_vote
team: 48
trigger: approval
approval: 0.394
recall_share: 0.517
result: recalled
owner: Selah Marlowe
replacement: Bryn Rosales
candidates: ['Rosalind Iverson', 'Yasmin McBride', 'Bryn Rosales', 'Gabriela Adeyemi', 'Kasey Chambers']
capital: 0.434
```


## A fanbase and the press that covers it

### Fanbase of Team 34  (Long-Suffering)
```yaml
IDENTITY: [Team 34 fans; market size 36 of 100; the franchise's permanent card, it outlives every CEO]
PERSONALITY: [Long-Suffering] wants one real playoff run; fears false hope; picks CEOs who are strong on patience
ARCHETYPES: [+ Demanding, - Steady Hands]
RATINGS:
  - loyalty: 64
  - expectations: 70   (born at 55; drifts with results, within +/-15)
  - passion: 55
  - volatility: 50
  - media_trust: 63
  - approval of the CEO: 60%
  - Fan Capital: 0.63  (recall immunity; worth 3.9 points on a recall vote)
  - what the press did to approval last season: +1.6 points
  - pressure thresholds: exile 81, losing 36, scandal 50, spotlight 62
METERS (this franchise's own; they rise and fall with what happens, and their resting level drifts):
  - Civic Pride: 54  (somewhere in between; resting level 54, since year 0)
  - Hope: 46  (somewhere in between; resting level 38, since year 0)
  - Outrage: 27  (all calm; resting level 35, since year 0)
  - Next Generation: 100  (the kids wear the colors; resting level 99, since year 14)
  - Homecoming Pull: 61  (the exile healed into pride; resting level 55, since year 30)
BOYCOTT: [off]
MEMORIES (fading):
  - 37: the club was sent into exile  (remembered 77%)
  - 38: the club came home from exile  (remembered 67%)
  - 29: the club was sent into exile  (remembered 39%)
  - 30: the club came home from exile  (remembered 34%)
  - 26: Juana Okafor left the club  (remembered 15%)
  - 17: the championship  (remembered 14%)
SPENDING_ASK: [fair] what the fans asked of the CEO's investment this year
RELATIONSHIPS: {Penelope Lockhart (CEO): -42, Tove Clairmont (CEO): -26, Yelena Brightwater (CEO): -14, Lola Garrison (CEO): -11, Vera Choi (CEO): +19}
DECISION_LOG: [42 earlier; 37: asked for the fair level of investment; 37: kept the CEO; 38: asked for the fair level of investment; 38: kept the CEO; 39: asked for the fair level of investment; 40: asked for the fair level of investment]
```
### Fanbase of Team 39  (Entitled)
```yaml
IDENTITY: [Team 39 fans; market size 60 of 100; the franchise's permanent card, it outlives every CEO]
PERSONALITY: [Entitled] wants a title every year; fears being ignored; picks CEOs who are strong on ambition
ARCHETYPES: [+ Demanding, - Distrust the Press]
RATINGS:
  - loyalty: 19
  - expectations: 51   (born at 66; drifts with results, within +/-15)
  - passion: 46
  - volatility: 39
  - media_trust: 16
  - approval of the CEO: 45%
  - Fan Capital: 0.36  (recall immunity; worth 0.0 points on a recall vote)
  - what the press did to approval last season: -0.4 points
  - pressure thresholds: exile 69, losing 57, scandal 56, spotlight 30
METERS (this franchise's own; they rise and fall with what happens, and their resting level drifts):
  - Outrage: 30  (all calm; resting level 38, since year 0)
  - Memory Keepers: 36  (last year is ancient history; resting level 36, since year 0)
  - Wallet Mood: 55  (somewhere in between; resting level 56, since year 0)
  - Kinship With the Roster: 51  (somewhere in between; resting level 53, since year 1)
  - Grudge: 74  (they have not forgiven the league; resting level 72, since year 17)
BOYCOTT: [off]
MEMORIES (fading):
  - 39: the club was sent into exile  (remembered 90%)
  - 40: the club came home from exile  (remembered 80%)
  - 37: the club was sent into exile  (remembered 74%)
  - 38: the club came home from exile  (remembered 66%)
  - 39: the fans began to boycott  (remembered 63%)
  - 34: the club was sent into exile  (remembered 55%)
SPENDING_ASK: [fair] what the fans asked of the CEO's investment this year
RELATIONSHIPS: {Maribel Hargrove (CEO): -44, Janelle Forsythe (CEO): -38, Elsa Maynard (CEO): -32, Amina Aoki (CEO): -32, Penelope Dubois (CEO): -32, Brenna Ahlberg (CEO): -32, Maya Marlowe (CEO): -32, Teagan Kasprzak (CEO): -32, Penelope Vasquez (CEO): -32, Laila Tavares (CEO): -32, Naomi Trevino (CEO): -32, Stella Quillen (CEO): +24}
DECISION_LOG: [49 earlier; 37: voted to recall the CEO; 38: asked for the fair level of investment; 38: voted to recall the CEO; 39: asked for the fair level of investment; 39: voted to recall the CEO; 40: asked for the fair level of investment]
```
### Fanbase of Team 42  (Die-Hards)
```yaml
IDENTITY: [Team 42 fans; market size 58 of 100; the franchise's permanent card, it outlives every CEO]
PERSONALITY: [Die-Hards] wants a team that is theirs; fears a sale or a move; picks CEOs who are strong on popularity
ARCHETYPES: [+ Fanatical, - Easily Pleased]
RATINGS:
  - loyalty: 65
  - expectations: 42   (born at 40; drifts with results, within +/-15)
  - passion: 78
  - volatility: 52
  - media_trust: 55
  - approval of the CEO: 62%
  - Fan Capital: 0.66  (recall immunity; worth 4.7 points on a recall vote)
  - what the press did to approval last season: -1.5 points
  - pressure thresholds: exile 47, losing 36, scandal 61, spotlight 69
METERS (this franchise's own; they rise and fall with what happens, and their resting level drifts):
  - Outrage: 100  (the phones are ringing; resting level 89, since year 0)
  - Hope: 85  (next year is the year; resting level 92, since year 0)
  - Bandwagon: 90  (everyone wants a seat; resting level 80, since year 0)
  - Grudge: 50  (somewhere in between; resting level 42, since year 21)
  - Next Generation: 56  (somewhere in between; resting level 52, since year 34)
BOYCOTT: [off]
MEMORIES (fading):
  - 40: the club was sent into exile  (remembered 100%)
  - 36: the championship  (remembered 71%)
  - 34: the championship  (remembered 59%)
  - 39: Lola Dietrich left the club  (remembered 46%)
  - 30: the club was sent into exile  (remembered 42%)
  - 31: the club came home from exile  (remembered 37%)
SPENDING_ASK: [fair] what the fans asked of the CEO's investment this year
RELATIONSHIPS: {Anika Coleridge (CEO): -42, Mika Jefferson (CEO): -27, Alexis Eklund (CEO): -26, Cassidy Waller (CEO): +3, Maeve Pinkerton (CEO): +8}
DECISION_LOG: [45 earlier; 37: asked for the fair level of investment; 38: asked for the fair level of investment; 39: asked for the fair level of investment; 39: kept the CEO; 40: asked for the fair level of investment; 40: kept the CEO]
```
The franchise's permanent card, with its own meters, memories and any boycott (the club with the longest memory):

### Fanbase of Team 41  (Party Crowd)
```yaml
IDENTITY: [Team 41 fans; market size 42 of 100; the franchise's permanent card, it outlives every CEO]
PERSONALITY: [Party Crowd] wants a good time; fears boredom; picks CEOs who are strong on involvement
ARCHETYPES: [+ Demanding, - Fair-Weather]
RATINGS:
  - loyalty: 40
  - expectations: 61   (born at 51; drifts with results, within +/-15)
  - passion: 48
  - volatility: 56
  - media_trust: 40
  - approval of the CEO: 59%
  - Fan Capital: 0.58  (recall immunity; worth 2.3 points on a recall vote)
  - what the press did to approval last season: +0.9 points
  - pressure thresholds: exile 63, losing 57, scandal 30, spotlight 46
METERS (this franchise's own; they rise and fall with what happens, and their resting level drifts):
  - Outrage: 62  (the phones are ringing; resting level 70, since year 0)
  - Hope: 47  (somewhere in between; resting level 43, since year 0)
  - Patience: 54  (somewhere in between; resting level 56, since year 0)
  - Grudge: 83  (they have not forgiven the league; resting level 77, since year 16)
  - Civic Pride: 32  (the team is just a tenant; resting level 31, since year 30)
BOYCOTT: [off]
MEMORIES (fading):
  - 38: the club was sent into exile  (remembered 84%)
  - 39: the club came home from exile  (remembered 73%)
  - 38: the fans began to boycott  (remembered 59%)
  - 33: the club was sent into exile  (remembered 55%)
  - 34: the club came home from exile  (remembered 48%)
  - 34: the fans began to boycott  (remembered 42%)
SPENDING_ASK: [fair] what the fans asked of the CEO's investment this year
RELATIONSHIPS: {Yuki Olmstead (CEO): -59, Agnes Emerson (CEO): -32, Odalys Maynard (CEO): -25, Zelda Pettigrew (CEO): -13, Jamila Beaumont (CEO): +9}
DECISION_LOG: [46 earlier; 37: asked for the fair level of investment; 38: asked for the fair level of investment; 38: kept the CEO; 39: asked for the fair level of investment; 39: kept the CEO; 40: asked for the fair level of investment]
```
### The Scoreboard  (national, league-wide; active)
```yaml
IDENTITY: [The Scoreboard, national outlet; byline Jamila Buchanan]
PERSONALITY: [Hype Machine] wants clicks and a roaring crowd; fears irrelevance
ARCHETYPES: [+ Everywhere, - Dry as Dust]
RATINGS:
  - reach: 86
  - sensationalism: 43
  - weight in the legend and Hall of Fame votes: 76
  - the facts: always accurate; it tells each team's year as it was
  - pressure thresholds: spotlight 45, access 34, irrelevance 37
RELATIONSHIPS: {}  # none yet; filled by Interactions
DECISION_LOG: [none yet]
```
### Team 24 Insider  (local, Team 24; active)
```yaml
IDENTITY: [Team 24 Insider, local outlet; byline Elena Merrick]
PERSONALITY: [Hype Machine] wants clicks and a roaring crowd; fears irrelevance
ARCHETYPES: [+ Headline Chaser, - Nobody Reads It]
RATINGS:
  - reach: 39
  - sensationalism: 81
  - weight in the legend and Hall of Fame votes: 44
  - the facts: always accurate; it frames each year the way its own fans prefer (by at most 25 points of tone)
  - pressure thresholds: spotlight 61, access 47, irrelevance 43
RELATIONSHIPS: {}  # none yet; filled by Interactions
DECISION_LOG: [none yet]
```

## A CEO, answering to her fans

The CEO's own meters end with her tenure (the fanbase's are the permanent ones). She chooses a pledge each year and, under a boycott, how to answer it.

### CEO Phoebe Mikkelsen  (Team 10, CEO)
```yaml
IDENTITY: [Phoebe Mikkelsen, age 67, from Detroit MI; Local business CEO]
SOUL (fixed): [+ Shrewd Operator, - Despised]
PERSONALITY: [Opportunist] wants a quick profit; fears a long losing stretch
  - allowed by her soul: Penny-Pincher, Opportunist, Legacy Builder, Patient Steward; right now she is clear-eyed (+0.04)
RATINGS:
  - patience: 44  (sees herself at 47, overrating)
  - ambition: 49  (sees herself at 52, overrating)
  - involvement: 42  (sees herself at 43)
  - popularity: 36  (sees herself at 35)
  - business: 57  (sees herself at 53, doubting)
  - fan approval right now: 62%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 45, media 44, losing 50, subsidy 58
METERS (hers alone; they end with her tenure):
  - Fan Rapport: 68  (she knows exactly what these fans want)
  - Standing Among CEOs: 50  (somewhere in between)
  - Legacy: 66  (her name will be on the wall)
PLEDGE: [standard] the share of a profit she puts back into the club
TRAJECTORY: [age 52: 46; age 54: 46; age 56: 45; age 58: 47; age 60: 46; age 62: 46; age 64: 46; age 66: 46; peak 47 at 58; now 46]
RECOGNITION: [star; esteem 16.2; honors: Champion x2]
RELATIONSHIPS: {Eden Buchanan (gm): -15, Emani Grantham (gm): -11, Phoebe Burkhart (coach): -10, Zoe Alderman (coach): -6, Kenna Aguilar (gm): +4, Team 10 fans: +37}
CAREER: [elected 24]
DECISION_LOG: [18 earlier; 35: survived a recall vote; 36: pledged the standard share of profit to the club; 37: pledged the standard share of profit to the club; 38: pledged the standard share of profit to the club; 39: pledged the standard share of profit to the club; 40: pledged the standard share of profit to the club]
```

## Scenes as the Archive records them

Each firing, recall vote and exile determination is a scene: every party gives its own claim, and the evidence section says, from the engine's own numbers, which claims hold. The scenes never change an outcome (the check script proves a league plays out identically with them on or off); they explain it, and they move relationships and decision logs.

**An exile determination**

```
EVENT 40-exile_determination-46-1  (Team 46; exile determination; finished fifth in the division)
├── Owner claims: Maia Beaumont (Glory Hunter): "Fifth in the division, and I will say who is to blame: Hana Fitzgerald. The roster rated 47% and they won 33%."  [supported by the record]
├── Coach claims: Hana Fitzgerald (Developer): "I was handed a roster 1.3 deviations below average and the schedule did the rest."  [supported, but overstated]
├── GM claims: Aiko Dalton (Planner): "The roster was 4 of 5 in this division on paper. The record, 33%, was 13% below what it should have been."  [supported by the record]
├── The fans claim: Team 46 fans: "They finished 33%. We wanted a title every year and we feared being ignored; that is what we got."  [supported by the record]
├── Press claims: Team 46 Sideline (Statistician): "They finished 33%. The town is watching closely, and that is how we are telling it."  [supported by the record]
└── Evidence supports: Exile followed a thin roster and under-delivery against the roster.  (record 33%, roster predicts 47%, roster -0.6 deviations from average)
    Outcome: Team 46 is exiled for next season
```

**A firing the record backs**

```
EVENT 40-firing-48-1  (Team 48; firing; CEO fired the coach (results))
├── Owner claims: Bryn Rosales (Glory Hunter): "the roster should have won about 54% and they won 21%. I gave her 2 seasons; I had no patience left."  [supported by the record]
├── Coach claims: Andrea Obuya (Disciplinarian): "You gave me a roster 0.4 deviations below the league's average and expected a contender."  [not supported by the record]
├── GM claims: Sofia Fitzgerald (Talent Hawk): "The roster was fine. The record was 21%, against 54% on paper."  [supported by the record]
├── The fans claim: Team 48 fans: "They finished 21%. We wanted honesty and we feared being fooled again; that is what we got."  [supported by the record]
├── Press claims: Team 48 Insider (Contrarian): "They finished 21%. The town is watching closely, and that is how we are telling it."  [supported by the record]
└── Evidence supports: The firing is backed by the record, and the roster does not excuse it: the team won well under what it was built to win.  (record 21%, roster predicts 54%, roster +0.2 deviations from average)
    Outcome: Andrea Obuya fired; replaced by a new coach
```

**A harsh firing (the roster explains the record)**

```
EVENT 40-firing-48-2  (Team 48; firing; CEO fired the gm (results))
├── Owner claims: Bryn Rosales (Glory Hunter): "the roster should have won about 54% and they won 21%. I trusted her with the roster; I had no patience left."  [supported by the record]
├── GM claims: Sofia Fitzgerald (Talent Hawk): "I built the roster and she lost games the roster should have won: 21% on a team that rates 54%."  [supported by the record]
├── Coach claims: Andrea Obuya (Disciplinarian): "I coached what I was handed, a roster 0.2 deviations above average."  [not supported by the record]
├── The fans claim: Team 48 fans: "They finished 21%. We wanted honesty and we feared being fooled again; that is what we got."  [supported by the record]
├── Press claims: Team 48 Insider (Contrarian): "They finished 21%. The town is watching closely, and that is how we are telling it."  [supported by the record]
└── Evidence supports: A harsh firing: the record was poor (21%), but the roster she built was not thin, so the shortfall was on the field.  (record 21%, roster predicts 54%, roster +0.2 deviations from average)
    Outcome: Sofia Fitzgerald fired; replaced by a new gm
```

**A new CEO's sweep**

```
EVENT 40-firing-06-2  (Team 06; firing; CEO fired the gm (new CEO cleaned house))
├── Owner claims: Soledad Jankowski (Patient Steward): "New CEO, new staff. I wanted a slow, sound build and I wasn't going to ask Samira Colburn for it."  [supported by the record]
├── GM claims: Samira Colburn (Talent Hawk): "I built the roster and she lost games the roster should have won: 50% on a team that rates 67%."  [supported by the record]
├── Coach claims: Layla Boateng (Players' Coach): "I coached what I was handed, a roster 1.6 deviations above average."  [not supported by the record]
├── The fans claim: Team 06 fans: "They finished 50%. We wanted honesty and we feared being fooled again; we have no complaint about the record, but we are watching."  [not supported by the record]
├── Press claims: Team 06 Sideline (Hype Machine): "They finished 50%. The town is watching closely, and that is how we are telling it."  [supported by the record]
└── Evidence supports: A sweep: the new CEO cleared the staff on arrival, whatever the record (50% against 67% on paper).  (record 50%, roster predicts 67%, roster +1.6 deviations from average)
    Outcome: Samira Colburn fired; replaced by a new gm
```

**A recall vote that removes a CEO**

```
EVENT 40-recall_vote-48-1  (Team 48; recall vote; vote triggered by approval)
├── Owner claims: Selah Marlowe (Penny-Pincher): "I thought we were at 35%. The team lost, and the fans are blaming the person they can vote on."  [supported by the record]
├── The fans claim: Team 48 fans: "They finished 21%. We wanted honesty and we feared being fooled again; that is what we got." We wanted a CEO strong on business and we chose Bryn Rosales.  [supported by the record]
├── Press claims: Team 48 Insider (Contrarian): "They finished 21%. The town is watching closely, and that is how we are telling it."  [supported by the record]
├── New CEO claims: Bryn Rosales (Glory Hunter): "Five of us stood. The fans wanted strength on business and picked me. I want a title right now."  [not supported by the record]
└── Evidence supports: 51.7% voted to recall (a majority of the 1,000,000 fans is needed): recalled.  (record 21%, roster predicts 54%, roster +0.2 deviations from average)
    Outcome: Selah Marlowe recalled; Bryn Rosales elected from 5 candidates
```

**A recall vote the CEO survives**

```
EVENT 40-recall_vote-47-1  (Team 47; recall vote; vote triggered by rotation)
├── Owner claims: Beatriz Dimitrov (Local Hero): "I told you we were at 73%. The fans know what I stand for: the town's love."  [supported by the record]
├── The fans claim: Team 47 fans: "They finished 83%. We wanted a good time and we feared boredom; we have no complaint about the record, but we are watching."  [not supported by the record]
├── Press claims: Team 47 Courier (Watchdog): "They finished 83%. The town is behind the team, and that is how we are telling it."  [supported by the record]
└── Evidence supports: 19.4% voted to recall (a majority of the 1,000,000 fans is needed): the CEO survives.  (record 83%, roster predicts 51%, roster -0.1 deviations from average)
    Outcome: Beatriz Dimitrov survives
```


## What an agent is shown, and what the log keeps

Choices go through Decision Points. An agent is shown its own card, what it perceives (candidates' ratings as the CEO sees them, with blind spots) and the legal options, and answers with one option id. The guard applies the choice (or the autopilot's choice if the answer is invalid or late) and logs it. Below: the two decisions a CEO faces, as an agent receives them, and the log line.

**A CEO's staff review, as an agent receives it:**

```json
{
 "top_priority": {
  "goal": "Win the Diamond Coronation. It is the first priority of every role in the league; everything else on this card is a means to it.",
  "your_team": "Team 01",
  "strength_rank": 30,
  "of_teams": 48,
  "coronations_won": 0,
  "last_won": null
 },
 "id": "1-staff_review-01-1",
 "kind": "staff_review",
 "year": 1,
 "team": 1,
 "decider": {
  "role": "ceo",
  "name": "Stella Wagner",
  "trait": "Glory Hunter",
  "wants": "a title right now",
  "fears": "being a laughingstock",
  "ratings": {
   "patience": 34.5,
   "ambition": 76.1,
   "involvement": 34.2,
   "popularity": 57.3,
   "business": 54.7
  },
  "pressure": {
   "recall": 49,
   "media": 70,
   "losing": 51,
   "subsidy": 65
  },
  "age": 57,
  "reputation": "unknown",
  "honors": {},
  "career_summary": {
   "jobs": 1,
   "fired": 0,
   "recalled": 0
  },
  "recent_decisions": [
   {
    "year": 1,
    "did": "pledged the lean share of profit to the club"
   }
  ],
  "notes_to_self": []
 },
 "context": {
  "record_this_season": 0.444,
  "record_last_season": null,
  "exiled_this_year": false,
  "fan_approval_of_you": 0.645,
  "facing_a_recall_vote_this_year": true,
  "you_are_a_new_ceo": false,
  "press_effect_on_fans": -0.004,
  "coach": {
   "name": "Honor Lachance",
   "age": 63,
   "path": "Small-college head coach promoted",
   "trait": "Developer",
   "perceived": {
    "offense": 51.0,
    "defense": 41.0,
    "development": 66.0,
    "gamecraft": 39.0,
    "discipline": 25.0,
    "motivation": 54.0
   },
   "reputation": "unknown",
   "honors": {},
   "previous_jobs": 1,
   "seasons_with_team": 1,
   "pressure_on_her": 0.056,
   "can_be_fired": true
  },
  "gm": {
   "name": "Astrid Ellison",
   "age": 39,
   "path": "Agent turned GM",
   "trait": "Talent Hawk",
   "perceived": {
    "scouting": 63.0,
    "negotiation": 56.0,
    "evaluation": 67.0,
    "trades": 53.0,
    "cap_sense": 29.0
   },
   "reputation": "unknown",
   "honors": {},
   "previous_jobs": 1,
   "seasons_with_team": 1,
   "pressure_on_her": 0.056,
   "can_be_fired": true
  }
 },
 "options": [
  {
   "id": "keep_all",
   "label": "Keep the coach and the GM",
   "tags": {
    "fires": 0
   }
  },
  {
   "id": "fire_coach",
   "label": "Fire coach Honor Lachance",
   "tags": {
    "fires": 1
   }
  },
  {
   "id": "fire_gm",
   "label": "Fire GM Astrid Ellison",
   "tags": {
    "fires": 1
   }
  },
  {
   "id": "fire_both",
   "label": "Fire both",
   "tags": {
    "fires": 2
   }
  }
 ],
 "instructions": "Reply with the id of exactly one option, and optionally a short reason and a short note to yourself (plain words; the note is shown back to you at your next decision)."
}
```

**A coaching hire, as an agent receives it:**

```json
{
 "top_priority": {
  "goal": "Win the Diamond Coronation. It is the first priority of every role in the league; everything else on this card is a means to it.",
  "your_team": "Team 06",
  "strength_rank": 38,
  "of_teams": 48,
  "coronations_won": 0,
  "last_won": null
 },
 "id": "1-hire_coach-06-1",
 "kind": "hire_coach",
 "year": 1,
 "team": 6,
 "decider": {
  "role": "ceo",
  "name": "Priya Pruitt",
  "trait": "Patient Steward",
  "wants": "a slow, sound build",
  "fears": "panic",
  "ratings": {
   "patience": 61.9,
   "ambition": 34.7,
   "involvement": 43.6,
   "popularity": 49.5,
   "business": 50.1
  },
  "pressure": {
   "recall": 51,
   "media": 31,
   "losing": 51,
   "subsidy": 77
  },
  "age": 60,
  "reputation": "unknown",
  "honors": {},
  "career_summary": {
   "jobs": 1,
   "fired": 0,
   "recalled": 0
  },
  "recent_decisions": [
   {
    "year": 1,
    "did": "pledged the lean share of profit to the club"
   }
  ],
  "notes_to_self": []
 },
 "context": {
  "team_needs": "a head coach"
 },
 "options": [
  {
   "id": "candidate_0",
   "label": "Hire Yara Marlowe",
   "tags": {
    "between_jobs": false
   },
   "view": {
    "name": "Yara Marlowe",
    "age": 43,
    "path": "Analytics-minded newcomer",
    "trait": "Tactician",
    "perceived": {
     "offense": 15.0,
     "defense": 52.0,
     "development": 82.0,
     "gamecraft": 77.0,
     "discipline": 59.0,
     "motivation": 52.0
    },
    "reputation": "unknown",
    "honors": {},
    "previous_jobs": 0
   }
  },
  {
   "id": "candidate_1",
   "label": "Hire Julia Burkhart",
   "tags": {
    "between_jobs": false
   },
   "view": {
    "name": "Julia Burkhart",
    "age": 62,
    "path": "Analytics-minded newcomer",
    "trait": "Innovator",
    "perceived": {
     "offense": 37.0,
     "defense": 63.0,
     "development": 34.0,
     "gamecraft": 28.0,
     "discipline": 52.0,
     "motivation": 60.0
    },
    "reputation": "unknown",
    "honors": {},
    "previous_jobs": 0
   }
  },
  {
   "id": "candidate_2",
   "label": "Hire Mei Eklund",
   "tags": {
    "between_jobs": false
   },
   "view": {
    "name": "Mei Eklund",
    "age": 51,
    "path": "Former star player turned coach",
    "trait": "Disciplinarian",
    "perceived": {
     "offense": 59.0,
     "defense": 39.0,
     "development": 67.0,
     "gamecraft": 48.0,
     "discipline": 55.0,
     "motivation": 32.0
    },
    "reputation": "unknown",
    "honors": {},
    "previous_jobs": 0
   }
  }
 ],
 "instructions": "Reply with the id of exactly one option, and optionally a short reason and a short note to yourself (plain words; the note is shown back to you at your next decision)."
}
```

**The choice log keeps:**

```
{"id": "1-hire_coach-06-1", "year": 1, "kind": "hire_coach", "team": 6, "actor": "owner", "options": ["candidate_0", "candidate_1", "candidate_2"], "default": "candidate_0", "chosen": "candidate_0", "driver": "agent", "status": "ok", "reason": "Illustrative answer from a stand-in agent."}
{"id": "1-hire_coach-07-1", "year": 1, "kind": "hire_coach", "team": 7, "actor": "owner", "options": ["candidate_0", "candidate_1", "candidate_2"], "default": "candidate_0", "chosen": "candidate_0", "driver": "agent", "status": "ok", "reason": "Illustrative answer from a stand-in agent."}
{"id": "1-hire_coach-11-1", "year": 1, "kind": "hire_coach", "team": 11, "actor": "owner", "options": ["candidate_0", "candidate_1", "candidate_2"], "default": "candidate_0", "chosen": "candidate_0", "driver": "agent", "status": "ok", "reason": "Illustrative answer from a stand-in agent."}
{"id": "1-hire_coach-27-1", "year": 1, "kind": "hire_coach", "team": 27, "actor": "owner", "options": ["candidate_0", "candidate_1", "candidate_2"], "default": "candidate_0", "chosen": "candidate_0", "driver": "agent", "status": "ok", "reason": "Illustrative answer from a stand-in agent."}
{"id": "1-hire_coach-31-1", "year": 1,
```


## How the cards spread across the league

**Core personalities (all rostered players):** Diplomat 584, Grinder 446, Competitor 441, Perfectionist 364, Showman 245, Quiet Leader 166, Free Spirit 154, Hothead 90, Mercenary 29, Loyalist 25

**Most common positive archetypes:** Well-Rounded 748, Road Grader 129, Ballhawk 123, Pass-Pro Wall 120, Edge Terror 119, Shutdown Corner 107, Run Stuffer 90, Route Technician 83

**Coach effect across the 48 teams:** average -0.01, spread (sd) 0.43, best +1.05, worst -0.83 points of expected margin. For scale, team talent has a spread of about 3 to 4 points.

**Personality shifts:** 3093 of 31416 players have changed personality at least once in 40 seasons.

**Standing in the media's eyes** (everyone who ever lived, by what the media calls her now): known 236, respected 120, star 35, Hall of Famer 7, legend 3. 7 are in the Hall of Fame.

**Fan cultures:** Die-Hards 13, Entitled 11, Party Crowd 9, Gloomy Realists 7, Long-Suffering 5, Front-Runners 3

**Fan Capital:** average 0.53, from 0.36 to 0.66; the most it can buffer a recall vote is 15 points.

**Fan meters:** every fanbase has 3 from birth and can awaken up to 5; now [(5, 42), (4, 4), (3, 2)] (meters per club, clubs). Most common: Outrage 33, Grudge 32, Homecoming Pull 28, Civic Pride 23.

**Fan memories** held now: exile 186, return 157, boycott 75, boycott_end 34, star_left 28, title 21, drought 12. **Boycotts** on now: 0 clubs; 75 begun within the memory window. A full boycott costs 40% of local revenue.

**The press on approval, last season:** average 1.0 points either way, largest 3.2 (the cap is 3 before market size and trust).

**Outlets:** 52 (4 national, one local beat per team); a national outlet tells a team's year as it was, a local outlet frames it toward its fans' mood by at most 25 points of tone.

**CEO choices on the record:** ceo_boycott concede 17, ceo_boycott hold 31, ceo_pledge standard 1867. CEOs who stepped aside under a boycott: 0.

**Scenes:** 1120 in 40 seasons ([('recall_vote', 566), ('exile_determination', 320), ('firing', 234)]). Firings by ruling: fair 153, sweep 60, harsh 14, unfounded 7.

**Recall votes:** 566 in 40 seasons (14.2 a year); 188 CEOs recalled (4.7 a year), 33% of votes. CEOs retire on their own too: 48 so far.

**Firings:** 152 coaches and 82 GMs fired in 40 seasons.

**Coaches so far:** 365 hired and 299 retired in 40 seasons; 19 coaches and 14 GMs are between jobs right now.

**Coordinators:** 719 hired and 583 retired in 40 seasons; 40 between jobs. Schemes proposed: coverage 818, pass 778, blitz 772, run 755, balanced 717; the head coach vetoed 714 of 3123. 469 coordinators fired by their head coaches.

```
THALIA LOMBARDI  -  offensive coordinator, Team 01  -  age 36, from Boise ID
  PLAYCALLING 60   VISION 43   heat -0.07   years here 1
  Her lift to her unit: +0.15 points of margin (the average coordinator is zero).
  Career: 39 hired
  Lately: 40 proposed the pass scheme

KAIA BURKHART  -  defensive coordinator, Team 01  -  age 53, from Laredo TX
  PLAYCALLING 54   VISION 44   heat -0.06   years here 6
  Her lift to her unit: +0.03 points of margin (the average coordinator is zero).
  Career: 34 hired
  Lately: 38 proposed the blitz scheme; 39 proposed the blitz scheme; 40 proposed the coverage scheme
```

**GM plan choices on the record:** gm_cap_plan balanced 1920, gm_draft_focus needs 1920 (the autopilot keeps the old rule).

**Players with cards:** 3244 active or unsigned, 28872 retired.
