# Character cards: samples

Seed 1, after 14 seasons. Names, hometowns and backgrounds come from placeholder word lists (engine/card_pools.py) that you can replace. Ratings, archetypes and the coach effect are real: they come from the engine. Relationships and the decision log start empty on purpose; the Interaction system will fill them.

## How to read a card

- **Soul (archetypes)** is fixed for life. It is read from the rating profile she is born with: her best attribute names the positive archetype and her weakest the negative one. Her development is bent to stay true to it.
- **Personality** is how her soul shows up. Her archetype allows four personalities; which one she shows depends on her temperament and on how she rates herself. Her self-image lags the truth, so a declining veteran overrates herself and a rising rookie undersells herself. When her confidence moves enough, her personality can shift, but only inside the four her soul allows.
- **Pressure thresholds** (exile, contract, spotlight, loyalty) are how much each kind of pressure rattles her, 1 to 100. They do nothing yet; the Interaction system will use them.
- **Coach ratings**: offense and defense lift the team (up to +/- 1.0 point of margin each); development adds up to 0.4 rating points a year to each young player. The other three are stored for later. Legends are the rare all-time greats.

## A franchise player at each position group

### Brooke Beaumont  (QB, Team 39)
```yaml
IDENTITY: [Brooke Beaumont, age 29, from Spokane WA; Power-conference star]
SOUL (fixed): [+ Well-Rounded, - Reads Late]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is clear-eyed (-0.01)
RATINGS: [overall 85, Franchise player]
  - accuracy: 87  (sees herself at 87)
  - arm: 87  (sees herself at 86)
  - awareness: 80  (sees herself at 81)
  - pressure thresholds: exile 54, contract 54, spotlight 40, loyalty 35
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 7 (pick 8)]
DECISION_LOG: [none yet]
```
### Nova Gentry  (WR, Team 46)
```yaml
IDENTITY: [Nova Gentry, age 27, from Winnipeg MB; Two-sport athlete]
SOUL (fixed): [+ Burner, - Rough Routes]  temperament family: flash
PERSONALITY: [Free Spirit] wants freedom and adventure along the way; fears a rigid system
  - allowed by her soul: Showman, Free Spirit, Competitor, Mercenary; right now she is full of doubt (-1.00)
RATINGS: [overall 94, Franchise player]
  - route: 86  (sees herself at 78, doubting)
  - hands: 95  (sees herself at 86, doubting)
  - speed: 100  (sees herself at 91, doubting)
  - pressure thresholds: exile 27, contract 43, spotlight 44, loyalty 52
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 9 (pick 2)]
DECISION_LOG: [none yet]
```
### Samira Paddock  (OL, Team 14)
```yaml
IDENTITY: [Samira Paddock, age 24, from Sao Paulo Brazil; Walk-on turned starter]
SOUL (fixed): [+ Pass-Pro Wall, - Soft in the Run]  temperament family: precision
PERSONALITY: [Perfectionist] wants flawless execution; fears the one mistake everyone remembers
  - allowed by her soul: Perfectionist, Quiet Leader, Grinder, Diplomat; right now she is full of doubt (-0.78)
RATINGS: [overall 92, Franchise player]
  - pass_block: 97  (sees herself at 91, doubting)
  - run_block: 88  (sees herself at 82, doubting)
  - pressure thresholds: exile 53, contract 40, spotlight 58, loyalty 55
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 12 (pick 7)]
DECISION_LOG: [none yet]
```
### Brooke Okafor  (DL, Team 25)
```yaml
IDENTITY: [Brooke Okafor, age 27, from Duluth MN; Overlooked recruit]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is clear-eyed (+0.05)
RATINGS: [overall 94, Franchise player]
  - pass_rush: 94  (sees herself at 94)
  - run_stop: 95  (sees herself at 96)
  - pressure thresholds: exile 72, contract 37, spotlight 27, loyalty 71
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 9 (pick 6)]
DECISION_LOG: [none yet]
```
### Aaliyah Jefferson  (CB, Team 05)
```yaml
IDENTITY: [Aaliyah Jefferson, age 30, from Tacoma WA; Two-sport athlete]
SOUL (fixed): [+ Ballhawk, - Avoids Contact]  temperament family: flash
PERSONALITY: [Free Spirit] wants freedom and adventure along the way; fears a rigid system
  - allowed by her soul: Showman, Free Spirit, Competitor, Mercenary; right now she is clear-eyed (-0.18)
RATINGS: [overall 95, Franchise player]
  - coverage: 97  (sees herself at 93, doubting)
  - ball_skills: 97  (sees herself at 94, doubting)
  - tackling: 87  (sees herself at 89)
  - pressure thresholds: exile 34, contract 35, spotlight 62, loyalty 55
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 6 (pick 3); became Free Spirit (was Showman) 8]
DECISION_LOG: [none yet]
```
### Aaliyah Chavez  (K, Team 47)
```yaml
IDENTITY: [Aaliyah Chavez, age 30, from Helsinki Finland; Power-conference star]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is full of doubt (-0.76)
RATINGS: [overall 91, Franchise player]
  - power: 95  (sees herself at 89, doubting)
  - accuracy: 88  (sees herself at 82, doubting)
  - pressure thresholds: exile 41, contract 24, spotlight 49, loyalty 43
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```

