# Character cards: samples

Seed 1, after 40 seasons. Names, hometowns and backgrounds come from placeholder word lists (engine/card_pools.py) that you can replace. Ratings, archetypes and the coach effect are real: they come from the engine. Relationships and the decision log start empty and fill as the Interaction system plays scenes (firings, recall votes and exile determinations so far).

## How to read a card

- **Soul (archetypes)** is fixed for life. It is read from the rating profile she is born with: her best attribute names the positive archetype and her weakest the negative one. Her development is bent to stay true to it.
- **Personality** is how her soul shows up. Her archetype allows four personalities; which one she shows depends on her temperament and on how she rates herself. Her self-image lags the truth, so a declining veteran overrates herself and a rising rookie undersells herself. When her confidence moves enough, her personality can shift, but only inside the four her soul allows.
- **Pressure thresholds** (exile, contract, spotlight, loyalty) are how much each kind of pressure rattles her, 1 to 100. They do nothing yet; the Interaction system will use them.
- **Fanbases and outlets**: a fanbase has a culture (its personality), five ratings and two stores: approval of the CEO and Fan Capital (goodwill built by sustained success, which only ever buffers a recall). Its expectations drift with what the team delivers, inside a bound set at birth. An outlet has a voice, five ratings and Credibility, which rises when its forecasts come true and falls when they miss; one that stays irrelevant folds and is replaced. The press can move a CEO's approval by at most 3 points a year.
- **Coach ratings**: offense and defense lift the team (up to +/- 1.0 point of margin each); development adds up to 0.4 rating points a year to each young player. The other three are stored for later. Effects are measured against the league's current average coach, so the average coach does nothing.
- **Living cards**: coaches, GMs and CEOs grow and fade over their careers (ratings move inside the shape their soul gave them), rate themselves with a lag, and can change personality inside the four traits their soul allows. People between jobs live on and can be offered to CEOs again. The TRAJECTORY line is their overall level by age.
- **Recognition**: nobody is a legend by birth. Honors (titles, All-League, Coach of the Year...) build a career esteem; the 52 outlets read it with their own noise, and a credibility-weighted share calling someone a legend makes it so (or the media splits and she is *contested*). The Hall of Fame (outlets and CEOs) votes on people who retired a few years ago. There is no cap on either.

## A franchise player at each position group

### Ruth Aoki  (QB, Team 35)
```yaml
IDENTITY: [Ruth Aoki, age 28, from Bozeman MT; Small-college standout]
SOUL (fixed): [+ Surgeon, - Short-Armed]  temperament family: precision
PERSONALITY: [Perfectionist] wants flawless execution; fears the one mistake everyone remembers
  - allowed by her soul: Perfectionist, Quiet Leader, Grinder, Diplomat; right now she is full of doubt (-0.91)
RATINGS: [overall 94, Franchise player]
  - accuracy: 100  (sees herself at 93, doubting)
  - arm: 90  (sees herself at 79, doubting)
  - awareness: 90  (sees herself at 85, doubting)
  - pressure thresholds: exile 45, contract 47, spotlight 60, loyalty 72
RECOGNITION: [unknown; esteem 2.5; honors: All-League]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 34 (pick 10)]
DECISION_LOG: [none yet]
```
### Abigail Dunmore  (WR, Team 39)
```yaml
IDENTITY: [Abigail Dunmore, age 25, from Cleveland OH; Small-college standout]
SOUL (fixed): [+ Glue Hands, - Rough Routes]  temperament family: precision
PERSONALITY: [Perfectionist] wants flawless execution; fears the one mistake everyone remembers
  - allowed by her soul: Perfectionist, Quiet Leader, Grinder, Diplomat; right now she is full of doubt (-0.71)
RATINGS: [overall 89, Franchise player]
  - route: 82  (sees herself at 76, doubting)
  - hands: 93  (sees herself at 87, doubting)
  - speed: 92  (sees herself at 87, doubting)
  - pressure thresholds: exile 49, contract 50, spotlight 46, loyalty 29
RECOGNITION: [unknown; esteem 2.5; honors: All-League]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 37 (pick 6)]
DECISION_LOG: [none yet]
```
### Nia Jankowski  (OL, Team 43)
```yaml
IDENTITY: [Nia Jankowski, age 30, from Gary IN; Small-college standout]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is overconfident (+0.75)
RATINGS: [overall 89, Franchise player]
  - pass_block: 89  (sees herself at 94, overrating)
  - run_block: 88  (sees herself at 96, overrating)
  - pressure thresholds: exile 34, contract 41, spotlight 58, loyalty 61
RECOGNITION: [respected; esteem 10.5; honors: All-League x5]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 32 (pick 2)]
DECISION_LOG: [none yet]
```
### Bianca Baptiste  (DL, Team 36)
```yaml
IDENTITY: [Bianca Baptiste, age 27, from Montreal QC; Came up through the academy system]
SOUL (fixed): [+ Run Stuffer, - Little Pressure]  temperament family: power
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is full of doubt (-0.33)
RATINGS: [overall 94, Franchise player]
  - pass_rush: 89  (sees herself at 86, doubting)
  - run_stop: 100  (sees herself at 98, doubting)
  - pressure thresholds: exile 50, contract 67, spotlight 44, loyalty 28
RECOGNITION: [respected; esteem 9.1; honors: All-League x4]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 35 (pick 2)]
DECISION_LOG: [none yet]
```
### Zelda Eberhardt  (CB, Team 41)
```yaml
IDENTITY: [Zelda Eberhardt, age 31, from Sao Paulo Brazil; Overlooked recruit]
SOUL (fixed): [+ Ballhawk, - Avoids Contact]  temperament family: flash
PERSONALITY: [Showman] wants the spotlight and a signature moment; fears being ignored by the media
  - allowed by her soul: Showman, Free Spirit, Competitor, Mercenary; right now she is overconfident (+0.73)
RATINGS: [overall 81, Franchise player]
  - coverage: 78  (sees herself at 84, overrating)
  - ball_skills: 91  (sees herself at 95, overrating)
  - tackling: 75  (sees herself at 82, overrating)
  - pressure thresholds: exile 62, contract 80, spotlight 57, loyalty 58
RECOGNITION: [respected; esteem 12.9; honors: All-League x6]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 31 (pick 5); became Showman (was Free Spirit) 39]
DECISION_LOG: [none yet]
```
### Destiny Jimenez  (K, Team 20)
```yaml
IDENTITY: [Destiny Jimenez, age 38, from Albuquerque NM; Walk-on turned starter]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is clear-eyed (+0.23)
RATINGS: [overall 86, Franchise player]
  - power: 89  (sees herself at 89)
  - accuracy: 84  (sees herself at 87, overrating)
  - pressure thresholds: exile 72, contract 59, spotlight 61, loyalty 41
RECOGNITION: [known; esteem 8.6; honors: All-League x4]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [became Grinder (was Diplomat) 27; became Diplomat (was Grinder) 39]
DECISION_LOG: [none yet]
```

