"""Diamond Football League (DFL) rules.

Every rule number lives here. No other file may hard-code one.
Change a number here and the whole league follows.

Every rule is labelled with where it came from (see PROVENANCE at the bottom):

  CONFIRMED  Jeph wrote it in the rules text or said it in chat.
  ASSUMED    The AI proposed it to fill a gap. It is a working default only and
             stays provisional until Jeph confirms or changes it.

The game-result and talent model is NOT a rule. It is a stand-in that lives in
placeholder_model.py and is labelled as such.
"""

# ---- League structure (CONFIRMED) -----------------------------------------
CONFERENCES = ("Western", "Eastern")   # Western = blue, Eastern = red
DIVISIONS_PER_CONFERENCE = 4
TEAMS_PER_DIVISION = 6                 # 5 active + 1 exile slot
ACTIVE_PER_DIVISION = 5
EXILE_SLOTS_PER_DIVISION = 1

TOTAL_DIVISIONS = len(CONFERENCES) * DIVISIONS_PER_CONFERENCE                       # 8
TOTAL_TEAMS = TOTAL_DIVISIONS * TEAMS_PER_DIVISION                                  # 48
ACTIVE_TEAMS = TOTAL_DIVISIONS * ACTIVE_PER_DIVISION                                # 40
EXILED_TEAMS = TOTAL_TEAMS - ACTIVE_TEAMS                                           # 8

# ---- Tiers (schedule strength rank, 1 = strongest). NOT playoff seeds. -----
TIERS = (1, 2, 3, 4, 5)
# Tier-based non-division opponents: tier -> tiers it plays (CONFIRMED, from rules text)
TIER_OPPONENTS = {
    1: (1, 2),
    2: (1, 3),
    3: (2, 4),
    4: (3, 5),
    5: (4, 5),
}
EXILE_RETURN_TIER = 5                  # CONFIRMED: an exiled team returns as Tier 5
# ASSUMED: how a team earns its tier. Last season's finish inside its division:
# 1st -> Tier 1 ... 4th -> Tier 4, the team returning from exile -> Tier 5.
TIER_FROM = "last_division_finish"

# ---- Regular season (CONFIRMED) -------------------------------------------
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
WILD_CARD_WEEK, DIVISIONAL_WEEK, CHAMPIONSHIP_WEEK, FINAL_WEEK = 20, 21, 22, 23

# ASSUMED: inside weeks 5-14, the five weeks that carry division games. The other
# five weeks are tier-based games. (A 5-team division cannot all play each other in
# one week, so in a division week one team plays a tier-based game instead.)
CONFERENCE_BLOCK_DIVISION_WEEKS = (5, 7, 9, 11, 13)
# ASSUMED: games never end in a tie (overtime always produces a winner).
TIES_ALLOWED = False

# ---- Playoffs --------------------------------------------------------------
# CONFIRMED (Jeph answered this one): 4 division winners + 3 wild cards.
DIVISION_WINNERS_PER_CONFERENCE = 4
WILD_CARDS_PER_CONFERENCE = 3
PLAYOFF_SEEDS_PER_CONFERENCE = DIVISION_WINNERS_PER_CONFERENCE + WILD_CARDS_PER_CONFERENCE  # 7
PLAYOFF_TEAMS = PLAYOFF_SEEDS_PER_CONFERENCE * len(CONFERENCES)                             # 14
TOP_SEED_HAS_BYE = True
# CONFIRMED (Jeph, 2026-10-04): the final is the Diamond Coronation. The champion is presented with a Diamond Tiara
# rather than a trophy. "Super Bowl" appears in the old rules text and may still be used in conversation.
FINAL_NAME = "Diamond Coronation"
FINAL_AWARD = "Diamond Tiara"
FINAL_OLD_NAME = "Super Bowl"
# ASSUMED: seeds 1-4 are the division winners ranked by record; 5-7 the wild cards.
# ASSUMED: a team that finishes 5th in its division cannot be a wild card (it is exiled).
FIFTH_PLACE_WILD_CARD_ELIGIBLE = False
# ASSUMED: the Diamond Coronation is played at a neutral site (no home advantage).
FINAL_IS_NEUTRAL_SITE = True

# ---- Exile -----------------------------------------------------------------
EXILE_TRIGGER_FINISH = 5        # CONFIRMED: finish 5th in the division
EXILE_DURATION_SEASONS = 1
# CONFIRMED (Jeph, 2026-10-04): the LEAGUE does not treat exile as punishment. It is help for a
# distressed team (relief, plus play in exotic locations around the world while it rebuilds).
# Media and fans may feel differently. The help should be modest: a returning team should have
# the potential to compete for 3rd place in its division, sometimes succeeding, sometimes not.
# This is the target the placeholder benefits are tuned to (see calibrate_exile.py).
EXILE_IS_PUNISHMENT = False
EXILE_TARGET_DIVISION_FINISH = 3
EXILE_CAP_ABSORPTION = 0.50     # 50% cap relief (not used until the cap model exists)
AMBASSADOR_ROUND_ROBIN_TEAMS = EXILED_TEAMS
AMBASSADOR_GAMES_PER_TEAM = AMBASSADOR_ROUND_ROBIN_TEAMS - 1   # 7
AMBASSADOR_TOTAL_GAMES = AMBASSADOR_ROUND_ROBIN_TEAMS * AMBASSADOR_GAMES_PER_TEAM // 2  # 28
AMBASSADOR_WEEKS = (1, 7)       # ASSUMED placement
AMBASSADOR_BOWL_WEEK = 8        # ASSUMED: the two best Ambassador records meet