## A young rookie and a veteran

### Anneke Chandler  (CB, Team 37)
```yaml
IDENTITY: [Anneke Chandler, age 22, from Helsinki Finland; Late bloomer]
SOUL (fixed): [+ Ballhawk, - Beaten Deep]  temperament family: flash
PERSONALITY: [Showman] wants the spotlight and a signature moment; fears being ignored by the media
  - allowed by her soul: Showman, Free Spirit, Competitor, Mercenary; right now she is overconfident (+0.64)
RATINGS: [overall 59, Depth]
  - coverage: 56  (sees herself at 64, overrating)
  - ball_skills: 64  (sees herself at 68, overrating)
  - tackling: 62  (sees herself at 66, overrating)
  - pressure thresholds: exile 40, contract 79, spotlight 59, loyalty 41
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 14 (pick 1)]
DECISION_LOG: [none yet]
```
### Alma Navarro  (P, Team 35)
```yaml
IDENTITY: [Alma Navarro, age 36, from Birmingham AL; Overlooked recruit]
SOUL (fixed): [+ Boomer, - Wayward]  temperament family: power
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is overconfident (+0.95)
RATINGS: [overall 91, Franchise player]
  - power: 97  (sees herself at 105, overrating)
  - accuracy: 81  (sees herself at 89, overrating)
  - pressure thresholds: exile 22, contract 57, spotlight 43, loyalty 44
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```

## A player whose personality changed (her soul stayed the same)

### Kirsten Pemberton  (DL, Team 45)
```yaml
IDENTITY: [Kirsten Pemberton, age 32, from Youngstown OH; Overlooked recruit]
SOUL (fixed): [+ Run Stuffer, - Little Pressure]  temperament family: power
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is clear-eyed (+0.19)
RATINGS: [overall 64, Starter]
  - pass_rush: 60  (sees herself at 61)
  - run_stop: 68  (sees herself at 70, overrating)
  - pressure thresholds: exile 60, contract 51, spotlight 69, loyalty 52
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [became Grinder (was Competitor) 6; became Competitor (was Grinder) 10; became Grinder (was Competitor) 11; became Competitor (was Grinder) 13]
DECISION_LOG: [none yet]
```

## A retired player (cards are kept for the Archive)

