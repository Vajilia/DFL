"""A compact fingerprint of a league's whole history, used to prove that a change to the code leaves every outcome alone.

    python engine/fingerprint.py [--seeds 33,5] [--seasons 40]     prints a hash per seed
"""
import hashlib
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402


def fingerprint_of(lg, results) -> str:
    h = hashlib.sha256()
    for r in results:
        h.update(repr((r.year, r.champion, tuple(r.new_exiles), tuple(sorted(r.returners)),
                       tuple(sorted((tid, round(float(s.pct), 6)) for tid, s in r.stats.items())),
                       tuple(r.staff["recalled"]), tuple(r.staff["coach_fired"]), tuple(r.staff["gm_fired"]),
                       tuple(sorted((tid, round(a, 6)) for tid, a in r.staff["approval"].items())))).encode())
    h.update(repr([(t.id, t.coach.name, t.gm.name, t.owner.name, round(t.strength, 5)) for t in lg.teams]).encode())
    return h.hexdigest()[:16]


def run(seed: int, seasons: int, **kw):
    rng = random.Random(seed)
    lg = new_league(rng, rosters=True, **kw)
    res = [run_season(lg, y, rng, Options(engine="fast", keep_boxes=False)) for y in range(1, seasons + 1)]
    return lg, res, rng


if __name__ == "__main__":
    seeds = [int(x) for x in (sys.argv[sys.argv.index("--seeds") + 1] if "--seeds" in sys.argv else "33,5").split(",")]
    seasons = int(sys.argv[sys.argv.index("--seasons") + 1]) if "--seasons" in sys.argv else 40
    for s in seeds:
        lg, res, _ = run(s, seasons)
        print(s, seasons, fingerprint_of(lg, res))