# ---- Tiebreakers -----------------------------------------------------------
# CONFIRMED (Jeph, 2026-10-04): all tie-breaking mirrors the NFL, at least for now. "nfl" uses the NFL's
# procedures (tiebreak.py). "simple" is the short Phase 1 list kept below for comparison and the old checks.
TIEBREAK_STYLE = "nfl"
# The simple Phase 1 lists (used only when TIEBREAK_STYLE = "simple").
# Division ranking, which decides exile:
TIEBREAKERS = (
    "head_to_head",
    "division_record",
    "point_differential",
    "seeded_coin_flip",
)
# ASSUMED: used to rank division winners and wild cards across divisions
# (head-to-head is skipped because those teams often never met).
CROSS_DIVISION_TIEBREAKERS = (
    "conference_record",
    "point_differential",
    "seeded_coin_flip",
)
# ASSUMED: used inside the Ambassador season and for ordering draft picks by record.
RECORD_ONLY_TIEBREAKERS = (
    "head_to_head",
    "point_differential",
    "seeded_coin_flip",
)

# ---- Draft -----------------------------------------------------------------
LOTTERY_TEAMS = 8               # CONFIRMED: 8 teams in the lottery
# CONFIRMED (Jeph, 2026-10-04): the number of balls a team holds depends on its rank among the 8. Four balls
# are drawn to decide picks 1-4; the other four teams take picks 5-8 in order of record (worst first).
LOTTERY_DRAWN_PICKS = 4
# CONFIRMED (Jeph, 2026-10-04): the lottery team with the best record holds 1 ball, the next best 2 balls, and so on
# up to 8 balls for the worst record. Listed worst record -> best record, so the worst team holds 8 of the 36 balls.
LOTTERY_WEIGHTS = (8, 7, 6, 5, 4, 3, 2, 1)
# CONFIRMED (Jeph, 2026-10-04): the lottery covers the 8 teams that just finished 5th.
# (The other option below is kept only so studies can compare it.)
#   "just_finished_fifth" = the 8 teams that just finished 5th (they sit out next season)
#   "just_finished_exile" = the 8 teams that just served their exile year (they return)
LOTTERY_POOL = "just_finished_fifth"
# CONFIRMED (Jeph, 2026-10-04, accepting the AI's advice from reports/exile_two_draft_study.md): a team back from exile has already had
# its lottery pick, so in its second draft it picks inside the 9-34 band as a block at the end (picks 27-34), ordered
# among themselves by Ambassador Season record. Options: "by_record" (mixed in with everyone, Phase 1 behaviour),
# "end_of_band", "start_of_band".
RETURNER_DRAFT_SLOT = "end_of_band"
# ASSUMED: the four draws are one at a time by weight, without replacement (a team already drawn is skipped).
DRAFT_PICKS = {
    "exiled_lottery": (1, 8),         # CONFIRMED
    "active_non_playoff": (9, 34),    # CONFIRMED
    "playoff_teams": (35, 48),        # CONFIRMED (by round, then record)
}

# ---- Fair competitiveness: the standard every test is judged against --------------------------
# CONFIRMED (Jeph, 2026-10-04): the test for any trend in the simulation is whether it falls outside the
# expected / accepted range of "fair competitiveness".
# CONFIRMED (Jeph, 2026-10-04): the ranges below, proposed by the AI, are accepted as the working limits. Change any of them here.
# name -> (low, high, plain-language meaning). Judged on pooled multi-season runs after a warm-up.
FAIR_COMPETITION_BANDS = {
    "win_pct_sd":           (0.13, 0.19, "spread of regular-season win percentage across teams (pure luck alone is about 0.12)"),
    "year_to_year_corr":    (0.10, 0.50, "how much a team's win % repeats from one season to the next (0 = pure luck, 1 = fixed)"),
    "close_game_share":     (0.35, 0.55, "share of games decided by 8 points or fewer"),
    "repeat_champion_rate": (0.00, 0.12, "share of seasons in which the champion is the previous champion"),
    "max_titles_in_20":     (0, 4.7, "most titles one team wins in any 20-season stretch, averaged over leagues. A league where every playoff team had exactly equal title odds averages 4.7 (40 equal teams would give 3.1), so this caps concentration at pure luck among the 14"),
    "worst_league_titles":  (0, 7, "most titles one team wins in any 20 seasons in the single worst league (7 or more happens under pure luck about 3% of the time, so it signals a dynasty)"),
    "best_team_title_odds": (0.08, 0.25, "how often the strongest team on paper wins the title"),
    "returner_avg_finish":  (2.8, 3.4, "average division finish of a team back from exile (3.0 = league average)"),
    "returner_win_div":     (0.10, 0.30, "share of returning teams that win their division"),
    "returner_fifth_again": (0.10, 0.30, "share of returning teams that finish 5th again"),
    "exile_effect":         (-0.5, 0.5, "extra team rating (points, about half a win per point) a team has two years after finishing 5th compared with one that finished 4th"),
    "exile_double_early":   (0.00, 0.10, "share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick in their second draft"),
    "stuck_at_bottom":      (0.00, 0.10, "share of team-seasons that follow three straight bottom-two finishes (pure luck gives about 0.06; exile years are skipped)"),
}

