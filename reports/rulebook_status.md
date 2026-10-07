# Rulebook status: code against the DFL Rulebook

Written by `engine/check_rulebook.py`. The prose rulebook is the living doc "DFL Rulebook: The Synthesis"; `engine/rulebook.py` is its machine-readable form, one row per rule. **built** = the code matches the rulebook value; **differs** = the code has it with another value or another mechanism and must change; **missing** = the rulebook sets it and the code has nothing yet.

| Area | built | differs | missing |
| --- | --- | --- | --- |
| Skeleton | 8 | 0 | 0 |
| Standings | 4 | 0 | 0 |
| Draft | 4 | 0 | 2 |
| Rosters | 2 | 0 | 0 |
| Cap | 11 | 1 | 1 |
| Player movement | 1 | 0 | 4 |
| Ownership | 2 | 0 | 0 |
| Finance | 0 | 0 | 1 |
| Governance | 0 | 0 | 4 |
| DFLPA | 0 | 0 | 1 |
| Health | 0 | 0 | 1 |
| **All** | 32 | 1 | 14 |

## The code differs from the rulebook

| Rule | Basis | What the rulebook says |
| --- | --- | --- |
| `resign` | nfl | Veteran deals and extensions are agreed at contract tables with each player's DFLPA representative; the engine re-signs expiring players by a probability dial. Extensions only after a drafted player's third season. |

## The rulebook sets it and the code has nothing yet

| Rule | Basis | What the rulebook says |
| --- | --- | --- |
| `draft.compensatory` | adapted | Compensatory picks at the end of rounds 3-7 for net losses of qualifying free agents: at most 48 a year, 4 for any one team |
| `draft.trading` | nfl | Picks may be traded for the current draft and up to three drafts ahead |
| `salary.staff` | fair | Staff pay is outside the cap, with limits: one staff contract at most 8% of the cap, the whole football staff at most 20% |
| `fa.tenders` | nfl | RFA tenders (first-round, second-round, original-round, right of first refusal), NFL 2026 x 0.332, or 110% of prior base salary if higher |
| `fa.tags` | adapted | One tag a team a year. Franchise = average of the top 7 salaries at the position (NFL 5, scaled) or 120% of prior salary; transition = average of the top 15 (NFL 10, scaled); consecutive franchise tags 120% then 144% |
| `fa.waivers` | nfl | Players with under 4 accrued seasons go on waivers for 24 hours when released; vested veterans become free agents at once |
| `trade.deadline` | nfl | Trades from the start of the league year to the Tuesday after Week 9; both teams under the cap after the trade; the receiving team takes the salary, signing-bonus proration stays with the team that traded |
| `revenue` | nfl | National revenue shared equally among 48 teams; 34% of each team's ticket revenue goes into a pool shared equally; local revenue kept; four fiscal quarters on an accrual basis |
| `votes` | adapted | Three-quarters of clubs (36 of 48) for rule, bylaw and playing-rule changes; two-thirds (32 of 48) to choose a Commissioner's successor (the first Commissioner is the league's human operator; NFL: 3/4 or 20, 2/3 or 18, whichever is greater); eight-member Competition Committee, one per division |
| `commissioner` | skeleton | Every Commissioner power is shrink-only: reject, cap, delay or reduce; never add. Reviews every trade and contract against the cap and the bands. |
| `dflpa.representative` | skeleton | No independent agents. The DFLPA gives every player and coach a representative who advises her and ensures DFL rules, the CBA and fair competitiveness are respected; she may hold a deal back but never sets terms. Contract and trade tables exist; the representative is not yet a role. |
| `discipline` | nfl | Conduct, substance and gambling policy, tampering and cap-circumvention penalties (up to 10% of the cap in a season), game-integrity penalties; every Commissioner penalty is a reduction and autopilot applies the baseline |
| `hiring` | skeleton | No decision, agent or text can read a character's demographics (names and portraits only); every head-coach or GM search interviews at least two external candidates; an audit fails if any outcome depends on demographics |
| `health` | nfl | Injury report, concussion protocol (mandatory removal), injured lists. The engine has per-game injuries with placeholder rates only. |

## The code matches the rulebook