### Mabel Colburn  (WR, retired)
```yaml
IDENTITY: [Mabel Colburn, age 32, from Portland OR; Coach's daughter]
SOUL (fixed): [+ Burner, - No Glaring Weakness]  temperament family: flash
PERSONALITY: [Showman] wants the spotlight and a signature moment; fears being ignored by the media
  - allowed by her soul: Showman, Free Spirit, Competitor, Mercenary; right now she is overconfident (+0.76)
RATINGS: [overall 88, Franchise player]
  - route: 88  (sees herself at 93, overrating)
  - hands: 86  (sees herself at 92, overrating)
  - speed: 91  (sees herself at 97, overrating)
  - pressure thresholds: exile 62, contract 55, spotlight 66, loyalty 56
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [became Free Spirit (was Showman) 1; became Showman (was Free Spirit) 7; retired 9]
DECISION_LOG: [none yet]
```

## Head coaches: a legend, a typical coach and a weak one

### Coach Amelia Colburn  (Team 16)  -  LEGEND
```yaml
IDENTITY: [Amelia Colburn, age 52, from Lubbock TX; Analytics-minded newcomer]
PERSONALITY: [Gambler] wants a fourth-down legend; fears being second-guessed for the one that failed
ARCHETYPES: [+ Legend: Defensive Architect, - Undisciplined]
RATINGS:
  - offense: 90   -> +0.80 points of margin
  - defense: 94   -> +0.87 points of margin
  - development: 91   -> +0.33 rating points per year to each young player
  - gamecraft: 75   (no on-field effect yet)
  - discipline: 74   (no on-field effect yet)
  - motivation: 77   (no on-field effect yet)
  - pressure thresholds: exile 42, contract 56, spotlight 31, loyalty 38
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [hired 0]
DECISION_LOG: [none yet]
```
### Coach Iris Dellinger  (Team 46)
```yaml
IDENTITY: [Iris Dellinger, age 59, from Milwaukee WI; Came over from another league]
PERSONALITY: [Tactician] wants the cleverest scheme in the league; fears being out-schemed on a big night
ARCHETYPES: [+ Talent Developer, - Undisciplined]
RATINGS:
  - offense: 52   -> +0.03 points of margin
  - defense: 37   -> -0.26 points of margin
  - development: 71   -> +0.17 rating points per year to each young player
  - gamecraft: 44   (no on-field effect yet)
  - discipline: 26   (no on-field effect yet)
  - motivation: 57   (no on-field effect yet)
  - pressure thresholds: exile 43, contract 42, spotlight 82, loyalty 51
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [hired 0]
DECISION_LOG: [none yet]
```
### Coach Georgia McAllister  (Team 20)
```yaml
IDENTITY: [Georgia McAllister, age 44, from Tacoma WA; Long-time position coach]
PERSONALITY: [Tactician] wants the cleverest scheme in the league; fears being out-schemed on a big night
ARCHETYPES: [+ Clock Manager, - Predictable Offense]
RATINGS:
  - offense: 15   -> -0.71 points of margin
  - defense: 41   -> -0.19 points of margin
  - development: 42   -> -0.06 rating points per year to each young player
  - gamecraft: 55   (no on-field effect yet)
  - discipline: 30   (no on-field effect yet)
  - motivation: 47   (no on-field effect yet)
  - pressure thresholds: exile 53, contract 26, spotlight 36, loyalty 46
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [hired 10]
DECISION_LOG: [none yet]
```

## How the cards spread across the league

**Core personalities (all rostered players):** Diplomat 500, Competitor 444, Grinder 351, Perfectionist 349, Showman 211, Quiet Leader 156, Free Spirit 105, Hothead 90, Mercenary 34, Loyalist 16

**Most common positive archetypes:** Well-Rounded 639, Pass-Pro Wall 139, Ballhawk 108, Edge Terror 96, Run Stuffer 90, Glue Hands 87, Road Grader 86, Route Technician 76

**Coach effect across the 48 teams:** average -0.06, spread (sd) 0.62, best +1.76, worst -0.93 points of expected margin. For scale, team talent has a spread of about 3 to 4 points.

**Personality shifts:** 783 of 5284 players have changed personality at least once in 14 seasons.

**Legends:** 9 of 116 coaches hired so far are legends; 3 on the field now.

**Coaches so far:** 116 hired and 68 retired in 14 seasons.

**Players with cards:** 2321 active or unsigned, 3028 retired.
