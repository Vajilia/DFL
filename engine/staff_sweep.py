"""Do owners, GMs, recalls and firings keep the league inside the fair-competitiveness bands?

Same leagues and seeds in every row. The first row has no staff at all (coaches fixed for life, no owners or GMs).
The rest turn on owners who fire coaches and GMs with small levers; the last rows make the GM levers 3x and 6x stronger
as a stress test. Writes reports/staff_fairness_study.md.

    python engine/staff_sweep.py [--leagues 8] [--seasons 48]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards as C  # noqa: E402
import fairness  # noqa: E402
import staff_cards as S  # noqa: E402
from coach_sweep import footprint  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__)).rsplit(os.sep, 1)[0]

# (label, staff on?, GM scouting points, GM retention, engine)
VARIANTS = [
    ("A. Coaches only, as before (no owners, no GMs; coaches leave only by retiring)", False, 1.5, 0.30, "fast"),
    ("B. Owners fire coaches, GMs on, as built", True, 1.5, 0.30, "fast"),
    ("C. Stress test: GM levers 3x", True, 4.5, 0.90, "fast"),
    ("D. Stress test: GM levers 6x", True, 9.0, 1.50, "fast"),
    ("E. As built, full drive engine", True, 1.5, 0.30, "drives"),
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
    out = ["# Owners, GMs, recalls and fair competitiveness\n",
           "Owners never touch a game. What they change is who coaches and who manages: an owner whose team under-delivers builds up "
           "\"heat\" and eventually fires her coach and GM, and a new owner sometimes sweeps the staff out. GMs have two small levers: "
           "they lift their team's rookie a little each year (a 100-rated scout is worth +1.5 rating points; a 1 costs the same) and "
           "they keep slightly more of the roster from reaching free agency (a 100-rated negotiator cuts contract expiries by 30%; a 1 raises them by 30%). "
           "The question for every row: does any trend leave its band?\n"]
    base = (S.GM_SCOUTING_POINTS, S.GM_RETENTION)
    for label, staff, pts, ret, eng in VARIANTS:
        if keep and label[0] not in keep:
            continue
        S.GM_SCOUTING_POINTS, S.GM_RETENTION = pts, ret
        n = a.drive_leagues if eng == "drives" else a.leagues
        per, rows = fairness.run(eng, range(100, 100 + n), a.seasons, staff=staff)
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
    S.GM_SCOUTING_POINTS, S.GM_RETENTION = base
    path = a.out or os.path.join(ROOT, "reports", "staff_fairness_study.md")
    open(path, "w").write("\n".join(out))
    print("wrote", path)


if __name__ == "__main__":
    main()