## A young rookie and a veteran

### Gwen Rivas  (CB, Team 44)
```yaml
IDENTITY: [Gwen Rivas, age 22, from Cleveland OH; Coach's daughter]
SOUL (fixed): [+ Willing Tackler, - Beaten Deep]  temperament family: power
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is clear-eyed (+0.06)
RATINGS: [overall 77, Star]
  - coverage: 74  (sees herself at 76, overrating)
  - ball_skills: 81  (sees herself at 82)
  - tackling: 83  (sees herself at 81)
  - pressure thresholds: exile 36, contract 44, spotlight 48, loyalty 46
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 40 (pick 1)]
DECISION_LOG: [none yet]
```
### Evangeline Dalton  (OL, Team 19)
```yaml
IDENTITY: [Evangeline Dalton, age 32, from Birmingham AL; Walk-on turned starter]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is overconfident (+0.38)
RATINGS: [overall 88, Franchise player]
  - pass_block: 85  (sees herself at 89, overrating)
  - run_block: 91  (sees herself at 94, overrating)
  - pressure thresholds: exile 70, contract 77, spotlight 53, loyalty 64
RECOGNITION: [star; esteem 22.4; honors: All-League x5, Player of the Year x3]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```

## A player whose personality changed (her soul stayed the same)

### Marguerite Fairbanks  (S, Team 17)
```yaml
IDENTITY: [Marguerite Fairbanks, age 34, from Columbus OH; Two-sport athlete]
SOUL (fixed): [+ Deep Patroller, - Poor Ball Skills]  temperament family: command
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
  - allowed by her soul: Quiet Leader, Competitor, Diplomat, Perfectionist; right now she is overconfident (+0.94)
RATINGS: [overall 60, Depth]
  - coverage: 67  (sees herself at 74, overrating)
  - ball_skills: 55  (sees herself at 62, overrating)
  - tackling: 56  (sees herself at 65, overrating)
  - pressure thresholds: exile 60, contract 60, spotlight 11, loyalty 65
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [became Quiet Leader (was Competitor) 29; became Perfectionist (was Quiet Leader) 30; became Competitor (was Perfectionist) 35]
DECISION_LOG: [none yet]
```

## A retired player (cards are kept for the Archive)

### Bianca Davenport  (CB, retired)
```yaml
IDENTITY: [Bianca Davenport, age 33, from Jackson MS; Coach's daughter]
SOUL (fixed): [+ Willing Tackler, - Poor Ball Skills]  temperament family: power
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is clear-eyed (+0.11)
RATINGS: [overall 95, Franchise player]
  - coverage: 97  (sees herself at 98)
  - ball_skills: 89  (sees herself at 91)
  - tackling: 96  (sees herself at 96)
  - pressure thresholds: exile 53, contract 41, spotlight 42, loyalty 25
RECOGNITION: [Hall of Famer; esteem 45.3; honors: All-League x10, Player of the Year x8, Hall of Fame]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 17 (pick 2); became Grinder (was Competitor) 18; became Competitor (was Grinder) 27; retired 28; hof_ballot 31]
DECISION_LOG: [none yet]
```

## Head coaches: the most esteemed ever, a typical coach and a weak one

