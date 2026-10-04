# Character cards: samples

Seed 1, after 6 seasons. Names, hometowns and backgrounds come from placeholder word lists (engine/card_pools.py) that you can replace. Ratings, archetypes and the coach effect are real: they come from the engine. Relationships and the decision log start empty on purpose; the Interaction system will fill them.

## How to read a card

- **Archetypes** describe the player's rating profile: her best attribute names the positive archetype and her weakest the negative one.
- **Pressure thresholds** (exile, contract, spotlight, loyalty) are how much each kind of pressure rattles her, 1 to 100. They do nothing yet; the Interaction system will use them.
- **Coach ratings**: only offense and defense move games today (capped at +/- 1.0 point of margin each). The other four are stored for later.

## A franchise player at each position group

### Anika Oakley  (QB, Team 38)
```yaml
IDENTITY: [Anika Oakley, age 28, from Charleston SC; Power-conference star]
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
ARCHETYPES: [+ Surgeon, - No Glaring Weakness]
RATINGS: [overall 89, Franchise player]
  - accuracy: 93
  - arm: 86
  - awareness: 86
  - pressure thresholds: exile 55, contract 38, spotlight 70, loyalty 46
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```
### Mabel Colburn  (WR, Team 17)
```yaml
IDENTITY: [Mabel Colburn, age 29, from Youngstown OH; International pathway]
PERSONALITY: [Hothead] wants to settle every score on the field; fears being embarrassed in public
ARCHETYPES: [+ Burner, - No Glaring Weakness]
RATINGS: [overall 96, Franchise player]
  - route: 91
  - hands: 98
  - speed: 100
  - pressure thresholds: exile 57, contract 57, spotlight 90, loyalty 53
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```
### Kasey Navarro  (OL, Team 37)
```yaml
IDENTITY: [Kasey Navarro, age 30, from Fargo ND; Small-college standout]
PERSONALITY: [Loyalist] wants to be a franchise's one-club legend; fears being traded or cut
ARCHETYPES: [+ Road Grader, - No Glaring Weakness]
RATINGS: [overall 95, Franchise player]
  - pass_block: 91
  - run_block: 100
  - pressure thresholds: exile 42, contract 69, spotlight 41, loyalty 71
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```
### Odalys Alderman  (DL, Team 35)
```yaml
IDENTITY: [Odalys Alderman, age 27, from Corpus Christi TX; Two-sport athlete]
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
ARCHETYPES: [+ Edge Terror, - No Glaring Weakness]
RATINGS: [overall 94, Franchise player]
  - pass_rush: 100
  - run_stop: 88
  - pressure thresholds: exile 65, contract 56, spotlight 53, loyalty 46
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 1 (pick 6)]
DECISION_LOG: [none yet]
```
### Adriana Avery  (CB, Team 28)
```yaml
IDENTITY: [Adriana Avery, age 28, from Sao Paulo Brazil; Late bloomer]
PERSONALITY: [Loyalist] wants to be a franchise's one-club legend; fears being traded or cut
ARCHETYPES: [+ Well-Rounded, - No Glaring Weakness]
RATINGS: [overall 90, Franchise player]
  - coverage: 91
  - ball_skills: 90
  - tackling: 89
  - pressure thresholds: exile 56, contract 51, spotlight 44, loyalty 65
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```
### Roxanne Eastwood  (K, Team 06)
```yaml
IDENTITY: [Roxanne Eastwood, age 30, from Gary IN; Coach's daughter]
PERSONALITY: [Free Spirit] wants freedom and adventure along the way; fears a rigid system
ARCHETYPES: [+ Automatic, - No Glaring Weakness]
RATINGS: [overall 98, Franchise player]
  - power: 94
  - accuracy: 100
  - pressure thresholds: exile 71, contract 59, spotlight 37, loyalty 36
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```

## A young rookie and a veteran

