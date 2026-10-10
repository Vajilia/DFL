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

### Evangeline Gentry II  (QB, Team 10)
```yaml
IDENTITY: [Evangeline Gentry II, age 24, from Spokane WA; Overlooked recruit]
SOUL (fixed): [+ Surgeon, - Reads Late]  temperament family: precision
PERSONALITY: [Perfectionist] wants flawless execution; fears the one mistake everyone remembers
  - allowed by her soul: Perfectionist, Quiet Leader, Grinder, Diplomat; right now she is full of doubt (-0.51)
RATINGS: [overall 83, Franchise player]
  - accuracy: 88  (sees herself at 83, doubting)
  - arm: 80  (sees herself at 78, doubting)
  - awareness: 79  (sees herself at 74, doubting)
  - pressure thresholds: exile 55, contract 72, spotlight 78, loyalty 23
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 39 (pick 2)]
DECISION_LOG: [none yet]
```
### Selah Ibarra II  (WR, Team 23)
```yaml
IDENTITY: [Selah Ibarra II, age 25, from El Paso TX; International pathway]
SOUL (fixed): [+ Burner, - Drop-Prone]  temperament family: flash
PERSONALITY: [Free Spirit] wants freedom and adventure along the way; fears a rigid system
  - allowed by her soul: Showman, Free Spirit, Competitor, Mercenary; right now she is full of doubt (-0.91)
RATINGS: [overall 90, Franchise player]
  - route: 86  (sees herself at 81, doubting)
  - hands: 83  (sees herself at 76, doubting)
  - speed: 99  (sees herself at 91, doubting)
  - pressure thresholds: exile 62, contract 50, spotlight 69, loyalty 63
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 37 (pick 2); became Free Spirit (was Showman) 40]
DECISION_LOG: [none yet]
```
### Liesel Toussaint II  (OL, Team 45)
```yaml
IDENTITY: [Liesel Toussaint II, age 27, from Portland OR; Two-sport athlete]
SOUL (fixed): [+ Pass-Pro Wall, - Soft in the Run]  temperament family: precision
PERSONALITY: [Perfectionist] wants flawless execution; fears the one mistake everyone remembers
  - allowed by her soul: Perfectionist, Quiet Leader, Grinder, Diplomat; right now she is full of doubt (-0.31)
RATINGS: [overall 77, Star]
  - pass_block: 80  (sees herself at 78)
  - run_block: 74  (sees herself at 71, doubting)
  - pressure thresholds: exile 65, contract 45, spotlight 45, loyalty 56
RECOGNITION: [unknown; esteem 2.5; honors: All-League]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 35 (pick 18)]
DECISION_LOG: [none yet]
```
### Rachelle Barlow II  (DL, Team 23)
```yaml
IDENTITY: [Rachelle Barlow II, age 27, from Anchorage AK; Power-conference star]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is full of doubt (-0.46)
RATINGS: [overall 86, Franchise player]
  - pass_rush: 89  (sees herself at 84, doubting)
  - run_stop: 82  (sees herself at 79, doubting)
  - pressure thresholds: exile 39, contract 51, spotlight 55, loyalty 49
RECOGNITION: [known; esteem 4.8; honors: All-League x2]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 36 (pick 6)]
DECISION_LOG: [none yet]
```
### Mireya Dellinger II  (CB, Team 22)
```yaml
IDENTITY: [Mireya Dellinger II, age 29, from El Paso TX; Two-sport athlete]
SOUL (fixed): [+ Ballhawk, - Avoids Contact]  temperament family: flash
PERSONALITY: [Free Spirit] wants freedom and adventure along the way; fears a rigid system
  - allowed by her soul: Showman, Free Spirit, Competitor, Mercenary; right now she is full of doubt (-0.30)
RATINGS: [overall 91, Franchise player]
  - coverage: 91  (sees herself at 87, doubting)
  - ball_skills: 97  (sees herself at 95, doubting)
  - tackling: 81  (sees herself at 80)
  - pressure thresholds: exile 41, contract 28, spotlight 43, loyalty 23
RECOGNITION: [respected; esteem 11.1; honors: All-League x5]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 33 (pick 2)]
DECISION_LOG: [none yet]
```
### Kenna Toussaint II  (K, Team 30)
```yaml
IDENTITY: [Kenna Toussaint II, age 31, from Bozeman MT; Coach's daughter]
SOUL (fixed): [+ Big Leg, - Erratic]  temperament family: power
PERSONALITY: [Grinder] wants to earn every inch; fears being handed nothing and losing it anyway
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is full of doubt (-1.00)
RATINGS: [overall 83, Franchise player]
  - power: 91  (sees herself at 81, doubting)
  - accuracy: 78  (sees herself at 65, doubting)
  - pressure thresholds: exile 46, contract 38, spotlight 45, loyalty 55
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```

## A young rookie and a veteran

### Alba Fennimore II  (RB, Team 21)
```yaml
IDENTITY: [Alba Fennimore II, age 22, from Columbus OH; Two-sport athlete]
SOUL (fixed): [+ Shifty Slasher, - Goes Down Easy]  temperament family: flash
PERSONALITY: [Showman] wants the spotlight and a signature moment; fears being ignored by the media
  - allowed by her soul: Showman, Free Spirit, Competitor, Mercenary; right now she is overconfident (+0.33)
RATINGS: [overall 69, Starter]
  - elusive: 78  (sees herself at 81, overrating)
  - power: 58  (sees herself at 61, overrating)
  - hands: 73  (sees herself at 75, overrating)
  - pressure thresholds: exile 40, contract 67, spotlight 65, loyalty 43
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 40 (pick 1)]
DECISION_LOG: [none yet]
```
### Xiomara Mangum  (WR, Team 03)
```yaml
IDENTITY: [Xiomara Mangum, age 33, from Omaha NE; International pathway]
SOUL (fixed): [+ Burner, - Drop-Prone]  temperament family: flash
PERSONALITY: [Showman] wants the spotlight and a signature moment; fears being ignored by the media
  - allowed by her soul: Showman, Free Spirit, Competitor, Mercenary; right now she is overconfident (+0.71)
RATINGS: [overall 87, Franchise player]
  - route: 89  (sees herself at 94, overrating)
  - hands: 79  (sees herself at 86, overrating)
  - speed: 93  (sees herself at 97, overrating)
  - pressure thresholds: exile 66, contract 52, spotlight 49, loyalty 72
RECOGNITION: [legend; esteem 38.0; honors: All-League x9, Champion, Player of the Year x6]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 29 (pick 1); became Free Spirit (was Showman) 31; became Showman (was Free Spirit) 37]
DECISION_LOG: [none yet]
```

