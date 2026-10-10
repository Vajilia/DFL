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

### Candace Pinkerton II  (QB, Team 22)
```yaml
IDENTITY: [Candace Pinkerton II, age 31, from Milwaukee WI; Came up through the academy system]
ORIGIN: [born 2034-06-14; Penn State (tier 1); senior year 222/365, 2643 yds, 16 TD, 9 INT]
BIO (code): Out of Milwaukee WI, Candace Pinkerton II is a product of the academy system. She played at Penn State and as a senior threw for 2,643 yards and 16 touchdowns on 222 completions. Team 22 took her with pick 12 in 31, in the first round. Teammates call her a competitor who hates to lose at anything; she wants to win everything in front of her and fears being outworked.
SOUL (fixed): [+ Field General, - Wild Arm]  temperament family: command
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
  - allowed by her soul: Quiet Leader, Competitor, Diplomat, Perfectionist; right now she is overconfident (+0.60)
RATINGS: [overall 88, Franchise player]
  - accuracy: 83  (sees herself at 87, overrating)
  - arm: 90  (sees herself at 96, overrating)
  - awareness: 95  (sees herself at 99, overrating)
  - pressure thresholds: exile 75, contract 67, spotlight 62, loyalty 68
RECOGNITION: [known; esteem 7.9; honors: Champion, All-League x3]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 31 (pick 12); became Perfectionist (was Competitor) 37; became Competitor (was Perfectionist) 40]
DECISION_LOG: [none yet]
```
### Concetta Reyes II  (WR, Team 21)
```yaml
IDENTITY: [Concetta Reyes II, age 24, from Dayton OH; Junior-college transfer]
ORIGIN: [born 2041-11-11; Miami (FL) (tier 1); senior year 104 rec, 1711 yds, 13 TD]
BIO (code): Out of Dayton OH, Concetta Reyes II is a junior-college transfer who made the most of her second chance. She played at Miami (FL) and as a senior caught 104 passes for 1,711 yards and 13 touchdowns. Team 21 took her with pick 2 in 38, in the first round. Teammates call her a free spirit who plays loose; she wants freedom and adventure along the way and fears a rigid system.
SOUL (fixed): [+ Burner, - Drop-Prone]  temperament family: flash
PERSONALITY: [Free Spirit] wants freedom and adventure along the way; fears a rigid system
  - allowed by her soul: Showman, Free Spirit, Competitor, Mercenary; right now she is full of doubt (-1.00)
RATINGS: [overall 82, Franchise player]
  - route: 88  (sees herself at 76, doubting)
  - hands: 70  (sees herself at 60, doubting)
  - speed: 87  (sees herself at 78, doubting)
  - pressure thresholds: exile 60, contract 64, spotlight 28, loyalty 45
RECOGNITION: [unknown; esteem 2.5; honors: All-League]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 38 (pick 2)]
DECISION_LOG: [none yet]
```
### Zoe Lindqvist II  (OL, Team 11)
```yaml
IDENTITY: [Zoe Lindqvist II, age 30, from Omaha NE; Junior-college transfer]
ORIGIN: [born 2035-06-24; Baylor (tier 1); senior year 13 starts, 1 sacks allowed, 51 pancakes]
BIO (code): Zoe Lindqvist II grew up in Omaha NE, a junior-college transfer who made the most of her second chance. She played at Baylor and as a senior started 13 games and gave up 1 sacks. Team 41 took her with pick 5 in 32, in the first round. Teammates call her the one who keeps the room together; she wants a calm, united team and fears locker-room civil war.
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is clear-eyed (+0.06)
RATINGS: [overall 94, Franchise player]
  - pass_block: 95  (sees herself at 97)
  - run_block: 93  (sees herself at 92)
  - pressure thresholds: exile 51, contract 75, spotlight 54, loyalty 75
RECOGNITION: [star; esteem 24.2; honors: All-League x6, Player of the Year x3]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 32 (pick 5)]
DECISION_LOG: [none yet]
```
### Alina Kowalski II  (DL, Team 36)
```yaml
IDENTITY: [Alina Kowalski II, age 28, from Accra Ghana; Junior-college transfer]
ORIGIN: [born 2037-07-07; Purdue (tier 1); senior year 67 tkl, 13 TFL, 8 sacks]
BIO (code): Alina Kowalski II grew up in Accra Ghana, a junior-college transfer who made the most of her second chance. She played at Purdue and as a senior made 67 tackles, 13 for loss, and 8 sacks. Team 36 took her with pick 2 in 35, in the first round. Teammates call her the one who keeps the room together; she wants a calm, united team and fears locker-room civil war.
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is full of doubt (-1.00)
RATINGS: [overall 99, Franchise player]
  - pass_rush: 100  (sees herself at 88, doubting)
  - run_stop: 97  (sees herself at 90, doubting)
  - pressure thresholds: exile 56, contract 48, spotlight 50, loyalty 57
RECOGNITION: [respected; esteem 9.1; honors: All-League x4]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 35 (pick 2)]
DECISION_LOG: [none yet]
```
### Tilda Delgado II  (CB, Team 18)
```yaml
IDENTITY: [Tilda Delgado II, age 27, from Kansas City MO; Walk-on turned starter]
ORIGIN: [born 2038-01-06; West Virginia (tier 1); senior year 37 tkl, 3 INT, 11 PD]
BIO (code): Out of Kansas City MO, Tilda Delgado II is a walk-on who earned her scholarship and then her starting job. She played at West Virginia and as a senior made 37 tackles with 3 interceptions and 11 passes defended. Team 18 took her with pick 18 in 35, in the first round. Teammates call her never happier than when the lights are on; she wants the spotlight and a signature moment and fears being ignored by the media.
SOUL (fixed): [+ Shutdown Corner, - Avoids Contact]  temperament family: flash
PERSONALITY: [Showman] wants the spotlight and a signature moment; fears being ignored by the media
  - allowed by her soul: Showman, Free Spirit, Competitor, Mercenary; right now she is full of doubt (-0.27)
RATINGS: [overall 90, Franchise player]
  - coverage: 95  (sees herself at 93, doubting)
  - ball_skills: 83  (sees herself at 80, doubting)
  - tackling: 82  (sees herself at 82)
  - pressure thresholds: exile 34, contract 33, spotlight 89, loyalty 38
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 35 (pick 18)]
DECISION_LOG: [none yet]
```
### Emani Rourke  (K, Team 18)
```yaml
IDENTITY: [Emani Rourke, age 36, from Reno NV; Came up through the academy system]
ORIGIN: [born 2029-07-01; Penn State (tier 1); senior year 24/29 FG, long 46]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Grinder] wants to earn every inch; fears being handed nothing and losing it anyway
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is full of doubt (-0.72)
RATINGS: [overall 90, Franchise player]
  - power: 88  (sees herself at 81, doubting)
  - accuracy: 92  (sees herself at 88, doubting)
  - pressure thresholds: exile 83, contract 69, spotlight 58, loyalty 78
RECOGNITION: [star; esteem 16.3; honors: All-League x8]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```

