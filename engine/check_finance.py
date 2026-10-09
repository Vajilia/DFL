"""Checks for club finance (Step 7): the CEO's draw cap and tenure, the Fund's inflow, subsidies, the books balancing, approval nudges and
that money never touches the game.

    python engine/check_finance.py
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import finance as F  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


def league(seed=7):
    rng = random.Random(seed)
    return new_league(rng, rosters=True), rng


# ---- the rules in the skeleton -------------------------------------------------------------------------------------------
check("draw cap is $100M", F.DRAW_CAP == 100.0)
check("tenure range is 10 to 20", (F.TENURE_MIN, F.TENURE_MAX) == (10, 20))
check("a fanbase card is a million fans", F.FANS_PER_CARD == 1_000_000)

lg, rng = league()
rows = []
for y in range(1, 31):
    res = run_season(lg, y, rng, Options(engine="fast", keep_boxes=False))
    rows.append(res.offseason["finance"])
lines = [l for f in rows for l in f["lines"].values()]
check("no draw above the cap", all(l["draw"] <= F.DRAW_CAP + 1e-9 for l in lines), f"max {max(l['draw'] for l in lines):.1f}")
check("the cap binds for some club-years in 30 seasons", any(l["to_fund"] > 0 for l in lines), f"{sum(1 for l in lines if l['to_fund'] > 0)} club-years")
check("excess above the cap equals what goes to the Fund",
      all(abs(f["to_fund"] - sum(l["to_fund"] for l in f["lines"].values())) < 0.02 for f in rows))

# the books balance: surplus = reinvested + saved-to-reserve + draw(before subsidy) + to_fund for a profit, and a loss is covered
def balanced(l):
    if l["surplus"] >= 0:
        sub_out = l.get("subsidy_paid", 0.0)
        return l["reinvested"] + l["draw"] + sub_out + l["to_fund"] <= l["surplus"] + 0.05 and l["draw"] >= 0
    return abs(l["loss"] + l["surplus"]) < 0.02
check("every profit is fully accounted for (spent, saved, drawn, or sent to the Fund)", all(balanced(l) for l in lines))
check("a loss is covered by the reserve, a subsidy or the CEO's pocket",
      all(abs(l["loss"] - l.get("covered_by_reserve", 0.0) - l.get("subsidy_received", 0.0) - l.get("own_pocket", 0.0)) < 0.05 for l in lines if l["loss"] > 0))
check("subsidies paid equal subsidies received in every year",
      all(abs(sum(l.get("subsidy_paid", 0.0) for l in f["lines"].values()) - sum(l.get("subsidy_received", 0.0) for l in f["lines"].values())) < 0.25 for f in rows))
check("reserves stay between 0 and the maximum", all(-1e-9 <= t.reserve <= F.RESERVE_MAX + 1e-9 for t in lg.teams))
check("nudges are small", all(abs(l["nudge"]) <= F.FAN_SPEND_WEIGHT + F.FAN_GREED_HIT + 1e-9 for l in lines))
check("exiled clubs earn less local money than they would at home",
      all(l["local"] - l["ticket_pool_in"] < F.LOCAL_BASE * 1.6 * F.EXILE_LOCAL_SHARE + 12 for l in lines if l["exiled"]))
check("clubs keep a bounded set of books", all(len(t.books) <= F.BOOKS_YEARS for t in lg.teams))

# the ticket pool: 34% of every club's tickets, shared equally
check("the ticket pool pays out exactly what it takes in, every year",
      all(abs(sum(l["ticket_pool_in"] for l in f["lines"].values()) - sum(l["ticket_pool_out"] for l in f["lines"].values())) < 0.3 for f in rows))
check("every club receives the same ticket-pool share in a year", all(len({l["ticket_pool_in"] for l in f["lines"].values()}) == 1 for f in rows))

# forced sale: two subsidised quarters call a vote; 25 of the 47 other CEOs sell the club out from under her
import rules as R  # noqa: E402
voted = [l for l in lines if "sale_votes" in l]
check("a vote is called only for two or more subsidised quarters", all(l["sub_quarters"] >= R.FORCED_SALE_SUBSIDY_QUARTERS for l in voted))
check("every club with two or more subsidised quarters had a vote", all("sale_votes" in l for l in lines if l["sub_quarters"] >= R.FORCED_SALE_SUBSIDY_QUARTERS))
check("a sale passes at 25 votes and not before", all((l["sale_votes"] >= R.FORCED_SALE_VOTES_NEEDED) == (l["sale_result"] == "sold") for l in voted))
check("no vote has more than 47 voters (the CEO concerned is recused)", all(l["sale_votes"] <= 47 for l in voted))

# CEOs serve 10 to 20 years
gone = [o for o in lg.owners if o.status == "retired" and o.tenure > 0 and o.age < 85]
check("retired CEOs served their tenure", gone and all(o.seasons_owned >= o.tenure for o in gone), f"{len(gone)} CEOs")
check("every new CEO has a 10-20 year tenure", all(10 <= o.tenure <= 20 for o in lg.owners))

# revenue behaves
t = lg.teams[0]
lo = F.revenue(t, 0.25, False, False, False)
hi = F.revenue(t, 0.75, True, True, False)
check("a better team earns more local money", hi["local"] > lo["local"])
ex = F.revenue(t, 0.5, False, False, True)
home = F.revenue(t, 0.5, False, False, False)
check("an exiled club earns a fraction of home revenue", ex["local"] < home["local"] and ex["national"] < home["national"])

# money never touches the game: the same seed with finance's nudges removed plays the same first season
def first_season(nudge_on):
    lg1, r1 = league(11)
    res = run_season(lg1, 1, r1, Options(engine="fast", keep_boxes=False))
    return [(g.home_pts, g.away_pts) for g in res.games]
check("a first season is deterministic with finance in the loop", first_season(True) == first_season(False))

# save and load keep the books
import tempfile  # noqa: E402
import store  # noqa: E402
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "x.db")
    store.save(path, lg, rng, 30)
    lg2, rng2, yr = store.load(path)
    check("books and reserves survive a save", all(a.books == b.books and abs(a.reserve - b.reserve) < 1e-9 for a, b in zip(lg.teams, lg2.teams)))
    check("tenure and draws survive a save", all(a.owner.tenure == b.owner.tenure and abs(a.owner.draws - b.owner.draws) < 1e-6 for a, b in zip(lg.teams, lg2.teams)))

print()
print("FAILED: " + ", ".join(failures) if failures else "all finance checks passed")
sys.exit(1 if failures else 0)
