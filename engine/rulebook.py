"""The DFL Rulebook, as data (v1, frozen 2026-10-06).

The prose rulebook ("DFL Rulebook: The Synthesis", a living doc) decides every rule by one test, in order:
  1. skeleton   The Commissioner's own rule. Not re-opened.
  2. nfl        the real NFL rule, copied.
  3. adapted    the NFL rule, changed only as far as 48 teams, 18 games and the exile system force.
  4. fair       no usable NFL rule, so chosen to keep the fair-competitiveness bands in range.

Everything decided before the pause (docs/decisions_pre_rebase.md) is reference only.
This file is the code's view of the rulebook: one row per rule, with the value the rulebook sets for any rule that is a number,
and an honest status for how the engine compares:

  built    every named constant exists in rules.py / economy.py and equals the rulebook value
  differs  the engine has the constant (or the mechanism) but with another value: it must change
  missing  the rulebook sets it and the engine has no such constant yet (the name is the one to add)

engine/check_rulebook.py fails if a status is untrue (a "built" row whose value drifted, a "differs" row that now matches, a "missing"
row whose constant has appeared) or if a constant in rules.py / economy.py is in no row. So this file cannot go stale quietly.

`mechanism` is a hand-kept note on behaviour that a constant cannot show (built / partial / not built). The check cannot verify it.
"""
SKELETON, NFL, ADAPTED, FAIR = "skeleton", "nfl", "adapted", "fair"
BASES = (SKELETON, NFL, ADAPTED, FAIR)

# Constants that are not rules. Each needs a reason.
EXEMPT = {
    "rules.SKELETON": "label vocabulary of the basis table",
    "rules.NFL": "label vocabulary of the basis table",
    "rules.ADAPTED": "label vocabulary of the basis table",
    "rules.FAIR": "label vocabulary of the basis table",
    "rules.MODEL": "label vocabulary of the basis table",
    "rules.BASIS": "the basis of each rule, one entry per rule or group; the rulebook rows are the authority",
    "rules.FINAL_OLD_NAME": "the old name \"Super Bowl\", kept so the old text can be read",
    "economy.C": "an imported module, not a constant",
    "economy.PAY_SCALE": "market-price model dial (what a rating costs); not a rule",
    "economy.PAY_POWER": "market-price model dial; not a rule",
    "economy.POS_PAY": "market-price model dial; not a rule",
    "economy.INIT_PAYROLL": "founding-league setup dial; not a rule",
}