### Coach Tatiana Amundsen  (retired)  -  HALL OF FAMER
```yaml
IDENTITY: [Tatiana Amundsen, age 61, from Compton CA; Analytics-minded newcomer]
SOUL (fixed): [+ Inspirer, - Leaky Defense]
PERSONALITY: [Players' Coach] wants a locker room that plays hard for her; fears losing the room
  - allowed by her soul: Players' Coach, Developer, Innovator, Survivor; right now she is clear-eyed (-0.23)
RATINGS:
  - offense: 80  (sees herself at 79)   -> +0.47 points of margin
  - defense: 40  (sees herself at 36, doubting)   -> -0.25 points of margin
  - development: 60  (sees herself at 58, doubting)   -> +0.05 rating points per year to each young player
  - gamecraft: 74  (sees herself at 73)   (no on-field effect yet)
  - discipline: 60  (sees herself at 60)   (no on-field effect yet)
  - motivation: 83  (sees herself at 80, doubting)   (no on-field effect yet)
  - pressure thresholds: exile 55, contract 45, spotlight 55, loyalty 32
TRAJECTORY: [age 47: 57; age 49: 63; age 51: 65; age 53: 66; age 55: 68; age 57: 67; age 59: 67; age 61: 66; peak 68 at 55; now 66]
RECOGNITION: [Hall of Famer; esteem 31.6; honors: Coach of the Year, Champion x2, Hall of Fame]
RELATIONSHIPS: {Grace Grantham (owner): -5}
CAREER: [hired 0; retired 15; hof_ballot 18]
DECISION_LOG: [8: was exiled with her team]
```
### Coach Bianca Chandler  (Team 48)
```yaml
IDENTITY: [Bianca Chandler, age 51, from Winnipeg MB; Coordinator who got her first shot]
SOUL (fixed): [+ Taskmaster, - Predictable Offense]
PERSONALITY: [Disciplinarian] wants order, rules and no excuses; fears chaos and ego
  - allowed by her soul: Disciplinarian, Steady Hand, Survivor, Tactician; right now she is clear-eyed (+0.10)
RATINGS:
  - offense: 39  (sees herself at 39)   -> -0.31 points of margin
  - defense: 63  (sees herself at 63)   -> +0.17 points of margin
  - development: 66  (sees herself at 68)   -> +0.13 rating points per year to each young player
  - gamecraft: 65  (sees herself at 67)   (no on-field effect yet)
  - discipline: 71  (sees herself at 72)   (no on-field effect yet)
  - motivation: 42  (sees herself at 42)   (no on-field effect yet)
  - pressure thresholds: exile 44, contract 20, spotlight 49, loyalty 57
TRAJECTORY: [age 46: 60; age 47: 59; age 48: 60; age 49: 58; age 50: 59; age 51: 58; peak 60 at 46; now 58]
RECOGNITION: [known; esteem 3.6; honors: none yet]
RELATIONSHIPS: {Elena Haskell (owner): -5}
CAREER: [hired 34]
DECISION_LOG: [37: was exiled with her team]
```
### Coach Dara Ostrander  (Team 33)
```yaml
IDENTITY: [Dara Ostrander, age 49, from Bozeman MT; Long-time position coach]
SOUL (fixed): [+ Clock Manager, - Predictable Offense]
PERSONALITY: [Survivor] wants another contract year; fears the owner's phone call
  - allowed by her soul: Tactician, Gambler, Survivor, Steady Hand; right now she is full of doubt (-0.57)
RATINGS:
  - offense: 24  (sees herself at 19, doubting)   -> -0.62 points of margin
  - defense: 32  (sees herself at 28, doubting)   -> -0.45 points of margin
  - development: 48  (sees herself at 45, doubting)   -> -0.02 rating points per year to each young player
  - gamecraft: 56  (sees herself at 49, doubting)   (no on-field effect yet)
  - discipline: 47  (sees herself at 44, doubting)   (no on-field effect yet)
  - motivation: 25  (sees herself at 21, doubting)   (no on-field effect yet)
  - pressure thresholds: exile 48, contract 56, spotlight 34, loyalty 58
TRAJECTORY: [just started]
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [hired 40]
DECISION_LOG: [none yet]
```

**A coach between jobs (she lives on and may be offered to a CEO again):**

### Coach Anneke Lockhart  (between jobs)
```yaml
IDENTITY: [Anneke Lockhart, age 52, from Helsinki Finland; Third-generation coaching family]
SOUL (fixed): [+ Defensive Architect, - Stunts Growth]
PERSONALITY: [Survivor] wants another contract year; fears the owner's phone call
  - allowed by her soul: Disciplinarian, Tactician, Steady Hand, Survivor; right now she is full of doubt (-0.59)
RATINGS:
  - offense: 52  (sees herself at 46, doubting)   -> -0.04 points of margin
  - defense: 60  (sees herself at 55, doubting)   -> +0.14 points of margin
  - development: 48  (sees herself at 42, doubting)   -> -0.00 rating points per year to each young player
  - gamecraft: 56  (sees herself at 55)   (no on-field effect yet)
  - discipline: 51  (sees herself at 45, doubting)   (no on-field effect yet)
  - motivation: 52  (sees herself at 47, doubting)   (no on-field effect yet)
  - pressure thresholds: exile 33, contract 52, spotlight 10, loyalty 49
TRAJECTORY: [age 43: 52; age 44: 51; age 45: 51; age 46: 52; age 47: 52; age 48: 52; age 49: 52; age 50: 52; age 51: 52; age 52: 53; peak 53 at 52; now 53]
RECOGNITION: [known; esteem 7.1; honors: Coach of the Year]
RELATIONSHIPS: {Juana Emerson (owner): -30, Elsa Brightwater (gm): +0}
CAREER: [hired 30; fired 38]
DECISION_LOG: [38: was fired by Juana Emerson]
```

