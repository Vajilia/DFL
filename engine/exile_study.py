"""Does exile pay? A sensitivity study.

Question: for a team of a given strength, is it better off finishing 5th (exiled) or 4th?

Method: simulate many leagues. For every division and season, take the team that finished
4th and the team that finished 5th, group them by how strong they were at kickoff (so a
strong 4th is only compared with a similarly strong 5th), and follow both for the next
four seasons. Differences are 5th-place (exiled) minus 4th-place.

IMPORTANT: draft value and cap relief are PLACEHOLDER numbers (placeholder_model.py), so
the study sweeps them instead of trusting one guess. Owner recall, revenue and fan capital
are not modelled yet, so the true cost of exile is bigger than this study can show.

    python engine/exile_study.py            (full study, a few minutes)
    python engine/exile_study.py --quick    (small, for testing)
"""
import argparse
import itertools
import math
import os
import random
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import placeholder_model as PM  # noqa: E402
import rules as R  # noqa: E402
from run_sim import simulate  # noqa: E402
from season import Options  # noqa: E402

OUTCOMES = ["talent_at_return", "wins_4yr", "playoffs_4yr", "titles_4yr", "exiled_again", "seasons_played"]
NICE = {
    "talent_at_return": "Team strength two seasons later (points)",
    "wins_4yr": "Regular-season wins over the next 4 seasons",
    "playoffs_4yr": "Playoff appearances over the next 4 seasons",
    "titles_4yr": "Championships over the next 4 seasons",
    "exiled_again": "Chance of being exiled again within 4 seasons",
    "seasons_played": "Seasons actually played out of the next 4",
}
BIN_W = 1.0
NBINS = 17            # strength bins from -8 to +8
HORIZON = 4
BURN = 5