## A young rookie and a veteran

### Georgia Forsythe II  (RB, Team 31)
```yaml
IDENTITY: [Georgia Forsythe II, age 22, from Kansas City MO; Came up through the academy system]
ORIGIN: [born 2043-07-11; Mississippi State (tier 1); senior year 220 att, 1201 yds, 12 TD, 30 rec]
BIO (code): Out of Kansas City MO, Georgia Forsythe II is a product of the academy system. She played at Mississippi State and as a senior ran for 1,201 yards and 12 touchdowns. Team 31 took her with pick 1 in 40, in the first round. Teammates call her the one who keeps the room together; she wants a calm, united team and fears locker-room civil war.
SOUL (fixed): [+ Well-Rounded, - Goes Down Easy]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is overconfident (+0.89)
RATINGS: [overall 80, Star]
  - elusive: 82  (sees herself at 88, overrating)
  - power: 77  (sees herself at 85, overrating)
  - hands: 81  (sees herself at 88, overrating)
  - pressure thresholds: exile 36, contract 36, spotlight 64, loyalty 92
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 40 (pick 1)]
DECISION_LOG: [none yet]
```
### Eliana Wagner II  (P, Team 19)
```yaml
IDENTITY: [Eliana Wagner II, age 32, from Pittsburgh PA; Small-college standout]
ORIGIN: [born 2033-04-25; Stanford (tier 1); senior year 58 punts, 43.2 avg, 28 inside the 20]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Grinder] wants to earn every inch; fears being handed nothing and losing it anyway
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is full of doubt (-0.71)
RATINGS: [overall 96, Franchise player]
  - power: 94  (sees herself at 88, doubting)
  - accuracy: 100  (sees herself at 94, doubting)
  - pressure thresholds: exile 77, contract 55, spotlight 42, loyalty 46
RECOGNITION: [known; esteem 8.0; honors: Champion, All-League x3]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 30 (pick 164); became Grinder (was Diplomat) 32]
DECISION_LOG: [none yet]
```

## A player whose personality changed (her soul stayed the same)

### Maeve Farrow  (S, Team 05)
```yaml
IDENTITY: [Maeve Farrow, age 34, from Sacramento CA; Overlooked recruit]
ORIGIN: [born 2031-09-04; Arkansas (tier 1); senior year 78 tkl, 5 INT, 14 PD]
BIO (code): Maeve Farrow grew up in Sacramento CA, an overlooked recruit who has played with a chip on her shoulder since. She played at Arkansas and as a senior made 78 tackles with 5 interceptions and 14 passes defended. Team 42 took her with pick 5 in 28, in the first round. Teammates call her a perfectionist who watches film long after the others leave; she wants flawless execution and fears the one mistake everyone remembers.
SOUL (fixed): [+ Deep Patroller, - Poor Ball Skills]  temperament family: command
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
  - allowed by her soul: Quiet Leader, Competitor, Diplomat, Perfectionist; right now she is overconfident (+1.00)
RATINGS: [overall 70, Starter]
  - coverage: 75  (sees herself at 86, overrating)
  - ball_skills: 58  (sees herself at 67, overrating)
  - tackling: 74  (sees herself at 81, overrating)
  - pressure thresholds: exile 54, contract 57, spotlight 5, loyalty 21
RECOGNITION: [respected; esteem 11.7; honors: All-League x5, Player of the Year]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 28 (pick 5); became Competitor (was Perfectionist) 34; became Perfectionist (was Competitor) 37; became Competitor (was Perfectionist) 39]
DECISION_LOG: [none yet]
```

## A retired player (cards are kept for the Archive)

### Yelena McAllister  (K, retired)
```yaml
IDENTITY: [Yelena McAllister, age 30, from Tulsa OK; Overlooked recruit]
ORIGIN: [born 2003-03-18; Oklahoma (tier 1); senior year 28/32 FG, long 54]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is full of doubt (-0.98)
RATINGS: [overall 100, Franchise player]
  - power: 100  (sees herself at 94, doubting)
  - accuracy: 100  (sees herself at 91, doubting)
  - pressure thresholds: exile 60, contract 52, spotlight 79, loyalty 47
RECOGNITION: [known; esteem 4.5; honors: All-League x2]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [retired 8]
DECISION_LOG: [none yet]
```

## Head coaches: the most esteemed ever, a typical coach and a weak one

