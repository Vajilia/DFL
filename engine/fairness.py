"""Fair competitiveness: the standard every test in this project is judged against.

Jeph's rule (2026-10-04): a trend is a problem when it falls outside the expected / accepted range of
"fair competitiveness". The ranges themselves live in rules.FAIR_COMPETITION_BANDS (ASSUMED until Jeph
sets numbers). This module measures a simulated league history and says which trends are inside the bands.

    python engine/fairness.py [--engine fast] [--leagues 8] [--seasons 48]
"""
from __future__ import annotations

import argparse
import os
import random
import statistics as st
import sys
from collections import Counter, defaultdict
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules as R  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

BURN = 8          # seasons thrown away while the league settles out of its artificial starting point


def _corr(xs: List[float], ys: List[float]) -> float:
    if len(xs) < 3:
        return float("nan")
    mx, my = st.mean(xs), st.mean(ys)
    sx = sum((x - mx) ** 2 for x in xs) ** 0.5
    sy = sum((y - my) ** 2 for y in ys) ** 0.5
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def measure_league(seed: int, seasons: int, engine: str = "fast", opt: Options = None, burn: int = BURN, coaches: bool = True) -> Dict[str, float]:
    """Run one league and return its fairness measurements (after the warm-up)."""
    rng = random.Random(seed)
    lg = new_league(rng, rosters=(engine != "placeholder"), coaches=coaches)
    opt = opt or Options(engine=engine, keep_boxes=False)
    sd_by_season, close, games_n = [], 0, 0
    x_prev, y_next = [], []
    prev_pct: Dict[int, float] = {}
    champs, repeat, top_wins, top_n = [], 0, 0, 0
    ret_fin: List[int] = []
    prev_returners: List[int] = []
    finishes: Dict[int, List[int]] = defaultdict(list)
    stuck, stuck_n = 0, 0
    hist = []
    leg = dict(seasons=0, wins=0.0, playoffs=0, titles=0, seasons_all=0, titles_total=0)
    for y in range(1, seasons + 1):
        strengths = {tid: v[2] for tid, v in lg.snapshot().items()}
        legends = {t.id for t in lg.teams if t.coach is not None and t.coach.legend and t.status == "active"}
        res = run_season(lg, y, rng, opt)
        pct = {tid: float(s.pct) for tid, s in res.stats.items()}
        hist.append(dict(start=strengths, ranks=res.division_ranks, pick={t: p for p, t, _ in res.draft}, new=res.new_exiles))
        if y > burn:
            sd_by_season.append(st.pstdev(pct.values()))
            in_po = {t for seeds in res.seeds.values() for t in seeds}
            leg["seasons_all"] += 1
            for tid in legends:
                if tid in pct:
                    leg["seasons"] += 1
                    leg["wins"] += pct[tid]
                    leg["playoffs"] += tid in in_po
                    leg["titles"] += tid == res.champion
            for g in res.games:
                close += abs(g.home_pts - g.away_pts) <= 8
                games_n += 1
            for tid, p in pct.items():
                if tid in prev_pct:
                    x_prev.append(prev_pct[tid]); y_next.append(p)
            if champs:
                repeat += res.champion == champs[-1]
            champs.append(res.champion)
            top = max((tid for tid in pct), key=lambda t: strengths[t])
            top_wins += res.champion == top
            top_n += 1
            for ranks in res.division_ranks.values():
                ret_fin += [ranks.index(t) + 1 for t in prev_returners if t in ranks]
            for ranks in res.division_ranks.values():
                for pos, tid in enumerate(ranks, start=1):
                    h = finishes[tid]
                    if len(h) >= 3:
                        stuck_n += 1
                        stuck += all(f >= 4 for f in h[-3:])
                    h.append(pos)
        else:
            if y == burn:                       # start the finish history with a settled league
                pass
            for ranks in res.division_ranks.values():
                for pos, tid in enumerate(ranks, start=1):
                    finishes[tid].append(pos)
        prev_pct = pct
        prev_returners = res.returners
    # titles in any 20-season stretch
    win = 20
    worst = 0
    for i in range(0, max(1, len(champs) - win + 1)):
        worst = max(worst, max(Counter(champs[i:i + win]).values()))
    n_ret = len(ret_fin)
    # exile effect: 4th and 5th place teams in year i, their rating at the start of year i + 2
    xs, ys, five = [], [], []
    early, n_new = 0, 0
    for i in range(burn, len(hist)):
        if i + 2 < len(hist):
            for ranks in hist[i]["ranks"].values():
                for pos in (4, 5):
                    t = ranks[pos - 1]
                    xs.append(hist[i]["start"][t]); ys.append(hist[i + 2]["start"][t]); five.append(1.0 if pos == 5 else 0.0)
        if i + 1 < len(hist):
            for t in hist[i]["new"]:
                n_new += 1
                early += hist[i]["pick"][t] <= 8 and hist[i + 1]["pick"][t] <= 16
    return {
        "win_pct_sd": st.mean(sd_by_season),
        "year_to_year_corr": _corr(x_prev, y_next),
        "close_game_share": close / games_n,
        "repeat_champion_rate": repeat / max(1, len(champs) - 1),
        "max_titles_in_20": worst,
        "worst_league_titles": worst,
        "best_team_title_odds": top_wins / top_n,
        "returner_avg_finish": st.mean(ret_fin),
        "returner_win_div": sum(f == 1 for f in ret_fin) / n_ret,
        "returner_fifth_again": sum(f == 5 for f in ret_fin) / n_ret,
        "stuck_at_bottom": stuck / max(1, stuck_n),
        "exile_double_early": early / max(1, n_new),
        "_xy": (xs, ys, five),
        "_legend": leg,
        "_n_returners": n_ret,
    }


