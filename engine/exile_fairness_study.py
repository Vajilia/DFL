"""How should an exiled team's two drafts work so exile stays fair?

Compares draft variants on the roster model (fast engine) and writes reports/exile_two_draft_study.md.

    python engine/exile_fairness_study.py [--leagues 6] [--seasons 48]

Measures, for each variant:
  * where a team back from exile finishes (target: about 3rd, so 2.8 to 3.4);
  * the exile effect: does finishing 5th leave a team better off two years later than finishing 4th would have?
    (regression of team rating at the start of year Y+2 on rating in year Y and a 5th-place flag);
  * stacking: the picks an exiled team holds in its two drafts, and how often both are early;
  * tank stakes: how much draft position hangs on the Ambassador Season.
"""
import argparse
import os
import random
import statistics as st
import sys
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules as R  # noqa: E402
from league import new_league  # noqa: E402
from roster_model import RosterModel  # noqa: E402
from season import Options, run_season  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BURN = 8

# (draft options, premium signings per returning team)
VARIANTS = {
    "A. Lottery for new exiles; returners mixed into the band by Ambassador record (Phase 1 way), 0.25 premium signings":
        (dict(lottery_pool="just_finished_fifth", returner_slot="by_record"), 0.25),
    "B. Lottery for new exiles; returners as a block at the end of the band, 0.25 premium signings":
        (dict(lottery_pool="just_finished_fifth", returner_slot="end_of_band"), 0.25),
    "C. Lottery for new exiles; returners as a block at the start of the band, 0.25 premium signings":
        (dict(lottery_pool="just_finished_fifth", returner_slot="start_of_band"), 0.25),
    "D. Lottery for returners after the exile year; new exiles pick by record, 0.25 premium signings":
        (dict(lottery_pool="just_finished_exile", returner_slot="by_record"), 0.25),
    "E. Same as B with no premium signings (the lottery pick is the only help)":
        (dict(lottery_pool="just_finished_fifth", returner_slot="end_of_band"), 0.0),
    "F. RECOMMENDED: same as B with 0.05 premium signings":
        (dict(lottery_pool="just_finished_fifth", returner_slot="end_of_band"), 0.05),
}