# ---- Owner accountability --------------------------------------------------
# CONFIRMED (Jeph, 2026-10-04): every division's owners are voted on once every
# 8 years, one division league-wide per year. The earlier "4-year cycle" was wrong.
RECALL_DIVISIONS_PER_YEAR = 1
RECALL_CYCLE_YEARS = TOTAL_DIVISIONS // RECALL_DIVISIONS_PER_YEAR   # 8
RECALL_APPROVAL_THRESHOLD = 0.40
RECALL_VOTERS = 1_000_000
RECALL_REPLACEMENT_CANDIDATES = 5
RECALL_ON_EXILE = True          # CONFIRMED (rules text: "Trigger: ... or team exiled")
FORCED_SALE_SUBSIDY_QUARTERS = 2
FORCED_SALE_VOTES_NEEDED = 25   # of 48 owners
OWNER_MAY_OWN_TWICE = False

# ---- Agents / real-time clock ---------------------------------------------
AGENT_WORKERS = 4
REAL_WEEKS_PER_SEASON = 2

# ---- Character card limits -------------------------------------------------
RATING_MIN, RATING_MAX = 1, 100
RELATIONSHIP_MIN, RELATIONSHIP_MAX = -100, 100

# ---- Where each rule came from --------------------------------------------
CONFIRMED = "confirmed"
ASSUMED = "assumed"
PROVENANCE = {
    "League structure (48 teams, 2 conferences, 8 divisions, 5 active + 1 exile slot)": CONFIRMED,
    "Schedule shape (18 games, 19 weeks, 4 non-conference, 4+4 division, 6 tier-based)": CONFIRMED,
    "Tier opponent table": CONFIRMED,
    "Exile trigger (finish 5th), one-season duration, return as Tier 5": CONFIRMED,
    "Ambassador Season (7-game round-robin among the 8 exiled teams + Ambassador Bowl)": CONFIRMED,
    "Playoff field (4 division winners + 3 wild cards per conference)": CONFIRMED,
    "Playoff bracket (wild card, divisional, championship, final; seed 1 bye)": CONFIRMED,
    "Draft bands (1-8 exiled lottery, 9-34 active non-playoff, 35-48 playoff)": CONFIRMED,
    "Lottery is 8 teams": CONFIRMED,
    "Lottery draws 4 balls for picks 1-4; the other 4 teams pick 5-8 by record": CONFIRMED,
    "Recall: 1 division league-wide per year, 8-year cycle": CONFIRMED,
    "Recall also triggered by exile": CONFIRMED,
    "Exile is relief, not punishment; a returning team can compete for about 3rd in its division": CONFIRMED,
    "Lottery balls: best record of the eight holds 1 ball, next best 2, ... worst 8 (36 balls)": CONFIRMED,
    "Which 8 teams are in the lottery (the teams that just finished 5th)": CONFIRMED,
    "Lottery drawn one pick at a time by weight": ASSUMED,
    "Teams back from exile pick as a block at the end of the 9-34 band (no stacking of two high picks)": CONFIRMED,
    "The final is the Diamond Coronation; the champion receives a Diamond Tiara": CONFIRMED,
    "How tiers are earned (last division finish)": ASSUMED,
    "Tiebreakers mirror the NFL": CONFIRMED,
    "NFL tiebreak adaptations (restart rule used to rank everyone, wild-card division reduction, Ambassador chain, estimated touchdowns)": ASSUMED,
    "5th-place teams cannot take a wild card": ASSUMED,
    "No tied games": ASSUMED,
    "Which weeks inside 5-14 carry division games": ASSUMED,
    "Home/away balance (9 home, 9 away)": ASSUMED,
    "Draft order inside the bands (worst record first, NFL tiebreakers)": ASSUMED,
    "Ambassador weeks and the Ambassador Bowl format": ASSUMED,
    "Order in which divisions come up for owner recall": ASSUMED,
    "Starting league (which teams begin in exile, starting tiers)": ASSUMED,
    "Character cards come in this order: players, then coaches, then the other categories": CONFIRMED,
    "Cards are generated by code from the league seed (a writing layer for backstories comes later)": CONFIRMED,
    "Coach cards may change results only by a small, capped amount, re-tested against the fairness bands": CONFIRMED,
    "How big the coach cap is (1.0 point of margin per side of the ball), coach ratings, aging and retirement, and every word list on the cards": ASSUMED,
    "Every test is judged against \"fair competitiveness\"": CONFIRMED,
    "The numeric ranges that define fair competitiveness (AI proposal, accepted by Jeph as working limits)": CONFIRMED,
}


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
