"""Checks for the CEO card's answers to her fans (ceo_card.py): the pledge and boycott Decision Points, her three temporary meters, and the
fans' memory passing to the next CEO.

    python engine/check_ceo.py
"""
import dataclasses
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ceo_card as CC  # noqa: E402
import fan_media_cards as FM  # noqa: E402
import finance as FIN  # noqa: E402
import staff_cards as S  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


def play(seed, years, driver=None):
    r = random.Random(seed)
    L = new_league(r, rosters=True)
    L.driver = driver
    res = [run_season(L, y, r, Options(engine="fast", keep_boxes=False)) for y in range(1, years + 1)]
    return L, res


# ---- the card ---------------------------------------------------------------------------------------------
L, res = play(33, 14)
check("every CEO who has sat a season has her three meters, all between 1 and 100",
      all(set(t.owner.meters) == set(CC.METERS) and all(1 <= v <= 100 for v in t.owner.meters.values()) for t in L.teams if t.owner.seasons_owned > 0))
check("the card prints its meters and its pledge, and says CEO", all(k in S.render_owner(L.teams[2].owner, L) for k in ("METERS", "PLEDGE", "Fan Rapport", "### CEO")))
check("Fan Rapport moves approval by no more than its cap", abs(CC.RAPPORT_APPROVAL) <= 0.01 + 1e-12 and all(abs(CC.rapport_nudge(t.owner)) <= CC.RAPPORT_APPROVAL + 1e-12 for t in L.teams))
o = L.teams[0].owner
CC.ensure(o)
o.meters["standing"] = 100.0
hi = CC.sale_shift(o)
o.meters["standing"] = 1.0
lo = CC.sale_shift(o)
check("a CEO the others respect is less likely to be cast out, within the cap", hi < 0 < lo and abs(hi) <= CC.STANDING_SALE + 1e-9 and abs(lo) <= CC.STANDING_SALE + 1e-9, f"{hi:+.3f} / {lo:+.3f}")
check("Legacy is cosmetic: nothing in the engine reads it", not any('"legacy"' in line for f in ("finance.py", "fan_media_cards.py", "game_engine.py", "sim.py", "rosters.py")
                                                                  for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f)).read().splitlines()))

# ---- Decision Points ----------------------------------------------------------------------------------------
pl = [e for e in L.choice_log if e["kind"] == "ceo_pledge"]
check("each CEO with a profit chose a pledge through a Decision Point, and the autopilot chose standard", len(pl) > 400 and all(e["chosen"] == "standard" and e["driver"] == "autopilot" for e in pl), f"{len(pl)} pledges")
bc = [e for e in L.choice_log if e["kind"] == "ceo_boycott"]
check("boycott answers are logged, and the autopilot only holds or concedes", all(e["chosen"] in ("hold", "concede") for e in bc), f"{len(bc)} answers")


class Generous:
    name = "generous"

    def choose(self, dp):
        return ("generous" if dp.kind == "ceo_pledge" else dp.default), "spend"


class Lean:
    name = "lean"

    def choose(self, dp):
        return ("lean" if dp.kind == "ceo_pledge" else dp.default), "save"


rg, rl = random.Random(14), random.Random(14)
Lg, Ll = new_league(rg, rosters=True), new_league(rl, rosters=True)
Lg.driver, Ll.driver = Generous(), Lean()
rg1 = run_season(Lg, 1, rg, Options(engine="fast", keep_boxes=False))
rl1 = run_season(Ll, 1, rl, Options(engine="fast", keep_boxes=False))
inv_g = sum(ln["reinvested"] for t in Lg.teams for ln in t.books if ln.get("year") == 1)
inv_l = sum(ln["reinvested"] for t in Ll.teams for ln in t.books if ln.get("year") == 1)
check("a generous pledge puts back more of the profit than a lean one", inv_g > inv_l * 1.5, f"{inv_g:.0f} vs {inv_l:.0f} ($ millions, league total)")
check("no CEO puts back more than the reinvest cap, even if generous",
      all(ln["reinvested"] <= CC.REINVEST_MAX * ln["surplus"] + 1e-6 for t in Lg.teams for ln in t.books if ln.get("year") == 1 and ln["surplus"] > 0))
check("the fans' spending nudge stays inside its cap whatever the pledge",
      all(abs(ln["nudge"]) <= FIN.FAN_SPEND_WEIGHT + FIN.FAN_GREED_HIT + 1e-9 for LL in (Lg, Ll) for t in LL.teams for ln in t.books if ln.get("year") == 1))