## A player whose personality changed (her soul stayed the same)

### Yuki Echeverria  (DL, Team 20)
```yaml
IDENTITY: [Yuki Echeverria, age 32, from Detroit MI; Walk-on turned starter]
SOUL (fixed): [+ Edge Terror, - Gets Washed Out]  temperament family: power
PERSONALITY: [Grinder] wants to earn every inch; fears being handed nothing and losing it anyway
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is full of doubt (-0.43)
RATINGS: [overall 62, Depth]
  - pass_rush: 64  (sees herself at 61, doubting)
  - run_stop: 59  (sees herself at 55, doubting)
  - pressure thresholds: exile 64, contract 58, spotlight 43, loyalty 37
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [became Grinder (was Competitor) 33; became Competitor (was Grinder) 34; became Grinder (was Competitor) 39]
DECISION_LOG: [none yet]
```

## A retired player (cards are kept for the Archive)

### Maya Meyers  (K, retired)
```yaml
IDENTITY: [Maya Meyers, age 40, from Spokane WA; Junior-college transfer]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is overconfident (+0.72)
RATINGS: [overall 93, Franchise player]
  - power: 93  (sees herself at 97, overrating)
  - accuracy: 93  (sees herself at 100, overrating)
  - pressure thresholds: exile 58, contract 85, spotlight 71, loyalty 50
RECOGNITION: [respected; esteem 15.6; honors: All-League x9]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [retired 14; hof_ballot 17; hof_ballot 18; hof_ballot 19; hof_ballot 20; hof_ballot 21; hof_ballot 22]
DECISION_LOG: [none yet]
```

## Head coaches: the most esteemed ever, a typical coach and a weak one

### Coach Priya Devereux  (retired)  -  LEGEND
```yaml
IDENTITY: [Priya Devereux, age 61, from Toledo OH; Former star player turned coach]
SOUL (fixed): [+ Talent Developer, - Undisciplined]
PERSONALITY: [Developer] wants to turn raw talent into stars; fears wasting a prospect
  - allowed by her soul: Developer, Players' Coach, Steady Hand, Innovator; right now she is clear-eyed (+0.13)
RATINGS:
  - offense: 52  (sees herself at 52)   -> +0.02 points of margin
  - defense: 60  (sees herself at 61)   -> +0.04 points of margin
  - development: 60  (sees herself at 62)   -> +0.05 rating points per year to each young player
  - gamecraft: 53  (sees herself at 54)   (no on-field effect yet)
  - discipline: 33  (sees herself at 35, overrating)   (no on-field effect yet)
  - motivation: 49  (sees herself at 48)   (no on-field effect yet)
  - pressure thresholds: exile 50, contract 71, spotlight 29, loyalty 48
TRAJECTORY: [age 41: 49; age 44: 52; age 47: 52; age 50: 51; age 53: 50; age 56: 51; age 59: 50; peak 52 at 49; now 51]
RECOGNITION: [legend; esteem 22.5; honors: Coach of the Year, Champion]
RELATIONSHIPS: {Amelia Orozco (CEO): -1}
CAREER: [entered_coaching 17; interviewed 17; hired 17; retired 38]
DECISION_LOG: [11 earlier; 32: vetoed Amelia Sheridan's run scheme; 32: hired Junie Fennimore as defensive coordinator; 34: hired Kyra Pemberton as defensive coordinator; 35: vetoed Amelia Sheridan's run scheme; 35: vetoed Kyra Pemberton's coverage scheme; 35: hired Harlow Hightower as offensive coordinator]
```
### Coach Beatriz Nightingale  (Team 10)
```yaml
IDENTITY: [Beatriz Nightingale, age 59, from Buffalo NY; Coordinator who got her first shot]
SOUL (fixed): [+ Offensive Mastermind, - Undisciplined]
PERSONALITY: [Tactician] wants the cleverest scheme in the league; fears being out-schemed on a big night
  - allowed by her soul: Tactician, Innovator, Gambler, Steady Hand; right now she is clear-eyed (+0.20)
RATINGS:
  - offense: 60  (sees herself at 61)   -> +0.16 points of margin
  - defense: 51  (sees herself at 52)   -> -0.13 points of margin
  - development: 40  (sees herself at 42)   -> -0.10 rating points per year to each young player
  - gamecraft: 51  (sees herself at 53, overrating)   (no on-field effect yet)
  - discipline: 28  (sees herself at 29)   (no on-field effect yet)
  - motivation: 58  (sees herself at 61, overrating)   (no on-field effect yet)
  - pressure thresholds: exile 46, contract 70, spotlight 59, loyalty 36
TRAJECTORY: [age 50: 45; age 51: 44; age 52: 45; age 53: 46; age 54: 46; age 55: 46; age 56: 47; age 57: 46; age 58: 47; age 59: 48; peak 48 at 59; now 48]
RECOGNITION: [unknown; esteem 2.1; honors: none yet]
RELATIONSHIPS: {Hadley Hammond (CEO): +4}
CAREER: [hired 30; interviewed 37; interviewed 38; promoted 39; hired 39]
DECISION_LOG: [10 earlier; 39: was overruled by Juana Vandermeer on the blitz scheme; the unit plays balanced; 39: fired Freya Castellano as offensive coordinator; 39: fired Mabel Pettigrew as defensive coordinator; 39: hired Dorothea Sheridan as offensive coordinator; 39: hired Matilda Marchetti as defensive coordinator; 40: vetoed Matilda Marchetti's coverage scheme]
```
### Coach Isla Ibarra  (Team 19)
```yaml
IDENTITY: [Isla Ibarra, age 55, from Savannah GA; Former star player turned coach]
SOUL (fixed): [+ Taskmaster, - Predictable Offense]
PERSONALITY: [Survivor] wants another contract year; fears the CEO's phone call
  - allowed by her soul: Disciplinarian, Steady Hand, Survivor, Tactician; right now she is full of doubt (-0.82)
RATINGS:
  - offense: 26  (sees herself at 20, doubting)   -> -0.52 points of margin
  - defense: 34  (sees herself at 28, doubting)   -> -0.47 points of margin
  - development: 69  (sees herself at 60, doubting)   -> +0.14 rating points per year to each young player
  - gamecraft: 42  (sees herself at 38, doubting)   (no on-field effect yet)
  - discipline: 79  (sees herself at 72, doubting)   (no on-field effect yet)
  - motivation: 28  (sees herself at 22, doubting)   (no on-field effect yet)
  - pressure thresholds: exile 47, contract 94, spotlight 51, loyalty 57
TRAJECTORY: [age 36: 44; age 39: 47; age 42: 47; age 45: 47; age 48: 47; age 51: 46; age 54: 45; peak 48 at 40; now 46]
RECOGNITION: [known; esteem 7.4; honors: none yet]
RELATIONSHIPS: {Naomi Benavides (CEO): -5, Treasure Calloway (CEO): +4}
CAREER: [entered_coaching 20; hired 23; fired 27; hired 28]
DECISION_LOG: [7 earlier; 32: lost Echo Espinoza as defensive coordinator to a head-coaching job; 32: was exiled with her team; 33: lost Chiara Lockhart as offensive coordinator to a head-coaching job; 36: lost Selah Boateng as defensive coordinator to a head-coaching job; 38: vetoed Kirsten Clairmont's blitz scheme; 40: lost Alba Buchanan as offensive coordinator to a head-coaching job]
```

