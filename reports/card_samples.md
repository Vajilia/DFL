# Character cards: samples

Seed 1, after 14 seasons. Names, hometowns and backgrounds come from placeholder word lists (engine/card_pools.py) that you can replace. Ratings, archetypes and the coach effect are real: they come from the engine. Relationships and the decision log start empty on purpose; the Interaction system will fill them.

## How to read a card

- **Soul (archetypes)** is fixed for life. It is read from the rating profile she is born with: her best attribute names the positive archetype and her weakest the negative one. Her development is bent to stay true to it.
- **Personality** is how her soul shows up. Her archetype allows four personalities; which one she shows depends on her temperament and on how she rates herself. Her self-image lags the truth, so a declining veteran overrates herself and a rising rookie undersells herself. When her confidence moves enough, her personality can shift, but only inside the four her soul allows.
- **Pressure thresholds** (exile, contract, spotlight, loyalty) are how much each kind of pressure rattles her, 1 to 100. They do nothing yet; the Interaction system will use them.
- **Coach ratings**: offense and defense lift the team (up to +/- 1.0 point of margin each); development adds up to 0.4 rating points a year to each young player. The other three are stored for later. Legends are the rare all-time greats.

## A franchise player at each position group

### Alana Landry  (QB, Team 45)
```yaml
IDENTITY: [Alana Landry, age 28, from Knoxville TN; Overlooked recruit]
SOUL (fixed): [+ Cannon, - Wild Arm]  temperament family: power
PERSONALITY: [Grinder] wants to earn every inch; fears being handed nothing and losing it anyway
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is full of doubt (-1.00)
RATINGS: [overall 90, Franchise player]
  - accuracy: 88  (sees herself at 75, doubting)
  - arm: 93  (sees herself at 79, doubting)
  - awareness: 91  (sees herself at 78, doubting)
  - pressure thresholds: exile 52, contract 64, spotlight 33, loyalty 63
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 9 (pick 6)]
DECISION_LOG: [none yet]
```
### Josie Kimura  (WR, Team 23)
```yaml
IDENTITY: [Josie Kimura, age 29, from Toledo OH; Late bloomer]
SOUL (fixed): [+ Well-Rounded, - Lacks Burst]  temperament family: balanced
PERSONALITY: [Grinder] wants to earn every inch; fears being handed nothing and losing it anyway
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is full of doubt (-1.00)
RATINGS: [overall 88, Franchise player]
  - route: 89  (sees herself at 83, doubting)
  - hands: 92  (sees herself at 83, doubting)
  - speed: 85  (sees herself at 75, doubting)
  - pressure thresholds: exile 36, contract 79, spotlight 30, loyalty 54
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 7 (pick 3)]
DECISION_LOG: [none yet]
```
### Celeste Stratton  (OL, Team 13)
```yaml
IDENTITY: [Celeste Stratton, age 27, from Sacramento CA; Junior-college transfer]
SOUL (fixed): [+ Road Grader, - Turnstile]  temperament family: power
PERSONALITY: [Hothead] wants to settle every score on the field; fears being embarrassed in public
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is overconfident (+0.50)
RATINGS: [overall 96, Franchise player]
  - pass_block: 92  (sees herself at 97, overrating)
  - run_block: 100  (sees herself at 103, overrating)
  - pressure thresholds: exile 30, contract 47, spotlight 45, loyalty 61
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 9 (pick 3)]
DECISION_LOG: [none yet]
```
### Alana Trevino  (DL, Team 17)
```yaml
IDENTITY: [Alana Trevino, age 29, from Glasgow Scotland; Small-college standout]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is clear-eyed (-0.12)
RATINGS: [overall 99, Franchise player]
  - pass_rush: 99  (sees herself at 98)
  - run_stop: 98  (sees herself at 96)
  - pressure thresholds: exile 46, contract 51, spotlight 22, loyalty 49
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 7 (pick 2)]
DECISION_LOG: [none yet]
```
### Tamsin Christensen  (CB, Team 37)
```yaml
IDENTITY: [Tamsin Christensen, age 24, from Kansas City MO; Small-college standout]
SOUL (fixed): [+ Shutdown Corner, - Poor Ball Skills]  temperament family: flash
PERSONALITY: [Showman] wants the spotlight and a signature moment; fears being ignored by the media
  - allowed by her soul: Showman, Free Spirit, Competitor, Mercenary; right now she is clear-eyed (+0.04)
RATINGS: [overall 90, Franchise player]
  - coverage: 95  (sees herself at 94)
  - ball_skills: 78  (sees herself at 81, overrating)
  - tackling: 94  (sees herself at 93)
  - pressure thresholds: exile 77, contract 39, spotlight 70, loyalty 10
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 12 (pick 3)]
DECISION_LOG: [none yet]
```
### Liesel Trevino  (K, Team 18)
```yaml
IDENTITY: [Liesel Trevino, age 26, from Reno NV; Overlooked recruit]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is full of doubt (-0.55)
RATINGS: [overall 98, Franchise player]
  - power: 98  (sees herself at 94, doubting)
  - accuracy: 98  (sees herself at 94, doubting)
  - pressure thresholds: exile 26, contract 55, spotlight 48, loyalty 58
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 10 (pick 4)]
DECISION_LOG: [none yet]
```