### Coach Tamsin Haskell  (retired)  -  HALL OF FAMER
```yaml
IDENTITY: [Tamsin Haskell, age 53, from Knoxville TN; Coordinator who got her first shot]
SOUL (fixed): [+ Taskmaster, - Flat Locker Room]
PERSONALITY: [Survivor] wants another contract year; fears the CEO's phone call
  - allowed by her soul: Disciplinarian, Steady Hand, Survivor, Tactician; right now she is full of doubt (-1.00)
RATINGS:
  - offense: 53  (sees herself at 43, doubting)   -> +0.03 points of margin
  - defense: 66  (sees herself at 54, doubting)   -> +0.25 points of margin
  - development: 59  (sees herself at 48, doubting)   -> +0.05 rating points per year to each young player
  - gamecraft: 53  (sees herself at 44, doubting)   (no on-field effect yet)
  - discipline: 87  (sees herself at 77, doubting)   (no on-field effect yet)
  - motivation: 42  (sees herself at 34, doubting)   (no on-field effect yet)
  - pressure thresholds: exile 44, contract 80, spotlight 71, loyalty 44
TRAJECTORY: [age 34: 58; age 37: 57; age 40: 58; age 43: 58; age 46: 57; age 49: 56; age 52: 60; peak 60 at 53; now 60]
RECOGNITION: [Hall of Famer; esteem 24.0; honors: Coach of the Year x3, Champion, Hall of Fame]
RELATIONSHIPS: {Maribel Brandt (CEO): -29, Hattie Dubois (CEO): -1, Juana Hargrove (gm): +0}
CAREER: [hired 0; promoted 5; hired 5; fired 16; hired 16; fired 18; hired 19; retired 21; hof_ballot 24]
DECISION_LOG: [17 earlier; 16: vetoed Fatima Maldonado's pass scheme; 16: was fired by Maribel Brandt; 17: proposed the run scheme; 18: proposed the run scheme; 20: proposed the pass scheme; 21: proposed the pass scheme]
```
### Coach Soledad Whitlock  (Team 47)
```yaml
IDENTITY: [Soledad Whitlock, age 52, from Memphis TN; Long-time position coach]
SOUL (fixed): [+ Inspirer, - Costly Decisions]
PERSONALITY: [Players' Coach] wants a locker room that plays hard for her; fears losing the room
  - allowed by her soul: Players' Coach, Developer, Innovator, Survivor; right now she is full of doubt (-0.55)
RATINGS:
  - offense: 62  (sees herself at 57, doubting)   -> +0.15 points of margin
  - defense: 48  (sees herself at 44, doubting)   -> -0.18 points of margin
  - development: 63  (sees herself at 58, doubting)   -> +0.06 rating points per year to each young player
  - gamecraft: 38  (sees herself at 32, doubting)   (no on-field effect yet)
  - discipline: 49  (sees herself at 45, doubting)   (no on-field effect yet)
  - motivation: 75  (sees herself at 71, doubting)   (no on-field effect yet)
  - pressure thresholds: exile 62, contract 52, spotlight 70, loyalty 61
TRAJECTORY: [age 45: 48; age 46: 50; age 47: 51; age 48: 54; age 49: 54; age 50: 54; age 51: 56; age 52: 56; peak 56 at 51; now 56]
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {Giselle Haskell (CEO): -6}
CAREER: [entered_coaching 32; hired 33]
DECISION_LOG: [4 earlier; 37: vetoed Noor Kaplan's blitz scheme; 37: lost Noor Kaplan as defensive coordinator to a head-coaching job; 38: vetoed Emani Novak's blitz scheme; 39: vetoed Janelle Holmgren's run scheme; 39: vetoed Emani Novak's coverage scheme; 39: was exiled with her team]
```
### Coach Amelia Mulvaney  (Team 41)
```yaml
IDENTITY: [Amelia Mulvaney, age 59, from Dublin Ireland; Coordinator who got her first shot]
SOUL (fixed): [+ Taskmaster, - Leaky Defense]
PERSONALITY: [Steady Hand] wants sustained quiet success; fears a collapse nobody saw coming
  - allowed by her soul: Disciplinarian, Steady Hand, Survivor, Tactician; right now she is clear-eyed (-0.15)
RATINGS:
  - offense: 40  (sees herself at 38)   -> -0.29 points of margin
  - defense: 27  (sees herself at 26)   -> -0.60 points of margin
  - development: 32  (sees herself at 31)   -> -0.19 rating points per year to each young player
  - gamecraft: 54  (sees herself at 52, doubting)   (no on-field effect yet)
  - discipline: 72  (sees herself at 73)   (no on-field effect yet)
  - motivation: 63  (sees herself at 60, doubting)   (no on-field effect yet)
  - pressure thresholds: exile 44, contract 55, spotlight 44, loyalty 82
TRAJECTORY: [age 56: 48; age 57: 49; age 58: 49; age 59: 48; peak 49 at 57; now 48]
RECOGNITION: [known; esteem 4.3; honors: Coach of the Year]
RELATIONSHIPS: {Sadie Villanueva (CEO): +4}
CAREER: [entered_coaching 36; hired 37]
DECISION_LOG: [37: fired Kora Holmgren as defensive coordinator; 37: hired Penelope Crenshaw as offensive coordinator; 37: hired Julia Atwood as defensive coordinator; 40: vetoed Penelope Crenshaw's pass scheme; 40: hired Zadie Zeller as offensive coordinator]
```

**A coach between jobs (she lives on and may be offered to a CEO again):**

### Coach Willa Brockway  (between jobs)
```yaml
IDENTITY: [Willa Brockway, age 52, from Tallahassee FL; Rose through the assistant ranks]
SOUL (fixed): [+ Defensive Architect, - Costly Decisions]
PERSONALITY: [Disciplinarian] wants order, rules and no excuses; fears chaos and ego
  - allowed by her soul: Disciplinarian, Tactician, Steady Hand, Survivor; right now she is overconfident (+0.43)
RATINGS:
  - offense: 57  (sees herself at 60, overrating)   -> +0.04 points of margin
  - defense: 60  (sees herself at 63, overrating)   -> +0.07 points of margin
  - development: 50  (sees herself at 54, overrating)   -> -0.04 rating points per year to each young player
  - gamecraft: 44  (sees herself at 46, overrating)   (no on-field effect yet)
  - discipline: 46  (sees herself at 51, overrating)   (no on-field effect yet)
  - motivation: 54  (sees herself at 57, overrating)   (no on-field effect yet)
  - pressure thresholds: exile 83, contract 61, spotlight 81, loyalty 57
TRAJECTORY: [age 39: 48; age 41: 49; age 43: 51; age 45: 50; age 47: 49; age 49: 49; age 51: 51; peak 52 at 52; now 52]
RECOGNITION: [unknown; esteem 0.4; honors: Coach of the Year]
RELATIONSHIPS: {Tatiana Beaumont (CEO): -27, Junie Avery (CEO): -20, Delphine Crawley (CEO): +4}
CAREER: [entered_coaching 26; hired 26; fired 40]
DECISION_LOG: [10 earlier; 35: vetoed Alexis Larkin's pass scheme; 35: vetoed Mireya Jacobsen's coverage scheme; 36: was exiled with her team; 39: vetoed Mireya Jacobsen's blitz scheme; 40: was exiled with her team; 40: was fired by Tatiana Beaumont]
```

## Recognition: who the media called a legend, and the Hall of Fame

Nobody was made a legend. These are the Archive's own entries, in order:

