"""Payroll and cap report: what the pay scale and the cap rules do over long leagues (writes reports/cap_report.md).

    python engine/economy_report.py [--leagues 4] [--seasons 48]
"""
import argparse
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import economy as EC  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

BURN = 8


def one(seed, seasons):
    rng = random.Random(seed)
    lg = new_league(rng, rosters=True)
    pays, banks, below, at_limit, star_share = [], [], 0, 0, []
    cuts = blocked = resigned = desg = 0
    for y in range(1, seasons + 1):
        res = run_season(lg, y, rng, Options(engine="fast", keep_boxes=False))
        o = res.offseason or {}
        if y > BURN:
            cuts += o.get("cap_cuts", 0)
            desg += o.get("designated", 0)
            blocked += o.get("cap_blocked", 0)
            resigned += o.get("resigned", 0)
            for t in lg.teams:
                p = EC.payroll(t)
                pays.append(p)
                banks.append(t.bank)
                below += p < EC.floor()
                at_limit += p >= EC.limit(t) - 0.5
                top = sorted((q.salary for q in t.roster), reverse=True)[:5]
                star_share.append(sum(top) / p)
    caps = [e for e in lg.archive if e["event"] == "cap_close" and e["year"] > BURN]
    return dict(pays=pays, banks=banks, below=below / len(pays), at_limit=at_limit / len(pays), star_share=st.mean(star_share),
                forfeited=st.mean(e["forfeited"] for e in caps), shortfall=st.mean(e["shortfall"] for e in caps), levy=st.mean(e["levy"] for e in caps), payout=st.mean(e["payout"] for e in caps), dead=st.mean(e["dead_mean"] for e in caps),
                absorbed=st.mean(e["absorbed"] for e in caps), pool=lg.pool, cuts=cuts / (seasons - BURN), blocked=blocked / (seasons - BURN),
                resigned=resigned / (seasons - BURN), designated=desg / (seasons - BURN))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leagues", type=int, default=4)
    ap.add_argument("--seasons", type=int, default=48)
    a = ap.parse_args()
    rs = [one(s, a.seasons) for s in range(300, 300 + a.leagues)]
    pays = sum((r["pays"] for r in rs), [])
    banks = sum((r["banks"] for r in rs), [])
    q = st.quantiles(pays, n=20)
    m = lambda k: st.mean(r[k] for r in rs)  # noqa: E731
    out = ["# Payroll and the cap\n",
           f"{a.leagues} leagues x {a.seasons} seasons, fast engine, autopilot, first {BURN} seasons dropped. Every number is the AI's placeholder "
           "pay scale (economy.py); the rules ($100M cap that never inflates, $125M most a team may go into a season with, 90% floor over four seasons, exiled "
           "teams' payroll counted at half) are the Commissioner's.\n",
           "## Where payrolls sit\n",
           f"Mean payroll {st.mean(pays):.1f}M of the $100M cap; the middle 90% of team-seasons run {q[0]:.1f}M to {q[-1]:.1f}M. "
           f"{100 * m('below'):.1f}% of team-seasons end below the 90% floor and {100 * m('at_limit'):.1f}% end at their limit. "
           f"The five best-paid players take {100 * m('star_share'):.0f}% of a team's payroll on average.\n",
           "## Banked room\n",
           f"A team carries on average {st.mean(banks):.1f}M of banked room into a season (most possible 25M); "
           f"{100 * sum(b >= 24.99 for b in banks) / len(banks):.0f}% of team-seasons begin with the full 25M and "
           f"{100 * sum(b < 0.01 for b in banks) / len(banks):.0f}% with none.\n",
           "## Dead money\n",
           f"A team carries on average {m('dead'):.1f}M of dead money (bonus and guaranteed pay of players it let go); {m('designated'):.1f} cuts a season use one of the "
           "two post-draft designations that split the hit across two seasons.\n",
           "## The Equalization Fund\n",
           f"Each season the Fund takes in {m('forfeited'):.0f}M of forfeited room and pays out the league's half of exiled teams' payroll, {m('absorbed'):.0f}M. "
           f"In a year it falls short the 48 teams cover it equally (an average levy of {m('levy'):.0f}M a season); above its {EC.FUND_RESERVE:.0f}M reserve the surplus goes equally to the "
           f"teams that played (an average of {m('payout'):.0f}M a season). Floor top-ups paid to players average {m('shortfall'):.1f}M a season across the league.\n",
           "## What the cap costs teams\n",
           f"Each season the league re-signs {m('resigned'):.0f} expiring players, loses {m('blocked'):.1f} it could not afford to keep, "
           f"and teams that spent banked room cut {m('cuts'):.1f} contracts to get back under the cap.\n"]
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "cap_report.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
