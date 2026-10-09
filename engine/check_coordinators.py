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
import coordinators as CO  # noqa: E402
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
first_names = [c.name for c in L.coords]
check("every team has an offensive and a defensive coordinator, on her own side, with a unique id",
      all(t.oc and t.dc and t.oc.side == "offense" and t.dc.side == "defense" for t in L.teams) and len({c.cid for c in L.coords}) == len(L.coords))
check("a coordinator's name is not a head coach's", not ({c.name for c in L.coords} & {c.name for c in L.coaches}))
CO.refresh_refs(L)
for side in CO.SIDES:
    pts = [c.points for c in CO.seated(L, side)]
    check(f"the average {side} coordinator on the job is worth zero", abs(sum(pts) / len(pts)) < 0.03, f"{sum(pts) / len(pts):+.4f}")
check("a coordinator's lift is capped", all(abs(c.points) <= CO.COORD_POINTS_AT_100 + 1e-12 for c in L.coords))
bound = CO.COORD_POINTS_AT_100 + CO.SCHEME_CAP
check("a unit's whole coaching lift stays inside the cap", all(abs(x) <= bound + 1e-9 for t in L.teams for x in CO.lifts(t.coach, t)), f"bound {bound}")
check("every team's scheme fits are mirrored and between -1 and 1",
      all(abs(t.scheme_fit["pass"] + t.scheme_fit["run"]) < 1e-9 and abs(t.scheme_fit["blitz"] + t.scheme_fit["coverage"]) < 1e-9
          and all(-1 <= v <= 1 for v in t.scheme_fit.values()) for t in L.teams))
check("the card prints", all(k in CO.render_coord(L.teams[3].oc, L) for k in ("PLAYCALLING", "VISION", "offensive coordinator")))
check("coordinators grow, fade and retire: some have retired, some are between jobs, ages move", any(c.status == "retired" for c in L.coords) and L.free_coords and all(len(c.history) >= 1 for c in L.coords))

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
    c = CO.make_coord_card(L.card_seed, 9000 + int(vision), side, t0.id)
    c.ratings["vision"] = vision
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
before = len(L.coords)
L.driver = Pick({"coord_review": lambda dp: "fire_both" if "fire_both" in dp.option_ids else dp.default})
pct = {t.id: 0.5 for t in L.teams}
out = CO.season(L, 101, pct, set())
check("firing every coordinator fills every seat in the same offseason with people who have real ids",
      all(t.oc and t.dc for t in L.teams) and len(out["fired"]) >= 70 and all(t.oc.cid < CO.CAND_BASE and t.dc.cid < CO.CAND_BASE for t in L.teams)
      and len({c.cid for c in L.coords}) == len(L.coords), f"{len(out['fired'])} fired")
check("candidates who were not hired never enter the league's books", len(L.coords) - before <= len(out["hired"]), f"{len(L.coords) - before} new cards for {len(out['hired'])} seats")
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

# ---- saves, determinism, old leagues --------------------------------------------------------------------------
path = tempfile.mktemp(suffix=".db")
La3, ra3, _ = play(7, 5)
store.save(path, La3, ra3, 5)
Lb, rb, yb = store.load(path)
same = all(a.oc.name == b.oc.name and a.dc.name == b.dc.name and a.scheme == b.scheme and a.oc.heat == b.oc.heat for a, b in zip(La3.teams, Lb.teams))
check("coordinators, schemes, free coordinators and the Coronation list survive a save", same and len(Lb.coords) == len(La3.coords) and len(Lb.free_coords) == len(La3.free_coords) and Lb.titles == La3.titles)
x = run_season(La3, 6, ra3, Options(engine="fast", keep_boxes=False))
y = run_season(Lb, 6, rb, Options(engine="fast", keep_boxes=False))
check("a loaded league plays on exactly as the original (champion and every coordinator)", x.champion == y.champion and all(a.oc.name == b.oc.name and a.dc.name == b.dc.name for a, b in zip(La3.teams, Lb.teams)))
check("a snapshot of the league (pickle) keeps them too", all(t.oc is not None for t in pickle.loads(pickle.dumps(La3)).teams))
check("same seed, same coordinators (every one, hired through eight seasons)", [c.name for c in play(33, 8)[0].coords] == first_names)
for t in Lb.teams:
    t.oc = t.dc = None
    t.scheme, t.scheme_fit = {}, {}
Lb.coords, Lb.free_coords = [], []
run_season(Lb, 7, rb, Options(engine="fast", keep_boxes=False))
check("a league saved before coordinators existed gets them at the next preseason and plays on", all(t.oc and t.dc for t in Lb.teams))
print()
if failures:
    print(f"{len(failures)} coordinator check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All coordinator checks passed.")
