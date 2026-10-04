"""Diamond Football League (DFL) rules.

Every rule number lives here. No other file may hard-code one.
Change a number here and the whole league follows.
"""

# ---- League structure ------------------------------------------------------
CONFERENCES = ("Western", "Eastern")   # Western = blue, Eastern = red
DIVISIONS_PER_CONFERENCE = 4
TEAMS_PER_DIVISION = 6                 # 5 active + 1 exile slot
ACTIVE_PER_DIVISION = 5
EXILE_SLOTS_PER_DIVISION = 1

TOTAL_TEAMS = len(CONFERENCES) * DIVISIONS_PER_CONFERENCE * TEAMS_PER_DIVISION      # 48
ACTIVE_TEAMS = len(CONFERENCES) * DIVISIONS_PER_CONFERENCE * ACTIVE_PER_DIVISION    # 40
EXILED_TEAMS = TOTAL_TEAMS - ACTIVE_TEAMS                                           # 8

# ---- Tiers (schedule strength rank, 1 = strongest). NOT playoff seeds. ------
TIERS = (1, 2, 3, 4, 5)
# Tier-based non-division opponents: tier -> tiers it plays
TIER_OPPONENTS = {
    1: (1, 2),
    2: (1, 3),
    3: (2, 4),
    4: (3, 5),
    5: (4, 5),
}
EXILE_RETURN_TIER = 5

# ---- Regular season --------------------------------------------------------
GAMES_PER_TEAM = 18
NON_CONFERENCE_GAMES = 4        # weeks 1-4, same tier vs same tier
DIVISION_GAMES_FIRST_BLOCK = 4  # weeks 5-14
TIER_BASED_GAMES = 6            # weeks 5-14
DIVISION_GAMES_SECOND_BLOCK = 4 # weeks 15-19
WEEKS_NON_CONFERENCE = (1, 4)
WEEKS_CONFERENCE = (5, 14)
WEEKS_DIVISIONAL = (15, 19)
REGULAR_SEASON_WEEKS = 19       # 18 games + 1 bye
PLAYOFF_WEEKS = 4               # wild card, divisional, championship, final
GAME_WEEKS_TOTAL = REGULAR_SEASON_WEEKS + PLAYOFF_WEEKS   # 23

# ---- Playoffs --------------------------------------------------------------
DIVISION_WINNERS_PER_CONFERENCE = 4
WILD_CARDS_PER_CONFERENCE = 3
PLAYOFF_SEEDS_PER_CONFERENCE = DIVISION_WINNERS_PER_CONFERENCE + WILD_CARDS_PER_CONFERENCE  # 7
PLAYOFF_TEAMS = PLAYOFF_SEEDS_PER_CONFERENCE * len(CONFERENCES)                             # 14
TOP_SEED_HAS_BYE = True

# ---- Exile -----------------------------------------------------------------
EXILE_TRIGGER_FINISH = 5        # finish 5th in the division
EXILE_DURATION_SEASONS = 1
EXILE_CAP_ABSORPTION = 0.50     # 50% cap relief
AMBASSADOR_ROUND_ROBIN_TEAMS = EXILED_TEAMS
AMBASSADOR_GAMES_PER_TEAM = AMBASSADOR_ROUND_ROBIN_TEAMS - 1   # 7
AMBASSADOR_TOTAL_GAMES = AMBASSADOR_ROUND_ROBIN_TEAMS * AMBASSADOR_GAMES_PER_TEAM // 2  # 28

# ---- Tiebreakers (in order) ------------------------------------------------
TIEBREAKERS = (
    "head_to_head",
    "division_record",
    "point_differential",
    "seeded_coin_flip",
)

# ---- Draft -----------------------------------------------------------------
# Lottery: worst record -> best record among the exiled teams, percent, sums to 100
LOTTERY_WEIGHTS = (18, 16, 15, 13, 12, 10, 9, 7)
LOTTERY_APPLIES_TO = "teams_that_just_finished_fifth"
DRAFT_PICKS = {
    "exiled_lottery": (1, 8),
    "active_non_playoff": (9, 34),
    "playoff_teams": (35, 48),
}

# ---- Owner accountability --------------------------------------------------
RECALL_DIVISIONS_PER_CONFERENCE_PER_YEAR = 1
RECALL_CYCLE_YEARS = DIVISIONS_PER_CONFERENCE // RECALL_DIVISIONS_PER_CONFERENCE_PER_YEAR  # 4
RECALL_APPROVAL_THRESHOLD = 0.40
RECALL_VOTERS = 1_000_000
RECALL_REPLACEMENT_CANDIDATES = 5
FORCED_SALE_SUBSIDY_QUARTERS = 2
FORCED_SALE_VOTES_NEEDED = 25   # of 48 owners
OWNER_MAY_OWN_TWICE = False

# ---- Agents / real-time clock ---------------------------------------------
AGENT_WORKERS = 4
REAL_WEEKS_PER_SEASON = 2

# ---- Character card limits -------------------------------------------------
RATING_MIN, RATING_MAX = 1, 100
RELATIONSHIP_MIN, RELATIONSHIP_MAX = -100, 100


def placeholder_teams():
    """Build 48 placeholder teams: Team 01 .. Team 48. Real names come later."""
    teams = []
    n = 0
    for conf in CONFERENCES:
        for d in range(1, DIVISIONS_PER_CONFERENCE + 1):
            for slot in range(1, TEAMS_PER_DIVISION + 1):
                n += 1
                teams.append({
                    "id": n,
                    "name": f"Team {n:02d}",
                    "conference": conf,
                    "division": f"{conf} {d}",
                    "tier": slot if slot <= ACTIVE_PER_DIVISION else EXILE_RETURN_TIER,
                    "status": "active" if slot <= ACTIVE_PER_DIVISION else "exiled",
                })
    return teams
