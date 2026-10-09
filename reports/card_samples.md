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

### Ingrid Alvarado II  (QB, Team 29)
```yaml
IDENTITY: [Ingrid Alvarado II, age 27, from Kansas City MO; Walk-on turned starter]
SOUL (fixed): [+ Cannon, - Reads Late]  temperament family: power
PERSONALITY: [Hothead] wants to settle every score on the field; fears being embarrassed in public
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is clear-eyed (+0.22)
RATINGS: [overall 97, Franchise player]
  - accuracy: 97  (sees herself at 97)
  - arm: 100  (sees herself at 103, overrating)
  - awareness: 96  (sees herself at 98)
  - pressure thresholds: exile 37, contract 71, spotlight 59, loyalty 45
RECOGNITION: [star; esteem 18.4; honors: All-League x3, Player of the Year x3]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 35 (pick 1)]
DECISION_LOG: [none yet]
```
### Iris Winslow II  (WR, Team 18)
```yaml
IDENTITY: [Iris Winslow II, age 23, from Salt Lake City UT; Junior-college transfer]
SOUL (fixed): [+ Glue Hands, - Rough Routes]  temperament family: precision
PERSONALITY: [Perfectionist] wants flawless execution; fears the one mistake everyone remembers
  - allowed by her soul: Perfectionist, Quiet Leader, Grinder, Diplomat; right now she is clear-eyed (-0.06)
RATINGS: [overall 87, Franchise player]
  - route: 81  (sees herself at 78, doubting)
  - hands: 94  (sees herself at 94)
  - speed: 86  (sees herself at 88)
  - pressure thresholds: exile 34, contract 51, spotlight 64, loyalty 26
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 39 (pick 1)]
DECISION_LOG: [none yet]
```
### Priya Burkhart II  (OL, Team 08)
```yaml
IDENTITY: [Priya Burkhart II, age 23, from Toledo OH; Power-conference star]
SOUL (fixed): [+ Road Grader, - Turnstile]  temperament family: power
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is overconfident (+0.41)
RATINGS: [overall 86, Franchise player]
  - pass_block: 80  (sees herself at 83, overrating)
  - run_block: 91  (sees herself at 95, overrating)
  - pressure thresholds: exile 45, contract 52, spotlight 63, loyalty 63
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 40 (pick 3)]
DECISION_LOG: [none yet]
```
### Ananya Meyers II  (DL, Team 19)
```yaml
IDENTITY: [Ananya Meyers II, age 26, from Lafayette LA; Power-conference star]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is clear-eyed (+0.06)
RATINGS: [overall 95, Franchise player]
  - pass_rush: 98  (sees herself at 99)
  - run_stop: 92  (sees herself at 92)
  - pressure thresholds: exile 78, contract 31, spotlight 70, loyalty 73
RECOGNITION: [respected; esteem 9.1; honors: All-League x4]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 36 (pick 5)]
DECISION_LOG: [none yet]
```
### Rafaela Choi II  (CB, Team 07)
```yaml
IDENTITY: [Rafaela Choi II, age 25, from Indianapolis IN; Junior-college transfer]
SOUL (fixed): [+ Ballhawk, - Avoids Contact]  temperament family: flash
PERSONALITY: [Showman] wants the spotlight and a signature moment; fears being ignored by the media
  - allowed by her soul: Showman, Free Spirit, Competitor, Mercenary; right now she is clear-eyed (+0.22)
RATINGS: [overall 92, Franchise player]
  - coverage: 91  (sees herself at 91)
  - ball_skills: 99  (sees herself at 102, overrating)
  - tackling: 83  (sees herself at 85, overrating)
  - pressure thresholds: exile 54, contract 43, spotlight 75, loyalty 58
RECOGNITION: [known; esteem 4.8; honors: All-League x2]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 37 (pick 1)]
DECISION_LOG: [none yet]
```
### Alicia Caldwell  (K, Team 40)
```yaml
IDENTITY: [Alicia Caldwell, age 35, from Omaha NE; Came up through the academy system]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Grinder] wants to earn every inch; fears being handed nothing and losing it anyway
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is full of doubt (-1.00)
RATINGS: [overall 88, Franchise player]
  - power: 89  (sees herself at 77, doubting)
  - accuracy: 87  (sees herself at 72, doubting)
  - pressure thresholds: exile 48, contract 53, spotlight 36, loyalty 82
RECOGNITION: [unknown; esteem 1.1; honors: Champion]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```

## A young rookie and a veteran

### Honor Radcliffe II  (DL, Team 33)
```yaml
IDENTITY: [Honor Radcliffe II, age 22, from Nashville TN; Power-conference star]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is clear-eyed (+0.03)
RATINGS: [overall 76, Star]
  - pass_rush: 76  (sees herself at 76)
  - run_stop: 76  (sees herself at 76)
  - pressure thresholds: exile 21, contract 52, spotlight 43, loyalty 13
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 40 (pick 1)]
DECISION_LOG: [none yet]
```
### Jocelyn Whitlock  (P, Team 11)
```yaml
IDENTITY: [Jocelyn Whitlock, age 36, from Omaha NE; Small-college standout]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Grinder] wants to earn every inch; fears being handed nothing and losing it anyway
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is overconfident (+0.27)
RATINGS: [overall 91, Franchise player]
  - power: 92  (sees herself at 94)
  - accuracy: 89  (sees herself at 92, overrating)
  - pressure thresholds: exile 75, contract 38, spotlight 64, loyalty 32
RECOGNITION: [respected; esteem 12.1; honors: All-League x6]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```

