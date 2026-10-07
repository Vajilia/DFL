"""Checks for pay and the salary cap: the Commissioner's rules ($100M cap that never inflates, banking up to $125M, anything above forfeited to the pool,
a payroll floor of about 90%, the 50% absorption for an exiled team) and the contracts that make them bite.

    python engine/check_economy.py
"""
import os
import random
import statistics as st
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import economy as EC  # noqa: E402
import fingerprint as FP  # noqa: E402
import store  # noqa: E402
from league import new_league  # noqa: E402
from positions import POSITIONS, ROSTER_SIZE  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


def opt():
    return Options(engine="fast", keep_boxes=False)


# ---- the rules, one at a time, on a league where every payroll is set by hand -----------------------------------------------------------------
def fresh():
    lg = new_league(random.Random(2), rosters=True)
    return lg


def set_payroll(t, total):
    """Everyone under contract counts, so the practice squad's wage comes off first and the roster shares the rest."""
    ps = sum(p.salary for p in t.practice_squad)
    for p in t.roster:
        p.salary = (total - ps) / len(t.roster)


lg = fresh()
check("the cap is $100 million, the most a team may go into a season with is $125 million, the floor is 90% of the cap", EC.CAP == 100.0 and EC.BANK_LIMIT == 125.0 and EC.floor() == 90.0)
check("a new league has every team inside the cap and above the floor", all(EC.floor() - 0.5 <= EC.payroll(t) <= EC.CAP for t in lg.teams) and all(t.bank == 0 for t in lg.teams),
      f"payrolls {min(EC.payroll(t) for t in lg.teams):.1f} to {max(EC.payroll(t) for t in lg.teams):.1f}")
a, b, c, d, e = lg.teams[:5]
for t in lg.teams:
    set_payroll(t, 95.0)
set_payroll(a, 90.0)                      # spends the floor and no more: banks the room
b.bank = 25.0
set_payroll(b, 90.0)                      # already at the $125M limit and underspends: the excess is forfeited
set_payroll(c, 70.0)                      # far under the floor: it banks only its real unused room (the floor is tested over four seasons, below)
set_payroll(d, 100.0)                     # spends everything: banks nothing
e.bank = 10.0
set_payroll(e, 108.0)                     # spent some of its banked room: nothing left to bank
f = lg.teams[5]
set_payroll(f, 96.0)                      # an exiled team coming back: half its payroll was absorbed
rec = EC.close_season(lg, [f.id], 1)
check("unused room is banked for next season: $10M unspent means a $110M limit", a.bank == 10.0 and EC.limit(a) == 110.0)
check("but $125M is the most a team can go into a season with: $35M unspent at a $125M limit banks $25M and the other $10M is forfeited", b.bank == 25.0 and EC.limit(b) == 125.0)
check("a team far below the floor banks only its real unused room ($30M unused: $25M banked, $5M forfeited); one season alone never triggers the floor", c.bank == 25.0 and rec["shortfall"] == 0.0, f"banked {c.bank}, shortfall {rec['shortfall']}")
check("a team that spends all of its room banks nothing, and one that spent part of its banked room has no room left", d.bank == 0.0 and abs(e.bank - 2.0) < 1e-9, f"spent-to-the-limit team banks {d.bank}, the team that spent $108M of a $110M limit banks {e.bank}")
check("an exiled team's payroll counts at half, the floor does not apply, and the league absorbs the other half", abs(rec["absorbed"] - 48.0) < 1e-9 and f.bank == 25.0, f"banked {f.bank}")
want_forfeit = 10.0 + 5.0 + (100.0 - 48.0 - 25.0)             # team b, team c, and the exiled team's room beyond $25M
check("forfeited room goes into the Equalization Fund as dollars, the league's half of the exiled payroll comes out, and a deficit is covered equally by all 48 teams",
      abs(rec["forfeited"] - want_forfeit) < 1e-6 and abs(rec["levy"] - (rec["absorbed"] - rec["forfeited"])) < 1e-6 and lg.pool == 0.0
      and all(abs(t.fund_cash + rec["levy"] / 48) < 1e-6 for t in lg.teams),
      f"forfeited {rec['forfeited']}, absorbed {rec['absorbed']}, levy {rec['levy']}")
check("nobody ever has a limit above $125M or below $100M", all(EC.CAP <= EC.limit(t) <= EC.BANK_LIMIT for t in lg.teams))

# ---- the pay scale -------------------------------------------------------------------------------------------------------------------------------------
check("pay rises with rating and a quarterback costs more than a kicker of the same rating", all(EC.market_salary("WR", x) <= EC.market_salary("WR", x + 1) for x in range(30, 94)) and EC.market_salary("QB", 80) > EC.market_salary("K", 80))
check("nobody costs less than the minimum or more than a quarter of the cap", EC.market_salary("QB", 100) == EC.MAX_SALARY == 25.0 and EC.market_salary("P", 20) == EC.MIN_SALARY)
check("the rookie scale falls with the pick (a fixed wage scale, not a negotiation)", all(EC.rookie_salary(k) >= EC.rookie_salary(k + 1) for k in range(1, 336)) and EC.rookie_salary(1) > 3 * EC.rookie_salary(48) - 1)

# ---- a long league obeys the cap every single season -------------------------------------------------------------------------------------------------
r = random.Random(33)
L = new_league(r, rosters=True)
bad, floor_n, banked, blocked, re_n, exp_n, pools = [], 0, [], 0, 0, 0, []
over_max = under_min = size_bad = lens_bad = 0
for y in range(1, 41):
    res = run_season(L, y, r, Options(engine="fast", keep_boxes=False))
    for t in L.teams:
        if EC.payroll(t) > EC.limit(t) + 1e-6:
            bad.append((y, t.id, EC.payroll(t), EC.limit(t)))
        size_bad += len(t.roster) != ROSTER_SIZE
        for p in t.roster:
            over_max += p.salary > EC.MAX_SALARY + 1e-9
            under_min += p.salary < EC.MIN_SALARY - 1e-9
            lens_bad += not (1 <= p.years_left <= 5)
    floor_n += sum(1 for t in L.teams if EC.payroll(t) < EC.floor())
    banked.append(sum(t.bank for t in L.teams) / 48)