## Recognition: who the media called a legend, and the Hall of Fame

Nobody was made a legend. These are the Archive's own entries, in order:

```
year 5: legend contested: Britta Cordero (coach), esteem 21.5, 33% of outlets
year 7: legend recognized: Mabel Colburn (player), esteem 24.6, 63% of outlets
year 7: legend contested: Britta Cordero (coach), esteem 22.6, 46% of outlets
year 9: legend recognized: Corinne Crenshaw (coach), esteem 26.8, 100% of outlets
year 9: legend recognized: Mirabel Leclair (owner), esteem 23.3, 75% of outlets
year 10: legend contested: Britta Cordero (coach), esteem 23.0, 56% of outlets
year 10: legend recognized: Penelope Nolan (coach), esteem 23.7, 100% of outlets
year 11: legend recognized: Olive Caldwell (player), esteem 27.6, 100% of outlets
year 11: legend contested: Penelope Nolan (coach), esteem 23.0, 59% of outlets
year 14: legend recognized: Tatiana Amundsen (coach), esteem 23.7, 100% of outlets
year 15: legend recognized: Luna Palmieri (gm), esteem 22.3, 100% of outlets
year 17: legend recognized: Fiona Briggs (player), esteem 25.7, 100% of outlets
```

**The Hall of Fame so far:**

| Year | Kind | Name | Esteem | Vote | Honors |
|---|---|---|---|---|---|
| 15 | player | Mabel Colburn | 29.2 | 97% | All-League x12, Player of the Year x3 |
| 15 | player | Adriana Avery | 23.5 | 79% | All-League x9, Champion x2, Player of the Year x1 |
| 16 | CEO | Mirabel Leclair | 21.6 | 93% | Champion x2 |
| 17 | player | Olive Caldwell | 27.5 | 96% | All-League x10, Player of the Year x3 |
| 18 | coach | Tatiana Amundsen | 31.6 | 100% | Coach of the Year x1, Champion x2 |
| 23 | coach | Corinne Crenshaw | 20.4 | 77% | Champion x2 |
| 24 | player | Fiona Briggs | 36.1 | 98% | All-League x9, Player of the Year x6 |
| 27 | gm | Luna Palmieri | 16.5 | 78% | Executive of the Year x1, Champion x2 |
| 29 | gm | Simone Vickers | 16.9 | 81% | Champion x3 |
| 30 | gm | Mika Holmgren | 17.6 | 85% | Champion x3 |
| 31 | player | Bianca Davenport | 45.3 | 100% | All-League x10, Player of the Year x8 |
| 35 | gm | Esme Ziegler | 16.9 | 80% | Champion x2 |
| 36 | CEO | Gwen Hutchins | 20.1 | 87% | Champion x2 |
| 38 | player | Maya Robeson | 30.3 | 99% | All-League x7, Player of the Year x5 |

**The most esteemed player:**

### Bianca Davenport  (CB, retired)
```yaml
IDENTITY: [Bianca Davenport, age 33, from Jackson MS; Coach's daughter]
SOUL (fixed): [+ Willing Tackler, - Poor Ball Skills]  temperament family: power
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is clear-eyed (+0.11)
RATINGS: [overall 95, Franchise player]
  - coverage: 97  (sees herself at 98)
  - ball_skills: 89  (sees herself at 91)
  - tackling: 96  (sees herself at 96)
  - pressure thresholds: exile 53, contract 41, spotlight 42, loyalty 25
RECOGNITION: [Hall of Famer; esteem 45.3; honors: All-League x10, Player of the Year x8, Hall of Fame]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 17 (pick 2); became Grinder (was Competitor) 18; became Competitor (was Grinder) 27; retired 28; hof_ballot 31]
DECISION_LOG: [none yet]
```

## A CEO, a GM, and the Archive's first entries