## A player whose personality changed (her soul stayed the same)

### Beatriz Hightower II  (TE, Team 03)
```yaml
IDENTITY: [Beatriz Hightower II, age 31, from Compton CA; Two-sport athlete]
SOUL (fixed): [+ In-Line Anchor, - Stiff Routes]  temperament family: power
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is overconfident (+0.59)
RATINGS: [overall 62, Starter]
  - route: 54  (sees herself at 60, overrating)
  - hands: 58  (sees herself at 62, overrating)
  - block: 71  (sees herself at 76, overrating)
  - pressure thresholds: exile 57, contract 50, spotlight 28, loyalty 61
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 31 (pick 95); became Grinder (was Competitor) 33; became Competitor (was Grinder) 37]
DECISION_LOG: [none yet]
```

## A retired player (cards are kept for the Archive)

### Colette Kincaid  (OL, retired)
```yaml
IDENTITY: [Colette Kincaid, age 31, from Buffalo NY; Power-conference star]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is overconfident (+0.40)
RATINGS: [overall 92, Franchise player]
  - pass_block: 92  (sees herself at 96, overrating)
  - run_block: 91  (sees herself at 94, overrating)
  - pressure thresholds: exile 18, contract 33, spotlight 53, loyalty 61
RECOGNITION: [respected; esteem 14.8; honors: All-League x3, Player of the Year x2]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [retired 5; hof_ballot 8; hof_ballot 9; hof_ballot 10; hof_ballot 11; hof_ballot 12; hof_ballot 13]
DECISION_LOG: [none yet]
```

## Head coaches: the most esteemed ever, a typical coach and a weak one

### Coach Rosario Lachance  (retired)  -  HALL OF FAMER
```yaml
IDENTITY: [Rosario Lachance, age 60, from Honolulu HI; Third-generation coaching family]
SOUL (fixed): [+ Taskmaster, - Predictable Offense]
PERSONALITY: [Disciplinarian] wants order, rules and no excuses; fears chaos and ego
  - allowed by her soul: Disciplinarian, Steady Hand, Survivor, Tactician; right now she is clear-eyed (-0.13)
RATINGS:
  - offense: 38  (sees herself at 38)   -> -0.31 points of margin
  - defense: 55  (sees herself at 55)   -> +0.11 points of margin
  - development: 60  (sees herself at 57, doubting)   -> +0.05 rating points per year to each young player
  - gamecraft: 50  (sees herself at 49)   (no on-field effect yet)
  - discipline: 66  (sees herself at 63, doubting)   (no on-field effect yet)
  - motivation: 56  (sees herself at 55)   (no on-field effect yet)
  - pressure thresholds: exile 54, contract 77, spotlight 56, loyalty 63
TRAJECTORY: [age 47: 53; age 49: 54; age 51: 54; age 53: 53; age 55: 52; age 57: 54; age 59: 54; peak 55 at 50; now 54]
RECOGNITION: [Hall of Famer; esteem 38.9; honors: Coach of the Year, Champion x4, Hall of Fame]
RELATIONSHIPS: {Freya Garrison (CEO): -1}
CAREER: [hired 14; retired 28; hof_ballot 31]
DECISION_LOG: [19: was exiled with her team]
```
### Coach Anneke Lockhart  (Team 26)
```yaml
IDENTITY: [Anneke Lockhart, age 52, from Helsinki Finland; Third-generation coaching family]
SOUL (fixed): [+ Defensive Architect, - Stunts Growth]
PERSONALITY: [Survivor] wants another contract year; fears the CEO's phone call
  - allowed by her soul: Disciplinarian, Tactician, Steady Hand, Survivor; right now she is full of doubt (-0.59)
RATINGS:
  - offense: 52  (sees herself at 46, doubting)   -> -0.05 points of margin
  - defense: 60  (sees herself at 55, doubting)   -> +0.08 points of margin
  - development: 48  (sees herself at 42, doubting)   -> -0.04 rating points per year to each young player
  - gamecraft: 56  (sees herself at 55)   (no on-field effect yet)
  - discipline: 51  (sees herself at 45, doubting)   (no on-field effect yet)
  - motivation: 52  (sees herself at 47, doubting)   (no on-field effect yet)
  - pressure thresholds: exile 33, contract 52, spotlight 10, loyalty 49
TRAJECTORY: [age 43: 52; age 44: 51; age 45: 51; age 46: 52; age 47: 52; age 48: 52; age 49: 52; age 50: 52; age 51: 52; age 52: 53; peak 53 at 52; now 53]
RECOGNITION: [known; esteem 6.9; honors: none yet]
RELATIONSHIPS: {Maia Beaumont (CEO): -1}
CAREER: [hired 30]
DECISION_LOG: [40: was exiled with her team]
```
### Coach Dara Ostrander  (Team 23)
```yaml
IDENTITY: [Dara Ostrander, age 50, from Bozeman MT; Long-time position coach]
SOUL (fixed): [+ Clock Manager, - Predictable Offense]
PERSONALITY: [Survivor] wants another contract year; fears the CEO's phone call
  - allowed by her soul: Tactician, Gambler, Survivor, Steady Hand; right now she is full of doubt (-0.62)
RATINGS:
  - offense: 25  (sees herself at 20, doubting)   -> -0.59 points of margin
  - defense: 32  (sees herself at 29, doubting)   -> -0.48 points of margin
  - development: 49  (sees herself at 44, doubting)   -> -0.03 rating points per year to each young player
  - gamecraft: 57  (sees herself at 49, doubting)   (no on-field effect yet)
  - discipline: 48  (sees herself at 44, doubting)   (no on-field effect yet)
  - motivation: 27  (sees herself at 21, doubting)   (no on-field effect yet)
  - pressure thresholds: exile 48, contract 56, spotlight 34, loyalty 58
TRAJECTORY: [age 50: 40; peak 40 at 50; now 40]
RECOGNITION: [unknown; esteem 0.4; honors: none yet]
RELATIONSHIPS: {Mercy Avery (CEO): +4}
CAREER: [hired 39]
DECISION_LOG: [none yet]
```

