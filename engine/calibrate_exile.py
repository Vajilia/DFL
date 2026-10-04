"""Calibrate the placeholder exile benefits to Jeph's design intent.

Design intent (Jeph, 2026-10-04): exile is relief, not punishment. A team coming back from
exile should have the potential to compete for 3rd place in its division: sometimes it will
get there, sometimes it won't. That is the level of help exile should give.

This turns the intent into a measurable target (average first-season-back division finish
close to 3.0, with a real spread of outcomes) and searches the placeholder draft-value and
cap-relief numbers for settings that hit it.

    python engine/calibrate_exile.py
"""
import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import placeholder_model as PM  # noqa: E402
import rules as R  # noqa: E402
from run_sim import simulate  # noqa: E402
from season import Options  # noqa: E402

BURN = 5


def return_finishes(results):
    """Division finish (1-5) of every team in its first season back from exile."""
    out, made_playoffs = [], []
    for i, res in enumerate(results[:-1]):
        nxt = results[i + 1]
        if i + 1 < BURN:
            continue
        for tid in res.returners:
            for ranks in nxt.division_ranks.values():
                if tid in ranks:
                    out.append(ranks.index(tid) + 1)
            made_playoffs.append(tid in nxt.exits)
    return out, made_playoffs


def run(args):
    pool, pick1, bonus, leagues, seasons = args
    opt = Options(model=PM.Model(draft_pick1_value=pick1, exile_return_bonus=bonus),
                  lottery_pool=pool, validate_schedule=False)
    finishes, playoffs = [], []
    for s in range(leagues):
        _, res = simulate(7000 + s, seasons, opt)
        f, p = return_finishes(res)
        finishes += f
        playoffs += p
    f = np.array(finishes)
    return (pool, pick1, bonus), {
        "mean": f.mean(), "dist": [float((f == k).mean()) for k in range(1, 6)],
        "playoffs": float(np.mean(playoffs)), "n": len(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports"))
    ap.add_argument("--reuse", action="store_true", help="rebuild the report from the saved simulation results")
    ap.add_argument("--leagues", type=int, default=30)
    ap.add_argument("--seasons", type=int, default=30)
    a = ap.parse_args()
    pools = ["just_finished_fifth", "just_finished_exile"]
    pick1s = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    bonuses = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]
    jobs = [(p, v, b, a.leagues, a.seasons) for p in pools for v in pick1s for b in bonuses]
    res = {}
    cache = os.path.join(a.out, ".exile_calibration.json")
    if a.reuse and os.path.exists(cache):
        import json as _j
        for k, v in _j.load(open(cache)).items():
            p_, v_, b_ = k.split("|")
            res[(p_, float(v_), float(b_))] = v
        print("reused saved results")
    else:
        with ProcessPoolExecutor(max_workers=2) as ex:
            for k, v in ex.map(run, jobs):
                res[k] = v
                print("done", k, f"{v['mean']:.2f}", flush=True)

    L = []
    w = L.append
    w("# Calibrating exile to the design intent\n")
    w("**Design intent (Jeph):** exile is relief, not punishment. A team coming back should have the potential to compete for "
      "**3rd place in its division**. Sometimes it gets there, sometimes it doesn't. Not a lock to contend, not a lock to flop.\n")
    w("**Target used:** average first-season-back division finish close to 3.0 (between 2.8 and 3.2), with every finish from 1st to 5th "
      "still possible. For reference, a team picked at random finishes 3.0 on average and gets exiled 20% of the time.\n")
    w("All numbers below use the placeholder draft-value and cap-relief settings (`engine/placeholder_model.py`). They are tuning dials, "
      "not rules. Each cell is the average first-season-back division finish (1 = division winner, 5 = exiled again).\n")
    for pool, label in ((pools[0], "Lottery for the 8 teams that just finished 5th"),
                        (pools[1], "Lottery for the 8 teams that just served their exile year")):
        w(f"## {label}\n")
        w("| pick-1 value \\ cap relief | " + " | ".join(f"{b:+.1f}" for b in bonuses) + " |")
        w("| --- | " + " | ".join("---" for _ in bonuses) + " |")
        for v in pick1s:
            cells = []
            for b in bonuses:
                m = res[(pool, v, b)]["mean"]
                cells.append(f"**{m:.2f}**" if 2.8 <= m <= 3.2 else f"{m:.2f}")
            w(f"| {v:+.1f} | " + " | ".join(cells) + " |")
        w("\nBold = inside the 2.8 to 3.2 target.\n")
    # recommendation: cells in target, prefer smallest benefit sum
    for pool, label in ((pools[0], "just finished 5th"), (pools[1], "just served exile")):
        hits = [(v, b) for v in pick1s for b in bonuses if 2.8 <= res[(pool, v, b)]["mean"] <= 3.2]
        w(f"## Where the target is met (lottery for teams that {label})\n")
        if not hits:
            w("No combination tested lands inside the target.\n")
            continue
        hits.sort(key=lambda x: abs(res[(pool, *x)]["mean"] - 3.0))
        w("| pick-1 value | cap relief | Average finish | 1st | 2nd | 3rd | 4th | 5th (exiled again) | Made playoffs |")
        w("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for v, b in hits[:6]:
            r = res[(pool, v, b)]
            d = r["dist"]
            w(f"| {v:+.1f} | {b:+.1f} | {r['mean']:.2f} | " + " | ".join(f"{100 * x:.0f}%" for x in d) +
              f" | {100 * r['playoffs']:.0f}% |")
        w("")
    key = (R.LOTTERY_POOL, PM.DRAFT_PICK1_VALUE, PM.EXILE_RETURN_BONUS)
    if key in res:
        r = res[key]
        d = r["dist"]
        w("## Settings now in use\n")
        w(f"The placeholder model currently uses a pick-1 value of {PM.DRAFT_PICK1_VALUE:+.1f} and cap relief of "
          f"{PM.EXILE_RETURN_BONUS:+.1f}. A returning team then averages a {r['mean']:.2f} finish in its division: "
          f"1st {100 * d[0]:.0f}%, 2nd {100 * d[1]:.0f}%, 3rd {100 * d[2]:.0f}%, 4th {100 * d[3]:.0f}%, 5th {100 * d[4]:.0f}%. "
          f"It finishes 3rd or better {100 * sum(d[:3]):.0f}% of the time and makes the playoffs {100 * r['playoffs']:.0f}% of the time. "
          "That is a team with a real chance at 3rd or better but no guarantee, which is how I read the design intent. "
          "Say \"a bit more help\" or \"a bit less\" and I will move the dials.\n")
    w("## Reading this\n")
    w("Many combinations hit the same target, because draft value and cap relief both just add talent. "
      "The choice between them is a story choice, not a math one: put the help in the lottery pick, in cap relief, or split it. "
      "The simulation only needs the total help to be about right.\n")
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "exile_calibration.md")
    open(path, "w").write("\n".join(L) + "\n")
    import json
    json.dump({f"{k[0]}|{k[1]}|{k[2]}": v for k, v in res.items()},
              open(os.path.join(a.out, ".exile_calibration.json"), "w"))
    print("wrote", path)


if __name__ == "__main__":
    main()
