"""Injuries during the game (rules version 4, 2026-10-14): a player is hurt on a play, leaves, and the best healthy player at her position takes over.
Rules 1 to 3 keep the old after-the-game roll and must come out exactly as before (check_clock.py holds their fingerprints).

    python engine/check_ingame_injuries.py
"""
import collections
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import game_engine as GE
import injuries as IJ
import site_export
from league import new_league
from season import Options, run_season

failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


d4, d3 = site_export.export(7, 4), site_export.export(7, 3)
c = collections.Counter()
for gid, b in d4["box"].items():
    pl, ps = b["pl"], b["p"]
    gone = {}
    for i, p in enumerate(ps):
        k = p[6]
        if k == "IJ":
            c["ij"] += 1
            a, s, kind = p[7], p[8], p[9]
            if not (a >= 0 and s >= 0 and pl[a][1] == pl[s][1] and pl[a][2] == pl[s][2] and a != s):
                c["bad_pair"] += 1                                 # the player who comes in plays the same position for the same club
            if not (0 <= kind < len(IJ.KIND_NAMES)):
                c["bad_kind"] += 1
            if a in gone:
                c["twice"] += 1
            gone[a] = i
        elif k in ("RU", "PC", "PI", "SK", "IN", "FG", "PU", "SP", "KN"):
            for who in (p[7], p[8], p[9]) if k not in ("FG", "PU") else (p[7],):
                if who in gone:
                    c["after_leaving"] += 1                        # a player who left is never in a later play of the game
    c["games"] += 1
check("rules 4: players are hurt in games, about three a game", 2.0 <= c["ij"] / c["games"] <= 5.0, f"{c['ij'] / c['games']:.2f}")
check("rules 4: the player who comes in has the same position and club, and the injury is one of the table's", c["bad_pair"] == 0 and c["bad_kind"] == 0, str(c))
check("rules 4: nobody is hurt twice in a game, and nobody plays after leaving", c["twice"] == 0 and c["after_leaving"] == 0, str(c))
check("rules 3 has no injuries in the log", all(p[6] != "IJ" for b in d3["box"].values() for p in b["p"]))

# scoring and the usual counts are not disturbed by the new rule
def per(d, k):
    return sum(1 for b in d["box"].values() for p in b["p"] if p[6] == k) / len(d["box"])
check("rules 4: penalties and scoring stay in their usual range", abs(per(d4, "PN") - per(d3, "PN")) < 1.5 and abs(per(d4, "TO") - per(d3, "TO")) < 1.5, f"{per(d3, 'PN'):.2f} {per(d4, 'PN'):.2f}")
pts = lambda d: st.mean(g["hp"] + g["ap"] for g in d["games"])
check("rules 4: scoring per game stays within two points of rules 3", abs(pts(d4) - pts(d3)) < 2.0, f"{pts(d3):.1f} {pts(d4):.1f}")

# a season: the league's injury list is the game's, at the old model's rate
rng = random.Random(33)
lg = new_league(rng, rosters=True)
ev, conc = [], []
for y in range(1, 5):
    res = run_season(lg, y, rng, Options(engine="drives", keep_boxes=False, engine_params=GE.EngineParams(rules=4)))
    if y > 1:
        rn = res.runner
        ev.append(len(rn.injury_log) / 48)
        conc.append(sum(1 for x in rn.injury_log if x[4] == IJ.CONCUSSION) / 48)
        check(f"rules 4: year {y}: every injury in the log has a player out for at least a game", all(x[3] >= 1 for x in rn.injury_log))
check("rules 4: injuries per club per season are near the NFL's 30", 25 <= st.mean(ev) <= 42, f"{st.mean(ev):.1f}")
check("rules 4: concussions per club are 1.5 to 4 a season", 1.5 <= st.mean(conc) <= 4, f"{st.mean(conc):.1f}")

# the same seed gives the same games
a, b = site_export.export(7, 4)["box"], d4["box"]
check("rules 4: the same seed gives the same games", a == b)

print("\n%d failed" % len(failures) if failures else "\nall passed")
sys.exit(1 if failures else 0)