**A coach between jobs (she lives on and may be offered to a CEO again):**

### Coach Bianca Chandler  (between jobs)
```yaml
IDENTITY: [Bianca Chandler, age 51, from Winnipeg MB; Coordinator who got her first shot]
SOUL (fixed): [+ Taskmaster, - Predictable Offense]
PERSONALITY: [Disciplinarian] wants order, rules and no excuses; fears chaos and ego
  - allowed by her soul: Disciplinarian, Steady Hand, Survivor, Tactician; right now she is clear-eyed (+0.10)
RATINGS:
  - offense: 39  (sees herself at 39)   -> -0.34 points of margin
  - defense: 63  (sees herself at 63)   -> +0.20 points of margin
  - development: 66  (sees herself at 68)   -> +0.11 rating points per year to each young player
  - gamecraft: 65  (sees herself at 67)   (no on-field effect yet)
  - discipline: 71  (sees herself at 72)   (no on-field effect yet)
  - motivation: 42  (sees herself at 42)   (no on-field effect yet)
  - pressure thresholds: exile 44, contract 20, spotlight 49, loyalty 57
TRAJECTORY: [age 46: 60; age 47: 59; age 48: 60; age 49: 58; age 50: 59; age 51: 58; peak 60 at 46; now 58]
RECOGNITION: [known; esteem 5.6; honors: none yet]
RELATIONSHIPS: {Ivy Carrow (CEO): -32, Sofia Fitzgerald (gm): +0, Monique Merrick (CEO): +4}
CAREER: [hired 34; fired 38]
DECISION_LOG: [38: was fired by Ivy Carrow]
```

## Recognition: who the media called a legend, and the Hall of Fame

Nobody was made a legend. These are the Archive's own entries, in order:

```
year 7: legend contested: Nia Amundsen (player), esteem 22.8, 34% of outlets
year 8: legend recognized: Nia Amundsen (player), esteem 27.9, 78% of outlets
year 16: legend recognized: Teagan Kasprzak (player), esteem 28.8, 73% of outlets
year 20: legend recognized: Ingrid Ellison (gm), esteem 18.1, 77% of outlets
year 22: legend recognized: Hadley Dahl (coach), esteem 30.2, 100% of outlets
year 22: legend recognized: Julia Obuya (gm), esteem 21.5, 100% of outlets
year 22: legend recognized: Imani Blackwood (owner), esteem 24.8, 100% of outlets
year 24: legend recognized: Kiara Peralta (player), esteem 27.5, 76% of outlets
year 24: legend recognized: Rosario Lachance (coach), esteem 23.4, 84% of outlets
year 25: legend contested: Evangeline Avery (owner), esteem 24.5, 55% of outlets
year 26: legend recognized: Evangeline Avery (owner), esteem 25.2, 73% of outlets
year 27: legend recognized: Rhea Fennimore (gm), esteem 18.8, 62% of outlets
```

**The Hall of Fame so far:**

| Year | Kind | Name | Esteem | Vote | Honors |
|---|---|---|---|---|---|
| 16 | player | Nia Amundsen | 28.9 | 97% | Champion x2, All-League x10, Player of the Year x3 |
| 23 | gm | Ingrid Ellison | 18.1 | 93% | Champion x2, Executive of the Year x2 |
| 23 | player | Teagan Kasprzak | 38.5 | 100% | All-League x12, Champion x2, Player of the Year x5 |
| 26 | owner | Imani Blackwood | 25.3 | 95% | Champion x3 |
| 30 | coach | Hadley Dahl | 27.9 | 97% | Champion x3, Coach of the Year x1 |
| 31 | coach | Rosario Lachance | 38.9 | 100% | Coach of the Year x1, Champion x4 |
| 32 | player | Kiara Peralta | 27.4 | 92% | All-League x8, Player of the Year x4 |
| 32 | player | Esme Edmonds | 29.3 | 100% | All-League x10, Player of the Year x3 |
| 37 | owner | Evangeline Avery | 23.1 | 95% | Champion x4 |
| 40 | coach | Kimi Danforth | 25.4 | 97% | Champion x2 |

**The most esteemed player:**

