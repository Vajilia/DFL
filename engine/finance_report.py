"""Club finance report: what the money layer does over long leagues (writes reports/finance_report.md).

    python engine/finance_report.py [--leagues 3] [--seasons 40]
"""
import argparse
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import finance as F  # noqa: E402
from league import new_league  # noqa: E402
from season import Options, run_season  # noqa: E402

BURN = 8


def one(seed, seasons):
    rng = random.Random(seed)
    lg = new_league(rng, rosters=True)
    recs, sold, votes = [], 0, 0
    for y in range(1, seasons + 1):
        o = run_season(lg, y, rng, Options(engine="fast", keep_boxes=False)).offseason
        if y > BURN:
            recs.append(o["finance"])
            sold += len(o["forced_sales"])
            votes += sum(1 for l in o["finance"]["lines"].values() if "sale_votes" in l)
    tenures = [x.seasons_owned for x in lg.owners if x.status == "retired" and x.tenure > 0 and x.age < 85]
    return recs, sold, votes, tenures


ap = argparse.ArgumentParser()
ap.add_argument("--leagues", type=int, default=3)
ap.add_argument("--seasons", type=int, default=40)
a = ap.parse_args()
allrecs, sold, votes, tenures = [], 0, 0, []
for s in range(a.leagues):
    r, so, v, t = one(101 + s, a.seasons)
    allrecs += r
    sold += so
    votes += v
    tenures += t
lines = [l for r in allrecs for l in r["lines"].values()]
n_years = len(allrecs)
sur = sorted(l["surplus"] for l in lines)
draws = [l["draw"] for l in lines]
md = "# Club finance\n\n"
md += (f"{a.leagues} leagues x {a.seasons} seasons, fast engine, autopilot, first {BURN} seasons dropped. Every dollar level is a model dial "
       f"(finance.py); the draw cap ($100M), the 10 to 20 year tenure, the 34% ticket pool and the forced-sale vote are the Commissioner's rules.\n\n")
md += "## Revenue and surplus\n\n"
md += (f"Mean revenue {st.mean(l['national'] + l['local'] for l in lines):.0f}M a club; mean surplus {st.mean(sur):.0f}M (lowest {sur[0]:.0f}M, "
       f"10th percentile {sur[len(sur) // 10]:.0f}M, 90th {sur[9 * len(sur) // 10]:.0f}M, highest {sur[-1]:.0f}M). "
       f"{100 * sum(1 for l in lines if l['loss'] > 0) / len(lines):.1f}% of club-seasons end in a loss.\n\n")
md += "## The CEO's draw and the Fund\n\n"
md += (f"Mean draw {st.mean(draws):.0f}M. {100 * sum(1 for l in lines if l['to_fund'] > 0) / len(lines):.1f}% of club-seasons hit the $100M cap "
       f"({sum(1 for l in lines if l['to_fund'] > 0)} of {len(lines)}); the excess sent to the Equalization Fund averages "
       f"{st.mean(r['to_fund'] for r in allrecs):.1f}M a season across the league.\n\n")
md += "## Subsidies and forced sales\n\n"
md += (f"Subsidies from CEOs' draws average {st.mean(r['subsidy'] for r in allrecs):.1f}M a season; CEOs put {st.mean(r['own_pocket'] for r in allrecs):.1f}M "
       f"a season of their own money into clubs the reserve and subsidies could not cover. {votes} forced-sale votes were called in {n_years} league-seasons; "
       f"{sold} owners were forced to sell.\n\n")
md += "## Tenure\n\n"
md += (f"{len(tenures)} CEOs completed their tenure: average {st.mean(tenures):.1f} seasons (shortest {min(tenures)}, longest {max(tenures)}). "
       f"Recalls and forced sales end tenures early and are not counted here.\n" if tenures else "No CEO completed a tenure in this run.\n")
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "finance_report.md")
open(path, "w").write(md)
print(md)
