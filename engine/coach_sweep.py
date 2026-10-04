"""How big can the coach effects get before a fair-competitiveness band breaks?

Sweeps the three coach dials (team lift, player development, how often a legend appears) with the same leagues and
seeds, reports every band for each setting, and what the legends actually achieve. Writes reports/coach_fairness_study.md.

    python engine/coach_sweep.py [--leagues 8] [--seasons 48]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as C  # noqa: E402
import fairness  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__)).rsplit(os.sep, 1)[0]

# (label, coaches on?, team points at 100, development points at 100, legend rate, engine, leagues)
VARIANTS = [
    ("A. No coaches at all (souls only)", False, 1.0, 0.0, 0.05, "fast"),
    ("B. Team lift only, as first built (1.0 point, no development)", True, 1.0, 0.0, 0.05, "fast"),
    ("C. Add player development at 0.15 rating points a year", True, 1.0, 0.15, 0.05, "fast"),
    ("D. Development 0.25", True, 1.0, 0.25, 0.05, "fast"),
    ("E. Development 0.40", True, 1.0, 0.40, 0.05, "fast"),
    ("F. Development 0.60", True, 1.0, 0.60, 0.05, "fast"),
    ("G. Development 1.00", True, 1.0, 1.00, 0.05, "fast"),
    ("H. Development 0.40 and team lift 1.5 points", True, 1.5, 0.40, 0.05, "fast"),
    ("I. Development 0.40 and team lift 2.0 points", True, 2.0, 0.40, 0.05, "fast"),
    ("J. Development 0.40, lift 1.0, legends twice as common (10%)", True, 1.0, 0.40, 0.10, "fast"),
]


def footprint(per):
    t = {k: sum(d["_legend"][k] for d in per) for k in ("seasons", "wins", "playoffs", "titles", "seasons_all")}
    if not t["seasons"]:
        return "No legend-led team-seasons occurred."
    n = t["seasons"]
    return (f"Legend-led teams: {n / len(per):.0f} team-seasons per league (about {n / max(1, t['seasons_all']):.1f} legends on the field at a time). "
            f"They won {100 * t['wins'] / n:.1f}% of their games (league average 50%), made the playoffs {100 * t['playoffs'] / n:.0f}% of the time "
            f"(14 of 40 teams = 35% on average) and won the title in {100 * t['titles'] / n:.1f}% of seasons (1 in 40 = 2.5% on average).")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--leagues", type=int, default=8)
    ap.add_argument("--seasons", type=int, default=48)
    ap.add_argument("--only", default="", help="comma-separated variant letters, e.g. D,E")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--out", default="", help="write the report here instead of reports/coach_fairness_study.md")
    a = ap.parse_args(argv)
    keep = {x.strip() for x in a.only.split(",") if x.strip()}
    out = ["# Coach effects and fair competitiveness\n",
           "Each coach card has three levers: a lift to the team's offense and defense (a 50 rating is average and does nothing; "
           "a 100 is worth the stated points of margin), and a yearly boost to the development of each of her players (a 100 adds "
           "the stated rating points per year to every young player, half that to older ones; a 1 takes it away). Rare legends "
           "(5% of hires unless stated) have 90-plus ratings on all three. Coaches stay until they retire, so a great coach is a lasting edge. "
           "Same leagues and seeds in every row, 48 seasons each (first 8 thrown away). The question for every row: does any trend leave its band?\n"]
    base = (C.COACH_POINTS_AT_100, C.DEV_POINTS_AT_100, C.LEGEND_RATE)
    summary = []
    for label, coaches, pts, dev, leg, eng in VARIANTS:
        if keep and label[0] not in keep:
            continue
        C.COACH_POINTS_AT_100, C.DEV_POINTS_AT_100, C.LEGEND_RATE = pts, dev, leg
        per, rows = fairness.run(eng, range(100, 100 + a.leagues), a.seasons, coaches=coaches)
        bad = [r[0][:40] for r in rows if not r[4]]
        out.append(f"## {label}\n")
        out.append(fairness.table(rows))
        out.append("\n" + ("All trends inside the bands.\n" if not bad else f"**Outside the bands:** {', '.join(bad)}.\n"))
        if coaches:
            out.append(footprint(per) + "\n")
        v = {r[0]: r[1] for r in rows}
        summary.append((label, v, bad, footprint(per) if coaches else ""))
        print(label, "->", "ALL INSIDE" if not bad else "OUTSIDE: " + "; ".join(bad), flush=True)
        print("   ", footprint(per) if coaches else "", flush=True)
        print("    title conc (mean/worst):", round(v["max_titles_in_20"], 2), v["worst_league_titles"],
              " corr:", round(v["year_to_year_corr"], 3), " best-team odds:", round(v["best_team_title_odds"], 3),
              " stuck:", round(v["stuck_at_bottom"], 3), " win sd:", round(v["win_pct_sd"], 3), flush=True)
    C.COACH_POINTS_AT_100, C.DEV_POINTS_AT_100, C.LEGEND_RATE = base
    if not a.no_write:
        path = a.out or os.path.join(ROOT, "reports", "coach_fairness_study.md")
        open(path, "w").write("\n".join(out))
        print("wrote", path)


if __name__ == "__main__":
    main()