| Rule | Basis | What the rulebook says |
| --- | --- | --- |
| `shape` | skeleton | 48 teams, 2 conferences, 8 divisions of 6; each division has one exile slot, so 40 teams play and 8 are exiled |
| `schedule` | skeleton | 18 games over 19 weeks (one bye): 4 non-conference same-tier, 4+4 division, 6 tier-based; 9 home and 9 away |
| `schedule.tier_earning` | fair | A team's tier is its last division finish (1st = Tier 1 ... 4th = Tier 4); the team back from exile is Tier 5; which weeks carry division games is a scheduling detail |
| `exile` | skeleton | Finish 5th in the division: exiled for one season, returns as Tier 5; exile is help, not punishment, aimed so a returning team can compete for 3rd |
| `exile.ambassador` | skeleton | Exiled teams play the Ambassador Season: a 7-game round robin among the 8, then an Ambassador Bowl |
| `playoffs` | skeleton | 7 per conference (4 division winners + 3 wild cards), seed 1 has a bye, 13 games in all; the final is the Diamond Coronation, champion gets the Diamond Tiara, at a neutral site |
| `fairness` | skeleton | Every test is judged against the fair-competitiveness bands (13 of them, accepted by the Commissioner as working limits) |
| `operations` | skeleton | How the sim is run and the card limits: 4 agent workers, 2 real weeks a season, ratings 1-100, relationships -100 to +100 |
| `ties` | nfl | Regular-season ties are possible and count as half a win; postseason games never end in a tie. Built in games, standings and tiebreaks. Gap: the drive engine ties in about 1.5% of games (NFL about 0.24%); the overtime scoring is re-fitted in build step 9. |
| `overtime` | nfl | Regular season: 10-minute overtime, both teams possess even after a touchdown, then sudden death, tie if still level. Postseason: 15-minute periods, no ties. |
| `overtime.constants` | nfl | Overtime lengths |
| `tiebreak.lists` | nfl | NFL division and wild-card tiebreaker lists (checked against nfl.com 2026-10-06). The list restarts when two clubs remain, and for division ties when three remain after a fourth is eliminated. The short Phase 1 lists are kept for comparison only. |
| `draft.lottery` | skeleton | Lottery of the 8 teams that just finished 5th: 36 balls (worst holds 8 ... best holds 1), 4 balls drawn for picks 1-4, the rest pick 5-8 by record; returners pick as a block at the end of the 9-34 band |
| `draft.bands` | skeleton | Every round has the same 48 places: 1-8 lottery, 9-34 non-playoff teams and returners, 35-48 playoff teams ordered by how far they got |
| `draft.rounds` | adapted | 7 rounds of 48 picks, 336 in all, the same 48-place order every round; the rookie's rating falls with the overall pick and the pick sets the rookie-scale salary |
| `draft.clock` | nfl | Minutes a pick: 8 in round 1, 7 in round 2, 5 in rounds 3-6, 4 in round 7, then autopilot. The constants exist; picks are made by the autopilot formula at once until agents draft. |
| `roster.size` | nfl | 53 on the roster, with the DFL's own split across the 11 modelled positions (QB 3, RB 4, WR 6, TE 4, OL 9, DL 8, LB 6, CB 6, S 5, K 1, P 1) |
| `roster.lists` | nfl | 90 in camp cut to 53, 48 active on game day, practice squad of 16 (rookies and second-year players, at most 6 veterans), up to 8 injured-reserve returns a season after at least 4 games; exiled teams keep the same lists. Earned accrued service controls practice-squad eligibility; practice-squad elevations to game day are not modelled. |
| `cap` | skeleton | $100M hard cap that never inflates; room banked to a $125M ceiling; ~90% floor; exiled teams' payroll counts at half. Dead money counts against the cap. |
| `cap.floor_window` | nfl | The floor is measured over rolling four-season windows of the seasons a team played (exile seasons are skipped); a shortfall is paid to that team's own players. Known simplification: the engine's cash is the cap number (base plus bonus share) plus dead money. |
| `cap.offseason_count` | nfl | Offseason: only the 51 highest cap numbers count until the season begins (the 52nd and 53rd roster places and the practice squad are held back as a reserve so a team can still field its season inside the cap) |
| `cap.equalization` | fair | Forfeited room is converted to dollars in an Equalization Fund that pays the league's half of exiled teams' payrolls; a deficit is covered equally by all 48 teams; what stands above a reserve (a model dial, $100M) is paid equally to the 40 playing teams. Teams' net cash from the Fund is kept for the finance model (step 7); 'any subsidy' arrives with revenue sharing in step 7. |
| `salary.minimum` | nfl | Minimum salary by credited seasons, NFL 2026 x 0.332: $0.29M, 0.33, 0.36, 0.38, 0.40, 0.43M. The lowest rung ($0.29M, a rookie) is the least anyone can be paid. |
| `salary.minimum_scale` | nfl | The scale itself, by credited seasons 0, 1, 2, 3, 4-6, 7+ (earned credited service controls minimum base pay, including continuing-contract floors) |
| `salary.maximum` | fair | Table limit: no contract's yearly cap value above 25% of the cap |
| `rookie.scale` | nfl | Four-year slot scale over all 336 picks, NFL x 0.332: pick 1 about $4.4M, $1.2M at the end of round 1, $0.65M at the end of round 2, $0.5M falling to $0.3M through rounds 3-7 (near the veteran minimum at pick 336); first-round deals fully guaranteed; every rookie deal carries a signing bonus (a model dial by round) |
| `rookie.undrafted` | nfl | Undrafted rookies sign for three years at the minimum |
| `practice_squad.pay` | nfl | Practice-squad players are paid the practice-squad wage (NFL 2025 weekly scale x 0.332, about $0.10M a year) and count against the cap |
| `contract.structure` | nfl | Signing bonus prorated evenly over at most 5 years; contracts of 1-5 years; guarantees (veterans: the first year of the base; round-1 rookies: the whole contract); dead money on release, all in the year of release; two post-draft release designations a year that split the hit across two seasons. Known simplifications: injury and skill guarantees are one 'guaranteed' amount; the cap number is otherwise flat, with earned-service minimum base-pay increases; retirement frees the contract. |
| `fa.classes` | nfl | Accrued season = 6 qualifying regular-season or Ambassador round-robin games on the active/inactive roster or IR; credited season = 3 active/inactive roster games (IR does not count for minimum-salary credit, CBA Article 26 Section 2). Classification at expiration: unrestricted at 4+ accrued seasons, restricted at exactly 3, exclusive rights below 3; exiled clubs use restricted treatment. Service accounting and classification are built; credited-service minimum base pay and accrued-service practice-squad eligibility are integrated; tenders and rights enforcement remain pending. Founding and old-save service is estimated from prior years; generated rookies and founding practice-squad players start at zero. |
| `recall` | skeleton | One division a year in rotation (every owner voted on once in 8 years); approval under 40% or exile calls an early vote; 1,000,000 fans, simple majority; 5 candidates; no one owns twice. Gap: the electorate is a number only, and the approval trigger sits inside the exile flag. |
| `forced_sale` | skeleton | Two or more subsidised quarters in any rolling four; 25 of 48 owners vote, the owner concerned recused; immediate and final. The constants exist; there is no revenue, subsidy or vote in the engine. |