### Teagan Kasprzak  (DL, retired)
```yaml
IDENTITY: [Teagan Kasprzak, age 36, from Kansas City MO; Junior-college transfer]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is overconfident (+1.00)
RATINGS: [overall 82, Franchise player]
  - pass_rush: 79  (sees herself at 92, overrating)
  - run_stop: 86  (sees herself at 97, overrating)
  - pressure thresholds: exile 53, contract 71, spotlight 43, loyalty 65
RECOGNITION: [Hall of Famer; esteem 38.5; honors: All-League x12, Champion x2, Player of the Year x5, Hall of Fame]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 6 (pick 4); retired 20; hof_ballot 23]
DECISION_LOG: [none yet]
```

## A CEO, a GM, and the Archive's first entries

### CEO Valentina Kirkland  (Team 40, CEO)
```yaml
IDENTITY: [Valentina Kirkland, age 70, from Fresno CA; Sports-franchise veteran]
SOUL (fixed): [+ Fan Favorite, - Money Pit]
PERSONALITY: [Showwoman] wants spectacle and headlines; fears boredom
  - allowed by her soul: Local Hero, Showwoman, Glory Hunter, Patient Steward; right now she is clear-eyed (-0.24)
RATINGS:
  - patience: 35  (sees herself at 31, doubting)
  - ambition: 46  (sees herself at 45)
  - involvement: 38  (sees herself at 36)
  - popularity: 62  (sees herself at 61)
  - business: 35  (sees herself at 33)
  - fan approval right now: 80%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 64, media 54, losing 55, subsidy 69
METERS (hers alone; they end with her tenure):
  - Fan Rapport: 75  (she knows exactly what these fans want)
  - Standing Among CEOs: 52  (somewhere in between)
  - Legacy: 69  (her name will be on the wall)
PLEDGE: [standard] the share of a profit she puts back into the club
TRAJECTORY: [age 55: 44; age 57: 44; age 59: 44; age 61: 44; age 63: 44; age 65: 43; age 67: 44; age 69: 44; peak 44 at 55; now 43]
RECOGNITION: [star; esteem 16.7; honors: Champion]
RELATIONSHIPS: {Lupe Kawamoto (coach): +4, Corinne Atwood (coach): +4, Mirabel Sutherland (gm): +4, Haruka Dunmore (gm): +4, Team 40 fans: +33}
CAREER: [elected 24]
DECISION_LOG: [13 earlier; 36: pledged the standard share of profit to the club; 37: pledged the standard share of profit to the club; 38: pledged the standard share of profit to the club; 39: pledged the standard share of profit to the club; 39: survived a recall vote; 40: pledged the standard share of profit to the club]
```
### CEO Phoebe Ferreira  (Team 48, recalled)
```yaml
IDENTITY: [Phoebe Ferreira, age 59, from Duluth MN; Philanthropist]
SOUL (fixed): [+ Hands-On Leader, - Despised]
PERSONALITY: [Patient Steward] wants a slow, sound build; fears panic
  - allowed by her soul: Meddler, Legacy Builder, Glory Hunter, Patient Steward; right now she is full of doubt (-0.81)
RATINGS:
  - patience: 55  (sees herself at 48, doubting)
  - ambition: 57  (sees herself at 51, doubting)
  - involvement: 72  (sees herself at 67, doubting)
  - popularity: 26  (sees herself at 18, doubting)
  - business: 55  (sees herself at 48, doubting)
  - fan approval right now: 37%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 50, media 52, losing 23, subsidy 44
METERS (hers alone; they end with her tenure):
  - Fan Rapport: 46  (somewhere in between)
  - Standing Among CEOs: 50  (somewhere in between)
  - Legacy: 7  (she will be forgotten)
PLEDGE: [standard] the share of a profit she puts back into the club
TRAJECTORY: [age 59: 53; peak 53 at 59; now 53]
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {Team 48 fans: -40, Priya Devereux (coach): -11, Yelena Lachance (coach): -5, Janelle Acosta (gm): -5, Sylvie Fennimore (gm): -1}
CAREER: [elected 39; recalled 40]
DECISION_LOG: [39: was elected by the fans of team 48; 39: fired coach Yelena Lachance (new CEO cleaned house); 39: fired gm Janelle Acosta (new CEO cleaned house); 40: pledged the standard share of profit to the club; 40: blamed Priya Devereux for the exile; 40: was recalled]
```
### GM Paloma Espinoza  (Team 33, gm)
```yaml
IDENTITY: [Paloma Espinoza, age 51, from Juneau AK; Coach's trusted lieutenant]
SOUL (fixed): [+ Closer, - Cap Casualty]
PERSONALITY: [Dealmaker] wants the best contract in every negotiation; fears being outmaneuvered
  - allowed by her soul: Dealmaker, Cold Realist, Loyal Lieutenant, Planner; right now she is overconfident (+1.00)
RATINGS:
  - scouting: 79  (sees herself at 89, overrating)   -> +0.92 rating points on her team's rookie each year
  - negotiation: 83  (sees herself at 92, overrating)   -> 20% fewer contract expiries
  - evaluation: 81  (sees herself at 88, overrating)   (no on-field effect yet)
  - trades: 56  (sees herself at 64, overrating)   (no on-field effect yet)
  - cap_sense: 54  (sees herself at 63, overrating)   (no on-field effect yet)
  - pressure thresholds: exile 38, contract 49, spotlight 46, loyalty 47
TRAJECTORY: [age 50: 71; age 51: 71; peak 71 at 50; now 71]
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {Junie Avery (CEO): -1}
CAREER: [hired 38]
DECISION_LOG: [39: was exiled with her team]
```
**A recall vote as the Archive logs it:**

