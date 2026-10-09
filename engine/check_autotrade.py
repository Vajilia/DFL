"""Autopilot trades (autotrade.py): a trade market of veterans for picks and pick swaps, priced on a draft-value chart, always legal, and subject to the
Commissioner's reject-only review.

    python engine/check_autotrade.py
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import autotrade as A  # noqa: E402
import governance as GV  # noqa: E402
import rules as R  # noqa: E402
import transactions as T  # noqa: E402
from league import new_league  # noqa: E402
from roster_model import RosterModel  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


# ---- the chart ---------------------------------------------------------------------------------------------------------------
pts = [A.pick_points(n) for n in range(1, 337)]
check("the first pick is worth 3000 points", abs(pts[0] - 3000) < 1e-6)
check("picks lose value all the way down the board", all(a > b for a, b in zip(pts, pts[1:])))
check("the chart has the NFL's shape (pick 1 is worth 5 to 12 times pick 48, and a last-round pick is under 3% of pick 1)",
      5 < pts[0] / pts[47] < 12 and pts[335] < 0.03 * pts[0], f"pick 48 = {pts[47]:.0f}, pick 336 = {pts[335]:.0f}")
rm = RosterModel()
r = random.Random(3)
lg = new_league(r, rosters=True)
p = max((q for t in lg.teams for q in t.roster), key=lambda q: q.ovr)
check("a star is worth a high pick, a backup nothing", A.player_points(p, rm) > 800, f"{p.ovr:.0f} rated = {A.player_points(p, rm):.0f}")
low = min((q for t in lg.teams for q in t.roster), key=lambda q: q.ovr)
check("a player below the threshold is worth nothing", A.player_points(low, rm) == 0.0)
old = max((q for t in lg.teams for q in t.roster if q.age >= 31), key=lambda q: q.ovr, default=None)
young_pts = A.player_points(p, rm)
p.age += 6
check("age lowers a player's value", A.player_points(p, rm) < young_pts)
p.age -= 6

# ---- pricing ---------------------------------------------------------------------------------------------------------------
lg.movement.ensure_picks(lg, 1)
mine = A._free_picks(lg, 5, (1, 2))
check("a club's free picks are the picks it owns in the two coming drafts", len(mine) == 2 * R.DRAFT_ROUNDS and all(pk.owner == 5 for pk in mine))
for target in (60.0, 150.0, 400.0):
    got = A._price(mine, target)
    tot = sum(A.pick_value(k) for k in got) if got else None
    check(f"a price of {target:.0f} points is paid within the fair range", got is None or A.FAIR_LOW * target - 1e-9 <= tot <= A.FAIR_HIGH * target + 1e-9, f"{tot}")

# ---- seasons -----------------------------------------------------------------------------------------------------------------
for engine in ("fast", "drives"):
    r = random.Random(7)
    L = new_league(r, rosters=True)
    off_n, in_n, per = 0, 0, []
    for y in range(1, 5 if engine == "fast" else 3):
        s = run_season(L, y, r, Options(engine=engine, keep_boxes=False))
        off, ins = s.offseason.get("trades", []), s.runner.trade_log
        off_n += len(off)
        in_n += len(ins)
        per.append(len(off) + len(ins))
        for tr in off + ins:
            a, b = tr["clubs"]
            if a == b:
                check(f"[{engine}] a club traded with itself", False)
        check(f"[{engine}] year {y}: every in-season trade came before the deadline", all(t["week"] is None or t["week"] <= R.TRADE_DEADLINE_WEEK for t in ins))
    years = len(per)
    check(f"[{engine}] the market is active but not wild (15 to 100 trades a year)", all(15 <= n <= 100 for n in per), f"{per}")
    check(f"[{engine}] most trades are in the offseason", off_n > in_n, f"{off_n} offseason, {in_n} in season")
    ev = [e for e in L.movement.events if e.get("kind") == "trade"]
    check(f"[{engine}] every trade is in the ledger of events", len(ev) >= off_n + in_n - 1, f"{len(ev)} events")
    check(f"[{engine}] rosters are full after the trades", all(len(t.roster) == R.ROSTER_LIMIT for t in L.teams))
    check(f"[{engine}] no club is left without a kicker or a punter", all(any(q.pos == "K" for q in t.roster) and any(q.pos == "P" for q in t.roster) for t in L.teams))

# ---- the Commissioner can reject, never improve -----------------------------------------------------------------------------
r = random.Random(11)
L = new_league(r, rosters=True)
L.movement.ensure_picks(L, 1)
orig = GV.review_trade
GV.review_trade = lambda *a, **k: GV.reject("trade", 1.0, "test")
none = A.window(L, r, RosterModel(), 1, None, 1.0, 0.5, 1, rounds=2)
GV.review_trade = orig
check("when the Commissioner rejects every trade, none is made", none == [])
some = A.window(L, r, RosterModel(), 1, None, 1.0, 0.5, 1, rounds=2)
check("with no rejection the same market makes trades", len(some) > 0, f"{len(some)}")
ex = L.teams[3]
ex.status = "exiled"
more = A.window(L, r, RosterModel(), 1, None, 1.0, 0.5, 1, rounds=2)
check("an exiled club does not trade", all(ex.id not in t["clubs"] for t in more))

print()
if failures:
    print(f"{len(failures)} autotrade check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All autotrade checks passed.")