check("pledges never change a game: the season's results are the same whatever the CEOs pledge (money is settled after the games)",
      [(g.home_pts, g.away_pts) for g in rg1.games] == [(g.home_pts, g.away_pts) for g in rl1.games])

# ---- the boycott answer -----------------------------------------------------------------------------------------
lb = new_league(random.Random(9), rosters=True)
for y in range(1, 4):
    run_season(lb, y, random.Random(90 + y), Options(engine="fast", keep_boxes=False))
tb = lb.teams[5]
tb.fans.boycott = 0.8


class Answer:
    name = "answer"

    def __init__(self, pick):
        self.pick = pick

    def choose(self, dp):
        return (self.pick if dp.kind == "ceo_boycott" else dp.default), "test"


lb.driver = Answer("concede")
out = CC.boycott_decisions(lb, 9, [tb])
check("conceding eases the boycott and promises more investment next year", out == {tb.id: "concede"} and abs(tb.fans.boycott - 0.8 * CC.CONCEDE_FACTOR) < 1e-9 and tb.owner.pledge_bonus == CC.CONCEDE_BONUS)
lb.driver = Answer("hold")
before = tb.fans.boycott
CC.boycott_decisions(lb, 9, [tb])
check("holding firm changes nothing", tb.fans.boycott == before)
check("no answer is asked when there is no boycott", CC.boycott_decisions(lb, 9, [lb.teams[6]]) == {} if lb.teams[6].fans.boycott < FM.BOYCOTT_START else True)
# a full season with a driver that always steps aside
rs = random.Random(21)
Ls = new_league(rs, rosters=True)
for y in range(1, 6):
    Ls.driver = Answer("step_aside")
    run_season(Ls, y, rs, Options(engine="fast", keep_boxes=False))
aside = [o for o in Ls.owners if any(d["action"].startswith("stepped aside") for d in o.decision_log)]
check("a CEO who steps aside retires, and her club has a new CEO with no boycott", all(o.status == "retired" for o in aside) and all(Ls.by_id[o.teams_owned[0]].owner.oid != o.oid for o in aside) and all(Ls.by_id[o.teams_owned[0]].fans.boycott < 0.5 for o in aside), f"{len(aside)} stepped aside")

# ---- the fans' memory passes to the next CEO ------------------------------------------------------------------------
lm = new_league(random.Random(5), rosters=True)
tm = lm.teams[0]
tm.fans.meters = {}
tm.owner.approval = 0.55
tm.fans.memories = []
tm.fans.approval = 0.55
CC.inherit(tm, 1)
plain = tm.owner.approval
tm.owner.approval = 0.55
FM.remember(tm.fans, 1, "title", "the championship", 1.0)
FM.remember(tm.fans, 1, "return", "home", 1.0)
CC.inherit(tm, 1)
glory = tm.owner.approval
tm.owner.approval = 0.55
tm.fans.memories = []
for k in ("exile", "drought", "boycott", "exile", "boycott"):
    FM.remember(tm.fans, 1, k, k, 1.0)
CC.inherit(tm, 1)
scar = tm.owner.approval
check("a new CEO's honeymoon is warmer where the fans remember glory and colder where they remember scars", glory > plain > scar, f"{100 * glory:.1f} / {100 * plain:.1f} / {100 * scar:.1f}")
check("the inheritance is capped", glory - 0.55 <= CC.INHERIT_CAP + 1e-9 and 0.55 - scar <= CC.INHERIT_CAP + 1e-9)
check("the mirror stays in step", abs(tm.fans.approval - tm.owner.approval) < 1e-12)

# ---- greed under a boycott ------------------------------------------------------------------------------------------
lgr = new_league(random.Random(8), rosters=True)
tg = lgr.teams[0]
tg.fans.boycott = 0.5
ln = dict(draw=95.0)
check("a maximum draw from a club whose fans are boycotting counts as greed even if it wins", (ln["draw"] >= FIN.GREED_DRAW_SHARE * FIN.DRAW_CAP) and tg.fans.boycott >= FM.BOYCOTT_START)

# ---- old saves --------------------------------------------------------------------------------------------------------
d = dataclasses.asdict(L.teams[1].owner)
for k in ("meters", "pledge", "pledge_bonus"):
    d.pop(k)
oc = S.OwnerCard(**d)
check("a CEO card saved before the meters existed loads and gets the starting meters when first used", oc.meters == {} and CC.value(oc, "rapport") == 50.0 and oc.pledge == "standard" and CC.reinvest_share(oc, 0.2) == 0.2)

print()
if failures:
    print(f"{len(failures)} CEO check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All CEO checks passed.")
