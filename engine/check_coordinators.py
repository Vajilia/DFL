"""Checks for the coordinators and the GM's plan (coordinators.py, gm_plan.py): the head coach hires, reviews and may veto; the coordinators
propose schemes and carry the plays; the Diamond Coronation tops every decision.

    python engine/check_coordinators.py
"""
import os
import pickle
import random
import statistics as st
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as C  # noqa: E402
import coordinators as CO  # noqa: E402
import staff_cards as SC  # noqa: E402
import decisions as D  # noqa: E402
import gm_plan as GP  # noqa: E402
import offseason as OFF  # noqa: E402
import store  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


def play(seed, years, driver=None, start=None):
    r = random.Random(seed)
    L = new_league(r, rosters=True)
    L.driver = driver
    res = [run_season(L, y, r, Options(engine="fast", keep_boxes=False)) for y in range(1, years + 1)]
    return L, r, res


class Pick:
    """A driver that answers some kinds with a fixed rule and everything else with the autopilot."""
    name = "pick"

    def __init__(self, rules):
        self.rules, self.seen = rules, {}

    def choose(self, dp):
        self.seen.setdefault(dp.kind, dp.public())
        f = self.rules.get(dp.kind)
        return (f(dp), "test") if f else (dp.default, "autopilot")


# ---- the cards ---------------------------------------------------------------------------------------------
L, rng, res = play(33, 8)
first_names = [c.name for c in L.coaches]
check("every team has an offensive and a defensive coordinator, who are ordinary coach cards doing that job, with a unique id",
      all(isinstance(t.oc, C.CoachCard) and isinstance(t.dc, C.CoachCard) and t.oc.job == "offensive coordinator" and t.dc.job == "defensive coordinator" and t.coach.job == "head coach" for t in L.teams)
      and len({c.cid for c in L.coaches}) == len(L.coaches))
check("nobody holds two jobs: every head coach, coordinator and person in the pool is a different card",
      len({id(x) for x in [t.coach for t in L.teams] + [t.oc for t in L.teams] + [t.dc for t in L.teams] + CO.pool(L)}) == 3 * 48 + len(CO.pool(L)))
CO.refresh_refs(L)
for side in CO.SIDES:
    pts = [CO.points(c, side) for c in CO.seated(L, side)]
    check(f"the average {side} coordinator on the job is worth zero", abs(sum(pts) / len(pts)) < 0.03, f"{sum(pts) / len(pts):+.4f}")
check("a coordinator's lift is capped", all(abs(CO.points(c, s)) <= CO.COORD_POINTS_AT_100 + 1e-12 for s in CO.SIDES for c in CO.seated(L, s)))
bound = CO.COORD_POINTS_AT_100 + CO.SCHEME_CAP
check("a unit's whole coaching lift stays inside the cap", all(abs(x) <= bound + 1e-9 for t in L.teams for x in CO.lifts(t.coach, t)), f"bound {bound}")
check("every team's scheme fits are mirrored and between -1 and 1",
      all(abs(t.scheme_fit["pass"] + t.scheme_fit["run"]) < 1e-9 and abs(t.scheme_fit["blitz"] + t.scheme_fit["coverage"]) < 1e-9
          and all(-1 <= v <= 1 for v in t.scheme_fit.values()) for t in L.teams))
check("the card prints", all(k in CO.render_coord(L.teams[3].oc, L) for k in ("PLAYCALLING", "VISION", "offensive coordinator")))
check("coordinators grow, fade and retire like any coach: some have retired as coordinators, ratings move", any(c.retired and any(e.get("job", "").endswith("coordinator") for e in c.career) for c in L.coaches)
      and any(len(c.history) > 1 for t in L.teams for c in (t.oc, t.dc)))

# ---- the Decision Points -----------------------------------------------------------------------------------
kinds = {e["kind"] for e in L.choice_log}
check("the coordinators' Decision Points are asked", {"coord_scheme", "scheme_veto", "coord_review", "hire_coordinator", "gm_draft_focus", "gm_cap_plan"} <= kinds, str(sorted(k for k in kinds if k.startswith(("coord", "scheme", "hire_coord", "gm_")))))
check("the autopilot chooses the old rule for the GM (needs, balanced)", all(e["chosen"] == "needs" for e in L.choice_log if e["kind"] == "gm_draft_focus") and all(e["chosen"] == "balanced" for e in L.choice_log if e["kind"] == "gm_cap_plan"))
sc = [e["chosen"] for e in L.choice_log if e["kind"] == "coord_scheme"]
check("the autopilot's coordinators propose all three schemes, mostly a leaning one", len(set(sc)) >= 5 and sc.count("balanced") < len(sc) * 0.6, f"{len(sc)} proposals")
vt = [e["chosen"] for e in L.choice_log if e["kind"] == "scheme_veto"]
check("head coaches veto some proposals and approve most", 0 < vt.count("veto") < vt.count("approve"), f"{vt.count('veto')} vetoes of {len(vt)}")
fired = [e for e in L.choice_log if e["kind"] == "coord_review" and e["chosen"] != "keep_both"]
check("head coaches fire coordinators, and every seat is filled again", len(fired) > 20 and all(t.oc and t.dc for t in L.teams), f"{len(fired)} reviews with a firing")

