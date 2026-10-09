"""Do the fairness bands hold whatever the agents choose?

Same leagues and seeds in every row; only who makes the CEO's keep/fire/hire choices changes. The first row is the autopilot (the
rules as they were before agents). The others are random-legal play and four adversaries that use the TRUE state to push staff
quality to the legal limit (see adversaries.py). The question for every row: does any trend leave its band?
Writes reports/decision_fairness_study.md.

    python engine/decision_sweep.py [--leagues 8] [--seasons 48] [--only A,B]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adversaries as ADV  # noqa: E402
import agents as AG  # noqa: E402
import decisions as D  # noqa: E402
import fairness  # noqa: E402
from coach_sweep import footprint  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__)).rsplit(os.sep, 1)[0]

VARIANTS = [
    ("A. Autopilot (the rules as they were before agents)", lambda: D.PolicyDriver()),
    ("B. Random legal choices", lambda: D.RandomLegalDriver(7)),
    ("C. Nobody is ever fired", lambda: ADV.StandPat()),
    ("D. Worst case: every CEO fires everyone every year and hires the truly best candidate", lambda: ADV.ChurnOracle()),
    ("E. Worst case: only the 8 strongest teams churn and hire perfectly", lambda: ADV.EliteOracle(8)),
    ("F. Worst case: the 8 strongest hire the best, the 8 weakest the worst, every year", lambda: ADV.Polarized(8)),
    ("G. Worst case: everyone hunts for the most famous coach", lambda: ADV.StarHunter()),
    ("H. Worst case: every CEO recycles the same people between jobs", lambda: ADV.CarouselRider()),
]

# the stand-in agent (agents.py) reads only what a real agent is shown; a dozen at a time through the real pool
AGENT_VARIANTS = [
    ("A. Autopilot (the rules as they were before agents)", lambda: D.PolicyDriver()),
    ("I. A stand-in agent in all 48 CEOs' seats (cards decide, a dozen at a time)", lambda: D.AgentDriver(AG.StandIn(), workers=12)),
    ("J. Agents in 12 seats (every fourth team), the autopilot in the other 36", lambda: AG.seats(range(1, 49, 4), AG.StandIn())),
    ("K. The same agent, but a quarter of its answers are lost or invalid (the autopilot steps in)", lambda: D.AgentDriver(AG.Flaky(AG.StandIn(), every=4), workers=12)),
    ("L. Worst case at the interview table: the 8 strongest hire the best and guarantee her three seasons, the 8 weakest hire the worst on no guarantee", lambda: ADV.LockIn(8)),
    ("M. Every candidate refuses every job (the league office fills every seat by the old rule)", lambda: ADV.EveryoneWalks()),
    ("N. Hard bargaining: every candidate asks for the most and walks without it, every CEO holds the line", lambda: ADV.HardBargain()),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leagues", type=int, default=8)
    ap.add_argument("--seasons", type=int, default=48)
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--agents", action="store_true", help="the stand-in agent rows instead of the adversary rows")
    a = ap.parse_args()
    variants = AGENT_VARIANTS if a.agents else VARIANTS
    keep = {x.strip() for x in a.only.split(",") if x.strip()}
    if a.agents:
        out = ["# Agents in the CEOs' seats: fairness with a stand-in agent\n",
               "A stand-in agent (agents.py) reads only the view a real agent would be shown (the deciding card, her notes, the options with the ratings "
               "she perceives) and chooses from the engine's options; CEOs with different personalities choose differently. It is a rulebook, not a "
               "model, so this tests the machinery and the bands, not the quality of a real agent's judgment. Rows: all 48 seats, a dozen seats, and "
               "an agent whose answers are often lost or invalid.\n"]
    else:
      out = ["# Whatever the agents choose: fairness under the worst legal play\n",
           "The principle: the road has guardrails and traffic controls, the character card is the driver, and what the driver does with the car "
           "always stays inside the fair-competitiveness bands. The first CEO choice to go through a Decision Point is keep, fire or hire "
           "for the coach and the GM (the hire is one of three candidates). The autopilot row reproduces the league as it was before agents. "
           "The other rows replace the CEOs' choices with random play and with adversaries that see the TRUE ratings of every candidate "
           "(no real agent can) and play the legal limit. Everything they do is a legal option; the guard would reject anything else.\n"]
    for label, mk in variants:
        if keep and label[0] not in keep:
            continue
        per, rows = fairness.run("fast", range(100, 100 + a.leagues), a.seasons, driver=mk())
        bad = [r[0] for r in rows if not r[4]]
        out.append(f"## {label}\n")
        out.append(f"fast engine, {a.leagues} leagues x {a.seasons} seasons.\n")
        out.append(fairness.table(rows))
        out.append("\n" + ("All trends inside the bands.\n" if not bad else f"**Outside the bands:** {', '.join(bad)}.\n"))
        out.append(footprint(per) + "\n")
        v = {r[0]: r[1] for r in rows}
        print("    ", footprint(per), flush=True)
        print(label, "->", "ALL INSIDE" if not bad else "OUTSIDE: " + "; ".join(bad), flush=True)
        print("    title conc:", round(v["max_titles_in_20"], 2), v["worst_league_titles"], " corr:", round(v["year_to_year_corr"], 3),
              " best-team odds:", round(v["best_team_title_odds"], 3), " repeat:", round(v["repeat_champion_rate"], 3),
              " stuck:", round(v["stuck_at_bottom"], 3), " exile fx:", round(v["exile_effect"], 2), flush=True)
    path = a.out or os.path.join(ROOT, "reports", "agent_fairness_study.md" if a.agents else "decision_fairness_study.md")
    open(path, "w").write("\n".join(out))
    print("wrote", path)


if __name__ == "__main__":
    main()
