"""Checks for CEO and GM cards, recall votes, hiring and firing.

    python engine/check_staff.py
"""
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as C  # noqa: E402
import rules as R  # noqa: E402
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
check("every team has a CEO and a GM", all(t.owner is not None and t.gm is not None for t in lg.teams))
check("CEO and GM names are unique", len({t.owner.name for t in lg.teams}) == 48 and len({t.gm.name for t in lg.teams}) == 48)
check("all staff ratings are between 1 and 100", all(1 <= v <= 100 for t in lg.teams for v in list(t.owner.ratings.values()) + list(t.gm.ratings.values())))
check("starting approvals are sensible", all(0.3 <= t.owner.approval <= 0.75 for t in lg.teams))
check("cards print in the template format", all(k in S.render_owner(lg.teams[0].owner, lg) for k in ("IDENTITY", "PERSONALITY", "SOUL", "RATINGS", "RECOGNITION", "RELATIONSHIPS")) and "GM" in S.render_gm(lg.teams[0].gm, lg))
lg2 = new_league(random.Random(5), rosters=True)
check("same seed gives the same CEOs and GMs", [(t.owner.name, t.gm.name) for t in lg.teams] == [(t.owner.name, t.gm.name) for t in lg2.teams])

# ---- GM levers are small and capped ----------------------------------------------------------------
gms = [S.make_gm_card(3, i) for i in range(1, 2001)]
check("GM scouting effect stays inside its cap", all(abs(g.scouting_points) <= S.GM_SCOUTING_POINTS + 1e-9 for g in gms))
check("GM retention effect stays inside its cap", all(abs(g.retention_factor - 1) <= S.GM_RETENTION + 1e-9 for g in gms))
big = S.make_gm_card(1, 1)
big.ratings.update(scouting=100.0, negotiation=1.0)
check("the caps hold at the extremes", abs(big.scouting_points) <= S.GM_SCOUTING_POINTS + 1e-9 and abs(big.retention_factor - 1) <= S.GM_RETENTION + 1e-9)
check("the average GM changes nothing (ratings centered on 50)", abs(st.mean(g.scouting_points for g in gms)) < 0.1 and abs(st.mean(g.retention_factor for g in gms) - 1) < 0.02)
check("with no staff the GM levers do nothing", S.gm_scouting_bonus(new_league(random.Random(1), rosters=True, coaches=False).teams[0]) == 0.0)

# ---- 40 seasons of accountability --------------------------------------------------------------------
def play(seed, years=40):
    r = random.Random(seed)
    L = new_league(r, rosters=True)
    hist = []
    for y in range(1, years + 1):
        res = run_season(L, y, r, Options(engine="fast", keep_boxes=False))
        hist.append(res)
    return L, hist


L, hist = play(33)
check("every team has a CEO, a GM and a coach at all times", all(t.owner and t.gm and t.coach for t in L.teams))
seats = {}
twice = False
for o in L.owners:
    if len(set(o.teams_owned)) > 1:
        twice = True
check("no CEO has ever owned two teams", not twice, f"{len(L.owners)} CEOs and candidates generated")
check("no recalled or retired CEO owns a team now", all(t.owner.status == "owner" for t in L.teams))
check("nobody owns a team twice (each seated CEO is unique)", len({t.owner.oid for t in L.teams}) == 48)
rotation_ok = True
for y in range(1, 41):
    div = (y - 1) % R.TOTAL_DIVISIONS
    voted = set(hist[y - 1].staff["votes"])
    rotation_ok &= all(t.id in voted for t in L.division(div))
check("every CEO in the rotation division is voted on every year (8-year cycle)", rotation_ok)
exile_ok = all(set(h.new_exiles) <= set(h.staff["votes"]) for h in hist)
check("every newly exiled team's CEO faces a vote", exile_ok)
events = [e for e in L.archive if e["event"] == "recall_vote"]
check("recall votes are logged with 5 candidates each", all(len(e["candidates"]) == R.RECALL_REPLACEMENT_CANDIDATES and e["replacement"] in e["candidates"] for e in events if e["result"] == "recalled"))
check("a recall needs a majority (share above 50%), a survival does not reach it", all((e["recall_share"] >= 0.5) if e["result"] == "recalled" else (e["recall_share"] <= 0.5) for e in events))
check("votes are not rubber stamps: some CEOs fall and some survive", any(e["result"] == "recalled" for e in events) and any(e["result"] == "survived" for e in events),
      f"{sum(e['result'] == 'recalled' for e in events)} recalled, {sum(e['result'] == 'survived' for e in events)} survived of {len(events)}")
low = [o for o in L.owners if o.status == "recalled"]
check("recalled CEOs had fans against them", st.mean(next(e for e in o.career if e["event"] == "recalled")["approval"] for o in low) < 0.45, f"average approval {st.mean(next(e for e in o.career if e['event'] == 'recalled')['approval'] for o in low):.2f}")
per_year = [len(h.staff["recalled"]) for h in hist]
check("recalls per year look sensible (some every year, never most of the league)", 0 < st.mean(per_year) < 10 and max(per_year) < 20, f"average {st.mean(per_year):.1f}, max {max(per_year)}")
approvals = [a for h in hist[8:] for a in h.staff["approval"].values()]
check("fan approval is spread across teams and stays in range", 0.05 < st.pstdev(approvals) < 0.2 and 0 <= min(approvals) and max(approvals) <= 1, f"mean {st.mean(approvals):.2f}, sd {st.pstdev(approvals):.2f}")
cf = sum(len(h.staff["coach_fired"]) for h in hist) / 40
check("coaches get fired, at a plausible rate", 2 < cf < 12, f"{cf:.1f} firings a year")
gf = sum(len(h.staff["gm_fired"]) for h in hist) / 40
check("GMs get fired, less often than coaches", 0.5 < gf < cf, f"{gf:.1f} firings a year")
import recognition as RC  # noqa: E402
o0 = L.teams[0].owner
check("fame buys no rope: the firing threshold does not depend on esteem (the dial is zero; at 1.0 it would double at the legend bar)",
      S.ROPE_WEIGHT == 0.0 and S.GM_ROPE_WEIGHT == 0.0 and abs(S._fire_threshold(o0, 1.0 + S.ROPE_WEIGHT * 1.0) - S._fire_threshold(o0, 1.0)) < 1e-9)
fired = [c for c in L.coaches if any(e["event"] == "fired" for e in c.career)]
check("fired coaches did worse than keepers (their heat was real)", st.mean(c.heat for c in fired) > st.mean(t.coach.heat for t in L.teams), "")
check("the Archive records the firings and hirings", {"coach_fired", "gm_fired", "gm_hired", "recall_vote"} <= {e["event"] for e in L.archive})
check("CEOs are not ancient", all(t.owner.age <= S.OWNER_MAX_AGE for t in L.teams))

# ---- determinism and no effect on the engine's random stream ------------------------------------------------
L2, _ = play(33, 12)
L3, _ = play(33, 12)
check("same seed gives the identical history of recalls and firings", L2.archive == L3.archive)

print()
if failures:
    print(f"{len(failures)} staff check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All staff checks passed.")
