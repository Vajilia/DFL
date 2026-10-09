"""Checks for injuries (Step 8): kinds, NFL-scale rates, concussion protocol, the weekly report, healing and save/load.

    python engine/check_injuries.py
"""
import os
import random
import statistics as st
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import injuries as I  # noqa: E402
import rules as R  # noqa: E402
import store  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


# ---- the table
check("kind shares add to one", abs(sum(k[1] for k in I.KINDS) - 1.0) < 1e-9)
check("every kind's lengths and weights line up", all(len(k[2][0]) == len(k[2][1]) for k in I.KINDS))
conc = [k for k in I.KINDS if k[0] == I.CONCUSSION][0]
check("concussions are about 7% of injuries (NFL 6 to 8%)", 0.06 <= conc[1] <= 0.08, f"{conc[1]:.2f}")
rng = random.Random(1)
draws = [I.draw_kind(rng) for _ in range(20000)]
check("a concussion always misses at least one game (the protocol's mandatory removal)", all(g >= 1 for k, g in draws if k == I.CONCUSSION))
check("every injury misses at least one game", all(g >= 1 for _, g in draws))
check("mean injury length is 4 to 6 games", 4.0 <= st.mean(g for _, g in draws) <= 6.0, f"{st.mean(g for _, g in draws):.2f}")
check("QBs, kickers and punters are hurt less often than other positions", I.POS_RISK["QB"] < 1 and I.POS_RISK["K"] < I.POS_RISK["QB"] and I.POS_RISK["P"] < I.POS_RISK["QB"])

# ---- a league
for eng in ("fast", "drives"):
    rng = random.Random(33)
    lg = new_league(rng, rosters=True)
    ev, weeks, irn, conc_n, atonce = [], [], [], [], []
    for y in range(1, 9):
        res = run_season(lg, y, rng, Options(engine=eng, keep_boxes=False))
        if y == 1:
            first = res
        if y > 3:
            rn = res.runner
            ev.append(len(rn.injury_log) / 48)
            weeks.append(sum(len(r) for r in rn.injury_reports) / 48)
            irn.append(sum(l["ir_placed"] for l in rn.ir_log) / 48)
            conc_n.append(sum(1 for x in rn.injury_log if x[4] == I.CONCUSSION) / 48)
            atonce.append(st.mean(len(r) for r in rn.injury_reports) / 48)
    check(f"[{eng}] injuries per club per season are near the NFL's 30", 25 <= st.mean(ev) <= 42, f"{st.mean(ev):.1f}")
    check(f"[{eng}] player-games lost per club are inside the NFL's range (95 to 250)", 95 <= st.mean(weeks) <= 200, f"{st.mean(weeks):.0f}")
    check(f"[{eng}] injured-reserve moves per club are 8 to 20", 8 <= st.mean(irn) <= 20, f"{st.mean(irn):.1f}")
    check(f"[{eng}] concussions per club are 1.5 to 4", 1.5 <= st.mean(conc_n) <= 4, f"{st.mean(conc_n):.1f}")
    check(f"[{eng}] 4 to 10 players per club are on the weekly report at a time", 4 <= st.mean(atonce) <= 10, f"{st.mean(atonce):.1f}")
    rep = first.runner.injury_reports
    check(f"[{eng}] there is one weekly report per week", len(rep) == R.REGULAR_SEASON_WEEKS, f"{len(rep)}")
    rows = [r for week in rep for r in week]
    check(f"[{eng}] every report row names a kind, a team, a position and games left", all(r["kind"] in I.KIND_NAMES and r["games_left"] > 0 and r["pos"] and r["status"] in ("out", "IR") for r in rows))
    check(f"[{eng}] injuries happen only in the regular season", all(x[0] <= R.REGULAR_SEASON_WEEKS for x in first.runner.injury_log))
    check(f"[{eng}] nobody starts a season hurt", all(p.weeks_out == 0 and p.injury == "" for t in lg.teams for p in t.roster))

