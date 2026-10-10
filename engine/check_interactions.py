"""Checks for the Interaction system's first slice (firing, recall vote and exile determination scenes).

    python engine/check_interactions.py
"""
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import interactions as IX  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


def play(seed, years, **kw):
    r = random.Random(seed)
    L = new_league(r, rosters=True, **kw)
    res = [run_season(L, y, r, Options(engine="fast", keep_boxes=False)) for y in range(1, years + 1)]
    return L, res, r


def scenes(L, kind=None):
    return [e for e in L.archive if e["event"] == "interaction" and (kind is None or e["kind"] == kind)]


# ---- scenes never change an outcome -------------------------------------------------------------------------
YEARS = 40
La, ra, rnga = play(33, YEARS, interactions=True)
Lb, rb, rngb = play(33, YEARS, interactions=False)


def fingerprint(res):
    return [(r.champion, tuple(r.new_exiles), tuple(sorted(r.returners)), tuple(r.votes) if hasattr(r, "votes") else (),
             tuple(sorted((tid, round(float(s.pct), 6)) for tid, s in r.stats.items())), tuple(r.staff["recalled"]),
             tuple(r.staff["coach_fired"]), tuple(r.staff["gm_fired"]), tuple(sorted(r.staff["approval"].items()))) for r in res]


check(f"{YEARS} seasons play out identically with scenes on or off (champions, exiles, every win percentage, every recall and firing, every approval)",
      fingerprint(ra) == fingerprint(rb))
check("scenes draw nothing from the engine's random stream", rnga.getstate() == rngb.getstate())
check("the plain Archive entries are identical with scenes on or off", [e for e in La.archive if e["event"] != "interaction"] == Lb.archive)
check("with scenes off there are no scenes and no relationships anywhere",
      not scenes(Lb) and all(not o.relationships for o in Lb.owners) and all(not c.relationships for c in Lb.coaches))
check("the final rosters and ratings are the same too", [(t.coach.name, t.owner.name, t.gm.name, round(t.strength, 4)) for t in La.teams] ==
      [(t.coach.name, t.owner.name, t.gm.name, round(t.strength, 4)) for t in Lb.teams])

# ---- every required event has a scene --------------------------------------------------------------------------
check("every exile gets a determination scene", len(scenes(La, "exile_determination")) == sum(len(r.new_exiles) for r in ra))
check("every recall vote gets a scene", len(scenes(La, "recall_vote")) == sum(len(r.staff["votes"]) for r in ra))
check("every firing gets a scene", len(scenes(La, "firing")) == sum(len(r.staff["coach_fired"]) + len(r.staff["gm_fired"]) for r in ra))
exiled_by_year = {r.year: set(r.new_exiles) for r in ra}
check("exile scenes are about exactly the teams that were exiled that year", all(e["team"] in exiled_by_year[e["year"]] for e in scenes(La, "exile_determination")))
pct = {r.year: {tid: float(s.pct) for tid, s in r.stats.items()} for r in ra}
check("the record in each scene's evidence is the team's real record", all(abs(e["evidence"]["record"] - pct[e["year"]][e["team"]]) < 1e-3
      for e in scenes(La) if e["team"] in pct[e["year"]]))
ids = [e["id"] for e in scenes(La)]
check("scene ids are unique", len(ids) == len(set(ids)))

# ---- claims and evidence --------------------------------------------------------------------------------------
ok = True
bad = None
for e in scenes(La):
    for c in e["claims"]:
        if c["role"] == "new_owner":
            continue
        want = IX.supported(c["frame"], e["evidence"])
        if want != (c["role"] in e["supports"]):
            ok, bad = False, (e["id"], c["role"], c["frame"])
check("a claim is marked supported exactly when the engine's numbers back it", ok, str(bad) if bad else "")
mand = [e for e in scenes(La, "recall_vote") if any(c["role"] == "new_owner" for c in e["claims"])]
check("a new CEO's mandate is supported exactly when she topped the candidates on the fans' taste",
      all(("new_owner" in e["supports"]) == bool(e["evidence"]["elected_is_best_on_taste"]) for e in mand), f"{len(mand)} elections")
fire = scenes(La, "firing")
rul = [e["evidence"]["ruling"] for e in fire]
check("every firing gets one ruling: sweep, fair, harsh or unfounded", set(rul) <= {"sweep", "fair", "harsh", "unfounded"})
check("a sweep is only ever by a new CEO, and only a new CEO's sweep is called one",
      all((e["evidence"]["ruling"] == "sweep") == e["evidence"]["new_owner"] for e in fire))