```
year 9: legend contested: Valentina Chavez (coach), esteem 20.2, 35% of outlets
year 9: legend contested: Alma Andersen (player), esteem 22.2, 31% of outlets
year 12: legend contested: Iris Iverson (player), esteem 23.6, 39% of outlets
year 14: legend recognized: Janelle Amundsen (player), esteem 27.5, 100% of outlets
year 16: legend recognized: Tamsin Haskell (coach), esteem 24.0, 71% of outlets
year 19: legend recognized: Nina Lachance (coach), esteem 27.8, 100% of outlets
year 19: legend contested: Ingrid Ellison (gm), esteem 19.7, 56% of outlets
year 19: legend contested: Celeste Coleridge (owner), esteem 17.9, 39% of outlets
year 19: legend contested: Lupe Cordero (player), esteem 24.7, 33% of outlets
year 20: legend recognized: Ingrid Ellison (gm), esteem 20.3, 100% of outlets
year 20: legend recognized: Lupe Cordero (player), esteem 29.7, 100% of outlets
year 27: legend contested: Hattie Dubois (owner), esteem 17.9, 31% of outlets
```

**The Hall of Fame so far:**

| Year | Kind | Name | Esteem | Vote | Honors |
|---|---|---|---|---|---|
| 14 | player | Alma Andersen | 22.2 | 76% | All-League x7, Player of the Year x2 |
| 16 | player | Iris Iverson | 23.6 | 84% | All-League x8, Player of the Year x2 |
| 20 | player | Janelle Amundsen | 32.9 | 99% | All-League x8, Player of the Year x5 |
| 23 | gm | Ingrid Ellison | 20.3 | 99% | Executive of the Year x1, Champion x2 |
| 24 | coach | Tamsin Haskell | 24.0 | 96% | Coach of the Year x3, Champion x1 |
| 27 | coach | Nina Lachance | 21.7 | 86% | Coach of the Year x1, Champion x2 |
| 30 | player | Lupe Cordero | 31.8 | 99% | All-League x11, Player of the Year x5, Champion x2 |
| 35 | player | Paloma Brockway | 24.1 | 80% | All-League x7, Player of the Year x3, Champion x1 |
| 38 | player | Junie Pinkerton | 26.2 | 91% | All-League x8, Player of the Year x3 |

**The most esteemed player:**

### Janelle Amundsen  (OL, retired)
```yaml
IDENTITY: [Janelle Amundsen, age 33, from Juneau AK; Overlooked recruit]
ORIGIN: [born 2009-05-13; Northern Illinois (tier 2); senior year 13 starts, 1 sacks allowed, 50 pancakes]
BIO (code): Out of Juneau AK, Janelle Amundsen is an overlooked recruit who has played with a chip on her shoulder since. She played at Northern Illinois and as a senior started 13 games and gave up 1 sacks. Team 40 took her with pick 4 in 6, in the first round. Teammates call her loyal to a fault to whoever gives her a chance; she wants to be a franchise's one-club legend and fears being traded or cut.
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Loyalist] wants to be a franchise's one-club legend; fears being traded or cut
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is overconfident (+0.44)
RATINGS: [overall 89, Franchise player]
  - pass_block: 88  (sees herself at 90)
  - run_block: 90  (sees herself at 95, overrating)
  - pressure thresholds: exile 44, contract 48, spotlight 38, loyalty 66
RECOGNITION: [Hall of Famer; esteem 32.9; honors: All-League x8, Player of the Year x5, Hall of Fame]
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 6 (pick 4); retired 17; hof_ballot 20]
DECISION_LOG: [none yet]
```

## A CEO, a GM, and the Archive's first entries

### CEO Kenna Contreras  (Team 34, CEO)
```yaml
IDENTITY: [Kenna Contreras, age 65, from Dayton OH; Real-estate magnate]
SOUL (fixed): [+ Hands-On Leader, - Content With Mediocrity]
PERSONALITY: [Meddler] wants a hand in every decision; fears being irrelevant
  - allowed by her soul: Meddler, Legacy Builder, Glory Hunter, Patient Steward; right now she is overconfident (+0.37)
RATINGS:
  - patience: 50  (sees herself at 55, overrating)
  - ambition: 23  (sees herself at 27, overrating)
  - involvement: 76  (sees herself at 77)
  - popularity: 60  (sees herself at 65, overrating)
  - business: 38  (sees herself at 38)
  - fan approval right now: 41%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 44, media 48, losing 59, subsidy 54
METERS (hers alone; they end with her tenure):
  - Fan Rapport: 55  (somewhere in between)
  - Standing Among CEOs: 50  (somewhere in between)
  - Legacy: 12  (she will be forgotten)
PLEDGE: [standard] the share of a profit she puts back into the club
TRAJECTORY: [age 53: 49; age 55: 49; age 57: 50; age 59: 49; age 61: 49; age 63: 49; age 65: 49; peak 50 at 57; now 49]
RECOGNITION: [unknown; esteem 2.1; honors: none yet]
RELATIONSHIPS: {Catalina Saunders (coach): -21, Antonia Davenport (gm): -20, Rosalind Briggs (coach): -10, Thalia Duarte (coach): -1, Layla Boateng (coach): +4, Astrid Cabrera (coach): +4, Team 34 fans: +28}
CAREER: [elected 27]
DECISION_LOG: [18 earlier; 38: survived a recall vote; 39: pledged the standard share of profit to the club; 39: held firm against the boycott; 39: fired coach Catalina Saunders (results); 40: pledged the standard share of profit to the club; 40: held firm against the boycott]
```
### CEO Jocelyn Oakley  (Team 39, recalled)
```yaml
IDENTITY: [Jocelyn Oakley, age 62, from Dublin Ireland; Former player turned investor]
SOUL (fixed): [+ Patient Steward, - Absentee CEO]
PERSONALITY: [Patient Steward] wants a slow, sound build; fears panic
  - allowed by her soul: Patient Steward, Legacy Builder, Local Hero, Penny-Pincher; right now she is clear-eyed (-0.06)
RATINGS:
  - patience: 55  (sees herself at 53)
  - ambition: 52  (sees herself at 51)
  - involvement: 32  (sees herself at 33)
  - popularity: 33  (sees herself at 35, overrating)
  - business: 50  (sees herself at 46, doubting)
  - fan approval right now: 38%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 57, media 76, losing 58, subsidy 35
METERS (hers alone; they end with her tenure):
  - Fan Rapport: 47  (somewhere in between)
  - Standing Among CEOs: 50  (somewhere in between)
  - Legacy: 13  (she will be forgotten)
PLEDGE: [standard] the share of a profit she puts back into the club
TRAJECTORY: [age 62: 44; peak 44 at 62; now 44]
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {Team 39 fans: -43}
CAREER: [elected 39; recalled 40]
DECISION_LOG: [39: was elected by the fans of team 39; 40: pledged the standard share of profit to the club; 40: was recalled]
```
### GM Sunny Atwood  (Team 40, gm)
```yaml
IDENTITY: [Sunny Atwood, age 65, from Helsinki Finland; Hired away from another league]
SOUL (fixed): [+ Draft Whisperer, - Misjudges Players]
PERSONALITY: [Talent Hawk] wants the best young players; fears missing on a first-round pick
  - allowed by her soul: Talent Hawk, Gambler, Planner, Loyal Lieutenant; right now she is clear-eyed (-0.15)
RATINGS:
  - scouting: 94  (sees herself at 95)   -> +1.34 rating points on her team's rookie each year
  - negotiation: 63  (sees herself at 58, doubting)   -> 8% fewer contract expiries
  - evaluation: 35  (sees herself at 34)   (no on-field effect yet)
  - trades: 44  (sees herself at 45)   (no on-field effect yet)
  - cap_sense: 36  (sees herself at 34, doubting)   (no on-field effect yet)
  - pressure thresholds: exile 53, contract 63, spotlight 44, loyalty 35
TRAJECTORY: [just started]
RECOGNITION: [unknown; esteem 0.0; honors: none yet]
RELATIONSHIPS: {Giselle Eastwood (CEO): +4}
CAREER: [hired 40]
DECISION_LOG: [none yet]
```
**A recall vote as the Archive logs it:**