### Aaliyah Jefferson  (WR, Team 06)
```yaml
IDENTITY: [Aaliyah Jefferson, age 22, from Omaha NE; Power-conference star]
PERSONALITY: [Free Spirit] wants freedom and adventure along the way; fears a rigid system
ARCHETYPES: [+ Burner, - No Glaring Weakness]
RATINGS: [overall 77, Star]
  - route: 66
  - hands: 77
  - speed: 88
  - pressure thresholds: exile 84, contract 57, spotlight 51, loyalty 55
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 6 (pick 1)]
DECISION_LOG: [none yet]
```
### Kenna Bellamy  (P, Team 10)
```yaml
IDENTITY: [Kenna Bellamy, age 33, from El Paso TX; Two-sport athlete]
PERSONALITY: [Grinder] wants to earn every inch; fears being handed nothing and losing it anyway
ARCHETYPES: [+ Well-Rounded, - No Glaring Weakness]
RATINGS: [overall 100, Franchise player]
  - power: 100
  - accuracy: 100
  - pressure thresholds: exile 40, contract 39, spotlight 30, loyalty 29
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```

## A retired player (cards are kept for the Archive)

### Bianca Leclair  (WR, retired)
```yaml
IDENTITY: [Bianca Leclair, age 32, from Montreal QC; Walk-on turned starter]
PERSONALITY: [Quiet Leader] wants her teammates' respect; fears letting the locker room down
ARCHETYPES: [+ Well-Rounded, - No Glaring Weakness]
RATINGS: [overall 88, Franchise player]
  - route: 86
  - hands: 91
  - speed: 88
  - pressure thresholds: exile 48, contract 48, spotlight 61, loyalty 21
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [retired 1]
DECISION_LOG: [none yet]
```

## Head coaches: the best and the weakest by total on-field effect

### Coach Una Stratton  (Team 32)
```yaml
IDENTITY: [Una Stratton, age 62, from Indianapolis IN; Long-time position coach]
PERSONALITY: [Innovator] wants to change how the game is played; fears being called old-fashioned
ARCHETYPES: [+ Defensive Architect, - Undisciplined]
RATINGS:
  - offense: 44   -> -0.12 points of margin
  - defense: 93   -> +0.86 points of margin
  - development: 74   (no on-field effect yet)
  - gamecraft: 36   (no on-field effect yet)
  - discipline: 29   (no on-field effect yet)
  - motivation: 57   (no on-field effect yet)
  - pressure thresholds: exile 50, contract 47, spotlight 83, loyalty 54
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [hired 0]
DECISION_LOG: [none yet]
```
### Coach Nina Lachance  (Team 42)
```yaml
IDENTITY: [Nina Lachance, age 46, from Perth Australia; Former star player turned coach]
PERSONALITY: [Innovator] wants to change how the game is played; fears being called old-fashioned
ARCHETYPES: [+ Clock Manager, - Predictable Offense]
RATINGS:
  - offense: 26   -> -0.48 points of margin
  - defense: 32   -> -0.36 points of margin
  - development: 37   (no on-field effect yet)
  - gamecraft: 64   (no on-field effect yet)
  - discipline: 61   (no on-field effect yet)
  - motivation: 60   (no on-field effect yet)
  - pressure thresholds: exile 32, contract 40, spotlight 70, loyalty 43
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [hired 0]
DECISION_LOG: [none yet]
```

## How the cards spread across the league

**Core personalities (all rostered players):** Loyalist 236, Diplomat 235, Mercenary 231, Showman 230, Grinder 228, Competitor 227, Hothead 227, Quiet Leader 226, Perfectionist 213, Free Spirit 203

**Most common positive archetypes:** No Standout Skill 867, Well-Rounded 282, Pass-Pro Wall 90, Ballhawk 88, Road Grader 81, Burner 60, Glue Hands 56, Run Stuffer 53

**Coach effect across the 48 teams:** average +0.00, spread (sd) 0.40, best +0.74, worst -0.84 points of expected margin. For scale, team talent has a spread of about 3 to 4 points.

**Coaches so far:** 75 hired and 27 retired in 6 seasons.

**Players with cards:** 2515 active or unsigned, 1050 retired.