# vision sharpens the proposal; gamecraft sharpens the veto
t0 = L.teams[0]
def share_best(vision, side="offense"):
    c = C.make_coach_card(L.card_seed, 90000 + int(vision), None, age=40)
    c.ratings["gamecraft"] = vision
    n = 0
    for y in range(1, 301):
        dp = CO._scheme_point(L, t0, side, c, y, 5, 0.5)
        n += dp.default == "pass"
    return n / 300
hi, lo = share_best(100.0), share_best(1.0)
check("a coordinator with vision proposes the best-fitting scheme far more often than one without", hi > 0.85 and lo < 0.45, f"{hi:.2f} vs {lo:.2f}")
hc = t0.coach
t0.scheme_fit = {"pass": -0.5, "run": 0.5, "blitz": 0.0, "coverage": 0.0}
def veto_rate(gamecraft):
    old = hc.ratings["gamecraft"]
    hc.ratings["gamecraft"] = gamecraft
    n = sum(CO._veto_point(L, t0, "offense", t0.oc, "pass", y, 5).default == "veto" for y in range(1, 301))
    hc.ratings["gamecraft"] = old
    return n / 300
sharp, blunt = veto_rate(100.0), veto_rate(1.0)
check("a sharp head coach always vetoes a scheme that fights the roster; a poor one often lets it through", sharp == 1.0 and blunt < 0.9, f"{sharp:.2f} vs {blunt:.2f}")

# ---- a veto, and the reviews, when the drivers say so ----------------------------------------------------
drv = Pick({"scheme_veto": lambda dp: "veto"})
L.driver = drv
heat0 = {t.id: t.oc.heat for t in L.teams}
CO.preseason(L, 99)
check("a veto sends the unit back to balanced and costs the coordinator a little standing",
      all(t.scheme == {"offense": "balanced", "defense": "balanced"} for t in L.teams) and all(t.oc.heat >= heat0[t.id] for t in L.teams)
      and any(t.oc.heat > heat0[t.id] for t in L.teams))
check("a vetoed coordinator and her boss both have it on their card", any("overruled" in (t.oc.decision_log[-1]["action"] if t.oc.decision_log else "") for t in L.teams)
      and any("vetoed" in (t.coach.decision_log[-1]["action"] if t.coach.decision_log else "") for t in L.teams))
L.driver = Pick({"scheme_veto": lambda dp: "approve", "coord_scheme": lambda dp: min(dp.options, key=lambda o: dp.internal["fit"][o["id"]])["id"]})
CO.preseason(L, 100)
worst = [CO.lifts(t.coach, t) for t in L.teams]
check("even a league of the worst schemes, all approved, stays inside the cap",
      all(abs(x) <= bound + 1e-9 for pair in worst for x in pair) and all(t.scheme["offense"] != "balanced" or abs(t.scheme_fit["pass"]) < 0.02 for t in L.teams))
before = len(L.coaches)
L.driver = Pick({"coord_review": lambda dp: "fire_both" if "fire_both" in dp.option_ids else dp.default})
pct = {t.id: 0.5 for t in L.teams}
out = CO.season(L, 101, pct, set())
check("firing every coordinator fills every seat in the same offseason, from the pool, and nobody holds two seats",
      all(t.oc and t.dc for t in L.teams) and len(out["fired"]) >= 70 and len({id(x) for t in L.teams for x in (t.oc, t.dc)}) == 96
      and not any(any(c is t.oc or c is t.dc for t in L.teams) for c in L.free_coaches), f"{len(out['fired'])} fired")
check("the creator added people only to give each open seat a slate (the pool was topped up, not flooded)", len(L.coaches) - before <= 3 * len(out["hired"]) + CO.POOL_MIN, f"{len(L.coaches) - before} new cards for {len(out['hired'])} seats")
L.driver = Pick({"coord_review": lambda dp: "keep_both"})
out = CO.season(L, 102, pct, set())
check("a head coach who keeps everyone fires no one (age and retirement still open seats, and those are filled)", not out["fired"] and all(t.oc and t.dc for t in L.teams))
L.driver = None