```
year: 40
event: recall_vote
team: 40
trigger: approval
approval: 0.384
recall_share: 0.512
result: recalled
owner: Daniela Rutledge
replacement: Giselle Eastwood
candidates: ['Maribel Lombardi', 'Sadie Peralta', 'Zelda Villanueva', 'Cassidy Briggs', 'Giselle Eastwood']
capital: 0.59
```


## A fanbase and the press that covers it

### Fanbase of Team 19  (Entitled)
```yaml
IDENTITY: [Team 19 fans; market size 22 of 100; the franchise's permanent card, it outlives every CEO]
PERSONALITY: [Entitled] wants a title every year; fears being ignored; picks CEOs who are strong on ambition
ARCHETYPES: [+ Demanding, - Steady Hands]
RATINGS:
  - loyalty: 46
  - expectations: 86   (born at 71; drifts with results, within +/-15)
  - passion: 56
  - volatility: 37
  - media_trust: 62
  - approval of the CEO: 65%
  - Fan Capital: 0.65  (recall immunity; worth 4.6 points on a recall vote)
  - what the press did to approval last season: +2.0 points
  - pressure thresholds: exile 70, losing 59, scandal 73, spotlight 57
METERS (this franchise's own; they rise and fall with what happens, and their resting level drifts):
  - Hope: 75  (next year is the year; resting level 63, since year 0)
  - Outrage: 21  (all calm; resting level 32, since year 0)
  - Grudge: 48  (somewhere in between; resting level 48, since year 0)
  - Homecoming Pull: 60  (the exile healed into pride; resting level 58, since year 14)
BOYCOTT: [off]
MEMORIES (fading):
  - 36: the championship  (remembered 71%)
  - 33: the club was sent into exile  (remembered 55%)
  - 34: the club came home from exile  (remembered 48%)
  - 33: the fans began to boycott  (remembered 38%)
  - 25: the club was sent into exile  (remembered 27%)
  - 26: the club came home from exile  (remembered 24%)
SPENDING_ASK: [fair] what the fans asked of the CEO's investment this year
RELATIONSHIPS: {Amelia Benavides (CEO): -47, Adaeze Oakley (CEO): -36, Evangeline Cruz (CEO): -33, Linnea Yamada (CEO): -33, Marisol Goldberg (CEO): -33, Alma Chambers (CEO): -33, Anneke Zeller (CEO): +23}
DECISION_LOG: [45 earlier; 36: asked for the fair level of investment; 36: kept the CEO; 37: asked for the fair level of investment; 38: asked for the fair level of investment; 39: asked for the fair level of investment; 40: asked for the fair level of investment]
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
  - approval of the CEO: 52%
  - Fan Capital: 0.41  (recall immunity; worth 0.0 points on a recall vote)
  - what the press did to approval last season: -1.3 points
  - pressure thresholds: exile 69, losing 57, scandal 56, spotlight 30
METERS (this franchise's own; they rise and fall with what happens, and their resting level drifts):
  - Outrage: 39  (all calm; resting level 36, since year 0)
  - Memory Keepers: 36  (last year is ancient history; resting level 36, since year 0)
  - Wallet Mood: 56  (somewhere in between; resting level 53, since year 0)
  - Grudge: 53  (somewhere in between; resting level 50, since year 2)
BOYCOTT: [off]
MEMORIES (fading):
  - 39: the club was sent into exile  (remembered 90%)
  - 40: the club came home from exile  (remembered 80%)
  - 36: the club was sent into exile  (remembered 67%)
  - 37: the club came home from exile  (remembered 59%)
  - 37: the fans began to boycott  (remembered 52%)
  - 29: the club was sent into exile  (remembered 33%)
SPENDING_ASK: [fair] what the fans asked of the CEO's investment this year
RELATIONSHIPS: {Maribel Hargrove (CEO): -46, Sylvie Arceneaux (CEO): -32, Lacey Dunmore (CEO): -32, Aria Barlow (CEO): -32, Fiona Valdez (CEO): -32, Fatima Ferreira (CEO): -32, Georgia Contreras (CEO): -32, Stella Buchanan (CEO): -32, Lydia Gallagher (CEO): -32, Yelena Brightwater (CEO): -32, Rosalind Iverson (CEO): -32, Jocelyn Oakley (CEO): -32, Jelena Hammond (CEO): +22}
DECISION_LOG: [49 earlier; 37: voted to recall the CEO; 38: asked for the fair level of investment; 39: asked for the fair level of investment; 39: voted to recall the CEO; 40: asked for the fair level of investment; 40: voted to recall the CEO]
```
### Fanbase of Team 19  (Entitled)
```yaml
IDENTITY: [Team 19 fans; market size 22 of 100; the franchise's permanent card, it outlives every CEO]
PERSONALITY: [Entitled] wants a title every year; fears being ignored; picks CEOs who are strong on ambition
ARCHETYPES: [+ Demanding, - Steady Hands]
RATINGS:
  - loyalty: 46
  - expectations: 86   (born at 71; drifts with results, within +/-15)
  - passion: 56
  - volatility: 37
  - media_trust: 62
  - approval of the CEO: 65%
  - Fan Capital: 0.65  (recall immunity; worth 4.6 points on a recall vote)
  - what the press did to approval last season: +2.0 points
  - pressure thresholds: exile 70, losing 59, scandal 73, spotlight 57
METERS (this franchise's own; they rise and fall with what happens, and their resting level drifts):
  - Hope: 75  (next year is the year; resting level 63, since year 0)
  - Outrage: 21  (all calm; resting level 32, since year 0)
  - Grudge: 48  (somewhere in between; resting level 48, since year 0)
  - Homecoming Pull: 60  (the exile healed into pride; resting level 58, since year 14)
BOYCOTT: [off]
MEMORIES (fading):
  - 36: the championship  (remembered 71%)
  - 33: the club was sent into exile  (remembered 55%)
  - 34: the club came home from exile  (remembered 48%)
  - 33: the fans began to boycott  (remembered 38%)
  - 25: the club was sent into exile  (remembered 27%)
  - 26: the club came home from exile  (remembered 24%)
SPENDING_ASK: [fair] what the fans asked of the CEO's investment this year
RELATIONSHIPS: {Amelia Benavides (CEO): -47, Adaeze Oakley (CEO): -36, Evangeline Cruz (CEO): -33, Linnea Yamada (CEO): -33, Marisol Goldberg (CEO): -33, Alma Chambers (CEO): -33, Anneke Zeller (CEO): +23}
DECISION_LOG: [45 earlier; 36: asked for the fair level of investment; 36: kept the CEO; 37: asked for the fair level of investment; 38: asked for the fair level of investment; 39: asked for the fair level of investment; 40: asked for the fair level of investment]
```
The franchise's permanent card, with its own meters, memories and any boycott (the club with the longest memory):