**A coach between jobs (she lives on and may be offered to a CEO again):**

### Coach Grace Clairmont  (between jobs)
```yaml
IDENTITY: [Grace Clairmont, age 53, from Miami FL; Small-college head coach promoted]
SOUL (fixed): [+ Clock Manager, - Undisciplined]
PERSONALITY: [Tactician] wants the cleverest scheme in the league; fears being out-schemed on a big night
  - allowed by her soul: Tactician, Gambler, Survivor, Steady Hand; right now she is clear-eyed (-0.10)
RATINGS:
  - offense: 67  (sees herself at 69)   -> +0.31 points of margin
  - defense: 69  (sees herself at 68)   -> +0.23 points of margin
  - development: 62  (sees herself at 61)   -> +0.07 rating points per year to each young player
  - gamecraft: 73  (sees herself at 72)   (no on-field effect yet)
  - discipline: 56  (sees herself at 54)   (no on-field effect yet)
  - motivation: 68  (sees herself at 65, doubting)   (no on-field effect yet)
  - pressure thresholds: exile 49, contract 48, spotlight 51, loyalty 53
TRAJECTORY: [age 34: 52; age 37: 54; age 40: 58; age 43: 60; age 46: 60; age 49: 63; age 52: 64; peak 66 at 53; now 66]
RECOGNITION: [respected; esteem 12.2; honors: Coach of the Year, Champion]
RELATIONSHIPS: {Greta Schaefer (CEO): -31, Ines Crawley (CEO): -1, Lourdes Ellison (gm): +0}
CAREER: [hired 21; fired 23; hired 23; fired 26; hired 29; fired 40]
DECISION_LOG: [15 earlier; 32: hired Andrea Kruger as defensive coordinator; 34: vetoed Jasmine Pemberton's pass scheme; 35: vetoed Andrea Kruger's coverage scheme; 37: lost Andrea Kruger as defensive coordinator to a head-coaching job; 40: was exiled with her team; 40: was fired by Greta Schaefer]
```

## Recognition: who the media called a legend, and the Hall of Fame

Nobody was made a legend. These are the Archive's own entries, in order:

```
year 3: legend recognized: Leona Kincaid (coach), esteem 27.7, 100% of outlets
year 3: legend recognized: Elsa Eberhardt (gm), esteem 19.5, 100% of outlets
year 3: legend recognized: Aiko Vasquez (owner), esteem 23.2, 61% of outlets
year 9: legend recognized: Lupe Pinkerton (player), esteem 25.9, 60% of outlets
year 12: legend contested: Emilia Jimenez (coach), esteem 20.8, 35% of outlets
year 12: legend contested: Elsa Eberhardt (gm), esteem 16.1, 33% of outlets
year 13: legend contested: Petra Sutherland (owner), esteem 20.2, 50% of outlets
year 13: legend contested: Leona Kincaid (coach), esteem 20.8, 38% of outlets
year 13: legend contested: Aiko Vasquez (owner), esteem 18.8, 56% of outlets
year 14: legend contested: Iris Buchanan (owner), esteem 19.6, 49% of outlets
year 14: legend contested: Emilia Jimenez (coach), esteem 21.9, 31% of outlets
year 16: legend recognized: Emilia Jimenez (coach), esteem 21.9, 75% of outlets
```

**The Hall of Fame so far:**

| Year | Kind | Name | Esteem | Vote | Honors |
|---|---|---|---|---|---|
| 15 | owner | Aiko Vasquez | 18.8 | 80% | Champion x3 |
| 15 | player | Lupe Pinkerton | 28.4 | 93% | All-League x8, Player of the Year x4, Champion x1 |
| 16 | coach | Emilia Jimenez | 21.9 | 86% | Champion x1 |
| 17 | owner | Iris Buchanan | 19.6 | 79% | Champion x1 |
| 24 | owner | Georgia Keller | 21.9 | 93% | Champion x2 |
| 25 | player | Mabel Herrera | 26.0 | 93% | All-League x10, Champion x1, Player of the Year x2 |
| 27 | gm | Daniela Zamora | 21.4 | 99% | Executive of the Year x1, Champion x3 |
| 28 | gm | Sabine Pruitt | 15.3 | 81% | Champion x2 |
| 28 | player | Malia Abara | 36.5 | 100% | All-League x7, Player of the Year x6, Champion x1 |
| 34 | coach | Paloma Yoder | 21.4 | 86% | Champion x3 |
| 40 | owner | Kimi Waller | 18.6 | 76% | Champion x4 |

**The most esteemed player:**

