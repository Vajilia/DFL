"""Checks for hiring (Step 8b): the two-interview rule and the demographics audit, plus staff pay limits.

The rulebook (Skeleton): no decision, agent or text can read a character's demographics (names and portraits only); every head-coach or GM search
interviews at least two external candidates; an audit fails if any outcome depends on demographics. The engine holds no demographic fields at all, so
the audit is two tests: a schema scan for any such field, and a name-blind replay (the same league with every name changed must play out identically).

    python engine/check_hiring.py
"""
import dataclasses
import hashlib
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as C  # noqa: E402
import economy as EC  # noqa: E402
import fan_media_cards as FM  # noqa: E402
import players as PL  # noqa: E402
import rules as R  # noqa: E402
import staff_cards as SC  # noqa: E402
import staff_pay as SP  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


# ---- 1. no demographic field exists anywhere
FORBIDDEN = ("race", "racial", "ethnic", "gender", "sex", "religion", "orientation", "disability", "nationality", "skin", "pronoun", "portrait", "complexion")
classes = [C.CoachCard, SC.OwnerCard, SC.GMCard, FM.FanbaseCard, FM.MediaCard, PL.Player]
bad = [(c.__name__, f.name) for c in classes for f in dataclasses.fields(c) if any(w in f.name.lower() for w in FORBIDDEN)]
check("no card or player has a demographic field", not bad, str(bad))
import card_pools as CP  # noqa: E402
pool_names = [n for n in dir(CP) if n.isupper() and isinstance(getattr(CP, n), (list, tuple, dict))]
check("the card pools hold no demographic pool", not [n for n in pool_names if any(w in n.lower() for w in FORBIDDEN)])
check("the decision views offer only the rating names of the role (no demographic attribute)",
      not [a for a in SC.COACH_VIEW + tuple(SC.GM_ATTRS) if any(w in a for w in FORBIDDEN)])


# ---- 2. the name-blind replay: change every name, replay, and nothing but the names may differ
def outcome_hash(lg, results) -> str:
    h = hashlib.sha256()
    for r in results:
        h.update(repr((r.year, r.champion, tuple(r.new_exiles), tuple(sorted(r.returners)),
                       tuple(sorted((tid, round(float(s.pct), 6)) for tid, s in r.stats.items())),
                       tuple(r.staff["recalled"]), tuple(r.staff["coach_fired"]), tuple(r.staff["gm_fired"]),
                       tuple(sorted((tid, round(a, 6)) for tid, a in r.staff["approval"].items())))).encode())
    h.update(repr([(t.id, t.coach.cid, t.gm.gid, t.owner.oid, round(t.strength, 5)) for t in lg.teams]).encode())
    h.update(repr(sorted((p.id, p.pos, round(p.ovr, 3), p.team_id) for p in lg.free_agents)).encode())
    return h.hexdigest()[:16]


def replay(seed, seasons, shift):
    original = C.make_name

    def shifted(s, n):
        F, L = len(CP.FIRST_NAMES), len(CP.LAST_NAMES)
        first, last = original(s + shift, n * 3 + shift)
        return last, first               # a different name, even a different order
    C.make_name = shifted if shift else original
    try:
        rng = random.Random(seed)
        lg = new_league(rng, rosters=True)
        res = [run_season(lg, y, rng, Options(engine="fast", keep_boxes=False)) for y in range(1, seasons + 1)]
        names = [t.owner.name for t in lg.teams]
        return outcome_hash(lg, res), names, lg
    finally:
        C.make_name = original


for seed in (33, 5):
    h0, n0, lg0 = replay(seed, 25, 0)
    h1, n1, _ = replay(seed, 25, 12345)
    h2, n2, _ = replay(seed, 25, 777)
    check(f"seed {seed}: the names really did change in the replays", n0 != n1 and n0 != n2)
    check(f"seed {seed}: with every name changed, 25 seasons of outcomes are identical (nothing depends on a name)", h0 == h1 == h2, f"{h0} {h1} {h2}")
    if seed == 33:
        base = lg0


# ---- 3. the interview rule
hires = [(c, e) for c in list(base.coaches) + list(base.gms) for e in c.career if e.get("event") == "hired" and "interviews" in e]
check("there were hires to audit", len(hires) > 50, f"{len(hires)}")
check("every search interviewed at least two external candidates", all(e["interviews"] >= R.EXTERNAL_INTERVIEWS_MIN for _, e in hires))
interviewed = [e for c in list(base.free_coaches) + list(base.free_gms) + list(base.passed_over) for e in c.career if e.get("event") == "interviewed"]
check("courtesy interviews were recorded on the candidates", len(interviewed) > 0, f"{len(interviewed)}")
check("every candidate interviewed was not already working for the club that interviewed her",
      all(c.team_id != e["team"] for c in list(base.free_coaches) + list(base.free_gms) + list(base.passed_over) for e in c.career if e.get("event") == "interviewed"))

# ---- 4. staff pay limits
one, total_max = EC.STAFF_CONTRACT_MAX_PCT * EC.CAP, EC.STAFF_PAYROLL_MAX_PCT * EC.CAP
pays = [SP.staff_payroll(t) for t in base.teams]
check("no staff contract is above 8% of the cap", all(p["coach"] <= one + 1e-9 and p["gm"] <= one + 1e-9 for p in pays), f"max coach {max(p['coach'] for p in pays):.2f}M")
check("no club's football staff is above 20% of the cap", all(p["total"] <= total_max + 1e-9 for p in pays), f"max {max(p['total'] for p in pays):.2f}M")
check("a better coach is paid more", SP.coach_pay_raw(sorted((t.coach for t in base.teams), key=lambda c: sum(c.ratings.values()))[-1])
      > SP.coach_pay_raw(sorted((t.coach for t in base.teams), key=lambda c: sum(c.ratings.values()))[0]))
t0 = base.teams[0]
saved = SP.COACH_MAX_RAW
SP.COACH_MAX_RAW = 40.0
try:
    t0.coach.ratings = {k: 100.0 for k in t0.coach.ratings}
    capped = SP.staff_payroll(t0)
    check("an over-limit coach contract is clamped to $8M and the guard reports it", abs(capped["coach"] - one) < 1e-9 and capped["clamped"] >= 1, str(capped))
    SP.ASSISTANTS_BASE = 40.0
    capped = SP.staff_payroll(t0)
    check("an over-limit staff total is clamped to $20M by cutting the assistants", abs(capped["total"] - total_max) < 1e-6, str(capped))
finally:
    SP.COACH_MAX_RAW = saved
    SP.ASSISTANTS_BASE = 7.0

print()
print("FAILED: " + ", ".join(failures) if failures else "all hiring checks passed")
sys.exit(1 if failures else 0)