# ---- the Coronation comes first --------------------------------------------------------------------------------
L2, rng2, res2 = play(5, 4, driver=None)
cap = Pick({})
L2.driver = cap
run_season(L2, 5, rng2, Options(engine="fast", keep_boxes=False))
check("every kind of decision shows the Diamond Coronation first", cap.seen and all(p["top_priority"]["goal"].startswith("Win the Diamond Coronation") and list(p)[0] == "top_priority" for p in cap.seen.values()),
      f"{len(cap.seen)} kinds")
check("the priority line says where the team stands", all(k in next(iter(cap.seen.values()))["top_priority"] for k in ("your_team", "strength_rank", "coronations_won", "last_won")))
check("the league keeps the Coronation winners: one a season", sum(len(v) for v in L2.titles.values()) == 5 and L2.titles == {k: v for k, v in L2.titles.items()})

# ---- the GM's plan --------------------------------------------------------------------------------------------
def banked(rule, seed=21, years=5):
    La, ra, _ = play(seed, years, driver=Pick({"gm_cap_plan": lambda dp: rule}))
    return statistics_mean([t.bank for t in La.teams]), La
def statistics_mean(xs):
    return sum(xs) / len(xs)
tight, Lt = banked("tight")
allin, La = banked("all_in")
check("a GM who keeps extra room back banks more of it than one who spends to the limit", tight > allin, f"{tight:.2f} vs {allin:.2f}")
check("neither plan breaks the hard cap", all(OFF.EC.counted_51([p.salary for p in t.roster], t.dead_now) <= OFF.EC.limit(t) + 1.0 for Lx in (Lt, La) for t in Lx.teams))
team = L.teams[0]
saved = team.roster
team.roster = [p for p in saved if p.pos != "QB"]
rq = random.Random(3)
needs = sum(OFF._pick_rookie_position(team.roster, 200, rq, "needs") == "QB" for _ in range(3000)) / 3000
best = sum(OFF._pick_rookie_position(team.roster, 200, rq, "best_player") == "QB" for _ in range(3000)) / 3000
team.roster = saved
check("drafting for need goes for a missing position; drafting the best player does not", needs > 2 * best and best > 0, f"{needs:.3f} vs {best:.3f}")
check("the GM's plan is on her card when it is not the old rule", any(g["action"].startswith("planned the offseason") for g in sum((t.gm.decision_log for t in Lt.teams), [])))

# ---- one coaching pool ---------------------------------------------------------------------------------------
class Choose(Pick):
    pass



L3, r3, _ = play(21, 6)
before = L3._coach_ids
n = len(CO.pool(L3))
made = CO.top_up(L3, 7, 0)
check("a pool at or over its target is left alone (no new people, no new ids)", (n >= CO.POOL_MIN and made == 0 and L3._coach_ids == before) or (n < CO.POOL_MIN and made == CO.POOL_MIN - n), f"{n} in the pool")
L3.free_coaches = L3.free_coaches[:5]
made = CO.top_up(L3, 7, 0)
check("a pool that has run low is topped up to its target", len(CO.pool(L3)) == CO.POOL_MIN and made > 0, f"{made} new people")
made = CO.top_up(L3, 7, 30)
check("and to a slate for every open seat when many are open at once", len(CO.pool(L3)) >= CO.SLATE * 30, f"{len(CO.pool(L3))} in the pool for 30 seats")
newest = [c for c in L3.coaches if any(e["event"] == "entered_coaching" for e in c.career)]
check("the creator's new people are young coaches in the making", newest and all(CO.POOL_AGE[0] <= c.age <= CO.POOL_AGE[1] + 8 for c in newest), f"{len(newest)} people")

# a head coach can hire a former head coach as a coordinator
t1 = L3.teams[1]
x = L3.teams[0].coach
L3.driver = None
SC._release(L3, "coach", x, 0, 7)
x.career.append({"year": 7, "event": "fired", "team": 0})
L3.teams[0].coach = None
x.job = ""
t1.oc = None
keep = (CO.POOL_MIN, CO.SLATE)
L3.free_coaches = [c for c in L3.free_coaches if c is x][:1] + [c for c in L3.free_coaches if c is not x][:2]
CO.POOL_MIN = 0
L3.driver = Pick({"hire_coordinator": lambda dp: next(k for k, c in dp.internal["candidates"].items() if c is x)})
hired = CO._hire_round(L3, 7, [(t1, "offense")])
CO.POOL_MIN = keep[0]
check("a head coach can hire a former head coach as her coordinator, from the same pool", t1.oc is x and x.job == "offensive coordinator" and CO.was_head_coach(x)
      and not any(c is x for c in L3.free_coaches), hired[0][2] if hired else "")