### Xiomara Mangum  (WR, Team 03)
```yaml
IDENTITY: [Xiomara Mangum, age 33, from Omaha NE; International pathway]
SOUL (fixed): [+ Burner, - Drop-Prone]  temperament family: flash
PERSONALITY: [Showman] wants the spotlight and a signature moment; fears being ignored by the media
  - allowed by her soul: Showman, Free Spirit, Competitor, Mercenary; right now she is overconfident (+0.71)
RATINGS: [overall 87, Franchise player]
  - route: 89  (sees herself at 94, overrating)
  - hands: 79  (sees herself at 86, overrating)
  - speed: 93  (sees herself at 97, overrating)
  - pressure thresholds: exile 66, contract 52, spotlight 49, loyalty 72
RECOGNITION: [legend; esteem 38.0; honors: All-League x9, Champion, Player of the Year x6]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 29 (pick 1); became Free Spirit (was Showman) 31; became Showman (was Free Spirit) 37]
DECISION_LOG: [none yet]
```

## A CEO, a GM, and the Archive's first entries

### CEO Astrid Alderman  (Team 25, CEO)
```yaml
IDENTITY: [Astrid Alderman, age 58, from Birmingham AL; Real-estate magnate]
SOUL (fixed): [+ Shrewd Operator, - Despised]
PERSONALITY: [Penny-Pincher] wants a profitable franchise; fears a league subsidy
  - allowed by her soul: Penny-Pincher, Opportunist, Legacy Builder, Patient Steward; right now she is clear-eyed (-0.11)
RATINGS:
  - patience: 39  (sees herself at 37)
  - ambition: 43  (sees herself at 43)
  - involvement: 54  (sees herself at 55)
  - popularity: 30  (sees herself at 27, doubting)
  - business: 54  (sees herself at 52)
  - fan approval right now: 47%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 5, media 57, losing 40, subsidy 46
METERS (hers alone; they end with her tenure):
  - Fan Rapport: 59  (somewhere in between)
  - Standing Among CEOs: 50  (somewhere in between)
  - Legacy: 24  (she will be forgotten)
PLEDGE: [standard] the share of a profit she puts back into the club
TRAJECTORY: [age 43: 43; age 45: 44; age 47: 43; age 49: 44; age 51: 44; age 53: 43; age 55: 43; age 57: 43; peak 44 at 45; now 44]
RECOGNITION: [known; esteem 3.8; honors: none yet]
RELATIONSHIPS: {Catalina Keller (gm): -16, Catalina Alvarado (coach): -11, Elise Holmgren (coach): -10, Odalys Macalister (gm): -10, Saoirse Redfern (coach): -1, Team 25 fans: +31}
CAREER: [elected 24]
DECISION_LOG: [20 earlier; 37: survived a recall vote; 38: pledged the standard share of profit to the club; 39: pledged the standard share of profit to the club; 39: blamed Catalina Keller for the exile; 39: survived a recall vote; 40: pledged the standard share of profit to the club]
```
### CEO Priya Mangum  (Team 20, recalled)
```yaml
IDENTITY: [Priya Mangum, age 50, from Mobile AL; Tech founder]
SOUL (fixed): [+ Hands-On Leader, - Despised]
PERSONALITY: [Meddler] wants a hand in every decision; fears being irrelevant
  - allowed by her soul: Meddler, Legacy Builder, Glory Hunter, Patient Steward; right now she is overconfident (+0.42)
RATINGS:
  - patience: 52  (sees herself at 55, overrating)
  - ambition: 50  (sees herself at 55, overrating)
  - involvement: 74  (sees herself at 77, overrating)
  - popularity: 31  (sees herself at 34, overrating)
  - business: 44  (sees herself at 48, overrating)
  - fan approval right now: 38%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 57, media 52, losing 46, subsidy 28
METERS (hers alone; they end with her tenure):
  - Fan Rapport: 47  (somewhere in between)
  - Standing Among CEOs: 50  (somewhere in between)
  - Legacy: 8  (she will be forgotten)
PLEDGE: [standard] the share of a profit she puts back into the club
TRAJECTORY: [age 50: 50; peak 50 at 50; now 50]
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {Team 20 fans: -43, Cassidy Delgado (gm): -15, Juana Vandermeer (coach): -5}
CAREER: [elected 39; recalled 40]
DECISION_LOG: [40: pledged the standard share of profit to the club; 40: blamed Cassidy Delgado for the exile; 40: was recalled]
```
### GM Paloma Espinoza  (Team 04, gm)
```yaml
IDENTITY: [Paloma Espinoza, age 52, from Juneau AK; Coach's trusted lieutenant]
SOUL (fixed): [+ Closer, - Cap Casualty]
PERSONALITY: [Dealmaker] wants the best contract in every negotiation; fears being outmaneuvered
  - allowed by her soul: Dealmaker, Cold Realist, Loyal Lieutenant, Planner; right now she is overconfident (+1.00)
RATINGS:
  - scouting: 79  (sees herself at 88, overrating)   -> +0.89 rating points on her team's rookie each year
  - negotiation: 83  (sees herself at 92, overrating)   -> 20% fewer contract expiries
  - evaluation: 81  (sees herself at 88, overrating)   (no on-field effect yet)
  - trades: 57  (sees herself at 65, overrating)   (no on-field effect yet)
  - cap_sense: 53  (sees herself at 63, overrating)   (no on-field effect yet)
  - pressure thresholds: exile 38, contract 49, spotlight 46, loyalty 47
TRAJECTORY: [age 50: 71; age 51: 71; age 52: 71; peak 71 at 50; now 71]
RECOGNITION: [unknown; esteem 0.6; honors: none yet]
RELATIONSHIPS: {Nina Pinkerton (CEO): -1}
CAREER: [hired 37]
DECISION_LOG: [38: was exiled with her team]
```
**A recall vote as the Archive logs it:**

```
year: 40
event: recall_vote
team: 43
trigger: approval
approval: 0.291
recall_share: 0.614
result: recalled
owner: Naomi Trevino
replacement: Celeste Morrow
candidates: ['Josie Alderman', 'Matilda Christensen', 'Saoirse Flanagan', 'Zuri Jovanovic', 'Celeste Morrow']
capital: 0.396
```


## A fanbase and the press that covers it