## A young rookie and a veteran

### Ines Barrientos  (DL, Team 44)
```yaml
IDENTITY: [Ines Barrientos, age 22, from Mobile AL; Overlooked recruit]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Mercenary] wants the biggest contract on the market; fears a bad deal and an early exit
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is overconfident (+0.37)
RATINGS: [overall 63, Starter]
  - pass_rush: 62  (sees herself at 64)
  - run_stop: 64  (sees herself at 69, overrating)
  - pressure thresholds: exile 39, contract 49, spotlight 39, loyalty 63
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [drafted 14 (pick 1)]
DECISION_LOG: [none yet]
```
### Jasmine Christensen  (P, Team 07)
```yaml
IDENTITY: [Jasmine Christensen, age 36, from Richmond VA; Overlooked recruit]
SOUL (fixed): [+ Boomer, - Wayward]  temperament family: power
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is overconfident (+0.82)
RATINGS: [overall 92, Franchise player]
  - power: 100  (sees herself at 106, overrating)
  - accuracy: 80  (sees herself at 87, overrating)
  - pressure thresholds: exile 66, contract 63, spotlight 69, loyalty 27
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [none recorded]
DECISION_LOG: [none yet]
```

## A player whose personality changed (her soul stayed the same)

### Lourdes Andersen  (LB, Team 01)
```yaml
IDENTITY: [Lourdes Andersen, age 30, from Fargo ND; Walk-on turned starter]
SOUL (fixed): [+ Thumper, - Blitzes Poorly]  temperament family: power
PERSONALITY: [Competitor] wants to win everything in front of her; fears being outworked
  - allowed by her soul: Competitor, Hothead, Grinder, Loyalist; right now she is full of doubt (-0.59)
RATINGS: [overall 62, Depth]
  - pass_rush: 51  (sees herself at 46, doubting)
  - run_stop: 71  (sees herself at 66, doubting)
  - coverage: 59  (sees herself at 55, doubting)
  - pressure thresholds: exile 54, contract 55, spotlight 49, loyalty 26
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [became Grinder (was Competitor) 7; became Competitor (was Grinder) 12]
DECISION_LOG: [none yet]
```

## A retired player (cards are kept for the Archive)

### Elsa Alderman  (K, retired)
```yaml
IDENTITY: [Elsa Alderman, age 37, from Lubbock TX; Coach's daughter]
SOUL (fixed): [+ Well-Rounded, - No Glaring Weakness]  temperament family: balanced
PERSONALITY: [Diplomat] wants a calm, united team; fears locker-room civil war
  - allowed by her soul: Diplomat, Grinder, Loyalist, Mercenary; right now she is clear-eyed (+0.22)
RATINGS: [overall 92, Franchise player]
  - power: 90  (sees herself at 94, overrating)
  - accuracy: 93  (sees herself at 93)
  - pressure thresholds: exile 23, contract 53, spotlight 48, loyalty 57
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [retired 11]
DECISION_LOG: [none yet]
```

## Head coaches: a legend, a typical coach and a weak one

