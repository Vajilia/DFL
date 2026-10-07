"""Checks for fanbase and media cards.

    python engine/check_fans.py
"""
import os
import copy
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fan_media_cards as FM  # noqa: E402
import staff_cards as S  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


# ---- a fresh league --------------------------------------------------------------------------------
lg = new_league(random.Random(5), rosters=True)
check("every team has one fanbase", all(t.fans is not None for t in lg.teams) and len(lg.fanbases) == 48)
nat = [m for m in lg.media if m.kind == "national"]
loc = [m for m in lg.media if m.kind == "local"]
check("four national outlets and one local outlet per team", len(nat) == FM.N_NATIONAL and sorted(m.team_id for m in loc) == sorted(t.id for t in lg.teams))
check("all fan and media ratings are between 1 and 100", all(1 <= v <= 100 for f in lg.fanbases for v in f.ratings.values()) and all(1 <= v <= 100 for m in lg.media for v in m.ratings.values()))
check("fan ratings are centered near 50 across the league", abs(st.mean(f.ratings[a] for f in lg.fanbases for a in FM.FAN_ATTRS) - 50) < 4)
check("every fan culture appears somewhere in a 48-team league", {f.culture for f in lg.fanbases} == set(FM.CULTURES))
check("fan approval starts equal to the owner's", all(abs(t.fans.approval - t.owner.approval) < 1e-9 for t in lg.teams))
check("cards print in the template format", all(k in FM.render_fanbase(lg.fanbases[0], lg) for k in ("IDENTITY", "PERSONALITY", "ARCHETYPES", "RATINGS", "RELATIONSHIPS"))
      and all(k in FM.render_outlet(lg.media[0], lg) for k in ("IDENTITY", "PERSONALITY", "ARCHETYPES", "RATINGS", "RELATIONSHIPS")))
lg2 = new_league(random.Random(5), rosters=True)
check("same seed gives the same fanbases and outlets",
      [(f.culture, f.ratings) for f in lg.fanbases] == [(f.culture, f.ratings) for f in lg2.fanbases] and [(m.name, m.voice, m.ratings) for m in lg.media] == [(m.name, m.voice, m.ratings) for m in lg2.media])
check("local outlets carry their own team's name", all(lg.by_id[m.team_id].name in m.name for m in loc))
check("with the fan switch off there are no fan cards", all(t.fans is None for t in new_league(random.Random(5), rosters=True, fans=False).teams))

# ---- fan capital is only ever a buffer -----------------------------------------------------------------
t0 = lg.teams[0]
vals = []
for cap in (0.0, 0.3, 0.5, 0.6, 1.0):
    t0.fans.capital = cap
    vals.append(FM.capital_buffer(t0))
check("Fan Capital never makes a recall more likely", all(v >= 0 for v in vals))
check("Fan Capital's buffer stays inside its cap", max(vals) <= FM.CAPITAL_RECALL_WEIGHT * (1 - FM.CAPITAL_FLOOR) + 1e-9, f"max {max(vals):.3f}")

# Compare forecast grading against the same result and starting credibility.
# This isolates the earning rule from a particular league's recent luck.
graded = copy.deepcopy(lg)
accurate, sloppy = [copy.deepcopy(nat[0]) for _ in range(2)]
accurate.mid, sloppy.mid = 900001, 900002
accurate.credibility = sloppy.credibility = 50.0
accurate.forecasts, sloppy.forecasts = {t0.id: 0.7}, {t0.id: 0.5}
graded.media = [accurate, sloppy]
FM.media_season(graded, 1, {t0.id: 0.7}, t0.id, [])
check("a better forecast earns more credibility against the same result",
      accurate.credibility > 50.0 > sloppy.credibility and accurate.record[-1]["error"] < sloppy.record[-1]["error"])


# ---- 40 seasons -------------------------------------------------------------------------------------
def play(seed, years=40, fans=True):
    r = random.Random(seed)
    L = new_league(r, rosters=True, fans=fans)
    snaps = []
    for y in range(1, years + 1):
        res = run_season(L, y, r, Options(engine="fast", keep_boxes=False))
        snaps.append(res)
        # checked every season, not just at the end
        for t in L.teams:
            f = t.fans
            if not (0 <= f.approval <= 1 and 0 <= f.capital <= 1 and abs(f.approval - t.owner.approval) < 1e-9
                    and abs(f.ratings["expectations"] - f.birth_expectations) <= FM.EXPECT_BOUND + 1e-6
                    and abs(f.last_sway) <= FM.MEDIA_SWAY * 1.25 * 1.5 + 1e-9):
                failures.append(f"season {y}: fan state out of bounds for team {t.id}")
                break
    return L, snaps, r