### CEO Treasure Calloway  (Team 02, CEO)
```yaml
IDENTITY: [Treasure Calloway, age 64, from Calgary AB; Self-made industrialist]
SOUL (fixed): [+ Relentless Competitor, - Money Pit]
PERSONALITY: [Glory Hunter] wants a title right now; fears being a laughingstock
  - allowed by her soul: Glory Hunter, Legacy Builder, Showwoman, Opportunist; right now she is full of doubt (-0.26)
RATINGS:
  - patience: 55  (sees herself at 53)
  - ambition: 63  (sees herself at 60, doubting)
  - involvement: 21  (sees herself at 18, doubting)
  - popularity: 60  (sees herself at 58)
  - business: 19  (sees herself at 18)
  - fan approval right now: 60%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 71, media 66, losing 34, subsidy 37
TRAJECTORY: [age 43: 44; age 46: 44; age 49: 44; age 52: 44; age 55: 44; age 58: 43; age 61: 44; age 64: 44; peak 44 at 48; now 44]
RECOGNITION: [respected; esteem 10.3; honors: none yet]
RELATIONSHIPS: {Team 02 fans: +26}
CAREER: [elected 18]
DECISION_LOG: [18: was elected by the fans of team 2; 25: survived a recall vote; 33: survived a recall vote]
```
### CEO Esperanza Caldwell  (Team 33, recalled)
```yaml
IDENTITY: [Esperanza Caldwell, age 55, from Providence RI; Consortium front-woman]
SOUL (fixed): [+ Hands-On Leader, - Trigger-Happy]
PERSONALITY: [Meddler] wants a hand in every decision; fears being irrelevant
  - allowed by her soul: Meddler, Legacy Builder, Glory Hunter, Patient Steward; right now she is clear-eyed (-0.15)
RATINGS:
  - patience: 39  (sees herself at 36, doubting)
  - ambition: 44  (sees herself at 43)
  - involvement: 75  (sees herself at 75)
  - popularity: 64  (sees herself at 62)
  - business: 44  (sees herself at 42)
  - fan approval right now: 38%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 60, media 65, losing 38, subsidy 47
TRAJECTORY: [age 54: 53; age 55: 53; peak 53 at 54; now 53]
RECOGNITION: [unknown; esteem 1.3; honors: none yet]
RELATIONSHIPS: {Team 33 fans: -44, Lacey Dahl (coach): -15, Quinn Kendrick (coach): -5, Ruth Fairbanks (gm): -5, Delphine Mikkelsen (gm): -5}
CAREER: [elected 38; recalled 40]
DECISION_LOG: [38: fired coach Quinn Kendrick (new owner cleaned house); 38: fired gm Ruth Fairbanks (new owner cleaned house); 40: blamed Lacey Dahl for the exile; 40: was recalled]
```
### GM Lola Akana  (Team 42, gm)
```yaml
IDENTITY: [Lola Akana, age 61, from Columbus OH; Came up through the personnel department]
SOUL (fixed): [+ Master Trader, - Draft-Day Disaster]
PERSONALITY: [Dealmaker] wants the best contract in every negotiation; fears being outmaneuvered
  - allowed by her soul: Dealmaker, Gambler, Cold Realist, Talent Hawk; right now she is clear-eyed (-0.19)
RATINGS:
  - scouting: 19  (sees herself at 18)   -> -0.95 rating points on her team's rookie each year
  - negotiation: 52  (sees herself at 51)   -> 1% fewer contract expiries
  - evaluation: 56  (sees herself at 55)   (no on-field effect yet)
  - trades: 69  (sees herself at 67, doubting)   (no on-field effect yet)
  - cap_sense: 48  (sees herself at 45, doubting)   (no on-field effect yet)
  - pressure thresholds: exile 65, contract 72, spotlight 27, loyalty 42
TRAJECTORY: [age 60: 48; age 61: 49; peak 49 at 61; now 49]
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [hired 38]
DECISION_LOG: [none yet]
```
**A recall vote as the Archive logs it:**

```
year: 40
event: recall_vote
team: 33
trigger: approval
approval: 0.378
recall_share: 0.513
result: recalled
owner: Esperanza Caldwell
replacement: Amina Kawamoto
candidates: ['Kora Amundsen', 'Nova Coleridge', 'Teagan Forsythe', 'Amina Kawamoto', 'Echo Nakamura']
capital: 0.521
```


## A fanbase and the press that covers it