### Coach Aaliyah Lockhart  (Team 20)  -  LEGEND
```yaml
IDENTITY: [Aaliyah Lockhart, age 43, from Winnipeg MB; Rose through the assistant ranks]
PERSONALITY: [Gambler] wants a fourth-down legend; fears being second-guessed for the one that failed
ARCHETYPES: [+ Legend: Inspirer, - Undisciplined]
RATINGS:
  - offense: 91   -> +0.81 points of margin
  - defense: 90   -> +0.80 points of margin
  - development: 89   -> +0.31 rating points per year to each young player
  - gamecraft: 84   (no on-field effect yet)
  - discipline: 79   (no on-field effect yet)
  - motivation: 94   (no on-field effect yet)
  - pressure thresholds: exile 34, contract 51, spotlight 15, loyalty 48
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [hired 14]
DECISION_LOG: [none yet]
```
### Coach Alicia Arceneaux  (Team 40)
```yaml
IDENTITY: [Alicia Arceneaux, age 61, from Accra Ghana; Former star player turned coach]
PERSONALITY: [Tactician] wants the cleverest scheme in the league; fears being out-schemed on a big night
ARCHETYPES: [+ Inspirer, - Stunts Growth]
RATINGS:
  - offense: 54   -> +0.07 points of margin
  - defense: 48   -> -0.05 points of margin
  - development: 33   -> -0.14 rating points per year to each young player
  - gamecraft: 66   (no on-field effect yet)
  - discipline: 60   (no on-field effect yet)
  - motivation: 74   (no on-field effect yet)
  - pressure thresholds: exile 41, contract 39, spotlight 42, loyalty 59
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [hired 10]
DECISION_LOG: [none yet]
```
### Coach Camila Toussaint  (Team 27)
```yaml
IDENTITY: [Camila Toussaint, age 44, from Spokane WA; Came over from another league]
PERSONALITY: [Gambler] wants a fourth-down legend; fears being second-guessed for the one that failed
ARCHETYPES: [+ Clock Manager, - Leaky Defense]
RATINGS:
  - offense: 28   -> -0.44 points of margin
  - defense: 26   -> -0.49 points of margin
  - development: 43   -> -0.05 rating points per year to each young player
  - gamecraft: 70   (no on-field effect yet)
  - discipline: 50   (no on-field effect yet)
  - motivation: 47   (no on-field effect yet)
  - pressure thresholds: exile 35, contract 45, spotlight 48, loyalty 52
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [hired 12]
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
  - fan approval right now: 60%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 62, media 69, losing 51, subsidy 48
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [bought 0]
DECISION_LOG: [none yet]
```
### Owner Sylvie Solberg  (Team 12, recalled)
```yaml
IDENTITY: [Sylvie Solberg, age 65, from Spokane WA; Sports-franchise veteran]
PERSONALITY: [Meddler] wants a hand in every decision; fears being irrelevant
ARCHETYPES: [+ Relentless Competitor, - Absentee Owner]
RATINGS:
  - patience: 61
  - ambition: 71
  - involvement: 56
  - popularity: 60
  - business: 65
  - fan approval right now: 43%  (a recall vote is triggered under 40%)
  - pressure thresholds: recall 52, media 51, losing 73, subsidy 39
RELATIONSHIPS: {}  # none yet; filled by Interactions
CAREER: [elected 13; recalled 14]
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
team: 44
trigger: approval
approval: 0.375
recall_share: 0.51
result: recalled
owner: Kimi Eberhardt
replacement: Angela Tillman
candidates: ['Laila Goldberg', 'Oona Kruger', 'Tilda Obuya', 'Angela Tillman', 'Eliana Beaumont']
```


## How the cards spread across the league

**Core personalities (all rostered players):** Diplomat 529, Competitor 439, Grinder 343, Perfectionist 309, Showman 227, Quiet Leader 143, Hothead 105, Free Spirit 96, Mercenary 41, Loyalist 24

**Most common positive archetypes:** Well-Rounded 692, Ballhawk 115, Road Grader 104, Run Stuffer 98, Pass-Pro Wall 96, Route Technician 78, Edge Terror 76, Willing Tackler 74

**Coach effect across the 48 teams:** average -0.05, spread (sd) 0.55, best +1.76, worst -0.93 points of expected margin. For scale, team talent has a spread of about 3 to 4 points.

**Personality shifts:** 784 of 5287 players have changed personality at least once in 14 seasons.

**Legends:** 6 of 174 coaches hired so far are legends; 2 on the field now.

**Recall votes:** 187 in 14 seasons (13.4 a year); 49 owners recalled (3.5 a year), 26% of votes. Owners retire on their own too: 44 so far.

**Firings:** 57 coaches and 34 GMs fired in 14 seasons.

**Coaches so far:** 174 hired and 126 retired in 14 seasons.

**Players with cards:** 2360 active or unsigned, 3031 retired.