def run_variant(opts: dict, seeds, seasons, premium=None):
    rm = RosterModel() if premium is None else RosterModel(exile_premium_signings=premium)
    fin_back = []
    X, Y_, F5, Fy = [], [], [], []
    picks_Y, picks_Y1, both_early, both_top12 = [], [], 0, 0
    n_ex = 0
    stakes = []
    ret_finish_4th = []
    for sd in seeds:
        rng = random.Random(sd)
        lg = new_league(rng, rosters=True)
        hist = []                                   # per season: dict(start ratings, ranks, draft pick of each team, returners)
        for y in range(1, seasons + 1):
            r = run_season(lg, y, rng, Options(engine="fast", keep_boxes=False, roster_model=rm, **opts))
            hist.append(dict(start={t: v[2] for t, v in r.start.items()}, ranks=r.division_ranks,
                             pick={t: p for p, t, _ in r.draft}, returners=r.returners, new=r.new_exiles))
        for i, h in enumerate(hist):
            if i < BURN:
                continue
            # where did last year's returners finish
            if i >= 1:
                for ranks in h["ranks"].values():
                    fin_back += [ranks.index(t) + 1 for t in hist[i - 1]["returners"] if t in ranks]
            # exile effect: 4th and 5th place finishers in year i, rating at the start of year i+2
            if i + 2 < len(hist):
                for ranks in h["ranks"].values():
                    for pos in (4, 5):
                        t = ranks[pos - 1]
                        X.append(h["start"][t]); Y_.append(hist[i + 2]["start"][t]); F5.append(1.0 if pos == 5 else 0.0)
                        # finish in year i+2 (None if exiled that year)
                        for rk in hist[i + 2]["ranks"].values():
                            if t in rk:
                                Fy.append((pos, rk.index(t) + 1))
            # stacking: the new exiles' pick this year and their pick next year
            if i + 1 < len(hist):
                for t in h["new"]:
                    picks_Y.append(h["pick"][t]); picks_Y1.append(hist[i + 1]["pick"][t])
                    n_ex += 1
                    both_early += h["pick"][t] <= 8 and hist[i + 1]["pick"][t] <= 16
                    both_top12 += h["pick"][t] <= 12 and hist[i + 1]["pick"][t] <= 12
            # stakes of the Ambassador Season: best-ranked vs worst-ranked returner's pick next draft
            ps = sorted(h["pick"][t] for t in h["returners"])
            stakes.append(ps[-1] - ps[0])
    A = np.column_stack([np.ones(len(X)), X, F5])
    coef, *_ = np.linalg.lstsq(A, np.array(Y_), rcond=None)
    resid = np.array(Y_) - A @ coef
    cov = np.linalg.inv(A.T @ A) * resid.var(ddof=3)
    se = float(np.sqrt(cov[2, 2]))
    f4 = [f for p, f in Fy if p == 4]
    f5 = [f for p, f in Fy if p == 5]
    return dict(
        finish=st.mean(fin_back), win=sum(f == 1 for f in fin_back) / len(fin_back),
        fifth=sum(f == 5 for f in fin_back) / len(fin_back),
        effect=float(coef[2]), effect_se=se,
        f4=st.mean(f4), f5=st.mean(f5), n4=len(f4), n5=len(f5),
        pick_Y=st.mean(picks_Y), pick_Y1=st.mean(picks_Y1),
        both_early=both_early / n_ex, both_top12=both_top12 / n_ex,
        stakes=st.mean(stakes),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leagues", type=int, default=6)
    ap.add_argument("--seasons", type=int, default=48)
    a = ap.parse_args()
    seeds = range(300, 300 + a.leagues)
    rows = {}
    for name, (opts, prem) in VARIANTS.items():
        rows[name] = run_variant(opts, seeds, a.seasons, prem)
        print(name, {k: round(v, 3) for k, v in rows[name].items()}, flush=True)
    L = ["# Exile and the two drafts: variant study\n",
         f"Roster model, fast engine, {a.leagues} leagues x {a.seasons} seasons (first {BURN} thrown away). All numbers come from "
         "placeholder dials. \"Exile effect\" is in team-rating points (about 1 point of margin per point; roughly half a win over 18 games).\n",
         "| Variant | Returner avg finish | Wins division | 5th again | Exile effect (rating pts, +/- 1 se) | Finish 2 yrs on: was 4th / was 5th | "
         "Pick in draft 1 / draft 2 | Early in both drafts (top 8 then top 16) | Ambassador stakes (pick gap) |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for name, r in rows.items():
        L.append(f"| {name} | {r['finish']:.2f} | {100 * r['win']:.0f}% | {100 * r['fifth']:.0f}% | {r['effect']:+.2f} (+/- {r['effect_se']:.2f}) | "
                 f"{r['f4']:.2f} / {r['f5']:.2f} | {r['pick_Y']:.1f} / {r['pick_Y1']:.1f} | {100 * r['both_early']:.0f}% | {r['stakes']:.0f} |")
    L.append('\n## How to read this\n\n- **Exile effect** compares a team that finished 5th with one that finished 4th, both starting year Y with the same rating, and asks how much stronger the exiled team is at the start of year Y+2. Near zero means finishing 5th neither helps nor hurts; a big positive number means teams would rather finish 5th than 4th. Proposed fair band: -0.5 to +0.5 points (`rules.FAIR_COMPETITION_BANDS`).\n- **Early in both drafts** is the share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick the next year.\n- **Ambassador stakes** is the gap in draft position between the best and worst Ambassador Season finisher. A big gap invites tanking a seven-game season. In variant D it is the spread of the lottery itself, not a block, so it is not comparable.\n- The Phase 1 way (A) lets a returning team that happens to have a good Ambassador record also pick early again, which is how about four in ten exiled teams end up with two early picks.\n')
    open(os.path.join(ROOT, "reports", "exile_two_draft_study.md"), "w").write("\n".join(L) + "\n")
    print("wrote reports/exile_two_draft_study.md")


if __name__ == "__main__":
    main()