### Fanbase of Team 02  (Front-Runners)
```yaml
IDENTITY: [Team 02 fans; market size 48 of 100]
PERSONALITY: [Front-Runners] wants winners; fears a long losing stretch; picks owners who are strong on ambition
ARCHETYPES: [+ Demanding, - Indifferent]
RATINGS:
  - loyalty: 58
  - expectations: 84   (born at 69; drifts with results, within +/-15)
  - passion: 42
  - volatility: 69
  - media_trust: 55
  - approval of the owner: 60%
  - Fan Capital: 0.63  (recall immunity; worth 3.9 points on a recall vote)
  - what the press did to approval last season: +0.1 points
  - pressure thresholds: exile 74, losing 49, scandal 59, spotlight 50
RELATIONSHIPS: {Alana Cruz (owner): -43, Galina Quillen (owner): -43, Fiona Valdez (owner): -30, Adriana Flanagan (owner): +9, Treasure Calloway (owner): +23}
DECISION_LOG: [3 earlier; 9: kept the owner; 16: kept the owner; 17: voted to recall the owner; 18: voted to recall the owner; 25: kept the owner; 33: kept the owner]
```
### Fanbase of Team 06  (Gloomy Realists)
```yaml
IDENTITY: [Team 06 fans; market size 47 of 100]
PERSONALITY: [Gloomy Realists] wants honesty; fears being fooled again; picks owners who are strong on business
ARCHETYPES: [+ Hang On Every Word, - Easily Pleased]
RATINGS:
  - loyalty: 35
  - expectations: 26   (born at 41; drifts with results, within +/-15)
  - passion: 37
  - volatility: 28
  - media_trust: 57
  - approval of the owner: 55%
  - Fan Capital: 0.41  (recall immunity; worth 0.0 points on a recall vote)
  - what the press did to approval last season: -0.4 points
  - pressure thresholds: exile 37, losing 45, scandal 56, spotlight 34
RELATIONSHIPS: {Evangeline Gentry (owner): -48, Tamsin Castellano (owner): -28, Alexis Herrera (owner): -28, Teagan Sheridan (owner): -28, Colette Christensen (owner): -28, Yelena Eberhardt (owner): -28, Kirsten Tillman (owner): -28, Anika Morrow (owner): -28, Petra Sutherland (owner): +1, Vivian Blackwood (owner): +18}
DECISION_LOG: [7 earlier; 19: voted to recall the owner; 22: voted to recall the owner; 25: kept the owner; 33: voted to recall the owner; 36: voted to recall the owner; 38: voted to recall the owner]
```
### Fanbase of Team 14  (Die-Hards)
```yaml
IDENTITY: [Team 14 fans; market size 70 of 100]
PERSONALITY: [Die-Hards] wants a team that is theirs; fears a sale or a move; picks owners who are strong on popularity
ARCHETYPES: [+ Fanatical, - Steady Hands]
RATINGS:
  - loyalty: 77
  - expectations: 57   (born at 49; drifts with results, within +/-15)
  - passion: 83
  - volatility: 34
  - media_trust: 60
  - approval of the owner: 68%
  - Fan Capital: 0.67  (recall immunity; worth 5.0 points on a recall vote)
  - what the press did to approval last season: +2.1 points
  - pressure thresholds: exile 35, losing 55, scandal 43, spotlight 60
RELATIONSHIPS: {Haruka Zamora (owner): -66, Catalina Davenport (owner): -52, Gabriela Farrow (owner): -19, Lourdes Jankowski (owner): -19, Malia Kasprzak (owner): +1, Emani Hammond (owner): +2}
DECISION_LOG: [4 earlier; 17: kept the owner; 19: voted to recall the owner; 21: kept the owner; 23: kept the owner; 27: kept the owner; 35: kept the owner]
```
### The DFL Wire  (national, league-wide; active)
```yaml
IDENTITY: [The DFL Wire, national outlet; byline Ivy Kimura]
PERSONALITY: [Statistician] wants being right; fears being wrong in public
ARCHETYPES: [+ Usually Right, - Dry as Dust]
RATINGS:
  - accuracy: 75
  - sensationalism: 36
  - reach: 69
  - access: 48
  - independence: 41
  - Credibility: 42  (the currency: it weights this outlet's say in a team's coverage)
  - forecast record (mean miss, win%): 35: 0.11, 36: 0.13, 37: 0.12, 38: 0.12, 39: 0.11, 40: 0.11
  - pressure thresholds: spotlight 38, access 54, irrelevance 56
RELATIONSHIPS: {}  # none yet; filled by Interactions
DECISION_LOG: [none yet]
```
### League Line  (national, league-wide; active)
```yaml
IDENTITY: [League Line, national outlet; byline Eden Garrison]
PERSONALITY: [Contrarian] wants the take nobody else has; fears agreeing with everyone
ARCHETYPES: [+ Everywhere, - Owner's Mouthpiece]
RATINGS:
  - accuracy: 41
  - sensationalism: 64
  - reach: 77
  - access: 45
  - independence: 39
  - Credibility: 32  (the currency: it weights this outlet's say in a team's coverage)
  - forecast record (mean miss, win%): 35: 0.15, 36: 0.14, 37: 0.16, 38: 0.11, 39: 0.15, 40: 0.14
  - pressure thresholds: spotlight 55, access 62, irrelevance 95
RELATIONSHIPS: {}  # none yet; filled by Interactions
DECISION_LOG: [none yet]
```
### Team 25 Sports Desk  (local, Team 25; active)
```yaml
IDENTITY: [Team 25 Sports Desk, local outlet; byline Jada Rourke]
PERSONALITY: [Homer] wants the team's love; fears losing her access
ARCHETYPES: [+ Headline Chaser, - Nobody Reads It]
RATINGS:
  - accuracy: 51
  - sensationalism: 66
  - reach: 42
  - access: 62
  - independence: 61
  - Credibility: 75  (the currency: it weights this outlet's say in a team's coverage)
  - forecast record (mean miss, win%): 35: 0.10, 36: 0.00, 37: 0.00, 38: 0.07, 39: 0.05, 40: 0.02
  - pressure thresholds: spotlight 44, access 50, irrelevance 67
RELATIONSHIPS: {}  # none yet; filled by Interactions
DECISION_LOG: [none yet]
```
**An outlet that folded (the Archive keeps the card):**