L3.driver = None

# a coordinator on another club can be hired away as a head coach, and her club refills her seat in the same offseason
L4, r4, _ = play(5, 7)
t_new, t_old = L4.teams[7], L4.teams[9]
mover = t_old.oc
mover.seasons_with_team = CO.PROMOTE_MIN_YEARS
old_boss = t_old.coach
t_new.coach = None
class TakeCoordinator(Pick):
    name = "take-coordinator"
cands_seen = []
def pick_coord(dp):
    cands_seen.extend(dp.internal["candidates"].values())
    return next((k for k, c in dp.internal["candidates"].items() if c is mover), dp.default)
L4.driver = Pick({"hire_coach": pick_coord})
r = random.Random(1)
orig = CO.slate
def forced(lg, t, year, taken, head, rr):
    got = orig(lg, t, year, taken, head, rr)
    if head and mover not in got:
        got[-1] = mover
    return got
CO.slate = forced
SC._hire_round(L4, 8, [("coach", t_new)])
CO.slate = orig
check("a coordinator who has earned it can be hired away as a head coach: no permission step, she leaves her seat", t_new.coach is mover and mover.job == "head coach" and t_old.oc is None
      and any(e["event"] == "promoted" for e in mover.career))
L4.driver = Pick({})
out = CO.season(L4, 8, {t.id: 0.5 for t in L4.teams}, set())
check("and her old club refills the seat in the same offseason, with its head coach choosing", t_old.oc is not None and t_old.oc is not mover and any(h[0] == t_old.id for h in out["hired"]))
L4.driver = None
check("a coordinator with too little time in her seat is not on the head-coach market", all(c is not t_old.dc for c in CO.slate(L4, L4.teams[3], 9, set(), True, random.Random(2))) or t_old.dc.seasons_with_team >= CO.PROMOTE_MIN_YEARS)
promos = [c for c in L.coaches if any(e["event"] == "promoted" for e in c.career)]
check("over eight seasons some coordinators were hired away as head coaches", len(promos) >= 5, f"{len(promos)} promotions")
fh = [c for c in L.coaches if CO.was_head_coach(c) and any(e["event"] == "hired" and "coordinator" in str(e.get("job", "")) for e in c.career)]
check("and some coordinators had been head coaches before", len(fh) >= 5, f"{len(fh)} former head coaches")

# ---- saves, determinism, old leagues --------------------------------------------------------------------------
path = tempfile.mktemp(suffix=".db")
La3, ra3, _ = play(7, 5)
store.save(path, La3, ra3, 5)
Lb, rb, yb = store.load(path)
same = all(a.oc.name == b.oc.name and a.dc.name == b.dc.name and a.scheme == b.scheme and a.oc.heat == b.oc.heat for a, b in zip(La3.teams, Lb.teams))
check("coordinators, schemes, the coaching pool and the Coronation list survive a save", same and len(Lb.coaches) == len(La3.coaches) and len(Lb.free_coaches) == len(La3.free_coaches) and Lb.titles == La3.titles)
x = run_season(La3, 6, ra3, Options(engine="fast", keep_boxes=False))
y = run_season(Lb, 6, rb, Options(engine="fast", keep_boxes=False))
check("a loaded league plays on exactly as the original (champion and every coordinator)", x.champion == y.champion and all(a.oc.name == b.oc.name and a.dc.name == b.dc.name for a, b in zip(La3.teams, Lb.teams)))
check("a snapshot of the league (pickle) keeps them too", all(t.oc is not None for t in pickle.loads(pickle.dumps(La3)).teams))
check("same seed, same coaching world (every coach card, created and hired through eight seasons)", [c.name for c in play(33, 8)[0].coaches] == first_names)
for t in Lb.teams:
    t.oc = t.dc = None
    t.scheme, t.scheme_fit = {}, {}
run_season(Lb, 7, rb, Options(engine="fast", keep_boxes=False))
check("a league saved before coordinators existed gets them at the next preseason and plays on", all(t.oc and t.dc for t in Lb.teams))
print()
if failures:
    print(f"{len(failures)} coordinator check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All coordinator checks passed.")