L, snaps, r_on = play(33)
check("approval, capital and expectations stay inside their bounds every season (and mirror the owner)", not [f for f in failures if f.startswith("season")])
max_sway = max(abs(t.fans.last_sway) for t in L.teams)
check("the press moves approval by no more than its cap", max_sway <= FM.MEDIA_SWAY * 1.25 * 1.5 + 1e-9, f"largest this year {100 * max_sway:.1f} points")
check("every team still has exactly one active local outlet and four active national outlets",
      all(sum(1 for m in L.media if m.status == "active" and m.kind == "local" and m.team_id == t.id) == 1 for t in L.teams)
      and sum(1 for m in L.media if m.status == "active" and m.kind == "national") == FM.N_NATIONAL)
check("credibility stays between 1 and 100", all(1 <= m.credibility <= 100 for m in L.media))
folded = [m for m in L.media if m.status == "folded"]
check("outlets fold and are replaced (the Archive records it)", len(folded) > 0 and sum(e["event"] == "outlet_folded" for e in L.archive) == len(folded), f"{len(folded)} folded in 40 seasons")
active = [m for m in L.media if m.status == "active" and len(m.record) >= 20]
for extra_seed in (8, 9, 10, 11):                 # pool four more leagues: one league's 46 outlets is too few for a stable correlation (the true link is real but weak, about 0.1 to 0.2, because a season's results are noisy)
    rr = random.Random(extra_seed)
    Lx = new_league(rr, rosters=True)
    for y in range(1, 41):
        run_season(Lx, y, rr, Options(engine="fast", keep_boxes=False))
    active += [m for m in Lx.media if m.status == "active" and len(m.record) >= 20]
accs = [m.ratings["accuracy"] for m in active]
# Credibility is a short moving average. Compare accuracy with the mean scored
# forecast over a career, rather than one noisy final-year credibility value.
creds = [st.mean(max(0.0, 100.0 * (1.0 - e["error"] / 0.20)) for e in m.record) for m in active]
mx, my = st.mean(accs), st.mean(creds)
corr = sum((a - mx) * (c - my) for a, c in zip(accs, creds)) / (sum((a - mx) ** 2 for a in accs) ** 0.5 * sum((c - my) ** 2 for c in creds) ** 0.5)
check("accurate outlets earn higher forecast scores over their careers", corr > 0.05, f"correlation {corr:.2f} over {len(active)} outlets with 20+ seasons in 5 leagues")

# expectations drift the way results run
wins = {t.id: [] for t in L.teams}
for res in snaps:
    for tid, s in res.stats.items():
        wins[tid].append(float(s.pct))
xs = [st.mean(wins[t.id]) for t in L.teams]
ys = [t.fans.ratings["expectations"] - t.fans.birth_expectations for t in L.teams]
mx, my = st.mean(xs), st.mean(ys)
c2 = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / (sum((a - mx) ** 2 for a in xs) ** 0.5 * sum((b - my) ** 2 for b in ys) ** 0.5)
check("fans who see winning come to expect it (expectations drift with results)", c2 > 0.4, f"correlation {c2:.2f}")
check("expectations do not all inflate together", abs(st.mean(ys)) < 4, f"mean drift {st.mean(ys):+.1f}")

# the fans choose by their taste
gain = []
by_name = {o.name: o for o in L.owners}
for e in L.archive:
    if e["event"] == "recall_vote" and e["result"] == "recalled":
        taste = L.by_id[e["team"]].fans.taste
        cands = [by_name[n] for n in e["candidates"] if n in by_name]
        pick = by_name.get(e["replacement"])
        if pick and cands:
            gain.append(pick.ratings[taste] - st.mean(c.ratings[taste] for c in cands))
check("fans elect the candidate who is strong on the trait their culture looks for", len(gain) > 30 and st.mean(gain) > 3, f"{len(gain)} recalls; winner is +{st.mean(gain):.1f} on their taste")

# ---- no effect on the engine's random stream ------------------------------------------------------------------
ra, rb = random.Random(9), random.Random(9)
La, Lb = new_league(ra, rosters=True, fans=True), new_league(rb, rosters=True, fans=False)
a1 = run_season(La, 1, ra, Options(engine="fast", keep_boxes=False))
b1 = run_season(Lb, 1, rb, Options(engine="fast", keep_boxes=False))
check("fan and media cards draw nothing from the engine's random stream", ra.getstate() == rb.getstate())
check("the first season's results do not depend on the fan switch", [(g.home_pts, g.away_pts) for g in a1.games] == [(g.home_pts, g.away_pts) for g in b1.games])

# ---- determinism ---------------------------------------------------------------------------------------------
_, s1, _ = play(21, 10)
_, s2, _ = play(21, 10)
check("same seed gives the identical history", [(s.champion, s.new_exiles) for s in s1] == [(s.champion, s.new_exiles) for s in s2])
La, _, _ = play(21, 12)
Lb, _, _ = play(21, 12)
check("same seed gives the identical Archive", La.archive == Lb.archive)
check("never-twice still holds", all(len(set(o.teams_owned)) <= 1 for o in L.owners) and len({t.owner.oid for t in L.teams}) == 48)

print()
if failures:
    print(f"{len(failures)} fan/media check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All fan and media checks passed.")