### Fanbase of Team 34  (Long-Suffering)
```yaml
IDENTITY: [Team 34 fans; market size 36 of 100; the franchise's permanent card, it outlives every CEO]
PERSONALITY: [Long-Suffering] wants one real playoff run; fears false hope; picks CEOs who are strong on patience
ARCHETYPES: [+ Never Leave, - Easily Pleased]
RATINGS:
  - loyalty: 64
  - expectations: 41   (born at 55; drifts with results, within +/-15)
  - passion: 55
  - volatility: 50
  - media_trust: 63
  - approval of the CEO: 41%
  - Fan Capital: 0.47  (recall immunity; worth 0.0 points on a recall vote)
  - what the press did to approval last season: -0.6 points
  - pressure thresholds: exile 81, losing 36, scandal 50, spotlight 62
METERS (this franchise's own; they rise and fall with what happens, and their resting level drifts):
  - Civic Pride: 54  (somewhere in between; resting level 53, since year 0)
  - Hope: 12  (nobody believes anymore; resting level 19, since year 0)
  - Outrage: 64  (the phones are ringing; resting level 54, since year 0)
  - Grudge: 76  (they have not forgiven the league; resting level 70, since year 1)
  - Homecoming Pull: 50  (somewhere in between; resting level 40, since year 2)
BOYCOTT: [on, level 0.29] the fans are staying away: the club's local revenue is down 12% until a new CEO is seated or they come back
MEMORIES (fading):
  - 38: the club was sent into exile  (remembered 84%)
  - 39: the club came home from exile  (remembered 73%)
  - 34: the club was sent into exile  (remembered 59%)
  - 38: the fans began to boycott  (remembered 59%)
  - 35: the club came home from exile  (remembered 52%)
  - 27: the club was sent into exile  (remembered 32%)
SPENDING_ASK: [fair] what the fans asked of the CEO's investment this year
RELATIONSHIPS: {Penelope Lockhart (CEO): -70, Chiara Hutchins (CEO): -38, Kora Forsythe (CEO): -26, Winona Buchanan (CEO): -26, Kenna Contreras (CEO): -1}
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

### CEO Kenna Contreras  (Team 34, CEO)
```yaml
IDENTITY: [Kenna Contreras, age 65, from Dayton OH; Real-estate magnate]
SOUL (fixed): [+ Hands-On Leader, - Content With Mediocrity]
PERSONALITY: [Meddler] wants a hand in every decision; fears being irrelevant
  - allowed by her soul: Meddler, Legacy Builder, Glory Hunter, Patient Steward; right now she is overconfident (+0.37)
RATINGS:
  - patience: 50  (sees herself at 55, overrating)
  - ambition: 23  (sees herself at 27, overrating)
  - involvement: 76  (sees herself at 77)
  - popularity: 60  (sees herself at 65, overrating)
  - business: 38  (sees herself at 38)
  - fan approval right now: 41%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 44, media 48, losing 59, subsidy 54
METERS (hers alone; they end with her tenure):
  - Fan Rapport: 55  (somewhere in between)
  - Standing Among CEOs: 50  (somewhere in between)
  - Legacy: 12  (she will be forgotten)