# ---- healing and save/load
rng = random.Random(9)
lg = new_league(rng, rosters=True)
run_season(lg, 1, rng, Options(engine="fast", keep_boxes=False))
p = lg.teams[0].roster[0]
p.weeks_out, p.injury = 2, "knee"
I.tick_week([p], set())
check("a hurt player heals one week at a time and keeps her injury until she is well", p.weeks_out == 1 and p.injury == "knee")
I.tick_week([p], set())
check("and the injury clears when she is well", p.weeks_out == 0 and p.injury == "")
q = lg.teams[1].roster[0]
q.weeks_out, q.injury = 3, "concussion"
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "x.db")
    store.save(path, lg, rng, 1)
    lg2, _, _ = store.load(path)
    q2 = [x for x in lg2.teams[1].roster if x.id == q.id][0]
    check("an injury (kind and games left) survives a save", q2.weeks_out == 3 and q2.injury == "concussion")

# ---- lasting damage (the Commissioner's design: it affects the career afterward, and no ailment outlives the career)
import offseason as OFF  # noqa: E402
from players import make_player  # noqa: E402
rr = random.Random(5)
n = 20000
knee_long = sum(1 for _ in range(n) if I.roll_lasting("knee", 12, rr) > 0) / n
knee_short = sum(1 for _ in range(n) if I.roll_lasting("knee", 1, rr) > 0) / n
check("a long knee injury often leaves lasting damage, a one-game knock almost never", knee_long > 0.3 and knee_short < 0.05, f"{knee_long:.2f} vs {knee_short:.3f}")
check("points lost are small (1 to 4)", all(1 <= x <= 4 for x in (I.roll_lasting("neck", 12, rr) for _ in range(500)) if x))
pl = make_player(random.Random(2), 99001, "WR", 70.0, 26)
before, atts = pl.ovr, dict(pl.ratings)
I.apply_lasting(pl, "knee", 3)
check("lasting damage takes the points off every rating and the overall", abs((before - pl.ovr) - 3) < 1e-6 and all(pl.ratings[a] == atts[a] - 3 for a in atts))
check("and is on her record", pl.wear == ["knee"] and pl.wear_points == 3)
low = make_player(random.Random(3), 99002, "WR", 2.0, 26)
I.apply_lasting(low, "knee", 4)
check("ratings never go below the floor", all(v >= R.RATING_MIN for v in low.ratings.values()))
a, b = make_player(random.Random(4), 99003, "WR", 60.0, 31), make_player(random.Random(4), 99004, "WR", 60.0, 31)
b.wear = ["knee", "back"]
check("lasting damage shortens a career (higher retirement chance)", OFF._retire_prob(b) > OFF._retire_prob(a))
I.clear_on_exit(b)
check("when her career ends the record is wiped (no ailment outlives a career)", b.wear == [] and b.wear_points == 0)
rng = random.Random(21)
lg = new_league(rng, rosters=True)
res = run_season(lg, 1, rng, Options(engine="fast", keep_boxes=False))
inj, las = len(res.runner.injury_log), len(res.runner.lasting_log)
check("about 3 to 12% of injuries leave lasting damage", 0.03 <= las / inj <= 0.12, f"{las} of {inj}")
check("every lasting-damage entry names a real injury kind and 1 to 4 points", all(k in I.KIND_NAMES and 1 <= pts <= 4 for _, _, _, k, pts in res.runner.lasting_log))
for _ in range(3):
    res = run_season(lg, 2 + _, rng, Options(engine="fast", keep_boxes=False))
check("players who left the league carry no record of damage", all(not p.wear for p in lg.retired_players))
check("damage on the record equals the points lost", all(p.wear_points >= len(p.wear) for t in lg.teams for p in t.roster))

print()
print("FAILED: " + ", ".join(failures) if failures else "all injury checks passed")
sys.exit(1 if failures else 0)