check("a firing is never called fair unless the record backs the CEO", all("owner" in e["supports"] for e in fire if e["evidence"]["ruling"] == "fair"))
# harsh runs 5 to 8% of firings; with ~200 firings a seed can dip just under 5%, so the floor is 3% and at least 5 cases
check("the evidence really decides: fair and harsh firings both happen", all(rul.count(k) / len(rul) > 0.03 and rul.count(k) >= 5 for k in ("fair", "harsh")),
      ", ".join(f"{k} {rul.count(k)}" for k in ("sweep", "fair", "harsh", "unfounded")))
gap = [c["claimed_z"] - e["evidence"]["strength_z"] for e in scenes(La) for c in e["claims"] if c["role"] == "coach" and c["frame"] == "talent" and "claimed_z" in c]
check("coaches who blame the roster exaggerate on average", len(gap) > 50 and st.mean(gap) < -0.3, f"claimed {st.mean(gap):+.2f} deviations lower than the truth over {len(gap)} claims")
sup = [("coach" in e["supports"]) for e in scenes(La) if any(c["role"] == "coach" and c["frame"] == "talent" and "claimed_z" in c for c in e["claims"])]
check("some of those excuses are true and some are not", 0.05 < sum(sup) / len(sup) < 0.95, f"{sum(sup)} of {len(sup)} backed")
check("each scene's claims come from different parties", all(len({c["role"] for c in e["claims"]}) == len(e["claims"]) for e in scenes(La)))
check("every scene has at least a CEO claim and an evidence verdict", all(e["claims"] and e["claims"][0]["role"] == "owner" and e["verdict"] for e in scenes(La)))

# ---- relationships and decision logs -------------------------------------------------------------------------
cards = list(La.owners) + list(La.coaches) + list(La.gms) + list(La.fanbases) + list(La.media)
vals = [v for c in cards for v in c.relationships.values()]
check("relationships stay between -100 and +100", vals and all(-100 <= v <= 100 for v in vals), f"{len(vals)} relationships")
fired_coaches = [c for c in La.coaches if any(e["event"] == "fired" and "job" not in e for e in c.career)]      # head coaches: a coordinator is fired by her head coach, not a CEO
check("fired coaches hold a grudge against the CEO who fired them", all(any(k.startswith("owner:") and v < 0 for k, v in c.relationships.items()) for c in fired_coaches),
      f"{len(fired_coaches)} fired coaches")
recalled = [o for o in La.owners if o.status == "recalled"]
check("recalled CEOs hold a grudge against their fans (however much goodwill they had banked)", all(o.relationships.get(f"fans:{o.teams_owned[0]}", 0) < 0 for o in recalled), f"{len(recalled)} recalled CEOs")
check("and the fans against them", all(La.by_id[o.teams_owned[0]].fans.relationships.get(f"owner:{o.oid}", 0) < 0 for o in recalled))
check("an elected CEO starts warm with her fans", any(o.relationships.get(f"fans:{o.teams_owned[0]}", 0) > 0 for o in La.owners if o.status == "owner" and any(e["event"] == "elected" for e in o.career)))
check("every card's relationship keys name real kinds of party", all(k.split(":")[0] in ("owner", "coach", "gm", "fans", "press") for c in cards for k in c.relationships))
log_ids = {d.get("interaction") for c in cards for d in c.decision_log}      # staff and plan entries (coordinators.py, gm_plan.py) belong to no scene
check("every exile, recall and firing scene is in at least one decision log", set(ids) <= log_ids, f"{len(set(ids) - log_ids)} missing")
check("CEOs who fired someone logged the choice", all(any(d["action"].startswith("fired") for d in t.owner.decision_log) for t in La.teams if any(e["event"] == "coach_fired" and e["team"] == t.id and e["by"] == t.owner.name for e in La.archive)))

# ---- rendering ---------------------------------------------------------------------------------------------
for kind in ("exile_determination", "recall_vote", "firing"):
    txt = IX.render_scene(scenes(La, kind)[-1], La)
    check(f"a {kind.replace('_', ' ')} scene prints in the Archive's format", txt.startswith("EVENT") and "claims:" in txt and "Evidence supports:" in txt and "Outcome:" in txt)

# ---- determinism, and it works without fan and media cards ------------------------------------------------------
Lc, _, _ = play(33, 12, interactions=True)
Ld, _, _ = play(33, 12, interactions=True)
check("same seed gives the identical scenes", scenes(Lc) == scenes(Ld))
Le, _, _ = play(8, 10, fans=False)
check("scenes still work with no fan or media cards (those parties just do not speak)",
      scenes(Le) and all(c["role"] not in ("fans", "press") for e in scenes(Le) for c in e["claims"]))

print()
if failures:
    print(f"{len(failures)} interaction check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All interaction checks passed.")