PLEDGE: [standard] the share of a profit she puts back into the club
TRAJECTORY: [age 53: 49; age 55: 49; age 57: 50; age 59: 49; age 61: 49; age 63: 49; age 65: 49; peak 50 at 57; now 49]
RECOGNITION: [unknown; esteem 2.1; honors: none yet]
RELATIONSHIPS: {Catalina Saunders (coach): -21, Antonia Davenport (gm): -20, Rosalind Briggs (coach): -10, Thalia Duarte (coach): -1, Layla Boateng (coach): +4, Astrid Cabrera (coach): +4, Team 34 fans: +28}
CAREER: [elected 27]
DECISION_LOG: [18 earlier; 38: survived a recall vote; 39: pledged the standard share of profit to the club; 39: held firm against the boycott; 39: fired coach Catalina Saunders (results); 40: pledged the standard share of profit to the club; 40: held firm against the boycott]
```

## Scenes as the Archive records them

Each firing, recall vote and exile determination is a scene: every party gives its own claim, and the evidence section says, from the engine's own numbers, which claims hold. The scenes never change an outcome (the check script proves a league plays out identically with them on or off); they explain it, and they move relationships and decision logs.

**An exile determination**

```
EVENT 40-exile_determination-43-1  (Team 43; exile determination; finished fifth in the division)
├── Owner claims: Delphine Nettles (Meddler): "Fifth in the division, and I will say who is to blame: Felicity Ostrander. The roster rated 39% and they won 33%."  [not supported by the record]
├── Coach claims: Felicity Ostrander (Survivor): "I was handed a roster 1.4 deviations below average and the schedule did the rest."  [supported by the record]
├── GM claims: Natalia Chandler (Cold Realist): "The roster was 5 of 5 in this division on paper. The record, 33%, was 6% below what it should have been."  [not supported by the record]
├── The fans claim: Team 43 fans: "They finished 33%. We wanted a good time and we feared boredom; that is what we got."  [supported by the record]
├── Press claims: Team 43 Gazette (Homer): "They finished 33%. The town is watching closely, and that is how we are telling it."  [supported by the record]
└── Evidence supports: Exile followed a thin roster.  (record 33%, roster predicts 39%, roster -1.1 deviations from average)
    Outcome: Team 43 is exiled for next season
```

**A firing the record backs**

```
EVENT 40-firing-39-1  (Team 39; firing; CEO fired the coach (results))
├── Owner claims: Jelena Hammond (Patient Steward): "29% is not what I bought this team for. I gave her 1 season; I was patient."  [supported by the record]
├── Coach claims: Lacey Baptiste (Survivor): "You gave me a roster 1.4 deviations below the league's average and expected a contender."  [supported by the record]
├── GM claims: Kirsten Solberg (Gambler): "The roster was fine. The record was 29%, against 37% on paper."  [supported by the record]
├── The fans claim: Team 39 fans: "They finished 29%. We wanted a title every year and we feared being ignored; that is what we got."  [supported by the record]
├── Press claims: Team 39 Courier (Gossip): "They finished 29%. The town is watching closely, and that is how we are telling it."  [supported by the record]
└── Evidence supports: The firing is backed by the record, and the roster does not excuse it: the team won well under what it was built to win.  (record 29%, roster predicts 37%, roster -1.2 deviations from average)
    Outcome: Lacey Baptiste fired; replaced by a new coach
```

**A harsh firing (the roster explains the record)**

```
EVENT 40-firing-09-2  (Team 09; firing; CEO fired the gm (results))
├── Owner claims: Brooke Kendrick (Showwoman): "the roster should have won about 47% and they won 14%. I trusted her with the roster; I was patient."  [supported by the record]
├── GM claims: Willa Marchetti (Dealmaker): "I built the roster and she lost games the roster should have won: 14% on a team that rates 47%."  [supported by the record]
├── Coach claims: Winona Greer (Disciplinarian): "I coached what I was handed, a roster 0.3 deviations below average."  [not supported by the record]
├── The fans claim: Team 09 fans: "We stand by our own, and we have 43 points of goodwill banked. This town wanted a team that is theirs."  [not supported by the record]
├── Press claims: Team 09 Sports Desk (Hype Machine): "They finished 14%. The town is restless, and that is how we are telling it."  [supported by the record]
└── Evidence supports: A harsh firing: the record was poor (14%), but the roster she built was not thin, so the shortfall was on the field.  (record 14%, roster predicts 47%, roster -0.3 deviations from average)
    Outcome: Willa Marchetti fired; replaced by a new gm
```

**A new CEO's sweep**

```
EVENT 40-firing-39-2  (Team 39; firing; CEO fired the gm (new CEO cleaned house))
├── Owner claims: Jelena Hammond (Patient Steward): "New CEO, new staff. I wanted a slow, sound build and I wasn't going to ask Kirsten Solberg for it."  [supported by the record]
├── GM claims: Kirsten Solberg (Gambler): "I built the roster and she lost games the roster should have won: 29% on a team that rates 37%."  [supported by the record]
├── Coach claims: Lacey Baptiste (Survivor): "I coached what I was handed, a roster 1.2 deviations below average."  [supported by the record]
├── The fans claim: Team 39 fans: "They finished 29%. We wanted a title every year and we feared being ignored; that is what we got."  [supported by the record]
├── Press claims: Team 39 Courier (Gossip): "They finished 29%. The town is watching closely, and that is how we are telling it."  [supported by the record]
└── Evidence supports: A sweep: the new CEO cleared the staff on arrival, whatever the record (29% against 37% on paper).  (record 29%, roster predicts 37%, roster -1.2 deviations from average)
    Outcome: Kirsten Solberg fired; replaced by a new gm
```

**A recall vote that removes a CEO**

```
EVENT 40-recall_vote-40-1  (Team 40; recall vote; vote triggered by approval)
├── Owner claims: Daniela Rutledge (Penny-Pincher): "I thought we were at 36%. The team lost, and the fans are blaming the person they can vote on."  [supported by the record]
├── The fans claim: Team 40 fans: "We stand by our own, and we have 59 points of goodwill banked. This town wanted a team that is theirs." We wanted a CEO strong on popularity and we chose Giselle Eastwood.  [supported by the record]
├── Press claims: Team 40 Insider (Homer): "They finished 33%. The town is watching closely, and that is how we are telling it."  [supported by the record]
├── New CEO claims: Giselle Eastwood (Showwoman): "Five of us stood. The fans wanted strength on popularity and picked me. I want spectacle and headlines."  [supported by the record]
└── Evidence supports: 51.2% voted to recall (a majority of the 1,000,000 fans is needed): recalled.  (record 33%, roster predicts 37%, roster -1.3 deviations from average)
    Outcome: Daniela Rutledge recalled; Giselle Eastwood elected from 5 candidates
