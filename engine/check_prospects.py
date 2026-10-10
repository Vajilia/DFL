"""Checks for the draft class and every player's origin (prospects.py): the class is a ranked table of real players with colleges, dates of birth,
hometowns and college statistics; the draft picks from it; the league's talent and its random stream are untouched.

    python engine/check_prospects.py
"""
import os
import random
import statistics as st
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as C  # noqa: E402
import decisions as D  # noqa: E402
import economy as EC  # noqa: E402
import offseason as OFF  # noqa: E402
import prospects as PR  # noqa: E402
import rules as R  # noqa: E402
import store  # noqa: E402
from league import new_league  # noqa: E402
from positions import POSITIONS, ROSTER_COUNTS  # noqa: E402
from roster_model import RosterModel  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


# ---- watch every class and every rookie signing in a six-year league ---------------------------------------------------------------------
classes, rookies, ages = [], [], {}
_build, _sign = PR.build_class, EC.sign


def build(lg, rm, rng, year, n):
    rows = _build(lg, rm, rng, year, n)
    classes.append((year, n, list(rows), [(p.pos, p.ovr, p.origin["grade"]) for p in rows]))
    ages.update({p.id: p.age for p in rows})
    return rows


def sign(p, *a, **k):
    if k.get("rookie"):
        rookies.append((p.id, p.draft_pick, p.draft_year, p.pos, p.ovr, p.origin.get("class_rank"), p.team_id))
    return _sign(p, *a, **k)


PR.build_class, EC.sign = build, sign
r = random.Random(33)
L = new_league(r, rosters=True)
for y in range(1, 7):
    run_season(L, y, r, Options(engine="fast", keep_boxes=False))
PR.build_class, EC.sign = _build, _sign

check("a class is built every offseason: the 336 picks plus the compensatory picks, one row per pick", len(classes) == 6 and all(n >= 7 * R.TOTAL_TEAMS and len(rows) == n for _, n, rows, _ in classes),
      [n for _, n, _, _ in classes])
check("every pick takes a different prospect and each class is used up (rookies = picks)", len(rookies) == sum(n for _, n, _, _ in classes) and len({x[0] for x in rookies}) == len(rookies))
ranks = [[p.origin["class_rank"] for p in rows] for _, _, rows, _ in classes]
check("the board is ranked 1..N, and every prospect is on no roster until she is picked", all(rk == list(range(1, len(rk) + 1)) for rk in ranks) and all(p.team_id is None for _, _, rows, _ in classes[-1:] for p in rows if p.id not in {x[0] for x in rookies}))

rows_all = [p for _, _, rows, _ in classes for p in rows]
check("every prospect has an origin: a real college, a tier, a date of birth that matches her age, a hometown and four seasons of statistics",
      all(p.origin["college"] in dict(PR.COLLEGES) and p.origin["tier"] == dict(PR.COLLEGES)[p.origin["college"]] and len(p.origin["stats"]) == 4
          and [s["class_year"] for s in p.origin["stats"]] == list(PR.SEASONS) and int(p.origin["dob"][:4]) == PR.CALENDAR_BASE + y_ - ages[p.id]
          and p.origin["hometown"] in C.CP.HOMETOWNS for (y_, _, rows, _) in classes for p in rows))
check("college statistics are the position's own (a QB has passing numbers, a kicker field goals, a lineman starts)",
      all(("cmp" in p.origin["stats"][0]) == (p.pos == "QB") and ("fg_att" in p.origin["stats"][0]) == (p.pos == "K") and ("starts" in p.origin["stats"][0]) == (p.pos == "OL") for p in rows_all))
check("kickers and punters are not on the top of the board", all(p.origin["class_rank"] > PR.PROD_FLOOR_RANK for p in rows_all if p.pos in ("K", "P")) and any(p.pos in ("K", "P") for p in rows_all))

# production follows the grade: a better prospect has better numbers (the signal a scout reads)
def yds(p):
    return sum(s.get("yds", 0) for s in p.origin["stats"]) if p.pos in ("WR", "RB") else None


wr = [(p.origin["grade"], yds(p)) for p in rows_all if p.pos == "WR"]
hi = [y for g, y in wr if g >= 60]
lo = [y for g, y in wr if g < 45]
check("a higher production grade means more production (wide receivers: yards of the top grades vs the bottom)", len(hi) > 5 and len(lo) > 5 and st.mean(hi) > 2 * st.mean(lo), (round(st.mean(hi)), round(st.mean(lo))))
errs = [g - o for _, _, _, rows in classes for _, o, g in rows]
check("the grade is her true rating plus scouting noise of the dialled size (so a scout can be wrong, but not wildly)", abs(st.mean(errs)) < 0.7 and abs(st.pstdev(errs) - PR.GRADE_SD) < 0.7, (round(st.mean(errs), 2), round(st.pstdev(errs), 2)))
tiers = [p.origin["tier"] for p in rows_all if p.origin["grade"] >= 70]
check("the top prospects come mostly from power programs, with a few from small colleges", tiers and 0.6 < tiers.count(1) / len(tiers) < 0.95 and any(t != 1 for t in tiers), round(tiers.count(1) / len(tiers), 2))
check("a wide spread of colleges: most programs on the list send someone", len({p.origin["college"] for p in rows_all}) > 0.7 * len(PR.COLLEGES), len({p.origin["college"] for p in rows_all}))

