"""Checks for the GM-and-head-coach relationship (relations.py): the Commissioner's ruling that the two are equals with separate spheres,
that neither is obliged to cooperate, and that how they get on is a road each side travels.

    python engine/check_relations.py
"""
import os
import random
import statistics as st
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decisions as D  # noqa: E402
import relations as RL  # noqa: E402
import store  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


def play(seed, years, driver=None, patch=False):
    r = random.Random(seed)
    L = new_league(r, rosters=True)
    L.driver = driver
    if patch:
        orig = RL.season
        RL.season = lambda lg, year, pct: dict(pairs=0, started=0)
    try:
        res = [run_season(L, y, r, Options(engine="fast", keep_boxes=False)) for y in range(1, years + 1)]
    finally:
        if patch:
            RL.season = orig
    return L, r, res


def pairs(L):
    for t in L.teams:
        if t.coach is not None and t.gm is not None and t.status == "active":
            yield t, t.gm.relationships.get(f"coach:{t.coach.cid}"), t.coach.relationships.get(f"gm:{t.gm.gid}")


# labels
check("labels run from a great partnership to bitter enemies",
      RL.label(80) == "a great partnership" and RL.label(40) == "they get on well" and RL.label(0) == "indifferent"
      and RL.label(-25) == "strained" and RL.label(-90) == "bitter enemies" and RL.label(-100) == "bitter enemies")


class Spy:
    name = "spy"

    def __init__(self):
        self.kinds = {}

    def choose(self, dp):
        ctx = dp.context
        d = self.kinds.setdefault(dp.kind, [0, 0])
        d[0] += 1
        d[1] += int("your_gm" in ctx or "how_your_gm_and_coach_get_on" in ctx or "your_head_coach" in ctx)
        return dp.default, "spy"


spy = Spy()
L, r, res = play(33, 4, driver=spy)
ps = list(pairs(L))
have = [(t, a, b) for t, a, b in ps if a is not None and b is not None]
check("every settled pair has a meter on each side (a pairing made this offseason starts next season)", len(ps) >= 40 and len(have) >= len(ps) - 6
      and all((a is None) == (b is None) for _, a, b in ps), f"{len(have)}/{len(ps)} pairs")
ps = have
allv = [v for _, a, b in ps for v in (a, b)]
check("the meters stay inside -100..100", all(-100 <= v <= 100 for v in allv), f"{min(allv)}..{max(allv)}")
check("most pairs get on, but not all", st.mean(1 if v > 0 else 0 for v in allv) > 0.6 and any(v < 0 for v in allv),
      f"{sum(v > 0 for v in allv)}/{len(allv)} positive, {sum(v < -40 for v in allv)} below -40")
check("the two sides can disagree about how it is going", sum(1 for _, a, b in ps if a != b) > len(ps) * 0.8)
check("pairs differ widely (some great, some bitter)", st.pstdev(allv) > 15, f"sd {st.pstdev(allv):.1f}")

# the head coach, the GM and the CEO are each shown the relationship at their own decisions
for kind in ("scheme_veto", "coord_review", "hire_coordinator", "staff_review", "gm_draft_pick"):
    n, shown = spy.kinds.get(kind, [0, 0])
    check(f"{kind}: shown the relationship", n > 0 and shown >= 0.9 * n, f"{shown}/{n}")

# the meter responds to the club's fortunes and to scheme fit
class T:  # a synthetic club
    pass


def synth(L, win):
    t = next(x for x in L.teams if x.coach is not None and x.gm is not None and x.status == "active")
    return t


L2, _, _ = play(5, 1)
t = synth(L2, 0)
kc, kg = f"coach:{t.coach.cid}", f"gm:{t.gm.gid}"
for rel in (t.gm.relationships, t.coach.relationships):
    for k in list(rel):
        if k in (kc, kg):
            rel[k] = 0
hi, lo = [], []
for y in range(100, 140):
    for pct, bucket in ((0.9, hi), (0.1, lo)):
        t.gm.relationships[kc] = 0
        t.scheme_fit = {}
        RL.season(L2, y, {tm.id: (pct if tm.id == t.id else 0.5) for tm in L2.teams})
        bucket.append(t.gm.relationships[kc])
check("a winning club warms the pair and a losing one cools it", st.mean(hi) > st.mean(lo) + 10, f"{st.mean(hi):.1f} vs {st.mean(lo):.1f}")
fit_hi, fit_lo = [], []
sch = list((t.scheme or {"offense": "balanced"}).values()) or ["balanced"]
for y in range(100, 140):
    for fv, bucket in ((1.0, fit_hi), (-1.0, fit_lo)):
        t.gm.relationships[kc] = 0
        t.scheme = {"offense": "pass"}
        t.scheme_fit = {"pass": fv}
        RL.season(L2, y, {tm.id: 0.5 for tm in L2.teams})
        bucket.append(t.gm.relationships[kc])
check("a roster that suits the schemes warms the pair; one that fights them cools it", st.mean(fit_hi) > st.mean(fit_lo) + 6, f"{st.mean(fit_hi):.1f} vs {st.mean(fit_lo):.1f}")
a = RL.season(L2, 200, {})
check("the season reports counts", set(a) == {"pairs", "started"})

# clicking and grating temperaments
c, g = t.coach, t.gm
c.trait, g.trait = "Players' Coach", "Loyal Lieutenant"
up = RL._affinity(c, g)
c.trait, g.trait = "Disciplinarian", "Dealmaker"
down = RL._affinity(c, g)
check("some temperaments click and some grate", up > 0 > down)

# autopilot output unchanged, private streams only
La, ra, resa = play(21, 3)
Lb, rb, resb = play(21, 3, patch=True)
sig = lambda L, r, res: (r.random(), [(x.champion if hasattr(x, "champion") else None) for x in res], [round(t.strength, 6) for t in L.teams])
check("the relationship changes nothing the engine does, and uses no engine randomness", sig(La, ra, resa) == sig(Lb, rb, resb))

# determinism and the store
Lc, rc, _ = play(21, 3)
check("replaying a seed gives the same relationships", [(a, b) for _, a, b in pairs(La)] == [(a, b) for _, a, b in pairs(Lc)])
with tempfile.TemporaryDirectory() as d:
    db = os.path.join(d, "l.db")
    store.save(db, La, ra, 3)
    Ld, _, _ = store.load(db)
    check("the relationships survive saving and loading", [(a, b) for _, a, b in pairs(La)] == [(a, b) for _, a, b in pairs(Ld)])

# views
t = next(t for t, a, b in pairs(La) if a is not None)
vg, vc = RL.view(t, "gm"), RL.view(t, "coach")
check("each seat is shown her own side, as a label and a score", set(vg) == {"how_you_get_on", "score"} and set(vc) == {"how_you_get_on", "score"})
check("the head coach's note says the GM has no say in coaching and neither is obliged", "neither" in RL.gm_note(t)["your_gm"]["note"] and "no say" in RL.gm_note(t)["your_gm"]["note"])
t0 = next(x for x in La.teams if x.status == "active")
saved = t0.gm
t0.gm = None
check("no GM, no view", RL.view(t0, "coach") == {} and RL.pair_view(t0) == {} and RL.gm_note(t0)["your_gm"] == "none at present")
t0.gm = saved

print("\n" + ("ALL PASS" if not failures else f"{len(failures)} FAILED: {failures}"))
sys.exit(1 if failures else 0)