```

**A recall vote the CEO survives**

```
EVENT 40-recall_vote-48-1  (Team 48; recall vote; vote triggered by rotation)
├── Owner claims: Luna Madsen (Glory Hunter): "I told you we were at 55%. The fans know what I stand for: a title right now."  [supported by the record]
├── The fans claim: Team 48 fans: "They finished 56%. We wanted honesty and we feared being fooled again; we have no complaint about the record, but we are watching."  [not supported by the record]
├── Press claims: Team 48 Insider (Contrarian): "They finished 56%. The town is watching closely, and that is how we are telling it."  [supported by the record]
└── Evidence supports: 38.7% voted to recall (a majority of the 1,000,000 fans is needed): the CEO survives.  (record 56%, roster predicts 45%, roster -0.5 deviations from average)
    Outcome: Luna Madsen survives
```


## What an agent is shown, and what the log keeps

Choices go through Decision Points. An agent is shown its own card, what it perceives (candidates' ratings as the CEO sees them, with blind spots) and the legal options, and answers with one option id. The guard applies the choice (or the autopilot's choice if the answer is invalid or late) and logs it. Below: the two decisions a CEO faces, as an agent receives them, and the log line.

**A CEO's staff review, as an agent receives it:**

```json
{
 "top_priority": {
  "goal": "Win the Diamond Coronation. It is the first priority of every role in the league; everything else on this card is a means to it.",
  "your_team": "Team 01",
  "strength_rank": 24,
  "of_teams": 48,
  "coronations_won": 0,
  "last_won": null,
  "you_are_judged_on": "Judged by the fans: the club's record and the Coronation, the fans' trust in your pledges, and a club that stays solvent (payroll floor of about $90M over four seasons). You hire and fire the GM and the head coach."
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
  "last_won": null,
  "you_are_judged_on": "Judged by the fans: the club's record and the Coronation, the fans' trust in your pledges, and a club that stays solvent (payroll floor of about $90M over four seasons). You hire and fire the GM and the head coach."
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

**Core personalities (all rostered players):** Diplomat 567, Competitor 465, Grinder 421, Perfectionist 383, Showman 249, Quiet Leader 171, Free Spirit 135, Hothead 94, Mercenary 36, Loyalist 23

**Most common positive archetypes:** Well-Rounded 738, Pass-Pro Wall 132, Ballhawk 120, Edge Terror 117, Shutdown Corner 108, Road Grader 102, Run Stuffer 90, Thumper 86

**Coach effect across the 48 teams:** average +0.02, spread (sd) 0.45, best +1.08, worst -0.89 points of expected margin. For scale, team talent has a spread of about 3 to 4 points.

**Personality shifts:** 3091 of 32200 players have changed personality at least once in 40 seasons.

**Standing in the media's eyes** (everyone who ever lived, by what the media calls her now): known 228, respected 137, star 36, Hall of Famer 9, legend 1. 9 are in the Hall of Fame.

**Fan cultures:** Die-Hards 13, Entitled 11, Party Crowd 9, Gloomy Realists 7, Long-Suffering 5, Front-Runners 3

**Fan Capital:** average 0.53, from 0.39 to 0.65; the most it can buffer a recall vote is 15 points.

**Fan meters:** every fanbase has 3 from birth and can awaken up to 5; now [(5, 37), (4, 10), (3, 1)] (meters per club, clubs). Most common: Grudge 31, Outrage 29, Homecoming Pull 28, Civic Pride 26.

**Fan memories** held now: exile 185, return 157, boycott 69, boycott_end 33, star_left 26, title 20, drought 12. **Boycotts** on now: 1 clubs; 69 begun within the memory window. A full boycott costs 40% of local revenue.

**The press on approval, last season:** average 1.2 points either way, largest 3.3 (the cap is 3 before market size and trust).

**Outlets:** 52 (4 national, one local beat per team); a national outlet tells a team's year as it was, a local outlet frames it toward its fans' mood by at most 25 points of tone.

**CEO choices on the record:** ceo_boycott concede 17, ceo_boycott hold 20, ceo_pledge standard 1845. CEOs who stepped aside under a boycott: 0.

**Scenes:** 1162 in 40 seasons ([('recall_vote', 569), ('exile_determination', 320), ('firing', 273)]). Firings by ruling: fair 178, sweep 70, harsh 22, unfounded 3.

**Recall votes:** 569 in 40 seasons (14.2 a year); 202 CEOs recalled (5.0 a year), 36% of votes. CEOs retire on their own too: 49 so far.

**Firings:** 174 coaches and 99 GMs fired in 40 seasons.

**Coaches so far:** 729 cards created (head coaches and coordinators) and 541 retired in 40 seasons; 44 coaches and 10 GMs are between jobs right now.

**The coaching pool:** 729 coach cards in 40 seasons (head coaches and coordinators are the same kind of card), 44 between jobs now (the creator tops the pool up only when it falls under 40). 574 have worked as a coordinator, 180 coordinators were hired away as head coaches, and 240 coordinators had been head coaches before.

**Coordinators:** schemes proposed: coverage 821, run 775, pass 756, blitz 747, balanced 741; the head coach vetoed 727 of 3099. 463 coordinators fired by their head coaches.

```
ROSARIO DANFORTH  -  offensive coordinator, Team 01  -  age 61, from Tallahassee FL
  PLAYCALLING 39   VISION (gamecraft) 55   heat -0.08   years here 6
  Her lift to her unit: -0.23 points of margin (the average coordinator is zero).
  Career: 30 entered_coaching; 31 hired; 34 fired; 34 hired (offensive coordinator); 37 interviewed (coach)
  Lately: 39 proposed the run scheme; 40 proposed the run scheme; 40 was overruled by Sabine Bradshaw on the run scheme; the unit plays balanced

IVY LOVETT  -  defensive coordinator, Team 01  -  age 45, from Columbus OH
  PLAYCALLING 39   VISION (gamecraft) 77   heat -0.11   years here 6
  Her lift to her unit: -0.25 points of margin (the average coordinator is zero).
  Career: 32 hired (defensive coordinator); 33 fired (defensive coordinator); 34 hired (defensive coordinator)
  Lately: 38 proposed the coverage scheme; 39 proposed the blitz scheme; 40 proposed the coverage scheme
```

**GM plan choices on the record:** gm_cap_plan balanced 1920, gm_draft_focus needs 1920 (the autopilot keeps the old rule).

**Players with cards:** 3244 active or unsigned, 29656 retired.