def evaluate(per_league: List[Dict[str, float]]):
    """Pool the leagues. Returns [(name, value, low, high, ok, spread_low, spread_high, meaning)]."""
    rows = []
    # the exile effect is a regression, so pool the raw samples from every league
    import numpy as np
    xs = sum((d["_xy"][0] for d in per_league), []); ys = sum((d["_xy"][1] for d in per_league), [])
    fv = sum((d["_xy"][2] for d in per_league), [])
    A = np.column_stack([np.ones(len(xs)), xs, fv])
    pooled_effect = float(np.linalg.lstsq(A, np.array(ys), rcond=None)[0][2])
    for d in per_league:
        a_ = np.column_stack([np.ones(len(d["_xy"][0])), d["_xy"][0], d["_xy"][2]])
        d["exile_effect"] = float(np.linalg.lstsq(a_, np.array(d["_xy"][1]), rcond=None)[0][2])
    for name, (lo, hi, meaning) in R.FAIR_COMPETITION_BANDS.items():
        vals = [d[name] for d in per_league]
        v = max(vals) if name == "worst_league_titles" else pooled_effect if name == "exile_effect" else st.mean(vals)   # titles: judge the worst league
        rows.append((name, v, lo, hi, lo <= v <= hi, min(vals), max(vals), meaning))
    return rows


def run(engine: str, seeds, seasons: int, **kw):
    per = [measure_league(s, seasons, engine, **kw) for s in seeds]
    return per, evaluate(per)


def table(rows) -> str:
    L = ["| Trend | This league | Fair-competitiveness band | Inside? | Range across leagues |", "| --- | --- | --- | --- | --- |"]
    for name, v, lo, hi, ok, a, b, meaning in rows:
        f = (lambda x: f"{x:.3f}") if name not in ("max_titles_in_20", "worst_league_titles", "returner_avg_finish", "exile_effect") else (lambda x: f"{x:.0f}" if name == "worst_league_titles" else f"{x:.2f}")
        L.append(f"| {meaning} | {f(v)} | {f(lo)} to {f(hi)} | {'yes' if ok else '**NO**'} | {f(a)} to {f(b)} |")
    return "\n".join(L)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="fast")
    ap.add_argument("--leagues", type=int, default=8)
    ap.add_argument("--seasons", type=int, default=48)
    ap.add_argument("--write", action="store_true", help="write reports/fairness_report.md (fast and drive engines)")
    a = ap.parse_args()
    if a.write:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out = ["# Fair competitiveness report\n",
               "Standard (Jeph, 2026-10-04): a trend is a problem when it falls outside the expected / accepted range of "
               "\"fair competitiveness\". The numeric ranges below are the AI's first proposal and are **assumed** until you set "
               "your own (`FAIR_COMPETITION_BANDS` in `engine/rules.py`). Each league runs 48 seasons; the first 8 are thrown "
               "away while the league settles. Values are averaged over the leagues; the last column shows the spread.\n"]
        for eng, n in (("fast", 8), ("drives", 5)):
            per, rows = run(eng, range(100, 100 + n), 48)
            bad = [r[0] for r in rows if not r[4]]
            out.append(f"## {eng} engine, {n} leagues x 48 seasons\n")
            out.append(table(rows))
            out.append("\n" + ("All trends inside the bands.\n" if not bad else f"Outside the bands: {', '.join(bad)}.\n"))
        open(os.path.join(root, "reports", "fairness_report.md"), "w").write("\n".join(out))
        print("wrote reports/fairness_report.md")
        sys.exit(0)
    per, rows = run(a.engine, range(100, 100 + a.leagues), a.seasons)
    print(table(rows))
    bad = [r[0] for r in rows if not r[4]]
    print("\nAll trends inside the fair-competitiveness bands." if not bad else f"\nOUTSIDE the bands: {', '.join(bad)}")
    sys.exit(1 if bad else 0)
