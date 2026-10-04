"""Write reports/card_samples.md: sample player and coach cards from a simulated league, plus how the cards
spread across the league.

    python engine/card_report.py [--seed 1] [--seasons 6]
"""
import argparse
import collections
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as C  # noqa: E402
from league import new_league  # noqa: E402
from positions import POSITIONS  # noqa: E402
from season import Options, run_season  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--seasons", type=int, default=6)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    lg = new_league(rng, rosters=True)
    for y in range(1, a.seasons + 1):
        res = run_season(lg, y, rng, Options(engine="fast", keep_boxes=False))
    out = ["# Character cards: samples\n",
           f"Seed {a.seed}, after {a.seasons} seasons. Names, hometowns and backgrounds come from placeholder word lists "
           "(engine/card_pools.py) that you can replace. Ratings, archetypes and the coach effect are real: they come from "
           "the engine. Relationships and the decision log start empty on purpose; the Interaction system will fill them.\n",
           "## How to read a card\n",
           "- **Archetypes** describe the player's rating profile: her best attribute names the positive archetype and her weakest the negative one.",
           "- **Pressure thresholds** (exile, contract, spotlight, loyalty) are how much each kind of pressure rattles her, 1 to 100. They do nothing yet; the Interaction system will use them.",
           "- **Coach ratings**: only offense and defense move games today (capped at +/- 1.0 point of margin each). The other four are stored for later.\n"]
    out.append("## A franchise player at each position group\n")
    active = [p for t in lg.teams for p in t.roster]
    for pos in ("QB", "WR", "OL", "DL", "CB", "K"):
        best = max((p for p in active if p.pos == pos), key=lambda p: p.ovr)
        out.append(render := C.render_player(best, lg))
    out.append("\n## A young rookie and a veteran\n")
    rookies = [p for p in active if p.draft_year == a.seasons]
    if rookies:
        out.append(C.render_player(min(rookies, key=lambda p: p.draft_pick), lg))
    vet = max((p for p in active if p.years_in_league > 8), key=lambda p: p.ovr, default=None)
    if vet:
        out.append(C.render_player(vet, lg))
    out.append("\n## A retired player (cards are kept for the Archive)\n")
    ret = max(lg.retired_players, key=lambda p: p.ovr)
    out.append(C.render_player(ret, lg))
    out.append("\n## Head coaches: the best and the weakest by total on-field effect\n")
    ranked = sorted(lg.teams, key=lambda t: t.coach.offense_points + t.coach.defense_points)
    out.append(C.render_coach(ranked[-1].coach, lg))
    out.append(C.render_coach(ranked[0].coach, lg))
    out.append("\n## How the cards spread across the league\n")
    tc = collections.Counter(p.card.trait for p in active)
    out.append("**Core personalities (all rostered players):** " + ", ".join(f"{k} {v}" for k, v in tc.most_common()) + "\n")
    ac = collections.Counter(C.archetypes(p.pos, p.ratings)[0] for p in active)
    out.append("**Most common positive archetypes:** " + ", ".join(f"{k} {v}" for k, v in ac.most_common(8)) + "\n")
    eff = [t.coach.offense_points + t.coach.defense_points for t in lg.teams]
    out.append(f"**Coach effect across the 48 teams:** average {st.mean(eff):+.2f}, spread (sd) {st.pstdev(eff):.2f}, "
               f"best {max(eff):+.2f}, worst {min(eff):+.2f} points of expected margin. For scale, team talent has a spread of about 3 to 4 points.\n")
    out.append(f"**Coaches so far:** {len(lg.coaches)} hired and {sum(c.retired for c in lg.coaches)} retired in {a.seasons} seasons.\n")
    out.append(f"**Players with cards:** {len(active) + len(lg.free_agents)} active or unsigned, {len(lg.retired_players)} retired.\n")
    path = os.path.join(ROOT, "reports", "card_samples.md")
    open(path, "w").write("\n".join(out))
    print("wrote", path)


if __name__ == "__main__":
    main()
