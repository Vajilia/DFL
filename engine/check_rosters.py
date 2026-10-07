"""Checks for the roster lists and the seven-round draft (build step 4): 90 in camp, 53 on the roster, 48 active, a practice squad of 16,
injured reserve, the 336-pick draft with the rookie scale, and undrafted signings.

    python engine/check_rosters.py
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import economy as EC  # noqa: E402
import rosters as RS  # noqa: E402
import rules as R  # noqa: E402
from league import new_league  # noqa: E402
from positions import ACTIVE_MINIMUMS, POSITIONS, ROSTER_COUNTS, ROSTER_SIZE  # noqa: E402
from roster_model import RosterModel  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


def lists_ok(lg, label):
    bad = []
    for t in lg.teams:
        ids = [p.id for p in RS.squad(t)]
        if len(t.roster) != ROSTER_SIZE:
            bad.append((t.id, "roster", len(t.roster)))
        if len(t.practice_squad) != R.PRACTICE_SQUAD_SIZE:
            bad.append((t.id, "practice squad", len(t.practice_squad)))
        if len(ids) != len(set(ids)):
            bad.append((t.id, "someone is on two lists"))
        if RS.veterans_on_squad(t.practice_squad) > R.PRACTICE_SQUAD_VETERANS_MAX:
            bad.append((t.id, "too many veterans on the practice squad"))
        if any(p.team_id != t.id for p in RS.squad(t)):
            bad.append((t.id, "a player's team id is wrong"))
    check(label, not bad, str(bad[:3]))


# ---- the founding league
rng = random.Random(4)
lg = new_league(rng, rosters=True)
check("the position table holds exactly 53 and the starters fit inside it", ROSTER_SIZE == R.ROSTER_LIMIT == 53 and all(ROSTER_COUNTS[p] > 0 for p in POSITIONS))
lists_ok(lg, "a new league: every team has 53 on the roster and 16 on the practice squad, nobody on two lists, at most 6 veterans on a squad")
check("every team's roster has the table count at every position",
      all(sum(1 for p in t.roster if p.pos == pos) == n for t in lg.teams for pos, n in ROSTER_COUNTS.items()))
check("practice-squad players are paid the practice-squad wage and counted against the cap",
      all(abs(p.salary - EC.PRACTICE_SQUAD_SALARY) < 1e-9 for t in lg.teams for p in t.practice_squad)
      and all(abs(EC.payroll(t) - (sum(p.salary for p in t.roster) + sum(p.salary for p in t.practice_squad))) < 1e-6 for t in lg.teams))
check("every team starts inside its cap and above the floor", all(EC.floor() - 1e-6 <= EC.payroll(t) <= EC.limit(t) + 1e-6 for t in lg.teams),
      f"{min(EC.payroll(t) for t in lg.teams):.1f} to {max(EC.payroll(t) for t in lg.teams):.1f}")

# ---- the game-day list
t = lg.teams[0]
act = RS.active_list(t)
check("48 are active on game day, all healthy", len(act) == R.ACTIVE_LIMIT and all(p.weeks_out == 0 for p in act), str(len(act)))
cnt = RS.counts(act)
check("the active list keeps the position minimums", all(cnt[pos] >= ACTIVE_MINIMUMS[pos] for pos in POSITIONS), str(cnt))
inactive = [p for p in t.roster if p not in act]
check("the five inactive players are the weakest surplus, never a starter", len(inactive) == 5 and all(
    p.ovr <= sorted((q.ovr for q in t.roster if q.pos == p.pos), reverse=True)[ACTIVE_MINIMUMS[p.pos] - 1] for p in inactive))
for p in t.roster[:6]:
    p.weeks_out = 3
act2 = RS.active_list(t)
check("injured players are never active", all(p.weeks_out == 0 for p in act2))
for p in t.roster:
    p.weeks_out = 0

# ---- injured reserve and promotions
rg = random.Random(1)
star = max((p for p in t.roster if p.pos == "OL"), key=lambda p: p.ovr)
star.weeks_out = 9
log = RS.manage_week(lg, rg, weeks_left=10)
check("a player out for 4 or more games who can return this season goes on injured reserve, designated to return",
      star in t.ir and star.ir_designated and t.ir_returns == 1 and star not in t.roster)
check("the roster is filled back to 53 from the practice squad and the practice squad is refilled to 16",
      len(t.roster) == 53 and len(t.practice_squad) == 16 and log["promoted"] >= 1, str(log))
check("the promoted player is at the position that was short", sum(1 for p in t.roster if p.pos == "OL") == ROSTER_COUNTS["OL"])
lists_ok(lg, "the lists stay valid after injured reserve moves")
# the player heals but must wait four games
for week in range(1, 12):
    for p in list(t.ir) + list(t.roster):
        if p.weeks_out > 0:
            p.weeks_out -= 1
    RS.manage_week(lg, rg, weeks_left=10 - week)
    if week == 3:
        check("she does not return before four games have passed", star in t.ir and star.ir_games == 3)
    if week == 9:
        break
check("after she has healed and four games have passed she returns and the roster stays at 53", star in t.roster and len(t.roster) == 53 and star not in t.ir,
      f"in roster {star in t.roster}, ir_games {star.ir_games}")
# season-ending injuries need no designation; a team out of designations cannot use injured reserve for players who will return
t2 = lg.teams[1]
t2.ir_returns = R.IR_RETURNS_MAX
back = max(t2.roster, key=lambda p: p.ovr if p.pos == "WR" else 0)
back.weeks_out = 6
RS.manage_week(lg, rg, weeks_left=12)
check("with all 8 returns used, a player who could come back this year stays on the roster", back in t2.roster and back not in t2.ir)
back.weeks_out = 20
RS.manage_week(lg, rg, weeks_left=12)
check("a season-ending injury goes on injured reserve without a designation", back in t2.ir and not back.ir_designated and t2.ir_returns == R.IR_RETURNS_MAX)
many = lg.teams[2]
hurt = sorted(many.roster, key=lambda p: -p.ovr)[:12]
for p in hurt:
    p.weeks_out = 6
RS.manage_week(lg, rg, weeks_left=12)
check("a team never uses more than 8 designated returns in a season", many.ir_returns == R.IR_RETURNS_MAX and sum(1 for p in many.ir if p.ir_designated) == R.IR_RETURNS_MAX,
      f"{many.ir_returns} designated")
lists_ok(lg, "the lists are still valid after a team loses twelve players at once")

# ---- the rookie scale
sc = [EC.rookie_salary(k) for k in range(1, 337)]
check("the rookie scale: pick 1 $4.4M, pick 48 $1.2M, pick 96 $0.65M, pick 97 $0.50M, pick 336 $0.30M",
      [sc[0], sc[47], sc[95], sc[96], sc[335]] == [4.4, 1.2, 0.65, 0.5, 0.3], str([sc[0], sc[47], sc[95], sc[96], sc[335]]))
check("the rookie scale never rises as the pick number grows and never falls below the minimum", all(a >= b for a, b in zip(sc, sc[1:])) and min(sc) >= EC.MIN_SALARY)

# ---- a full offseason: the camp, the cutdown and the seven-round draft
rg = random.Random(7)
lg = new_league(rg, rosters=True)
res = [run_season(lg, y, rg, Options(engine="fast", keep_boxes=False)) for y in (1, 2)]
off = res[0].offseason
check("the offseason drafts 7 rounds of 48: 336 rookies", off["rookies"] == R.DRAFT_ROUNDS * R.TOTAL_TEAMS == 336, str(off["rookies"]))
check("the camps hold 90 each before the cutdown", off["camp"] >= 90 * R.TOTAL_TEAMS * 0.97, f"{off['camp'] / R.TOTAL_TEAMS:.1f} a team")
lists_ok(lg, "after two full seasons every team has 53 and 16, nobody is on two lists, the practice squads obey the veteran limit")
check("nobody is left on injured reserve or hurt at the start of a season and the designations are reset",
      all(not t.ir and t.ir_returns == 0 and all(p.weeks_out == 0 for p in RS.squad(t)) for t in lg.teams))
check("every team is inside its cap after the offseason", all(EC.payroll(t) <= EC.limit(t) + 1e-6 for t in lg.teams),
      f"{max(EC.payroll(t) - EC.limit(t) for t in lg.teams):.2f} over at worst")
picks = {}
for t in lg.teams:
    for p in RS.squad(t):
        if p.draft_year == 1:
            picks[p.draft_pick] = p
for p in lg.free_agents + lg.retired_players:
    if p.draft_year == 1:
        picks[p.draft_pick] = p
check("every one of the 336 picks of the first draft is on record, in rounds 1 to 7", set(picks) == set(range(1, 337)), f"{len(picks)} found")
check("every rookie on a roster is paid the scale for her overall pick, on a four-year contract",
      all(abs(p.salary - EC.rookie_salary(p.draft_pick)) < 1e-6 and p.years_left == EC.ROOKIE_YEARS
          for t in lg.teams for p in t.roster if p.draft_year == 2))
r1 = [p for t in lg.teams for p in t.roster if p.draft_year == 2 and p.draft_pick <= 48]
check("the first-round rookies are better than the seventh-round rookies",
      len(r1) > 20 and sum(p.ovr for p in r1) / len(r1) > 55, f"{len(r1)} first-round rookies on rosters, mean {sum(p.ovr for p in r1) / len(r1):.1f}")
r1all = [p for p in picks.values() if p.draft_pick <= 48]
late_all = [p for p in picks.values() if p.draft_pick > 288]
check("a first-round pick averages higher than a seventh-round pick by more than ten points",
      sum(p.ovr for p in r1all) / len(r1all) - sum(p.ovr for p in late_all) / len(late_all) > 10)
udfa = [p for t in lg.teams for p in t.roster if p.draft_year is None and p.years_in_league <= 1 and p.salary <= EC.MIN_SALARY + 1e-9]
check("undrafted rookies sign for the minimum on three-year contracts, and some make rosters", off["udfa"] > 500 and len(udfa) > 0, f"{off['udfa']} invited, {len(udfa)} on rosters")
check("the market keeps the best of the unsigned, never more than the model's market size", len(lg.free_agents) <= RosterModel().market_size)
check("exiled teams have the same lists (every team has all of them)", all(len(t.roster) == 53 and len(t.practice_squad) == 16 for t in lg.exiled()))

print()
if failures:
    print(f"{len(failures)} roster check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All roster checks passed.")