```
year: 40
event: recall_vote
team: 48
trigger: approval
approval: 0.368
recall_share: 0.521
result: recalled
owner: Phoebe Ferreira
replacement: Lydia Aoki
candidates: ['Echo Nakamura', 'Isla Sinclair', 'Lydia Aoki', 'Rhea Contreras', 'Yara Gallagher']
capital: 0.442
```


## A fanbase and the press that covers it

### Fanbase of Team 06  (Gloomy Realists)
```yaml
IDENTITY: [Team 06 fans; market size 47 of 100; the franchise's permanent card, it outlives every CEO]
PERSONALITY: [Gloomy Realists] wants honesty; fears being fooled again; picks CEOs who are strong on business
ARCHETYPES: [+ Hang On Every Word, - Steady Hands]
RATINGS:
  - loyalty: 35
  - expectations: 56   (born at 41; drifts with results, within +/-15)
  - passion: 37
  - volatility: 28
  - media_trust: 57
  - approval of the CEO: 60%
  - Fan Capital: 0.59  (recall immunity; worth 2.8 points on a recall vote)
  - what the press did to approval last season: +0.6 points
  - pressure thresholds: exile 37, losing 45, scandal 56, spotlight 34
METERS (this franchise's own; they rise and fall with what happens, and their resting level drifts):
  - Tailgate Spirit: 43  (somewhere in between; resting level 36, since year 0)
  - Hope: 46  (somewhere in between; resting level 39, since year 0)
  - Civic Pride: 35  (the team is just a tenant; resting level 34, since year 0)
  - Outrage: 50  (somewhere in between; resting level 55, since year 13)
  - Grudge: 82  (they have not forgiven the league; resting level 78, since year 29)
BOYCOTT: [off]
MEMORIES (fading):
  - 37: the club was sent into exile  (remembered 77%)
  - 38: the club came home from exile  (remembered 67%)
  - 33: the club was sent into exile  (remembered 55%)
  - 34: the club came home from exile  (remembered 48%)
  - 29: the club was sent into exile  (remembered 39%)
  - 33: the fans began to boycott  (remembered 38%)
SPENDING_ASK: [fair] what the fans asked of the CEO's investment this year
RELATIONSHIPS: {Adaeze Kowalski (CEO): -54, Petra Sutherland (CEO): -48, Abigail Lombardi (CEO): -1, Emilia Oakley (CEO): +8}
DECISION_LOG: [46 earlier; 36: asked for the fair level of investment; 37: asked for the fair level of investment; 37: kept the CEO; 38: asked for the fair level of investment; 39: asked for the fair level of investment; 40: asked for the fair level of investment]
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
  - approval of the CEO: 51%
  - Fan Capital: 0.45  (recall immunity; worth 0.0 points on a recall vote)
  - what the press did to approval last season: -0.0 points
  - pressure thresholds: exile 48, losing 48, scandal 56, spotlight 60
METERS (this franchise's own; they rise and fall with what happens, and their resting level drifts):
  - Memory Keepers: 31  (last year is ancient history; resting level 31, since year 0)
  - Outrage: 53  (somewhere in between; resting level 56, since year 0)
  - Wallet Mood: 93  (they open their wallets gladly; resting level 79, since year 0)
  - Grudge: 73  (they have not forgiven the league; resting level 74, since year 1)
  - Homecoming Pull: 61  (the exile healed into pride; resting level 55, since year 5)
BOYCOTT: [off]
MEMORIES (fading):
  - 37: the club was sent into exile  (remembered 73%)
  - 38: the club came home from exile  (remembered 65%)
  - 38: the fans began to boycott  (remembered 56%)
  - 37: the fans began to boycott  (remembered 51%)
  - the boycott ended with a new CEO  (remembered 32%)
  - the boycott ended with a new CEO  (remembered 29%)
SPENDING_ASK: [fair] what the fans asked of the CEO's investment this year
RELATIONSHIPS: {Xiomara Underhill (CEO): -46, Sabine Espinoza (CEO): -29, Anika Forsythe (CEO): -29, Dara Rasmussen (CEO): -29, Gwen Hutchins (CEO): -29, Lourdes Jankowski (CEO): -29, Sunny Benavides (CEO): -29, Nadia Madsen (CEO): +24}
DECISION_LOG: [46 earlier; 37: asked for the fair level of investment; 37: voted to recall the CEO; 38: asked for the fair level of investment; 38: voted to recall the CEO; 39: asked for the fair level of investment; 40: asked for the fair level of investment]
```
### Fanbase of Team 32  (Die-Hards)
```yaml
IDENTITY: [Team 32 fans; market size 40 of 100; the franchise's permanent card, it outlives every CEO]
PERSONALITY: [Die-Hards] wants a team that is theirs; fears a sale or a move; picks CEOs who are strong on popularity
ARCHETYPES: [+ Demanding, - Steady Hands]
RATINGS:
  - loyalty: 62
  - expectations: 69   (born at 57; drifts with results, within +/-15)
  - passion: 64
  - volatility: 45
  - media_trust: 48
  - approval of the CEO: 68%
  - Fan Capital: 0.71  (recall immunity; worth 6.4 points on a recall vote)
  - what the press did to approval last season: +0.1 points
  - pressure thresholds: exile 62, losing 31, scandal 27, spotlight 51
METERS (this franchise's own; they rise and fall with what happens, and their resting level drifts):
  - Outrage: 50  (somewhere in between; resting level 56, since year 0)
  - Next Generation: 51  (somewhere in between; resting level 46, since year 0)
  - Patience: 74  (they will wait for it; resting level 66, since year 0)
  - Grudge: 59  (somewhere in between; resting level 60, since year 1)
  - Homecoming Pull: 72  (the exile healed into pride; resting level 71, since year 6)
BOYCOTT: [off]
MEMORIES (fading):
  - 36: the championship  (remembered 71%)
  - 33: the championship  (remembered 55%)
  - 27: the club was sent into exile  (remembered 32%)
  - 28: the club came home from exile  (remembered 28%)
  - 10 seasons without a playoff game  (remembered 25%)
  - 22: the club was sent into exile  (remembered 21%)
SPENDING_ASK: [fair] what the fans asked of the CEO's investment this year
RELATIONSHIPS: {Lourdes Aguilar (CEO): -51, Hattie Dubois (CEO): -41, Genevieve Benavides (CEO): -24, Soledad Aguilar (CEO): -24, Kirsten Davenport (CEO): -22, Rosario Waller (CEO): +4}
DECISION_LOG: [46 earlier; 36: asked for the fair level of investment; 37: asked for the fair level of investment; 38: asked for the fair level of investment; 38: kept the CEO; 39: asked for the fair level of investment; 40: asked for the fair level of investment]
```
The franchise's permanent card, with its own meters, memories and any boycott (the club with the longest memory):