ROWS = [
    # ---------------------------------------------------------------- skeleton: shape, schedule, exile, playoffs
    dict(id="shape", area="Skeleton", basis=SKELETON, status="built", mechanism="built",
         rule="48 teams, 2 conferences, 8 divisions of 6; each division has one exile slot, so 40 teams play and 8 are exiled",
         expect={"rules.TOTAL_TEAMS": 48, "rules.DIVISIONS_PER_CONFERENCE": 4, "rules.TEAMS_PER_DIVISION": 6,
                 "rules.ACTIVE_PER_DIVISION": 5, "rules.EXILE_SLOTS_PER_DIVISION": 1, "rules.TOTAL_DIVISIONS": 8,
                 "rules.ACTIVE_TEAMS": 40, "rules.EXILED_TEAMS": 8},
         covers=["rules.CONFERENCES"]),
    dict(id="schedule", area="Skeleton", basis=SKELETON, status="built", mechanism="built",
         rule="18 games over 19 weeks (one bye): 4 non-conference same-tier, 4+4 division, 6 tier-based; 9 home and 9 away",
         expect={"rules.GAMES_PER_TEAM": 18, "rules.REGULAR_SEASON_WEEKS": 19, "rules.NON_CONFERENCE_GAMES": 4,
                 "rules.DIVISION_GAMES_FIRST_BLOCK": 4, "rules.DIVISION_GAMES_SECOND_BLOCK": 4, "rules.TIER_BASED_GAMES": 6,
                 "rules.WEEKS_NON_CONFERENCE": (1, 4), "rules.WEEKS_CONFERENCE": (5, 14), "rules.WEEKS_DIVISIONAL": (15, 19),
                 "rules.TIERS": (1, 2, 3, 4, 5),
                 "rules.TIER_OPPONENTS": {1: (1, 2), 2: (1, 3), 3: (2, 4), 4: (3, 5), 5: (4, 5)}}),
    dict(id="schedule.tier_earning", area="Skeleton", basis=FAIR, status="built", mechanism="built",
         rule="A team's tier is its last division finish (1st = Tier 1 ... 4th = Tier 4); the team back from exile is Tier 5; which weeks carry division games is a scheduling detail",
         expect={"rules.TIER_FROM": "last_division_finish", "rules.EXILE_RETURN_TIER": 5},
         covers=["rules.CONFERENCE_BLOCK_DIVISION_WEEKS"]),
    dict(id="exile", area="Skeleton", basis=SKELETON, status="built", mechanism="built",
         rule="Finish 5th in the division: exiled for one season, returns as Tier 5; exile is help, not punishment, aimed so a returning team can compete for 3rd",
         expect={"rules.EXILE_TRIGGER_FINISH": 5, "rules.EXILE_DURATION_SEASONS": 1, "rules.EXILE_IS_PUNISHMENT": False,
                 "rules.EXILE_TARGET_DIVISION_FINISH": 3, "rules.FIFTH_PLACE_WILD_CARD_ELIGIBLE": False}),
    dict(id="exile.ambassador", area="Skeleton", basis=SKELETON, status="built", mechanism="built",
         rule="Exiled teams play the Ambassador Season: a 7-game round robin among the 8, then an Ambassador Bowl",
         expect={"rules.AMBASSADOR_ROUND_ROBIN_TEAMS": 8, "rules.AMBASSADOR_GAMES_PER_TEAM": 7, "rules.AMBASSADOR_TOTAL_GAMES": 28,
                 "rules.AMBASSADOR_WEEKS": (1, 7), "rules.AMBASSADOR_BOWL_WEEK": 8}),
    dict(id="playoffs", area="Skeleton", basis=SKELETON, status="built", mechanism="built",
         rule="7 per conference (4 division winners + 3 wild cards), seed 1 has a bye, 13 games in all; the final is the Diamond Coronation, champion gets the Diamond Tiara, at a neutral site",
         expect={"rules.DIVISION_WINNERS_PER_CONFERENCE": 4, "rules.WILD_CARDS_PER_CONFERENCE": 3,
                 "rules.PLAYOFF_SEEDS_PER_CONFERENCE": 7, "rules.PLAYOFF_TEAMS": 14, "rules.TOP_SEED_HAS_BYE": True,
                 "rules.PLAYOFF_WEEKS": 4, "rules.GAME_WEEKS_TOTAL": 23, "rules.WILD_CARD_WEEK": 20, "rules.DIVISIONAL_WEEK": 21,
                 "rules.CHAMPIONSHIP_WEEK": 22, "rules.FINAL_WEEK": 23, "rules.FINAL_IS_NEUTRAL_SITE": True,
                 "rules.FINAL_NAME": "Diamond Coronation", "rules.FINAL_AWARD": "Diamond Tiara"}),
    dict(id="fairness", area="Skeleton", basis=SKELETON, status="built", mechanism="built",
         rule="Every test is judged against the fair-competitiveness bands (13 of them, accepted by the Commissioner as working limits)",
         covers=["rules.FAIR_COMPETITION_BANDS"]),
    dict(id="operations", area="Skeleton", basis=SKELETON, status="built", mechanism="built",
         rule="How the sim is run and the card limits: 4 agent workers, 2 real weeks a season, ratings 1-100, relationships -100 to +100",
         expect={"rules.AGENT_WORKERS": 4, "rules.REAL_WEEKS_PER_SEASON": 2, "rules.RATING_MIN": 1, "rules.RATING_MAX": 100,
                 "rules.RELATIONSHIP_MIN": -100, "rules.RELATIONSHIP_MAX": 100}),

    # ---------------------------------------------------------------- schedule, overtime, tiebreakers
    dict(id="ties", area="Standings", basis=NFL, status="built", mechanism="partial",
         rule="Regular-season ties are possible and count as half a win; postseason games never end in a tie. Built in games, standings and tiebreaks. Gap: the drive engine ties in about 1.5% of games (NFL about 0.24%); the overtime scoring is re-fitted in build step 9.",
         expect={"rules.TIES_ALLOWED": True}),
    dict(id="overtime", area="Standings", basis=NFL, status="built", mechanism="built",
         rule="Regular season: 10-minute overtime, both teams possess even after a touchdown, then sudden death, tie if still level. Postseason: 15-minute periods, no ties.",
         expect={}),
    dict(id="overtime.constants", area="Standings", basis=NFL, status="built", mechanism="built",
         rule="Overtime lengths", expect={"rules.OVERTIME_MINUTES_REGULAR": 10, "rules.OVERTIME_MINUTES_POST": 15}),
    dict(id="tiebreak.lists", area="Standings", basis=NFL, status="built", mechanism="built",
         rule="NFL division and wild-card tiebreaker lists (checked against nfl.com 2026-10-06). The list restarts when two clubs remain, and for division ties when three remain after a fourth is eliminated. The short Phase 1 lists are kept for comparison only.",
         expect={"rules.TIEBREAK_STYLE": "nfl"},
         covers=["rules.TIEBREAKERS", "rules.CROSS_DIVISION_TIEBREAKERS", "rules.RECORD_ONLY_TIEBREAKERS"]),

    # ---------------------------------------------------------------- draft
    dict(id="draft.lottery", area="Draft", basis=SKELETON, status="built", mechanism="built",
         rule="Lottery of the 8 teams that just finished 5th: 36 balls (worst holds 8 ... best holds 1), 4 balls drawn for picks 1-4, the rest pick 5-8 by record; returners pick as a block at the end of the 9-34 band",
         expect={"rules.LOTTERY_TEAMS": 8, "rules.LOTTERY_DRAWN_PICKS": 4, "rules.LOTTERY_WEIGHTS": (8, 7, 6, 5, 4, 3, 2, 1),
                 "rules.LOTTERY_POOL": "just_finished_fifth", "rules.RETURNER_DRAFT_SLOT": "end_of_band"}),
    dict(id="draft.bands", area="Draft", basis=SKELETON, status="built", mechanism="built",
         rule="Every round has the same 48 places: 1-8 lottery, 9-34 non-playoff teams and returners, 35-48 playoff teams ordered by how far they got",
         expect={"rules.DRAFT_PICKS": {"exiled_lottery": (1, 8), "active_non_playoff": (9, 34), "playoff_teams": (35, 48)}}),
    dict(id="draft.rounds", area="Draft", basis=ADAPTED, status="built", mechanism="built",
         rule="7 rounds of 48 picks, 336 in all, the same 48-place order every round; the rookie's rating falls with the overall pick and the pick sets the rookie-scale salary",
         expect={"rules.DRAFT_ROUNDS": 7, "rules.DRAFT_PICKS_PER_ROUND": 48}),
    dict(id="draft.compensatory", area="Draft", basis=ADAPTED, status="missing", mechanism="not built",
         rule="Compensatory picks at the end of rounds 3-7 for net losses of qualifying free agents: at most 48 a year, 4 for any one team",
         expect={"rules.COMP_PICKS_MAX": 48, "rules.COMP_PICKS_PER_TEAM_MAX": 4}),
    dict(id="draft.trading", area="Draft", basis=NFL, status="missing", mechanism="not built",
         rule="Picks may be traded for the current draft and up to three drafts ahead",
         expect={"rules.PICK_TRADE_YEARS_AHEAD": 3}),
    dict(id="draft.clock", area="Draft", basis=NFL, status="built", mechanism="partial",
         rule="Minutes a pick: 8 in round 1, 7 in round 2, 5 in rounds 3-6, 4 in round 7, then autopilot. The constants exist; picks are made by the autopilot formula at once until agents draft.",
         expect={"rules.DRAFT_CLOCK_MINUTES": (8, 7, 5, 5, 5, 5, 4)}),

    # ---------------------------------------------------------------- rosters
    dict(id="roster.size", area="Rosters", basis=NFL, status="built", mechanism="built",
         rule="53 on the roster, with the DFL's own split across the 11 modelled positions (QB 3, RB 4, WR 6, TE 4, OL 9, DL 8, LB 6, CB 6, S 5, K 1, P 1)",
         expect={"economy.ROSTER_SIZE": 53, "rules.ROSTER_LIMIT": 53}, covers=["economy.SQUAD_SIZE"]),
    dict(id="roster.lists", area="Rosters", basis=NFL, status="built", mechanism="partial",
         rule="90 in camp cut to 53, 48 active on game day, practice squad of 16 (rookies and second-year players, at most 6 veterans), up to 8 injured-reserve returns a season after at least 4 games; exiled teams keep the same lists. Seasons in the league stand in for accrued seasons until step 6, and practice-squad elevations to game day are not modelled.",
         expect={"rules.CAMP_LIMIT": 90, "rules.ACTIVE_LIMIT": 48, "rules.PRACTICE_SQUAD_SIZE": 16, "rules.PRACTICE_SQUAD_SEASONS": 2,
                 "rules.PRACTICE_SQUAD_VETERANS_MAX": 6, "rules.IR_RETURNS_MAX": 8, "rules.IR_MIN_GAMES": 4}),

    # ---------------------------------------------------------------- contracts and the cap
    dict(id="cap", area="Cap", basis=SKELETON, status="built", mechanism="built",
         rule="$100M hard cap that never inflates; room banked to a $125M ceiling; ~90% floor; exiled teams' payroll counts at half. Dead money counts against the cap.",
         expect={"economy.CAP": 100.0, "economy.BANK_LIMIT": 125.0, "economy.FLOOR_FRAC": 0.90, "economy.ABSORPTION": 0.5,
                 "rules.EXILE_CAP_ABSORPTION": 0.50}),
    dict(id="cap.floor_window", area="Cap", basis=NFL, status="built", mechanism="built",
         rule="The floor is measured over rolling four-season windows of the seasons a team played (exile seasons are skipped); a shortfall is paid to that team's own players. Known simplification: the engine's cash is the cap number (base plus bonus share) plus dead money.",
         expect={"economy.FLOOR_WINDOW_SEASONS": 4}),
    dict(id="cap.offseason_count", area="Cap", basis=NFL, status="built", mechanism="built",
         rule="Offseason: only the 51 highest cap numbers count until the season begins (the 52nd and 53rd roster places and the practice squad are held back as a reserve so a team can still field its season inside the cap)",
         expect={"economy.OFFSEASON_COUNT": 51}, covers=["economy.OFFSEASON_RESERVE"]),
    dict(id="cap.equalization", area="Cap", basis=FAIR, status="built", mechanism="built",
         rule="Forfeited room is converted to dollars in an Equalization Fund that pays the league's half of exiled teams' payrolls; a deficit is covered equally by all 48 teams; what stands above a reserve (a model dial, $100M) is paid equally to the 40 playing teams. Teams' net cash from the Fund is kept for the finance model (step 7); 'any subsidy' arrives with revenue sharing in step 7.",
         expect={"economy.EQUALIZATION_SURPLUS_TEAMS": 40}, covers=["economy.FUND_RESERVE"]),
    dict(id="salary.minimum", area="Cap", basis=NFL, status="built", mechanism="built",
         rule="Minimum salary by credited seasons, NFL 2026 x 0.332: $0.29M, 0.33, 0.36, 0.38, 0.40, 0.43M. The lowest rung ($0.29M, a rookie) is the least anyone can be paid.",
         expect={"economy.MIN_SALARY": 0.29}),
    dict(id="salary.minimum_scale", area="Cap", basis=NFL, status="built", mechanism="partial",
         rule="The scale itself, by credited seasons 0, 1, 2, 3, 4-6, 7+ (seasons in the league stand in for credited seasons until step 6)",
         expect={"economy.MIN_SALARY_SCALE": (0.29, 0.33, 0.36, 0.38, 0.40, 0.43)}),
    dict(id="salary.maximum", area="Cap", basis=FAIR, status="built", mechanism="built",
         rule="Table limit: no contract's yearly cap value above 25% of the cap",
         expect={"economy.MAX_SALARY": 25.0}),
    dict(id="salary.staff", area="Cap", basis=FAIR, status="missing", mechanism="not built",
         rule="Staff pay is outside the cap, with limits: one staff contract at most 8% of the cap, the whole football staff at most 20%",
         expect={"economy.STAFF_CONTRACT_MAX_PCT": 0.08, "economy.STAFF_PAYROLL_MAX_PCT": 0.20}),
    dict(id="rookie.scale", area="Cap", basis=NFL, status="built", mechanism="built",
         rule="Four-year slot scale over all 336 picks, NFL x 0.332: pick 1 about $4.4M, $1.2M at the end of round 1, $0.65M at the end of round 2, $0.5M falling to $0.3M through rounds 3-7 (near the veteran minimum at pick 336); first-round deals fully guaranteed; every rookie deal carries a signing bonus (a model dial by round)",
         expect={"economy.ROOKIE_SCALE": ((1, 4.4), (48, 1.2), (96, 0.65), (97, 0.50), (336, 0.30)), "economy.ROOKIE_YEARS": 4},
         covers=["economy.ROOKIE_BONUS_SHARE"]),
    dict(id="rookie.undrafted", area="Cap", basis=NFL, status="built", mechanism="built",
         rule="Undrafted rookies sign for three years at the minimum",
         expect={"economy.UNDRAFTED_YEARS": 3}),
    dict(id="practice_squad.pay", area="Cap", basis=NFL, status="built", mechanism="built",
         rule="Practice-squad players are paid the practice-squad wage (NFL 2025 weekly scale x 0.332, about $0.10M a year) and count against the cap",
         expect={"economy.PRACTICE_SQUAD_SALARY": 0.10}),
    dict(id="resign", area="Cap", basis=NFL, status="differs", mechanism="differs",
         rule="Veteran deals and extensions are agreed at contract tables with each player's DFLPA representative; the engine re-signs expiring players by a probability dial. Extensions only after a drafted player's third season.",
         expect={}, covers=["economy.RESIGN_BASE"]),
    dict(id="contract.structure", area="Cap", basis=NFL, status="built", mechanism="partial",
         rule="Signing bonus prorated evenly over at most 5 years; contracts of 1-5 years; guarantees (veterans: the first year of the base; round-1 rookies: the whole contract); dead money on release, all in the year of release; two post-draft release designations a year that split the hit across two seasons. Known simplifications: injury and skill guarantees are one 'guaranteed' amount; the cap number is flat across a contract's years; retirement frees the contract.",
         expect={"economy.BONUS_PRORATION_MAX_YEARS": 5, "economy.CONTRACT_YEARS_MAX": 5, "economy.POST_DRAFT_DESIGNATIONS": 2},
         covers=["economy.VETERAN_BONUS_SHARE", "economy.BONUS_MIN_SALARY"]),

    # ---------------------------------------------------------------- free agency, tags, waivers, trades
    dict(id="fa.classes", area="Player movement", basis=NFL, status="built", mechanism="partial",
         rule="Accrued season = 6 qualifying regular-season or Ambassador round-robin games on the active/inactive roster or IR; credited season = 3 such games. Classification at expiration: unrestricted at 4+ accrued seasons, restricted at exactly 3, exclusive rights below 3; exiled clubs use restricted treatment. Service accounting and classification are built; tenders and rights enforcement, credited-service salary integration, and practice-squad eligibility integration remain pending. Founding and old-save service is estimated from prior years; generated rookies and founding practice-squad players start at zero.",
         expect={"rules.ACCRUED_SEASON_GAMES": 6, "rules.CREDITED_SEASON_GAMES": 3, "rules.UFA_SEASONS": 4, "rules.RFA_SEASONS": 3}),
    dict(id="fa.tenders", area="Player movement", basis=NFL, status="missing", mechanism="not built",
         rule="RFA tenders (first-round, second-round, original-round, right of first refusal), NFL 2026 x 0.332, or 110% of prior base salary if higher",
         expect={"economy.RFA_TENDERS": (2.69, 1.93, 1.22, 1.18)}),
    dict(id="fa.tags", area="Player movement", basis=ADAPTED, status="missing", mechanism="not built",
         rule="One tag a team a year. Franchise = average of the top 7 salaries at the position (NFL 5, scaled) or 120% of prior salary; transition = average of the top 15 (NFL 10, scaled); consecutive franchise tags 120% then 144%",
         expect={"economy.FRANCHISE_TAG_TOP_N": 7, "economy.TRANSITION_TAG_TOP_N": 15}),
    dict(id="fa.waivers", area="Player movement", basis=NFL, status="missing", mechanism="not built",
         rule="Players with under 4 accrued seasons go on waivers for 24 hours when released; vested veterans become free agents at once",
         expect={"rules.WAIVER_HOURS": 24}),
    dict(id="trade.deadline", area="Player movement", basis=NFL, status="missing", mechanism="not built",
         rule="Trades from the start of the league year to the Tuesday after Week 9; both teams under the cap after the trade; the receiving team takes the salary, signing-bonus proration stays with the team that traded",
         expect={"rules.TRADE_DEADLINE_WEEK": 9}),

    # ---------------------------------------------------------------- owners and finance
    dict(id="recall", area="Ownership", basis=SKELETON, status="built", mechanism="partial",
         rule="One division a year in rotation (every owner voted on once in 8 years); approval under 40% or exile calls an early vote; 1,000,000 fans, simple majority; 5 candidates; no one owns twice. Gap: the electorate is a number only, and the approval trigger sits inside the exile flag.",
         expect={"rules.RECALL_DIVISIONS_PER_YEAR": 1, "rules.RECALL_CYCLE_YEARS": 8, "rules.RECALL_APPROVAL_THRESHOLD": 0.40,
                 "rules.RECALL_VOTERS": 1_000_000, "rules.RECALL_REPLACEMENT_CANDIDATES": 5, "rules.RECALL_ON_EXILE": True,
                 "rules.OWNER_MAY_OWN_TWICE": False}),
    dict(id="forced_sale", area="Ownership", basis=SKELETON, status="built", mechanism="not built",
         rule="Two or more subsidised quarters in any rolling four; 25 of 48 owners vote, the owner concerned recused; immediate and final. The constants exist; there is no revenue, subsidy or vote in the engine.",
         expect={"rules.FORCED_SALE_SUBSIDY_QUARTERS": 2, "rules.FORCED_SALE_VOTES_NEEDED": 25}),
    dict(id="revenue", area="Finance", basis=NFL, status="missing", mechanism="not built",
         rule="National revenue shared equally among 48 teams; 34% of each team's ticket revenue goes into a pool shared equally; local revenue kept; four fiscal quarters on an accrual basis",
         expect={"rules.TICKET_POOL_SHARE": 0.34, "rules.FISCAL_QUARTERS": 4}),

    # ---------------------------------------------------------------- governance and the Commissioner
    dict(id="votes", area="Governance", basis=ADAPTED, status="missing", mechanism="not built",
         rule="Three-quarters of clubs (36 of 48) for rule, bylaw and playing-rule changes; two-thirds (32 of 48) to choose a Commissioner's successor (the first Commissioner is the league's human operator; NFL: 3/4 or 20, 2/3 or 18, whichever is greater); eight-member Competition Committee, one per division",
         expect={"rules.RULE_CHANGE_VOTES": 36, "rules.COMMISSIONER_VOTES": 32, "rules.COMPETITION_COMMITTEE_SEATS": 8}),
    dict(id="commissioner", area="Governance", basis=SKELETON, status="missing", mechanism="not built",
         rule="Every Commissioner power is shrink-only: reject, cap, delay or reduce; never add. Reviews every trade and contract against the cap and the bands.",
         expect={}),
    dict(id="dflpa.representative", area="DFLPA", basis=SKELETON, status="missing", mechanism="partial",
         rule="No independent agents. The DFLPA gives every player and coach a representative who advises her and ensures DFL rules, the CBA and fair competitiveness are respected; she may hold a deal back but never sets terms. Contract and trade tables exist; the representative is not yet a role.",
         expect={}),
    dict(id="discipline", area="Governance", basis=NFL, status="missing", mechanism="not built",
         rule="Conduct, substance and gambling policy, tampering and cap-circumvention penalties (up to 10% of the cap in a season), game-integrity penalties; every Commissioner penalty is a reduction and autopilot applies the baseline",
         expect={"rules.CAP_PENALTY_MAX_PCT": 0.10}),
    dict(id="hiring", area="Governance", basis=SKELETON, status="missing", mechanism="partial",
         rule="No decision, agent or text can read a character's demographics (names and portraits only); every head-coach or GM search interviews at least two external candidates; an audit fails if any outcome depends on demographics",
         expect={"rules.EXTERNAL_INTERVIEWS_MIN": 2}),
    dict(id="health", area="Health", basis=NFL, status="missing", mechanism="partial",
         rule="Injury report, concussion protocol (mandatory removal), injured lists. The engine has per-game injuries with placeholder rates only.",
         expect={}),
]
