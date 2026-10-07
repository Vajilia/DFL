"""Phase 0 check: load the rules and verify that the numbers agree with each other."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules as R  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


teams = R.placeholder_teams()
active = [t for t in teams if t["status"] == "active"]
exiled = [t for t in teams if t["status"] == "exiled"]

print(f"Teams: {len(teams)}   Active: {len(active)}   Exiled: {len(exiled)}\n")

check("48 teams in total", len(teams) == R.TOTAL_TEAMS == 48)
check("40 active, 8 exiled", len(active) == R.ACTIVE_TEAMS == 40 and len(exiled) == R.EXILED_TEAMS == 8)
check("team ids are unique", len({t["id"] for t in teams}) == len(teams))
check("every division has 6 teams (5 active, 1 exile)", all(
    sum(1 for t in teams if t["division"] == d) == R.TEAMS_PER_DIVISION
    and sum(1 for t in active if t["division"] == d) == R.ACTIVE_PER_DIVISION
    for d in {t["division"] for t in teams}))

# Schedule: build each tier's game count from the rules, not from a typed-in 18
other_divisions = R.DIVISIONS_PER_CONFERENCE - 1
rivals = R.ACTIVE_PER_DIVISION - 1
for tier in R.TIERS:
    non_conf = R.DIVISIONS_PER_CONFERENCE                       # one same-tier team per other-conference division
    division = rivals * 2                                       # each rival twice
    tier_based = len(R.TIER_OPPONENTS[tier]) * other_divisions  # one team of each listed tier per other division
    total = non_conf + division + tier_based
    check(f"tier {tier} plays {R.GAMES_PER_TEAM} games", total == R.GAMES_PER_TEAM,
          f"{non_conf} non-conference + {division} division + {tier_based} tier-based = {total}")

check("week blocks add up to 19 weeks",
      (R.WEEKS_NON_CONFERENCE[1] - R.WEEKS_NON_CONFERENCE[0] + 1)
      + (R.WEEKS_CONFERENCE[1] - R.WEEKS_CONFERENCE[0] + 1)
      + (R.WEEKS_DIVISIONAL[1] - R.WEEKS_DIVISIONAL[0] + 1) == R.REGULAR_SEASON_WEEKS)
check("19 weeks gives exactly 1 bye", R.REGULAR_SEASON_WEEKS - R.GAMES_PER_TEAM == 1)
check("tier-based games per tier equal the setting", all(
    len(R.TIER_OPPONENTS[t]) * other_divisions == R.TIER_BASED_GAMES for t in R.TIERS))
check("tier opponent table is symmetric", all(
    t in R.TIER_OPPONENTS[o] for t in R.TIERS for o in R.TIER_OPPONENTS[t]))

# Playoffs
check("14 playoff teams (7 per conference)", R.PLAYOFF_TEAMS == 14 and R.PLAYOFF_SEEDS_PER_CONFERENCE == 7)
check("division winners fill 4 seeds per conference", R.DIVISION_WINNERS_PER_CONFERENCE == R.DIVISIONS_PER_CONFERENCE)

# Exile / Ambassador season
check("Ambassador round-robin: 7 games per team, 28 total",
      R.AMBASSADOR_GAMES_PER_TEAM == 7 and R.AMBASSADOR_TOTAL_GAMES == 28)
check("one exile per division", R.EXILE_SLOTS_PER_DIVISION * R.DIVISIONS_PER_CONFERENCE * len(R.CONFERENCES) == R.EXILED_TEAMS)

# Draft and lottery
check("lottery balls run 8 (worst record) down to 1 (best record), 36 in all", list(R.LOTTERY_WEIGHTS) == [8, 7, 6, 5, 4, 3, 2, 1] and sum(R.LOTTERY_WEIGHTS) == 36, f"sum = {sum(R.LOTTERY_WEIGHTS)}")
check("lottery has one weight per exiled team", len(R.LOTTERY_WEIGHTS) == R.EXILED_TEAMS)
check("lottery weights fall from worst to best", list(R.LOTTERY_WEIGHTS) == sorted(R.LOTTERY_WEIGHTS, reverse=True))
picks = sum(hi - lo + 1 for lo, hi in R.DRAFT_PICKS.values())
check("draft has 48 picks", picks == R.TOTAL_TEAMS, f"{picks} picks")
lo, hi = R.DRAFT_PICKS["exiled_lottery"]
check("lottery picks = exiled teams", hi - lo + 1 == R.EXILED_TEAMS)
lo, hi = R.DRAFT_PICKS["active_non_playoff"]
check("non-playoff active picks = 26", hi - lo + 1 == R.ACTIVE_TEAMS - R.PLAYOFF_TEAMS == 26)
lo, hi = R.DRAFT_PICKS["playoff_teams"]
check("playoff picks = 14", hi - lo + 1 == R.PLAYOFF_TEAMS)

# Owner accountability
# Facts the Commissioner confirmed, written down independently of the formulas in rules.py
check("8 divisions in total", R.TOTAL_DIVISIONS == 8 and R.DIVISIONS_PER_CONFERENCE * len(R.CONFERENCES) == 8)
check("recall cycle is 8 years (1 division league-wide per year)",
      R.RECALL_DIVISIONS_PER_YEAR == 1 and R.RECALL_CYCLE_YEARS == 8)
check("lottery is 8 teams", R.LOTTERY_TEAMS == 8 and len(R.LOTTERY_WEIGHTS) == 8)
check("lottery draws no more teams than there are exiles", R.LOTTERY_TEAMS == R.EXILED_TEAMS)
check("every rule carries a rulebook basis (skeleton, nfl, adapted, fair or model)",
      all(v in (R.SKELETON, R.NFL, R.ADAPTED, R.FAIR, R.MODEL) for v in R.BASIS.values()))
check("lottery balls and lottery pool are the Commissioner's own rules (skeleton)",
      R.BASIS["Lottery balls: best record of the eight holds 1 ball, next best 2, ... worst 8 (36 balls)"] == R.SKELETON
      and R.BASIS["Which 8 teams are in the lottery (the teams that just finished 5th)"] == R.SKELETON)
check("tiebreakers mirror the NFL; the adaptations are labelled adapted",
      R.TIEBREAK_STYLE == "nfl" and R.BASIS["Tiebreakers mirror the NFL"] == R.NFL
      and R.BASIS["NFL tiebreak adaptations (restart rule used to rank everyone, wild-card division reduction, Ambassador chain, estimated touchdowns)"] == R.ADAPTED)
check("ties are an NFL rule now: no entry says games are never tied",
      not any("No tied games" in k for k in R.BASIS) and R.TIES_ALLOWED)
check("forced-sale vote is a majority of 48", R.FORCED_SALE_VOTES_NEEDED > R.TOTAL_TEAMS // 2)
check("season is 23 game weeks", R.GAME_WEEKS_TOTAL == 23)

print()
if failures:
    print(f"{len(failures)} check(s) FAILED")
    sys.exit(1)
print("All Phase 0 checks passed.")