### Fanbase of Team 37  (Party Crowd)
```yaml
IDENTITY: [Team 37 fans; market size 73 of 100; the franchise's permanent card, it outlives every CEO]
PERSONALITY: [Party Crowd] wants a good time; fears boredom; picks CEOs who are strong on involvement
ARCHETYPES: [+ Fanatical, - Steady Hands]
RATINGS:
  - loyalty: 41
  - expectations: 33   (born at 41; drifts with results, within +/-15)
  - passion: 70
  - volatility: 26
  - media_trust: 64
  - approval of the CEO: 41%
  - Fan Capital: 0.43  (recall immunity; worth 0.0 points on a recall vote)
  - what the press did to approval last season: -2.5 points
  - pressure thresholds: exile 70, losing 46, scandal 70, spotlight 58
METERS (this franchise's own; they rise and fall with what happens, and their resting level drifts):
  - Grudge: 89  (they have not forgiven the league; resting level 83, since year 0)
  - Faith in the Plan: 93  (the front office has earned trust; resting level 89, since year 0)
  - Tailgate Spirit: 72  (the lots are full by dawn; resting level 78, since year 0)
  - Kinship With the Roster: 49  (somewhere in between; resting level 51, since year 7)
  - Outrage: 66  (the phones are ringing; resting level 58, since year 13)
BOYCOTT: [on, level 0.17] the fans are staying away: the club's local revenue is down 7% until a new CEO is seated or they come back
MEMORIES (fading):
  - 39: the club was sent into exile  (remembered 92%)
  - 40: the club came home from exile  (remembered 80%)
  - 37: the club was sent into exile  (remembered 77%)
  - 40: the fans began to boycott  (remembered 70%)
  - 38: the club came home from exile  (remembered 67%)
  - 39: the fans began to boycott  (remembered 64%)
SPENDING_ASK: [fair] what the fans asked of the CEO's investment this year
RELATIONSHIPS: {Emani Brandt (CEO): -80, Layla Marlowe (CEO): -62, Gianna McBride (CEO): -39, Jelena Brandt (CEO): -29, Yasmin McBride (CEO): +28}
DECISION_LOG: [47 earlier; 37: asked for the fair level of investment; 37: kept the CEO; 38: asked for the fair level of investment; 39: asked for the fair level of investment; 39: voted to recall the CEO; 40: asked for the fair level of investment]
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

### CEO Valentina Kirkland  (Team 40, CEO)
```yaml
IDENTITY: [Valentina Kirkland, age 70, from Fresno CA; Sports-franchise veteran]
SOUL (fixed): [+ Fan Favorite, - Money Pit]
PERSONALITY: [Showwoman] wants spectacle and headlines; fears boredom
  - allowed by her soul: Local Hero, Showwoman, Glory Hunter, Patient Steward; right now she is clear-eyed (-0.24)
RATINGS:
  - patience: 35  (sees herself at 31, doubting)
  - ambition: 46  (sees herself at 45)
  - involvement: 38  (sees herself at 36)
  - popularity: 62  (sees herself at 61)
  - business: 35  (sees herself at 33)
  - fan approval right now: 80%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 64, media 54, losing 55, subsidy 69
METERS (hers alone; they end with her tenure):
  - Fan Rapport: 75  (she knows exactly what these fans want)
  - Standing Among CEOs: 52  (somewhere in between)
  - Legacy: 69  (her name will be on the wall)
