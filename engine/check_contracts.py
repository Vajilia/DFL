"""Checks for contracts and the cap (build step 5): signing bonuses spread over the contract, guarantees, dead money and the two post-draft
designations, the minimum scale by seasons, the 25% maximum, the 51 rule in the offseason, the floor over four seasons and the Equalization Fund.

    python engine/check_contracts.py
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import economy as EC  # noqa: E402
import rules as R  # noqa: E402
from league import new_league  # noqa: E402
from players import make_player  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


def player(pos="WR", ovr=70.0, age=26, seasons=3):
    p = make_player(random.Random(1), 9000 + int(ovr), pos, ovr, age, 0)
    p.years_in_league = seasons
    return p


# ---- the minimum scale and the maximum
check("the minimum salary rises with seasons: 0.29, 0.33, 0.36, 0.38 for 0 to 3, 0.40 for 4 to 6, 0.43 for 7 or more",
      [EC.min_salary(s) for s in (0, 1, 2, 3, 4, 5, 6, 7, 12)] == [0.29, 0.33, 0.36, 0.38, 0.40, 0.40, 0.40, 0.43, 0.43])
check("no one is priced below her rung of the minimum scale", all(EC.market_salary("P", 20, s) == EC.min_salary(s) for s in range(0, 10)))
check("no contract's yearly cap value is above a quarter of the cap ($25M), even if one is asked for more", EC.MAX_SALARY == 25.0 and EC.market_salary("QB", 100) == 25.0
      and (lambda p: (EC.sign(p, 40.0, 3), p.salary)[1])(player("QB", 90)) == 25.0)

# ---- a contract: bonus, base, guarantee
p = player("OL", 80)
EC.sign(p, 8.0, 4)
check("a veteran contract of 2 or more years and $1M or more carries a signing bonus spread over the whole contract",
      abs(p.bonus - 8.0 * EC.VETERAN_BONUS_SHARE) < 1e-6 and p.bonus_years == 4 and p.years_left == 4)
check("the first year of the base is guaranteed", abs(p.guaranteed - (8.0 - p.bonus)) < 1e-6)
q = player("OL", 50)
EC.sign(q, 0.5, 3)
r1 = player("OL", 50)
EC.sign(r1, 1.0, 1)
check("a veteran contract under $1M carries no bonus and nothing guaranteed; a one-year deal has no bonus to spread (its base is guaranteed)",
      q.bonus == 0 == q.guaranteed and r1.bonus == 0 and r1.bonus_years == 0 and abs(r1.guaranteed - 1.0) < 1e-9)
p5 = player("QB", 90)
EC.sign(p5, 20.0, 5)
check("a bonus is spread over at most five years and contracts run one to five years", p5.bonus_years == 5 and EC.CONTRACT_YEARS_MAX == 5
      and (lambda x: (EC.sign(x, 5.0, 9), x.years_left)[1])(player()) == 5)
rk = player("QB", 70, 22, 0)
EC.sign(rk, 4.4, EC.ROOKIE_YEARS, share=EC.ROOKIE_BONUS_SHARE[0], guarantee_years=EC.ROOKIE_YEARS, rookie=True)
check("a first-round rookie's whole contract is guaranteed", abs(EC.dead_charge(rk) - 4.4 * EC.ROOKIE_YEARS) < 1e-3, f"{EC.dead_charge(rk):.2f} of {4.4 * EC.ROOKIE_YEARS:.2f}")
late = player("WR", 45, 22, 0)
EC.sign(late, 0.3, EC.ROOKIE_YEARS, share=EC.ROOKIE_BONUS_SHARE[6], guarantee_years=0, rookie=True)
check("a late-round rookie has a small bonus and nothing else guaranteed", abs(EC.dead_charge(late) - 0.3 * EC.ROOKIE_BONUS_SHARE[6] * EC.ROOKIE_YEARS) < 1e-3)

# ---- each season of the contract is paid
x = player("OL", 80)
EC.sign(x, 8.0, 3)
b0, g0 = x.bonus, x.guaranteed
EC.run_down(x)
check("when a season is paid, a year of bonus is spread out and the base comes off what is guaranteed", x.years_left == 2 and x.bonus_years == 2 and x.guaranteed == 0.0 and x.bonus == b0 and g0 > 0)
EC.run_down(x)
EC.run_down(x)
check("when the contract ends nothing is owed", x.years_left == 0 and x.bonus_years == 0 and x.bonus == 0.0 and EC.dead_charge(x) == 0.0)

# ---- dead money
lg = new_league(random.Random(3), rosters=True)
t = lg.teams[0]
v = max(t.roster, key=lambda p: p.salary)
EC.sign(v, 9.0, 4)
dead = EC.dead_charge(v)
pay0 = EC.payroll(t)
t.roster.remove(v)
now = EC.release(t, v)
check("letting a player go takes her salary off the payroll and puts her unspent bonus and guaranteed pay on it as dead money, all this season",
      abs(now - dead) < 1e-6 and abs(t.dead_now - dead) < 1e-6 and t.dead_next == 0 and abs(EC.payroll(t) - (pay0 - 9.0 + dead)) < 1e-2 and v.salary == v.bonus == v.guaranteed == 0)
t2 = lg.teams[1]
w = max(t2.roster, key=lambda p: p.salary)
EC.sign(w, 9.0, 4)
dead2, bonus2 = EC.dead_charge(w), w.bonus
t2.roster.remove(w)
now2 = EC.release(t2, w, designate=True)
check("a post-draft designation puts only this year's bonus on this season's cap and the rest on next season's", abs(now2 - bonus2) < 1e-6 and abs(t2.dead_next - (dead2 - bonus2)) < 1e-6 and t2.designations == 1)
check("a team has two designations a year", EC.can_designate(t2) and (setattr(t2, "designations", 2) or not EC.can_designate(t2)) and EC.POST_DRAFT_DESIGNATIONS == 2)
EC.new_year(t2)
check("a new league year rolls what was pushed forward onto the cap and refreshes the designations", abs(t2.dead_now - (dead2 - bonus2)) < 1e-6 and t2.dead_next == 0 and t2.designations == 0)

# ---- the 51 rule
t3 = lg.teams[2]
allsal = sorted((p.salary for p in list(t3.roster) + list(t3.practice_squad)), reverse=True)
check("in the offseason only the 51 highest cap numbers count, plus dead money", abs(EC.offseason_payroll(t3) - sum(allsal[:51])) < 0.01
      and EC.offseason_payroll(t3) < EC.payroll(t3))
t3.dead_now = 2.0
check("dead money counts both in the offseason and in the season", abs(EC.offseason_payroll(t3) - (sum(allsal[:51]) + 2.0)) < 0.01 and abs(EC.payroll(t3) - (sum(allsal) + 2.0)) < 0.01)
t3.dead_now = 0.0

# ---- the floor over four seasons, and the Equalization Fund
lg = new_league(random.Random(4), rosters=True)
for tm in lg.teams:
    tm.dead_now = tm.dead_next = 0.0
    tm.cash, tm.topup, tm.fund_cash = [], [], 0.0
lg.pool = 0.0
under = lg.teams[0]


def set_pay(tm, total):
    ps = sum(p.salary for p in tm.practice_squad)
    for p in tm.roster:
        p.salary = (total - ps) / len(tm.roster)


for tm in lg.teams:
    set_pay(tm, 95.0)
set_pay(under, 80.0)
paid = []
for yr in range(1, 5):
    rec = EC.close_season(lg, [], yr)
    paid.append(rec["shortfall"])
    for tm in lg.teams:
        tm.bank = 0.0
check("the floor is tested over four seasons: a team 10M under the floor each year pays nothing for three seasons and then the 40M it fell short, to its own players",
      paid[:3] == [0.0, 0.0, 0.0] and abs(paid[3] - 40.0) < 1e-6, f"paid {paid}")
later = []
for yr in range(5, 9):
    later.append(EC.close_season(lg, [], yr)["shortfall"])
    for tm in lg.teams:
        tm.bank = 0.0
check("it is not charged twice for the same shortfall: the 40M it paid covers its window until it rolls out, then a team still under pays again (10M a year on average)",
      later[:3] == [0.0, 0.0, 0.0] and abs(later[3] - 40.0) < 1e-6, f"paid {later}")
set_pay(under, 95.0)
for yr in range(9, 13):
    rec = EC.close_season(lg, [], yr)
for tm in lg.teams:
    tm.bank = 0.0
check("once it spends at least the floor over the window it pays nothing", rec["shortfall"] == 0.0, f"{rec['shortfall']}")
ex = lg.teams[1]
ex_before = list(ex.cash)
rec = EC.close_season(lg, [ex.id], 13)
check("an exile season is skipped: it is not part of any team's four-season window", ex.cash == ex_before)

# the Fund's surplus is shared by the teams that played
lg2 = new_league(random.Random(6), rosters=True)
for tm in lg2.teams:
    tm.cash, tm.topup, tm.fund_cash, tm.dead_now, tm.dead_next = [], [], 0.0, 0.0, 0.0
    tm.bank = 25.0
    for p in tm.roster:
        p.salary = 1.0
    for p in tm.practice_squad:
        p.salary = 0.1
lg2.pool = 0.0
retd = [t.id for t in lg2.teams[:8]]
rec = EC.close_season(lg2, retd, 1)
playing = [t for t in lg2.teams if t.id not in retd]
check("what the Fund holds above its reserve is paid equally to the 40 teams that played, and the Fund keeps its reserve",
      rec["payout"] > 0 and abs(lg2.pool - EC.FUND_RESERVE) < 1e-6 and len(playing) == EC.EQUALIZATION_SURPLUS_TEAMS
      and len({round(t.fund_cash, 6) for t in playing}) == 1 and all(t.fund_cash == 0 for t in lg2.teams if t.id in retd) and abs(playing[0].fund_cash * 40 - rec["payout"]) < 1e-4,
      f"{rec['payout']:.0f}M, {playing[0].fund_cash:.2f}M each")

# ---- a league that plays: the rules hold every season
rg = random.Random(9)
L = new_league(rg, rosters=True)
dead, des, emerg, bad_bonus, bad_guar, over_max, years_bad = [], 0, 0, 0, 0, 0, 0
for y in range(1, 21):
    res = run_season(L, y, rg, Options(engine="fast", keep_boxes=False))
    dead.append(sum(t.dead_now for t in L.teams) / 48)
    des += res.offseason.get("designated", 0)
    emerg += res.offseason.get("emergency", 0)
    for tm in L.teams:
        for p in tm.roster:
            bad_bonus += not (0 <= p.bonus <= p.salary + 1e-9 and 0 <= p.bonus_years <= EC.BONUS_PRORATION_MAX_YEARS and p.bonus_years <= p.years_left)
            bad_guar += p.guaranteed < -1e-9
            over_max += p.salary > EC.MAX_SALARY + 1e-9 or p.salary < EC.min_salary(0) - 1e-9
            years_bad += not (1 <= p.years_left <= EC.CONTRACT_YEARS_MAX)
check("every contract in a 20-season league is sound: bonus within salary and within five years of the contract, nothing guaranteed below zero, salary between the minimum and the maximum, one to five years left",
      bad_bonus == bad_guar == over_max == years_bad == 0, f"{bad_bonus} {bad_guar} {over_max} {years_bad}")
check("dead money is a real, steady part of the cap (not zero, not a runaway)", 0.5 < sum(dead[5:]) / len(dead[5:]) < 15.0 and max(dead) < 25.0, f"mean {sum(dead[5:]) / len(dead[5:]):.1f}M a team, peak {max(dead):.1f}M")
check("teams do use their post-draft designations", des > 20, f"{des} in 20 seasons")
check("a team that has used its designations and still cannot get under the cap is rare (the league lets it defer the dead money)", emerg <= 20, f"{emerg} in 20 seasons of 48 teams")
check("every team is inside its cap after every offseason", all(EC.payroll(t) <= EC.limit(t) + 1e-6 for t in L.teams))

print()
if failures:
    print(f"{len(failures)} contract check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All contract checks passed.")