### Fanbase of Team 05  (Entitled)
```yaml
IDENTITY: [Team 05 fans; market size 51 of 100; the franchise's permanent card, it outlives every CEO]
PERSONALITY: [Entitled] wants a title every year; fears being ignored; picks CEOs who are strong on ambition
ARCHETYPES: [+ Demanding, - Indifferent]
RATINGS:
  - loyalty: 50
  - expectations: 81   (born at 66; drifts with results, within +/-15)
  - passion: 37
  - volatility: 44
  - media_trust: 45
  - approval of the CEO: 62%
  - Fan Capital: 0.60  (recall immunity; worth 2.9 points on a recall vote)
  - what the press did to approval last season: +1.0 points
  - pressure thresholds: exile 31, losing 43, scandal 53, spotlight 67
METERS (this franchise's own; they rise and fall with what happens, and their resting level drifts):
  - Grudge: 45  (somewhere in between; resting level 45, since year 0)
  - Bandwagon: 39  (only the faithful come; resting level 29, since year 0)
  - Next Generation: 34  (the young stay home; resting level 32, since year 0)
  - Outrage: 46  (somewhere in between; resting level 52, since year 2)
  - Homecoming Pull: 70  (the exile healed into pride; resting level 68, since year 3)
BOYCOTT: [off]
MEMORIES (fading):
  - 33: the club was sent into exile  (remembered 55%)
  - 34: the club came home from exile  (remembered 48%)
  - 33: the fans began to boycott  (remembered 38%)
  - 23: the club was sent into exile  (remembered 23%)
  - 31: Mabel Danforth left the club  (remembered 23%)
  - the boycott ended with a new CEO  (remembered 22%)
SPENDING_ASK: [fair] what the fans asked of the CEO's investment this year
RELATIONSHIPS: {Liesel Novak (CEO): -62, Adriana Christensen (CEO): -42, Juana Marlowe (CEO): -28, Greta Amundsen (CEO): -28, Fiona Lazarus (CEO): +20}
DECISION_LOG: [46 earlier; 35: asked for the fair level of investment; 36: asked for the fair level of investment; 37: asked for the fair level of investment; 38: asked for the fair level of investment; 39: asked for the fair level of investment; 40: asked for the fair level of investment]
```
### Fanbase of Team 24  (Front-Runners)
```yaml
IDENTITY: [Team 24 fans; market size 69 of 100; the franchise's permanent card, it outlives every CEO]
PERSONALITY: [Front-Runners] wants winners; fears a long losing stretch; picks CEOs who are strong on ambition
ARCHETYPES: [+ Demanding, - Distrust the Press]
RATINGS:
  - loyalty: 21
  - expectations: 71   (born at 86; drifts with results, within +/-15)
  - passion: 60
  - volatility: 52
  - media_trust: 18
  - approval of the CEO: 45%
  - Fan Capital: 0.35  (recall immunity; worth 0.0 points on a recall vote)
  - what the press did to approval last season: -1.4 points
  - pressure thresholds: exile 48, losing 48, scandal 56, spotlight 60
METERS (this franchise's own; they rise and fall with what happens, and their resting level drifts):
  - Memory Keepers: 31  (last year is ancient history; resting level 31, since year 0)
  - Outrage: 71  (the phones are ringing; resting level 68, since year 0)
  - Wallet Mood: 68  (they open their wallets gladly; resting level 70, since year 0)
  - Grudge: 85  (they have not forgiven the league; resting level 81, since year 1)
  - Civic Pride: 16  (the team is just a tenant; resting level 15, since year 23)
BOYCOTT: [off]
MEMORIES (fading):
  - 39: the club was sent into exile  (remembered 90%)
  - 40: the club came home from exile  (remembered 80%)
  - 37: the club was sent into exile  (remembered 73%)
  - 38: the club came home from exile  (remembered 65%)
  - 39: the fans began to boycott  (remembered 63%)
  - 38: the fans began to boycott  (remembered 56%)
SPENDING_ASK: [fair] what the fans asked of the CEO's investment this year
RELATIONSHIPS: {Xiomara Underhill (CEO): -46, Mila Ellison (CEO): -41, Eva Pappas (CEO): -31, Dominique Quillen (CEO): -29, Carys Iverson (CEO): -29, Luna Madsen (CEO): -29, Rachelle Crawley (CEO): -29, Andrea Briggs (CEO): +28}
DECISION_LOG: [50 earlier; 37: kept the CEO; 38: asked for the fair level of investment; 38: voted to recall the CEO; 39: asked for the fair level of investment; 39: voted to recall the CEO; 40: asked for the fair level of investment]
```
### Fanbase of Team 30  (Gloomy Realists)
```yaml
IDENTITY: [Team 30 fans; market size 54 of 100; the franchise's permanent card, it outlives every CEO]
PERSONALITY: [Gloomy Realists] wants honesty; fears being fooled again; picks CEOs who are strong on business
ARCHETYPES: [+ Demanding, - Indifferent]
RATINGS:
  - loyalty: 60
  - expectations: 85   (born at 70; drifts with results, within +/-15)
  - passion: 26
  - volatility: 28
  - media_trust: 32
  - approval of the CEO: 68%
  - Fan Capital: 0.70  (recall immunity; worth 5.9 points on a recall vote)
  - what the press did to approval last season: +1.3 points
  - pressure thresholds: exile 54, losing 36, scandal 29, spotlight 29
METERS (this franchise's own; they rise and fall with what happens, and their resting level drifts):
  - Civic Pride: 37  (the team is just a tenant; resting level 36, since year 0)
  - Grudge: 29  (old wounds have healed; resting level 30, since year 0)
  - Outrage: 27  (all calm; resting level 39, since year 0)
  - Homecoming Pull: 55  (somewhere in between; resting level 54, since year 5)
BOYCOTT: [off]
MEMORIES (fading):
  - 37: the championship  (remembered 77%)
  - 30: the club was sent into exile  (remembered 42%)
  - 31: the club came home from exile  (remembered 37%)
  - 28: the club was sent into exile  (remembered 35%)
  - 31: the fans began to boycott  (remembered 32%)
  - 29: the club came home from exile  (remembered 31%)
SPENDING_ASK: [fair] what the fans asked of the CEO's investment this year
RELATIONSHIPS: {Aiko Vasquez (CEO): -42, Olive Dunmore (CEO): -35, Carmen Contreras (CEO): -26, Elise Amundsen (CEO): -26, Andrea Eastwood (CEO): -26, Ayana Caldwell (CEO): +32}
DECISION_LOG: [47 earlier; 36: asked for the fair level of investment; 37: asked for the fair level of investment; 37: kept the CEO; 38: asked for the fair level of investment; 39: asked for the fair level of investment; 40: asked for the fair level of investment]
```
The franchise's permanent card, with its own meters, memories and any boycott (the club with the longest memory):