PLEDGE: [standard] the share of a profit she puts back into the club
TRAJECTORY: [age 55: 44; age 57: 44; age 59: 44; age 61: 44; age 63: 44; age 65: 43; age 67: 44; age 69: 44; peak 44 at 55; now 43]
RECOGNITION: [star; esteem 16.7; honors: Champion]
RELATIONSHIPS: {Lupe Kawamoto (coach): +4, Corinne Atwood (coach): +4, Mirabel Sutherland (gm): +4, Haruka Dunmore (gm): +4, Team 40 fans: +33}
CAREER: [elected 24]
DECISION_LOG: [13 earlier; 36: pledged the standard share of profit to the club; 37: pledged the standard share of profit to the club; 38: pledged the standard share of profit to the club; 39: pledged the standard share of profit to the club; 39: survived a recall vote; 40: pledged the standard share of profit to the club]
```

## Scenes as the Archive records them

Each firing, recall vote and exile determination is a scene: every party gives its own claim, and the evidence section says, from the engine's own numbers, which claims hold. The scenes never change an outcome (the check script proves a league plays out identically with them on or off); they explain it, and they move relationships and decision logs.

**An exile determination**

```
EVENT 40-exile_determination-48-1  (Team 48; exile determination; finished fifth in the division)
├── Owner claims: Phoebe Ferreira (Patient Steward): "Fifth in the division, and I will say who is to blame: Priya Devereux. The roster rated 40% and they won 33%."  [supported by the record]
├── Coach claims: Priya Devereux (Developer): "I was handed a roster 1.6 deviations below average and the schedule did the rest."  [supported, but overstated]
├── GM claims: Sylvie Fennimore (Dealmaker): "The roster was 4 of 5 in this division on paper. The record, 33%, was 7% below what it should have been."  [supported by the record]
├── The fans claim: Team 48 fans: "They finished 33%. We wanted honesty and we feared being fooled again; that is what we got."  [supported by the record]
├── Press claims: Team 48 Insider (Contrarian): "They finished 33%. The town is watching closely, and that is how we are telling it."  [supported by the record]
└── Evidence supports: Exile followed a thin roster and under-delivery against the roster.  (record 33%, roster predicts 40%, roster -0.8 deviations from average)
    Outcome: Team 48 is exiled for next season
```

**A firing the record backs**

```
EVENT 39-firing-47-1  (Team 47; firing; CEO fired the coach (results))
├── Owner claims: Daniela Rutledge (Penny-Pincher): "the roster should have won about 29% and they won 22%. I gave her 5 seasons; I had no patience left."  [supported by the record]
├── Coach claims: Maia Kaplan (Steady Hand): "You gave me a roster 2.5 deviations below the league's average and expected a contender."  [supported, but overstated]
├── GM claims: Tatiana Cordero (Dealmaker): "The roster was fine. The record was 22%, against 29% on paper."  [supported by the record]
├── The fans claim: Team 47 fans: "They finished 22%. We wanted a good time and we feared boredom; that is what we got."  [supported by the record]
├── Press claims: Team 47 Courier (Watchdog): "They finished 22%. The town is watching closely, and that is how we are telling it."  [supported by the record]
└── Evidence supports: The firing is backed by the record, and the roster does not excuse it: the team won well under what it was built to win.  (record 22%, roster predicts 29%, roster -1.8 deviations from average)
    Outcome: Maia Kaplan fired; replaced by a new coach
```

**A harsh firing (the roster explains the record)**

```
EVENT 40-firing-37-1  (Team 37; firing; CEO fired the gm (results))
├── Owner claims: Yasmin McBride (Meddler): "29% is not what I bought this team for. I trusted her with the roster; I was patient."  [supported by the record]
├── GM claims: Antonia Davenport (Cold Realist): "I built the roster and she lost games the roster should have won: 29% on a team that rates 47%."  [supported by the record]
├── Coach claims: Honor Underhill (Developer): "I coached what I was handed, a roster 0.2 deviations below average."  [not supported by the record]
├── The fans claim: Team 37 fans: "They finished 29%. We wanted a good time and we feared boredom; that is what we got."  [supported by the record]
├── Press claims: Team 37 Press (Contrarian): "They finished 29%. The town is restless, and that is how we are telling it."  [supported by the record]
└── Evidence supports: A harsh firing: the record was poor (29%), but the roster she built was not thin, so the shortfall was on the field.  (record 29%, roster predicts 47%, roster -0.2 deviations from average)
    Outcome: Antonia Davenport fired; replaced by a new gm
```

**A new CEO's sweep**

```
EVENT 39-firing-48-2  (Team 48; firing; CEO fired the gm (new CEO cleaned house))
├── Owner claims: Phoebe Ferreira (Patient Steward): "New CEO, new staff. I wanted a slow, sound build and I wasn't going to ask Janelle Acosta for it."  [supported by the record]
├── GM claims: Janelle Acosta (Talent Hawk): "I built the roster and she lost games the roster should have won: 44% on a team that rates 41%."  [not supported by the record]
├── Coach claims: Yelena Lachance (Developer): "I coached what I was handed, a roster 0.8 deviations below average."  [supported by the record]
├── The fans claim: Team 48 fans: "They finished 44%. We wanted honesty and we feared being fooled again; that is what we got."  [supported by the record]
├── Press claims: Team 48 Insider (Contrarian): "They finished 44%. The town is watching closely, and that is how we are telling it."  [supported by the record]
└── Evidence supports: A sweep: the new CEO cleared the staff on arrival, whatever the record (44% against 41% on paper).  (record 44%, roster predicts 41%, roster -0.8 deviations from average)
    Outcome: Janelle Acosta fired; replaced by a new gm