def league_table(results):
    """bins x group(0=4th,1=5th) x (count + outcomes)"""
    tab = np.zeros((NBINS, 2, 1 + len(OUTCOMES)))
    Y = len(results)
    for y in range(BURN + 1, Y - HORIZON + 1):
        res = results[y - 1]
        for ranks in res.division_ranks.values():
            for grp, tid in ((0, ranks[3]), (1, ranks[4])):
                s0 = res.start[tid][2]
                b = int(min(NBINS - 1, max(0, math.floor(s0 / BIN_W) + NBINS // 2)))
                wins = played = playoffs = titles = again = 0
                for k in range(1, HORIZON + 1):
                    fut = results[y - 1 + k]
                    if tid in fut.stats:
                        wins += fut.stats[tid].wins
                        played += 1
                    if tid in fut.exits:
                        playoffs += 1
                        titles += fut.exits[tid] == "champion"
                    if k >= 2 and tid in fut.new_exiles:
                        again = 1
                talent = results[y - 1 + 2].start[tid][2]
                tab[b, grp, 0] += 1
                tab[b, grp, 1:] += (talent, wins, playoffs, titles, again, played)
    return tab


def run_config(args):
    pool, pick1, bonus, leagues, seasons, seed0 = args
    model = PM.Model(draft_pick1_value=pick1, exile_return_bonus=bonus)
    opt = Options(model=model, lottery_pool=pool, validate_schedule=False)
    tabs = []
    for i in range(leagues):
        _, res = simulate(seed0 + i, seasons, opt)
        tabs.append(league_table(res))
    return (pool, pick1, bonus), np.array(tabs)


def stratified_diff(tabs):
    """tabs: (L, bins, 2, 1+K) -> difference (5th minus 4th) for each outcome."""
    t = tabs.sum(axis=0)
    n4, n5 = t[:, 0, 0], t[:, 1, 0]
    w = np.minimum(n4, n5)
    w = np.where(w >= 10, w, 0)
    if w.sum() == 0:
        return np.full(len(OUTCOMES), np.nan)
    m4 = t[:, 0, 1:] / np.maximum(n4, 1)[:, None]
    m5 = t[:, 1, 1:] / np.maximum(n5, 1)[:, None]
    return ((m5 - m4) * w[:, None]).sum(axis=0) / w.sum()


def with_ci(tabs, boots=300, seed=0):
    rng = np.random.default_rng(seed)
    point = stratified_diff(tabs)
    L = len(tabs)
    samples = np.array([stratified_diff(tabs[rng.integers(0, L, L)]) for _ in range(boots)])
    lo, hi = np.nanpercentile(samples, [2.5, 97.5], axis=0)
    return point, lo, hi


def fmt(x, digits=2):
    return f"{x:+.{digits}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--reuse", action="store_true", help="rebuild the report from the saved simulation results")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports"))
    args = ap.parse_args()
    leagues, seasons = (6, 16) if args.quick else (40, 30)
    pools = ["just_finished_fifth", "just_finished_exile"]
    pick1s = [0.0, 1.0, 2.0, 3.0, 4.5, 6.0]
    bonuses = [0.0, 0.5, 1.0, 2.0, 3.0]
    jobs = [(p, v, b, leagues, seasons, 1000) for p in pools for v in pick1s for b in bonuses]
    results = {}
    cache = os.path.join(args.out, ".exile_study_cache.npz")
    if args.reuse and os.path.exists(cache):
        z = np.load(cache, allow_pickle=True)
        results = {tuple(k): v for k, v in zip(z["keys"], z["tabs"])}
        results = {(k[0], float(k[1]), float(k[2])): v for k, v in results.items()}
        print("reused cached simulation results")
    else:
        with ProcessPoolExecutor(max_workers=2) as ex:
            for key, tabs in ex.map(run_config, jobs):
                results[key] = tabs
                print("done", key, flush=True)
        if not args.quick:
            os.makedirs(args.out, exist_ok=True)
            keys = np.empty(len(results), dtype=object)
            tabs_arr = np.empty(len(results), dtype=object)
            for i, (k, v) in enumerate(results.items()):
                keys[i], tabs_arr[i] = k, v
            np.savez(cache, keys=keys, tabs=tabs_arr)

    base_key = ("just_finished_fifth", PM.DRAFT_PICK1_VALUE, PM.EXILE_RETURN_BONUS)
    out = []
    ap_ = out.append
    ap_("# Does exile pay? Placeholder-model study\n")
    ap_(f"*{leagues} simulated leagues x {seasons} seasons for each of {len(jobs)} settings. "
        f"Every number is a difference: **team that finished 5th (and was exiled) minus team that finished 4th**, "
        f"comparing teams of similar strength. Positive means exile left the team better off.*\n")
    ap_("**Read this first.** Draft value and cap relief are placeholder guesses, so this report shows how the answer changes "
        "as those guesses change. It cannot say whether your final design is right. Owner recall, revenue and fan capital are "
        "not simulated yet, so the real cost of exile is larger than anything shown here.\n")
    ap_("## With the current placeholder settings\n")
    ap_(f"Lottery for teams that just finished 5th. A pick-1 draft pick is worth {PM.DRAFT_PICK1_VALUE:+.1f} points of team "
        f"strength; coming back from exile is worth {PM.EXILE_RETURN_BONUS:+.1f} points. These settings were calibrated so a returning "
        f"team averages roughly 3rd-to-4th in its division (exile as help, not punishment; see exile_calibration.md).\n")
    pt, lo, hi = with_ci(results[base_key])
    ap_("| Measure (exiled minus 4th place) | Difference | 95% range |")
    ap_("| --- | --- | --- |")
    for i, name in enumerate(OUTCOMES):
        d = 3 if name in ("exiled_again",) else 2
        ap_(f"| {NICE[name]} | {fmt(pt[i], d)} | {fmt(lo[i], d)} to {fmt(hi[i], d)} |")
    ap_("")

    def grid(pool, idx, title, digits=2):
        ap_(f"### {title}\n")
        ap_("Rows: how much a pick-1 draft pick is worth. Columns: how much cap relief is worth on return.\n")
        ap_("| pick-1 value \\ cap relief | " + " | ".join(f"{b:+.1f}" for b in bonuses) + " |")
        ap_("| --- | " + " | ".join("---" for _ in bonuses) + " |")
        for v in pick1s:
            row = []
            for b in bonuses:
                p, l, h = with_ci(results[(pool, v, b)], boots=100)
                cell = fmt(p[idx], digits)
                if not (l[idx] <= 0 <= h[idx]):
                    cell += " *"
                row.append(cell)
            ap_(f"| {v:+.1f} | " + " | ".join(row) + " |")
        ap_("\n`*` = clearly different from zero (95% range excludes zero).\n")

    ix = {n: i for i, n in enumerate(OUTCOMES)}
    ap_("## How the answer changes with the placeholder guesses\n")
    for pool, label in ((pools[0], "Lottery for the 8 teams that just finished 5th"),
                        (pools[1], "Lottery for the 8 teams that just served their exile year")):
        ap_(f"## {label}\n")
        grid(pool, ix["playoffs_4yr"], "Playoff appearances over the next 4 seasons (exiled minus 4th)")
        grid(pool, ix["talent_at_return"], "Team strength two seasons later, in points (exiled minus 4th)")
        grid(pool, ix["exiled_again"], "Chance of being exiled again within 4 seasons (exiled minus 4th)", 3)

    # what this means
    ap_("## What this means\n")
    per_point = 0.3989 / PM.MARGIN_SD * R.GAMES_PER_TEAM
    ix_p = ix["playoffs_4yr"]
    bp, bl, bh = with_ci(results[base_key])
    verdict = ("roughly breaks even" if bl[ix_p] <= 0 <= bh[ix_p]
               else "comes out ahead" if bp[ix_p] > 0 else "comes out behind")
    ap_(f"- **Scale.** One point of team strength is worth about {per_point:.1f} wins over an 18-game season, "
        f"so a pick-1 value of 3 points is about {3 * per_point:.1f} extra wins a year.")
    ap_(f"- **With today's placeholder settings**, a team that finishes 5th {verdict} against one that finishes 4th on playoff "
        f"appearances over four seasons ({fmt(bp[ix_p])}, range {fmt(bl[ix_p])} to {fmt(bh[ix_p])}), even though it sits out a whole "
        f"season. It returns {bp[ix['talent_at_return']]:.1f} points stronger and is {abs(bp[ix['exiled_again']]) * 100:.0f} percentage point"
        f"{'' if round(abs(bp[ix['exiled_again']]) * 100) == 1 else 's'} "
        f"{'less' if bp[ix['exiled_again']] < 0 else 'more'} likely to be exiled again.")
    base0 = with_ci(results[(pools[0], 0.0, 0.0)])[0][ix_p]
    ap_(f"- **With both benefits at zero**, exile costs {abs(base0):.2f} playoff appearances per four seasons. That is the true price "
        f"of the lost season on the field.")
    for pool, label in ((pools[0], "lottery for teams that just finished 5th"), (pools[1], "lottery for teams that just served exile")):
        parts = []
        for b in bonuses:
            ds = [with_ci(results[(pool, v, b)], boots=100)[0][ix_p] for v in pick1s]
            cross = None
            if ds[0] >= 0:
                cross = 0.0
            else:
                for i in range(1, len(ds)):
                    if ds[i] >= 0 > ds[i - 1]:
                        cross = pick1s[i - 1] + (0 - ds[i - 1]) / (ds[i] - ds[i - 1]) * (pick1s[i] - pick1s[i - 1])
                        break
            parts.append(f"cap relief {b:+.1f}: " + ("none needed" if cross == 0.0 else
                                                      f"pick-1 worth about {cross:.1f}" if cross is not None else "not reached by 6.0"))
        ap_(f"- **Break-even ({label}).** Exile matches finishing 4th on playoff appearances when " + "; ".join(parts) + ".")
    ap_("- **The dial that matters** is how big the draft and cap-relief benefits are compared with the cost of a lost season. "
        "Nothing here says which setting is right; it shows where the line is.")
    ap_("- **Not modelled yet:** owner recall, lost revenue and fan capital, and what characters choose to do. "
        "Those are the real costs of exile and they only appear once the character cards exist.\n")
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, "exile_study.md" if not args.quick else "exile_study_quick.md")
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