### Fanbase of Team 04  (Front-Runners)
```yaml
IDENTITY: [Team 04 fans; market size 45 of 100; the franchise's permanent card, it outlives every CEO]
PERSONALITY: [Front-Runners] wants winners; fears a long losing stretch; picks CEOs who are strong on ambition
ARCHETYPES: [+ Mood Swings, - Indifferent]
RATINGS:
  - loyalty: 54
  - expectations: 56   (born at 60; drifts with results, within +/-15)
  - passion: 27
  - volatility: 74
  - media_trust: 70
  - approval of the CEO: 45%
  - Fan Capital: 0.51  (recall immunity; worth 0.2 points on a recall vote)
  - what the press did to approval last season: -0.6 points
  - pressure thresholds: exile 47, losing 20, scandal 51, spotlight 29
METERS (this franchise's own; they rise and fall with what happens, and their resting level drifts):
  - Grudge: 78  (they have not forgiven the league; resting level 72, since year 0)
  - Homecoming Pull: 92  (the exile healed into pride; resting level 80, since year 0)
  - Tailgate Spirit: 47  (somewhere in between; resting level 47, since year 0)
  - Kinship With the Roster: 64  (they love their players; resting level 64, since year 4)
  - Outrage: 77  (the phones are ringing; resting level 75, since year 11)
BOYCOTT: [off]
MEMORIES (fading):
  - 38: the club was sent into exile  (remembered 84%)
  - 39: the club came home from exile  (remembered 73%)
  - 40: the fans began to boycott  (remembered 70%)
  - 35: the club was sent into exile  (remembered 65%)
  - 38: the fans began to boycott  (remembered 59%)
  - 36: the club came home from exile  (remembered 57%)
SPENDING_ASK: [fair] what the fans asked of the CEO's investment this year
RELATIONSHIPS: {Hazel Kirkland (CEO): -42, Daniela Jefferson (CEO): -28, Bridget Herrera (CEO): -26, Katya Madsen (CEO): -21, Nina Pinkerton (CEO): +10}
DECISION_LOG: [47 earlier; 36: asked for the fair level of investment; 37: asked for the fair level of investment; 38: asked for the fair level of investment; 38: kept the CEO; 39: asked for the fair level of investment; 40: asked for the fair level of investment]
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

### CEO Astrid Alderman  (Team 25, CEO)
```yaml
IDENTITY: [Astrid Alderman, age 58, from Birmingham AL; Real-estate magnate]
SOUL (fixed): [+ Shrewd Operator, - Despised]
PERSONALITY: [Penny-Pincher] wants a profitable franchise; fears a league subsidy
  - allowed by her soul: Penny-Pincher, Opportunist, Legacy Builder, Patient Steward; right now she is clear-eyed (-0.11)
RATINGS:
  - patience: 39  (sees herself at 37)
  - ambition: 43  (sees herself at 43)
  - involvement: 54  (sees herself at 55)
  - popularity: 30  (sees herself at 27, doubting)
  - business: 54  (sees herself at 52)
  - fan approval right now: 47%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 5, media 57, losing 40, subsidy 46
METERS (hers alone; they end with her tenure):
  - Fan Rapport: 59  (somewhere in between)
  - Standing Among CEOs: 50  (somewhere in between)
  - Legacy: 24  (she will be forgotten)
PLEDGE: [standard] the share of a profit she puts back into the club
TRAJECTORY: [age 43: 43; age 45: 44; age 47: 43; age 49: 44; age 51: 44; age 53: 43; age 55: 43; age 57: 43; peak 44 at 45; now 44]
RECOGNITION: [known; esteem 3.8; honors: none yet]
RELATIONSHIPS: {Catalina Keller (gm): -16, Catalina Alvarado (coach): -11, Elise Holmgren (coach): -10, Odalys Macalister (gm): -10, Saoirse Redfern (coach): -1, Team 25 fans: +31}
CAREER: [elected 24]
DECISION_LOG: [20 earlier; 37: survived a recall vote; 38: pledged the standard share of profit to the club; 39: pledged the standard share of profit to the club; 39: blamed Catalina Keller for the exile; 39: survived a recall vote; 40: pledged the standard share of profit to the club]
```

## Scenes as the Archive records them

Each firing, recall vote and exile determination is a scene: every party gives its own claim, and the evidence section says, from the engine's own numbers, which claims hold. The scenes never change an outcome (the check script proves a league plays out identically with them on or off); they explain it, and they move relationships and decision logs.

**An exile determination**

```
EVENT 40-exile_determination-43-1  (Team 43; exile determination; finished fifth in the division)
├── Owner claims: Naomi Trevino (Glory Hunter): "Fifth in the division, and I will say who is to blame: Aaliyah Dubois. The roster rated 38% and they won 33%."  [not supported by the record]
├── Coach claims: Aaliyah Dubois (Tactician): "I was handed a roster 1.6 deviations below average and the schedule did the rest."  [supported, but overstated]
├── GM claims: Lola Akana (Dealmaker): "The roster was 5 of 5 in this division on paper. The record, 33%, was 5% below what it should have been."  [not supported by the record]
├── The fans claim: Team 43 fans: "They finished 33%. We wanted a good time and we feared boredom; that is what we got."  [supported by the record]
├── Press claims: Team 43 Gazette (Homer): "They finished 33%. The town is watching closely, and that is how we are telling it."  [supported by the record]
└── Evidence supports: Exile followed a thin roster.  (record 33%, roster predicts 38%, roster -1.0 deviations from average)
    Outcome: Team 43 is exiled for next season