```

**A recall vote that removes a CEO**

```
EVENT 40-recall_vote-48-1  (Team 48; recall vote; vote triggered by approval)
├── Owner claims: Phoebe Ferreira (Patient Steward): "I thought we were at 32%. The team lost, and the fans are blaming the person they can vote on."  [supported by the record]
├── The fans claim: Team 48 fans: "They finished 33%. We wanted honesty and we feared being fooled again; that is what we got." We wanted a CEO strong on business and we chose Lydia Aoki.  [supported by the record]
├── Press claims: Team 48 Insider (Contrarian): "They finished 33%. The town is watching closely, and that is how we are telling it."  [supported by the record]
├── New CEO claims: Lydia Aoki (Opportunist): "Five of us stood. The fans wanted strength on business and picked me. I want a quick profit."  [supported by the record]
└── Evidence supports: 52.1% voted to recall (a majority of the 1,000,000 fans is needed): recalled.  (record 33%, roster predicts 40%, roster -0.8 deviations from average)
    Outcome: Phoebe Ferreira recalled; Lydia Aoki elected from 5 candidates
```

**A recall vote the CEO survives**

```
EVENT 40-recall_vote-46-1  (Team 46; recall vote; vote triggered by rotation)
├── Owner claims: Carmen Nakamura (Penny-Pincher): "I told you we were at 74%. The fans know what I stand for: a profitable franchise."  [not supported by the record]
├── The fans claim: Team 46 fans: "They finished 61%. We wanted a title every year and we feared being ignored; we have no complaint about the record, but we are watching."  [not supported by the record]
├── Press claims: Team 46 Sideline (Statistician): "They finished 61%. The town is behind the team, and that is how we are telling it."  [supported by the record]
└── Evidence supports: 19.7% voted to recall (a majority of the 1,000,000 fans is needed): the CEO survives.  (record 61%, roster predicts 50%, roster +0.1 deviations from average)
    Outcome: Carmen Nakamura survives
```


## What an agent is shown, and what the log keeps

Choices go through Decision Points. An agent is shown its own card, what it perceives (candidates' ratings as the CEO sees them, with blind spots) and the legal options, and answers with one option id. The guard applies the choice (or the autopilot's choice if the answer is invalid or late) and logs it. Below: the two decisions a CEO faces, as an agent receives them, and the log line.

**A CEO's staff review, as an agent receives it:**

```json
{
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
   "popularity": 57.1,
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
  "record_this_season": 0.222,
  "record_last_season": null,
  "exiled_this_year": true,
  "fan_approval_of_you": 0.513,
  "facing_a_recall_vote_this_year": true,
  "you_are_a_new_ceo": false,
  "press_effect_on_fans": -0.024,
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
   "pressure_on_her": 0.278,
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
   "pressure_on_her": 0.278,
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

**Core personalities (all rostered players):** Diplomat 546, Competitor 458, Grinder 436, Perfectionist 384, Showman 258, Quiet Leader 163, Free Spirit 151, Hothead 93, Loyalist 31, Mercenary 24

**Most common positive archetypes:** Well-Rounded 710, Pass-Pro Wall 134, Ballhawk 120, Edge Terror 118, Shutdown Corner 110, Road Grader 101, Run Stuffer 93, Thumper 86

**Coach effect across the 48 teams:** average +0.01, spread (sd) 0.45, best +1.01, worst -1.07 points of expected margin. For scale, team talent has a spread of about 3 to 4 points.

**Personality shifts:** 3069 of 31163 players have changed personality at least once in 40 seasons.

**Standing in the media's eyes** (everyone who ever lived, by what the media calls her now): known 253, respected 94, star 42, Hall of Famer 10, legend 3. 10 are in the Hall of Fame.

**Fan cultures:** Die-Hards 13, Entitled 11, Party Crowd 9, Gloomy Realists 7, Long-Suffering 5, Front-Runners 3

**Fan Capital:** average 0.53, from 0.38 to 0.71; the most it can buffer a recall vote is 15 points.

**Fan meters:** every fanbase has 3 from birth and can awaken up to 5; now [(5, 40), (4, 7), (3, 1)] (meters per club, clubs). Most common: Outrage 32, Grudge 30, Homecoming Pull 28, Civic Pride 26.

**Fan memories** held now: exile 197, return 174, boycott 80, boycott_end 29, title 21, star_left 17, drought 16. **Boycotts** on now: 1 clubs; 80 begun within the memory window. A full boycott costs 40% of local revenue.

**The press on approval, last season:** average 0.9 points either way, largest 3.1 (the cap is 3 before market size and trust).

**Outlets:** 52 (4 national, one local beat per team); a national outlet tells a team's year as it was, a local outlet frames it toward its fans' mood by at most 25 points of tone.

**CEO choices on the record:** ceo_boycott concede 9, ceo_boycott hold 28, ceo_pledge standard 1873. CEOs who stepped aside under a boycott: 0.

**Scenes:** 1090 in 40 seasons ([('recall_vote', 555), ('exile_determination', 320), ('firing', 215)]). Firings by ruling: fair 146, sweep 46, harsh 19, unfounded 4.

**Recall votes:** 555 in 40 seasons (13.9 a year); 194 CEOs recalled (4.8 a year), 35% of votes. CEOs retire on their own too: 44 so far.

**Firings:** 144 coaches and 71 GMs fired in 40 seasons.

**Coaches so far:** 376 hired and 314 retired in 40 seasons; 14 coaches and 12 GMs are between jobs right now.

**Players with cards:** 3244 active or unsigned, 28619 retired.