# the league's talent is where it has always been: the rating of the pick by round, against the rookie curve
rm, rr = RosterModel(), random.Random(7)
bands = [(1, 10), (11, 32), (33, 96), (97, 200), (201, 400)]
worst = 0.0
for lo_, hi_ in bands:
    got = [x[4] for x in rookies if lo_ <= x[1] <= hi_]
    ref = [OFF.rookie_ovr(pk, rm, rr) for pk in range(lo_, hi_ + 1) for _ in range(30)]
    worst = max(worst, abs(st.mean(got) - st.mean(ref)))
check("the rating of the player taken at each stage of the draft matches the rookie curve the league has always had (within 2.5 points on the autopilot)", worst < 2.5, round(worst, 2))
check("the draft takes the board in order, near enough: the average distance between a pick and her board rank is small", st.mean(abs(x[1] - x[5]) for x in rookies) < 25 and st.mean(x[1] - x[5] for x in rookies) < 10,
      (round(st.mean(abs(x[1] - x[5]) for x in rookies), 1), round(st.mean(x[1] - x[5] for x in rookies), 1)))
mix = {p: sum(1 for x in rookies if x[3] == p) / len(rookies) for p in POSITIONS}
check("the positions drafted follow the roster's proportions (within 4 points each) and no kicker or punter goes in the first 100",
      all(abs(mix[p] - ROSTER_COUNTS[p] / 53) < 0.04 for p in POSITIONS) and not any(x[3] in ("K", "P") and x[1] <= 100 for x in rookies), {k: round(v, 3) for k, v in mix.items()})

# ---- the origin comes from private streams ---------------------------------------------------------------------------------------------------
q = random.Random(9)
Lq = new_league(q, rosters=True)
state = q.getstate()
for t in Lq.teams[:4]:
    for p in t.roster:
        PR.ensure_origin(Lq.card_seed, p, 3)
check("looking up a player's college never touches the engine's random stream", q.getstate() == state)
a = PR.make_origin(Lq.card_seed, Lq.teams[0].roster[0], 3)
check("the same player always has the same origin, in any order of asking", a == PR.make_origin(Lq.card_seed, Lq.teams[0].roster[0], 3) and a["dob"][:4] == str(PR.CALENDAR_BASE + 3 - Lq.teams[0].roster[0].age))
check("a founding veteran gets an origin the first time one is needed, from her rating (and it is kept)", all(p.origin for t in Lq.teams[:4] for p in t.roster) and Lq.teams[0].roster[0].origin == PR.ensure_origin(Lq.card_seed, Lq.teams[0].roster[0], 99))

# ---- cards and the save ----------------------------------------------------------------------------------------------------------------------
drafted = [p for t in L.teams for p in t.roster if p.draft_year and p.card is not None]
check("a player's card takes her hometown and date of birth from her origin, and has a bio only if one was written (first two rounds, or asked for)",
      drafted and all(p.card.hometown == p.origin["hometown"] and p.card.dob == p.origin["dob"] and (p.card.bio != "") == (p.card.enriched != "") for p in drafted)
      and all(p.card.enriched == "code" for p in drafted if p.draft_year == 6 and p.draft_pick <= 96) and all(p.card.enriched == "" for p in drafted if p.draft_pick > 96 and p.draft_year == 6))
path = os.path.join(tempfile.mkdtemp(), "prospects.db")
store.save(path, L, r, 6)
L2, _, _ = store.load(path)
by1 = {p.id: p for t in L.teams for p in t.roster}
by2 = {p.id: p for t in L2.teams for p in t.roster}
check("origins and the new card fields survive a save and load unchanged", len(by1) == len(by2) and all(by1[i].origin == by2[i].origin and by1[i].card.dob == by2[i].card.dob for i in by1))

# ---- the autopilot is the rule; a GM who overrules it picks another prospect from the same board ---------------------------------------------
class Alt:
    name = "alt"

    def choose(self, dp):
        if dp.kind == "gm_draft_pick":
            return dp.options[-1]["id"], "the alternate"
        return dp.default, "autopilot"


r3 = random.Random(33)
L3 = new_league(r3, rosters=True)
L3.driver = Alt()
for y in range(1, 4):
    run_season(L3, y, r3, Options(engine="fast", keep_boxes=False))
log = [e for e in L3.choice_log if e["kind"] == "gm_draft_pick"]
check("a GM who takes the alternate every time changes the pick without breaking the class (every pick still a different prospect, rosters legal)",
      any(e["chosen"] != e["default"] for e in log) and all(len(t.roster) == R.ROSTER_LIMIT for t in L3.teams))

if failures:
    print(f"\n{len(failures)} FAILED")
    sys.exit(1)
print("\nAll prospect checks passed.")