### Team 38 Sideline  (local, Team 38; folded)
```yaml
IDENTITY: [Team 38 Sideline, local outlet; byline Priya Alvarado]
PERSONALITY: [Gossip] wants the leak; fears a dead story
ARCHETYPES: [+ Headline Chaser, - Nobody Reads It]
RATINGS:
  - accuracy: 40
  - sensationalism: 56
  - reach: 38
  - access: 49
  - independence: 47
  - Credibility: 10  (the currency: it weights this outlet's say in a team's coverage)
  - forecast record (mean miss, win%): 8: 0.17, 9: 0.14, 10: 0.35, 12: 0.17, 14: 0.25, 15: 0.22
  - pressure thresholds: spotlight 52, access 48, irrelevance 42
RELATIONSHIPS: {}  # none yet; filled by Interactions
DECISION_LOG: [none yet]
```
```
year: 5
event: outlet_folded
outlet: Team 21 Press
kind: local
team: 21
credibility: 16.4
replacement: Team 21 Sports Desk
```


## Scenes as the Archive records them

Each firing, recall vote and exile determination is a scene: every party gives its own claim, and the evidence section says, from the engine's own numbers, which claims hold. The scenes never change an outcome (the check script proves a league plays out identically with them on or off); they explain it, and they move relationships and decision logs.

**An exile determination**

```
EVENT 40-exile_determination-44-1  (Team 44; exile determination; finished fifth in the division)
├── Owner claims: Cleo Oakley (Legacy Builder): "Fifth in the division, and I will say who is to blame: Rafaela Hightower. She built a roster that was 0.0 deviations above the league's average."  [not supported by the record]
├── Coach claims: Grace Fontaine (Players' Coach): "I was handed a roster 0.1 deviations above average and the schedule did the rest."  [not supported by the record]
├── GM claims: Rafaela Hightower (Dealmaker): "The roster was 3 of 5 in this division on paper. The record, 17%, was 31% below what it should have been."  [supported by the record]
├── The fans claim: Team 44 fans: "We stand by our own, and we have 59 points of goodwill banked. This town wanted a team that is theirs."  [supported by the record]
├── Press claims: Team 44 Press (Watchdog): "We had them at 58%. They finished 17%. Nobody saw this coming."  [not supported by the record]
└── Evidence supports: Exile followed under-delivery against the roster.  (record 17%, roster predicts 48%, roster +0.0 deviations from average)
    Outcome: Team 44 is exiled for next season
```

**A firing the record backs**

```
EVENT 40-firing-26-2  (Team 26; firing; owner fired the gm (results))
├── Owner claims: Agnes Yoder (Showwoman): "the roster should have won about 43% and they won 29%. I trusted her with the roster; I had no patience left."  [supported by the record]
├── GM claims: Cassidy Delgado (Dealmaker): "I built the roster and she lost games the roster should have won: 29% on a team that rates 43%."  [supported by the record]
├── Coach claims: Janelle Mathis (Survivor): "I coached what I was handed, a roster 0.6 deviations below average."  [supported by the record]
├── The fans claim: Team 26 fans: "They finished 29%. We wanted a title every year and we feared being ignored; that is what we got."  [supported by the record]
└── Evidence supports: The firing is backed by the record, and the roster does not excuse it: it was a thin roster.  (record 29%, roster predicts 43%, roster -0.6 deviations from average)
    Outcome: Cassidy Delgado fired; replaced by a new gm
```

**A harsh firing (the roster explains the record)**

```
EVENT 38-firing-28-2  (Team 28; firing; owner fired the gm (results))
├── Owner claims: Nia Iverson (Showwoman): "the roster should have won about 56% and they won 29%. I trusted her with the roster; I had no patience left."  [supported by the record]
├── GM claims: Adriana Maynard (Cold Realist): "I built the roster and she lost games the roster should have won: 29% on a team that rates 56%."  [supported by the record]
├── Coach claims: Naomi Kawamoto (Survivor): "I coached what I was handed, a roster 1.2 deviations above average."  [not supported by the record]
├── The fans claim: Team 28 fans: "We stand by our own, and we have 44 points of goodwill banked. This town wanted a team that is theirs."  [not supported by the record]
└── Evidence supports: A harsh firing: the record was poor (29%), but the roster she built was not thin, so the shortfall was on the field.  (record 29%, roster predicts 56%, roster +1.2 deviations from average)
    Outcome: Adriana Maynard fired; replaced by a new gm
```

**A new CEO's sweep**

```
EVENT 40-firing-33-2  (Team 33; firing; owner fired the gm (new owner cleaned house))
├── Owner claims: Amina Kawamoto (Patient Steward): "New owner, new staff. I wanted a slow, sound build and I wasn't going to ask Delphine Mikkelsen for it."  [supported by the record]
├── GM claims: Delphine Mikkelsen (Gambler): "I built the roster and she lost games the roster should have won: 39% on a team that rates 57%."  [supported by the record]
├── Coach claims: Lacey Dahl (Disciplinarian): "I coached what I was handed, a roster 1.3 deviations above average."  [not supported by the record]
├── The fans claim: Team 33 fans: "We stand by our own, and we have 52 points of goodwill banked. This town wanted a team that is theirs."  [not supported by the record]
├── Press claims: Team 33 Sports Desk (Homer): "We had them at 42%. They finished 39%. We called it."  [supported by the record]
└── Evidence supports: A sweep: the new owner cleared the staff on arrival, whatever the record (39% against 57% on paper).  (record 39%, roster predicts 57%, roster +1.3 deviations from average)
    Outcome: Delphine Mikkelsen fired; replaced by a new gm
```

