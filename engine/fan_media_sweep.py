"""Do fanbase and media cards keep the league inside the fair-competitiveness bands?

Same leagues and seeds in every row. The first row has owners, GMs and coaches but the old placeholder approval model (no fan
or media cards). The rest turn the fan and media cards on; the last stress rows make the press 3x and 6x stronger and Fan Capital
3x stronger. Writes reports/fan_media_fairness_study.md.

    python engine/fan_media_sweep.py [--leagues 8] [--seasons 48]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fairness  # noqa: E402
import fan_media_cards as FM  # noqa: E402
from coach_sweep import footprint  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__)).rsplit(os.sep, 1)[0]

# (label, fans on?, media sway, capital weight, engine)
VARIANTS = [
    ("A. Old placeholder approval model (owners, GMs and coaches, no fan or media cards)", False, 0.03, 0.30, "fast"),
    ("B. Fanbase and media cards, as built", True, 0.03, 0.30, "fast"),
    ("C. Stress test: the press 3x stronger and Fan Capital 3x stronger", True, 0.09, 0.90, "fast"),
    ("D. Stress test: the press 6x stronger and Fan Capital 6x stronger", True, 0.18, 1.80, "fast"),
    ("E. As built, full drive engine", True, 0.03, 0.30, "drives"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leagues", type=int, default=8)
    ap.add_argument("--drive-leagues", type=int, default=6)
    ap.add_argument("--seasons", type=int, default=48)
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    keep = {x.strip() for x in a.only.split(",") if x.strip()}
    out = ["# Fanbase and media cards, and fair competitiveness\n",
           "Fans and the press never touch a game. A fanbase's culture and ratings decide how an owner's approval responds to a season "
           "(how patient, how demanding, how moody, how much it believes the press). The press moves approval by at most 3 points a year "
           "(more in a big market, to a trusting fanbase). Fan Capital, the slow store of goodwill, only ever buffers a recall vote. "
           "Approval decides recalls, and a recall can lead to a coach or GM being fired, so the only road to the field is long. "
           "The question for every row: does any trend leave its band?\n"]
    base = (FM.MEDIA_SWAY, FM.CAPITAL_RECALL_WEIGHT)
    for label, fans, sway, capw, eng in VARIANTS:
        if keep and label[0] not in keep:
            continue
        FM.MEDIA_SWAY, FM.CAPITAL_RECALL_WEIGHT = sway, capw
        n = a.drive_leagues if eng == "drives" else a.leagues
        per, rows = fairness.run(eng, range(100, 100 + n), a.seasons, fans=fans)
        bad = [r[0] for r in rows if not r[4]]
        out.append(f"## {label}\n")
        out.append(f"{eng} engine, {n} leagues x {a.seasons} seasons.\n")
        out.append(fairness.table(rows))
        out.append("\n" + ("All trends inside the bands.\n" if not bad else f"**Outside the bands:** {', '.join(bad)}.\n"))
        out.append(footprint(per) + "\n")
        v = {r[0]: r[1] for r in rows}
        print("    ", footprint(per), flush=True)
        print(label, "->", "ALL INSIDE" if not bad else "OUTSIDE: " + "; ".join(bad), flush=True)
        print("    title conc:", round(v["max_titles_in_20"], 2), v["worst_league_titles"], " corr:", round(v["year_to_year_corr"], 3),
              " best-team odds:", round(v["best_team_title_odds"], 3), " repeat:", round(v["repeat_champion_rate"], 3),
              " stuck:", round(v["stuck_at_bottom"], 3), " exile fx:", round(v["exile_effect"], 2), flush=True)
    FM.MEDIA_SWAY, FM.CAPITAL_RECALL_WEIGHT = base
    path = a.out or os.path.join(ROOT, "reports", "fan_media_fairness_study.md")
    open(path, "w").write("\n".join(out))
    print("wrote", path)


if __name__ == "__main__":
    main()
