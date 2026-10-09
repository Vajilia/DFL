"""Practice-squad elevations: up to 2 a game, 3 a season per player, only to fill a position below its game-day minimum, back to the squad after.

    python engine/check_elevations.py
"""
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rosters  # noqa: E402
import rules as R  # noqa: E402
from league import new_league  # noqa: E402
from positions import ACTIVE_MINIMUMS, ROSTER_SIZE  # noqa: E402
from season import Options, run_season  # noqa: E402

failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


# ---- the rule on a hand-built case ---------------------------------------------------------------------------------
rng = random.Random(4)
lg = new_league(rng, rosters=True)
t = lg.teams[0]
ol = [p for p in t.roster if p.pos == "OL"]
for p in ol[:4]:
    p.weeks_out = 2                                                  # five healthy OL left; the game-day minimum is 7
ps_ol = [p for p in t.practice_squad if p.pos == "OL"]
if not ps_ol:
    q = next(p for p in t.practice_squad)
    q.pos = "OL"
    ps_ol = [q]
up = rosters.elevate(t)
check("a position below its game-day minimum gets practice-squad help", len(up) >= 1 and all(p in t.practice_squad for p in up))
check("never more than 2 in a game", len(up) <= R.PRACTICE_ELEVATIONS_MAX_GAME)
check("the elevated player is on the game-day list", all(p in rosters.game_roster(t) for p in up))
check("elevated players stay on the practice squad (not the 53)", all(p not in t.roster for p in up) and len(t.roster) == ROSTER_SIZE)
check("no more than 48 are active on game day", len(rosters.active_list(t)) <= R.ACTIVE_LIMIT)
check("each use is counted against the player", all(p.elevations == 1 for p in up))
for p in ol[:4]:
    p.weeks_out = 0
t.elevated = []
check("a healthy team elevates no one", rosters.elevate(t) == [])
star = ps_ol[0]
star.elevations = R.PRACTICE_ELEVATIONS_MAX_PLAYER
for p in ol[:4]:
    p.weeks_out = 2
check("a player already elevated 3 times is not elevated again", star not in rosters.elevate(t))
for p in ol[:4]:
    p.weeks_out = 0
star.elevations = 0
t.elevated = []

# ---- seasons ----------------------------------------------------------------------------------------------------------
for engine in ("fast", "drives"):
    r = random.Random(11)
    L = new_league(r, rosters=True)
    res = run_season(L, 1, r, Options(engine=engine, keep_boxes=False))
    log = res.runner.elevation_log
    per_game = Counter((w, tid) for w, tid, *_ in log)
    per_player = Counter(pid for _, _, pid, *_ in log)
    team_games = 18 * len(L.teams)
    check(f"[{engine}] practice-squad players are elevated in a season", len(log) > 0, f"{len(log)} call-ups, {len(log) / team_games:.2f} per team-game")
    check(f"[{engine}] at most 2 per team per game", max(per_game.values(), default=0) <= 2)
    check(f"[{engine}] no player more than 3 times", max(per_player.values(), default=0) <= R.PRACTICE_ELEVATIONS_MAX_PLAYER)
    check(f"[{engine}] call-ups are an occasional fix, well under one per team-game", len(log) / team_games < 0.6)
    check(f"[{engine}] practice squads are full again after the offseason", all(len(t.practice_squad) == R.PRACTICE_SQUAD_SIZE for t in L.teams))
    check(f"[{engine}] counts reset for the new season", all(p.elevations == 0 for t in L.teams for p in t.roster + t.practice_squad))
    check(f"[{engine}] no elevation list is left over", all(not t.elevated for t in L.teams))

print()
if failures:
    print(f"{len(failures)} elevation check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All elevation checks passed.")