**A recall vote that removes a CEO**

```
EVENT 40-recall_vote-33-1  (Team 33; recall vote; vote triggered by approval)
├── Owner claims: Esperanza Caldwell (Meddler): "I thought we were at 41%. This is what the papers did to me, not what I did to this team."  [not supported by the record]
├── The fans claim: Team 33 fans: "We stand by our own, and we have 52 points of goodwill banked. This town wanted a team that is theirs." We wanted an owner strong on popularity and we chose Amina Kawamoto.  [not supported by the record]
├── Press claims: Team 33 Sports Desk (Homer): "We had them at 42%. They finished 39%. We called it."  [supported by the record]
├── New owner claims: Amina Kawamoto (Patient Steward): "Five of us stood. The fans wanted strength on popularity and picked me. I want a slow, sound build."  [supported by the record]
└── Evidence supports: 51.3% voted to recall (a majority of the 1,000,000 fans is needed): recalled.  (record 39%, roster predicts 57%, roster +1.3 deviations from average)
    Outcome: Esperanza Caldwell recalled; Amina Kawamoto elected from 5 candidates
```

**A recall vote the CEO survives**

```
EVENT 40-recall_vote-48-1  (Team 48; recall vote; vote triggered by rotation)
├── Owner claims: Elena Haskell (Opportunist): "I told you we were at 64%. The fans know what I stand for: a quick profit."  [supported by the record]
├── The fans claim: Team 48 fans: "They finished 67%. We wanted honesty and we feared being fooled again; we have no complaint about the record, but we are watching."  [not supported by the record]
├── Press claims: Team 48 Insider (Contrarian): "We had them at 58%. They finished 67%. Nobody saw this coming."  [not supported by the record]
└── Evidence supports: 20.6% voted to recall (a majority of the 1,000,000 fans is needed): the owner survives.  (record 67%, roster predicts 44%, roster -0.5 deviations from average)
    Outcome: Elena Haskell survives
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
  "role": "owner",
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
  }
 },
 "context": {
  "record_this_season": 0.5,
  "record_last_season": null,
  "exiled_this_year": false,
  "fan_approval_of_you": 0.666,
  "facing_a_recall_vote_this_year": true,
  "you_are_a_new_owner": false,
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
   "pressure_on_her": 0.0
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
 "instructions": "Reply with the id of exactly one option, and optionally a short reason in plain words."
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
  "role": "owner",
  "name": "Priya Pruitt",
  "trait": "Patient Steward",
  "wants": "a slow, sound build",
  "fears": "panic",
  "ratings": {
   "patience": 61.9,
   "ambition": 34.7,
   "involvement": 43.6,
   "popularity": 49.7,
   "business": 50.1
  },
  "pressure": {
   "recall": 51,
   "media": 31,
   "losing": 51,
   "subsidy": 77
  }
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
 "instructions": "Reply with the id of exactly one option, and optionally a short reason in plain words."
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

**Core personalities (all rostered players):** Diplomat 515, Competitor 440, Grinder 375, Perfectionist 320, Showman 211, Quiet Leader 128, Free Spirit 120, Hothead 85, Mercenary 36, Loyalist 26

**Most common positive archetypes:** Well-Rounded 681, Ballhawk 115, Road Grader 107, Edge Terror 99, Pass-Pro Wall 94, Burner 85, Route Technician 80, Glue Hands 79

**Coach effect across the 48 teams:** average -0.01, spread (sd) 0.38, best +0.74, worst -1.07 points of expected margin. For scale, team talent has a spread of about 3 to 4 points.

**Personality shifts:** 2164 of 11069 players have changed personality at least once in 40 seasons.

**Standing in the media's eyes** (everyone who ever lived, by what the media calls her now): known 229, respected 104, star 36, Hall of Famer 14, legend 1. 14 are in the Hall of Fame.

**Fan cultures:** Die-Hards 13, Entitled 11, Party Crowd 9, Gloomy Realists 7, Long-Suffering 5, Front-Runners 3

**Fan Capital:** average 0.53, from 0.41 to 0.67; the most it can buffer a recall vote is 15 points.

**The press on approval, last season:** average 0.9 points either way, largest 3.2 (the cap is 3 before market size and trust).

**Outlets:** 52 active (4 national, one local beat per team); credibility averages 43, from 17 to 75; 14 have folded and been replaced in 40 seasons.

**Scenes:** 1106 in 40 seasons ([('recall_vote', 546), ('exile_determination', 320), ('firing', 240)]). Firings by ruling: fair 150, sweep 69, harsh 15, unfounded 6.

**Recall votes:** 546 in 40 seasons (13.7 a year); 173 CEOs recalled (4.3 a year), 32% of votes. CEOs retire on their own too: 151 so far.

**Firings:** 154 coaches and 86 GMs fired in 40 seasons.

**Coaches so far:** 370 hired and 305 retired in 40 seasons; 17 coaches and 13 GMs are between jobs right now.

**Players with cards:** 2388 active or unsigned, 8813 retired.