check("no team ever has a payroll above its limit at the start of a season (40 seasons, 48 teams): the cap is a hard limit", not bad, f"{len(bad)} breaches")
check("every roster is full, every salary is between the minimum and a quarter of the cap, and every contract has one to five seasons left", size_bad == over_max == under_min == lens_bad == 0)
caps = [e for e in L.archive if e["event"] == "cap_close"]
check("the Archive records each season's accounts", len(caps) == 40 and all({"forfeited", "shortfall", "absorbed", "levy", "payout", "pool"} <= set(e) for e in caps))
check("the Fund's books add up: the balance is every forfeit less every absorbed payroll, plus levies, less payouts", abs(L.pool - sum(e["forfeited"] - e["absorbed"] + e["levy"] - e["payout"] for e in caps)) < 1.0, f"fund {L.pool:.0f}M")
check("the Fund pays out only above its reserve, and what teams were paid and charged matches the books", L.pool <= EC.FUND_RESERVE + 1e-6
      and abs(sum(t.fund_cash for t in L.teams) - sum(e["payout"] - e["levy"] for e in caps)) < 1.0, f"net team cash {sum(t.fund_cash for t in L.teams):.0f}M")
check("the cap matters: teams do bank room, teams do sometimes end below the floor, and room is not always full", 1.0 < st.mean(banked[10:]) < 24.9 and floor_n > 0, f"mean banked {st.mean(banked[10:]):.1f}M a team, {floor_n} team-seasons below the floor")
mean_pay = st.mean(e["payroll_mean"] for e in caps[10:])
check("teams spend most of the cap on average (the pay scale is calibrated so)", 92.0 <= mean_pay <= 100.0, f"mean payroll {mean_pay:.1f}M")
returners = [e for e in caps if e["absorbed"] > 0]
check("exiled teams' relief is absorbed by the league every season there is one", len(returners) > 30 and st.mean(e["absorbed"] for e in returners) > 30, f"{st.mean(e['absorbed'] for e in returners):.0f}M a season over {len(returners)} seasons")

# ---- contracts end, are re-signed or hit the market, and the cap can cost a team a player ------------------------------------------------------------------
Lc = new_league(random.Random(5), rosters=True)
rr = random.Random(5)
exp = res_n = blk = ent = cuts = 0
rate = []
for y in range(1, 21):
    rs = run_season(Lc, y, rr, Options(engine="fast", keep_boxes=False))
    lg_ = rs.offseason
    if lg_:
        exp += lg_["expired_roster"]; res_n += lg_["resigned"]; blk += lg_["cap_blocked"]; cuts += lg_["cap_cuts"]
share = exp / (20 * 48 * ROSTER_SIZE)     # the 53; the practice squad is on one-year wages and is not counted
check("about 15% of each roster reaches the market each year, as before the cap (stars stay more, a good negotiator keeps more)", 0.10 <= share <= 0.20 and exp > 0, f"{100 * share:.1f}% a year")
check("the cap does cost teams players: some expiring players are lost because the team has no room to re-sign them, and a team that spent banked room sheds contracts when its limit falls back", blk > 0 and cuts > 0 and res_n > 0, f"{res_n} re-signed, {blk} lost to the cap, {cuts} cut to get back under it, in 20 seasons")

# ---- determinism and the save --------------------------------------------------------------------------------------------------------------------------
def pays(seed, years):
    rg = random.Random(seed)
    lgx = new_league(rg, rosters=True)
    res_ = [run_season(lgx, y, rg, opt()) for y in range(1, years + 1)]
    return lgx, res_, rg


A, ra, rg = pays(7, 12)
B, rb, _ = pays(7, 12)
check("same seed, same payrolls, banks, pool and fingerprint", [(t.id, EC.payroll(t), t.bank) for t in A.teams] == [(t.id, EC.payroll(t), t.bank) for t in B.teams] and A.pool == B.pool and FP.fingerprint_of(A, ra) == FP.fingerprint_of(B, rb))
db = os.path.join(tempfile.mkdtemp(), "e.db")
store.save(db, A, rg, 12)
C, rc, y = store.load(db)
check("salaries, bonuses, guarantees, contract years, banked room, dead money, the four-season floor books and the Equalization Fund survive saving and loading",
      [(p.id, p.salary, p.years_left, p.bonus, p.bonus_years, p.guaranteed) for t in A.teams for p in t.roster] == [(p.id, p.salary, p.years_left, p.bonus, p.bonus_years, p.guaranteed) for t in C.teams for p in t.roster]
      and [(t.bank, t.dead_now, t.dead_next, t.designations, t.cash, t.topup, t.fund_cash) for t in A.teams] == [(t.bank, t.dead_now, t.dead_next, t.designations, t.cash, t.topup, t.fund_cash) for t in C.teams]
      and A.pool == C.pool)
ra2 = [run_season(A, y, rg, opt()) for y in range(13, 19)]
rc2 = [run_season(C, y, rc, opt()) for y in range(13, 19)]
check("a league saved at season 12 and loaded plays on exactly as if it had never stopped, cap and all (6 more seasons)", FP.fingerprint_of(A, ra + ra2) == FP.fingerprint_of(C, ra + rc2) and A.pool == C.pool)

print()
if failures:
    print(f"{len(failures)} economy check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All economy checks passed.")