```

**A firing the record backs**

```
EVENT 40-firing-38-1  (Team 38; firing; CEO fired the coach (results))
├── Owner claims: Esme Sandoval (Legacy Builder): "22% is not what I bought this team for. I gave her 2 seasons; I was patient."  [supported by the record]
├── Coach claims: Mila Underhill (Players' Coach): "We were up from 0% to 22%. You do not fire a team that is climbing."  [supported by the record]
├── GM claims: Ines Salazar (Planner): "The roster was fine. The record was 22%, against 52% on paper."  [supported by the record]
├── The fans claim: Team 38 fans: "We stand by our own, and we have 37 points of goodwill banked. This town wanted one real playoff run."  [not supported by the record]
├── Press claims: Team 38 Sideline (Gossip): "They finished 22%. The town is watching closely, and that is how we are telling it."  [supported by the record]
└── Evidence supports: The firing is backed by the record, and the roster does not excuse it: the team won well under what it was built to win.  (record 22%, roster predicts 52%, roster +0.4 deviations from average)
    Outcome: Mila Underhill fired; replaced by a new coach
```

**A harsh firing (the roster explains the record)**

```
EVENT 40-firing-43-1  (Team 43; firing; CEO fired the coach (results))
├── Owner claims: Celeste Morrow (Meddler): "33% is not what I bought this team for. I gave her 3 seasons; I had no patience left."  [supported by the record]
├── Coach claims: Aaliyah Dubois (Tactician): "You gave me a roster 2.0 deviations below the league's average and expected a contender."  [supported, but overstated]
├── GM claims: Lola Akana (Dealmaker): "The roster was fine. The record was 33%, against 38% on paper."  [not supported by the record]
├── The fans claim: Team 43 fans: "They finished 33%. We wanted a good time and we feared boredom; that is what we got."  [supported by the record]
├── Press claims: Team 43 Gazette (Homer): "They finished 33%. The town is watching closely, and that is how we are telling it."  [supported by the record]
└── Evidence supports: A harsh firing: the record was poor (33%), but the roster explains it; the team won about what it was built to win.  (record 33%, roster predicts 38%, roster -1.0 deviations from average)
    Outcome: Aaliyah Dubois fired; replaced by a new coach
```

**A new CEO's sweep**

```
EVENT 40-firing-11-2  (Team 11; firing; CEO fired the gm (new CEO cleaned house))
├── Owner claims: Greta Schaefer (Penny-Pincher): "New CEO, new staff. I wanted a profitable franchise and I wasn't going to ask Lourdes Ellison for it."  [supported by the record]
├── GM claims: Lourdes Ellison (Cold Realist): "I built the roster and she lost games the roster should have won: 39% on a team that rates 52%."  [supported by the record]
├── Coach claims: Grace Clairmont (Tactician): "I coached what I was handed, a roster 0.3 deviations above average."  [not supported by the record]
├── The fans claim: Team 11 fans: "They finished 39%. We wanted a title every year and we feared being ignored; that is what we got."  [supported by the record]
├── Press claims: Team 11 Gazette (Hype Machine): "They finished 39%. The town is watching closely, and that is how we are telling it."  [supported by the record]
└── Evidence supports: A sweep: the new CEO cleared the staff on arrival, whatever the record (39% against 52% on paper).  (record 39%, roster predicts 52%, roster +0.3 deviations from average)
    Outcome: Lourdes Ellison fired; replaced by a new gm
```

**A recall vote that removes a CEO**

```
EVENT 40-recall_vote-43-1  (Team 43; recall vote; vote triggered by approval)
├── Owner claims: Naomi Trevino (Glory Hunter): "I thought we were at 36%. The team lost, and the fans are blaming the person they can vote on."  [supported by the record]
├── The fans claim: Team 43 fans: "They finished 33%. We wanted a good time and we feared boredom; that is what we got." We wanted a CEO strong on involvement and we chose Celeste Morrow.  [supported by the record]
├── Press claims: Team 43 Gazette (Homer): "They finished 33%. The town is watching closely, and that is how we are telling it."  [supported by the record]
├── New CEO claims: Celeste Morrow (Meddler): "Five of us stood. The fans wanted strength on involvement and picked me. I want a hand in every decision."  [not supported by the record]
└── Evidence supports: 61.4% voted to recall (a majority of the 1,000,000 fans is needed): recalled.  (record 33%, roster predicts 38%, roster -1.0 deviations from average)
    Outcome: Naomi Trevino recalled; Celeste Morrow elected from 5 candidates
```

**A recall vote the CEO survives**

```
EVENT 40-recall_vote-48-1  (Team 48; recall vote; vote triggered by rotation)
├── Owner claims: Willa Merrick (Meddler): "I told you we were at 64%. The fans know what I stand for: a hand in every decision."  [supported by the record]
├── The fans claim: Team 48 fans: "They finished 61%. We wanted honesty and we feared being fooled again; we have no complaint about the record, but we are watching."  [not supported by the record]
├── Press claims: Team 48 Insider (Contrarian): "They finished 61%. The town is behind the team, and that is how we are telling it."  [supported by the record]
└── Evidence supports: 25.4% voted to recall (a majority of the 1,000,000 fans is needed): the CEO survives.  (record 61%, roster predicts 56%, roster +0.7 deviations from average)
    Outcome: Willa Merrick survives
```


## What an agent is shown, and what the log keeps

Choices go through Decision Points. An agent is shown its own card, what it perceives (candidates' ratings as the CEO sees them, with blind spots) and the legal options, and answers with one option id. The guard applies the choice (or the autopilot's choice if the answer is invalid or late) and logs it. Below: the two decisions a CEO faces, as an agent receives them, and the log line.

**A CEO's staff review, as an agent receives it:**

```json
{
 "top_priority": {
  "goal": "Win the Diamond Coronation. It is the first priority of every role in the league; everything else on this card is a means to it.",
  "your_team": "Team 01",
  "strength_rank": 36,
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
   "popularity": 57.4,
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
  "record_this_season": 0.5,
  "record_last_season": null,
  "exiled_this_year": false,
  "fan_approval_of_you": 0.665,
  "facing_a_recall_vote_this_year": true,
  "you_are_a_new_ceo": false,
  "press_effect_on_fans": 0.001,
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
   "pressure_on_her": 0.0,
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
   "pressure_on_her": 0.0,
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
  "name": "Isla Alvarado",
  "trait": "Showwoman",
  "wants": "spectacle and headlines",
  "fears": "boredom",
  "ratings": {
   "patience": 25.2,
   "ambition": 62.9,
   "involvement": 58.5,
   "popularity": 64.2,
   "business": 44.4
  },
  "pressure": {
   "recall": 65,
   "media": 32,
   "losing": 34,
   "subsidy": 53
  },
  "age": 51,
  "reputation": "unknown",
  "honors": {},
  "career_summary": {
   "jobs": 1,
   "fired": 0,
   "recalled": 0
  },
  "recent_decisions": [],
  "notes_to_self": []
 },
 "context": {
  "team_needs": "a head coach"
 },
 "options": [
  {
   "id": "candidate_0",
   "label": "Hire Laila Adeyemi",
   "tags": {
    "between_jobs": true
   },
   "view": {
    "name": "Laila Adeyemi",
    "age": 51,
    "path": "Coordinator who got her first shot",
    "trait": "Steady Hand",
    "perceived": {
     "offense": 63.0,
     "defense": 37.0,
     "development": 59.0,
     "gamecraft": 57.0,
     "discipline": 55.0,
     "motivation": 71.0
    },
    "reputation": "unknown",
    "honors": {},
    "previous_jobs": 0
   }
  },
  {
   "id": "candidate_1",
   "label": "Hire Junie Abara",
   "tags": {
    "between_jobs": true
   },
   "view": {
    "name": "Junie Abara",
    "age": 45,
    "path": "Came over from another league",
    "trait": "Tactician",
    "perceived": {
     "offense": 52.0,
     "defense": 46.0,
     "development": 27.0,
     "gamecraft": 28.0,
     "discipline": 53.0,
     "motivation": 52.0
    },
    "reputation": "unknown",
    "honors": {},
    "previous_jobs": 0
   }
  },
  {
   "id": "candidate_2",
   "label": "Hire Eliana Meyers",
   "tags": {
    "between_jobs": true
   },
   "view": {
    "name": "Eliana Meyers",
    "age": 55,
    "path": "Former star player turned coach",
    "trait": "Tactician",
    "perceived": {
     "offense": 59.0,
     "defense": 47.0,
     "development": 68.0,
     "gamecraft": 63.0,
     "discipline": 27.0,
     "motivation": 47.0
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

**Core personalities (all rostered players):** Diplomat 548, Competitor 478, Grinder 438, Perfectionist 343, Showman 238, Quiet Leader 182, Free Spirit 157, Hothead 96, Mercenary 42, Loyalist 22

**Most common positive archetypes:** Well-Rounded 728, Shutdown Corner 114, Road Grader 113, Edge Terror 111, Pass-Pro Wall 109, Ballhawk 108, Run Stuffer 96, Burner 87

**Coach effect across the 48 teams:** average -0.07, spread (sd) 0.39, best +0.81, worst -0.98 points of expected margin. For scale, team talent has a spread of about 3 to 4 points.

**Personality shifts:** 3154 of 31026 players have changed personality at least once in 40 seasons.

**Standing in the media's eyes** (everyone who ever lived, by what the media calls her now): known 243, respected 112, star 36, Hall of Famer 11, legend 2. 11 are in the Hall of Fame.

**Fan cultures:** Die-Hards 13, Entitled 11, Party Crowd 9, Gloomy Realists 7, Long-Suffering 5, Front-Runners 3

**Fan Capital:** average 0.53, from 0.35 to 0.70; the most it can buffer a recall vote is 15 points.

**Fan meters:** every fanbase has 3 from birth and can awaken up to 5; now [(5, 41), (4, 7)] (meters per club, clubs). Most common: Grudge 34, Outrage 34, Civic Pride 27, Homecoming Pull 23.

**Fan memories** held now: exile 179, return 154, boycott 76, boycott_end 32, star_left 31, title 25, drought 6. **Boycotts** on now: 0 clubs; 76 begun within the memory window. A full boycott costs 40% of local revenue.

**The press on approval, last season:** average 1.4 points either way, largest 3.3 (the cap is 3 before market size and trust).

**Outlets:** 52 (4 national, one local beat per team); a national outlet tells a team's year as it was, a local outlet frames it toward its fans' mood by at most 25 points of tone.

**CEO choices on the record:** ceo_boycott concede 19, ceo_boycott hold 19, ceo_pledge standard 1877. CEOs who stepped aside under a boycott: 0.

**Scenes:** 1122 in 40 seasons ([('recall_vote', 559), ('exile_determination', 320), ('firing', 243)]). Firings by ruling: fair 166, sweep 49, harsh 22, unfounded 6.

**Recall votes:** 559 in 40 seasons (14.0 a year); 191 CEOs recalled (4.8 a year), 34% of votes. CEOs retire on their own too: 48 so far.

**Firings:** 157 coaches and 86 GMs fired in 40 seasons.

**Coaches so far:** 715 cards created (head coaches and coordinators) and 531 retired in 40 seasons; 40 coaches and 14 GMs are between jobs right now.

**The coaching pool:** 715 coach cards in 40 seasons (head coaches and coordinators are the same kind of card), 40 between jobs now (the creator tops the pool up only when it falls under 40). 564 have worked as a coordinator, 166 coordinators were hired away as head coaches, and 233 coordinators had been head coaches before.

**Coordinators:** schemes proposed: coverage 796, blitz 791, run 785, pass 757, balanced 711; the head coach vetoed 690 of 3129. 450 coordinators fired by their head coaches.

```
PETRA JARRETT  -  offensive coordinator, Team 01  -  age 53, from Baton Rouge LA
  PLAYCALLING 59   VISION (gamecraft) 57   heat -0.18   years here 3
  Her lift to her unit: +0.11 points of margin (the average coordinator is zero).
  Career: 36 entered_coaching; 37 interviewed (coach); 37 hired (offensive coordinator)
  Lately: 39 was overruled by Georgia Espinoza on the pass scheme; the unit plays balanced; 40 proposed the pass scheme; 40 was overruled by Georgia Espinoza on the pass scheme; the unit plays balanced

BRYN EBERHARDT  -  defensive coordinator, Team 01  -  age 57, from Denver CO
  PLAYCALLING 72   VISION (gamecraft) 64   heat -0.22   years here 3
  Her lift to her unit: +0.31 points of margin (the average coordinator is zero).
  Career: 33 entered_coaching; 33 hired (defensive coordinator); 36 fired (defensive coordinator); 37 hired (defensive coordinator)
  Lately: 38 proposed the blitz scheme; 39 proposed the blitz scheme; 40 proposed the coverage scheme
```

**GM plan choices on the record:** gm_cap_plan balanced 1920, gm_draft_focus needs 1920 (the autopilot keeps the old rule).

**Players with cards:** 3244 active or unsigned, 28482 retired.