## Constants match but the behaviour is not all there (hand-kept note)

| Rule | Mechanism | What the rulebook says |
| --- | --- | --- |
| `ties` | partial | Regular-season ties are possible and count as half a win; postseason games never end in a tie. Built in games, standings and tiebreaks. Gap: the drive engine ties in about 1.5% of games (NFL about 0.24%); the overtime scoring is re-fitted in build step 9. |
| `draft.clock` | partial | Minutes a pick: 8 in round 1, 7 in round 2, 5 in rounds 3-6, 4 in round 7, then autopilot. The constants exist; picks are made by the autopilot formula at once until agents draft. |
| `roster.lists` | partial | 90 in camp cut to 53, 48 active on game day, practice squad of 16 (rookies and second-year players, at most 6 veterans), up to 8 injured-reserve returns a season after at least 4 games; exiled teams keep the same lists. Earned accrued service controls practice-squad eligibility; practice-squad elevations to game day are not modelled. |
| `contract.structure` | partial | Signing bonus prorated evenly over at most 5 years; contracts of 1-5 years; guarantees (veterans: the first year of the base; round-1 rookies: the whole contract); dead money on release, all in the year of release; two post-draft release designations a year that split the hit across two seasons. Known simplifications: injury and skill guarantees are one 'guaranteed' amount; the cap number is otherwise flat, with earned-service minimum base-pay increases; retirement frees the contract. |
| `fa.classes` | partial | Accrued season = 6 qualifying regular-season or Ambassador round-robin games on the active/inactive roster or IR; credited season = 3 active/inactive roster games (IR does not count for minimum-salary credit, CBA Article 26 Section 2). Classification at expiration: unrestricted at 4+ accrued seasons, restricted at exactly 3, exclusive rights below 3; exiled clubs use restricted treatment. Service accounting and classification are built; credited-service minimum base pay and accrued-service practice-squad eligibility are integrated; tenders and rights enforcement remain pending. Founding and old-save service is estimated from prior years; generated rookies and founding practice-squad players start at zero. |
| `recall` | partial | One division a year in rotation (every owner voted on once in 8 years); approval under 40% or exile calls an early vote; 1,000,000 fans, simple majority; 5 candidates; no one owns twice. Gap: the electorate is a number only, and the approval trigger sits inside the exile flag. |
| `forced_sale` | not built | Two or more subsidised quarters in any rolling four; 25 of 48 owners vote, the owner concerned recused; immediate and final. The constants exist; there is no revenue, subsidy or vote in the engine. |
